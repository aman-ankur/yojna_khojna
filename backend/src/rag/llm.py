"""Module for initializing the Anthropic LLM."""

import os
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_chat_model() -> ChatAnthropic:
    """
    Initializes and returns the Anthropic chat model.

    Loads the API key from the environment variable ANTHROPIC_API_KEY.

    Returns:
        ChatAnthropic: An instance of the LangChain Anthropic chat model.

    Raises:
        ValueError: If the ANTHROPIC_API_KEY environment variable is not set.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY environment variable not set. "
            "Please set the key in your .env file."
        )

    # Initialize the ChatAnthropic model
    # You can customize the model name (e.g., "claude-3-sonnet-20240229")
    # and other parameters like temperature, max_tokens, timeout as needed.
    # Refer to anthropic_claude_best_practices.md for guidance.
    model = ChatAnthropic(
        model="claude-3-5-sonnet-20241022", # Upgrading from Haiku to 3.5 Sonnet for better quality
        anthropic_api_key=api_key,
        temperature=0.1, # Lower temperature for more focused and consistent RAG answers
        max_tokens=4096, # Increased max tokens to handle longer responses, especially in Hindi
        timeout=90.0, # Increased timeout for longer responses
    )
    return model 