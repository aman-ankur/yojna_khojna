import logging
from pathlib import Path
from typing import Optional, List
import sys # Import sys for exit

# Import pipeline functions & schemas
from .data_pipeline.pdf_extractor import extract_text_from_pdf # Assuming this has basic error handling
from .data_pipeline.document_chunker import chunk_text # Assuming this has basic error handling
from .data_pipeline.embedding_generator import generate_embeddings # Now raises exceptions
from .schemas import DocumentChunk
from .vector_db.weaviate_client import get_weaviate_client, ensure_schema_exists, batch_import_chunks # Now raises exceptions
from . import config # Loads env vars and sets up logging
# Import custom exceptions
from .exceptions import (
    PipelineError,
    PDFProcessingError, # Placeholder, assuming pdf_extractor raises this
    ChunkingError,      # Placeholder, assuming document_chunker raises this
    EmbeddingModelError,
    EmbeddingGenerationError,
    WeaviateConnectionError,
    WeaviateSchemaError,
    WeaviateStorageError
)

# Get logger instance - logging is configured in config.py
logger = logging.getLogger(__name__)
# Removed old basicConfig call

def process_pdf(pdf_path: Path) -> Optional[List[DocumentChunk]]:
    """
    Processes a single PDF file: extracts text, chunks it, generates embeddings.
    Logs errors and raises PipelineError or its subclasses upon failure.

    Args:
        pdf_path: The path to the PDF file.

    Returns:
        A list of DocumentChunk objects with embeddings if successful.

    Raises:
        PipelineError: If any step in the processing fails.
    """
    logger.info(f"Starting processing for PDF: {pdf_path.name}")
    document_id = pdf_path.stem

    # 1. Extract text from PDF
    try:
        # Assuming pdf_extractor is refactored to raise PDFProcessingError
        extracted_data = extract_text_from_pdf(pdf_path)
        if not extracted_data:
            # Handle case where extraction returns empty but no exception
            logger.error(f"No text data extracted from {pdf_path.name}. Skipping further processing.")
            raise PDFProcessingError(f"No text data extracted from {pdf_path.name}")
        logger.info(f"Successfully extracted text from {len(extracted_data)} pages in {pdf_path.name}.")
    except Exception as e:
        # Catch generic Exception temporarily if pdf_extractor not refactored
        logger.error(f"Failed to extract text from {document_id}: {e}", exc_info=True)
        raise PDFProcessingError(f"Failed during PDF text extraction for {document_id}: {e}") from e

    # 2. Chunk the extracted text
    try:
        # Assuming document_chunker is refactored to raise ChunkingError
        chunks = chunk_text(extracted_data=extracted_data, document_id=document_id)
        if not chunks:
            # Log warning but proceed if chunking yields empty list (might be valid for small docs)
            logger.warning(f"No chunks were generated for document {document_id}, though text was extracted.")
        logger.info(f"Successfully generated {len(chunks)} chunks for document {document_id}.")
    except Exception as e:
         # Catch generic Exception temporarily if document_chunker not refactored
        logger.error(f"Failed to chunk text for {document_id}: {e}", exc_info=True)
        raise ChunkingError(f"Failed during text chunking for {document_id}: {e}") from e

    # Handle case where no chunks generated (even if not an error)
    if not chunks:
        logger.warning(f"Skipping embedding and storage for {document_id} as no chunks were generated.")
        return [] # Return empty list, not None, to indicate processing finished but yielded no chunks

    # 3. Generate Embeddings for the chunks
    try:
        chunks_with_embeddings = generate_embeddings(chunks)
        logger.info(f"Successfully generated embeddings for {len(chunks_with_embeddings)} chunks for document {document_id}.")
        return chunks_with_embeddings
    except (EmbeddingModelError, EmbeddingGenerationError) as e:
        # Catch specific embedding errors raised by the generator
        logger.error(f"Failed during embedding generation for {document_id}: {e}", exc_info=True)
        raise # Re-raise the original exception
    except Exception as e:
        # Catch unexpected errors during embedding
        logger.error(f"Unexpected error during embedding generation for {document_id}: {e}", exc_info=True)
        raise EmbeddingGenerationError(f"Unexpected error during embedding for {document_id}: {e}") from e

def run_pipeline():
    """Runs the main pipeline for a single PDF specified in config, handling errors."""
    logger.info("Starting Main Data Pipeline Runner")
    weaviate_client = None # Ensure client is defined for finally block

    try:
        # --- Configuration & Setup --- #
        test_pdf_to_process = config.get_default_test_pdf_path()
        logger.info(f"Using test PDF path from config: {test_pdf_to_process}")

        test_docs_dir = test_pdf_to_process.parent
        if not test_docs_dir.exists():
            try:
                logger.info(f"Creating directory: {test_docs_dir}")
                test_docs_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logger.error(f"Failed to create directory {test_docs_dir}: {e}", exc_info=True)
                raise PipelineError(f"Failed to create directory {test_docs_dir}") from e

        if not test_pdf_to_process.exists():
            logger.error(f"Test PDF file configured in .env (DEFAULT_TEST_PDF) not found at: {test_pdf_to_process}")
            raise FileNotFoundError(f"Test PDF not found at {test_pdf_to_process}")

        # --- PDF Processing --- #
        logger.info(f"Attempting to process PDF: {test_pdf_to_process}")
        generated_chunks = process_pdf(test_pdf_to_process)

        # --- Weaviate Integration --- #
        if generated_chunks: # Only attempt Weaviate if chunks exist
            logger.info(f"Attempting to store {len(generated_chunks)} results in Weaviate...")
            weaviate_client = get_weaviate_client() # Raises WeaviateConnectionError on failure

            ensure_schema_exists(weaviate_client) # Raises WeaviateSchemaError on failure

            # Filter chunks with embeddings (should be all unless embedding failed, caught above)
            chunks_to_import = [chunk for chunk in generated_chunks if chunk.embedding is not None]

            if chunks_to_import:
                batch_import_chunks(weaviate_client, chunks_to_import) # Raises WeaviateStorageError
                logger.info(f"Weaviate storage completed for {test_pdf_to_process.name}.")
            else:
                logger.warning("No chunks with embeddings found to import (check previous logs).")
        else:
             logger.warning(f"Skipping Weaviate storage for {test_pdf_to_process.name} as no chunks were generated.")

        logger.info(f"Pipeline finished successfully for {test_pdf_to_process.name}.")

    # --- Error Handling for the entire pipeline run --- #
    except FileNotFoundError as e:
        logger.error(f"Pipeline aborted: {e}")
        # No further action needed, error logged
    except (PDFProcessingError, ChunkingError, EmbeddingModelError, EmbeddingGenerationError) as e:
        logger.error(f"Pipeline failed during document processing: {e}", exc_info=True)
        # Error specific to document processing logged by process_pdf
    except (WeaviateConnectionError, WeaviateSchemaError, WeaviateStorageError) as e:
        logger.error(f"Pipeline failed during Weaviate operation: {e}", exc_info=True)
        # Specific Weaviate error logged by weaviate_client functions
    except PipelineError as e:
        # Catch base pipeline errors (like directory creation failure)
        logger.error(f"Pipeline failed: {e}", exc_info=True)
    except Exception as e:
        # Catch any truly unexpected errors
        logger.critical(f"An unexpected critical error occurred in the pipeline: {e}", exc_info=True)
    finally:
        # --- Cleanup --- #
        if weaviate_client and weaviate_client.is_connected():
            weaviate_client.close()
            logger.info("Weaviate client connection closed.")
        logger.info("Pipeline runner finished.")

if __name__ == '__main__':
    run_pipeline() 