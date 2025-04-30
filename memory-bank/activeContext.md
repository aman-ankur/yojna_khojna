# Active Context & Current Focus

## Project Status (Updated: April 2025)

The Yojna Khojna project is a RAG-based government scheme assistant for low-literacy Indian populations. We are currently in the evaluation phase after successfully completing the enhanced RAG pipeline implementation.

### Completed Components

1. **Core Data Pipeline**:
    - PDF extraction (including table detection/marking)
    - **Semantic Document Chunking**: Implemented strategy to preserve tables and split along section boundaries (`document_chunker.py`).
    - Embedding generation
    - Weaviate storage
2. **Basic RAG Backend**: Initial version with LangChain and Claude integration
3. **Frontend Interface**: React-based chat UI with bilingual support
4. **Enhanced RAG Pipeline**:
   - New prompts for better reformulation and practical answers
   - Domain-specific entity extraction with multilingual support **(including enhanced financial entity detection)**
   - Enhanced retrieval with follow-up queries
   - Response formatting with monetary amount highlighting
   - Completed comprehensive test suite (tests passing after user fixes)

### Current Focus: Evaluation and Deployment

We're now focused on evaluating the enhanced RAG system and preparing for deployment:

1. **Evaluation**:
   - Manual testing with real-world queries across different scheme categories
   - Side-by-side comparison of old vs. new RAG system
   - Measuring improvements in answer quality, comprehensiveness, and cross-document synthesis

2. **Documentation**:
   - Creating user guides and examples
   - Updating technical documentation
   - Creating deployment instructions including spaCy model setup
   - **Improving PDF Table Extraction (Completed):** Enhanced `pdf_extractor.py` to detect and format tables as Markdown, preserving structured data during ingestion. Added corresponding tests.

3. **Deployment Preparation**:
   - Testing in a staging environment
   - Updating Docker configuration for spaCy models
   - Final quality assurance checks

## Technical Requirements & Constraints

The implementation maintains the following key requirements:

1. **Architectural**: LangChain-based RAG using Weaviate vector database
2. **Performance**: Optimized for responsive user experience with cost awareness
3. **Deployment**: Docker-containerized with proper environment setup for spaCy
4. **Testing**: Comprehensive test coverage for all components
5. **Languages**: Bilingual support (Hindi/English)

## Development Environment

- **Backend**: Python FastAPI with LangChain, Weaviate, spaCy, and Claude API
- **Frontend**: React TypeScript with Material UI
- **Local Setup**: Docker for Weaviate, virtual environment for Python

## Dependencies

- **LLM**: Anthropic Claude (version 3)
- **Vector DB**: Weaviate
- **NLP**: spaCy with xx_ent_wiki_sm (multilingual model)
- **Embedding**: Sentence-Transformers
- **PDF Processing**: pdfplumber (with table extraction) + pytesseract OCR fallback

## Immediate Next Steps

1. Create test cases for manual evaluation across different scheme categories **(including specific tests for financial queries)**
2. Develop a benchmark dataset for measuring improvements
3. Document examples of enhanced responses for stakeholders
4. Prepare deployment guide with spaCy model setup instructions
