from pydantic import BaseModel, Field
from typing import Dict, Any

class DocumentChunk(BaseModel):
    """
    Represents a single chunk of text extracted from a document.
    Includes metadata about the chunk's origin.
    """
    chunk_id: str = Field(..., description="Unique identifier for the chunk (e.g., {document_id}_page_{page_num}_chunk_{chunk_index})")
    document_id: str = Field(..., description="Identifier of the source document")
    text: str = Field(..., description="The actual text content of the chunk")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata associated with the chunk (e.g., page number, chunk index)")

# You can add other data models (schemas) needed by your application here
# For example:
# class ProcessedDocument(BaseModel):
#     document_id: str
#     source_path: str
#     status: str
#     extracted_text: List[Tuple[int, str]] | None = None
#     chunks: List[DocumentChunk] | None = None 