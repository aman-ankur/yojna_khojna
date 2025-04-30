import logging
import uuid
import re
from typing import List, Dict, Any, Tuple, Optional
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import PromptTemplate
from langchain_anthropic import ChatAnthropic
from ..schemas import SuggestedQuestion

# Set up logging
logger = logging.getLogger(__name__)

# Define question categories based on PRD
QUESTION_CATEGORIES = {
    "ELIGIBILITY": {
        "name": "Eligibility Clarification",
        "templates": [
            "Am I eligible for {scheme} if {situation}?",
            "What are the income limits for {scheme}?",
            "Can I apply for {scheme} if I'm from {category}?",
        ]
    },
    "APPLICATION": {
        "name": "Application Process",
        "templates": [
            "What is the step-by-step process to apply for {scheme}?",
            "Where do I need to go to apply for {scheme}?",
            "Can I apply online for {scheme}?",
        ]
    },
    "DOCUMENTS": {
        "name": "Document Requirements",
        "templates": [
            "What documents do I need to apply for {scheme}?",
            "Is {document} required for {scheme}?",
            "What if I don't have {document} for my {scheme} application?",
        ]
    },
    "BENEFITS": {
        "name": "Benefits & Amounts",
        "templates": [
            "How much financial assistance will I get from {scheme}?",
            "What are all the benefits provided under {scheme}?",
            "When will I receive the money from {scheme}?",
        ]
    },
    "TIMELINE": {
        "name": "Timelines & Deadlines",
        "templates": [
            "What is the last date to apply for {scheme}?",
            "How long does the {scheme} application process take?",
            "When will {scheme} benefits start after approval?",
        ]
    },
    "CONTACT": {
        "name": "Contact Information",
        "templates": [
            "Who should I contact if I have problems with my {scheme} application?",
            "Where is the nearest office to apply for {scheme}?",
            "Is there a helpline number for {scheme}?",
        ]
    },
    "RELATED": {
        "name": "Related Schemes",
        "templates": [
            "Are there any other schemes similar to {scheme}?",
            "What schemes are available for {demographic}?",
            "Can I apply for multiple schemes together?",
        ]
    },
    "PERSONAL": {
        "name": "Personal Situation",
        "templates": [
            "How can {scheme} help me with {situation}?",
            "What if my {circumstance} changes after applying for {scheme}?",
            "Is {scheme} suitable for someone in my situation?",
        ]
    }
}

# Define language variants for templates
TEMPLATE_TRANSLATIONS = {
    "en": {
        "Am I eligible for {scheme} if {situation}?": "Am I eligible for {scheme} if {situation}?",
        "What are the income limits for {scheme}?": "What are the income limits for {scheme}?"
        # Add more translations as needed
    },
    "hi": {
        "Am I eligible for {scheme} if {situation}?": "क्या मैं {situation} होने पर {scheme} के लिए पात्र हूँ?",
        "What are the income limits for {scheme}?": "{scheme} के लिए आय सीमा क्या है?"
        # Add more translations as needed
    }
}

# Entity extraction regex patterns
SCHEME_NAME_PATTERN = r'((?:[A-Z][a-z]+ )+Yojana|(?:[A-Z][a-z]+ )+Scheme|(?:[A-Z][a-z]+ )+योजना)'
AMOUNT_PATTERN = r'(₹|Rs\.?)\s*[\d,]+(?:\.\d+)?(?:\s*(?:lakh|lakhs|हज़ार|crore))?'
DOCUMENT_PATTERN = r'(Aadhaar|PAN|ration card|income certificate|caste certificate|आधार|पैन कार्ड|राशन कार्ड)'

def extract_entities(text: str) -> Dict[str, List[str]]:
    """Extract entities like scheme names, amounts, etc. from text."""
    entities = {
        "schemes": [],
        "amounts": [],
        "documents": []
    }
    
    # Extract scheme names
    scheme_matches = re.findall(SCHEME_NAME_PATTERN, text)
    entities["schemes"] = list(set(scheme_matches))
    
    # Extract monetary amounts
    amount_matches = re.findall(AMOUNT_PATTERN, text)
    entities["amounts"] = list(set(amount_matches))
    
    # Extract document names
    document_matches = re.findall(DOCUMENT_PATTERN, text)
    entities["documents"] = list(set(document_matches))
    
    logger.debug(f"Extracted entities: {entities}")
    return entities

def detect_language(text: str) -> str:
    """Detect language of the text (simplified version)."""
    # Check for Hindi characters
    if re.search(r'[\u0900-\u097F]', text):
        return "hi"
    return "en"

def generate_template_questions(
    question: str, 
    answer: str, 
    entities: Dict[str, List[str]], 
    language: str = "en"
) -> List[SuggestedQuestion]:
    """Generate questions based on templates and extracted entities."""
    suggested_questions = []
    scheme = entities["schemes"][0] if entities["schemes"] else "this scheme"
    
    # Select relevant categories based on entities
    relevant_categories = []
    
    # Always consider eligibility and application process
    relevant_categories.extend(["ELIGIBILITY", "APPLICATION"])
    
    # Add document category if no documents mentioned
    if not entities["documents"]:
        relevant_categories.append("DOCUMENTS")
    
    # Add benefits category if no amounts mentioned
    if not entities["amounts"]:
        relevant_categories.append("BENEFITS")
    
    # Add timeline category
    relevant_categories.append("TIMELINE")
    
    # Add related schemes category
    relevant_categories.append("RELATED")
    
    # Ensure we don't have duplicates
    relevant_categories = list(set(relevant_categories))
    
    # Take at most 3 categories to avoid overwhelming the user
    selected_categories = relevant_categories[:3]
    
    # For each category, generate a question
    for category in selected_categories:
        category_data = QUESTION_CATEGORIES[category]
        templates = category_data["templates"]
        
        # Select a template
        template = templates[0]  # Default to first template
        
        # Try to translate the template
        if language in TEMPLATE_TRANSLATIONS and template in TEMPLATE_TRANSLATIONS[language]:
            template = TEMPLATE_TRANSLATIONS[language][template]
        
        # Fill in template with entity values
        try:
            filled_question = template.format(
                scheme=scheme,
                situation="my situation",
                category="my category",
                document="Aadhaar card",
                demographic="my demographic",
                circumstance="circumstances"
            )
            
            question_id = str(uuid.uuid4())
            suggested_questions.append(
                SuggestedQuestion(id=question_id, text=filled_question)
            )
        except KeyError as e:
            logger.error(f"Error filling template {template}: {e}")
    
    return suggested_questions

async def generate_contextual_questions(
    question: str, 
    answer: str, 
    chat_history: List[Dict[str, str]], 
    llm: Optional[ChatAnthropic] = None,
    language: str = "en"
) -> List[SuggestedQuestion]:
    """Generate contextual follow-up questions using LLM."""
    if llm is None:
        llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            temperature=0.1,
            max_tokens=4096
        )
    
    # Format chat history for the prompt
    formatted_history = ""
    for msg in chat_history:
        if msg["role"] == "user":
            formatted_history += f"User: {msg['content']}\n"
        else:
            formatted_history += f"Assistant: {msg['content']}\n"
    
    # Update prompt to specify exactly 4 questions and emphasize language matching
    prompt_template = """You are an AI assistant helping users navigate government schemes in India. 
Based on the conversation history and the most recent query and answer, suggest exactly 4 relevant follow-up questions 
that the user might want to ask next.

Focus on questions about:
1. Eligibility criteria
2. Application process
3. Required documents
4. Benefits and financial assistance
5. Deadlines and timelines
6. Contact information
7. Related schemes
8. Specific advice for their situation

The questions should be clear, specific, and directly relevant to the current conversation topic.

IMPORTANT: Generate the questions in the SAME LANGUAGE as the conversation. If the conversation is in Hindi, generate Hindi questions. If in English, generate English questions.

Conversation History:
{history}

Most Recent User Query: {question}
Most Recent Assistant Response: {answer}

Detected Language: {language}

Generate exactly 4 follow-up questions in JSON format:
[
  {{"id": "1", "text": "First follow-up question"}},
  {{"id": "2", "text": "Second follow-up question"}},
  {{"id": "3", "text": "Third follow-up question"}},
  {{"id": "4", "text": "Fourth follow-up question"}}
]
"""
    
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["history", "question", "answer", "language"]
    )
    
    # Prepare the formatted prompt with language
    formatted_prompt = prompt.format(
        history=formatted_history,
        question=question,
        answer=answer,
        language=language
    )
    
    try:
        # Call the LLM to generate questions
        llm_response = await llm.ainvoke(formatted_prompt)
        response_text = llm_response.content
        
        # Extract JSON from response (handling potential formatting issues)
        json_match = re.search(r'\[\s*\{.*\}\s*\]', response_text, re.DOTALL)
        if json_match:
            import json
            questions_json = json.loads(json_match.group(0))
            
            # Convert to SuggestedQuestion objects
            suggested_questions = [
                SuggestedQuestion(id=str(uuid.uuid4()), text=q["text"]) 
                for q in questions_json
            ]
            
            logger.info(f"Generated {len(suggested_questions)} contextual questions")
            return suggested_questions
        else:
            logger.error("Failed to extract JSON from LLM response")
            return []
    
    except Exception as e:
        logger.error(f"Error generating contextual questions: {e}")
        return []

async def generate_suggestions(
    question: str, 
    answer: str, 
    chat_history: List[Dict[str, str]]
) -> List[SuggestedQuestion]:
    """Main function to generate suggested questions."""
    # Detect language
    language = detect_language(question if question else answer)
    
    # Extract entities from the conversation
    entities = extract_entities(question + " " + answer)
    
    # Generate questions using templates
    template_questions = generate_template_questions(question, answer, entities, language)
    
    # Generate contextual questions using LLM with language parameter
    contextual_questions = await generate_contextual_questions(
        question, 
        answer, 
        chat_history,
        language=language
    )
    
    # Combine questions (prioritizing contextual ones)
    all_questions = contextual_questions + template_questions
    
    # Limit to exactly 4 questions
    return all_questions[:4] 