# Active Context

## Current Goal
Transitioning to Task 1.8: Configuration Management after successfully implementing embedding generation and Weaviate storage.

## Focus Areas
*   Refining the data pipeline for robustness.
*   Setting up configuration loading (env vars/config file).
*   Planning for Task 2 (Search API).

## Recent Activity
*   Completed Task 1.6: Embedding Generation.
    *   Chose local Sentence Transformer model (`paraphrase-multilingual-mpnet-base-v2`).
    *   Added `sentence-transformers` to `requirements.txt`.
    *   Updated `DocumentChunk` schema in `schemas.py` to include `embedding` field.
    *   Implemented `embedding_generator.py`.
    *   Integrated into `main_pipeline.py`.
*   Completed Task 1.7: Vector DB Storage.
    *   Implemented `vector_db/weaviate_client.py` using Weaviate client v4.
    *   Added functions for connection, schema creation (`YojnaChunk` collection), and batch import.
    *   Integrated Weaviate storage step into `main_pipeline.py`.
    *   Successfully tested the full pipeline including PDF processing, embedding, and Weaviate storage.
*   Updated progress documentation.

## Blockers
*   None currently.

## Next Steps
1.  Implement Task 1.8: Configuration Management.
2.  Enhance error handling and logging (Task 1.9).
3.  Begin planning/implementation of Task 2: Semantic Search API.
