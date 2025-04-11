import logging
from typing import List
from sentence_transformers import SentenceTransformer
from ..schemas import DocumentChunk
import numpy as np
from .. import config # Import the config module

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load the model only once when the module is loaded
model = None # Initialize model as None
model_name = config.EMBEDDING_MODEL_NAME # Get model name from config

try:
    logging.info(f"Loading Sentence Transformer model: {model_name}")
    model = SentenceTransformer(model_name)
    logging.info(f"Sentence Transformer model '{model_name}' loaded successfully.")
except Exception as e:
    logging.error(f"Failed to load Sentence Transformer model '{model_name}': {e}")
    # model remains None

def generate_embeddings(chunks: List[DocumentChunk]) -> List[DocumentChunk]:
    """
    Generates vector embeddings for the text content of each DocumentChunk.

    Args:
        chunks: A list of DocumentChunk objects.

    Returns:
        The same list of DocumentChunk objects, with the 'embedding' field populated.
        Returns the original list without embeddings if the model failed to load.
    """
    if model is None:
        logging.error("Embedding model is not available. Skipping embedding generation.")
        return chunks

    if not chunks:
        logging.info("No chunks provided for embedding generation.")
        return []

    texts_to_embed = [chunk.text for chunk in chunks]
    logging.info(f"Generating embeddings for {len(texts_to_embed)} chunks...")

    try:
        # Generate embeddings. The model's encode method returns numpy arrays.
        embeddings_np = model.encode(texts_to_embed, show_progress_bar=True)

        # Convert numpy arrays to lists and update chunks
        for i, chunk in enumerate(chunks):
            chunk.embedding = embeddings_np[i].tolist() # Convert numpy array to list for JSON serialization

        logging.info("Embeddings generated successfully.")
        return chunks

    except Exception as e:
        logging.error(f"Error generating embeddings: {e}")
        # Return chunks without embeddings in case of error
        return chunks

# Basic testing block
if __name__ == '__main__':
    print("Running basic embedding generator test...")

    # Create some dummy DocumentChunk objects
    test_chunks = [
        DocumentChunk(chunk_id="doc1_chunk1", document_id="doc1", text="यह पहला परीक्षण खंड है।"),
        DocumentChunk(chunk_id="doc1_chunk2", document_id="doc1", text="This is the second test chunk."),
        DocumentChunk(chunk_id="doc2_chunk1", document_id="doc2", text="एक और दस्तावेज़ से खंड।"),
    ]

    # Generate embeddings
    chunks_with_embeddings = generate_embeddings(test_chunks)

    # Verify embeddings were added
    if chunks_with_embeddings and all(chunk.embedding is not None for chunk in chunks_with_embeddings):
        print(f"Successfully generated embeddings for {len(chunks_with_embeddings)} chunks.")
        first_embedding_sample = chunks_with_embeddings[0].embedding[:5] # Show first 5 dimensions
        print(f"Sample embedding (first 5 dims of first chunk): {first_embedding_sample}")
        print(f"Embedding dimension: {len(chunks_with_embeddings[0].embedding)}")
    elif model is None:
         print("Test skipped because the embedding model failed to load.")
    else:
        print("Failed to generate embeddings for some or all chunks.")

    print("Basic test finished.") 