"""
AWS S3 service for Surfside data downloads.
"""
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from typing import List, Optional
from datetime import date, datetime
import os
from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import S3Error


class S3Service:
    """Service for AWS S3 operations."""
    
    def __init__(self):
        """Initialize S3 client."""
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
            self.bucket_name = settings.S3_BUCKET_NAME
        except NoCredentialsError:
            raise S3Error("AWS credentials not found")
    
    def list_files(self, prefix: str = "") -> List[str]:
        """
        List all files in S3 bucket with optional prefix.
        
        Args:
            prefix: Optional prefix to filter files
            
        Returns:
            List of file keys
            
        Raises:
            S3Error: If listing fails
        """
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            if 'Contents' not in response:
                return []
            
            files = [obj['Key'] for obj in response['Contents']]
            logger.info(f"Found {len(files)} files in S3 bucket with prefix '{prefix}'")
            
            return files
            
        except ClientError as e:
            logger.error(f"Error listing S3 files: {str(e)}")
            raise S3Error(f"Failed to list S3 files: {str(e)}")
    
    def download_file(self, s3_key: str, local_path: str) -> str:
        """
        Download file from S3 to local path.
        
        Args:
            s3_key: S3 object key
            local_path: Local file path to save to
            
        Returns:
            Local file path
            
        Raises:
            S3Error: If download fails
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            self.s3_client.download_file(
                Bucket=self.bucket_name,
                Key=s3_key,
                Filename=local_path
            )
            
            logger.info(f"Downloaded {s3_key} to {local_path}")
            return local_path
            
        except ClientError as e:
            logger.error(f"Error downloading S3 file: {str(e)}")
            raise S3Error(f"Failed to download {s3_key}: {str(e)}")
    
    def find_file_for_date(self, target_date: date, client_prefix: str = "") -> Optional[str]:
        """
        Find Surfside file for a specific date.
        
        Expected file pattern: surfside_YYYY-MM-DD.csv or surfside_YYYY-MM-DD.xlsx
        
        Args:
            target_date: Date to find file for
            client_prefix: Optional client-specific prefix
            
        Returns:
            S3 key if found, None otherwise
        """
        date_str = target_date.strftime('%Y-%m-%d')
        
        # Try different file patterns
        patterns = [
            f"{client_prefix}surfside_{date_str}.csv",
            f"{client_prefix}surfside_{date_str}.xlsx",
            f"{client_prefix}Surfside_{date_str}.csv",
            f"{client_prefix}Surfside_{date_str}.xlsx",
            f"{client_prefix}{date_str}_surfside.csv",
            f"{client_prefix}{date_str}_surfside.xlsx"
        ]
        
        all_files = self.list_files(prefix=client_prefix)
        
        for pattern in patterns:
            if pattern in all_files:
                logger.info(f"Found file for date {date_str}: {pattern}")
                return pattern
        
        logger.warning(f"No file found for date {date_str}")
        return None
    
    def download_file_for_date(
        self,
        target_date: date,
        client_prefix: str = "",
        download_dir: str = "/tmp/surfside"
    ) -> Optional[str]:
        """
        Find and download Surfside file for a specific date.
        
        Args:
            target_date: Date to download file for
            client_prefix: Optional client-specific prefix
            download_dir: Local directory to save file
            
        Returns:
            Local file path if successful, None otherwise
        """
        s3_key = self.find_file_for_date(target_date, client_prefix)
        
        if not s3_key:
            return None
        
        # Create local file path
        filename = os.path.basename(s3_key)
        local_path = os.path.join(download_dir, filename)
        
        return self.download_file(s3_key, local_path)
    
    def file_exists(self, s3_key: str) -> bool:
        """
        Check if file exists in S3.
        
        Args:
            s3_key: S3 object key
            
        Returns:
            True if file exists, False otherwise
        """
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except ClientError:
            return False
