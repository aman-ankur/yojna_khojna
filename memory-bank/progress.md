# Project Progress

## Current Phase: Phase 2 - Core Conversational API (RAG - English)

**Objective:** Create the backend API endpoint for RAG-based Q&A (English first), starting with document ingestion via API.

**Completed Tasks:**

*   [x] **1.1: Backend Environment Setup:**
    *   Initialized Python project structure (src, tests, etc.).
    *   Set up virtual environment.
    *   Created initial `requirements.txt`.
    *   Established basic logging configuration.
*   [x] **1.2: PDF Text Extraction (pdfplumber):**
    *   Implemented `pdf_extractor.py` using `pdfplumber`.
    *   Function to extract text page by page.
*   [x] **1.3: OCR Integration (pytesseract):**
    *   Integrated `pytesseract` into `pdf_extractor.py`.
    *   Added fallback logic to use OCR if direct text extraction is insufficient.
    *   Included necessary configurations (e.g., language packs `eng+hin`).
*   [x] **1.4: Vector Database Setup (Weaviate via Docker):**
    *   Created `docker-compose.yml` for Weaviate.
    *   Ensured Weaviate container runs successfully.
    *   Added `weaviate-client` to `requirements.txt`.
*   [x] **1.5: Implement Document Chunking (using LangChain):**
    *   Created `document_chunker.py` using `langchain.text_splitter.RecursiveCharacterTextSplitter`.
    *   Defined `DocumentChunk` schema in `schemas.py`.
    *   Created `main_pipeline.py` to orchestrate extraction and chunking.
    *   Tested chunking logic and pipeline integration.
*   [x] **1.6: Embedding Generation:**
    *   Choose an embedding model (e.g., Sentence Transformers, OpenAI API).
    *   Implement function in `embedding_generator.py` to generate vector embeddings for `DocumentChunk` text.
    *   Add necessary dependencies to `requirements.txt`.
*   [x] **1.7: Data Loading into Weaviate:**
    *   Implement `weaviate_loader.py` to connect to Weaviate.
    *   Define Weaviate schema for storing chunks and vectors.
    *   Load `DocumentChunk` objects and their embeddings into Weaviate.
*   [x] **1.8: Configuration Management** - Load settings (paths, model names, DB URLs) from env vars or config file.
    *   Implemented using `python-dotenv` in `config.py`.
    *   Loads `WEAVIATE_URL`, `EMBEDDING_MODEL_NAME`, `DEFAULT_TEST_PDF` with defaults.
*   [x] **1.9: Error Handling & Logging** - Enhance robustness and logging across the pipeline.
    *   Custom exceptions defined and used (`exceptions.py`).
    *   Key functions raise specific errors.
    *   Main pipeline includes `try...except` blocks for different stages.
    *   Logging centralized via `logging_config.py` and `dictConfig`. Removed `basicConfig` calls.
*   [x] **1.10: Testing** - Add more comprehensive unit and integration tests.
    *   Fixed issues with Weaviate client tests (updated to use VectorDistances instead of DistanceMetric).
    *   Enhanced embedding_generator tests with cases for mixed languages, empty text, and dimensionality checks.
    *   Added integration tests for the full pipeline from document chunks to embeddings to vector storage.
    *   Created test scaffolding for future search functionality.
    *   Added proper pytest configuration with custom markers.
*   [x] **2.1: Basic API Endpoint (FastAPI):**
    *   Added `fastapi`, `uvicorn`, `python-multipart` to dependencies.
    *   Created `backend/src/main.py` with FastAPI app instance.
    *   Added `/health` check endpoint.
    *   Implemented `/process-pdf` endpoint:
        *   Accepts PDF file upload.
        *   Saves file temporarily.
        *   Calls `process_pdf` from `main_pipeline.py`.
        *   Connects to Weaviate and stores resulting chunks/embeddings.
        *   Handles pipeline and Weaviate errors with HTTP exceptions.
        *   Includes temporary file cleanup and Weaviate client closure.
    *   Added `__init__.py` files for package structure.
    *   Enabled automatic Swagger (`/docs`) and ReDoc (`/redoc`) documentation.

*   [ ] **2.1a: Implement Idempotency Check:**
    *   Add SHA256 hash calculation for uploaded PDF content.
    *   Check against stored hashes (e.g., in Weaviate metadata) before processing.
    *   Store hash on successful processing.
*   [ ] **2.1b: Implement Asynchronous Processing:**
    *   Refactor `/process-pdf` to use FastAPI `BackgroundTasks`.
    *   Return `202 Accepted` immediately.
*   [ ] **2.1c: Log Deferred Improvements:** (Optional tracking task)
    *   Note Input Validation/Security and Config Robustness for future work.

**Current / Next Task:**

*   [ ] **2.1a: Implement Idempotency Check**

*   [ ] **2.2: Integrate LangChain for RAG:** (Renumbered/Refined from original plan)
    *   Integrate `langchain` components for building a Retrieval-Augmented Generation chain.
    *   Connect the chain to the Weaviate vector store as the retriever.
*   [ ] **2.3: Integrate LLM API:** (Renumbered/Refined)
    *   Choose and configure an LLM API client (e.g., OpenAI, Anthropic).
    *   Integrate the LLM into the LangChain RAG setup.
*   [ ] **2.4: Build Core RAG Chain:** (Renumbered/Refined)
    *   Construct the primary LangChain sequence: Retriever -> Prompt -> LLM -> Output Parser.
*   [ ] **2.5: Create `/chat` API Endpoint:** (Renumbered/Refined)
    *   Define a new endpoint in `main.py` to accept user queries.
    *   Pass the query to the RAG chain.
    *   Return the LLM's response.

---

*Note: This file tracks the high-level progress. Detailed decisions and technical context are in other `memory-bank` files. Task numbering refined based on implementation progress.*
