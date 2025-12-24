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
    
    # Required columns (normalized to lowercase for case-insensitive matching)
    REQUIRED_COLUMNS = [
        # 'reporting starts',  # TODO: Awaiting client confirmation on date field
        'campaign name',
        'ad set name',
        'ad name',
        'impressions',
        # 'link clicks',  # TODO: Awaiting client confirmation (Link clicks vs Clicks (all))
        # 'conversions',  # TODO: Not in current CSV - awaiting client confirmation
        # 'revenue'  # TODO: Not in current CSV - awaiting client confirmation
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
        
        # Check file size by seeking to end
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)
        
        if not FacebookValidator.validate_file_size(file_size):
            max_mb = FacebookValidator.MAX_FILE_SIZE / (1024 * 1024)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Maximum size: {max_mb}MB"
            )
        
        logger.info(f"File validation passed: {file.filename} ({file_size} bytes)")
