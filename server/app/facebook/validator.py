"""
File validation for Facebook uploads.
"""
from fastapi import UploadFile, HTTPException, status
from typing import List
import os
from app.core.config import settings
from app.core.logging import logger


class FacebookValidator:
    """Validator for Facebook file uploads."""
    
    ALLOWED_EXTENSIONS = ['.csv', '.xlsx', '.xls']
    MAX_FILE_SIZE = settings.MAX_UPLOAD_SIZE  # 50MB
    
    REQUIRED_COLUMNS = [
        'Date',
        'Campaign Name',
        'Ad Set Name',
        'Ad Name',
        'Impressions',
        'Clicks',
        'Conversions',
        'Revenue'
    ]
    
    @staticmethod
    def validate_file_extension(filename: str) -> bool:
        """
        Validate file extension.
        
        Args:
            filename: Name of uploaded file
            
        Returns:
            True if valid, False otherwise
        """
        ext = os.path.splitext(filename)[1].lower()
        return ext in FacebookValidator.ALLOWED_EXTENSIONS
    
    @staticmethod
    def validate_file_size(file_size: int) -> bool:
        """
        Validate file size.
        
        Args:
            file_size: Size of file in bytes
            
        Returns:
            True if valid, False otherwise
        """
        return file_size <= FacebookValidator.MAX_FILE_SIZE
    
    @staticmethod
    async def validate_upload(file: UploadFile) -> None:
        """
        Validate uploaded file.
        
        Args:
            file: Uploaded file
            
        Raises:
            HTTPException: If validation fails
        """
        # Check file extension
        if not FacebookValidator.validate_file_extension(file.filename):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file format. Allowed: {', '.join(FacebookValidator.ALLOWED_EXTENSIONS)}"
            )
        
        # Read file to check size
        content = await file.read()
        file_size = len(content)
        
        # Reset file pointer
        await file.seek(0)
        
        if not FacebookValidator.validate_file_size(file_size):
            max_mb = FacebookValidator.MAX_FILE_SIZE / (1024 * 1024)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Maximum size: {max_mb}MB"
            )
        
        logger.info(f"File validation passed: {file.filename} ({file_size} bytes)")
