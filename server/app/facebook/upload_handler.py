"""
Facebook file upload processing.
"""
from fastapi import UploadFile
from sqlalchemy.orm import Session
import uuid
import os
import shutil
from datetime import datetime, date
from pathlib import Path
from typing import List, Optional
from app.facebook.models import UploadedFile
from app.facebook.validator import FacebookValidator
from app.facebook.parser import FacebookParser
from app.etl.orchestrator import ETLOrchestrator
from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import ValidationError
from app.core.database import SessionLocal


async def process_facebook_upload_background(
    upload_id: uuid.UUID,
    file_path: str,
    file_name: str,
    client_id: uuid.UUID,
    client_name: str,
    ingestion_log_id: uuid.UUID,
    admin_emails: Optional[List[str]] = None
):
    """
    Background task to process Facebook upload (runs AFTER response is sent).
    """
    db = SessionLocal()
    ingestion_log = None
    
    try:
        logger.info(f"Starting background processing for upload {upload_id}")
        
        # Get upload record
        uploaded_file = db.query(UploadedFile).filter(UploadedFile.id == upload_id).first()
        if not uploaded_file:
            logger.error(f"Upload record not found: {upload_id}")
            return
            
        # Get ingestion log
        from app.metrics.models import IngestionLog
        ingestion_log = db.query(IngestionLog).filter(IngestionLog.id == ingestion_log_id).first()
        
        if not ingestion_log:
            logger.error(f"Ingestion log not found: {ingestion_log_id}")
            return

        orchestrator = ETLOrchestrator(db)

        # Parse file
        # print("[STEP 4] PARSING FILE (BACKGROUND)...")
        logger.info(f"Parsing Facebook file: {file_name}")
        
        try:
            raw_records = FacebookParser.parse_file(file_path)
            uploaded_file.records_count = len(raw_records)
            db.commit()
            
            # print(f"✓ File parsed successfully")
            # print(f"  Total records found: {len(raw_records)}\n")
            logger.info(f"Parsed {len(raw_records)} records from Facebook file")
            
            # Run ETL pipeline
            # print("[STEP 5] STARTING ETL PIPELINE (BACKGROUND)...\n")
            ingestion_log = await orchestrator.run_etl_pipeline(
                client_id=client_id,
                client_name=client_name,
                raw_records=raw_records,
                source='facebook',
                run_date=date.today(),
                file_name=file_name,
                admin_emails=admin_emails,
                ingestion_log_id=ingestion_log.id
            )
            
            # Update status based on ETL result
            if ingestion_log.status == 'success':
                uploaded_file.upload_status = 'processed'
                # print("\n" + "="*80)
                # print("✓ FACEBOOK ETL PIPELINE COMPLETED SUCCESSFULLY")
                # print("="*80)
            elif ingestion_log.status == 'partial':
                uploaded_file.upload_status = 'processed'
                uploaded_file.error_message = f"Partial success: {ingestion_log.message}"
                # print("\n" + "="*80)
                # print("⚠ FACEBOOK ETL PIPELINE COMPLETED WITH WARNINGS")
                # print(f"Message: {ingestion_log.message}")
                # print("="*80)
            else:
                uploaded_file.upload_status = 'failed'
                uploaded_file.error_message = f"ETL failed: {ingestion_log.message}"
                # print("\n" + "="*80)
                # print("✗ FACEBOOK ETL PIPELINE FAILED")
                # print(f"Error: {ingestion_log.message}")
                # print("="*80)
                
        except Exception as e:
            uploaded_file.upload_status = 'failed'
            uploaded_file.error_message = f"Processing failed: {str(e)}"
            
            # Update ingestion log if parsing fails
            if ingestion_log:
                ingestion_log.status = 'failed'
                ingestion_log.message = f"Parsing failed: {str(e)}"
                ingestion_log.finished_at = datetime.utcnow()
                db.commit()
                
            logger.error(f"Background processing error: {str(e)}", exc_info=True)
            
        uploaded_file.processed_at = datetime.utcnow()
        db.commit()
        
    except Exception as e:
        logger.error(f"Fatal background task error: {str(e)}", exc_info=True)
        # Try to fail log if needed
        if ingestion_log:
            try:
                ingestion_log.status = 'failed'
                ingestion_log.message = f"Fatal error: {str(e)}"
                db.commit()
            except:
                pass
    finally:
        db.close()


class FacebookUploadHandler:
    """Handler for Facebook file uploads and processing."""
    
    def __init__(self, db: Session):
        self.db = db
    
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
        Process uploaded Facebook file (Async).
        
        Args:
            file: Uploaded file
            client_id: Client ID
            client_name: Client name
            user_id: User who uploaded the file
            admin_emails: List of admin emails for alerts
            
        Returns:
            UploadedFile record (status=processing)
        """
        # print("\n" + "="*80)
        # print(f"FACEBOOK UPLOAD STARTED (ASYNC)")
        # print("="*80)
        # print(f"Client: {client_name}")
        # print(f"File: {file.filename}")
        # print("="*80 + "\n")
        
        logger.info(f"Initiating Facebook upload for client {client_name}: {file.filename}")
        
        # Validate file
        # print(f"[{datetime.utcnow()}] [STEP 1] VALIDATING FILE...")
        await FacebookValidator.validate_upload(file)
        # print(f"[{datetime.utcnow()}] ✓ File validation passed\n")
        
        # Get upload directory
        upload_dir = self._get_upload_directory(client_id)
        
        # Save file (Non-blocking)
        # print(f"[{datetime.utcnow()}] [STEP 2] SAVING FILE TO DISK...")
        import asyncio
        loop = asyncio.get_event_loop()
        file_path, file_size = await loop.run_in_executor(
            None, 
            self._save_uploaded_file, 
            file, 
            upload_dir
        )
        # print(f"[{datetime.utcnow()}] ✓ File saved: {file_path}")
        # print(f"  Size: {file_size:,} bytes\n")
        
        # Create upload record with 'processing' status
        uploaded_file = UploadedFile(
            client_id=client_id,
            source='facebook',
            file_name=file.filename,
            file_path=file_path,
            file_size=file_size,
            upload_status='processing',
            uploaded_by=user_id,
            records_count=0  # Will be updated in background
        )
        
        self.db.add(uploaded_file)
        self.db.commit()
        self.db.refresh(uploaded_file)
        
        logger.info(f"Created upload record: {uploaded_file.id}")

        # Create Ingestion Log immediately
        from app.metrics.models import IngestionLog
        ingestion_log = IngestionLog(
            run_date=date.today(),
            status='processing',
            started_at=datetime.utcnow(),
            file_name=file.filename,
            source='facebook',
            client_id=client_id
        )
        self.db.add(ingestion_log)
        self.db.commit()
        self.db.refresh(ingestion_log)
        logger.info(f"Created ingestion log: {ingestion_log.id}")
        
        # NOTE: Background task is now handled by the 'upload_monitor' job which polls for 'processing' logs.
        # This decouples the upload request from the heavy ETL process completely.
        
        # print(f"[{datetime.utcnow()}] [STEP 3] LOG CREATED - HANDOFF TO MONITOR")
        # print("Returning immediate response to client.\n")
        
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

