import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.main import app
from src.schemas import SuggestedQuestion

client = TestClient(app)

def test_suggested_questions_schema():
    """Test the suggested questions API schema validation."""
    # Create test data
    test_data = {
        "question": "Tell me about Pradhan Mantri Awas Yojana",
        "answer": "It's a housing scheme by the government of India.",
        "chat_history": [
            {"role": "user", "content": "Tell me about Pradhan Mantri Awas Yojana"},
            {"role": "assistant", "content": "It's a housing scheme by the government of India."}
        ]
    }
    
    # Make API request
    response = client.post("/suggested-questions", json=test_data)
    
    # Verify response status
    assert response.status_code == 200
    
    # Verify response schema
    data = response.json()
    assert "suggestions" in data
    assert isinstance(data["suggestions"], list)
    
    # If we got suggestions, verify their structure
    if data["suggestions"]:
        suggestion = data["suggestions"][0]
        assert "id" in suggestion
        assert "text" in suggestion
        assert isinstance(suggestion["id"], str)
        assert isinstance(suggestion["text"], str)

def test_suggested_questions_handles_errors():
    """Test that the endpoint handles errors gracefully."""
    # Create test data with potentially problematic inputs
    test_data = {
        "question": "",  # Empty question
        "answer": "Some answer",
        "chat_history": []  # Empty history
    }
    
    # Make API request
    response = client.post("/suggested-questions", json=test_data)
    
    # Even with bad data, endpoint should return 200 with empty suggestions
    assert response.status_code == 200
    
    # Verify response format has empty suggestions rather than error
    data = response.json()
    assert "suggestions" in data
    assert isinstance(data["suggestions"], list)
    
    # Try with missing fields
    response = client.post(
        "/suggested-questions", 
        json={"question": "question only"}
    )
    
    # Should return validation error
    assert response.status_code == 422 