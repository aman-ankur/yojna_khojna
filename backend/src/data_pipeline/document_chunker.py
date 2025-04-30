import logging
import re
import uuid
from typing import List, Tuple, Optional, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter
from ..schemas import DocumentChunk

# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# Use getLogger instead, configuration is handled centrally
logger = logging.getLogger(__name__)

# Configuration for chunking
CHUNK_SIZE = 1000  # Target size of each chunk (in characters) - Keep as is for now
CHUNK_OVERLAP = 250 # Overlap between consecutive chunks - Increased slightly for better context around splits
# Define separators for the enhanced strategy
# Priority: Section breaks, then paragraphs, then lines, etc.
SEPARATORS = [
    "__SECTION_BREAK__", # Custom marker for section starts
    "\n\n",
    "\n",
    ". ", "? ", "! ", # Sentences
    ", ",
    " ",
    ""
]

# Regex patterns
# Table pattern: Captures the entire block from start to end marker
TABLE_PATTERN = re.compile(r"(\[TABLE_START:.*?\]\n*.*?\n*^\[TABLE_END\])", re.MULTILINE | re.DOTALL)
# Section Header patterns (English and Hindi): Capture preceding ^ or \n\n (Group 1) and header text (Group 2)
# Use positive lookahead for trailing newline
SECTION_HEADER_PATTERN_EN = re.compile(r"((?:^|\n\n))\s*(Section\s+\d+(?:\.\d+)*\.\s+.*?)(?=\n)")
SECTION_HEADER_PATTERN_HI = re.compile(r"((?:^|\n\n))\s*(खंड\s+\d+(?:\.\d+)*\.\s+.*?)(?=\n)") # Assuming 'खंड' for Section

def _preprocess_text(text: str) -> Tuple[str, Dict[str, str]]:
    """
    Preprocesses text by replacing tables with placeholders and inserting section break markers.

    Returns:
        A tuple containing:
            - The modified text with placeholders and markers.
            - A dictionary mapping placeholders to original table content.
    """
    placeholder_map = {}
    processed_text = text

    # Replace tables with placeholders
    def replace_table(match):
        table_content = match.group(1)
        placeholder = f"__TABLE_{uuid.uuid4().hex[:8]}__"
        placeholder_map[placeholder] = table_content
        return placeholder

    processed_text = TABLE_PATTERN.sub(replace_table, processed_text)

    # Insert section break markers (process after table replacement)
    # We need to find headers and insert marker *before* them in the processed_text
    # This is tricky with string replacement; iterating and building might be safer.
    final_processed_text = ""
    last_index = 0
    combined_header_pattern = re.compile(f"({SECTION_HEADER_PATTERN_EN.pattern}|{SECTION_HEADER_PATTERN_HI.pattern})", re.MULTILINE)

    # Rebuild the string to insert markers correctly
    final_processed_text = ""
    last_index = 0
    # Combine patterns: Group 1 captures (^|\n\n), Group 2 captures the header text
    combined_pattern = re.compile(
        # Capture preceding part (non-capturing group within outer capture group 1)
        r"((?:^|\n\n))"
        # Capture optional whitespace after preceding part
        r"\s*"
        # Capture header text (Group 2 for EN, Group 3 for HI) - need to adjust indices later
        r"(?:(Section\s+\d+(?:\.\d+)*\.\s+.*?)|(खंड\s+\d+(?:\.\d+)*\.\s+.*?))"
        # Positive lookahead for trailing newline
        r"(?=\n)",
        re.MULTILINE
    )

    for match in combined_pattern.finditer(processed_text):
        preceding_part = match.group(1) # (^|\n\n)
        # Determine which header pattern matched (EN or HI)
        header_text = match.group(2) or match.group(3) # Get the actual header text
        header_start_index = match.start(2) if match.group(2) else match.start(3)

        # Append text before the match start
        final_processed_text += processed_text[last_index:match.start(0)]
        # Append the preceding part (^ or \n\n)
        final_processed_text += preceding_part
        # Append any whitespace between preceding part and header
        final_processed_text += processed_text[match.end(1):header_start_index]
        # Add the section break marker
        final_processed_text += "__SECTION_BREAK__"
        # Append the header text
        final_processed_text += header_text
        # Update last index to the end of the header text
        last_index = match.end(2) if match.group(2) else match.end(3)

    # Append the remaining text after the last header match
    final_processed_text += processed_text[last_index:]

    # Original implementation attempt (less safe due to potential overlapping replacements):
    # for pattern in [SECTION_HEADER_PATTERN_EN, SECTION_HEADER_PATTERN_HI]:
    #     # Use finditer to get match objects and insert marker before the match start
    #     matches = list(pattern.finditer(processed_text))
    #     offset = 0
    #     for match in matches:
    #         insert_pos = match.start(1) + offset # Adjust position based on previous insertions
    #         marker = "__SECTION_BREAK__"
    #         processed_text = processed_text[:insert_pos] + marker + processed_text[insert_pos:]
    #         offset += len(marker)

    return final_processed_text, placeholder_map


def _postprocess_chunks(chunks: List[str], placeholder_map: Dict[str, str]) -> List[str]:
    """
    Postprocesses chunks by replacing table placeholders and removing section markers.
    """
    processed_chunks = []
    for chunk in chunks:
        # Replace table placeholders
        for placeholder, table_content in placeholder_map.items():
            chunk = chunk.replace(placeholder, table_content)
        # Remove section break markers
        chunk = chunk.replace("__SECTION_BREAK__", "")
        # Strip potential leading/trailing whitespace introduced
        processed_chunks.append(chunk.strip())
    # Filter out any potentially empty chunks after processing
    return [c for c in processed_chunks if c]


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
    """
    Splits extracted text from a document into smaller chunks using a semantic strategy.

    Args:
        extracted_data: A list of tuples, where each tuple contains the page number
                        (1-indexed) and the extracted text for that page.
        document_id: A unique identifier for the source document (e.g., filename or hash).

    Returns:
        A list of DocumentChunk objects, each representing a text chunk with metadata.
        Returns an empty list if input is empty or an error occurs.
    """
    if not extracted_data:
        logger.warning("Received empty extracted data for chunking.")
        return []

    all_final_chunks: List[DocumentChunk] = []
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        is_separator_regex=False, # Markers are literal strings
        separators=SEPARATORS
    )

    logger.info(f"Starting semantic chunking process for document_id: {document_id}")
    logger.info(f"Starting chunking process for document_id: {document_id}") # Use logger instance
    total_pages = len(extracted_data)
    current_chunk_index = 1 # Global chunk index across pages for unique IDs

    for page_num, original_page_text in extracted_data:
        if not original_page_text or original_page_text.isspace():
            logger.debug(f"Skipping empty page {page_num} for document_id: {document_id}")
            continue

        try:
            # 1. Preprocess text for the current page
            preprocessed_text, placeholder_map = _preprocess_text(original_page_text)

            if not preprocessed_text or preprocessed_text.isspace():
                 logger.debug(f"Skipping page {page_num} after preprocessing resulted in empty text.")
                 continue

            # 2. Split the preprocessed text
            raw_chunks_on_page = text_splitter.split_text(preprocessed_text)

            # 3. Postprocess the chunks
            cleaned_chunks_on_page = _postprocess_chunks(raw_chunks_on_page, placeholder_map)

            num_chunks_on_page = len(cleaned_chunks_on_page)
            if num_chunks_on_page == 0:
                 logger.debug(f"No chunks generated for page {page_num} after postprocessing.")
                 continue

            # 4. Create DocumentChunk objects
            for i, chunk_content in enumerate(cleaned_chunks_on_page):
                # Use a running index for chunk_id to ensure uniqueness across pages
                chunk_id = f"{document_id}_chunk_{current_chunk_index}"
                current_chunk_index += 1
                # Metadata now includes original page number and index on that page
                chunk_metadata = {
                    "document_id": document_id,
                    "page_number": page_num,
                    "chunk_index_on_page": i + 1, # Index relative to this page's cleaned chunks
                    "total_chunks_on_page": num_chunks_on_page,
                    "total_document_pages": total_pages
                }
                document_chunk = DocumentChunk(
                    chunk_id=chunk_id,
                    document_id=document_id,
                    text=chunk_content,
                    metadata=chunk_metadata
                )
                all_final_chunks.append(document_chunk)

            logger.debug(f"Page {page_num} (doc: {document_id}) processed into {num_chunks_on_page} final chunks.")

        except Exception as e:
            logger.error(f"Error processing page {page_num} for document_id: {document_id}: {e}", exc_info=True)
            # Continue to next page if one page fails

    logger.info(f"Completed semantic chunking for document_id: {document_id}. Total chunks created: {len(all_final_chunks)}")
    return all_final_chunks

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
