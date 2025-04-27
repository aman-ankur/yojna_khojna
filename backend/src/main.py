import tempfile
import shutil
import logging
import hashlib
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware # Import CORS Middleware
from contextlib import contextmanager
import weaviate
import weaviate.classes as wvc # Import Weaviate classes for filtering
from weaviate.exceptions import WeaviateQueryError, WeaviateConnectionError as WeaviateV4ConnectionError # Import necessary exceptions
import sys # Import sys for exit
import re # Import regex module

# Import pipeline components and exceptions
from .main_pipeline import process_pdf
from .vector_db.weaviate_client import CLASS_NAME, get_weaviate_client, ensure_schema_exists, batch_import_chunks
from .exceptions import (
    PipelineError,
    PDFProcessingError,
    ChunkingError,
    EmbeddingModelError,
    EmbeddingGenerationError,
    WeaviateConnectionError,
    WeaviateSchemaError,
    WeaviateStorageError
)
# Ensure logging is configured (if not already done globally)
from .logging_config import setup_logging
setup_logging()

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Yojna Khojna API",
    description="API for the AI-Powered Government Scheme Assistant",
    version="0.1.0",
)

# === CORS Configuration ===
# Allow requests from your frontend development server
origins = [
    "http://localhost:5173", # Vite default dev server port
    "http://localhost:3000", # Common alternative (e.g., Create React App)
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # List of allowed origins
    allow_credentials=True,
    allow_methods=["*"], # Allow all methods (GET, POST, etc.)
    allow_headers=["*"], # Allow all headers
)
# =========================

# === DIAGNOSTIC ROUTE ===
@app.get("/test-route")
async def test_route():
    return {"message": "Test route is active!"}
# =======================

@contextmanager
def temporary_file_path(upload_file: UploadFile) -> Path:
    """Context manager to save UploadFile to a temporary path."""
    # Need to ensure the file pointer is at the beginning if read previously
    upload_file.file.seek(0)
    temp_file = None
    try:
        # Create a temporary file, ensuring it has the original extension if possible
        suffix = Path(upload_file.filename).suffix if upload_file.filename else '.tmp'
        # Use a readable prefix for easier debugging if needed
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix, prefix=f"upload_{Path(upload_file.filename).stem}_")
        shutil.copyfileobj(upload_file.file, temp_file)
        temp_file.close() # Close the file handle immediately after writing
        yield Path(temp_file.name)
    finally:
        if temp_file and Path(temp_file.name).exists():
            try:
                Path(temp_file.name).unlink()
                logger.debug(f"Successfully deleted temporary file: {temp_file.name}")
            except OSError as e:
                 logger.error(f"Error deleting temporary file {temp_file.name}: {e}")


async def calculate_file_hash(upload_file: UploadFile) -> str:
    """Calculates SHA256 hash of the UploadFile content efficiently."""
    hasher = hashlib.sha256()
    upload_file.file.seek(0) # Ensure we read from the beginning
    while chunk := await upload_file.read(8192): # Read in 8KB chunks
        hasher.update(chunk)
    upload_file.file.seek(0) # Reset pointer for potential later use
    return hasher.hexdigest()

async def check_hash_exists(client: weaviate.WeaviateClient, file_hash: str) -> bool:
    """Checks if any object with the given document_hash exists in Weaviate."""
    try:
        collection = client.collections.get(CLASS_NAME)
        response = collection.query.fetch_objects(
            limit=1,
            filters=wvc.query.Filter.by_property("document_hash").equal(file_hash)
        )
        return len(response.objects) > 0
    except (WeaviateQueryError, WeaviateV4ConnectionError) as e:
        logger.error(f"Weaviate error checking hash {file_hash}: {e}", exc_info=True)
        # Treat query/connection errors as if hash doesn't exist to allow processing attempt,
        # but log error. Alternatively, raise HTTPException 503.
        return False
    except Exception as e:
        logger.error(f"Unexpected error checking hash {file_hash}: {e}", exc_info=True)
        return False # Be permissive on check failure, log error

@app.get("/health", tags=["General"])
async def health_check():
    """Basic health check endpoint."""
    return {"status": "ok"}

@app.post("/process-pdf", tags=["Processing"], status_code=200) # Change default success to 200 OK
async def process_pdf_endpoint(background_tasks: BackgroundTasks, pdf_file: UploadFile = File(...)):
    """
    Accepts a PDF file. Checks if it has been processed before (via hash).
    If not, schedules the full processing pipeline (extract, chunk, embed,
    store in Weaviate) to run in the background and returns an immediate
    acknowledgement. If already processed, returns status indicating that.
    """
    logger.info(f"Received request to process PDF: {pdf_file.filename}")
    weaviate_client_checker = None

    try:
        # --- 1. Calculate Hash --- #
        file_hash = await calculate_file_hash(pdf_file)
        logger.info(f"Calculated SHA256 hash for {pdf_file.filename}: {file_hash[:8]}...{file_hash[-8:]}")

        # --- 2. Check for Existence using Hash --- #
        try:
            weaviate_client_checker = get_weaviate_client()
            exists = await check_hash_exists(weaviate_client_checker, file_hash)
        finally:
            if weaviate_client_checker:
                try:
                    weaviate_client_checker.close()
                    logger.debug("Closed Weaviate client used for hash check.")
                except Exception as ce:
                    logger.error(f"Error closing Weaviate hash check client: {ce}")

        if exists:
            logger.info(f"Document {pdf_file.filename} with hash {file_hash[:8]}... already exists. Skipping processing.")
            return {
                "filename": pdf_file.filename,
                "status": "exists",
                "message": "This document has already been processed.",
                "document_hash": file_hash
            }

        # --- 3. Schedule Background Processing --- #
        logger.info(f"Document {pdf_file.filename} (hash: {file_hash[:8]}...) not found. Scheduling for processing.")
        # Pass the file *content* and original filename/hash to the background task
        # Avoid passing the UploadFile object itself directly
        # Read content before background task starts to ensure it's available
        pdf_content = await pdf_file.read()
        await pdf_file.close() # Close the upload file handle

        background_tasks.add_task(run_processing_pipeline, pdf_content, pdf_file.filename, file_hash)

        # Return 202 Accepted status code now
        return {
            "filename": pdf_file.filename,
            "status": "processing_scheduled",
            "message": "Document accepted and scheduled for background processing.",
            "document_hash": file_hash
        }

    except WeaviateConnectionError as e: # Handle connection error during hash check
         logger.error(f"Could not connect to Weaviate to check hash for {pdf_file.filename}: {e}", exc_info=True)
         raise HTTPException(status_code=503, detail=f"Could not connect to vector database to check document status: {e}")
    except Exception as e:
        # Catch-all for unexpected errors during hash calc or scheduling
        logger.critical(f"Unexpected critical error scheduling processing for {pdf_file.filename}: {e}", exc_info=True)
        # Don't expose internal errors directly
        raise HTTPException(status_code=500, detail="Unexpected internal server error during request handling.")


def run_processing_pipeline(pdf_content: bytes, original_filename: str, file_hash: str):
    """Background task to process a PDF and store results in Weaviate."""
    logger.info(f"Background task started for {original_filename} (hash: {file_hash[:8]}...).")
    weaviate_client_processor = None

    # Use a temporary file context manager within the background task
    temp_pdf_path_obj = None
    try:
        # Create a temporary file to store the content for processing
        suffix = Path(original_filename).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, prefix=f"bg_{Path(original_filename).stem}_", mode='wb') as temp_file:
            temp_file.write(pdf_content)
            temp_pdf_path_str = temp_file.name
            temp_pdf_path_obj = Path(temp_pdf_path_str)
            logger.info(f"Background task saved content for {original_filename} to temporary path: {temp_pdf_path_str}")

        # --- 1. Process PDF (Extract, Chunk, Embed) ---
        # Note: process_pdf needs a Path object
        generated_chunks = process_pdf(temp_pdf_path_obj)

        # --- 2. Store in Weaviate ---
        if not generated_chunks:
            logger.warning(f"Background task: No chunks generated for {original_filename}, skipping storage.")
            # No need to return anything, just log
            return

        logger.info(f"Background task: Attempting to store {len(generated_chunks)} chunks in Weaviate for {original_filename}...")
        weaviate_client_processor = get_weaviate_client() # Raises WeaviateConnectionError
        # Schema should already exist from startup or previous runs
        # ensure_schema_exists(weaviate_client_processor) # Potentially skip in background task for performance?

        chunks_to_import = [chunk for chunk in generated_chunks if chunk.embedding is not None]

        if not chunks_to_import:
             logger.warning(f"Background task: No chunks with embeddings found to import for {original_filename}.")
             return

        # Pass the document_hash to batch_import_chunks
        batch_import_chunks(weaviate_client_processor, chunks_to_import, file_hash)
        logger.info(f"Background task: Successfully stored {len(chunks_to_import)} chunks for {original_filename} (hash: {file_hash[:8]}...).")

    # --- Specific Error Handling for Background Task ---
    # Catch specific errors and log them thoroughly. Avoid raising HTTPExceptions here.
    except (PDFProcessingError, ChunkingError, EmbeddingModelError, EmbeddingGenerationError) as e:
        logger.error(f"Background task processing error for {original_filename} (hash: {file_hash[:8]}...): {e}", exc_info=True)
    except (WeaviateConnectionError, WeaviateSchemaError, WeaviateStorageError) as e:
        logger.error(f"Background task Weaviate error for {original_filename} (hash: {file_hash[:8]}...): {e}", exc_info=True)
    except FileNotFoundError as e:
        logger.error(f"Background task FileNotFoundError for {original_filename} (hash: {file_hash[:8]}...): {e}", exc_info=True)
    except PipelineError as e:
        logger.error(f"Background task general pipeline error for {original_filename} (hash: {file_hash[:8]}...): {e}", exc_info=True)
    except Exception as e:
        logger.critical(f"Background task unexpected critical error for {original_filename} (hash: {file_hash[:8]}...): {e}", exc_info=True)
    finally:
        # --- Cleanup ---
        if weaviate_client_processor:
            try:
                weaviate_client_processor.close()
                logger.info(f"Background task closed Weaviate processor client for {original_filename}.")
            except Exception as ce:
                logger.error(f"Background task error closing Weaviate processor client for {original_filename}: {ce}", exc_info=True)
        # --- Delete Temporary File created by Background Task ---
        if temp_pdf_path_obj and temp_pdf_path_obj.exists():
            try:
                temp_pdf_path_obj.unlink()
                logger.info(f"Background task deleted temporary file: {temp_pdf_path_obj}")
            except OSError as e:
                logger.error(f"Background task error deleting temporary file {temp_pdf_path_obj}: {e}")
        logger.info(f"Background task finished for {original_filename} (hash: {file_hash[:8]}...).")


# === Chat Endpoint ===
from .schemas import ChatQuery, ChatResponse # Import chat schemas
# Import the NEW conversational RAG chain function
from .rag.chain import create_conversational_rag_chain
# Import LangChain message types for history formatting
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from typing import List, Tuple

# Potentially initialize the chain once on startup for efficiency
# If the chain itself is stateless (which LangChain chains usually are),
# this avoids re-initialization overhead on every request.
# Ensure components like LLM clients within the chain are thread-safe if doing this.
# For now, keeping initialization per-request for safety, can optimize later.
# conversational_rag_chain = create_conversational_rag_chain()

def format_response(llm_response: str) -> str:
    """Formats the LLM response to highlight entitlement amounts (Hindi focus)."""
    # Extract entitlement amounts with regex (supporting commas)
    # Looks for ₹ symbol, optional space, digits/commas
    amounts = re.findall(r'₹\s*[\d,]+(?:\.\d+)?', llm_response)
    
    if amounts:
        first_amount = amounts[0]
        # Check if the first sentence already contains the amount
        # Split by potential sentence terminators (. ! ? ।)
        first_sentence = re.split(r'[.!?।]', llm_response, 1)[0]
        
        if first_amount not in first_sentence:
            # Restructure to highlight entitlement amount (Hindi phrasing)
            print(f"Response Formatting: Moving amount {first_amount} to the beginning.")
            # Remove the amount from its original position to avoid repetition (optional, can be complex)
            # llm_response_without_amount = llm_response.replace(first_amount, "", 1) 
            # return f"आपको {first_amount} की राशि मिल सकती है। " + llm_response_without_amount
            # Simpler approach: just prepend
            return f"आपको {first_amount} की राशि मिल सकती है। {llm_response}"
        else:
            print(f"Response Formatting: Amount {first_amount} already in first sentence.")
            
    return llm_response

@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat_endpoint(query: ChatQuery):
    """
    Receives a user query and conversation history.
    Processes it through the conversational RAG chain.
    Formats the response to highlight key info.
    Returns the generated answer and the updated history.
    """
    logger.info(f"Received chat query: '{query.question}', History length: {len(query.chat_history)}")

    # Format the incoming history (list of tuples) into LangChain BaseMessage objects
    # Expects [(human_msg_1, ai_msg_1), (human_msg_2, ai_msg_2), ...]
    formatted_history: List[BaseMessage] = []
    for human_msg, ai_msg in query.chat_history:
        formatted_history.append(HumanMessage(content=human_msg))
        formatted_history.append(AIMessage(content=ai_msg))

    logger.debug(f"Formatted history: {formatted_history}")

    try:
        # Initialize the CONVERSATIONAL RAG chain
        # rag_chain = conversational_rag_chain # Use pre-initialized if done at startup
        rag_chain = create_conversational_rag_chain()

        # Invoke the chain with the question AND the formatted history
        logger.debug("Invoking conversational RAG chain...")
        # The chain expects a dictionary with 'input' and 'chat_history' keys
        response = await rag_chain.ainvoke({
            "input": query.question,
            "chat_history": formatted_history
        })

        # --- Extract Answer --- 
        # Handle potential variations in chain output structure
        if isinstance(response, dict) and 'answer' in response:
            raw_answer = response['answer']
        elif isinstance(response, str):
             raw_answer = response
        else:
            logger.error(f"Unexpected RAG chain response type: {type(response)}. Response: {response}")
            raw_answer = "" # Default to empty if format is unknown
            
        logger.info(f"Conversational RAG chain generated answer (raw): {raw_answer[:100]}...")

        if not raw_answer:
            logger.warning("Conversational RAG chain returned an empty answer.")
            # Maintain the original history if no answer is generated
            # Use a more informative message
            formatted_answer = "माफ़ कीजिए, मुझे इस सवाल का जवाब नहीं मिल पाया।" # Sorry, I couldn't find an answer to this question.
            updated_history = query.chat_history # Keep original history
            return ChatResponse(answer=formatted_answer, updated_history=updated_history)

        # --- Format the Response --- 
        formatted_answer = format_response(raw_answer)
        logger.info(f"Formatted answer: {formatted_answer[:100]}...")
        # -------------------------

        # Update the history with the new exchange using the *formatted* answer
        updated_history = query.chat_history + [(query.question, formatted_answer)]

        return ChatResponse(answer=formatted_answer, updated_history=updated_history)

    # Keep existing specific error handling
    except (WeaviateConnectionError, WeaviateSchemaError, EmbeddingModelError) as e:
        # Handle specific known errors related to dependencies
        logger.error(f"Dependency error during chat processing: {e}", exc_info=True)
        raise HTTPException(status_code=503, detail=f"Service dependency error: {e}")
    except Exception as e:
        # Catch-all for unexpected errors during RAG chain execution
        logger.critical(f"Unexpected error processing chat query '{query.question}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while processing the chat query.")


# Add more endpoints later 

# --- Application Startup ---
@app.on_event("startup")
async def startup_event():
    """Runs on application startup. Ensures Weaviate connection and schema.
    If connection or schema check fails, logs FATAL error and exits.
    """
    logger.info("Starting Yojna Khojna API...")
    client = None
    try:
        logger.info("Connecting to Weaviate to ensure schema exists...")
        client = get_weaviate_client()
        ensure_schema_exists(client) # Ensure schema exists and is up-to-date
        logger.info("Weaviate connection and schema check successful.")
    except (WeaviateConnectionError, WeaviateSchemaError) as e:
        logger.error(f"FATAL: Failed to connect to Weaviate or ensure schema during startup: {e}", exc_info=True)
        # Exit the application if critical setup fails
        # Note: In a containerized environment, the orchestrator should handle restarts.
        # For local dev, exiting makes the failure obvious.
        sys.exit(f"Startup failed due to Weaviate error: {e}")
    # Removed the broad Exception catch to make failures fatal
    # except Exception as e:
    #     logger.error(f"FATAL: Unexpected error during startup: {e}", exc_info=True)
    #     sys.exit(f"Startup failed due to unexpected error: {e}")
    finally:
        if client and client.is_connected():
            client.close()
            logger.info("Closed Weaviate client connection after startup check.")

# Add more endpoints later 