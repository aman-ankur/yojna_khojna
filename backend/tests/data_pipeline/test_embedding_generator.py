import pytest
from pytest_mock import MockerFixture
import numpy as np
from typing import List, Optional
from unittest.mock import MagicMock
from backend.src.schemas import DocumentChunk
from backend.src.exceptions import EmbeddingGenerationError

# Define a config fixture before importing the module to test
@pytest.fixture(scope="function", autouse=True)
def mock_config(monkeypatch):
    """Mock the config module to avoid using real configuration during tests."""
    mock_config = MagicMock()
    mock_config.EMBEDDING_MODEL_NAME = "test-embedding-model"
    monkeypatch.setattr("backend.src.config.EMBEDDING_MODEL_NAME", "test-embedding-model")
    return mock_config

# Only import the module AFTER we've defined the config fixture to avoid
# importing with real config during test collection
from backend.src.data_pipeline import embedding_generator

# Add a mock for the model to avoid the module-level exception
@pytest.fixture(scope="function", autouse=True)
def patch_model(monkeypatch):
    """Patch the model at the module level to avoid import error."""
    mock_model = MagicMock()
    # Pre-define the encode method on the mock
    mock_model.encode = MagicMock()
    monkeypatch.setattr("backend.src.data_pipeline.embedding_generator.model", mock_model)
    
    # Reset side effects that might be set by individual tests
    yield
    if hasattr(mock_model.encode, "side_effect"):
        mock_model.encode.side_effect = None

# Sample Chunks for testing
@pytest.fixture
def sample_chunks() -> List[DocumentChunk]:
    return [
        DocumentChunk(chunk_id="d1_c1", document_id="d1", text="This is the first chunk.", metadata={'page_number': 1}),
        DocumentChunk(chunk_id="d1_c2", document_id="d1", text="यह दूसरा खंड है।", metadata={'page_number': 1}),
        DocumentChunk(chunk_id="d2_c1", document_id="d2", text="Final chunk here.", metadata={'page_number': 5}),
    ]

# Test successful embedding generation
def test_generate_embeddings_success(mocker: MockerFixture, sample_chunks: List[DocumentChunk]):
    """Tests that embeddings are added correctly when model encode works."""
    # Create a mock without autospec to avoid the encode attribute issue
    mock_model = MagicMock()
    # Simulate the output of model.encode
    mock_embeddings = np.array([
        [0.1, 0.2, 0.3],
        [0.4, 0.5, 0.6],
        [0.7, 0.8, 0.9]
    ])
    mock_model.encode.return_value = mock_embeddings
    # Set the mock model
    mocker.patch("backend.src.data_pipeline.embedding_generator.model", mock_model)

    # Run the function
    result_chunks = embedding_generator.generate_embeddings(sample_chunks)

    # Assertions
    assert len(result_chunks) == 3
    mock_model.encode.assert_called_once_with([chunk.text for chunk in sample_chunks], show_progress_bar=True)
    # Check that each chunk has the embedding added (and converted to list)
    assert result_chunks[0].embedding == [0.1, 0.2, 0.3]
    assert result_chunks[1].embedding == [0.4, 0.5, 0.6]
    assert result_chunks[2].embedding == [0.7, 0.8, 0.9]
    assert result_chunks[0].chunk_id == "d1_c1" # Ensure original chunk data is preserved

# Test handling of empty input list
def test_generate_embeddings_empty_list(mocker: MockerFixture):
    """Tests that an empty list is returned when input is empty."""
    # Create a mock without autospec
    mock_model = MagicMock()
    mocker.patch("backend.src.data_pipeline.embedding_generator.model", mock_model)

    result_chunks = embedding_generator.generate_embeddings([])

    assert result_chunks == []
    mock_model.encode.assert_not_called()

# Test exception handling when model.encode fails
def test_generate_embeddings_encode_error(mocker: MockerFixture, sample_chunks: List[DocumentChunk]):
    """Tests that EmbeddingGenerationError is raised if model.encode fails."""
    # Create a mock without autospec
    mock_model = MagicMock()
    mock_model.encode.side_effect = RuntimeError("Model encoding failed!")
    mocker.patch("backend.src.data_pipeline.embedding_generator.model", mock_model)

    with pytest.raises(EmbeddingGenerationError, match="An error occurred during embedding generation: Model encoding failed!"):
        embedding_generator.generate_embeddings(sample_chunks)

    mock_model.encode.assert_called_once()

# Note: Testing the EmbeddingModelError raised at module load is tricky
# because the error occurs when this test file imports the module.
# A separate test strategy might be needed if explicitly testing that specific raise is critical. 