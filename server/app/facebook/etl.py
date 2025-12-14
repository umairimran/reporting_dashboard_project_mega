"""
Facebook ETL pipeline for uploaded files.
"""
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
import uuid
from datetime import date
from app.facebook.parser import FacebookParser
from app.etl.orchestrator import ETLOrchestrator
from app.core.logging import logger


class FacebookETL:
    """ETL pipeline for Facebook uploaded data."""
    
    def __init__(self, db: Session):
        self.db = db
        self.orchestrator = ETLOrchestrator(db)
    
    async def process_file(
        self,
        file_path: str,
        client_id: uuid.UUID,
        client_name: str,
        run_date: date,
        file_name: Optional[str] = None,
        admin_emails: Optional[List[str]] = None
    ):
        """
        Process uploaded Facebook file through ETL pipeline.
        
        Args:
            file_path: Path to the uploaded file
            client_id: Client ID
            client_name: Client name
            run_date: Date of the ETL run
            file_name: Original filename
            admin_emails: List of admin emails for alerts
            
        Returns:
            IngestionLog record
        """
        logger.info(f"Starting Facebook ETL for {client_name}")
        
        try:
            # Parse file
            logger.info(f"Parsing Facebook file: {file_path}")
            raw_records = FacebookParser.parse_file(file_path)
            
            logger.info(f"Parsed {len(raw_records)} records from Facebook")
            
            # Run ETL pipeline
            ingestion_log = await self.orchestrator.run_etl_pipeline(
                client_id=client_id,
                client_name=client_name,
                raw_records=raw_records,
                source='facebook',
                run_date=run_date,
                file_name=file_name,
                admin_emails=admin_emails
            )
            
            logger.info(f"Facebook ETL completed: {ingestion_log.status}")
            return ingestion_log
            
        except Exception as e:
            logger.error(f"Facebook ETL failed: {str(e)}", exc_info=True)
            raise
