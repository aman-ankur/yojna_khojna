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
*   **Other:** `python-dotenv` (config), `PyMuPDF` (PDF text extraction), `spacy` (NER for enhanced retrieval)

## Data Storage

*   **Vector Database:** Pinecone or Weaviate (for semantic search on document embeddings)
*   **Metadata/Structured Data:** Potentially a relational DB or NoSQL DB alongside the vector DB for structured scheme info (TBD based on evolution beyond POC). Redis for session state.

## Frontend

*   **Framework:** React.js (v19)
*   **Language:** TypeScript
*   **Build Tool:** Vite
*   **UI Library:** Material UI (MUI) - *(Chosen over Chakra UI due to integration issues during development)*
*   **State Management:** React Context API (for simple cases), potentially Zustand or Redux Toolkit if complexity grows.
*   **API Client:** Axios
*   **Styling:** Emotion (via MUI), CSS Modules (if needed)
*   **Testing:** Vitest, React Testing Library
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

### Vector Store: Weaviate

*   **Reasoning**: Open-source, good performance, supports hybrid search, and integrates well with LangChain.
*   **Configuration**: Deployed locally via Docker Compose (`docker-compose.yml`).
*   **Class Name**: `YojnaChunk` (This is the schema class name used to store processed document chunks).
*   **Text Property**: `text` (This is the property within `YojnaChunk` storing the chunk's text content).
*   **LangChain Integration**: Using `langchain-weaviate` package for v4 client compatibility.

### Conversation History Management

*   **Current Approach (Cost Optimized for POC):**
    *   Uses LangChain's `create_history_aware_retriever` pattern.
    *   An initial LLM call rephrases the user's latest question based on the chat history to create a standalone query for the retriever.
    *   The *final* question-answering prompt (passed to `create_stuff_documents_chain`) **does not** include the full chat history. It only uses the (potentially rephrased) question and the retrieved document context.
    *   **Rationale:** This significantly reduces costs associated with the final LLM call, as the prompt size doesn't grow linearly with the conversation. It forces the final answer to be strongly grounded in the retrieved documents, which aligns well with the goal of providing factual scheme information. The history-aware retriever ensures relevant context is used for document fetching.
    *   **Trade-off:** The final answer might be slightly less conversational (won't explicitly reference past turns unless captured in the rephrased question).
*   **Future Alternatives (if needed):**
    *   **Windowed History:** Pass only the last `k` turns to the final QA prompt (simpler, but may lose context).
    *   **Summarization Memory:** Use an LLM to summarize older history (preserves more context, but adds complexity and summarization cost).
    *   **Full History (Original POC approach):** Pass the entire history to the final QA prompt (most conversational context, highest potential cost).

### Enhanced Entity Extraction System

*   **Problem Addressed:** Standard Named Entity Recognition (NER) doesn't adequately capture domain-specific government scheme terminology, especially in a bilingual (Hindi/English) context.

*   **Implementation:**
    *   **Multilingual NER Model:** Replaced the English-only `en_core_web_sm` with `xx_ent_wiki_sm` for better Hindi support.
    *   **Domain Dictionary:** Created a comprehensive dictionary with 12 categories covering all aspects of government schemes:
        * Social welfare (housing schemes)
        * Healthcare benefits
        * Education support
        * Employment programs
        * Agricultural assistance
        * Utilities and subsidies
        * Disaster relief
        * Special category benefits (widows, disabled, etc.)
        * Financial assistance terms
        * Document requirements
        * Authorities and offices
        * Procedural terms
    *   **Multi-Strategy Extraction:**
        * Standard NER for recognizing general entities (ORG, PERSON, GPE, LOC)
        * Regular expression pattern matching for scheme names, monetary amounts
        * Dictionary lookup for domain-specific terminology
        * Bilingual term matching that pairs Hindi/English equivalents
    *   **Entity Prioritization:** Scoring algorithm to rank extracted entities based on:
        * Presence in original query (highest priority)
        * Entity type (schemes and monetary amounts get higher priority)
        * Relevance to eligibility, application process, documents
    *   **Graceful Degradation:** Robust fallback to regex-based extraction when spaCy is unavailable
    *   **Contextual Follow-Up Queries:** Context-aware query generation based on entity type:
        * Scheme-specific queries focus on eligibility and benefits
        * Financial queries focus on amounts and processes
        * Beneficiary queries focus on available schemes
        * Document queries focus on requirements and procedures

*   **File Structure:**
    *   **Main Implementation:** `backend/src/rag/chain.py`
        * `extract_key_entities`: The core extraction function
        * `prioritize_entities`: Entity ranking algorithm
        * `regex_entity_extraction`: Fallback mechanism
        * `generate_contextual_follow_up_query`: Query generation based on entity type
    *   **Testing:** `backend/tests/rag/test_chain.py` and `backend/src/rag/test_entity_extraction.py`
    *   **Documentation:** `entity_extraction_strategy.md` and `entity_extraction_setup.md`

*   **Integration:** The entity extraction is integrated into the enhanced retrieval pipeline:
    1. Initial search using the reformulated query
    2. Entity extraction from query and initial results
    3. Contextual follow-up searches for each extracted entity
    4. Result combination and deduplication
    5. Response generation with the comprehensive QA prompt

*   **Performance Considerations:**
    *   Text truncation to first 500 characters per document to improve processing speed
    *   Limited to top 5 most relevant entities to reduce follow-up searches
    *   Caching for spaCy model loading to avoid redundant initialization

*   **Deployment Requirements:**
    *   Additional dependency: `spacy>=3.0.0,<4.0.0`
    *   Additional model installation: `python -m spacy download xx_ent_wiki_sm`
    *   Updated Docker configuration with model installation step

## Testing
*   **Framework:** `pytest`
*   **Utilities:** `pytest-asyncio`, `pytest-mock`, `httpx` (for TestClient)

## Suggested Questions Feature Architecture

The Suggested Questions feature enhances user experience by providing contextually relevant follow-up questions after each assistant response. It follows a hybrid approach combining template-based and LLM-powered question generation.

### Frontend Components

```
SuggestedQuestions/
├── SuggestedQuestions.tsx   # Displays question chips in a horizontal scrollable container
├── hooks/
│   └── useSuggestions.ts    # Custom hook to fetch and manage suggestions state
└── services/
    └── suggestionsService.ts # API service for fetching suggestions
```

**Key features:**
- Horizontally scrollable question chips with tooltips
- Text truncation with fixed-width styling
- Automatic language matching (Hindi/English)
- Error handling and graceful degradation
- Integration with main chat flow

### Backend Components

```
src/
├── schemas.py                # Defines SuggestedQuestion and related schemas
├── main.py                   # Contains /suggested-questions API endpoint
└── services/
    └── suggestion_service.py # Implements question generation logic
```

**Generation strategy:**
1. **Entity extraction** - Identifies scheme names, amounts, and documents
2. **Template-based questions** - Uses predefined templates for common patterns
3. **LLM-generated questions** - Uses Claude to generate contextual questions
4. **Language detection** - Ensures questions match the conversation language
5. **Prioritization** - Selects top 4 most relevant questions

### Data Flow

1. User receives a response from the assistant
2. Frontend requests suggested questions from backend
3. Backend:
   - Analyzes conversation context and extracts entities
   - Generates template-based questions
   - Uses LLM to generate contextual questions
   - Selects and returns top 4 most relevant questions
4. Frontend displays the questions as clickable chips
5. When a user clicks a question, it's submitted as a new user query

### Testing Strategy

- **Frontend Tests:** Component rendering, function prop handling, error cases
- **Backend Tests:** Entity extraction, question generation, API contract

### Integration Points

- Integrates with the ChatContainer/ChatMessages components
- Leverages the existing entity extraction system
- Uses the Claude LLM through LangChain for question generation
- Handles both Hindi and English languages