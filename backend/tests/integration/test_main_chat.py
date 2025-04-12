"""Integration tests for the /chat API endpoint in main.py."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Import the FastAPI app instance
# Assuming your main app instance is named 'app' in 'backend.src.main'
# Adjust the import path if necessary
from backend.src.main import app

# Import exceptions that the endpoint might handle
from backend.src.exceptions import WeaviateConnectionError

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration

@pytest.fixture(scope="module")
def client():
    """Pytest fixture to create a FastAPI TestClient."""
    with TestClient(app) as c:
        yield c

@patch('backend.src.main.get_rag_chain')
def test_chat_endpoint_success(mock_get_rag_chain, client):
    """Test successful response from the /chat endpoint."""
    # Arrange
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = "This is the generated answer."
    mock_get_rag_chain.return_value = mock_chain
    
    query_data = {"question": "What is the eligibility?"}
    
    # Act
    response = client.post("/chat", json=query_data)
    
    # Assert
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["answer"] == "This is the generated answer."
    mock_get_rag_chain.assert_called_once()
    mock_chain.invoke.assert_called_once_with(query_data["question"])

@patch('backend.src.main.get_rag_chain')
def test_chat_endpoint_empty_answer(mock_get_rag_chain, client):
    """Test response when the RAG chain returns an empty answer."""
    # Arrange
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = "" # Simulate empty answer
    mock_get_rag_chain.return_value = mock_chain
    
    query_data = {"question": "An obscure question?"}
    
    # Act
    response = client.post("/chat", json=query_data)
    
    # Assert
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["answer"] == "Sorry, I couldn't generate an answer for that question."
    mock_get_rag_chain.assert_called_once()
    mock_chain.invoke.assert_called_once_with(query_data["question"])

@patch('backend.src.main.get_rag_chain')
def test_chat_endpoint_dependency_error(mock_get_rag_chain, client):
    """Test handling of known dependency errors (e.g., Weaviate)."""
    # Arrange
    error_message = "Test Weaviate connection failure"
    # Simulate get_rag_chain itself raising the error during initialization
    mock_get_rag_chain.side_effect = WeaviateConnectionError(error_message)
    
    query_data = {"question": "A valid question"}
    
    # Act
    response = client.post("/chat", json=query_data)
    
    # Assert
    assert response.status_code == 503 # Service Unavailable
    response_json = response.json()
    assert "detail" in response_json
    assert "Service dependency error" in response_json["detail"]
    assert error_message in response_json["detail"]
    mock_get_rag_chain.assert_called_once()

@patch('backend.src.main.get_rag_chain')
def test_chat_endpoint_unexpected_error(mock_get_rag_chain, client):
    """Test handling of unexpected errors during chain invocation."""
    # Arrange
    mock_chain = MagicMock()
    mock_chain.invoke.side_effect = Exception("Something totally unexpected happened")
    mock_get_rag_chain.return_value = mock_chain
    
    query_data = {"question": "Another question"}
    
    # Act
    response = client.post("/chat", json=query_data)
    
    # Assert
    assert response.status_code == 500 # Internal Server Error
    response_json = response.json()
    assert "detail" in response_json
    assert response_json["detail"] == "Internal server error while processing the chat query."
    mock_get_rag_chain.assert_called_once()
    mock_chain.invoke.assert_called_once_with(query_data["question"])

def test_chat_endpoint_invalid_input(client):
    """Test response when request body is invalid (missing question)."""
    # Arrange
    invalid_query_data = {"query": "This is not the right key"}
    
    # Act
    response = client.post("/chat", json=invalid_query_data)
    
    # Assert
    assert response.status_code == 422 # Unprocessable Entity
    # Optionally check the detail structure if needed
    # response_json = response.json()
    # assert "detail" in response_json 