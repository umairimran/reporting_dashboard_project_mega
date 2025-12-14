"""
Facebook file upload processing.
"""
from fastapi import UploadFile
from sqlalchemy.orm import Session
import uuid
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from app.facebook.models import UploadedFile
from app.facebook.validator import FacebookValidator
from app.facebook.parser import FacebookParser
from app.etl.orchestrator import ETLOrchestrator
from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import ValidationError


class FacebookUploadHandler:
    """Handler for Facebook file uploads and processing."""
    
    def __init__(self, db: Session):
        self.db = db
        self.orchestrator = ETLOrchestrator(db)
    
    def _get_upload_directory(self, client_id: uuid.UUID) -> str:
        """Get or create upload directory for a client."""
        upload_dir = os.path.join(settings.UPLOAD_DIR, 'facebook', str(client_id))
        os.makedirs(upload_dir, exist_ok=True)
        return upload_dir
    
    def _save_uploaded_file(self, file: UploadFile, upload_dir: str) -> tuple[str, int]:
        """
        Save uploaded file to disk.
        
        Returns:
            Tuple of (file_path, file_size)
        """
        # Generate unique filename to avoid conflicts
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(upload_dir, filename)
        
        # Save file
        with open(file_path, 'wb') as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_size = os.path.getsize(file_path)
        
        logger.info(f"Saved uploaded file: {file_path} ({file_size} bytes)")
        
        return file_path, file_size
    
    async def process_upload(
        self,
        file: UploadFile,
        client_id: uuid.UUID,
        client_name: str,
        user_id: uuid.UUID,
        admin_emails: Optional[List[str]] = None
    ) -> UploadedFile:
        """
        Process uploaded Facebook file.
        
        Args:
            file: Uploaded file
            client_id: Client ID
            client_name: Client name
            user_id: User who uploaded the file
            admin_emails: List of admin emails for alerts
            
        Returns:
            UploadedFile record
        """
        logger.info(f"Processing Facebook upload for client {client_name}: {file.filename}")
        
        # Validate file
        await FacebookValidator.validate_upload(file)
        
        # Get upload directory
        upload_dir = self._get_upload_directory(client_id)
        
        # Save file
        file_path, file_size = self._save_uploaded_file(file, upload_dir)
        
        # Create upload record
        uploaded_file = UploadedFile(
            client_id=client_id,
            source='facebook',
            file_name=file.filename,
            file_path=file_path,
            file_size=file_size,
            upload_status='pending',
            uploaded_by=user_id
        )
        
        self.db.add(uploaded_file)
        self.db.commit()
        self.db.refresh(uploaded_file)
        
        logger.info(f"Created upload record: {uploaded_file.id}")
        
        # Parse and process asynchronously
        try:
            # Update status to processing
            uploaded_file.upload_status = 'processing'
            self.db.commit()
            
            # Parse file
            logger.info(f"Parsing Facebook file: {file.filename}")
            raw_records = FacebookParser.parse_file(file_path)
            uploaded_file.records_count = len(raw_records)
            self.db.commit()
            
            logger.info(f"Parsed {len(raw_records)} records from Facebook file")
            
            # Run ETL pipeline
            from datetime import date
            ingestion_log = await self.orchestrator.run_etl_pipeline(
                client_id=client_id,
                client_name=client_name,
                raw_records=raw_records,
                source='facebook',
                run_date=date.today(),
                file_name=file.filename,
                admin_emails=admin_emails
            )
            
            # Update status based on ETL result
            if ingestion_log.status == 'success':
                uploaded_file.upload_status = 'processed'
            elif ingestion_log.status == 'partial':
                uploaded_file.upload_status = 'processed'
                uploaded_file.error_message = f"Partial success: {ingestion_log.message}"
            else:
                uploaded_file.upload_status = 'failed'
                uploaded_file.error_message = f"ETL failed: {ingestion_log.message}"
            
            uploaded_file.processed_at = datetime.utcnow()
            
            logger.info(f"Facebook upload processing completed: {uploaded_file.upload_status}")
            
        except Exception as e:
            uploaded_file.upload_status = 'failed'
            uploaded_file.error_message = str(e)
            uploaded_file.processed_at = datetime.utcnow()
            logger.error(f"Facebook upload processing failed: {str(e)}", exc_info=True)
        
        self.db.commit()
        self.db.refresh(uploaded_file)
        
        return uploaded_file
    
    def get_upload_history(
        self,
        client_id: uuid.UUID,
        limit: int = 50
    ) -> List[UploadedFile]:
        """Get upload history for a client."""
        return self.db.query(UploadedFile).filter(
            UploadedFile.client_id == client_id,
            UploadedFile.source == 'facebook'
        ).order_by(UploadedFile.created_at.desc()).limit(limit).all()
    
    def get_upload_by_id(self, upload_id: uuid.UUID) -> Optional[UploadedFile]:
        """Get upload record by ID."""
        return self.db.query(UploadedFile).filter(
            UploadedFile.id == upload_id
        ).first()
