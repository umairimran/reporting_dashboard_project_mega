"""
Staging table operations for ETL pipeline.
"""
from sqlalchemy.orm import Session
from typing import List, Dict
import uuid
from datetime import datetime, date
from decimal import Decimal
import json
from app.metrics.models import StagingMediaRaw
from app.core.logging import logger


class StagingService:
    """Service for staging table operations."""
    
    @staticmethod
    def create_ingestion_run_id() -> uuid.UUID:
        """Generate a unique ingestion run ID."""
        return uuid.uuid4()
    
    @staticmethod
    def _serialize_for_json(obj):
        """Convert non-JSON-serializable objects to JSON-serializable format."""
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, uuid.UUID):
            return str(obj)
        elif isinstance(obj, dict):
            return {key: StagingService._serialize_for_json(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [StagingService._serialize_for_json(item) for item in obj]
        else:
            return obj
    
    @staticmethod
    def insert_staging_records(
        db: Session,
        ingestion_run_id: uuid.UUID,
        records: List[Dict],
        client_id: uuid.UUID,
        source: str
    ) -> int:
        """
        Bulk insert records into staging table.
        
        Args:
            db: Database session
            ingestion_run_id: Unique run identifier
            records: List of raw data records
            client_id: Client UUID
            source: Data source ('surfside', 'vibe', 'facebook')
            
        Returns:
            Number of records inserted
        """
        staging_records = []
        
        for record in records:
            # Serialize the raw_data to make it JSON-compatible
            serialized_raw_data = StagingService._serialize_for_json(record)
            
            staging_record = StagingMediaRaw(
                ingestion_run_id=ingestion_run_id,
                client_id=client_id,
                source=source,
                date=record.get('date'),
                campaign_name=record.get('campaign_name'),
                strategy_name=record.get('strategy_name'),
                placement_name=record.get('placement_name'),
                creative_name=record.get('creative_name'),
                impressions=record.get('impressions', 0),
                clicks=record.get('clicks', 0),
                ctr=record.get('ctr', 0),
                conversions=record.get('conversions', 0),
                conversion_revenue=record.get('conversion_revenue', 0),
                raw_data=serialized_raw_data  # Store serialized data as JSON
            )
            staging_records.append(staging_record)
        
        if staging_records:
            db.bulk_save_objects(staging_records)
            db.flush()
            logger.info(f"Inserted {len(staging_records)} records into staging for run {ingestion_run_id}")
        
        return len(staging_records)
    
    @staticmethod
    def get_staging_records(
        db: Session,
        ingestion_run_id: uuid.UUID
    ) -> List[StagingMediaRaw]:
        """
        Get all staging records for a specific ingestion run.
        
        Args:
            db: Database session
            ingestion_run_id: Ingestion run identifier
            
        Returns:
            List of staging records
        """
        return db.query(StagingMediaRaw).filter(
            StagingMediaRaw.ingestion_run_id == ingestion_run_id
        ).all()
    
    @staticmethod
    def clean_old_staging_data(db: Session, days_to_keep: int = 7) -> int:
        """
        Delete staging data older than specified days.
        
        Args:
            db: Database session
            days_to_keep: Number of days to retain staging data
            
        Returns:
            Number of records deleted
        """
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        deleted = db.query(StagingMediaRaw).filter(
            StagingMediaRaw.created_at < cutoff_date
        ).delete()
        
        db.commit()
        logger.info(f"Cleaned {deleted} old staging records")
        
        return deleted
