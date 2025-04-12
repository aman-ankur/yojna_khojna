import weaviate
import weaviate.classes as wvc
import logging
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse
from weaviate.exceptions import WeaviateQueryError, WeaviateBaseError # More specific v4 exceptions
from ..schemas import DocumentChunk
from .. import config
# Import custom exceptions
from ..exceptions import WeaviateConnectionError, WeaviateSchemaError, WeaviateStorageError

# Get logger instance
logger = logging.getLogger(__name__)
# Removed old basicConfig call

# --- Configuration (Constants within this module) ---
CLASS_NAME = "YojnaChunk" # Name for the Weaviate collection

def get_weaviate_client() -> weaviate.WeaviateClient: # Return type is non-optional now, relies on exception
    """Connects to the Weaviate instance using v4 syntax and config URL.

    Returns:
        A connected WeaviateClient object.

    Raises:
        WeaviateConnectionError: If connection to Weaviate fails.
    """
    weaviate_url = config.WEAVIATE_URL
    logger.info(f"Attempting to connect to Weaviate at {weaviate_url}...")
    client: Optional[weaviate.WeaviateClient] = None # Define client before try
    try:
        if weaviate_url == "http://localhost:8080":
             client = weaviate.connect_to_local()
        else:
             parsed_url = urlparse(weaviate_url)
             host = parsed_url.hostname
             port = parsed_url.port
             http_secure = parsed_url.scheme == 'https'
             grpc_port = 50051 # Default assumption
             # Add more robust parsing/config for gRPC if needed
             logger.debug(f"Connecting to custom Weaviate URL: host={host}, port={port}, secure={http_secure}, grpc_port={grpc_port}")
             client = weaviate.connect_to_custom(
                 http_host=host, http_port=port, http_secure=http_secure,
                 grpc_host=host, grpc_port=grpc_port, grpc_secure=False
             )

        client.connect()

        if not client.is_ready():
             # Raise specific error if not ready after connect() call
             raise WeaviateConnectionError(f"Weaviate server at {weaviate_url} is not ready.")

        logger.info(f"Successfully connected to Weaviate at {weaviate_url}")
        return client

    except WeaviateBaseError as e: # Catch specific Weaviate errors
        logger.error(f"Weaviate connection error to {weaviate_url}: {e}", exc_info=True)
        if client: client.close() # Attempt to close if partially initialized
        raise WeaviateConnectionError(f"Failed to connect to Weaviate at {weaviate_url}: {e}") from e
    except Exception as e: # Catch any other unexpected errors
        logger.error(f"Unexpected error connecting to Weaviate at {weaviate_url}: {e}", exc_info=True)
        if client: client.close()
        raise WeaviateConnectionError(f"Unexpected error connecting to Weaviate at {weaviate_url}: {e}") from e

def ensure_schema_exists(client: weaviate.WeaviateClient):
    """Creates the YojnaChunk collection schema in Weaviate (v4) if it doesn't exist.

    Args:
        client: An initialized WeaviateClient.

    Raises:
        WeaviateSchemaError: If checking or creating the schema fails.
    """
    try:
        if client.collections.exists(CLASS_NAME):
            logger.info(f"Weaviate collection '{CLASS_NAME}' already exists.")
            return

        logger.info(f"Weaviate collection '{CLASS_NAME}' not found. Creating...")

        # Define properties using wvc constants
        properties = [
            wvc.config.Property(name="chunk_id", data_type=wvc.config.DataType.TEXT, description="Unique identifier for the chunk"),
            wvc.config.Property(name="document_id", data_type=wvc.config.DataType.TEXT, description="Identifier of the source document (e.g., filename stem)"),
            wvc.config.Property(name="document_hash", data_type=wvc.config.DataType.TEXT, description="SHA256 hash of the original document content",
                              tokenization=wvc.config.Tokenization.FIELD), # Use keyword tokenization for exact match filtering
            wvc.config.Property(name="text", data_type=wvc.config.DataType.TEXT, description="The actual text content of the chunk"),
            wvc.config.Property(name="page_number", data_type=wvc.config.DataType.INT, description="Page number from the source PDF"),
        ]

        # Define vector index config using wvc constants
        vector_index_config = wvc.config.Configure.VectorIndex.hnsw(
            distance_metric=wvc.config.VectorDistances.COSINE, # v4 uses constants here now
            ef_construction=128,
            max_connections=16
        )

        client.collections.create(
            name=CLASS_NAME,
            description="Stores chunks of text from Yojna documents with their embeddings",
            vectorizer_config=wvc.config.Configure.Vectorizer.none(),
            vector_index_config=vector_index_config,
            properties=properties
        )
        logger.info(f"Successfully created Weaviate collection '{CLASS_NAME}'.")

    except WeaviateBaseError as e:
        logger.error(f"Weaviate error occurred while checking/creating collection '{CLASS_NAME}': {e}", exc_info=True)
        raise WeaviateSchemaError(f"Failed to ensure Weaviate schema '{CLASS_NAME}': {e}") from e
    except Exception as e:
        logger.error(f"Unexpected error occurred while checking/creating collection '{CLASS_NAME}': {e}", exc_info=True)
        raise WeaviateSchemaError(f"Unexpected error ensuring Weaviate schema '{CLASS_NAME}': {e}") from e

def batch_import_chunks(client: weaviate.WeaviateClient, chunks: List[DocumentChunk], document_hash: str):
    """Imports a list of DocumentChunk objects into Weaviate using v4 batching,
    associating them with the original document's hash.

    Args:
        client: An initialized WeaviateClient.
        chunks: A list of DocumentChunk objects (must have embeddings).
        document_hash: The SHA256 hash of the original document.

    Raises:
        WeaviateConnectionError: If the client is not connected.
        WeaviateStorageError: If errors occur during batch import.
    """
    if not chunks:
        logger.warning("No chunks provided for batch import.")
        return

    if not client.is_connected():
        logger.error("Weaviate client is not connected. Cannot perform batch import.")
        raise WeaviateConnectionError("Client is not connected for batch import.")

    logger.info(f"Starting batch import of {len(chunks)} chunks into Weaviate collection '{CLASS_NAME}'...")
    skipped_count = 0
    objects_to_insert = []

    # Prepare data objects first
    for chunk in chunks:
        if chunk.embedding is None:
            logger.warning(f"Skipping chunk {chunk.chunk_id} due to missing embedding.")
            skipped_count += 1
            continue

        properties = {
            "chunk_id": chunk.chunk_id,
            "document_id": chunk.document_id,
            "document_hash": document_hash,
            "text": chunk.text,
            "page_number": chunk.metadata.get("page_number")
        }
        properties = {k: v for k, v in properties.items() if v is not None}

        objects_to_insert.append(wvc.data.DataObject(
            properties=properties,
            vector=chunk.embedding
        ))

    if not objects_to_insert:
        logger.warning("No valid chunks with embeddings found to import after filtering.")
        return

    try:
        collection = client.collections.get(CLASS_NAME)
        logger.debug(f"Attempting to insert {len(objects_to_insert)} objects into '{CLASS_NAME}'...")

        # Using insert_many for potentially better efficiency and error reporting
        response = collection.data.insert_many(objects_to_insert)

        # Check for errors in the response
        if response.has_errors:
            error_count = len(response.errors)
            logger.error(f"Encountered {error_count} errors during batch import.")
            # Log details of the first few errors for debugging
            for i, error_obj in enumerate(response.errors.items()):
                 if i < 5: # Log first 5 errors
                     logger.error(f" Error {i+1}: Index {error_obj[0]} - {error_obj[1].message}")
                 else:
                     logger.error(" ... (additional errors not logged)")
                     break
            # Raise an exception summarizing the failure
            raise WeaviateStorageError(
                f"{error_count} errors occurred during batch import into '{CLASS_NAME}'. Check logs for details.",
                failed_objects=response.errors # Pass the error details
            )
        else:
             success_count = len(objects_to_insert)
             logger.info(f"Successfully imported {success_count} chunks into Weaviate collection '{CLASS_NAME}'. Skipped: {skipped_count}")

    except WeaviateBaseError as e:
        logger.error(f"A Weaviate error occurred during the batch import process: {e}", exc_info=True)
        raise WeaviateStorageError(f"Weaviate error during batch import: {e}") from e
    except Exception as e:
         logger.error(f"An unexpected error occurred during the batch import process: {e}", exc_info=True)
         raise WeaviateStorageError(f"Unexpected error during batch import: {e}") from e

# Basic test connection (optional)
if __name__ == '__main__':
    print("Testing Weaviate v4 connection using config...")
    client = None # Initialize client to None
    try:
        client = get_weaviate_client()
        print("Connection successful.")
        print("Ensuring collection exists...")
        ensure_schema_exists(client)
        print("Collection check/creation process finished.")
        # Add a small test for batch import here if desired

    except (WeaviateConnectionError, WeaviateSchemaError) as e:
        # Catch specific custom exceptions
        print(f"ERROR: {e}")
    except Exception as e:
        # Catch any other unexpected errors
        print(f"An unexpected error occurred during test: {e}")
    finally:
        if client and client.is_connected():
            client.close()
            print("Weaviate client closed.")
        else:
            # Print the URL from config for debugging if connection failed
            print(f"Connection likely failed. Ensure Weaviate is running at {config.WEAVIATE_URL}") 