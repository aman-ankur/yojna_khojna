import weaviate
import weaviate.classes as wvc
import logging
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse
from weaviate.exceptions import (
    WeaviateConnectionError as WeaviateV4ConnectionError,
    WeaviateStartUpError,
    WeaviateQueryError # Keep this for potential query issues
    # Removed WeaviateInsertUpdateError as it's not directly importable/used this way
    # WeaviateError is not directly importable as a base catch-all
)
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
    """Establishes a connection to the Weaviate instance using v4 client.

    Returns:
        An initialized and connected WeaviateClient instance.

    Raises:
        WeaviateConnectionError: If connection fails.
    """
    weaviate_url = config.WEAVIATE_URL
    logger.info(f"Attempting to connect to Weaviate at {weaviate_url}...")
    client = None # Initialize client to None
    try:
        # Extract host and port for connect_to_local
        parts = weaviate_url.replace("http://", "").replace("https://", "").split(":")
        host = parts[0]
        port = int(parts[1]) if len(parts) > 1 else 8080 # Default port if not specified

        # Consider using connect_to_custom for more options like headers/auth later
        client = weaviate.connect_to_local(host=host, port=port)

        client.connect()

        if not client.is_connected() or not client.is_ready():
             raise WeaviateStartUpError("Weaviate client connected but instance is not ready.")

        logger.info(f"Successfully connected to Weaviate v{client.get_meta()['version']} at {weaviate_url}")
        return client

    except WeaviateStartUpError as e:
        logger.error(f"Weaviate instance not ready at {weaviate_url}: {e}", exc_info=True)
        if client: client.close()
        # Use the custom WeaviateConnectionError for consistency in the app
        raise WeaviateConnectionError(f"Weaviate instance not ready at {weaviate_url}: {e}") from e
    except WeaviateV4ConnectionError as e:
        logger.error(f"Weaviate connection error to {weaviate_url}: {e}", exc_info=True)
        if client: client.close()
        raise WeaviateConnectionError(f"Failed to connect to Weaviate at {weaviate_url}: {e}") from e
    except Exception as e: # Catch any other unexpected errors during connection setup
        logger.error(f"Unexpected error connecting to Weaviate at {weaviate_url}: {e}", exc_info=True)
        if client: client.close()
        raise WeaviateConnectionError(f"Unexpected error connecting to Weaviate at {weaviate_url}: {e}") from e

def ensure_schema_exists(client: weaviate.WeaviateClient):
    """Ensures the YojnaChunk collection schema exists and has the necessary properties.

    Checks if the collection exists. If not, creates it.
    If it exists, checks if the 'document_hash' property is present.
    If 'document_hash' is missing, DELETES the existing collection and recreates it.

    Args:
        client: An initialized WeaviateClient.

    Raises:
        WeaviateSchemaError: If checking, creating, or recreating the schema fails.
    """
    should_create_collection = False
    document_hash_property_name = "document_hash"

    try:
        if client.collections.exists(CLASS_NAME):
            logger.info(f"Weaviate collection '{CLASS_NAME}' already exists. Verifying properties...")
            collection = client.collections.get(CLASS_NAME)
            config = collection.config.get()

            # Check if document_hash property exists
            prop_exists = any(prop.name == document_hash_property_name for prop in config.properties)

            if not prop_exists:
                logger.warning(f"Property '{document_hash_property_name}' missing in existing collection '{CLASS_NAME}'. Deleting and recreating collection to ensure correct schema.")
                try:
                    client.collections.delete(CLASS_NAME)
                    logger.info(f"Successfully deleted existing collection '{CLASS_NAME}'.")
                    should_create_collection = True # Flag that we need to create it now
                except Exception as delete_e:
                    logger.error(f"Failed to delete existing collection '{CLASS_NAME}' during schema correction: {delete_e}", exc_info=True)
                    raise WeaviateSchemaError(f"Failed to delete collection '{CLASS_NAME}' with incorrect schema. Manual intervention required.") from delete_e
            else:
                logger.info(f"Property '{document_hash_property_name}' exists. Schema for '{CLASS_NAME}' confirmed.")
                return # Schema is correct, nothing more to do
        else:
            # Collection does not exist, needs creation
            should_create_collection = True

        # --- Collection Creation Logic --- #
        if should_create_collection:
            logger.info(f"Creating Weaviate collection '{CLASS_NAME}'...")

            # Define properties using wvc constants - include document_hash here directly
            properties = [
                wvc.config.Property(name="chunk_id", data_type=wvc.config.DataType.TEXT, description="Unique identifier for the chunk"),
                wvc.config.Property(name="document_id", data_type=wvc.config.DataType.TEXT, description="Identifier of the source document (e.g., filename stem)"),
                wvc.config.Property(
                    name=document_hash_property_name, # Use variable name
                    data_type=wvc.config.DataType.TEXT,
                    description="SHA256 hash of the original document content",
                    tokenization=wvc.config.Tokenization.FIELD
                ),
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
                vectorizer_config=wvc.config.Configure.Vectorizer.none(), # Assuming embeddings are generated externally
                vector_index_config=vector_index_config,
                properties=properties
            )
            logger.info(f"Successfully created Weaviate collection '{CLASS_NAME}'.")

    # Catch specific relevant Weaviate exceptions for schema operations
    except (WeaviateQueryError, WeaviateV4ConnectionError, WeaviateStartUpError) as e:
        logger.error(f"Weaviate error occurred during schema check/creation for collection '{CLASS_NAME}': {e}", exc_info=True)
        # Use the custom WeaviateSchemaError for consistency
        raise WeaviateSchemaError(f"Failed to ensure Weaviate schema '{CLASS_NAME}': {e}") from e
    # Catch the specific error raised if deleting the property failed
    except WeaviateSchemaError as e:
        # Re-raise it as it already indicates a schema problem
        raise e
    except Exception as e:
        logger.error(f"Unexpected error occurred during schema check/creation for collection '{CLASS_NAME}': {e}", exc_info=True)
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
        WeaviateStorageError: If errors occur during batch import (reported via response object or connection issues).
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
            "document_hash": document_hash, # Ensure hash is included
            "text": chunk.text,
            "page_number": chunk.metadata.get("page_number")
        }
        # Filter out None values if necessary, although Weaviate might handle them
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

        # Check for errors in the response object for item-specific failures
        if response.has_errors:
            error_count = len(response.errors)
            logger.error(f"Encountered {error_count} errors during batch import (reported by Weaviate response object).")
            # Log details of the first few errors for debugging
            for i, error_obj in enumerate(response.errors.items()):
                 if i < 5: # Log first 5 errors
                     logger.error(f" Error {i+1}: Index {error_obj[0]} - {error_obj[1].message}")
                 else:
                     logger.error(" ... (additional errors not logged)")
                     break
            # Raise an exception summarizing the failure
            # Use the custom WeaviateStorageError
            raise WeaviateStorageError(
                f"{error_count} errors occurred during batch import into '{CLASS_NAME}'. Check logs for details.",
                failed_objects=response.errors # Pass the error details
            )
        else:
             # Note: insert_many response doesn't directly give success count, assume all non-error objects succeeded
             success_count = len(objects_to_insert)
             logger.info(f"Successfully processed batch import request for {success_count} objects into Weaviate collection '{CLASS_NAME}'. Skipped: {skipped_count}")

    # Catch errors related to the API call itself (connection, query structure)
    except (WeaviateQueryError, WeaviateV4ConnectionError) as e:
        logger.error(f"A Weaviate API call error occurred during the batch import process: {e}", exc_info=True)
        raise WeaviateStorageError(f"Weaviate API call error during batch import: {e}") from e
    except Exception as e:
         logger.error(f"An unexpected error occurred during the batch import process: {e}", exc_info=True)
         raise WeaviateStorageError(f"Unexpected error during batch import: {e}") from e

# Basic test connection (optional)
if __name__ == '__main__':
    print("Testing Weaviate v4 connection using config...")
    test_client = None # Initialize client to None
    try:
        test_client = get_weaviate_client()
        print("Connection successful.")
        print("Ensuring collection exists and is up-to-date...")
        ensure_schema_exists(test_client)
        print("Collection check/update/creation process finished.")
        # Add a small test for batch import here if desired

    except (WeaviateConnectionError, WeaviateSchemaError) as e:
        # Catch specific custom exceptions
        print(f"ERROR: {e}")
    except Exception as e:
        # Catch any other unexpected errors
        print(f"An unexpected error occurred during test: {e}")
    finally:
        if test_client and test_client.is_connected():
            test_client.close()
            print("Weaviate client closed.")
        # else:
            # Print the URL from config for debugging if connection failed
            # print(f"Connection likely failed. Ensure Weaviate is running at {config.WEAVIATE_URL}") # Assuming config is available 