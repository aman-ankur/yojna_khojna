"""Handles connection to Weaviate vector store and retriever setup."""

import os
import weaviate
from langchain_community.vectorstores import Weaviate
from langchain_core.vectorstores import VectorStoreRetriever
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration --- #
WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://localhost:8080")
# TODO: Confirm these with the actual Weaviate schema created in Phase 1
WEAVIATE_CLASS_NAME = os.getenv("WEAVIATE_CLASS_NAME", "SchemeDocumentChunk")
WEAVIATE_TEXT_KEY = os.getenv("WEAVIATE_TEXT_KEY", "text")

# --- Weaviate Client --- #
_weaviate_client = None

def get_weaviate_client() -> weaviate.Client:
    """Initializes and returns a singleton Weaviate client instance."""
    global _weaviate_client
    if _weaviate_client is None:
        print(f"Attempting to connect to Weaviate at {WEAVIATE_URL}...")
        try:
            # TODO: Add authentication if Weaviate instance requires it
            # auth_config = weaviate.auth.AuthApiKey(api_key=os.getenv("WEAVIATE_API_KEY"))
            client = weaviate.Client(
                url=WEAVIATE_URL,
                # auth_client_secret=auth_config # Uncomment if using API key
            )
            if not client.is_ready():
                raise ConnectionError("Weaviate client is not ready.")
            _weaviate_client = client
            print("Successfully connected to Weaviate.")
        except Exception as e:
            print(f"Error connecting to Weaviate: {e}")
            # Depending on the application, might want to raise or handle differently
            raise
    return _weaviate_client

# --- LangChain Vector Store and Retriever --- #
_vector_store = None

def get_vector_store() -> Weaviate:
    """Initializes and returns a singleton LangChain Weaviate vector store instance."""
    global _vector_store
    if _vector_store is None:
        client = get_weaviate_client()
        print(f"Initializing LangChain Weaviate wrapper for class '{WEAVIATE_CLASS_NAME}' and text key '{WEAVIATE_TEXT_KEY}'")
        # Ensure the text key matches the property name in your Weaviate schema
        # that contains the text content you want to search over.
        _vector_store = Weaviate(
            client=client,
            index_name=WEAVIATE_CLASS_NAME,
            text_key=WEAVIATE_TEXT_KEY,
            # TODO: Specify attributes to retrieve if needed for metadata
            # attributes=['source_pdf', 'chunk_id']
        )
        print("LangChain Weaviate vector store initialized.")
    return _vector_store

def get_retriever(search_type="similarity", search_kwargs={"k": 3}) -> VectorStoreRetriever:
    """Creates and returns a LangChain retriever for the Weaviate vector store.

    Args:
        search_type (str): Type of search (e.g., "similarity", "mmr").
        search_kwargs (dict): Keyword arguments for the search (e.g., {"k": 3} for top 3 results).

    Returns:
        VectorStoreRetriever: The configured LangChain retriever.
    """
    vector_store = get_vector_store()
    retriever = vector_store.as_retriever(
        search_type=search_type,
        search_kwargs=search_kwargs
    )
    print(f"Weaviate retriever configured: type={search_type}, kwargs={search_kwargs}")
    return retriever

# --- Example Usage (for testing) --- #
if __name__ == '__main__':
    print("Testing Weaviate connection and retriever setup...")
    try:
        retriever = get_retriever()
        print("Retriever created successfully.")
        # Example query (assumes data is indexed)
        # try:
        #     results = retriever.invoke("What are the benefits of Awaas Yojna?")
        #     print(f"\nRetrieved {len(results)} documents:")
        #     for doc in results:
        #         print(f"- {doc.page_content[:100]}... (Metadata: {doc.metadata})")
        # except Exception as query_e:
        #     print(f"Error executing test query: {query_e}")
    except Exception as e:
        print(f"Failed to initialize retriever: {e}") 