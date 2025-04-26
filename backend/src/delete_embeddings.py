import os
import sys
import weaviate
from weaviate.exceptions import UnexpectedStatusCodeError
from dotenv import load_dotenv
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from .env file
# Assumes the .env file is in the parent directory (workspace root) relative to backend/src
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

# Configuration
WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://localhost:8080") # Default if not set
CLASS_NAME = "YojnaChunk" # Class name where embeddings are stored

def delete_all_embeddings():
    """Connects to Weaviate and deletes all objects from the specified class."""
    logging.info(f"Attempting to connect to Weaviate at {WEAVIATE_URL}...")

    try:
        # Adjusted for weaviate-client v4 initialization
        client = weaviate.connect_to_local(
            host=WEAVIATE_URL.split(":")[-2].strip("/"), # Extract host
            port=int(WEAVIATE_URL.split(":")[-1]), # Extract port
        )
        client.connect() # Establish connection

        if not client.is_ready():
            logging.error("Weaviate is not ready. Please check if it's running and accessible.")
            client.close()
            sys.exit(1)
        logging.info("Successfully connected to Weaviate.")

        # Check if the class exists using v4 syntax
        if not client.collections.exists(CLASS_NAME):
             logging.warning(f"Collection '{CLASS_NAME}' does not exist. No objects to delete.")
             client.close()
             return # Exit gracefully if class doesn't exist
        else:
            logging.info(f"Found collection '{CLASS_NAME}'.")

        # --- Confirmation ---
        print(f"\n*** WARNING: This script will permanently delete ALL objects from the '{CLASS_NAME}' collection in Weaviate at {WEAVIATE_URL}. ***")
        print("This action cannot be undone.")
        confirm = input("Type 'DELETE' to confirm: ")

        if confirm != "DELETE":
            logging.info("Deletion cancelled by user.")
            client.close()
            return

        # --- Deletion ---
        logging.info(f"Proceeding with deletion of all objects in collection '{CLASS_NAME}'...")

        try:
            # Use v4 batch delete with a 'where' filter to delete all
            response = client.collections.get(CLASS_NAME).data.delete_many(
                where=weaviate.classes.query.Filter.by_property("text").like("*") # A filter that matches all objects with a 'text' property
            )

            logging.info("Deletion process initiated.")
            # Analyze results (v4 response structure)
            successful_deletions = response.successful
            failed_deletions = response.failed
            matches = response.matches # Total objects matching the filter

            logging.info(f"Deletion Summary:")
            logging.info(f"  Objects matched for deletion: {matches}")
            logging.info(f"  Successfully deleted: {successful_deletions}")
            logging.info(f"  Failed to delete: {failed_deletions}")

            if failed_deletions > 0:
                logging.warning("Some objects failed to delete. Check Weaviate logs for details.")
                # You might want to inspect response.errors here for more details
            else:
                logging.info(f"All matched objects successfully deleted from collection '{CLASS_NAME}'.")

        except Exception as e:
            logging.error(f"An error occurred during the deletion process: {e}")
            client.close()
            sys.exit(1)

    except Exception as e:
        logging.error(f"Failed to connect or execute operation: {e}")
        if 'client' in locals() and client.is_connected():
            client.close()
        sys.exit(1)
    finally:
        # Ensure the client is closed
        if 'client' in locals() and client.is_connected():
            client.close()
            logging.info("Weaviate client connection closed.")

if __name__ == "__main__":
    delete_all_embeddings() 