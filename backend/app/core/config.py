from pydantic_settings import BaseSettings # Using pydantic-settings
from typing import List, Optional 

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Learning Management System"
    API_V1_STR: str = "/api/v1"
    
    # Database settings
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "lmsuser"
    POSTGRES_PASSWORD: str = "lmssecret"
    POSTGRES_DB: str = "lmsdb"
    SQLALCHEMY_DATABASE_URI: str = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}/{POSTGRES_DB}"

    # Redis settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # Vector DB settings
    # Pinecone (Legacy - can be removed if only Qdrant is used)
    VECTOR_DB_API_KEY: Optional[str] = "your-pinecone-api-key" # Renamed to be more specific
    VECTOR_DB_ENVIRONMENT: Optional[str] = "your-pinecone-environment" # Renamed

    # Qdrant settings
    QDRANT_URL: str = "http://localhost:6333" # Default local Qdrant URL
    QDRANT_API_KEY: Optional[str] = None # If using Qdrant Cloud with API key
    QDRANT_COLLECTION_NAME: str = "lms_knowledge_points" # Changed from VECTOR_DB_COLLECTION_NAME for clarity
    
    # OpenAI Settings
    OPENAI_API_KEY: str = "your-openai-api-key" # Ensure this is correctly loaded via .env
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # AWS Settings
    AWS_ACCESS_KEY_ID: str = "your-aws-access-key-id"
    AWS_SECRET_ACCESS_KEY: str = "your-aws-secret-access-key"
    AWS_S3_BUCKET_NAME: str = "your-lms-s3-bucket"
    AWS_REGION: str = "us-east-1" 
    CLOUDFRONT_DOMAIN: Optional[str] = None 

    # JWT Settings
    SECRET_KEY: str = "a_very_secret_key_that_should_be_changed" 
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7 

    class Config:
        env_file = ".env" 
        env_file_encoding = 'utf-8'

settings = Settings()
