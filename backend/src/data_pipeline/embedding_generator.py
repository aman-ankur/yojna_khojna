import logging
from typing import List, Optional
from sentence_transformers import SentenceTransformer
from ..schemas import DocumentChunk
import numpy as np
from .. import config
# Import custom exceptions
from ..exceptions import EmbeddingModelError, EmbeddingGenerationError

# Get logger instance
logger = logging.getLogger(__name__)

# Load the model only once when the module is loaded
model: Optional[SentenceTransformer] = None # Initialize model as None with type hint
model_name = config.EMBEDDING_MODEL_NAME

try:
    logger.info(f"Loading Sentence Transformer model: {model_name}")
    model = SentenceTransformer(model_name)
    logger.info(f"Sentence Transformer model '{model_name}' loaded successfully.")
except Exception as e:
    logger.error(f"Failed to load Sentence Transformer model '{model_name}': {e}", exc_info=True)
    # Raise immediately so failure is clear if the module is imported
    raise EmbeddingModelError(f"Failed to load Sentence Transformer model '{model_name}': {e}") from e

def generate_embeddings(chunks: List[DocumentChunk]) -> List[DocumentChunk]:
    """
    Generates vector embeddings for the text content of each DocumentChunk.

    Args:
        chunks: A list of DocumentChunk objects.

    Returns:
        The same list of DocumentChunk objects, with the 'embedding' field populated.

    Raises:
        EmbeddingModelError: If the embedding model was not loaded successfully.
        EmbeddingGenerationError: If an error occurs during the embedding process.
    """
    if model is None:
        # This case should theoretically not be reached if the module loaded successfully
        # due to the raise in the loading block, but check defensively.
        logger.error("Embedding model is not available. Cannot generate embeddings.")
        raise EmbeddingModelError("Embedding model was not loaded successfully.")

    if not chunks:
        logger.info("No chunks provided for embedding generation.")
        return []

    texts_to_embed = [chunk.text for chunk in chunks]
    logger.info(f"Generating embeddings for {len(texts_to_embed)} chunks using model '{model_name}'...")

    try:
        # Generate embeddings. The model's encode method returns numpy arrays.
        embeddings_np = model.encode(texts_to_embed, show_progress_bar=True)

        # Convert numpy arrays to lists and update chunks
        for i, chunk in enumerate(chunks):
            chunk.embedding = embeddings_np[i].tolist() # Convert numpy array to list for JSON serialization

        logger.info(f"Embeddings generated successfully for {len(chunks)} chunks.")
        return chunks

    except Exception as e:
        logger.error(f"Error generating embeddings: {e}", exc_info=True)
        # Wrap the original exception
        raise EmbeddingGenerationError(f"An error occurred during embedding generation: {e}") from e

# Basic testing block
if __name__ == '__main__':
    # This block needs to handle the potential EmbeddingModelError at module load time
    # and the errors from generate_embeddings.
    # We assume the model loaded okay if we reach this point without the script exiting.
    print("Running basic embedding generator test...")

    # Create some dummy DocumentChunk objects
    test_chunks = [
        DocumentChunk(chunk_id="doc1_chunk1", document_id="doc1", text="यह पहला परीक्षण खंड है।"),
        DocumentChunk(chunk_id="doc1_chunk2", document_id="doc1", text="This is the second test chunk."),
        DocumentChunk(chunk_id="doc2_chunk1", document_id="doc2", text="एक और दस्तावेज़ से खंड।"),
    ]

    try:
        # Generate embeddings
        chunks_with_embeddings = generate_embeddings(test_chunks)

        # Verify embeddings were added
        if chunks_with_embeddings and all(chunk.embedding is not None for chunk in chunks_with_embeddings):
            print(f"Successfully generated embeddings for {len(chunks_with_embeddings)} chunks.")
            first_embedding_sample = chunks_with_embeddings[0].embedding[:5] # Show first 5 dimensions
            print(f"Sample embedding (first 5 dims of first chunk): {first_embedding_sample}")
            print(f"Embedding dimension: {len(chunks_with_embeddings[0].embedding)}")
        else:
            # This case might be less likely now due to exceptions being raised
            print("Embeddings were not generated for some reason (check logs).")

    except EmbeddingGenerationError as e:
        print(f"ERROR during embedding generation test: {e}")
    except EmbeddingModelError as e:
        # This specific exception might not be caught here if raised at module load,
        # but catching it defensively in case the logic changes.
        print(f"ERROR: Embedding model seems unavailable: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during the test: {e}")

    print("Basic test finished.") 