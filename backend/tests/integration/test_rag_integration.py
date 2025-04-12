"""Integration tests for the RAG chain with actual Weaviate and Anthropic API."""

import os
import pytest
import weaviate
from dotenv import load_dotenv

from backend.src.rag.chain import get_rag_chain
from backend.src.rag.vector_store import get_retriever
from backend.src.rag.llm import get_chat_model

# Load environment variables for the tests
load_dotenv()

# Mark these tests as integration tests
pytestmark = pytest.mark.integration

def is_weaviate_available():
    """Check if Weaviate is available at the URL from environment variables."""
    try:
        import weaviate
        # Assume v4 and try connect_to_local first
        client = weaviate.connect_to_local()
        is_ready = client.is_ready()
        client.close() # Close the connection after check
        return is_ready
    except ImportError:
         # Handle case where weaviate-client might not be installed
         return False
    except Exception as e:
        # Catch potential connection errors or other issues
        print(f"Error checking Weaviate availability: {e}")
        # Attempt to close client if it was partially initialized
        try:
            if 'client' in locals() and hasattr(client, 'close'):
                client.close()
        except Exception as close_e:
            print(f"  Error closing client during exception handling: {close_e}")
        return False

def is_anthropic_key_available():
    """Check if the Anthropic API key is available in environment variables."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    return api_key is not None and api_key != "" and api_key != "YOUR_ANTHROPIC_API_KEY_HERE"

@pytest.mark.skipif(not is_weaviate_available(), 
                   reason="Weaviate is not available - integration test skipped")
@pytest.mark.skipif(not is_anthropic_key_available(), 
                   reason="Anthropic API key is not properly configured - integration test skipped")
def test_retriever_returns_documents():
    """Test that the Weaviate retriever returns documents for a query."""
    # Get the retriever
    retriever = get_retriever()
    
    # A generic question that should match documents if there's any data in Weaviate
    query = "What are the eligibility requirements?"
    
    # Retrieve documents
    docs = retriever.invoke(query)
    
    # Assert we got something back (assuming Weaviate has some data)
    assert docs, "No documents returned from Weaviate retriever. Is there data in the vector store?"
    assert len(docs) > 0, "No documents returned from the retriever"
    assert hasattr(docs[0], "page_content"), "Retrieved document doesn't have page_content attribute"
    assert docs[0].page_content, "Retrieved document has empty page_content"

@pytest.mark.skipif(not is_weaviate_available(), 
                   reason="Weaviate is not available - integration test skipped")
@pytest.mark.skipif(not is_anthropic_key_available(), 
                   reason="Anthropic API key is not properly configured - integration test skipped")
def test_llm_generates_response():
    """Test that the LLM can generate a response to a simple prompt."""
    # Get the LLM
    llm = get_chat_model()
    
    # Simple prompt that doesn't require retrieval
    result = llm.invoke("Explain briefly what Retrieval-Augmented Generation is.")
    
    # Assert we got a non-empty response
    assert result, "No response returned from LLM"
    assert result.content, "Empty content in LLM response"
    assert len(result.content) > 50, "LLM response is suspiciously short"

@pytest.mark.skipif(not is_weaviate_available(), 
                   reason="Weaviate is not available - integration test skipped")
@pytest.mark.skipif(not is_anthropic_key_available(), 
                   reason="Anthropic API key is not properly configured - integration test skipped")
def test_full_rag_chain():
    """Test the complete RAG chain with actual external dependencies."""
    # Get the chain
    chain = get_rag_chain()
    
    # Question that should prompt retrieval and then generation
    # Adjust this to match data you know exists in your Weaviate instance
    query = "What are the eligibility criteria for housing schemes?"
    
    # Run the chain
    result = chain.invoke(query)
    
    # Assert we got a meaningful response
    assert result, "No result returned from the RAG chain"
    assert len(result) > 100, "RAG chain result is suspiciously short"
    
    # Log the result for manual inspection
    print(f"\n--- RAG Chain Response ---\nQuery: {query}\nResponse: {result}\n------------------------\n") 