import pdfplumber
from pathlib import Path
from typing import List, Tuple, Optional
import logging
import pytesseract
from PIL import Image

# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# Use getLogger instead, configuration is handled centrally
logger = logging.getLogger(__name__)

# Configure Tesseract path if necessary (especially on Windows or if not in PATH)
# Example: pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

MIN_TEXT_LENGTH_FOR_OCR_FALLBACK = 20 # If extract_text yields fewer chars than this, try OCR
OCR_RESOLUTION = 300 # DPI for rendering PDF page to image for OCR

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
            # logging.info(f"Processing PDF: {pdf_path.name} with {len(pdf.pages)} pages.")
            logger.info(f"Processing PDF: {pdf_path.name} with {len(pdf.pages)} pages.") # Use logger instance
            for i, page in enumerate(pdf.pages):
                page_num = i + 1
                page_text = ""
                try:
                    # 1. Attempt direct text extraction
                    direct_text = page.extract_text()
                    cleaned_direct_text = ' '.join(direct_text.split()) if direct_text else ""

                    # 2. Check if direct text is substantial or if OCR fallback is needed
                    if len(cleaned_direct_text) < MIN_TEXT_LENGTH_FOR_OCR_FALLBACK:
                        # logging.info(f"Direct text extraction minimal on page {page_num}. Attempting OCR.")
                        logger.info(f"Direct text extraction minimal on page {page_num}. Attempting OCR.") # Use logger instance
                        try:
                            # Render page to image at higher resolution
                            page_image = page.to_image(resolution=OCR_RESOLUTION).original
                            # Perform OCR using English and Hindi
                            ocr_text = pytesseract.image_to_string(page_image, lang='eng+hin')
                            cleaned_ocr_text = ' '.join(ocr_text.split()) if ocr_text else ""
                            page_text = cleaned_ocr_text # Use OCR text if direct was minimal
                            if not page_text:
                                # logging.warning(f"OCR yielded no text on page {page_num} of {pdf_path.name}")
                                logger.warning(f"OCR yielded no text on page {page_num} of {pdf_path.name}") # Use logger instance
                        except Exception as ocr_err:
                            # logging.error(f"OCR failed on page {page_num} of {pdf_path.name}: {ocr_err}", exc_info=False)
                            logger.error(f"OCR failed on page {page_num} of {pdf_path.name}: {ocr_err}", exc_info=False) # Use logger instance
                            # Fallback to the minimal direct text if OCR fails
                            page_text = cleaned_direct_text 
                    else:
                        page_text = cleaned_direct_text # Use directly extracted text

                    if page_text:
                        extracted_data.append((page_num, page_text))
                        # logging.debug(f"Successfully processed page {page_num} (Length: {len(page_text)})")
                        logger.debug(f"Successfully processed page {page_num} (Length: {len(page_text)})") # Use logger instance
                    else:
                        # logging.warning(f"No text found or extracted on page {page_num} of {pdf_path.name}")
                        logger.warning(f"No text found or extracted on page {page_num} of {pdf_path.name}") # Use logger instance

                except Exception as page_err:
                    # logging.error(f"Error processing page {page_num} of {pdf_path.name}: {page_err}", exc_info=True)
                    logger.error(f"Error processing page {page_num} of {pdf_path.name}: {page_err}", exc_info=True) # Use logger instance
                    # Optionally skip page or handle error differently
                    continue # Move to the next page

            # logging.info(f"Successfully processed {len(extracted_data)} pages in {pdf_path.name}.")
            logger.info(f"Successfully processed {len(extracted_data)} pages in {pdf_path.name}.") # Use logger instance
            return extracted_data

    except Exception as e:
        # logging.error(f"Error opening or processing PDF file {pdf_path}: {e}", exc_info=True)
        logger.error(f"Error opening or processing PDF file {pdf_path}: {e}", exc_info=True) # Use logger instance
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