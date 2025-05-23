from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Any, Optional 
import uuid
import logging # Added for logging

from app.db.session import get_db
from app.models.user_models import User as PydanticUser
from app.models.document_models import Document as PydanticDocument, DocumentUpload 
from app.services import document_service
from app.core.dependencies import get_current_active_user
from app.core.s3_utils import upload_file_to_s3, delete_file_from_s3
from app.core.config import settings
from app.worker.worker_setup import default_queue # Import RQ queue
from app.worker.tasks import process_document_ocr # Import OCR task

router = APIRouter()
logger = logging.getLogger(__name__) # Added logger

@router.post("/upload", response_model=PydanticDocument, status_code=status.HTTP_201_CREATED)
async def upload_document( 
    title: str = Form(...), 
    description: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: PydanticUser = Depends(get_current_active_user)
) -> Any:
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file name provided.")
    
    allowed_content_types = ["application/pdf", "image/jpeg", "image/png", "text/plain", 
                             "application/vnd.openxmlformats-officedocument.wordprocessingml.document", 
                             "application/msword"] 
    if file.content_type not in allowed_content_types:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid file type: {file.content_type}. Allowed: PDF, JPEG, PNG, TXT, DOC, DOCX.")

    s3_url = upload_file_to_s3(file=file, bucket_name=settings.AWS_S3_BUCKET_NAME, user_id=current_user.id)
    if not s3_url:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not upload file to S3.")

    doc_upload_payload = DocumentUpload(title=title, description=description)

    created_doc = document_service.create_document(
        db=db, 
        doc_in=doc_upload_payload, 
        owner_id=current_user.id, 
        s3_url=s3_url
    )
    
    if created_doc:
        try:
            default_queue.enqueue(process_document_ocr, created_doc.id)
            logger.info(f"Enqueued OCR processing task for document {created_doc.id}")
        except Exception as e:
            # Log the enqueueing error, but don't fail the upload response
            # The document is saved, but processing might need manual trigger or a cleanup job
            logger.error(f"Failed to enqueue OCR task for document {created_doc.id}: {e}")
            # Optionally, update document status to something like PENDING_MANUAL_ENQUEUE
    
    return PydanticDocument.from_orm(created_doc)

@router.get("/", response_model=List[PydanticDocument])
def list_user_documents(
    db: Session = Depends(get_db),
    current_user: PydanticUser = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 10 
) -> Any:
    documents = document_service.get_documents_by_owner(db, owner_id=current_user.id, skip=skip, limit=limit)
    return [PydanticDocument.from_orm(doc) for doc in documents] 

@router.get("/{document_id}", response_model=PydanticDocument)
def get_user_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: PydanticUser = Depends(get_current_active_user)
) -> Any:
    document = document_service.get_document_by_id(db, document_id=document_id, owner_id=current_user.id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    return PydanticDocument.from_orm(document)

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: PydanticUser = Depends(get_current_active_user)
):
    doc_to_delete = document_service.get_document_by_id(db, document_id=document_id, owner_id=current_user.id)
    if not doc_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    if not delete_file_from_s3(s3_url=doc_to_delete.s3_url, bucket_name=settings.AWS_S3_BUCKET_NAME):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete file from S3. Database record not deleted.")
    
    deleted_db_doc = document_service.delete_document(db, document_id=document_id, owner_id=current_user.id)
    if not deleted_db_doc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete document from database after S3 deletion.")

    return None
