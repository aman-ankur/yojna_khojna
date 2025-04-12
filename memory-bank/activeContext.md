# Active Context

## Current Goal
Begin Phase 2, Task 2.2: Integrate LangChain for RAG.

## Focus Areas
*   Adding LangChain dependencies.
*   Creating a LangChain Retriever component using the Weaviate vector store.
*   Structuring the RAG module/code.

## Recent Activity
*   Completed Task 2.1a (Idempotency Check):
    *   Implemented SHA256 hashing for `/process-pdf`.
    *   Added Weaviate check for existing document hash.
*   Completed Task 2.1b (Asynchronous Processing):
    *   Refactored `/process-pdf` using FastAPI `BackgroundTasks`.
    *   Endpoint now returns immediately, processing occurs in background.
*   Added unit tests for the new functionality in `test_main.py`.

## Blockers
*   None currently.

## Next Steps
1.  **Add LangChain Dependencies:** Update `requirements.txt` with `langchain`, `langchain-community`, etc.
2.  **Create RAG Module:** Set up a new directory/file (e.g., `backend/src/rag/retriever.py`).
3.  **Implement Weaviate Retriever:** Write code to initialize `langchain_community.vectorstores.Weaviate` connected to our client and schema.
