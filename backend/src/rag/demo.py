#!/usr/bin/env python
"""
Demo script for testing the RAG chain interactively.

Usage:
    python -m backend.src.rag.demo

You can then enter questions and see the responses from the RAG system.
Press Ctrl+C to exit.
"""

import os
from dotenv import load_dotenv

from .chain import get_rag_chain

# Load environment variables
load_dotenv()


def check_dependencies():
    """Check if required dependencies are available."""
    # Check Weaviate URL
    weaviate_url = os.environ.get("WEAVIATE_URL")
    if not weaviate_url:
        print("⚠️  Warning: WEAVIATE_URL is not set in .env file")
        return False
    
    # Check Anthropic API key
    anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not anthropic_api_key:
        print("⚠️  Warning: ANTHROPIC_API_KEY is not set in .env file")
        return False
    elif anthropic_api_key == "YOUR_ANTHROPIC_API_KEY_HERE":
        print("⚠️  Warning: ANTHROPIC_API_KEY is set to the placeholder value")
        return False
    
    return True


def main():
    """Demo function to interactively test the RAG chain."""
    print("\n===== RAG Chain Demo =====")
    print("Loading RAG chain...")
    
    if not check_dependencies():
        print("⚠️  Some dependencies may not be properly configured.")
        proceed = input("Do you want to proceed anyway? (y/n): ")
        if proceed.lower() != 'y':
            print("Exiting.")
            return
    
    # Initialize the RAG chain
    rag_chain = get_rag_chain()
    print("RAG chain initialized successfully!")
    print("\nEnter your questions below, or press Ctrl+C to exit.\n")
    
    try:
        while True:
            # Get user question
            question = input("\n🧑 Question: ")
            if not question:
                continue
            
            # Process the question
            print("\n⏳ Generating answer...\n")
            answer = rag_chain.invoke(question)
            
            # Display the answer
            print(f"🤖 Answer: {answer}\n")
            print("-" * 50)
            
    except KeyboardInterrupt:
        print("\n\nExiting RAG demo. Goodbye!")


if __name__ == "__main__":
    main() 