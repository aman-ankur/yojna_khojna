"""Custom exception classes for the Yojna Khojna backend pipeline."""

class PipelineError(Exception):
    """Base class for exceptions in this pipeline."""
    pass

class PDFProcessingError(PipelineError):
    """Exception raised for errors during PDF text extraction or processing."""
    pass

class ChunkingError(PipelineError):
    """Exception raised for errors during text chunking."""
    pass

class EmbeddingModelError(PipelineError):
    """Exception raised for errors related to loading the embedding model."""
    pass

class EmbeddingGenerationError(PipelineError):
    """Exception raised for errors during the embedding generation process."""
    pass

class WeaviateError(PipelineError):
    """Base class for Weaviate related errors."""
    pass

class WeaviateConnectionError(WeaviateError):
    """Exception raised for errors connecting to Weaviate."""
    pass

class WeaviateSchemaError(WeaviateError):
    """Exception raised for errors related to Weaviate schema management."""
    pass

class WeaviateStorageError(WeaviateError):
    """Exception raised for errors during data storage in Weaviate."""
    def __init__(self, message, failed_objects=None):
        super().__init__(message)
        self.failed_objects = failed_objects # Optionally store details about failed batch items 