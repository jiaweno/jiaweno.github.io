from typing import Optional, List
from sqlalchemy.orm import Session
from app.db.models_sqlalchemy import Document as DocumentModel # SQLAlchemy model
from app.models.document_models import DocumentUpload as DocumentUploadSchema, DocumentStatus # Pydantic for creation payload from endpoint, and DocumentStatus
import uuid

def create_document(db: Session, doc_in: DocumentUploadSchema, owner_id: uuid.UUID, s3_url: str) -> DocumentModel:
    db_doc = DocumentModel(
        title=doc_in.title,
        description=doc_in.description,
        s3_url=s3_url,
        owner_id=owner_id
        # status will default to PENDING due to the default in DocumentModel
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    return db_doc

def get_document_by_id(db: Session, document_id: uuid.UUID, owner_id: Optional[uuid.UUID] = None) -> Optional[DocumentModel]: # Made owner_id optional for worker use
    query = db.query(DocumentModel).filter(DocumentModel.id == document_id)
    if owner_id: # If owner_id is provided (e.g., from API endpoint), filter by it
        query = query.filter(DocumentModel.owner_id == owner_id)
    return query.first()

def get_documents_by_owner(db: Session, owner_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[DocumentModel]: # Using List from typing
    return db.query(DocumentModel).filter(DocumentModel.owner_id == owner_id).order_by(DocumentModel.created_at.desc()).offset(skip).limit(limit).all()

def delete_document(db: Session, document_id: uuid.UUID, owner_id: uuid.UUID) -> Optional[DocumentModel]:
    # Use the modified get_document_by_id that includes owner_id check
    db_doc = get_document_by_id(db, document_id=document_id, owner_id=owner_id)
    if db_doc:
        db.delete(db_doc)
        db.commit()
        return db_doc
    return None
   
def update_document_status(db: Session, document_id: uuid.UUID, status: DocumentStatus, error_message: Optional[str] = None) -> Optional[DocumentModel]:
    # Using direct query as get_document_by_id now has optional owner_id, which is fine for worker
    db_doc = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
    if db_doc:
        db_doc.status = status
        if error_message:
            db_doc.processing_error = error_message
        else:
            # Clear previous errors if status is now successful or just moving to a new processing stage without error
            db_doc.processing_error = None 
        db.commit()
        db.refresh(db_doc)
        return db_doc
    return None

def update_document_extracted_text_url(db: Session, document_id: uuid.UUID, text_s3_url: str) -> Optional[DocumentModel]:
    # Using direct query as get_document_by_id now has optional owner_id
    db_doc = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
    if db_doc:
        db_doc.extracted_text_s3_url = text_s3_url
        db.commit()
        db.refresh(db_doc)
        return db_doc
    return None
