import logging
from pathlib import Path
from typing import Optional, List

# Import functions from our data pipeline modules
from .data_pipeline.pdf_extractor import extract_text_from_pdf
from .data_pipeline.document_chunker import chunk_text
from .data_pipeline.embedding_generator import generate_embeddings
from .schemas import DocumentChunk # Assuming schemas.py is in the same directory (src)
# Import Weaviate client functions
from .vector_db.weaviate_client import get_weaviate_client, ensure_schema_exists, batch_import_chunks

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_pdf(pdf_path: Path) -> Optional[List[DocumentChunk]]:
    """
    Processes a single PDF file: extracts text, chunks it, and generates embeddings.

    Args:
        pdf_path: The path to the PDF file.

    Returns:
        A list of DocumentChunk objects if successful, otherwise None.
    """
    logging.info(f"Starting processing for PDF: {pdf_path.name}")

    # 1. Extract text from PDF
    extracted_data = extract_text_from_pdf(pdf_path)

    if not extracted_data:
        logging.error(f"Failed to extract text from {pdf_path.name}. Skipping further processing.")
        return None

    logging.info(f"Successfully extracted text from {len(extracted_data)} pages in {pdf_path.name}.")

    # Generate a document ID (using filename without extension for simplicity)
    document_id = pdf_path.stem

    # 2. Chunk the extracted text
    try:
        chunks = chunk_text(extracted_data=extracted_data, document_id=document_id)
    except Exception as e:
        logging.error(f"Failed to chunk text for {document_id}: {e}", exc_info=True)
        return None

    if not chunks:
        logging.warning(f"No chunks were generated for document {document_id}, though text was extracted.")
        # Decide if this is an error or acceptable state - returning chunks for now

    logging.info(f"Successfully generated {len(chunks)} chunks for document {document_id}.")

    # 3. Generate Embeddings for the chunks
    try:
        chunks_with_embeddings = generate_embeddings(chunks)
        # Check if embeddings were actually added (model might have failed to load)
        if chunks_with_embeddings and chunks_with_embeddings[0].embedding is not None:
            logging.info(f"Successfully generated embeddings for {len(chunks_with_embeddings)} chunks.")
        else:
            logging.warning(f"Embeddings were not generated for document {document_id}. Check logs for model loading issues.")
        return chunks_with_embeddings # Return chunks potentially with embeddings
    except Exception as e:
        logging.error(f"Failed during embedding generation for {document_id}: {e}", exc_info=True)
        return chunks # Return original chunks if embedding fails


if __name__ == '__main__':
    print("Main Data Pipeline Runner")

    # --- Configuration --- #
    # IMPORTANT: Update this path to point to a real PDF file in your test_docs folder
    # Make sure the test_docs folder exists relative to where you run the script
    # or provide an absolute path.
    # Running this script from the 'backend' directory means the path is relative to 'backend'
    # test_pdf_to_process = Path("./../test_docs/small_awaas_yojna.pdf") # Example path relative to backend dir
    # Alternative: Absolute Path
    test_pdf_to_process = Path("/Users/aankur/workspace/yojna_khojna/backend/test_docs/small_awaas_yojna.pdf")
    # --- End Configuration --- #

    # Create test_docs directory if it doesn't exist (relative to workspace root)
    workspace_root = Path(__file__).parent.parent # Get workspace root assuming structure proj/backend/src
    test_docs_dir = workspace_root / "test_docs"
    if not test_docs_dir.exists():
        logging.info(f"Creating directory: {test_docs_dir}")
        test_docs_dir.mkdir(parents=True, exist_ok=True)

    if not test_pdf_to_process.exists():
        # Check relative to workspace root if not found relative to backend
        relative_to_workspace_path = workspace_root / test_pdf_to_process.name
        if relative_to_workspace_path.exists():
            test_pdf_to_process = relative_to_workspace_path
        else:
             print(f"\n--- ERROR ---")
             print(f"Test PDF file not found at the specified path: {test_pdf_to_process}")
             print(f"Please ensure the file exists or update the 'test_pdf_to_process' variable in the script.")
             print(f"Also looked for: {relative_to_workspace_path}")
             print(f"Make sure the 'test_docs' directory exists and contains your test PDF.")
    else:
        print(f"\nAttempting to process PDF: {test_pdf_to_process}")
        generated_chunks = process_pdf(test_pdf_to_process)

        if generated_chunks:
            print(f"\n--- Processing Summary for {test_pdf_to_process.name} ({len(generated_chunks)} chunks) ---")
            # Optionally print details of the first few chunks
            for i, chunk in enumerate(generated_chunks[:3]): # Print first 3 chunks
                print(f"\n Chunk {i+1} (ID: {chunk.chunk_id}) ")
                print(f" Page: {chunk.metadata.get('page_number')}")
                print(f" Text: '{chunk.text[:100]}...'" ) # Show start of text
                # Check and display embedding info
                if chunk.embedding:
                    print(f" Embedding: Generated (Dim: {len(chunk.embedding)}, First 5: {chunk.embedding[:5]})")
                else:
                    print(f" Embedding: Not generated")

            if len(generated_chunks) > 3:
                print("\n ... [additional chunks not shown] ...")

            # --- Weaviate Integration --- #
            print("\n--- Attempting to store results in Weaviate --- ")
            weaviate_client = get_weaviate_client() # Use default URL from weaviate_client.py
            try:
                if weaviate_client:
                    # Ensure the schema (class) exists in Weaviate
                    ensure_schema_exists(weaviate_client)

                    # Filter chunks that actually have embeddings (should be all if model worked)
                    chunks_to_import = [chunk for chunk in generated_chunks if chunk.embedding is not None]

                    if chunks_to_import:
                        # Import the chunks into Weaviate
                        batch_import_chunks(weaviate_client, chunks_to_import)
                    else:
                        print("No chunks with embeddings found to import.")
                else:
                    print("Failed to connect to Weaviate. Skipping data import.")
            finally:
                if weaviate_client:
                    weaviate_client.close()
                    print("Weaviate client connection closed.")
            # --- End Weaviate Integration --- #

        else:
            print(f"\n--- Processing Failed for {test_pdf_to_process.name} --- ")
            print(" Check logs for error details.") 