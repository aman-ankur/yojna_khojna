"""Tests for the LLM initialization."""

import pytest
from unittest.mock import patch, MagicMock
import os

from backend.src.rag.llm import get_chat_model
from langchain_anthropic import ChatAnthropic


def test_get_chat_model_success():
    """Test successful initialization of ChatAnthropic with API key."""
    # Arrange
    mock_api_key = "test-api-key"
    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": mock_api_key}):
        # Act
        model = get_chat_model()

        # Assert
        assert isinstance(model, ChatAnthropic)
        # Check if the key was passed using get_secret_value()
        assert model.anthropic_api_key.get_secret_value() == mock_api_key
        assert model.model == "claude-3-haiku-20240307" # Check default model
        assert model.temperature == 0.2


def test_get_chat_model_missing_key():
    """Test that ValueError is raised if API key is missing."""
    # Arrange
    # Ensure the key is not in the environment for this test
    with patch.dict(os.environ, {}, clear=True):
        # Act & Assert
        with pytest.raises(ValueError, match="ANTHROPIC_API_KEY environment variable not set"):
            get_chat_model() 