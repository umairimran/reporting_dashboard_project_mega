"""
Vibe ETL pipeline.
"""
from sqlalchemy.orm import Session
from typing import Optional, List
import uuid
from datetime import date
from app.vibe.service import VibeService
from app.vibe.parser import VibeParser
from app.vibe.models import VibeReportRequest
from app.etl.orchestrator import ETLOrchestrator
from app.core.logging import logger
from app.core.exceptions import VibeAPIError


class VibeETL:
    """ETL pipeline for Vibe API data."""
    
    def __init__(self, db: Session):
        self.db = db
        self.orchestrator = ETLOrchestrator(db)
    
    async def run_for_client(
        self,
        client_id: uuid.UUID,
        client_name: str,
        start_date: date,
        end_date: date,
        admin_emails: Optional[List[str]] = None
    ):
        """Run Vibe ETL for a specific client."""
        logger.info(f"Starting Vibe ETL for {client_name} ({start_date} to {end_date})")
        
        # Get API client
        api_client = VibeService.get_api_client(self.db, client_id)
        
        try:
            # Create report
            logger.info(f"Creating Vibe report for {client_name}")
            report_info = await api_client.create_report(start_date, end_date)
            report_id = report_info['report_id']
            
            # Track report request
            report_request = VibeReportRequest(
                client_id=client_id,
                report_id=report_id,
                status='created',
                start_date=start_date,
                end_date=end_date
            )
            self.db.add(report_request)
            self.db.commit()
            
            # Wait for report to be ready
            logger.info(f"Waiting for Vibe report {report_id} to be ready")
            download_url = await api_client.wait_for_report(report_id)
            
            report_request.download_url = download_url
            report_request.status = 'done'
            self.db.commit()
            
            # Download CSV
            logger.info(f"Downloading Vibe report {report_id}")
            csv_content = await api_client.download_report(download_url)
            
            # Parse CSV
            logger.info(f"Parsing Vibe CSV data")
            raw_records = VibeParser.parse_csv(csv_content)
            
            logger.info(f"Parsed {len(raw_records)} records from Vibe")
            
            # Run ETL pipeline
            ingestion_log = await self.orchestrator.run_etl_pipeline(
                client_id=client_id,
                client_name=client_name,
                raw_records=raw_records,
                source='vibe',
                run_date=end_date,
                admin_emails=admin_emails
            )
            
            logger.info(f"Vibe ETL completed: {ingestion_log.status}")
            return ingestion_log
            
        except Exception as e:
            logger.error(f"Vibe ETL failed for {client_name}: {str(e)}")
            
            # Update report request status if it exists
            if 'report_request' in locals():
                report_request.status = 'failed'
                self.db.commit()
            
            raise VibeAPIError(f"Vibe ETL failed: {str(e)}")
        
        finally:
            await api_client.close()
