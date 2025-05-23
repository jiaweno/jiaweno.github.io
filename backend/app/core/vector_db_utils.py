# backend/app/core/vector_db_utils.py
import logging
from typing import List, Optional, Dict, Any 
import uuid 
from qdrant_client import QdrantClient, models
from qdrant_client.http.exceptions import UnexpectedResponse # More specific exception
from app.core.config import settings

logger = logging.getLogger(__name__)

def get_qdrant_client() -> QdrantClient:
    if settings.QDRANT_URL.startswith("http"): # For non-cloud, local Qdrant
        client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY if settings.QDRANT_API_KEY else None)
    else: # For Qdrant Cloud (uses host and api_key, or grpc_port for gRPC)
        client = QdrantClient(
            host=settings.QDRANT_URL, # Assuming QDRANT_URL stores the host for cloud, or adjust config
            api_key=settings.QDRANT_API_KEY,
            # grpc_port=6334, # if using gRPC for cloud
            # prefer_grpc=True, # if using gRPC for cloud
        )
    logger.info(f"Qdrant client initialized for URL/host: {settings.QDRANT_URL}")
    return client

def get_embedding_dimension(model_name: str) -> int:
    # Simplified mapping, can be expanded or made more robust
    if "ada-002" in model_name: return 1536
    if "text-embedding-3-small" in model_name: return 1536 
    if "text-embedding-3-large" in model_name: return 3072
    logger.warning(f"Unknown OpenAI embedding model name '{model_name}' for dimension lookup. Defaulting to 1536. This might be incorrect.")
    return 1536 

def ensure_collection_exists(client: QdrantClient, collection_name: str, vector_size: int):
    try:
        client.get_collection(collection_name=collection_name)
        logger.info(f"Collection '{collection_name}' already exists.")
    except UnexpectedResponse as e: # Catching the specific exception for "Not Found"
        if e.status_code == 404: # HTTP 404 Not Found
            logger.info(f"Collection '{collection_name}' not found, creating it.")
            client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE)
            )
            logger.info(f"Collection '{collection_name}' created successfully.")
        else:
            logger.error(f"Error checking/creating collection {collection_name} (UnexpectedResponse): {e}")
            raise
    except Exception as e: # Catch other potential errors (e.g., network issues)
        logger.error(f"An unexpected error occurred while checking/creating collection {collection_name}: {e}")
        raise

def upsert_embedding(client: QdrantClient, collection_name: str, kp_id: uuid.UUID, vector: List[float], payload: Optional[Dict[str, Any]] = None):
    point_id_str = str(kp_id) # Qdrant point IDs can be UUIDs or strings; string representation is safe
    points = [models.PointStruct(id=point_id_str, vector=vector, payload=payload or {})]
    try:
        client.upsert(collection_name=collection_name, points=points, wait=True) # wait=True for confirmation
        logger.info(f"Upserted embedding for KP ID {kp_id} into '{collection_name}'.") # Changed to info for successful operation
    except Exception as e:
        logger.error(f"Failed to upsert embedding for KP ID {kp_id} into '{collection_name}': {e}")
        raise # Re-raise the exception to be handled by the calling task

# Example: For searching later (not part of this subtask but good to keep in mind)
# def search_embeddings(client: QdrantClient, collection_name: str, query_vector: List[float], limit: int = 5) -> List[models.ScoredPoint]:
#     search_result = client.search(
#         collection_name=collection_name,
#         query_vector=query_vector,
#         limit=limit
#     )
#     return search_result
