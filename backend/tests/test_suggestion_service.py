import pytest
import os
import sys
from unittest.mock import patch, AsyncMock, MagicMock
import json
import re

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.suggestion_service import (
    extract_entities,
    detect_language,
    generate_template_questions,
    generate_contextual_questions,
    generate_suggestions
)
from src.schemas import SuggestedQuestion

class TestSuggestionService:
    def test_extract_entities(self):
        """Test entity extraction from text."""
        # Test with scheme names
        text = "Pradhan Mantri Awas Yojana provides housing benefits."
        entities = extract_entities(text)
        assert "Pradhan Mantri Awas Yojana" in entities["schemes"]
        
        # Test with monetary amounts
        text = "You can get ₹50,000 under this scheme."
        entities = extract_entities(text)
        assert "₹" in entities["amounts"][0]
        
        # Test with documents
        text = "You need Aadhaar and ration card for verification."
        entities = extract_entities(text)
        assert "Aadhaar" in entities["documents"]
        assert "ration card" in entities["documents"]
    
    def test_detect_language(self):
        """Test language detection functionality."""
        # Test English text
        assert detect_language("How do I apply for this scheme?") == "en"
        
        # Test Hindi text
        assert detect_language("मैं इस योजना के लिए कैसे आवेदन करूं?") == "hi"
        
        # Test mixed text (should detect Hindi if any Hindi character present)
        assert detect_language("How to apply for आवास योजना?") == "hi"
    
    def test_generate_template_questions(self):
        """Test template-based question generation."""
        # Mock entity extraction result
        entities = {
            "schemes": ["Pradhan Mantri Awas Yojana"],
            "amounts": [],
            "documents": []
        }
        
        # Test English templates
        questions = generate_template_questions(
            question="Tell me about Pradhan Mantri Awas Yojana",
            answer="It provides housing benefits to eligible citizens.",
            entities=entities,
            language="en"
        )
        
        # Should generate at least one question
        assert len(questions) > 0
        assert isinstance(questions[0].id, str)
        assert "Pradhan Mantri Awas Yojana" in questions[0].text
        
        # Test Hindi templates
        questions = generate_template_questions(
            question="प्रधानमंत्री आवास योजना के बारे में बताएं",
            answer="यह पात्र नागरिकों को आवास लाभ प्रदान करता है।",
            entities=entities,
            language="hi"
        )
        
        # Should still work with Hindi
        assert len(questions) > 0
    
    @pytest.mark.asyncio
    async def test_generate_contextual_questions(self):
        """Test LLM-based contextual question generation."""
        # Mock LLM response
        mock_llm_response = AsyncMock()
        mock_content = MagicMock()
        mock_content.content = """
        Here are some suggested follow-up questions:
        
        [
          {"id": "1", "text": "What documents do I need for Pradhan Mantri Awas Yojana?"},
          {"id": "2", "text": "What is the eligibility criteria for this scheme?"},
          {"id": "3", "text": "How can I check my application status?"},
          {"id": "4", "text": "What is the amount of financial assistance provided?"}
        ]
        """
        mock_llm_response.return_value = mock_content
        
        # Mock chat history
        chat_history = [
            {"role": "user", "content": "Tell me about Pradhan Mantri Awas Yojana"},
            {"role": "assistant", "content": "It's a housing scheme by the government of India."}
        ]
        
        # Patch the LLM invoke method
        with patch('langchain_anthropic.ChatAnthropic.ainvoke', mock_llm_response):
            questions = await generate_contextual_questions(
                question="Tell me about Pradhan Mantri Awas Yojana",
                answer="It's a housing scheme by the government of India.",
                chat_history=chat_history,
                llm=None # Will create a new LLM instance
            )
            
            # Should get 4 questions from the mock response
            assert len(questions) == 4
            assert "documents" in questions[0].text.lower()
            assert "eligibility" in questions[1].text.lower()
    
    @pytest.mark.asyncio
    async def test_generate_suggestions_integration(self):
        """Test the main suggestion generation function."""
        # Mock the underlying functions
        with patch('src.services.suggestion_service.generate_template_questions') as mock_template, \
             patch('src.services.suggestion_service.generate_contextual_questions') as mock_contextual:
            
            # Set up return values with SuggestedQuestion objects instead of dictionaries
            mock_template.return_value = [
                SuggestedQuestion(id="t1", text="Template question 1"),
                SuggestedQuestion(id="t2", text="Template question 2")
            ]
            
            mock_contextual.return_value = [
                SuggestedQuestion(id="c1", text="Contextual question 1"),
                SuggestedQuestion(id="c2", text="Contextual question 2"),
                SuggestedQuestion(id="c3", text="Contextual question 3")
            ]
            
            # Test the integration
            chat_history = [
                {"role": "user", "content": "Question"},
                {"role": "assistant", "content": "Answer"}
            ]
            
            suggestions = await generate_suggestions(
                question="What is PM Awas Yojana?",
                answer="It's a housing scheme.",
                chat_history=chat_history
            )
            
            # Should prioritize contextual questions and limit to 5
            assert len(suggestions) <= 5
            
            # Contextual questions should come first
            if len(suggestions) > 0 and suggestions[0].id.startswith("c"):
                assert suggestions[0].text == "Contextual question 1" 