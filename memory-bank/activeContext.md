# Active Context

## Current Goal
Implement stability improvements (Idempotency, Async) for the `/process-pdf` endpoint before proceeding with Phase 2 RAG tasks.

## Focus Areas
*   Implementing idempotency check using file content hashing (SHA256).
*   Refactoring `/process-pdf` to use FastAPI `BackgroundTasks`.
*   Logging deferred improvements (Input Validation, Config Checks).

## Recent Activity
*   Completed Task 2.1: Basic API Endpoint (FastAPI).
    *   Created `backend/src/main.py` with FastAPI app.
    *   Implemented synchronous `/process-pdf` endpoint.
    *   Confirmed Swagger/ReDoc UI.
*   Reviewed stability/resilience based on project context (bulk uploads, testing needs).
*   Prioritized Idempotency and Async processing.

## Blockers
*   None currently.

## Next Steps
1.  **Implement Task 2.1a: Idempotency Check:**
    *   Add logic to `/process-pdf` to calculate SHA256 hash of uploaded file content.
    *   Implement mechanism to check if hash exists before processing (e.g., check Weaviate metadata).
    *   Store the hash upon successful processing.
2.  **Implement Task 2.1b: Asynchronous Processing:**
    *   Refactor `/process-pdf` to use `BackgroundTasks`.
    *   Move file saving, `process_pdf` call, Weaviate storage, and cleanup into a background function.
    *   Update endpoint to return `202 Accepted` immediately.
3.  **Log Deferred Tasks:** Add Input Validation/Security and Config Robustness to a backlog/technical debt tracker (or note in `progress.md`).
4.  **Begin Task 2.2:** Start LangChain integration.
