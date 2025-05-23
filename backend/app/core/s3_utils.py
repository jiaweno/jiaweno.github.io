import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from fastapi import UploadFile
import logging
from app.core.config import settings
import uuid

logger = logging.getLogger(__name__)

def get_s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )

def upload_file_to_s3(file: UploadFile, bucket_name: str, user_id: uuid.UUID) -> str | None:
    s3_client = get_s3_client()
    # Generate a unique filename to prevent overwrites and add user context
    file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'bin'
    s3_filename = f"uploads/{user_id}/{uuid.uuid4()}.{file_extension}"
    
    try:
        s3_client.upload_fileobj(file.file, bucket_name, s3_filename)
        # Construct the URL. This might vary based on your S3 setup (e.g., if using CloudFront in front)
        # For direct S3 URL:
        if settings.CLOUDFRONT_DOMAIN:
            file_url = f"https://{settings.CLOUDFRONT_DOMAIN}/{s3_filename}"
        else:
            file_url = f"https://{bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{s3_filename}"
        
        logger.info(f"File {file.filename} uploaded to {file_url}")
        return file_url
    except FileNotFoundError: # Should not happen with UploadFile's SpooledTemporaryFile
        logger.error(f"The file {file.filename} was not found for upload.")
        return None
    except NoCredentialsError:
        logger.error("Credentials not available for AWS S3.")
        return None
    except ClientError as e:
        logger.error(f"S3 ClientError: {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred during S3 upload: {e}")
        return None

def delete_file_from_s3(s3_url: str, bucket_name: str) -> bool:
    s3_client = get_s3_client()
    # Extract object key from S3 URL
    # This parsing needs to be robust, assuming standard S3 URL or CloudFront URL structure
    object_key = None
    if settings.CLOUDFRONT_DOMAIN and s3_url.startswith(f"https://{settings.CLOUDFRONT_DOMAIN}/"):
        object_key = s3_url.replace(f"https://{settings.CLOUDFRONT_DOMAIN}/", "")
    elif s3_url.startswith(f"https://{bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/"):
        object_key = s3_url.replace(f"https://{bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/", "")
    else:
        logger.error(f"Could not parse S3 object key from URL: {s3_url}")
        return False
    
    try:
        s3_client.delete_object(Bucket=bucket_name, Key=object_key)
        logger.info(f"File {object_key} deleted from S3 bucket {bucket_name}.")
        return True
    except ClientError as e:
        logger.error(f"S3 ClientError during delete: {e}")
        return False
    except Exception as e:
        logger.error(f"An unexpected error occurred during S3 delete: {e}")
        return False
