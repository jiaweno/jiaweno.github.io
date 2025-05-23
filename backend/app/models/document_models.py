from pydantic import BaseModel, Field 
from typing import Optional, List
import uuid
from enum import Enum
from datetime import datetime

class DocumentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING_OCR = "processing_ocr"       
    COMPLETED_OCR = "completed_ocr"         # Text extracted, ready for embedding
    FAILED_OCR = "failed_ocr"               
    PROCESSING_EMBEDDING = "processing_embedding" # New
    COMPLETED_EMBEDDING = "completed_embedding"   # New - Embeddings stored, KP created
    FAILED_EMBEDDING = "failed_embedding"         # New
    COMPLETED = "completed"                 # Final success state after all processing (embedding is last step for now)
    FAILED = "failed"                       # General failure 

# For endpoint payload where user only provides title and description
class DocumentUpload(BaseModel):
    title: str
    description: Optional[str] = None

# Base Pydantic model for document attributes that are common
class DocumentBase(BaseModel):
    title: str
    description: Optional[str] = None

class DocumentCreate(DocumentBase): # Used by service layer internally
    s3_url: str 
    owner_id: uuid.UUID

class DocumentUpdate(BaseModel): # For updating existing documents
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[DocumentStatus] = None 

class DocumentInDBBase(DocumentBase):
    id: uuid.UUID
    s3_url: str 
    owner_id: uuid.UUID 
    created_at: datetime
    updated_at: datetime
    status: DocumentStatus = DocumentStatus.PENDING
    
    extracted_text_s3_url: Optional[str] = None 
    processing_error: Optional[str] = None      

    class Config:
        from_attributes = True 

class Document(DocumentInDBBase): # This is the main model for responses
    pass
