# Technical Context: AI-Powered Government Scheme Assistant (POC)

This document outlines the specific technologies and tools proposed for the Proof of Concept (POC) implementation.

## Backend

*   **Language:** Python
*   **Framework:** FastAPI (for API development)
*   **Document Processing:**
    *   PDF Text Extraction: PyPDF2 / pdfplumber
    *   OCR: Tesseract (with Hindi language pack)
    *   NLP/Information Extraction: Hugging Face Transformers (specifically fine-tuned NER models)
*   **Conversational AI:**
    *   LLM: Anthropic Claude API
    *   Orchestration/RAG: LangChain
*   **State Management:** Redis
*   **Image Understanding:**
    *   Vision Models: CLIP or similar pre-trained models
    *   Fallback: Cloud Vision APIs (e.g., Google Cloud Vision)
*   **Rules Engine:** Simple Python implementation (for initial scheme matching logic)
*   **Chunking:** `langchain` library (`RecursiveCharacterTextSplitter`) for splitting extracted text into manageable chunks.

## Data Storage

*   **Vector Database:** Pinecone or Weaviate (for semantic search on document embeddings)
*   **Metadata/Structured Data:** Potentially a relational DB or NoSQL DB alongside the vector DB for structured scheme info (TBD based on evolution beyond POC). Redis for session state.

## Frontend

*   **Framework:** React.js
*   **UI Library:** Chakra UI or Material UI
*   **Type:** Progressive Web App (PWA)

## Deployment & Infrastructure (POC)

*   **Containerization:** Docker
*   **Orchestration:** Docker Compose (for local/simple deployments)
*   **Hosting:** Cloud VPS or Managed Container Service (e.g., AWS ECS, Google Cloud Run)
*   **CI/CD:** GitHub Actions

## Key Technical Considerations & Potential Constraints

*   **Multilingual Processing:** Requires robust handling of both Hindi (Devanagari script) and English text in NLP models, OCR, and potentially the LLM interactions.
*   **OCR Accuracy:** Accuracy of Tesseract on scanned government documents, especially in Hindi, needs validation.
*   **NER Model Fine-tuning:** Requires effort to fine-tune NER models for specific government scheme terminology and structures.
*   **LLM API Costs & Latency:** Dependence on external LLM APIs introduces cost and potential latency concerns. Rate limits might apply.
*   **Vector Database Selection:** Choice between Pinecone/Weaviate depends on cost, scalability needs, and specific feature requirements (e.g., metadata filtering).
*   **Low Bandwidth Optimization:** Frontend and API design must consider users with limited internet connectivity.
*   **Data Privacy & Security:** Handling potentially sensitive user information (profile, uploaded images) requires secure storage and processing practices.
*   **Scalability:** While the POC focuses on core functionality, the architecture should allow for future scaling.
*   **Asynchronous Processing Strategy (PDF Ingestion):**
    *   **Current:** Using FastAPI's built-in `BackgroundTasks` for the `/process-pdf` endpoint. This makes the API endpoint non-blocking for the client (suitable for initial development and testing).
    *   **Future Enhancement:** Plan to migrate to a dedicated Task Queue (e.g., Celery with Redis) for improved scalability, resilience (retries, persistence), and resource isolation, especially to handle bulk uploads efficiently and prevent heavy processing from impacting API server responsiveness. This migration is likely targeted for later phases (e.g., Deployment Prep).

### Data Management

*   **PDF Parsing:** `