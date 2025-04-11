# Yojna Khojna: AI Government Scheme Assistant

This project aims to build an AI-powered assistant to help Indian citizens understand and access government welfare schemes. It processes official documents (PDFs, including scanned ones) and provides a conversational interface (Hindi/English) for discovering schemes, checking eligibility, and understanding application processes.

## Core Idea

Government scheme information in India is often fragmented, complex, and hard for citizens to navigate. This project uses NLP and RAG (Retrieval Augmented Generation) techniques to bridge this gap by extracting information from source documents and presenting it accessibly.

## Key Features (Planned)

*   **Document Processing:** Ingests PDFs, performs OCR (Tesseract) on scanned documents, extracts text.
*   **Knowledge Base:** Uses a vector database (Weaviate) to store document embeddings for semantic search.
*   **Conversational AI (RAG):** Leverages LangChain and LLMs (OpenAI/Anthropic) to answer user queries based on retrieved document context.
*   **Bilingual Support:** Designed for both Hindi and English interaction.
*   **Personalization:** Aims to match users to relevant schemes based on profile information.
*   **Web Interface:** React-based frontend for user interaction.

## Tech Stack

*   **Backend:** Python, FastAPI, LangChain, Pytesseract, Pdfplumber
*   **Frontend:** React (TypeScript), Chakra UI / Material UI (TBD)
*   **Database:** Weaviate (Vector DB), Redis (Session State)
*   **Core AI:** Hugging Face Transformers (Embeddings/NER), LLM APIs (OpenAI/Anthropic)
*   **Infrastructure:** Docker, Docker Compose, GitHub Actions

## Getting Started

### Prerequisites

*   Python 3.9+
*   Docker & Docker Compose
*   Tesseract OCR Engine:
    *   macOS: `brew install tesseract tesseract-lang`
    *   Debian/Ubuntu: `sudo apt install tesseract-ocr tesseract-ocr-hin tesseract-ocr-eng`
    *   Windows: Installer from Tesseract GitHub (ensure Hindi/English packs are selected and `tesseract.exe` is in PATH).

### Backend Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd yojna_khojna
    ```
2.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```
3.  **Create and activate the virtual environment:**
    ```bash
    python3 -m venv yojna
    source yojna/bin/activate
    # On Windows: .\yojna\Scripts\activate
    ```
4.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Running the PDF Extractor (Test)

1.  Ensure the virtual environment is active (`source backend/yojna/bin/activate`).
2.  Place a sample PDF (text-based or scanned) into the `backend/test_docs/` directory.
3.  Update the `test_pdf_path` variable near the end of `backend/src/data_pipeline/pdf_extractor.py` to point to your test file.
4.  Run the script from the `backend` directory:
    ```bash
    python src/data_pipeline/pdf_extractor.py
    ```

### Running the Full Application (TBD)

Instructions for running the FastAPI server and the React frontend will be added once those components are further developed.

## Project Structure

```
.
├── .cursor/            # Cursor AI configuration and rules
├── backend/
│   ├── src/            # Backend source code (API, pipeline)
│   ├── test_docs/      # Sample documents for testing pipeline
│   ├── .gitignore
│   ├── requirements.txt
│   └── yojna/          # Python virtual environment (ignored by git)
├── frontend/           # (Placeholder for React frontend)
├── memory-bank/        # Project context, plans, progress docs
└── README.md           # This file
```

## Contributing

(Details TBD)

## License

(Details TBD) 