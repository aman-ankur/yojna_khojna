"""
Global pytest configuration. This file is automatically discovered by pytest.
It sets up paths, fixtures and other test configuration.
"""
import sys
import os
from pathlib import Path
import pytest
from unittest.mock import MagicMock, patch

# Add both backend/ and project root to sys.path to make imports work correctly
backend_dir = Path(__file__).parent.parent
project_root = backend_dir.parent

if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Print sys.path for debugging
print(f"Python path in conftest: {sys.path}")

# Mock out some tricky modules that might cause issues during tests
# sys.modules['sentence_transformers'] = MagicMock() # Commented out for integration tests

@pytest.fixture(scope="session", autouse=True)
def setup_environment():
    """Setup environment variables or other session-wide test configuration."""
    # Add any environment setup here (e.g. setting env variables)
    # Could mock out config module here if needed
    pass 

@pytest.fixture(autouse=True)
def mock_weaviate_for_ci(monkeypatch):
    """
    Automatically mock Weaviate client in CI environment.
    This prevents tests that use TestClient from failing due to
    FastAPI startup events trying to connect to a real Weaviate instance.
    """
    if os.environ.get('CI') == 'true':
        print("CI environment detected, mocking Weaviate client")
        
        # Create a mock Weaviate client that won't try to connect
        mock_client = MagicMock()
        mock_client.is_connected.return_value = True
        mock_client.collections.get.return_value = MagicMock()
        
        # Mock collections interface for check_hash_exists
        mock_collections = MagicMock()
        mock_collection_instance = MagicMock()
        mock_query = MagicMock()
        mock_response = MagicMock()
        mock_response.objects = []  # Default to no objects found
        mock_query.fetch_objects.return_value = mock_response
        mock_collection_instance.query = mock_query
        mock_collections.get.return_value = mock_collection_instance
        mock_client.collections = mock_collections
        
        # Mock schema check function to do nothing
        def mock_ensure_schema(*args, **kwargs):
            return True
            
        # Apply mocks
        monkeypatch.setattr('backend.src.vector_db.weaviate_client.get_weaviate_client', 
                          lambda *args, **kwargs: mock_client)
        monkeypatch.setattr('backend.src.main.ensure_schema_exists', 
                          mock_ensure_schema) 