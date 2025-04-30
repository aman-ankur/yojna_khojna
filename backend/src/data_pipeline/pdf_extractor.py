import pdfplumber
from pathlib import Path
from typing import List, Tuple, Optional
import logging
import pytesseract
from PIL import Image
import re # Import re for cleaning text within tables

# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# Use getLogger instead, configuration is handled centrally
logger = logging.getLogger(__name__)

# Configure Tesseract path if necessary (especially on Windows or if not in PATH)
# Example: pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

MIN_TEXT_LENGTH_FOR_OCR_FALLBACK = 20 # If extract_text yields fewer chars than this, try OCR
MIN_TABLE_ROWS_FOR_SIGNIFICANCE = 2 # Consider tables significant if they have at least this many rows
OCR_RESOLUTION = 300 # DPI for rendering PDF page to image for OCR

def detect_and_extract_tables(table_data: List[List[Optional[str]]], context: str = "Table") -> str:
    """
    Formats a list of lists representing a table into a Markdown string.
    Handles padding for inconsistent row lengths and empty tables.

    Args:
        table_data: The table content as a list of rows, where each row is a list of cells.
        context: Optional context string to include in the TABLE_START marker.

    Returns:
        A Markdown formatted string representation of the table, or an empty string if the table is empty.
    """
    if not table_data or not any(row for row in table_data):
        logger.debug("Skipping empty or invalid table data.")
        return ""

    # Clean cell content: replace None with "", strip whitespace, remove excessive newlines/spaces
    cleaned_table = []
    for row in table_data:
        if row is None: continue # Skip None rows
        cleaned_row = []
        for cell in row:
            if cell is None:
                cleaned_row.append("")
            else:
                # Remove excessive whitespace and newlines within a cell
                cleaned_cell = re.sub(r'\s+', ' ', str(cell)).strip()
                cleaned_row.append(cleaned_cell)
        # Only add non-empty rows
        if any(cleaned_row):
             cleaned_table.append(cleaned_row)

    if not cleaned_table:
         logger.debug("Skipping table with only empty cells after cleaning.")
         return ""

    # Determine the maximum number of columns based on the header or longest row
    num_cols = 0
    if cleaned_table[0]: # Check if header row exists and is not empty
        num_cols = len(cleaned_table[0])
    if num_cols == 0: # Fallback if header is empty or missing
         num_cols = max(len(row) for row in cleaned_table if row) if cleaned_table else 0

    if num_cols == 0:
        logger.debug("Skipping table with zero columns determined.")
        return ""

    # Pad rows to have the same number of columns
    padded_table = []
    for row in cleaned_table:
        if row is None: continue
        # Take only up to num_cols elements, pad if shorter
        padded_row = (row[:num_cols] + [""] * (num_cols - len(row))) if len(row) < num_cols else row[:num_cols]
        padded_table.append(padded_row)

    if not padded_table:
        logger.debug("Skipping table - resulted in empty padded table.")
        return ""

    # Format as Markdown
    markdown_lines = []
    markdown_lines.append(f"[TABLE_START: {context}]")

    # Header row
    header = " | ".join(str(cell) for cell in padded_table[0])
    markdown_lines.append(f"| {header} |")

    # Separator row
    separator = " | ".join(["---"] * num_cols)
    markdown_lines.append(f"| {separator} |")

    # Data rows
    for row in padded_table[1:]:
        data_row = " | ".join(str(cell) for cell in row)
        markdown_lines.append(f"| {data_row} |")

    markdown_lines.append("[TABLE_END]")

    return "\n".join(markdown_lines)


def extract_text_from_pdf(pdf_path: Path) -> Optional[List[Tuple[int, str]]]:
    """Extracts text from each page of a PDF file, using OCR as a fallback.

    Args:
        pdf_path: The path to the PDF file.

    Returns:
        A list of tuples, where each tuple contains the page number (1-indexed)
        and the extracted text for that page. Returns None if the file cannot be
        processed or does not exist.
    """
    if not pdf_path.is_file():
        # logging.error(f"PDF file not found: {pdf_path}")
        logger.error(f"PDF file not found: {pdf_path}") # Use logger instance
        return None

    extracted_data: List[Tuple[int, str]] = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            logger.info(f"Processing PDF: {pdf_path.name} with {len(pdf.pages)} pages.")
            for i, page in enumerate(pdf.pages):
                page_num = i + 1
                page_content = "" # Combined text and tables for the page
                try:
                    # 1. Attempt direct text extraction
                    direct_text = page.extract_text(x_tolerance=2, y_tolerance=2) # Adjust tolerances slightly
                    cleaned_direct_text = ' '.join(direct_text.split()) if direct_text else ""

                    # 2. Attempt table extraction
                    extracted_tables = page.extract_tables()
                    formatted_tables_text = ""
                    significant_tables_found = False
                    if extracted_tables:
                        logger.info(f"Found {len(extracted_tables)} table(s) on page {page_num}.")
                        table_texts = []
                        for idx, table in enumerate(extracted_tables):
                            # Provide context if possible (e.g., based on surrounding text - complex, skip for now)
                            # For now, just use a generic context
                            table_context = f"Page {page_num} - Table {idx+1}"
                            formatted_table = detect_and_extract_tables(table, table_context)
                            if formatted_table:
                                table_texts.append(formatted_table)
                                # Consider a table significant if it has enough rows
                                if table and len(table) >= MIN_TABLE_ROWS_FOR_SIGNIFICANCE:
                                    significant_tables_found = True
                        formatted_tables_text = "\n\n".join(table_texts) # Separate tables by double newline

                    # 3. Decide whether to use direct extraction or OCR fallback
                    use_ocr = False
                    if len(cleaned_direct_text) < MIN_TEXT_LENGTH_FOR_OCR_FALLBACK and not significant_tables_found:
                        logger.info(f"Direct text minimal and no significant tables found on page {page_num}. Attempting OCR.")
                        use_ocr = True

                    if use_ocr:
                        try:
                            # Render page to image at higher resolution
                            page_image = page.to_image(resolution=OCR_RESOLUTION).original
                            # Perform OCR using English and Hindi
                            ocr_text = pytesseract.image_to_string(page_image, lang='eng+hin')
                            cleaned_ocr_text = ' '.join(ocr_text.split()) if ocr_text else ""
                            page_content = cleaned_ocr_text # Use OCR text
                            if not page_content:
                                logger.warning(f"OCR yielded no text on page {page_num} of {pdf_path.name}")
                            # Note: OCR output won't contain formatted tables.
                        except Exception as ocr_err:
                            logger.error(f"OCR failed on page {page_num} of {pdf_path.name}: {ocr_err}", exc_info=False)
                            # Fallback to the minimal direct text if OCR fails, append any tables found before OCR attempt
                            page_content = cleaned_direct_text
                            if formatted_tables_text:
                                page_content += "\n\n" + formatted_tables_text
                    else:
                        # Use directly extracted text and append formatted tables
                        page_content = cleaned_direct_text
                        if formatted_tables_text:
                            page_content += "\n\n" + formatted_tables_text # Append tables

                    # Clean final page content
                    final_page_content = page_content.strip()

                    if final_page_content:
                        extracted_data.append((page_num, final_page_content))
                        logger.debug(f"Successfully processed page {page_num} (Length: {len(final_page_content)})")
                    else:
                        logger.warning(f"No text or table content found or extracted on page {page_num} of {pdf_path.name}")

                except Exception as page_err:
                    logger.error(f"Error processing page {page_num} of {pdf_path.name}: {page_err}", exc_info=True)
                    continue # Move to the next page

            logger.info(f"Successfully processed {len(extracted_data)} pages in {pdf_path.name}.")
            return extracted_data

    except Exception as e:
        logger.error(f"Error opening or processing PDF file {pdf_path}: {e}", exc_info=True)
        return None

if __name__ == '__main__':
    # Example usage: Replace with an actual PDF path for testing
    print("PDF Extractor Module with OCR Fallback")
    # --- IMPORTANT: Ensure this path points to your test PDF --- #
    # dummy_pdf_path = Path("/Users/aankur/Downloads/small_awaas_yojna.pdf") 
    # test_pdf_path = Path("path/to/your/image_based.pdf") # Use a PDF known to contain images
    test_pdf_path = Path("test_docs/small_awaas_yojna.pdf") # Example path

    if not test_pdf_path.parent.exists():
        test_pdf_path.parent.mkdir(parents=True, exist_ok=True)
        print(f"Created directory {test_pdf_path.parent}. Please place a test PDF at {test_pdf_path}")
    elif not test_pdf_path.exists():
        print(f"Please place a test PDF (ideally image-based) at: {test_pdf_path}")
    else:
        print(f"Attempting to extract text from: {test_pdf_path}")
        extracted_content = extract_text_from_pdf(test_pdf_path)
        if extracted_content:
            print(f"\n--- Extracted Content ({len(extracted_content)} pages) ---")
            for page_num, text in extracted_content:
                print(f"\n=== Page {page_num} ===")
                print(text[:500] + ("..." if len(text) > 500 else "")) # Print first 500 chars
        else:
            print("\nCould not extract text from the PDF or the PDF was empty/invalid.")
