import weaviate
import weaviate.classes as wvc # Import v4 classes
import logging
from typing import List, Optional, Dict, Any
# Removed v3 Client import
from weaviate.exceptions import UnexpectedStatusCodeException # Keep for potential http errors, though API errors are different now
from ..schemas import DocumentChunk

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Configuration --- (Ideally, use environment variables)
WEAVIATE_URL = "http://localhost:8080" # Default for local Docker setup
# Consider adding gRPC port if different, e.g., 50051
CLASS_NAME = "YojnaChunk" # Name for the Weaviate collection
VECTOR_DIMENSION = 768 # Dimension of paraphrase-multilingual-mpnet-base-v2 embeddings

def get_weaviate_client(url: str = WEAVIATE_URL) -> Optional[weaviate.WeaviateClient]: # Return type changed to v4 client
    """Connects to the Weaviate instance using v4 syntax.

    Args:
        url: The HTTP URL of the Weaviate instance.
             Note: gRPC port might be needed depending on connection method.

    Returns:
        A WeaviateClient object or None if connection fails.
    """
    try:
        # Using connect_to_local for simplicity, assumes default ports
        # For custom URLs/ports/auth, use weaviate.connect_to_custom(...)
        # Example: client = weaviate.connect_to_custom(http_host="localhost", http_port=8080, http_secure=False, grpc_host="localhost", grpc_port=50051)
        client = weaviate.connect_to_local() # Simplified connection for default localhost:8080
        client.connect()

        if client.is_ready():
            logging.info(f"Successfully connected to Weaviate (using v4 client)")
            return client
        else:
            logging.error(f"Weaviate (v4 client) at {url} is not ready.")
            client.close()
            return None
    except Exception as e:
        logging.error(f"Failed to connect to Weaviate (v4 client) at {url}: {e}", exc_info=True)
        return None

def ensure_schema_exists(client: weaviate.WeaviateClient): # Type hint updated
    """Creates the YojnaChunk collection schema in Weaviate (v4) if it doesn't exist.

    Args:
        client: An initialized WeaviateClient.
    """
    try:
        if client.collections.exists(CLASS_NAME):
            logging.info(f"Weaviate collection '{CLASS_NAME}' already exists.")
            return

        logging.info(f"Weaviate collection '{CLASS_NAME}' not found. Creating...")

        client.collections.create(
            name=CLASS_NAME,
            description="Stores chunks of text from Yojna documents with their embeddings",
            vectorizer_config=wvc.config.Configure.Vectorizer.none(), # Explicitly specify no vectorizer
            vector_index_config=wvc.config.Configure.VectorIndex.hnsw(
                distance_metric="cosine", # Using string literal for distance
                ef_construction=128,
                max_connections=16
                # ef parameter is set during queries in v4
            ),
            properties=[
                wvc.config.Property(name="chunk_id", data_type=wvc.config.DataType.TEXT, description="Unique identifier for the chunk"),
                wvc.config.Property(name="document_id", data_type=wvc.config.DataType.TEXT, description="Identifier of the source document"),
                wvc.config.Property(name="text", data_type=wvc.config.DataType.TEXT, description="The actual text content of the chunk"),
                wvc.config.Property(name="page_number", data_type=wvc.config.DataType.INT, description="Page number from the source PDF"),
                # Add other metadata fields if needed
            ]
        )
        logging.info(f"Successfully created Weaviate collection '{CLASS_NAME}'.")

    except Exception as e:
        logging.error(f"An unexpected error occurred while checking/creating collection '{CLASS_NAME}': {e}", exc_info=True)

def batch_import_chunks(client: weaviate.WeaviateClient, chunks: List[DocumentChunk]): # Type hint updated
    """Imports a list of DocumentChunk objects into Weaviate using v4 batching.

    Args:
        client: An initialized WeaviateClient.
        chunks: A list of DocumentChunk objects (must have embeddings).
    """
    if not chunks:
        logging.warning("No chunks provided for batch import.")
        return

    if not client.is_connected(): # Use is_connected() in v4
        logging.error("Weaviate client is not connected. Cannot perform batch import.")
        return

    logging.info(f"Starting batch import of {len(chunks)} chunks into Weaviate collection '{CLASS_NAME}'...")
    counter = 0
    errors = []

    try:
        collection = client.collections.get(CLASS_NAME)
        # Use context manager for batching in v4
        with collection.batch.dynamic() as batch:
            for chunk in chunks:
                if chunk.embedding is None:
                    logging.warning(f"Skipping chunk {chunk.chunk_id} due to missing embedding.")
                    continue

                properties = {
                    "chunk_id": chunk.chunk_id,
                    "document_id": chunk.document_id,
                    "text": chunk.text,
                    "page_number": chunk.metadata.get("page_number") # Extract relevant metadata
                    # Add other metadata properties here if defined in schema
                }
                # Remove None values, as Weaviate doesn't like them for non-nullable types like int
                properties = {k: v for k, v in properties.items() if v is not None}

                try:
                    batch.add_object(
                        properties=properties,
                        vector=chunk.embedding # Pass the pre-computed embedding vector
                        # uuid= # Optionally provide a specific UUID
                    )
                    counter += 1
                except Exception as e:
                    logging.error(f"Error adding chunk {chunk.chunk_id} to batch: {e}")
                    errors.append(str(e))

        # Check for batch errors after the 'with' block
        if batch.number_errors > 0:
             logging.error(f"Encountered {batch.number_errors} errors during batch import.")
             # Access detailed errors if needed:
             # for failed_obj in batch.failed_objects:
             #     logging.error(f"Failed object: {failed_obj.message}")

    except Exception as e:
         logging.error(f"An error occurred during the batch import process: {e}", exc_info=True)
         return # Exit if the batch context fails

    logging.info(f"Batch import finished. Attempted to add {counter} chunks to Weaviate collection '{CLASS_NAME}'. Errors: {len(errors)}")

# Basic test connection (optional)
if __name__ == '__main__':
    print("Testing Weaviate v4 connection...")
    client = get_weaviate_client()
    if client:
        try:
            print("Connection successful.")
            print("Ensuring collection exists...")
            ensure_schema_exists(client)
            print("Collection check/creation process finished.")
        finally:
            client.close() # Ensure client is closed after test
            print("Weaviate client closed.")
    else:
        print("Connection failed. Ensure Weaviate is running at", WEAVIATE_URL) 