# System Patterns: AI-Powered Government Scheme Assistant (POC)

## High-Level Architecture

The system follows a modular architecture comprising several key components communicating via APIs, primarily built using Python (FastAPI) for the backend and React.js for the frontend.

```mermaid
graph TD
    User[User (Web/Mobile)] --> Frontend[Frontend Application (React.js)];
    Frontend --> API_GW[API Gateway / Backend (FastAPI)];
    API_GW --> ConvIF[Conversational Interface];
    API_GW --> ImgMod[Image Understanding Module];
    API_GW --> SchemeMatch[Scheme Matching Service];

    ConvIF --> LLM[LLM (OpenAI/Anthropic)];
    ConvIF --> RAG[RAG (LangChain)];
    ConvIF --> StateMgmt[Conversation State (Redis)];
    RAG --> VecDB[Vector Database (Pinecone/Weaviate)];

    ImgMod --> VisionModel[Vision Foundation Model (CLIP)];
    ImgMod --> CloudVision[Cloud Vision API (Fallback)];

    SchemeMatch --> RulesEngine[Rules Engine (Python)];
    SchemeMatch --> VecDB;

    subgraph DocProcessing [Document Processing Engine (Offline/Batch)]
        direction LR
        PDFIngest[PDF Ingestion (PyPDF2/Tesseract)] --> InfoExtract[Information Extraction (Hugging Face NER)];
        InfoExtract --> KnowledgeStore[Knowledge Storage];
        KnowledgeStore --> VecDB;
    end

    User -- Image Upload --> ImgMod;
```

## Key Architectural Patterns & Decisions

1.  **Modular Design:** The system is broken down into distinct services (Document Processing, Conversational Interface, Image Understanding, Scheme Matching) to promote separation of concerns and independent development/scaling.
2.  **API-Driven Communication:** Components interact primarily through RESTful APIs managed by the FastAPI backend.
3.  **Retrieval Augmented Generation (RAG):** The Conversational Interface uses RAG to ground LLM responses in factual information retrieved from the processed government scheme documents stored in a vector database. This enhances accuracy and reduces hallucination.
4.  **Vector Database for Semantic Search:** A vector database (Pinecone/Weaviate) stores embeddings of document chunks, enabling efficient semantic search for relevant information based on user queries.
5.  **Hybrid Search:** The Scheme Matching Service employs both keyword-based filtering and semantic search on the vector database for robust scheme identification.
6.  **Multimodal Input:** The system is designed to handle both text queries and image uploads (e.g., photos of housing conditions) using a dedicated Image Understanding Module.
7.  **Cloud LLM Integration:** Leverages external LLM APIs (OpenAI/Anthropic) for advanced natural language understanding and generation, facilitated by LangChain.
8.  **State Management:** Redis is used to maintain conversation history and user context across multiple turns.
9.  **Offline Document Processing:** The resource-intensive task of ingesting, processing (OCR, NER), and embedding government documents is handled by a separate, potentially batch-oriented, pipeline.
10. **Progressive Web App (PWA):** The frontend is planned as a PWA to potentially offer some offline capabilities and better mobile integration.
11. **Containerization:** Docker is planned for containerizing application components, simplifying deployment and ensuring consistency across environments.

## Data Flow

*   **Text Query:** User Query -> Frontend -> Backend API -> Conversational Interface -> RAG -> Vector DB -> LLM -> Response -> Frontend -> User.
*   **Image Query:** User Image Upload -> Frontend -> Backend API -> Image Understanding Module -> Scheme Matching Service (+ Text Context from Conv. Interface) -> Vector DB -> Response -> Frontend -> User.
*   **Document Processing (Offline):** PDF/Scanned Docs -> Document Processing Engine -> Vector DB.
