import pytest
from pytest_mock import MockerFixture
import weaviate
from typing import List
import numpy as np
from unittest.mock import MagicMock, patch
from weaviate.exceptions import WeaviateBaseError
from weaviate.collections.classes.batch import BatchObjectReturn, ErrorObject

from backend.src.schemas import DocumentChunk
from backend.src.exceptions import WeaviateConnectionError, WeaviateSchemaError, WeaviateStorageError

# Mock config before importing the module
@pytest.fixture(scope="function", autouse=True)
def mock_config(monkeypatch):
    """Mock the config module to avoid using real configuration during tests."""
    mock_config = MagicMock()
    mock_config.WEAVIATE_URL = "http://localhost:8080"
    monkeypatch.setattr("backend.src.config.WEAVIATE_URL", "http://localhost:8080")
    return mock_config

# Import the module after mocking
from backend.src.vector_db import weaviate_client

# --- Fixtures ---
@pytest.fixture
def mock_weaviate_client_v4(mocker: MockerFixture) -> MagicMock:
    """Mocks the weaviate.connect_to_local and connect_to_custom functions."""
    mock_client = mocker.MagicMock(spec=weaviate.WeaviateClient)
    mocker.patch.object(weaviate, 'connect_to_local', return_value=mock_client)
    mocker.patch.object(weaviate, 'connect_to_custom', return_value=mock_client)
    
    # Create a detailed mock for collections
    mock_collections = mocker.MagicMock()
    mock_collection = mocker.MagicMock()
    mock_data = mocker.MagicMock()
    mock_batch = mocker.MagicMock()
    
    # Set up the get method to return the mock_collection
    mock_collections.get.return_value = mock_collection
    
    # Set up the collection mock objects
    mock_collection.data = mock_data
    mock_collection.batch = mock_batch
    
    # Set the collections attribute on the client mock
    mock_client.collections = mock_collections
    
    # Ensure connect/ready methods work
    mock_client.is_ready.return_value = True  # Default is ready (override in specific tests)
    mock_client.is_connected.return_value = True  # Default is connected
    
    return mock_client

@pytest.fixture
def sample_chunks_with_embeddings() -> List[DocumentChunk]:
    """Provides sample DocumentChunk objects with embeddings."""
    return [
        DocumentChunk(chunk_id="d1_c1", document_id="d1", text="Chunk 1 text", metadata={'page_number': 1}, embedding=[0.1]*768),
        DocumentChunk(chunk_id="d1_c2", document_id="d1", text="Chunk 2 text", metadata={'page_number': 2}, embedding=[0.2]*768),
        DocumentChunk(chunk_id="d1_c3", document_id="d1", text="Chunk 3 no embedding", metadata={'page_number': 3}, embedding=None),
    ]

# --- Tests for get_weaviate_client --- #
def test_get_weaviate_client_success(mocker: MockerFixture, mock_weaviate_client_v4):
    """Tests successful connection returns the client."""
    # Arrange
    mocker.patch.dict(weaviate_client.config.__dict__, {"WEAVIATE_URL": "http://localhost:8080"})
    mock_weaviate_client_v4.is_ready.return_value = True

    # Act
    client = weaviate_client.get_weaviate_client()

    # Assert
    assert client == mock_weaviate_client_v4
    weaviate.connect_to_local.assert_called_once()
    client.connect.assert_called_once()

def test_get_weaviate_client_custom_url_success(mocker: MockerFixture, mock_weaviate_client_v4):
    """Tests successful connection with a custom URL."""
    mocker.patch.dict(weaviate_client.config.__dict__, {"WEAVIATE_URL": "http://otherhost:9090"})
    mock_weaviate_client_v4.is_ready.return_value = True

    client = weaviate_client.get_weaviate_client()

    assert client == mock_weaviate_client_v4
    weaviate.connect_to_custom.assert_called_once_with(
        http_host='otherhost', http_port=9090, http_secure=False,
        grpc_host='otherhost', grpc_port=50051, grpc_secure=False
    )
    client.connect.assert_called_once()

def test_get_weaviate_client_not_ready(mocker: MockerFixture, mock_weaviate_client_v4):
    """Tests WeaviateConnectionError if client is not ready."""
    mocker.patch.dict(weaviate_client.config.__dict__, {"WEAVIATE_URL": "http://localhost:8080"})
    mock_weaviate_client_v4.is_ready.return_value = False

    with pytest.raises(WeaviateConnectionError, match="is not ready"):
        weaviate_client.get_weaviate_client()

    mock_weaviate_client_v4.close.assert_called_once()

def test_get_weaviate_client_connect_exception(mocker: MockerFixture, mock_weaviate_client_v4):
    """Tests WeaviateConnectionError if connect() raises an exception."""
    mocker.patch.dict(weaviate_client.config.__dict__, {"WEAVIATE_URL": "http://localhost:8080"})
    mock_weaviate_client_v4.connect.side_effect = WeaviateBaseError("Connection refused")

    with pytest.raises(WeaviateConnectionError, match="Connection refused"):
        weaviate_client.get_weaviate_client()

    mock_weaviate_client_v4.close.assert_called_once()

# --- Tests for ensure_schema_exists --- #
def test_ensure_schema_exists_already_exists(mock_weaviate_client_v4):
    """Tests schema creation is skipped if collection exists."""
    mock_collections = mock_weaviate_client_v4.collections
    mock_collections.exists.return_value = True

    weaviate_client.ensure_schema_exists(mock_weaviate_client_v4)

    mock_collections.exists.assert_called_once_with(weaviate_client.CLASS_NAME)
    mock_collections.create.assert_not_called()

def test_ensure_schema_exists_creates_new(mock_weaviate_client_v4):
    """Tests schema creation is called if collection does not exist."""
    mock_collections = mock_weaviate_client_v4.collections
    mock_collections.exists.return_value = False

    weaviate_client.ensure_schema_exists(mock_weaviate_client_v4)

    mock_collections.exists.assert_called_once_with(weaviate_client.CLASS_NAME)
    mock_collections.create.assert_called_once()
    # Could add more detailed assertions on the args passed to create if needed

def test_ensure_schema_exists_creation_error(mock_weaviate_client_v4):
    """Tests WeaviateSchemaError is raised if creation fails."""
    mock_collections = mock_weaviate_client_v4.collections
    mock_collections.exists.return_value = False
    mock_collections.create.side_effect = WeaviateBaseError("Schema creation failed")

    with pytest.raises(WeaviateSchemaError, match="Failed to ensure Weaviate schema"):
        weaviate_client.ensure_schema_exists(mock_weaviate_client_v4)

# --- Tests for batch_import_chunks --- #
def test_batch_import_chunks_success(mocker: MockerFixture, mock_weaviate_client_v4, sample_chunks_with_embeddings):
    """Tests successful batch import with filtering."""
    mock_weaviate_client_v4.is_connected.return_value = True
    mock_collection = mock_weaviate_client_v4.collections.get.return_value

    # Mock the response from insert_many
    mock_response = mocker.MagicMock(spec=BatchObjectReturn)
    mock_response.has_errors = False
    mock_response.errors = {}
    mock_collection.data.insert_many.return_value = mock_response

    weaviate_client.batch_import_chunks(mock_weaviate_client_v4, sample_chunks_with_embeddings)

    mock_collection.data.insert_many.assert_called_once()
    # Check that only the 2 chunks with embeddings were prepared
    call_args = mock_collection.data.insert_many.call_args[0][0] # Get the list passed to insert_many
    assert len(call_args) == 2
    assert call_args[0].properties['chunk_id'] == "d1_c1"
    assert call_args[1].properties['chunk_id'] == "d1_c2"
    assert np.array_equal(call_args[0].vector, [0.1]*768)

def test_batch_import_chunks_not_connected(mock_weaviate_client_v4, sample_chunks_with_embeddings):
    """Tests WeaviateConnectionError if client is not connected."""
    mock_weaviate_client_v4.is_connected.return_value = False

    with pytest.raises(WeaviateConnectionError, match="Client is not connected"):
        weaviate_client.batch_import_chunks(mock_weaviate_client_v4, sample_chunks_with_embeddings)

def test_batch_import_chunks_empty_list(mock_weaviate_client_v4):
    """Tests that import is skipped for an empty list."""
    mock_weaviate_client_v4.is_connected.return_value = True
    mock_collection = mock_weaviate_client_v4.collections.get.return_value

    weaviate_client.batch_import_chunks(mock_weaviate_client_v4, [])

    mock_collection.data.insert_many.assert_not_called()

def test_batch_import_chunks_all_skipped(mock_weaviate_client_v4):
    """Tests that import is skipped if all chunks lack embeddings."""
    mock_weaviate_client_v4.is_connected.return_value = True
    mock_collection = mock_weaviate_client_v4.collections.get.return_value
    chunks_no_embeddings = [DocumentChunk(chunk_id="c1", document_id="d1", text="t", embedding=None)]

    weaviate_client.batch_import_chunks(mock_weaviate_client_v4, chunks_no_embeddings)

    mock_collection.data.insert_many.assert_not_called()

def test_batch_import_chunks_batch_errors(mocker: MockerFixture, mock_weaviate_client_v4, sample_chunks_with_embeddings):
    """Tests WeaviateStorageError if insert_many response has errors."""
    mock_weaviate_client_v4.is_connected.return_value = True
    mock_collection = mock_weaviate_client_v4.collections.get.return_value

    # Mock the response from insert_many with errors
    mock_response = mocker.MagicMock(spec=BatchObjectReturn)
    mock_response.has_errors = True
    mock_error = ErrorObject(message="Import failed", object_=None, original_uuid=None)
    mock_response.errors = {0: mock_error} # Simulate error for the first object
    mock_collection.data.insert_many.return_value = mock_response

    with pytest.raises(WeaviateStorageError, match="1 errors occurred"):
        weaviate_client.batch_import_chunks(mock_weaviate_client_v4, sample_chunks_with_embeddings)

    mock_collection.data.insert_many.assert_called_once()

def test_batch_import_chunks_weaviate_exception(mocker: MockerFixture, mock_weaviate_client_v4, sample_chunks_with_embeddings):
    """Tests WeaviateStorageError if insert_many raises a Weaviate error."""
    mock_weaviate_client_v4.is_connected.return_value = True
    mock_collection = mock_weaviate_client_v4.collections.get.return_value
    mock_collection.data.insert_many.side_effect = WeaviateBaseError("DB connection lost")

    with pytest.raises(WeaviateStorageError, match="DB connection lost"):
        weaviate_client.batch_import_chunks(mock_weaviate_client_v4, sample_chunks_with_embeddings)

    mock_collection.data.insert_many.assert_called_once() 