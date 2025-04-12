"""Integration tests for the /chat API endpoint in main.py."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Import the FastAPI app instance and specific message types for assertions
from backend.src.main import app
from backend.src.exceptions import WeaviateConnectionError
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from typing import List, Tuple

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration

@pytest.fixture(scope="module")
def client():
    """Pytest fixture to create a FastAPI TestClient."""
    with TestClient(app) as c:
        yield c

# Patch the NEW chain creation function
@patch('backend.src.main.create_conversational_rag_chain')
def test_chat_endpoint_success_no_history(mock_create_chain, client):
    """Test successful response with no initial history."""
    # Arrange
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = "This is the initial answer."
    mock_create_chain.return_value = mock_chain

    # Note: chat_history defaults to [] if not provided
    query_data = {"question": "First question?"}
    expected_input_to_chain = {
        "input": query_data["question"],
        "chat_history": [] # Expect empty list of BaseMessages
    }
    expected_updated_history = [[query_data["question"], "This is the initial answer."]]

    # Act
    response = client.post("/chat", json=query_data)

    # Assert
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["answer"] == "This is the initial answer."
    assert response_json["updated_history"] == expected_updated_history
    mock_create_chain.assert_called_once()
    # Check that invoke was called with correctly formatted history (empty list)
    mock_chain.invoke.assert_called_once_with(expected_input_to_chain)

@patch('backend.src.main.create_conversational_rag_chain')
def test_chat_endpoint_success_with_history(mock_create_chain, client):
    """Test successful response with existing conversation history."""
    # Arrange
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = "This is the follow-up answer."
    mock_create_chain.return_value = mock_chain

    initial_history: List[Tuple[str, str]] = [("Question 1", "Answer 1")]
    query_data = {
        "question": "Follow-up question?",
        "chat_history": initial_history
    }

    # Construct the expected BaseMessage list passed to the chain
    expected_formatted_history: List[BaseMessage] = [
        HumanMessage(content="Question 1"),
        AIMessage(content="Answer 1")
    ]
    expected_input_to_chain = {
        "input": query_data["question"],
        "chat_history": expected_formatted_history
    }
    expected_updated_history = [[h[0], h[1]] for h in initial_history] + [[query_data["question"], "This is the follow-up answer."]]

    # Act
    response = client.post("/chat", json=query_data)

    # Assert
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["answer"] == "This is the follow-up answer."
    assert response_json["updated_history"] == expected_updated_history
    mock_create_chain.assert_called_once()
    # Check that invoke was called with correctly formatted history
    mock_chain.invoke.assert_called_once_with(expected_input_to_chain)


@patch('backend.src.main.create_conversational_rag_chain')
def test_chat_endpoint_empty_answer_with_history(mock_create_chain, client):
    """Test response when the RAG chain returns an empty answer with history."""
    # Arrange
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = "" # Simulate empty answer
    mock_create_chain.return_value = mock_chain

    initial_history: List[Tuple[str, str]] = [("Q1", "A1")]
    query_data = {"question": "An obscure question?", "chat_history": initial_history}

    expected_formatted_history = [HumanMessage(content="Q1"), AIMessage(content="A1")]
    expected_input_to_chain = {"input": query_data["question"], "chat_history": expected_formatted_history}

    # Act
    response = client.post("/chat", json=query_data)

    # Assert
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["answer"] == "Sorry, I couldn't generate an answer for that question."
    # IMPORTANT: History should NOT be updated if no answer was generated
    expected_initial_history_json = [[h[0], h[1]] for h in initial_history]
    assert response_json["updated_history"] == expected_initial_history_json
    mock_create_chain.assert_called_once()
    mock_chain.invoke.assert_called_once_with(expected_input_to_chain)

# Patch the NEW chain creation function for error tests
@patch('backend.src.main.create_conversational_rag_chain')
def test_chat_endpoint_dependency_error(mock_create_chain, client):
    """Test handling of known dependency errors (e.g., Weaviate)."""
    # Arrange
    error_message = "Test Weaviate connection failure"
    mock_create_chain.side_effect = WeaviateConnectionError(error_message)

    query_data = {"question": "A valid question"} # History defaults to []

    # Act
    response = client.post("/chat", json=query_data)

    # Assert
    assert response.status_code == 503 # Service Unavailable
    response_json = response.json()
    assert "detail" in response_json
    assert "Service dependency error" in response_json["detail"]
    assert error_message in response_json["detail"]
    mock_create_chain.assert_called_once()

@patch('backend.src.main.create_conversational_rag_chain')
def test_chat_endpoint_unexpected_error(mock_create_chain, client):
    """Test handling of unexpected errors during chain invocation."""
    # Arrange
    mock_chain = MagicMock()
    mock_chain.invoke.side_effect = Exception("Something totally unexpected happened")
    mock_create_chain.return_value = mock_chain

    query_data = {"question": "Another question", "chat_history": [("PrevQ", "PrevA")]}
    expected_formatted_history = [HumanMessage(content="PrevQ"), AIMessage(content="PrevA")]
    expected_input_to_chain = {"input": query_data["question"], "chat_history": expected_formatted_history}

    # Act
    response = client.post("/chat", json=query_data)

    # Assert
    assert response.status_code == 500 # Internal Server Error
    response_json = response.json()
    assert "detail" in response_json
    assert response_json["detail"] == "Internal server error while processing the chat query."
    mock_create_chain.assert_called_once()
    mock_chain.invoke.assert_called_once_with(expected_input_to_chain)

def test_chat_endpoint_invalid_input_history_format(client):
    """Test response when chat_history format is invalid."""
    # Arrange
    # History should be List[Tuple[str, str]]
    invalid_query_data = {"question": "Valid Q", "chat_history": ["just a string", ("ok tuple",)]}

    # Act
    response = client.post("/chat", json=invalid_query_data)

    # Assert
    assert response.status_code == 422 # Unprocessable Entity (due to Pydantic validation)

# Original invalid input test still valid
def test_chat_endpoint_invalid_input_missing_question(client):
    """Test response when request body is invalid (missing question)."""
    # Arrange
    invalid_query_data = {"chat_history": []} # Missing 'question'

    # Act
    response = client.post("/chat", json=invalid_query_data)

    # Assert
    assert response.status_code == 422 # Unprocessable Entity
    # Optionally check the detail structure if needed
    # response_json = response.json()
    # assert "detail" in response_json 