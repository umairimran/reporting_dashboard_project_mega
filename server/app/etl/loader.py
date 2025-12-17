"""
Data loader service for ETL pipeline.
"""
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Dict
import uuid
from datetime import date
from app.metrics.models import DailyMetrics
from app.campaigns.service import CampaignService
from app.clients.service import ClientService
from app.metrics.calculator import MetricsCalculator
from app.core.logging import logger
from app.core.exceptions import ValidationError


class LoaderService:
    """Service for loading transformed data into final tables."""
    
    @staticmethod
    def load_daily_metrics(
        db: Session,
        client_id: uuid.UUID,
        records: List[Dict],
        source: str
    ) -> tuple[int, int]:
        """
        Load records into daily_metrics table.
        
        Args:
            db: Database session
            client_id: Client UUID
            records: List of transformed records
            source: Data source ('surfside', 'vibe', 'facebook')
            
        Returns:
            Tuple of (records_loaded, records_failed)
        """
        print(f"[STEP 4.3] CALCULATING METRICS & LOADING DATA...")
        print(f"Total records to load: {len(records)}\n")
        
        loaded = 0
        failed = 0
        
        for idx, record in enumerate(records):
            try:
                # Get CPM for this client and source (uses today's date for current CPM settings)
                cpm_settings = ClientService.get_current_cpm(db, client_id, source)
                
                if not cpm_settings:
                    cpm = Decimal('17.00')  # Default from documentation
                    logger.warning(f"Using default CPM $17 for client {client_id} source {source}")
                else:
                    cpm = cpm_settings.cpm
                
                # Create campaign hierarchy
                campaign, strategy, placement, creative = CampaignService.create_full_hierarchy(
                    db=db,
                    client_id=client_id,
                    campaign_name=record['campaign_name'],
                    strategy_name=record['strategy_name'],
                    placement_name=record['placement_name'],
                    creative_name=record['creative_name'],
                    source=source
                )
                
                # Calculate metrics
                metrics = MetricsCalculator.calculate_all_metrics(
                    impressions=record['impressions'],
                    clicks=record['clicks'],
                    conversions=record['conversions'],
                    revenue=record['conversion_revenue'],
                    cpm=cpm
                )
                
                # Print detailed metrics for first few records
                if idx < 3 or (idx + 1) % 10 == 0:
                    print(f"  Record {idx + 1}: Metrics calculated")
                    print(f"    Date: {record['date']}")
                    print(f"    Campaign: {record['campaign_name'][:40]}..." if len(record['campaign_name']) > 40 else f"    Campaign: {record['campaign_name']}")
                    print(f"    Input Data:")
                    print(f"      Impressions: {record['impressions']:,}")
                    print(f"      Clicks: {record['clicks']:,}")
                    print(f"      Conversions: {record['conversions']:,}")
                    print(f"      Revenue: ${record['conversion_revenue']:,.2f}")
                    print(f"    CPM Rate: ${cpm}")
                    print(f"    Calculated Metrics:")
                    print(f"      Spend: ${metrics['spend']:,.2f} (Formula: Impressions {record['impressions']:,} ÷ 1000 × CPM ${cpm})")
                    print(f"      CTR: {metrics['ctr']:.6f}")
                    print(f"      CPC: ${metrics['cpc']:.4f}")
                    print(f"      CPA: ${metrics['cpa']:.4f}" if record['conversions'] > 0 else f"      CPA: $0.0000 (no conversions)")
                    print(f"      ROAS: {metrics['roas']:.4f}" if metrics['spend'] > 0 else f"      ROAS: 0.0000 (no spend)")
                    print()
                
                # Check if record already exists (duplicate detection)
                existing = db.query(DailyMetrics).filter(
                    DailyMetrics.client_id == client_id,
                    DailyMetrics.date == record['date'],
                    DailyMetrics.campaign_id == campaign.id,
                    DailyMetrics.strategy_id == strategy.id,
                    DailyMetrics.placement_id == placement.id,
                    DailyMetrics.creative_id == creative.id,
                    DailyMetrics.source == source
                ).first()
                
                if existing:
                    # Update existing record
                    existing.impressions = record['impressions']
                    existing.clicks = record['clicks']
                    existing.conversions = record['conversions']
                    existing.conversion_revenue = record['conversion_revenue']
                    existing.ctr = metrics['ctr']
                    existing.spend = metrics['spend']
                    existing.cpc = metrics['cpc']
                    existing.cpa = metrics['cpa']
                    existing.roas = metrics['roas']
                    logger.debug(f"Updated existing metric for {record['date']}")
                    if idx < 3:
                        print(f"    → Updated existing record in database\n")
                else:
                    # Create new record
                    daily_metric = DailyMetrics(
                        client_id=client_id,
                        date=record['date'],
                        campaign_id=campaign.id,
                        strategy_id=strategy.id,
                        placement_id=placement.id,
                        creative_id=creative.id,
                        source=source,
                        impressions=record['impressions'],
                        clicks=record['clicks'],
                        conversions=record['conversions'],
                        conversion_revenue=record['conversion_revenue'],
                        ctr=metrics['ctr'],
                        spend=metrics['spend'],
                        cpc=metrics['cpc'],
                        cpa=metrics['cpa'],
                        roas=metrics['roas']
                    )
                    db.add(daily_metric)
                    logger.debug(f"Created new metric for {record['date']}")
                    if idx < 3:
                        print(f"    → Inserted new record into database\n")
                
                loaded += 1
                
            except Exception as e:
                logger.error(f"Error loading record: {str(e)}")
                failed += 1
                db.rollback()
        
        # Commit all changes
        try:
            db.commit()
            print(f"\n✓ Data loading complete")
            print(f"  Records loaded: {loaded}")
            print(f"  Records failed: {failed}\n")
            logger.info(f"Loaded {loaded} records, {failed} failed")
        except Exception as e:
            print(f"\n✗ Error committing to database: {str(e)}\n")
            logger.error(f"Error committing records: {str(e)}")
            db.rollback()
            raise
        
        return loaded, failed
    
    @staticmethod
    def check_duplicates(
        db: Session,
        client_id: uuid.UUID,
        record_date: date,
        source: str
    ) -> int:
        """
        Check for existing records for a specific date and source.
        
        Args:
            db: Database session
            client_id: Client UUID
            record_date: Date to check
            source: Data source
            
        Returns:
            Count of existing records
        """
        count = db.query(DailyMetrics).filter(
            DailyMetrics.client_id == client_id,
            DailyMetrics.date == record_date,
            DailyMetrics.source == source
        ).count()
        
        return count
