import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file, searching upwards from the current file.
# This makes it work whether running from backend/ or project root.
dotenv_path = Path(__file__).resolve().parent.parent / '.env' # Assumes .env is in backend/
# Alternative: dotenv.find_dotenv() can also search upwards
load_dotenv(dotenv_path=dotenv_path)

# --- Weaviate Configuration --- # 
# Use os.getenv to read the variable, providing a default value if it's not set.
WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://localhost:8080")
# Add gRPC URL if needed later
# WEAVIATE_GRPC_URL = os.getenv("WEAVIATE_GRPC_URL", "http://localhost:50051")

# --- Embedding Model Configuration --- #
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "paraphrase-multilingual-mpnet-base-v2")

# --- Test Data Configuration --- #
# Note: Paths read from env vars might need conversion to Path objects if needed
DEFAULT_TEST_PDF_PATH_STR = os.getenv("DEFAULT_TEST_PDF", "./test_docs/small_awaas_yojna.pdf")

# --- Placeholder for Future Keys --- #
# EXAMPLE_API_KEY = os.getenv("EXAMPLE_API_KEY", None)

# You can add functions here for more complex loading or validation if needed
def get_default_test_pdf_path() -> Path:
    """Returns the default test PDF path as a Path object relative to the backend directory."""
    # Assuming the path in .env is relative to the backend directory
    backend_dir = Path(__file__).resolve().parent.parent
    return backend_dir / DEFAULT_TEST_PDF_PATH_STR

# Example of how to handle a boolean flag
# ENABLE_FEATURE_X = os.getenv("ENABLE_FEATURE_X", 'False').lower() in ('true', '1', 't', 'y', 'yes')

# Example of how to handle an integer
# MAX_WORKERS = int(os.getenv("MAX_WORKERS", '4'))

# It's good practice to print a confirmation or warning if sensitive keys are missing
# if not EXAMPLE_API_KEY:
#     print("Warning: EXAMPLE_API_KEY environment variable not set.") 