import pytest
import hashlib
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import UploadFile, BackgroundTasks
from fastapi.testclient import TestClient
from pathlib import Path
import io
import asyncio # Import asyncio for checks
from backend.src.exceptions import WeaviateConnectionError

# Import the FastAPI app instance from your main module
# Adjust the import path based on your project structure
from backend.src.main import app, calculate_file_hash, check_hash_exists, run_processing_pipeline

# Create a TestClient instance
client = TestClient(app)

# Fixture for a mock UploadFile
@pytest.fixture
def mock_upload_file():
    content = b"This is a test PDF content."
    file = io.BytesIO(content)
    upload_file = UploadFile(filename="test.pdf", file=file)
    return upload_file, content

# Fixture for a mock Weaviate client
@pytest.fixture
def mock_weaviate_client():
    mock = MagicMock()
    mock.is_connected.return_value = True
    # Mock the collections interface
    mock_collections = MagicMock()
    mock_collection_instance = MagicMock()

    # Mock the query interface
    mock_query = MagicMock()
    mock_response = MagicMock()
    mock_response.objects = [] # Default to no objects found
    mock_query.fetch_objects.return_value = mock_response

    # Mock the data interface for background task
    mock_data = MagicMock()
    mock_insert_response = MagicMock()
    mock_insert_response.has_errors = False
    mock_data.insert_many.return_value = mock_insert_response

    mock_collection_instance.query = mock_query
    mock_collection_instance.data = mock_data
    mock_collections.get.return_value = mock_collection_instance
    mock.collections = mock_collections

    return mock, mock_response # Return mock response too for modification

# Fixture for mock BackgroundTasks
@pytest.fixture
def mock_background_tasks():
    tasks = BackgroundTasks()
    tasks.add_task = MagicMock() # Mock the add_task method
    return tasks


# --- Test Functions --- #

# Tests will be added here 

@pytest.mark.asyncio
async def test_calculate_file_hash(mock_upload_file):
    """Test SHA256 hash calculation."""
    upload_file, content = mock_upload_file
    expected_hash = hashlib.sha256(content).hexdigest()
    actual_hash = await calculate_file_hash(upload_file)
    assert actual_hash == expected_hash
    # Ensure file pointer is reset
    assert upload_file.file.tell() == 0

@pytest.mark.asyncio
async def test_check_hash_exists_does_not_exist(mock_weaviate_client):
    """Test hash check when hash does not exist."""
    client, mock_response = mock_weaviate_client
    mock_response.objects = [] # Ensure no objects are returned
    exists = await check_hash_exists(client, "non_existent_hash")
    assert exists is False
    client.collections.get.assert_called_once_with("YojnaChunk")
    client.collections.get().query.fetch_objects.assert_called_once()

@pytest.mark.asyncio
async def test_check_hash_exists_exists(mock_weaviate_client):
    """Test hash check when hash exists."""
    client, mock_response = mock_weaviate_client
    mock_response.objects = [MagicMock()] # Simulate finding an object
    exists = await check_hash_exists(client, "existent_hash")
    assert exists is True
    client.collections.get.assert_called_once_with("YojnaChunk")
    client.collections.get().query.fetch_objects.assert_called_once()

@pytest.mark.asyncio
@patch('backend.src.main.get_weaviate_client')
@patch('backend.src.main.calculate_file_hash')
@patch('backend.src.main.check_hash_exists')
@patch('fastapi.BackgroundTasks.add_task')  # Patch add_task directly
async def test_process_pdf_endpoint_new_file(
    mock_add_task,  # Get the patched method
    mock_check_hash,
    mock_calc_hash,
    mock_get_client,
    mock_upload_file
    # Removed mock_background_tasks fixture from signature
):
    """Test /process-pdf endpoint when file hash is new."""
    upload_file, content = mock_upload_file
    test_hash = "new_file_hash"

    # Mock return values
    mock_get_client_instance = MagicMock()
    mock_get_client_instance.close = MagicMock() # Mock the close method needed in finally block
    mock_get_client.return_value = mock_get_client_instance # Use instance for check
    mock_calc_hash.return_value = test_hash
    mock_check_hash.return_value = False # Simulate hash doesn't exist

    # Remove dependency override block
    # app.dependency_overrides[BackgroundTasks] = lambda: mock_background_tasks

    # Use TestClient
    response = client.post("/process-pdf", files={"pdf_file": (upload_file.filename, content, "application/pdf")})

    # Assertions
    assert response.status_code == 200 # We changed default success to 200
    json_response = response.json()
    assert json_response["status"] == "processing_scheduled"
    assert json_response["filename"] == upload_file.filename
    assert json_response["document_hash"] == test_hash

    mock_calc_hash.assert_called_once()
    mock_get_client.assert_called_once()
    # Assert check_hash_exists was called with the specific client instance
    mock_check_hash.assert_called_once_with(mock_get_client_instance, test_hash)
    # Check that the background task was added with correct args using the direct patch
    mock_add_task.assert_called_once_with(
        run_processing_pipeline, content, upload_file.filename, test_hash
    )
    # Check that the client used for checking was closed
    mock_get_client_instance.close.assert_called_once()

    # Clean up dependency override (if any were set elsewhere, good practice)
    app.dependency_overrides = {}

@pytest.mark.asyncio
@patch('backend.src.main.get_weaviate_client')
@patch('backend.src.main.calculate_file_hash')
@patch('backend.src.main.check_hash_exists')
# No patch needed for BackgroundTasks here
async def test_process_pdf_endpoint_existing_file(
    mock_check_hash,
    mock_calc_hash,
    mock_get_client,
    mock_upload_file
    # Removed mock_background_tasks fixture from signature
):
    """Test /process-pdf endpoint when file hash already exists."""
    upload_file, content = mock_upload_file
    test_hash = "existing_file_hash"

    # Mock return values
    mock_get_client_instance = MagicMock()
    mock_get_client_instance.close = MagicMock() # Mock the close method needed in finally block
    mock_get_client.return_value = mock_get_client_instance # Use instance for check
    mock_calc_hash.return_value = test_hash
    mock_check_hash.return_value = True # Simulate hash *does* exist

    # No BackgroundTasks involved or overridden when file exists

    response = client.post("/process-pdf", files={"pdf_file": (upload_file.filename, content, "application/pdf")})

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] == "exists"
    assert json_response["filename"] == upload_file.filename
    assert json_response["document_hash"] == test_hash

    mock_calc_hash.assert_called_once()
    mock_get_client.assert_called_once()
    # Assert check_hash_exists was called with the specific client instance
    mock_check_hash.assert_called_once_with(mock_get_client_instance, test_hash)
    # Check that the client used for checking was closed
    mock_get_client_instance.close.assert_called_once()
    # Ensure add_task was not called (we don't need to patch it or assert on it directly here)

    # Clean up dependency override
    app.dependency_overrides = {}

# Test the background task function itself
@patch('backend.src.main.process_pdf')
@patch('backend.src.main.get_weaviate_client')
@patch('backend.src.main.batch_import_chunks')
@patch('tempfile.NamedTemporaryFile')
def test_run_processing_pipeline_success(
    mock_tempfile, mock_batch_import, mock_get_client, mock_process_pdf, mock_weaviate_client
):
    """Test the background pipeline function on success."""
    pdf_content = b"pdf data"
    filename = "test.pdf"
    file_hash = "testhash"
    mock_chunks = [MagicMock()] # Simulate successful chunking
    mock_client_instance, _ = mock_weaviate_client

    # Mock return values
    mock_process_pdf.return_value = mock_chunks
    mock_get_client.return_value = mock_client_instance

    # Mock the tempfile context manager
    mock_temp_file_obj = MagicMock()
    mock_temp_file_obj.name = "/tmp/fake_temp_file.pdf"
    mock_tempfile.return_value.__enter__.return_value = mock_temp_file_obj

    run_processing_pipeline(pdf_content, filename, file_hash)

    # Assertions
    mock_tempfile.assert_called_once()
    mock_process_pdf.assert_called_once_with(Path(mock_temp_file_obj.name))
    mock_get_client.assert_called_once()
    mock_batch_import.assert_called_once_with(mock_client_instance, mock_chunks, file_hash)
    mock_client_instance.close.assert_called_once()
    # Check if temp file unlink was attempted (needs mocking Path.unlink)
    # TODO: Add mock for Path.unlink if detailed cleanup verification is needed

@patch('backend.src.main.process_pdf')
@patch('backend.src.main.get_weaviate_client')
@patch('backend.src.main.batch_import_chunks')
@patch('tempfile.NamedTemporaryFile')
def test_run_processing_pipeline_processing_error(
    mock_tempfile, mock_batch_import, mock_get_client, mock_process_pdf
):
    """Test the background pipeline function when process_pdf fails."""
    pdf_content = b"pdf data"
    filename = "test.pdf"
    file_hash = "testhash"

    # Mock process_pdf to raise an error
    from backend.src.exceptions import PDFProcessingError
    mock_process_pdf.side_effect = PDFProcessingError("Extraction failed")

    # Mock the tempfile context manager
    mock_temp_file_obj = MagicMock()
    mock_temp_file_obj.name = "/tmp/fake_temp_file.pdf"
    mock_tempfile.return_value.__enter__.return_value = mock_temp_file_obj

    # Run the function (should catch the exception and log)
    run_processing_pipeline(pdf_content, filename, file_hash)

    # Assertions
    mock_tempfile.assert_called_once()
    mock_process_pdf.assert_called_once_with(Path(mock_temp_file_obj.name))
    # Ensure Weaviate connection and import were NOT called
    mock_get_client.assert_not_called()
    mock_batch_import.assert_not_called()
    # TODO: Add check for logging the error

# Add more tests for other error cases in run_processing_pipeline (e.g., Weaviate errors) 

@pytest.mark.asyncio
@patch('backend.src.main.create_conversational_rag_chain')
async def test_chat_endpoint_success_format(mock_create_chain):
    """Test the /chat endpoint, verifying mock execution and response format."""
    # --- Mock Setup --- # 
    # 1. Define the result we want ainvoke to return
    mock_result = {
        'answer': 'This is a mock AI answer.',
        'chat_history': [
            ["Test question?", "This is a mock AI answer."]
        ] 
    }

    # 2. Create an AsyncMock to represent the chain instance
    mock_chain_instance = AsyncMock()
    mock_chain_instance.ainvoke.return_value = mock_result
    
    # 3. Configure the patched factory to return our prepared mock chain instance
    mock_create_chain.return_value = mock_chain_instance
    # --- End Mock Setup --- #

    request_data = {
        "question": "Test question?",
        "chat_history": []
    }

    # Use TestClient 
    print("\n--- Making request with TestClient --- ")
    with TestClient(app) as client:
        response = client.post("/chat", json=request_data)
    print(f"--- TestClient response status: {response.status_code} ---")

    # --- Assertions --- #
    # 1. Verify the mock was called with expected arguments
    mock_create_chain.assert_called_once()
    mock_chain_instance.ainvoke.assert_called_once()
    
    # 2. Verify the response status and content
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}. Response: {response.text}"
    response_json = response.json()
    assert "answer" in response_json
    assert "updated_history" in response_json
    assert response_json["answer"] == "This is a mock AI answer."

    # Assert the structure of updated_history
    assert isinstance(response_json["updated_history"], list)
    assert len(response_json["updated_history"]) == 1
    first_turn = response_json["updated_history"][0]
    assert isinstance(first_turn, list)
    assert len(first_turn) == 2
    assert isinstance(first_turn[0], str)
    assert isinstance(first_turn[1], str)
    assert first_turn[0] == "Test question?"
    assert first_turn[1] == "This is a mock AI answer."

# ... (rest of test_main.py) ... 