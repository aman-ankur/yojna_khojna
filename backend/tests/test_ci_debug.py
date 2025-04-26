"""
Simple test file to diagnose CI issues with asyncio.
This file contains basic tests that help identify event loop or async testing issues.
"""
import os
import sys
import pytest
import asyncio
import platform
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from backend.src.main import app

def test_python_version():
    """Print Python version information for debugging"""
    print(f"Python version: {sys.version}")
    print(f"Python implementation: {platform.python_implementation()}")
    
def test_environment_variables():
    """Print relevant environment variables"""
    print(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")
    print(f"PYTEST_ASYNCIO_MODE: {os.environ.get('PYTEST_ASYNCIO_MODE', 'Not set')}")
    
    # Print all environment variables starting with PYTEST
    pytest_vars = {k: v for k, v in os.environ.items() if k.startswith('PYTEST')}
    print(f"All PYTEST environment variables: {pytest_vars}")

@pytest.mark.asyncio
async def test_asyncio_event_loop():
    """Test that asyncio event loop works correctly"""
    await asyncio.sleep(0.1)
    assert asyncio.get_event_loop() is not None
    print(f"Current event loop: {asyncio.get_event_loop()}")
    print(f"Event loop policy: {asyncio.get_event_loop_policy()}")
    
    # Check if we're in CI environment
    if os.environ.get('CI'):
        print("Running in CI environment")
    else:
        print("Running in local environment")

@pytest.mark.asyncio
async def test_basic_async():
    """Simple async test that should always pass."""
    await asyncio.sleep(0.1)
    assert True

@pytest.mark.asyncio
@patch('asyncio.sleep')
async def test_async_mock(mock_sleep):
    """Test that AsyncMock works correctly."""
    mock_sleep.return_value = None
    await asyncio.sleep(1)
    mock_sleep.assert_called_once_with(1)
    assert True

@pytest.mark.asyncio
async def test_fastapi_client():
    """Test that TestClient works in a simple async context."""
    try:
        with TestClient(app) as client:
            # Make a simple GET request to a route that should exist
            response = client.get("/health")
            assert response.status_code in (200, 404), f"Unexpected status code: {response.status_code}"
    except Exception as e:
        # Log but re-raise to see if this is the same issue we're facing in CI
        print(f"Exception in test_fastapi_client: {str(e)}")
        raise 