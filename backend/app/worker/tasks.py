import logging
import os
import tempfile
import uuid
from io import BytesIO
from typing import Optional, List # Added List for type hinting

import pytesseract # type: ignore
from PIL import Image # type: ignore
from sqlalchemy.orm import Session # type: ignore

from app.core.config import settings
from app.core.s3_utils import upload_file_to_s3, get_s3_client 
from app.db.session import SessionLocal 
from app.models.document_models import DocumentStatus
from app.services import document_service
from app.db.models_sqlalchemy import Document as DocumentModel 

# New imports for embedding task
import nltk # type: ignore
import openai # type: ignore
import tiktoken # type: ignore
from app.core.vector_db_utils import get_qdrant_client, ensure_collection_exists, upsert_embedding, get_embedding_dimension
from app.services import knowledge_point_service # New service
from app.worker.worker_setup import default_queue # RQ queue

logger = logging.getLogger(__name__)
if not logger.hasHandlers(): 
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# NLTK setup
try:
    nltk.data.find('tokenizers/punkt')
except nltk.downloader.DownloadError:
    logger.info("NLTK 'punkt' tokenizer not found. Downloading...")
    nltk.download('punkt', quiet=True)

# OpenAI API Key Setup
if settings.OPENAI_API_KEY:
    openai.api_key = settings.OPENAI_API_KEY
else:
    logger.warning("OPENAI_API_KEY not found in settings. Embedding task will likely fail.")


# Moved download_file_from_s3 to module level if not already in s3_utils
# (It was already at module level in the previous version of tasks.py)
def download_file_from_s3(s3_url: str, bucket_name: str) -> Optional[BytesIO]:
    s3_client = get_s3_client()
    object_key = None
    if settings.CLOUDFRONT_DOMAIN and s3_url.startswith(f"https://{settings.CLOUDFRONT_DOMAIN}/"):
        object_key = s3_url.split(f"https://{settings.CLOUDFRONT_DOMAIN}/", 1)[1]
    elif s3_url.startswith(f"https://{bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/"):
        object_key = s3_url.split(f"https://{bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/", 1)[1]
    elif s3_url.startswith(f"https://{bucket_name}.s3.amazonaws.com/"): 
        object_key = s3_url.split(f"https://{bucket_name}.s3.amazonaws.com/", 1)[1]
    else:
        logger.error(f"Could not parse S3 object key from URL for download: {s3_url}")
        return None
    
    try:
        file_buffer = BytesIO()
        s3_client.download_fileobj(bucket_name, object_key, file_buffer)
        file_buffer.seek(0)
        logger.info(f"File {object_key} downloaded from S3 bucket {bucket_name}.")
        return file_buffer
    except Exception as e:
        logger.error(f"Error downloading {object_key} from S3: {e}")
        return None


def get_text_chunks_nltk(text: str, max_tokens: int = 500, model_name: str = settings.OPENAI_EMBEDDING_MODEL) -> List[str]:
    try:
        encoding = tiktoken.encoding_for_model(model_name)
    except KeyError:
        logger.warning(f"Model {model_name} not found for tiktoken. Using cl100k_base.")
        encoding = tiktoken.get_encoding("cl100k_base")

    sentences = nltk.sent_tokenize(text)
    chunks = []
    current_chunk_list: List[str] = [] # Explicitly type for clarity
    current_chunk_tokens = 0

    for sentence in sentences:
        sentence_token_count = len(encoding.encode(sentence))
        
        if sentence_token_count > max_tokens:
            if current_chunk_list:
                chunks.append(" ".join(current_chunk_list))
                current_chunk_list = []
                current_chunk_tokens = 0
            
            words = sentence.split()
            temp_sub_chunk: List[str] = []
            temp_sub_chunk_tokens = 0
            for word in words:
                word_token_count = len(encoding.encode(word + " ")) 
                if temp_sub_chunk_tokens + word_token_count > max_tokens:
                    if temp_sub_chunk: chunks.append(" ".join(temp_sub_chunk))
                    temp_sub_chunk = [word]
                    temp_sub_chunk_tokens = word_token_count
                else:
                    temp_sub_chunk.append(word)
                    temp_sub_chunk_tokens += word_token_count
            if temp_sub_chunk: chunks.append(" ".join(temp_sub_chunk))
            continue

        if current_chunk_tokens + sentence_token_count <= max_tokens:
            current_chunk_list.append(sentence)
            current_chunk_tokens += sentence_token_count
        else:
            if current_chunk_list:
                chunks.append(" ".join(current_chunk_list))
            current_chunk_list = [sentence]
            current_chunk_tokens = sentence_token_count
    
    if current_chunk_list:
        chunks.append(" ".join(current_chunk_list))
        
    return [chunk for chunk in chunks if chunk.strip()]


def process_document_ocr(document_id: uuid.UUID):
    logger.info(f"Starting OCR processing for document_id: {document_id}")
    db: Session = SessionLocal() 
    doc = None # Initialize doc to None
    try:
        doc = document_service.get_document_by_id(db, document_id=document_id, owner_id=None)
        if not doc:
            logger.error(f"Document {document_id} not found in DB for OCR processing.")
            return

        document_service.update_document_status(db, document_id, DocumentStatus.PROCESSING_OCR)
        logger.info(f"Document {document_id} status updated to PROCESSING_OCR.")

        file_content_buffer = download_file_from_s3(doc.s3_url, settings.AWS_S3_BUCKET_NAME)
        if not file_content_buffer:
            raise ValueError(f"Failed to download file from S3: {doc.s3_url}")

        extracted_text = ""
        text_extracted_successfully = False
        file_extension = doc.s3_url.split('?')[0].split('.')[-1].lower()

        if file_extension in ['png', 'jpg', 'jpeg', 'tiff', 'bmp', 'gif']:
            try:
                image = Image.open(file_content_buffer)
                extracted_text = pytesseract.image_to_string(image)
                text_extracted_successfully = True
                logger.info(f"OCR successful for image: {doc.s3_url}")
            except Exception as e:
                logger.error(f"Pytesseract OCR failed for image {doc.s3_url}: {e}")
                raise ValueError(f"Pytesseract OCR processing error: {e}")
        elif file_extension == 'pdf':
            try:
                from pdf2image import convert_from_bytes # type: ignore
                images = convert_from_bytes(file_content_buffer.read())
                for i, image_page in enumerate(images):
                    extracted_text += pytesseract.image_to_string(image_page) + "\n\n"
                text_extracted_successfully = True
                logger.info(f"OCR successful for PDF: {doc.s3_url}")
            except ImportError:
                logger.error("pdf2image library is not installed. Cannot process PDF for OCR.")
                raise ValueError("pdf2image library not installed.")
            except Exception as e:
                logger.error(f"Pytesseract OCR (via pdf2image) failed for PDF {doc.s3_url}: {e}")
                raise ValueError(f"PDF OCR processing error (ensure poppler-utils is installed): {e}")
        elif file_extension == 'txt':
            try:
                extracted_text = file_content_buffer.read().decode('utf-8')
                text_extracted_successfully = True
                logger.info(f"Successfully read text content from .txt file: {doc.s3_url}")
            except Exception as e:
                logger.error(f"Failed to read .txt file {doc.s3_url}: {e}")
                raise ValueError(f"Error reading text file: {e}")
        else:
            logger.info(f"File type {file_extension} not processed by OCR/direct text extraction.")
            document_service.update_document_status(db, document_id, DocumentStatus.FAILED_OCR, error_message="File type not suitable for OCR or text extraction.")
            return # No text to process further

        if not extracted_text.strip() and text_extracted_successfully:
            logger.warning(f"OCR/text extraction for document {document_id} resulted in empty text.")
            document_service.update_document_status(db, document_id, DocumentStatus.FAILED_OCR, "OCR/text extraction resulted in empty text.")
            return # No text to process further
        
        if not text_extracted_successfully: # Should have been caught by earlier return, but as a safeguard
            logger.warning(f"Text extraction was not successful for document {document_id}, file type: {file_extension}")
            document_service.update_document_status(db, document_id, DocumentStatus.FAILED_OCR, "Text extraction not performed due to file type or error.")
            return

        text_file_name = f"extracted_texts/{doc.owner_id}/{document_id}.txt"
        class TextUploadFile:
            def __init__(self, content: bytes, filename: str):
                self.file = BytesIO(content)
                self.filename = filename
        text_upload_file = TextUploadFile(content=extracted_text.encode('utf-8'), filename=text_file_name)
        
        extracted_text_s3_url = upload_file_to_s3(
            file=text_upload_file, # type: ignore 
            bucket_name=settings.AWS_S3_BUCKET_NAME,
            user_id=doc.owner_id 
        )

        if not extracted_text_s3_url:
            raise ValueError("Failed to upload extracted text to S3.")

        document_service.update_document_extracted_text_url(db, document_id, extracted_text_s3_url)
        document_service.update_document_status(db, document_id, DocumentStatus.COMPLETED_OCR)
        logger.info(f"Document {document_id} OCR processing completed. Text at {extracted_text_s3_url}")
        
        # Enqueue embedding task
        default_queue.enqueue(process_document_embedding, document_id, job_timeout='2h')
        logger.info(f"Enqueued embedding task for document {document_id}")

    except Exception as e:
        logger.error(f"Unhandled error in OCR processing for document {document_id}: {e}", exc_info=True)
        if doc: # Check if doc was fetched before error
            document_service.update_document_status(db, document_id, DocumentStatus.FAILED_OCR, error_message=str(e))
    finally:
        db.close()
        logger.info(f"Closed DB session for OCR task, document_id: {document_id}")


def process_document_embedding(document_id: uuid.UUID):
    logger.info(f"Starting embedding processing for document_id: {document_id}")
    db: Session = SessionLocal()
    qdrant_client = None
    doc = None # Initialize doc to None
    try:
        doc = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
        if not doc or not doc.extracted_text_s3_url:
            logger.error(f"Document {document_id} or its extracted text URL not found for embedding.")
            if doc: document_service.update_document_status(db, document_id, DocumentStatus.FAILED_EMBEDDING, "Extracted text S3 URL not found.")
            return

        document_service.update_document_status(db, document_id, DocumentStatus.PROCESSING_EMBEDDING)

        text_content_buffer = download_file_from_s3(doc.extracted_text_s3_url, settings.AWS_S3_BUCKET_NAME)
        if not text_content_buffer:
            raise ValueError("Failed to download extracted text from S3 for embedding.")
        extracted_text = text_content_buffer.read().decode('utf-8')

        if not extracted_text.strip(): # Check if the extracted text is empty
            logger.warning(f"Extracted text for document {document_id} is empty. Skipping embedding.")
            document_service.update_document_status(db, document_id, DocumentStatus.FAILED_EMBEDDING, "Extracted text is empty, cannot process embeddings.")
            return

        text_chunks = get_text_chunks_nltk(extracted_text, model_name=settings.OPENAI_EMBEDDING_MODEL)
        if not text_chunks:
            logger.warning(f"No text chunks generated for document {document_id} after splitting.")
            document_service.update_document_status(db, document_id, DocumentStatus.FAILED_EMBEDDING, "Text chunking resulted in no processable chunks.")
            return
        
        logger.info(f"Document {document_id} split into {len(text_chunks)} chunks for embedding.")

        qdrant_client = get_qdrant_client()
        embedding_dimension = get_embedding_dimension(settings.OPENAI_EMBEDDING_MODEL)
        ensure_collection_exists(qdrant_client, settings.QDRANT_COLLECTION_NAME, embedding_dimension)

        for i, chunk_text in enumerate(text_chunks):
            if not chunk_text.strip():
                logger.debug(f"Skipping empty chunk {i+1}/{len(text_chunks)} for document {document_id}")
                continue
            try:
                response = openai.embeddings.create(
                    input=chunk_text,
                    model=settings.OPENAI_EMBEDDING_MODEL
                )
                embedding_vector = response.data[0].embedding

                kp = knowledge_point_service.create_knowledge_point(
                    db=db, 
                    document_id=document_id, 
                    content_chunk=chunk_text,
                    sequence_in_document=i+1 
                )

                qdrant_payload = {
                    "document_id": str(doc.id),
                    "document_title": doc.title,
                    "text_chunk_preview": chunk_text[:200] + "..." if len(chunk_text) > 200 else chunk_text,
                    "kp_id": str(kp.id)
                }
                upsert_embedding(qdrant_client, settings.QDRANT_COLLECTION_NAME, kp.id, embedding_vector, qdrant_payload)
                logger.debug(f"Processed chunk {i+1}/{len(text_chunks)} (KP ID: {kp.id}) for document {document_id}")

            except Exception as chunk_error:
                logger.error(f"Error processing chunk {i+1} for document {document_id}: {chunk_error}", exc_info=True)
                # Decide if one chunk error should fail the whole document embedding
        
        document_service.update_document_status(db, document_id, DocumentStatus.COMPLETED_EMBEDDING) # Changed to COMPLETED_EMBEDDING
        logger.info(f"Document {document_id} embedding processing completed successfully.")

    except Exception as e:
        logger.error(f"Overall error in embedding processing for document {document_id}: {e}", exc_info=True)
        if doc: # Check if doc was fetched
            document_service.update_document_status(db, document_id, DocumentStatus.FAILED_EMBEDDING, error_message=str(e))
    finally:
        db.close()
        logger.info(f"Closed DB session for embedding task, document_id: {document_id}")
