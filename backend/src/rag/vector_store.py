"""Handles connection to Weaviate vector store and retriever setup."""

import os
import weaviate
# Replace deprecated import with the new one
# from langchain_community.vectorstores import Weaviate
from langchain_weaviate import WeaviateVectorStore
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_community.embeddings import SentenceTransformerEmbeddings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration --- #
WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://localhost:8080")
# TODO: Confirm these with the actual Weaviate schema created in Phase 1
WEAVIATE_CLASS_NAME = os.getenv("WEAVIATE_CLASS_NAME", "SchemeDocumentChunk")
WEAVIATE_TEXT_KEY = os.getenv("WEAVIATE_TEXT_KEY", "text")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "paraphrase-multilingual-mpnet-base-v2")

# --- Weaviate Client --- #
_weaviate_client = None

def get_weaviate_client():
    """Initializes and returns a singleton Weaviate client instance."""
    global _weaviate_client
    if _weaviate_client is None:
        print(f"Attempting to connect to Weaviate (expecting local instance)...")
        try:
            # Assume v4 and try connect_to_local
            # For production/remote, use weaviate.connect_to_wcs() or weaviate.connect_to_custom()
            _weaviate_client = weaviate.connect_to_local()
            
            if not _weaviate_client.is_ready():
                raise ConnectionError("Weaviate client (connect_to_local) is not ready.")
            
            print("Successfully connected to Weaviate (using connect_to_local).")
        except ImportError:
             print("❌ Failed to import weaviate. Ensure 'weaviate-client' is installed.")
             raise
        except Exception as e:
            print(f"❌ Error connecting to Weaviate using connect_to_local: {e}")
            # Consider adding fallback to other connection methods if needed
            raise
    return _weaviate_client

# --- Embedding Model --- #
_embedding_model = None

def get_embedding_model():
    """Initializes and returns a singleton embedding model instance."""
    global _embedding_model
    if _embedding_model is None:
        print(f"Initializing embedding model: {EMBEDDING_MODEL_NAME}")
        # Use SentenceTransformerEmbeddings
        # Make sure the model name matches what was used for indexing!
        _embedding_model = SentenceTransformerEmbeddings(
            model_name=EMBEDDING_MODEL_NAME
        )
        print("Embedding model initialized.")
    return _embedding_model

# --- LangChain Vector Store and Retriever --- #
_vector_store = None

def get_vector_store() -> WeaviateVectorStore:
    """Initializes and returns a singleton LangChain Weaviate vector store instance."""
    global _vector_store
    if _vector_store is None:
        client = get_weaviate_client()
        embeddings = get_embedding_model()
        print(f"Initializing LangChain Weaviate wrapper for class '{WEAVIATE_CLASS_NAME}' and text key '{WEAVIATE_TEXT_KEY}'")
        
        # Pass the embedding model to the constructor
        _vector_store = WeaviateVectorStore(
            client=client,
            index_name=WEAVIATE_CLASS_NAME,
            text_key=WEAVIATE_TEXT_KEY,
            embedding=embeddings
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