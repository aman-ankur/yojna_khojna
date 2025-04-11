# Cursor AI Rules: AI-Powered Government Scheme Assistant

## 1. Project Goal & Vision

**Primary Goal:** Build an intuitive, accessible, and trustworthy AI assistant that empowers Indian citizens by simplifying information about government welfare schemes.

**Core Functionality:**
*   Process official government documents (PDFs, potentially scanned images).
*   Extract structured information and key details about schemes.
*   Provide conversational guidance in **both Hindi and English**.
*   Offer personalized scheme recommendations based on user profiles.
*   Clearly explain eligibility criteria and application processes.
*   Answer specific user questions accurately, citing sources.

## 2. Core Principles & User Experience

*   **Accessibility:** Prioritize clear, simple language, avoiding complex jargon. Ensure the UI (React frontend) is intuitive, responsive, and optimized for low-bandwidth conditions.
*   **Bilingual Support:** All user-facing interactions, data processing, and AI responses must seamlessly support both **Hindi (Devanagari script) and English**. This includes NLP, OCR, and LLM interactions.
*   **Personalization:** Tailor responses and scheme suggestions based on user-provided context (location, income, needs, etc.) maintained via Redis session state.
*   **Trust & Transparency:** Ground AI responses in factual information extracted from official documents. Use Retrieval Augmented Generation (RAG) via LangChain. Cite sources whenever possible. Clearly state when information cannot be found or the AI is uncertain.
*   **Accuracy:** Ensure the information extraction (NER) and scheme matching logic are as accurate as possible. Validate OCR results, especially for Hindi.
*   **Step-by-Step Guidance:** Assist users through complex processes like eligibility checks and applications with clear, sequential instructions.

## 3. Technical Stack & Constraints

*   **Backend:** Python with FastAPI. Use strict typing (type hints).
*   **Frontend:** React.js (likely with TypeScript, adhering to global rules) using Chakra UI or Material UI. Target a Progressive Web App (PWA).
*   **Conversational AI:** LangChain for RAG orchestration, integrating with OpenAI or Anthropic LLMs.
*   **Data Storage:**
    *   Vector Database (Pinecone/Weaviate) for semantic search on document embeddings.
    *   Redis for session/conversation state management.
    *   Metadata/Structured Data storage TBD (may involve SQL/NoSQL alongside vector DB).
*   **Document Processing:** PyPDF2/pdfplumber for text extraction, Tesseract for OCR (ensure Hindi support), Hugging Face Transformers for NER (requires fine-tuning for scheme details).
*   **Image Understanding:** Use CLIP or similar models, potentially falling back to Cloud Vision APIs.
*   **Deployment:** Docker for containerization, Docker Compose for local setup, target Cloud VPS or managed container services (AWS/GCP), use GitHub Actions for CI/CD.
*   **Key Constraints:** Address challenges in multilingual processing (Hindi/English), OCR accuracy for government documents (especially Hindi), NER model fine-tuning effort, LLM API costs/latency, and data privacy/security.

## 4. Architecture & System Patterns

*   **Modular Design:** Adhere to the defined modular architecture (API Gateway, Conversational Interface, Image Understanding, Scheme Matching, Document Processing).
*   **API-Driven:** Communication between frontend and backend, and between backend microservices (if applicable later), should be via well-defined RESTful APIs (FastAPI).
*   **RAG Implementation:** Prioritize the Retrieval Augmented Generation pattern using LangChain to ensure responses are grounded in the knowledge base (Vector DB).
*   **Hybrid Search:** Implement scheme matching using a combination of semantic search (Vector DB) and potentially keyword/rule-based filtering.
*   **Offline Processing:** Keep the document ingestion, OCR, NER, and embedding pipeline separate from the real-time request path.

## 5. Coding Standards & Practices

*   **Language:** Python (backend), TypeScript/JavaScript (frontend).
*   **Style:** Follow PEP 8 for Python and standard TypeScript/React best practices. Use linters and formatters.
*   **Error Handling:** Implement robust error handling using specific exceptions and try-catch blocks.
*   **Logging:** Use appropriate logging levels (DEBUG, INFO, ERROR) to track application flow and issues.
*   **Testing:** Adhere to Test-Driven Development (TDD) principles where practical. Write unit tests (pytest for Python, Jest/RTL for React) covering core logic, edge cases, and error conditions. Aim for high coverage on critical components.
*   **Asynchronicity:** Use `async`/`await` for I/O-bound operations in both Python (FastAPI/asyncio) and JavaScript/TypeScript.
*   **Backend Environment:** The Python virtual environment is located at `backend/yojna`. Activate using `source backend/yojna/bin/activate` (macOS/Linux) from the workspace root.

## 6. Version Control

*   Follow standard Git workflows (feature branches, descriptive commits, clear PRs). Reference global rules for specifics.

--- 