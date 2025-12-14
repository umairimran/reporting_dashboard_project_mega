"""
ETL orchestrator to coordinate all data sources.
"""
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
import uuid
from datetime import datetime, date
from app.metrics.models import IngestionLog
from app.etl.staging import StagingService
from app.etl.transformer import TransformerService
from app.etl.loader import LoaderService
from app.core.logging import logger
from app.core.email import email_service


class ETLOrchestrator:
    """Orchestrates ETL operations for all data sources."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def run_etl_pipeline(
        self,
        client_id: uuid.UUID,
        client_name: str,
        raw_records: List[Dict],
        source: str,
        run_date: date,
        file_name: Optional[str] = None,
        admin_emails: Optional[List[str]] = None
    ) -> IngestionLog:
        """
        Run complete ETL pipeline for a data source.
        
        Args:
            client_id: Client UUID
            client_name: Client name (for logging/alerts)
            raw_records: List of raw data records
            source: Data source ('surfside', 'vibe', 'facebook')
            run_date: Date of the data
            file_name: Optional source file name
            admin_emails: Optional list of admin emails for alerts
            
        Returns:
            IngestionLog record
        """
        started_at = datetime.utcnow()
        ingestion_run_id = StagingService.create_ingestion_run_id()
        
        # Create ingestion log
        ingestion_log = IngestionLog(
            run_date=run_date,
            status='processing',
            started_at=started_at,
            file_name=file_name,
            source=source,
            client_id=client_id
        )
        self.db.add(ingestion_log)
        self.db.commit()
        
        try:
            logger.info(f"Starting ETL for {source} - {client_name} - {run_date}")
            
            # Step 1: Validate and transform records
            valid_records, invalid_records = TransformerService.validate_and_transform(
                raw_records, source
            )
            
            if invalid_records:
                error_messages = [f"Record {r['record_index']}: {r['error']}" for r in invalid_records[:5]]
                logger.warning(f"Found {len(invalid_records)} invalid records")
                
                # Send validation error alert
                if admin_emails:
                    await email_service.send_validation_error_alert(
                        client_name=client_name,
                        source=source,
                        run_date=run_date,
                        errors=error_messages,
                        admin_emails=admin_emails
                    )
            
            if not valid_records:
                raise Exception("No valid records to process")
            
            # Step 2: Stage records
            staged_count = StagingService.insert_staging_records(
                db=self.db,
                ingestion_run_id=ingestion_run_id,
                records=valid_records,
                client_id=client_id,
                source=source
            )
            logger.info(f"Staged {staged_count} records")
            
            # Step 3: Load into final tables
            loaded, failed = LoaderService.load_daily_metrics(
                db=self.db,
                client_id=client_id,
                records=valid_records,
                source=source
            )
            
            # Update ingestion log
            ingestion_log.records_loaded = loaded
            ingestion_log.records_failed = failed + len(invalid_records)
            ingestion_log.finished_at = datetime.utcnow()
            
            if failed == 0 and len(invalid_records) == 0:
                ingestion_log.status = 'success'
                ingestion_log.message = f"Successfully processed {loaded} records"
            elif loaded > 0:
                ingestion_log.status = 'partial'
                ingestion_log.message = f"Processed {loaded} records, {failed + len(invalid_records)} failed"
            else:
                ingestion_log.status = 'failed'
                ingestion_log.message = "All records failed to process"
            
            self.db.commit()
            
            logger.info(f"ETL completed: {ingestion_log.status} - {ingestion_log.message}")
            
            # Send failure alert if needed
            if ingestion_log.status == 'failed' and admin_emails:
                await email_service.send_ingestion_failure_alert(
                    client_name=client_name,
                    source=source,
                    run_date=run_date,
                    error_message=ingestion_log.message,
                    admin_emails=admin_emails
                )
            
            return ingestion_log
            
        except Exception as e:
            logger.error(f"ETL pipeline failed: {str(e)}")
            
            # Update ingestion log
            ingestion_log.status = 'failed'
            ingestion_log.message = str(e)
            ingestion_log.finished_at = datetime.utcnow()
            ingestion_log.records_failed = len(raw_records)
            self.db.commit()
            
            # Send failure alert
            if admin_emails:
                await email_service.send_ingestion_failure_alert(
                    client_name=client_name,
                    source=source,
                    run_date=run_date,
                    error_message=str(e),
                    admin_emails=admin_emails
                )
            
            raise
