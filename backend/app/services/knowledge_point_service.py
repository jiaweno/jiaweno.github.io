# backend/app/services/knowledge_point_service.py
from typing import List, Optional 
from sqlalchemy.orm import Session
from app.db.models_sqlalchemy import KnowledgePoint as KPModel
# from app.models.learning_models import KnowledgePointCreate # Not strictly needed if passing fields directly
import uuid

def create_knowledge_point(db: Session, document_id: uuid.UUID, content_chunk: str, title: Optional[str]=None, sequence_in_document: Optional[int]=None) -> KPModel:
    # Generate a title if not provided, e.g., from the first 100 chars of the chunk
    effective_title = title if title else (content_chunk[:100] + "..." if len(content_chunk) > 100 else content_chunk)
    
    db_kp = KPModel(
        document_id=document_id,
        title=effective_title, # Use the derived or provided title
        content_chunk=content_chunk,
        sequence_in_document=sequence_in_document
    )
    db.add(db_kp)
    db.commit()
    db.refresh(db_kp)
    return db_kp

def get_knowledge_points_by_document(db: Session, document_id: uuid.UUID) -> List[KPModel]:
    return db.query(KPModel).filter(KPModel.document_id == document_id).order_by(KPModel.sequence_in_document, KPModel.created_at).all()
