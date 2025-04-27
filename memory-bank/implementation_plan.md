# Phased Implementation Plan: AI-Powered Government Scheme Assistant

This document outlines the planned phases for developing the AI-Powered Government Scheme Assistant.

**Note on Environment:** The Python backend virtual environment is located at `backend/yojna`. Activate using `source backend/yojna/bin/activate` (macOS/Linux) from the workspace root before running backend commands.

# Implementation Plan - Enhanced RAG Pipeline

## Phase 1: Analysis and Design (Completed ✅)

- [x] **1.1: Analyze Current Limitations**
  - [x] Review existing prompt structure and limitations
  - [x] Identify missing domain-specific context
  - [x] Document issues with cross-document connections
  - [x] Analyze response formatting gaps

- [x] **1.2: Design Enhanced Prompts**
  - [x] Draft query reformulation prompt
  - [x] Draft comprehensive RAG prompt
  - [x] Design entity extraction strategy
  - [x] Plan response formatting approach

## Phase 2: Implementation (Completed ✅)

- [x] **2.1: Enhanced Prompts**
  - [x] Implement "Yojna Khojna Question Reformulation System" prompt
  - [x] Implement "Yojna Khojna Government Scheme Assistant" prompt
  - [x] Remove sentence limitation

- [x] **2.2: Entity Extraction System**
  - [x] Implement domain-specific dictionary
  - [x] Add multilingual NER with xx_ent_wiki_sm
  - [x] Create regex fallback for when spaCy is unavailable
  - [x] Add entity prioritization logic

- [x] **2.3: Enhanced Retrieval**
  - [x] Implement enhanced_retrieval_step function
  - [x] Add contextual follow-up queries
  - [x] Implement document deduplication

- [x] **2.4: Response Formatting**
  - [x] Implement format_response to highlight monetary amounts
  - [x] Add language detection
  - [x] Handle both Hindi and English responses

## Phase 3: Testing (Completed ✅)

- [x] **3.1: Unit Testing**
  - [x] Test entity extraction
  - [x] Test prompt functionality
  - [x] Test response formatting

- [x] **3.2: Integration Testing**
  - [x] Test end-to-end enhanced RAG pipeline
  - [x] Test language handling
  - [x] Test empty/error responses

- [x] **3.3: Test Infrastructure**
  - [x] Create spaCy model verification script
  - [x] Create test runner script
  - [x] Fix all test failures

## Phase 4: Evaluation (Next Steps)

- [ ] **4.1: Manual Evaluation**
  - [ ] Create test cases across different scheme categories
  - [ ] Perform side-by-side comparisons with previous system
  - [ ] Evaluate Hindi and English handling

- [ ] **4.2: Benchmarking**
  - [ ] Create benchmark dataset
  - [ ] Measure improvements in:
    - [ ] Answer completeness
    - [ ] Cross-document connections
    - [ ] Practical guidance quality
    - [ ] Response formatting

## Phase 5: Documentation and Deployment

- [ ] **5.1: Documentation**
  - [ ] Create user guide with examples
  - [ ] Update technical documentation
  - [ ] Create deployment guide with spaCy model instructions

- [ ] **5.2: Deployment**
  - [ ] Test in staging environment
  - [ ] Update Docker configuration for spaCy models
  - [ ] Deploy to production

## Timeline

- **Phases 1-3** (Analysis, Implementation, Testing): Completed
- **Phase 4** (Evaluation): 1-2 weeks
- **Phase 5** (Documentation and Deployment): 1-2 weeks

## Key Metrics for Success

- All test cases passing
- Improved answer completeness (examples containing specific entitlement amounts)
- Better cross-document synthesis
- Consistent handling of both Hindi and English queries
- Proper highlighting of monetary values
- Functional multilingual entity extraction

**Phase 1: Foundational Data Pipeline & Knowledge Base**

*   **Goal:** Ingest government scheme documents, process them, and create a searchable knowledge base.
*   **Key Tasks:**
    1.  [X] Set up the Python backend environment.
    2.  [X] Implement PDF ingestion and text extraction (`pdfplumber`).
    3.  [X] Integrate Tesseract OCR (with Hindi support).
    4.  [X] Set up a vector database (Weaviate via Docker).
    5.  [ ] Implement document chunking.
    6.  [ ] Implement text embedding (Hugging Face) and store vectors/metadata.
    7.  [ ] Build initial pipeline scripts.
*   **Outcome:** A functional pipeline to process documents and populate a vector DB for semantic search.

**Phase 2: Core Conversational API (RAG - English)**

*   **Goal:** Create the backend API endpoint for RAG-based Q&A (English first).
*   **Key Tasks:**
    1.  Set up FastAPI project.
    2.  Integrate LangChain for RAG.
    3.  Connect LangChain to the vector DB.
    4.  Integrate with an LLM API (OpenAI/Anthropic).
    5.  Build the core RAG chain.
    6.  Create a `/chat` API endpoint in FastAPI.
    7.  Set up Redis (via Docker) for session state.
*   **Outcome:** A working backend API answering English questions via RAG.

**Phase 3: Basic Frontend Interface**

*   **Goal:** Develop a simple web UI for interaction.
*   **Key Tasks:**
    1.  Set up a React project (TypeScript).
    2.  Integrate UI library (Chakra UI / Material UI).
    3.  Build a simple chat interface.
    4.  Connect frontend to the backend `/chat` endpoint.
*   **Outcome:** An MVP web interface for English Q&A.

**Phase 4: Multilingual Support & Enhanced NLP**

*   **Goal:** Add Hindi support and improve information extraction.
*   **Key Tasks:**
    1.  Validate/tune Hindi OCR.
    2.  Adapt NLP pipeline for Hindi.
    3.  Modify RAG/prompts for bilingual support.
    4.  Start fine-tuning NER model for scheme details.
    5.  Plan structured data storage alongside vectors.
    6.  Enable Hindi input/display in frontend.
*   **Outcome:** Bilingual (Hindi/English) assistant with improved extraction accuracy.

**Phase 5: Scheme Matching & Personalization**

*   **Goal:** Implement personalized scheme matching and eligibility checks.
*   **Key Tasks:**
    1.  Define user profile model.
    2.  Add UI for profile collection (considering privacy).
    3.  Develop Scheme Matching Service (hybrid filter/semantic).
    4.  Design conversational flows for eligibility checks.
    5.  Create new API endpoints for profile/matching.
*   **Outcome:** Personalized scheme recommendations and eligibility guidance.

**Phase 6: Image Understanding, Application Guidance & Deployment Prep**

*   **Goal:** Add image analysis, application steps, and prepare for deployment.
*   **Key Tasks:**
    1.  Implement frontend image upload.
    2.  Build backend Image Understanding Module (CLIP).
    3.  Integrate image analysis into matching logic.
    4.  Provide step-by-step application guidance using extracted data.
    5.  Refine Dockerfiles/Docker Compose.
    6.  Implement CI/CD pipelines (GitHub Actions).
*   **Outcome:** Feature-rich assistant with multimodal input, application support, ready for deployment.

**Phase 7: Testing, Deployment & Iteration**

*   **Goal:** Ensure quality, deploy, and establish feedback loop.
*   **Key Tasks:**
    1.  Write comprehensive tests (unit, integration, E2E).
    2.  Conduct User Acceptance Testing (UAT).
    3.  Deploy to cloud infrastructure (AWS/GCP).
    4.  Set up monitoring, logging, alerting.
    5.  Iterate based on feedback and metrics.
*   **Outcome:** Deployed, tested application with ongoing improvement process. 