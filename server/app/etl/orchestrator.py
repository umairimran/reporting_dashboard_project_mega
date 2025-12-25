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
from app.metrics.aggregator import AggregatorService
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
        admin_emails: Optional[List[str]] = None,
        ingestion_log_id: Optional[uuid.UUID] = None
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
            ingestion_log_id: Optional ID of existing processing log
            
        Returns:
            IngestionLog record
        """
        started_at = datetime.utcnow()
        ingestion_run_id = StagingService.create_ingestion_run_id()
        
        # Get or create ingestion log
        if ingestion_log_id:
            ingestion_log = self.db.query(IngestionLog).filter(IngestionLog.id == ingestion_log_id).first()
            if not ingestion_log:
                logger.warning(f"Ingestion log {ingestion_log_id} not found, creating new one")
                ingestion_log = None
        else:
            ingestion_log = None
            
        if not ingestion_log:
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
            
            # Step 1.5: Aggregate records with same dimensions (important for Surfside)
            # This prevents duplicate key violations when multiple rows exist for same
            # date/campaign/strategy/placement/creative (e.g., different creative sizes)
            aggregated_records = TransformerService.aggregate_records(valid_records)
            
            # Step 2: Stage records
            staged_count = StagingService.insert_staging_records(
                db=self.db,
                ingestion_run_id=ingestion_run_id,
                records=aggregated_records,
                client_id=client_id,
                source=source
            )
            logger.info(f"Staged {staged_count} records")
            
            # Step 3: Load into final tables
            loaded, failed = LoaderService.load_daily_metrics(
                db=self.db,
                client_id=client_id,
                records=aggregated_records,
                source=source
            )
            
            # Step 4: Trigger immediate aggregation
            if loaded > 0 and aggregated_records:
                try:
                    # Find date range in the loaded records
                    dates = [r['date'] for r in aggregated_records if 'date' in r]
                    if dates:
                        min_date = min(dates)
                        max_date = max(dates)
                        logger.info(f"Triggering immediate aggregation for {min_date} - {max_date}")
                        AggregatorService.aggregate_date_range(self.db, client_id, min_date, max_date)
                except Exception as agg_err:
                    # Don't fail the whole ETL if aggregation fails, just log it
                    logger.error(f"Immediate aggregation failed: {str(agg_err)}")

            
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
