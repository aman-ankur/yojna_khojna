# Phased Implementation Plan: AI-Powered Government Scheme Assistant

This document outlines the planned phases for developing the AI-Powered Government Scheme Assistant.

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