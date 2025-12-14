"""
Surfside ETL pipeline.
"""
from sqlalchemy.orm import Session
from typing import Optional, List
import uuid
from datetime import date
from app.surfside.s3_service import S3Service
from app.surfside.parser import SurfsideParser
from app.etl.orchestrator import ETLOrchestrator
from app.core.logging import logger
from app.core.exceptions import S3Error, ValidationError


class SurfsideETL:
    """ETL pipeline for Surfside S3 data."""
    
    def __init__(self, db: Session):
        self.db = db
        self.s3_service = S3Service()
        self.orchestrator = ETLOrchestrator(db)
    
    async def run_for_client(
        self,
        client_id: uuid.UUID,
        client_name: str,
        target_date: date,
        client_prefix: str = "",
        admin_emails: Optional[List[str]] = None
    ):
        """
        Run Surfside ETL for a specific client and date.
        
        Args:
            client_id: Client UUID
            client_name: Client name
            target_date: Date to process data for
            client_prefix: Optional S3 prefix for client files
            admin_emails: List of admin emails for alerts
            
        Raises:
            S3Error: If S3 operations fail
            ValidationError: If file parsing fails
        """
        logger.info(f"Starting Surfside ETL for {client_name} - {target_date}")
        
        try:
            # Step 1: Download file from S3
            local_file_path = self.s3_service.download_file_for_date(
                target_date=target_date,
                client_prefix=client_prefix,
                download_dir=f"/tmp/surfside/{client_id}"
            )
            
            if not local_file_path:
                raise S3Error(f"No Surfside file found for date {target_date}")
            
            logger.info(f"Downloaded file: {local_file_path}")
            
            # Step 2: Parse file
            raw_records = SurfsideParser.parse_file(local_file_path)
            
            if not raw_records:
                raise ValidationError("No records found in file")
            
            # Step 3: Run ETL pipeline
            ingestion_log = await self.orchestrator.run_etl_pipeline(
                client_id=client_id,
                client_name=client_name,
                raw_records=raw_records,
                source='surfside',
                run_date=target_date,
                file_name=local_file_path.split('/')[-1],
                admin_emails=admin_emails
            )
            
            logger.info(f"Surfside ETL completed: {ingestion_log.status}")
            
            return ingestion_log
            
        except Exception as e:
            logger.error(f"Surfside ETL failed for {client_name}: {str(e)}")
            raise
