import pytest
from unittest.mock import MagicMock, patch
import numpy as np
from backend.src.schemas import DocumentChunk
from backend.src.data_pipeline import embedding_generator
from backend.src.vector_db import weaviate_client
from backend.src.exceptions import EmbeddingGenerationError, WeaviateStorageError

@pytest.fixture
def sample_document_chunks():
    """Create sample document chunks for testing."""
    return [
        DocumentChunk(
            chunk_id="test_chunk_1",
            document_id="test_doc_1",
            text="This is a sample chunk for testing the pipeline.",
            metadata={"page_number": 1}
        ),
        DocumentChunk(
            chunk_id="test_chunk_2",
            document_id="test_doc_1",
            text="This is another sample chunk with different content.",
            metadata={"page_number": 2}
        ),
        DocumentChunk(
            chunk_id="test_chunk_3", 
            document_id="test_doc_2",
            text="This chunk is from a different document.",
            metadata={"page_number": 1}
        )
    ]

@pytest.mark.integration
def test_embedding_and_storage_pipeline(sample_document_chunks):
    """
    Integration test for the full pipeline from document chunks to embedding generation
    to storage in the vector database.
    """
    # Mock the embedding model
    with patch.object(embedding_generator, 'model') as mock_model:
        # Set up mock embeddings - 3 samples with 4-dimensional vectors
        mock_embeddings = np.array([
            [0.1, 0.2, 0.3, 0.4],
            [0.5, 0.6, 0.7, 0.8],
            [0.9, 0.8, 0.7, 0.6]
        ])
        mock_model.encode.return_value = mock_embeddings
        
        # Mock the Weaviate client
        with patch.object(weaviate_client, 'get_weaviate_client') as mock_client_fn:
            mock_client = MagicMock()
            mock_client_fn.return_value = mock_client
            mock_client.is_connected.return_value = True
            
            # Mock collections
            mock_collection = MagicMock()
            mock_client.collections.get.return_value = mock_collection
            mock_client.collections.exists.return_value = True
            
            # Mock successful batch import
            mock_response = MagicMock()
            mock_response.has_errors = False
            mock_collection.data.insert_many.return_value = mock_response
            
            # Execute the pipeline
            # Step 1: Generate embeddings
            chunks_with_embeddings = embedding_generator.generate_embeddings(sample_document_chunks)
            
            # Verify embeddings were added
            assert len(chunks_with_embeddings) == 3
            assert all(chunk.embedding is not None for chunk in chunks_with_embeddings)
            assert len(chunks_with_embeddings[0].embedding) == 4
            
            # Step 2: Ensure schema exists
            weaviate_client.ensure_schema_exists(mock_client)
            
            # Step 3: Store chunks in vector database
            weaviate_client.batch_import_chunks(mock_client, chunks_with_embeddings, "test_hash_pipeline")
            
            # Verify the entire pipeline completed as expected
            mock_model.encode.assert_called_once()
            mock_client.collections.exists.assert_called_once()
            mock_collection.data.insert_many.assert_called_once()
            
            # Verify the objects passed to insert_many contain the correct data
            args, _ = mock_collection.data.insert_many.call_args
            inserted_objects = args[0]
            assert len(inserted_objects) == 3
            
            # Check the first object's properties
            # This is implementation-specific and depends on how batch_import_chunks creates objects
            # This test might need to be adjusted based on the actual implementation

@pytest.mark.integration
def test_pipeline_with_embedding_error(sample_document_chunks):
    """Test pipeline error handling when embedding generation fails."""
    with patch.object(embedding_generator, 'model') as mock_model:
        # Simulate embedding generation failure
        mock_model.encode.side_effect = RuntimeError("Embedding model failed")
        
        # Attempt to execute the pipeline
        with pytest.raises(EmbeddingGenerationError):
            embedding_generator.generate_embeddings(sample_document_chunks)

@pytest.mark.integration
def test_pipeline_with_storage_error(sample_document_chunks):
    """Test pipeline error handling when storage fails."""
    # Mock embedding generation to succeed
    with patch.object(embedding_generator, 'model') as mock_model:
        mock_embeddings = np.array([
            [0.1, 0.2, 0.3, 0.4],
            [0.5, 0.6, 0.7, 0.8],
            [0.9, 0.8, 0.7, 0.6]
        ])
        mock_model.encode.return_value = mock_embeddings
        
        # Generate embeddings
        chunks_with_embeddings = embedding_generator.generate_embeddings(sample_document_chunks)
        
        # Mock Weaviate to fail on import
        with patch.object(weaviate_client, 'get_weaviate_client') as mock_client_fn:
            mock_client = MagicMock()
            mock_client_fn.return_value = mock_client
            mock_client.is_connected.return_value = True
            
            # Mock collections
            mock_collection = MagicMock()
            mock_client.collections.get.return_value = mock_collection
            
            # Mock batch import failure
            mock_response = MagicMock()
            mock_response.has_errors = True
            mock_response.errors = {0: MagicMock(message="Storage error")}
            mock_collection.data.insert_many.return_value = mock_response
            
            # Attempt to store the chunks
            with pytest.raises(WeaviateStorageError):
                # Pass a dummy hash for testing purposes
                weaviate_client.batch_import_chunks(mock_client, chunks_with_embeddings, "test_hash_error")
                
            # Verify error handling
            mock_collection.data.insert_many.assert_called_once() 