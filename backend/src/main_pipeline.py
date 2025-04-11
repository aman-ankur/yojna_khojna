import logging
from pathlib import Path
from typing import Optional, List

# Import functions from our data pipeline modules
from .data_pipeline.pdf_extractor import extract_text_from_pdf
from .data_pipeline.document_chunker import chunk_text
from .schemas import DocumentChunk # Assuming schemas.py is in the same directory (src)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_pdf(pdf_path: Path) -> Optional[List[DocumentChunk]]:
    """
    Processes a single PDF file: extracts text and chunks it.

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
    return chunks


if __name__ == '__main__':
    print("Main Data Pipeline Runner")

    # --- Configuration --- #
    # IMPORTANT: Update this path to point to a real PDF file in your test_docs folder
    # Make sure the test_docs folder exists relative to where you run the script
    # or provide an absolute path.
    # Running this script from the 'backend' directory means the path is relative to 'backend'
    test_pdf_to_process = Path("./test_docs/small_awaas_yojna.pdf") # Example path relative to backend dir
    # Alternative: Absolute Path
    # test_pdf_to_process = Path("/Users/aankur/workspace/yojna_khojna/test_docs/small_awaas_yojna.pdf")
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
                print(f" Text: '{chunk.text[:150]}...'" ) # Show start of text
            if len(generated_chunks) > 3:
                print("\n ... [additional chunks not shown] ...")
        else:
            print(f"\n--- Processing Failed for {test_pdf_to_process.name} --- ")
            print(" Check logs for error details.") 