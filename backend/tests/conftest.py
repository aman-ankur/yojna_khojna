"""
Global pytest configuration. This file is automatically discovered by pytest.
It sets up paths, fixtures and other test configuration.
"""
import sys
import os
from pathlib import Path
import pytest
from unittest.mock import MagicMock

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
sys.modules['sentence_transformers'] = MagicMock()

@pytest.fixture(scope="session", autouse=True)
def setup_environment():
    """Setup environment variables or other session-wide test configuration."""
    # Add any environment setup here (e.g. setting env variables)
    # Could mock out config module here if needed
    pass 