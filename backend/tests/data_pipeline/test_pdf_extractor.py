import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, call
from backend.src.data_pipeline.pdf_extractor import detect_and_extract_tables, extract_text_from_pdf, MIN_TEXT_LENGTH_FOR_OCR_FALLBACK, MIN_TABLE_ROWS_FOR_SIGNIFICANCE

def test_detect_and_extract_tables():
    """Test that tables are correctly detected and formatted as markdown."""
    # Create test data similar to what pdfplumber would return
    test_table = [
        ["क्रम", "किस्त", "किस्त की राशि", "आवश्यक प्रगति"],
        ["1", "प्रथम", "सहयोग राशि का 15%", "पंजीकरण के बाद"],
        ["2", "द्वितीय", "सहयोग राशि का 25%", "प्लिंथ स्तर तक"]
    ]
    
    # Call the function
    result = detect_and_extract_tables(test_table, "Section 6.6.3 - Installment Schedule")
    
    # Check that the result is properly formatted
    assert "[TABLE_START: Section 6.6.3 - Installment Schedule]" in result
    assert "| क्रम | किस्त | किस्त की राशि | आवश्यक प्रगति |" in result
    assert "| 1 | प्रथम | सहयोग राशि का 15% | पंजीकरण के बाद |" in result
    assert "[TABLE_END]" in result

def test_table_padding():
    """Test that tables with inconsistent row lengths are padded correctly."""
    test_table = [
        ["Header 1", "Header 2", "Header 3"],
        ["Row 1 Col 1", "Row 1 Col 2"], # Missing third column
        ["Row 2 Col 1", "Row 2 Col 2", "Row 2 Col 3", "Extra column"]  # Extra column
    ]
    
    result = detect_and_extract_tables(test_table, "Inconsistent Table")
    
    # Verify headers are present
    assert "| Header 1 | Header 2 | Header 3 |" in result
    
    # Verify rows are properly padded
    assert "| Row 1 Col 1 | Row 1 Col 2 |  |" in result
    assert "| Row 2 Col 1 | Row 2 Col 2 | Row 2 Col 3 |" in result

def test_empty_table_handling():
    """Test that empty tables are handled gracefully."""
    # Empty table
    empty_table = []
    result = detect_and_extract_tables(empty_table, "Empty Table")
    assert result == ""

    # Table with empty header row
    empty_header = [[]]
    result = detect_and_extract_tables(empty_header, "Empty Header")
    assert result == ""

# --- Tests for extract_text_from_pdf ---

@pytest.fixture
def mock_pdf_page():
    """Fixture to create a mock pdfplumber page object."""
    page = MagicMock()
    page.extract_text.return_value = "This is the page text."
    page.extract_tables.return_value = None # Default: no tables
    page.page_number = 1
    # Mock image conversion and OCR for fallback tests
    mock_image = MagicMock()
    page.to_image.return_value.original = mock_image
    return page

@pytest.fixture
def mock_pdf_file(mock_pdf_page):
    """Fixture to create a mock pdfplumber PDF object with pages."""
    pdf = MagicMock()
    pdf.pages = [mock_pdf_page] # Default: one page
    # Ensure the context manager returns the mock pdf
    mock_open = MagicMock()
    mock_open.return_value.__enter__.return_value = pdf
    return mock_open

@patch('backend.src.data_pipeline.pdf_extractor.pdfplumber.open')
@patch('backend.src.data_pipeline.pdf_extractor.Path.is_file')
def test_extract_text_basic(mock_is_file, mock_pdfplumber_open, mock_pdf_file, mock_pdf_page):
    """Test basic text extraction without tables or OCR."""
    mock_is_file.return_value = True
    mock_pdfplumber_open.side_effect = mock_pdf_file # Use the mock_pdf_file fixture

    pdf_path = Path("dummy.pdf")
    result = extract_text_from_pdf(pdf_path)

    assert result is not None
    assert len(result) == 1
    assert result[0][0] == 1 # Page number
    assert "This is the page text." in result[0][1]
    assert "[TABLE_START" not in result[0][1] # No tables expected
    mock_pdf_page.extract_text.assert_called_once()
    mock_pdf_page.extract_tables.assert_called_once()
    mock_pdf_page.to_image.assert_not_called() # OCR should not be called

@patch('backend.src.data_pipeline.pdf_extractor.pytesseract.image_to_string')
@patch('backend.src.data_pipeline.pdf_extractor.pdfplumber.open')
@patch('backend.src.data_pipeline.pdf_extractor.Path.is_file')
def test_extract_text_with_ocr_fallback(mock_is_file, mock_pdfplumber_open, mock_pytesseract, mock_pdf_file, mock_pdf_page):
    """Test OCR fallback when direct text extraction is minimal."""
    mock_is_file.return_value = True
    mock_pdfplumber_open.side_effect = mock_pdf_file
    mock_pdf_page.extract_text.return_value = "Short" # Less than MIN_TEXT_LENGTH_FOR_OCR_FALLBACK
    mock_pdf_page.extract_tables.return_value = None # No tables
    mock_pytesseract.return_value = "This is OCR text."

    pdf_path = Path("dummy_ocr.pdf")
    result = extract_text_from_pdf(pdf_path)

    assert result is not None
    assert len(result) == 1
    assert result[0][0] == 1
    assert "This is OCR text." in result[0][1]
    assert "Short" not in result[0][1] # Original short text shouldn't be there
    assert "[TABLE_START" not in result[0][1]
    mock_pdf_page.extract_text.assert_called_once()
    mock_pdf_page.extract_tables.assert_called_once()
    mock_pdf_page.to_image.assert_called_once()
    mock_pytesseract.assert_called_once()

@patch('backend.src.data_pipeline.pdf_extractor.pdfplumber.open')
@patch('backend.src.data_pipeline.pdf_extractor.Path.is_file')
def test_extract_text_with_table(mock_is_file, mock_pdfplumber_open, mock_pdf_file, mock_pdf_page):
    """Test extraction when a table is present."""
    mock_is_file.return_value = True
    mock_pdfplumber_open.side_effect = mock_pdf_file
    mock_pdf_page.extract_text.return_value = "Text before table."
    test_table = [
        ["Col A", "Col B"],
        ["Val 1", "Val 2"],
        ["Val 3", "Val 4"]
    ]
    mock_pdf_page.extract_tables.return_value = [test_table] # One table found

    pdf_path = Path("dummy_table.pdf")
    result = extract_text_from_pdf(pdf_path)

    assert result is not None
    assert len(result) == 1
    assert result[0][0] == 1
    assert "Text before table." in result[0][1]
    assert "[TABLE_START: Page 1 - Table 1]" in result[0][1]
    assert "| Col A | Col B |" in result[0][1]
    assert "| Val 1 | Val 2 |" in result[0][1]
    assert "[TABLE_END]" in result[0][1]
    mock_pdf_page.extract_text.assert_called_once()
    mock_pdf_page.extract_tables.assert_called_once()
    mock_pdf_page.to_image.assert_not_called() # OCR should not be called

@patch('backend.src.data_pipeline.pdf_extractor.pytesseract.image_to_string')
@patch('backend.src.data_pipeline.pdf_extractor.pdfplumber.open')
@patch('backend.src.data_pipeline.pdf_extractor.Path.is_file')
def test_extract_text_minimal_text_but_significant_table_no_ocr(mock_is_file, mock_pdfplumber_open, mock_pytesseract, mock_pdf_file, mock_pdf_page):
    """Test that OCR is NOT triggered if text is minimal but a significant table exists."""
    mock_is_file.return_value = True
    mock_pdfplumber_open.side_effect = mock_pdf_file
    mock_pdf_page.extract_text.return_value = "Short" # Less than MIN_TEXT_LENGTH_FOR_OCR_FALLBACK
    # A table with enough rows to be considered significant
    significant_table = [["Header"]] + [[f"Row {i}"] for i in range(MIN_TABLE_ROWS_FOR_SIGNIFICANCE)]
    mock_pdf_page.extract_tables.return_value = [significant_table]

    pdf_path = Path("dummy_sig_table.pdf")
    result = extract_text_from_pdf(pdf_path)

    assert result is not None
    assert len(result) == 1
    assert result[0][0] == 1
    assert "Short" in result[0][1] # Original short text should be present
    assert "[TABLE_START: Page 1 - Table 1]" in result[0][1]
    assert "| Header |" in result[0][1]
    assert "[TABLE_END]" in result[0][1]
    mock_pdf_page.extract_text.assert_called_once()
    mock_pdf_page.extract_tables.assert_called_once()
    mock_pdf_page.to_image.assert_not_called() # OCR should NOT be called
    mock_pytesseract.assert_not_called()

@patch('backend.src.data_pipeline.pdf_extractor.pytesseract.image_to_string')
@patch('backend.src.data_pipeline.pdf_extractor.pdfplumber.open')
@patch('backend.src.data_pipeline.pdf_extractor.Path.is_file')
def test_extract_text_minimal_text_and_insignificant_table_uses_ocr(mock_is_file, mock_pdfplumber_open, mock_pytesseract, mock_pdf_file, mock_pdf_page):
    """Test that OCR IS triggered if text is minimal and table is insignificant."""
    mock_is_file.return_value = True
    mock_pdfplumber_open.side_effect = mock_pdf_file
    mock_pdf_page.extract_text.return_value = "Short" # Less than MIN_TEXT_LENGTH_FOR_OCR_FALLBACK
    # A table with fewer rows than required for significance
    insignificant_table = [["Header Only"]]
    mock_pdf_page.extract_tables.return_value = [insignificant_table]
    mock_pytesseract.return_value = "This is OCR text because table was small."

    pdf_path = Path("dummy_insig_table_ocr.pdf")
    result = extract_text_from_pdf(pdf_path)

    assert result is not None
    assert len(result) == 1
    assert result[0][0] == 1
    assert "This is OCR text because table was small." in result[0][1]
    # The insignificant table should NOT be in the OCR output
    assert "[TABLE_START" not in result[0][1]
    assert "| Header Only |" not in result[0][1]
    mock_pdf_page.extract_text.assert_called_once()
    mock_pdf_page.extract_tables.assert_called_once()
    mock_pdf_page.to_image.assert_called_once()
    mock_pytesseract.assert_called_once()


@patch('backend.src.data_pipeline.pdf_extractor.pdfplumber.open')
@patch('backend.src.data_pipeline.pdf_extractor.Path.is_file')
def test_extract_text_multiple_pages(mock_is_file, mock_pdfplumber_open):
    """Test extraction from a PDF with multiple pages."""
    mock_is_file.return_value = True

    # Create mock pages
    page1 = MagicMock()
    page1.page_number = 1
    page1.extract_text.return_value = "Text from page 1."
    page1.extract_tables.return_value = None

    page2 = MagicMock()
    page2.page_number = 2
    page2.extract_text.return_value = "Text from page 2."
    page2.extract_tables.return_value = [[["Table Header"], ["Table Data"]]] # Significant table

    # Create mock PDF with these pages
    pdf = MagicMock()
    pdf.pages = [page1, page2]
    mock_open = MagicMock()
    mock_open.return_value.__enter__.return_value = pdf
    mock_pdfplumber_open.side_effect = mock_open

    pdf_path = Path("multi_page.pdf")
    result = extract_text_from_pdf(pdf_path)

    assert result is not None
    assert len(result) == 2

    # Check page 1
    assert result[0][0] == 1
    assert "Text from page 1." in result[0][1]
    assert "[TABLE_START" not in result[0][1]

    # Check page 2
    assert result[1][0] == 2
    assert "Text from page 2." in result[1][1]
    assert "[TABLE_START: Page 2 - Table 1]" in result[1][1]
    assert "| Table Header |" in result[1][1]
    assert "| Table Data |" in result[1][1]
    assert "[TABLE_END]" in result[1][1]

@patch('backend.src.data_pipeline.pdf_extractor.pdfplumber.open')
@patch('backend.src.data_pipeline.pdf_extractor.Path.is_file')
def test_extract_text_file_not_found(mock_is_file, mock_pdfplumber_open):
    """Test behavior when the PDF file does not exist."""
    mock_is_file.return_value = False # Simulate file not found
    pdf_path = Path("non_existent.pdf")
    result = extract_text_from_pdf(pdf_path)
    assert result is None
    mock_pdfplumber_open.assert_not_called()

@patch('backend.src.data_pipeline.pdf_extractor.pdfplumber.open')
@patch('backend.src.data_pipeline.pdf_extractor.Path.is_file')
def test_extract_text_pdfplumber_error(mock_is_file, mock_pdfplumber_open):
    """Test behavior when pdfplumber raises an error during open."""
    mock_is_file.return_value = True
    mock_pdfplumber_open.side_effect = Exception("PDFPlumber failed to open") # Simulate error

    pdf_path = Path("error.pdf")
    result = extract_text_from_pdf(pdf_path)
    assert result is None

@patch('backend.src.data_pipeline.pdf_extractor.pdfplumber.open')
@patch('backend.src.data_pipeline.pdf_extractor.Path.is_file')
def test_extract_text_page_processing_error(mock_is_file, mock_pdfplumber_open, mock_pdf_file, mock_pdf_page):
    """Test behavior when an error occurs processing a specific page."""
    mock_is_file.return_value = True
    mock_pdfplumber_open.side_effect = mock_pdf_file
    # Simulate error during extract_text call
    mock_pdf_page.extract_text.side_effect = Exception("Page processing error")

    pdf_path = Path("page_error.pdf")
    result = extract_text_from_pdf(pdf_path)

    assert result is not None
    assert len(result) == 0 # Page with error should be skipped
