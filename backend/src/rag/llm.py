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
        model="claude-3-haiku-20240307", # Using Haiku for speed/cost initially
        anthropic_api_key=api_key,
        temperature=0.2, # Lower temperature for more focused RAG answers
        max_tokens=1024, # Set a reasonable max token limit
        timeout=60.0, # Set a timeout
    )
    return model 