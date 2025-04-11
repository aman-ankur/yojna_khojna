import logging
from typing import List, Tuple, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
from ..schemas import DocumentChunk  # Assuming a schema file exists or will be created

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration for chunking
CHUNK_SIZE = 1000  # Target size of each chunk (in characters)
CHUNK_OVERLAP = 200 # Overlap between consecutive chunks (in characters)

def chunk_text(extracted_data: List[Tuple[int, str]], document_id: str) -> List[DocumentChunk]:
    """
    Splits extracted text from a document into smaller chunks.

    Args:
        extracted_data: A list of tuples, where each tuple contains the page number
                        (1-indexed) and the extracted text for that page.
        document_id: A unique identifier for the source document (e.g., filename or hash).

    Returns:
        A list of DocumentChunk objects, each representing a text chunk with metadata.
        Returns an empty list if input is empty or an error occurs.
    """
    if not extracted_data:
        logging.warning("Received empty extracted data for chunking.")
        return []

    all_chunks: List[DocumentChunk] = []
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        is_separator_regex=False, # Treat separators literally
        separators=["\n\n", "\n", ". ", " ", ""] # Prioritized list of separators
    )

    logging.info(f"Starting chunking process for document_id: {document_id}")
    total_pages = len(extracted_data)

    for page_num, page_text in extracted_data:
        if not page_text or page_text.isspace():
            logging.debug(f"Skipping empty page {page_num} for document_id: {document_id}")
            continue

        try:
            # Create documents for LangChain, including metadata
            # LangChain splitters work best with their Document object structure
            # We simulate this structure slightly differently here, splitting page by page
            chunks_on_page = text_splitter.split_text(page_text)

            num_chunks_on_page = len(chunks_on_page)
            for i, chunk_content in enumerate(chunks_on_page):
                chunk_id = f"{document_id}_page_{page_num}_chunk_{i+1}"
                chunk_metadata = {
                    "document_id": document_id,
                    "page_number": page_num,
                    "chunk_index_on_page": i + 1,
                    "total_chunks_on_page": num_chunks_on_page,
                    "total_document_pages": total_pages
                }
                # Create a DocumentChunk object (assuming this schema exists)
                # You might need to adjust this based on your actual schema definition
                document_chunk = DocumentChunk(
                    chunk_id=chunk_id,
                    document_id=document_id,
                    text=chunk_content,
                    metadata=chunk_metadata
                )
                all_chunks.append(document_chunk)

            logging.debug(f"Page {page_num} (doc: {document_id}) split into {num_chunks_on_page} chunks.")

        except Exception as e:
            logging.error(f"Error chunking page {page_num} for document_id: {document_id}: {e}", exc_info=True)
            # Decide whether to skip the page or halt processing

    logging.info(f"Completed chunking for document_id: {document_id}. Total chunks created: {len(all_chunks)}")
    return all_chunks

# Example of a Pydantic schema (adjust as needed)
# You would typically place this in a schemas.py file
# from pydantic import BaseModel, Field
# from typing import Dict, Any
# class DocumentChunk(BaseModel):
#     chunk_id: str = Field(..., description="Unique identifier for the chunk")
#     document_id: str = Field(..., description="Identifier of the source document")
#     text: str = Field(..., description="The actual text content of the chunk")
#     metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata associated with the chunk (e.g., page number)")

# Example usage (if run directly)
if __name__ == '__main__':
    print("Document Chunker Module")
    # Dummy data simulating output from pdf_extractor
    dummy_extracted_data = [
        (1, "This is the first page. It contains some introductory text.\n\nHere is a second paragraph."),
        (2, "This is the second page. It has more details. Sentence 1. Sentence 2. Sentence 3 is a bit longer and might be split."),
        (3, "A short third page.")
    ]
    dummy_doc_id = "example_document_123"

    print(f"\nChunking document: {dummy_doc_id}")
    chunks = chunk_text(dummy_extracted_data, dummy_doc_id)

    if chunks:
        print(f"\n--- Generated Chunks ({len(chunks)}) ---")
        for i, chunk in enumerate(chunks):
            print(f"\n--- Chunk {i+1} (ID: {chunk.chunk_id}) ---")
            print(f"Source: Page {chunk.metadata.get('page_number')}")
            print(f"Text: '{chunk.text[:100]}...'") # Print start of text
            # print(f"Metadata: {chunk.metadata}") # Uncomment to see full metadata
    else:
        print("\nNo chunks were generated.")

    # Test with empty input
    print("\nTesting with empty input...")
    empty_chunks = chunk_text([], "empty_doc_id")
    print(f"Chunks generated from empty input: {len(empty_chunks)}")

    # Test with input containing empty page
    print("\nTesting with input containing an empty page...")
    data_with_empty_page = [
        (1, "Page one content."),
        (2, "   "), # Empty page
        (3, "Page three content.")
    ]
    chunks_with_empty = chunk_text(data_with_empty_page, "doc_with_empty_page")
    print(f"Chunks generated (should skip page 2): {len(chunks_with_empty)}")
    page_numbers = {chunk.metadata.get('page_number') for chunk in chunks_with_empty}
    print(f"Pages included in chunks: {page_numbers}") # Should be {1, 3} 