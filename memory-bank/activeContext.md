# Active Context

## Current Goal
Implement Phase 1, Task 1.6: Embedding Generation for document chunks.

## Focus Areas
*   Selecting an appropriate text embedding model (considering performance, cost, and language support).
*   Creating `embedding_generator.py` module.
*   Integrating the embedding step into `main_pipeline.py`.
*   Adding necessary libraries (e.g., `sentence-transformers`) to `requirements.txt`.

## Recent Activity
*   Completed Task 1.5: Document Chunking.
    *   Implemented `document_chunker.py` using `RecursiveCharacterTextSplitter`.
    *   Defined `DocumentChunk` schema in `schemas.py`.
    *   Created `main_pipeline.py` to orchestrate PDF extraction and chunking.
    *   Successfully tested the pipeline integration.
*   Updated progress documentation.

## Blockers
*   None currently.

## Next Steps
1.  Discuss and decide on the embedding model.
2.  Add the chosen embedding library to `requirements.txt`.
3.  Implement the `generate_embeddings` function.
4.  Modify `main_pipeline.py` to call the embedding function.
5.  Test the embedding generation.
