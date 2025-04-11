# Active Context

## Current Goal
Starting Phase 2: Core Conversational API (RAG - English) with Task 2.1: Basic API Endpoint (FastAPI).

## Focus Areas
*   Setting up the FastAPI application structure.
*   Creating the initial `/process-pdf` endpoint.
*   Integrating the existing `main_pipeline.py` logic into the API.

## Recent Activity
*   Completed Task 1.9a: Refine Logging Setup.
    *   Created `logging_config.py` using `dictConfig` for centralized setup.
    *   Called `setup_logging()` in `main_pipeline.py`.
    *   Removed `basicConfig` calls from `pdf_extractor.py` and `document_chunker.py`.
    *   Ensured consistent use of `logging.getLogger(__name__)`.
*   Verified Task 1.8 (Config Management) was complete.
*   Completed Task 1.10 (Testing).

## Blockers
*   None currently.

## Next Steps
1.  **Implement Task 2.1: Basic API Endpoint (FastAPI):**
    *   Add `fastapi` and `uvicorn` to `requirements.txt` (if not already present).
    *   Create `backend/src/main.py` for the FastAPI app.
    *   Define the `/process-pdf` endpoint (accepting file uploads).
    *   Adapt `run_pipeline()` logic to be called by the endpoint.
