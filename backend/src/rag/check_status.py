#!/usr/bin/env python
"""
Utility script to check the status of dependencies for the RAG system.
This script verifies:
1. Weaviate server is accessible and responsive
2. Anthropic API key is valid and working

Usage:
    python -m backend.src.rag.check_status
"""

import os
import sys
from time import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def check_weaviate():
    """Check if Weaviate is accessible."""
    weaviate_url_env = os.environ.get("WEAVIATE_URL") # Keep for reference/logging
    if not weaviate_url_env:
        print("❌ WEAVIATE_URL is not set in .env file")
        return False
    
    print(f"🔍 Checking Weaviate (expecting local connection at {weaviate_url_env})...")
    
    try:
        import weaviate
        
        # Assume v4 and try connect_to_local first
        print("  Attempting connection using weaviate.connect_to_local()")
        client = weaviate.connect_to_local()
        
        if client.is_ready():
            print("✅ Weaviate is accessible and ready (connected via connect_to_local)")
            client.close() # Close the connection after check
            return True
        else:
            print("❌ Weaviate connect_to_local() did not result in a ready client.")
            client.close()
            return False
            
    except ImportError:
         print("❌ Failed to import weaviate. Ensure 'weaviate-client' is installed.")
         return False
    except Exception as e:
        # Catch potential connection errors or other issues
        print(f"❌ Error connecting to Weaviate: {e}")
        # Attempt to close client if it was partially initialized
        try:
            if 'client' in locals() and hasattr(client, 'close'):
                client.close()
        except Exception as close_e:
            print(f"  Error closing client during exception handling: {close_e}")
        return False


def check_anthropic():
    """Check if Anthropic API is working."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY is not set in .env file")
        return False
    
    if api_key == "YOUR_ANTHROPIC_API_KEY_HERE":
        print("❌ ANTHROPIC_API_KEY is still set to the placeholder value")
        return False
    
    print("🔍 Checking Anthropic API connection...")
    
    try:
        from langchain_anthropic import ChatAnthropic
        
        # Create a minimal instance for testing
        model = ChatAnthropic(
            model="claude-3-haiku-20240307",
            anthropic_api_key=api_key,
            temperature=0,
            max_tokens=10,
            timeout=10.0,
        )
        
        # Simple test prompt
        start_time = time()
        response = model.invoke("Say hello")
        duration = time() - start_time
        
        # Check response
        if response and response.content:
            print(f"✅ Anthropic API is working (response time: {duration:.2f}s)")
            print(f"  Response: '{response.content}'")
            return True
        else:
            print("❌ Received empty response from Anthropic API")
            return False
            
    except Exception as e:
        print(f"❌ Error connecting to Anthropic API: {e}")
        return False


def main():
    """Main function to check all dependencies."""
    print("\n===== RAG System Dependency Check =====\n")
    
    weaviate_ok = check_weaviate()
    print()
    anthropic_ok = check_anthropic()
    
    print("\n===== Summary =====")
    print(f"Weaviate: {'✅ OK' if weaviate_ok else '❌ Failed'}")
    print(f"Anthropic API: {'✅ OK' if anthropic_ok else '❌ Failed'}")
    
    if weaviate_ok and anthropic_ok:
        print("\n✅ All dependencies are working! The RAG system should function correctly.")
        return 0
    else:
        print("\n⚠️  Some dependencies have issues. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 