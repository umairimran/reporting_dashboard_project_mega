"""
CSV export service for metrics data.
"""
import csv
import io
from sqlalchemy.orm import Session
from datetime import date
import uuid
from typing import List, Optional
from app.metrics.models import DailyMetrics
from app.core.logging import logger


class CSVExportService:
    """Service for exporting data to CSV format."""
    
    @staticmethod
    def _get_source_display_name(source_name: str) -> str:
        """Map source name to display name (surfside -> CTV)."""
        if source_name and source_name.lower() == "surfside":
            return "CTV"
        return source_name.upper() if source_name else "All Sources"
    
    @staticmethod
    def export_daily_metrics(
        db: Session,
        client_id: uuid.UUID,
        start_date: date,
        end_date: date,
        source: Optional[str] = None
    ) -> str:
        """
        Export daily metrics to CSV.
        
        Returns:
            CSV content as string
        """
        logger.info(f"Exporting daily metrics for client {client_id}")
        
        from app.campaigns.models import Campaign, Strategy, Placement, Creative, Region
        
        # Query metrics with LEFT OUTER joins to get names (handle nullable foreign keys)
        query = db.query(
            DailyMetrics,
            Campaign.name.label('campaign_name'),
            Strategy.name.label('strategy_name'),
            Placement.name.label('placement_name'),
            Creative.name.label('creative_name'),
            Region.name.label('region_name')
        ).outerjoin(Campaign, DailyMetrics.campaign_id == Campaign.id
        ).outerjoin(Strategy, DailyMetrics.strategy_id == Strategy.id
        ).outerjoin(Placement, DailyMetrics.placement_id == Placement.id
        ).outerjoin(Creative, DailyMetrics.creative_id == Creative.id
        ).outerjoin(Region, DailyMetrics.region_id == Region.id
        ).filter(
            DailyMetrics.client_id == client_id,
            DailyMetrics.date >= start_date,
            DailyMetrics.date <= end_date
        )
        
        if source:
            query = query.filter(DailyMetrics.source == source)
        
        results = query.order_by(DailyMetrics.date.desc()).all()
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Define Columns with visibility rules
        # Format: (Header, Extractor Function, Excluded Sources List)
        columns_config = [
            ("Date", lambda m, c, s, p, cr, r: m.date.strftime('%Y-%m-%d'), []),
            ("Campaign", lambda m, c, s, p, cr, r: c or "", ["surfside"]),
            ("Strategy", lambda m, c, s, p, cr, r: s or "", ["facebook"]),
            ("Placement", lambda m, c, s, p, cr, r: p or "", ["facebook"]),
            ("Creative", lambda m, c, s, p, cr, r: cr or "", ["surfside"]),
            ("Region", lambda m, c, s, p, cr, r: r or "", ["surfside"]),
            ("Source", lambda m, c, s, p, cr, r: CSVExportService._get_source_display_name(m.source), []),
            ("Impressions", lambda m, c, s, p, cr, r: m.impressions, []),
            ("Clicks", lambda m, c, s, p, cr, r: m.clicks, []),
            ("Conversions", lambda m, c, s, p, cr, r: m.conversions, ["facebook"]),
            ("Revenue", lambda m, c, s, p, cr, r: m.conversion_revenue, ["facebook"]),
            ("CTR (%)", lambda m, c, s, p, cr, r: m.ctr, []),
            ("Spend", lambda m, c, s, p, cr, r: m.spend, []),
            ("CPC", lambda m, c, s, p, cr, r: m.cpc if m.cpc is not None else 0, []),
            ("CPA", lambda m, c, s, p, cr, r: m.cpa if m.cpa is not None else 0, ["surfside"]),
            ("ROAS", lambda m, c, s, p, cr, r: m.roas if m.roas is not None else 0, ["surfside"])
        ]

        # Filter active columns based on source
        active_columns = []
        for header, extractor, excluded_sources in columns_config:
            if source and source in excluded_sources:
                continue
            active_columns.append((header, extractor))
            
        # Write header
        writer.writerow([col[0] for col in active_columns])
        
        # Write data
        for row_data in results:
            metric, campaign_name, strategy_name, placement_name, creative_name, region_name = row_data
            
            row = []
            for _, extractor in active_columns:
                row.append(extractor(metric, campaign_name, strategy_name, placement_name, creative_name, region_name))
            
            writer.writerow(row)
        
        csv_content = output.getvalue()
        output.close()
        
        logger.info(f"Exported {len(results)} records to CSV")
        
        return csv_content
    
    @staticmethod
    def export_campaign_summary(
        db: Session,
        client_id: uuid.UUID,
        start_date: date,
        end_date: date
    ) -> str:
        """
        Export campaign summary to CSV.
        
        Returns:
            CSV content as string
        """
        from sqlalchemy import func
        from app.metrics.calculator import MetricsCalculator
        from decimal import Decimal
        from app.campaigns.models import Campaign
        
        logger.info(f"Exporting campaign summary for client {client_id}")
        
        # Aggregate by campaign with LEFT OUTER JOIN to handle NULL campaigns
        results = db.query(
            Campaign.name.label('campaign_name'),
            func.sum(DailyMetrics.impressions).label('impressions'),
            func.sum(DailyMetrics.clicks).label('clicks'),
            func.sum(DailyMetrics.conversions).label('conversions'),
            func.sum(DailyMetrics.conversion_revenue).label('revenue'),
            func.sum(DailyMetrics.spend).label('spend')
        ).outerjoin(
            Campaign, DailyMetrics.campaign_id == Campaign.id
        ).filter(
            DailyMetrics.client_id == client_id,
            DailyMetrics.date >= start_date,
            DailyMetrics.date <= end_date
        ).group_by(
            Campaign.name
        ).order_by(
            func.sum(DailyMetrics.impressions).desc()
        ).all()
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Campaign',
            'Impressions',
            'Clicks',
            'Conversions',
            'Revenue',
            'Spend',
            'CTR (%)',
            'CPC',
            'CPA',
            'ROAS'
        ])
        
        # Write data
        for r in results:
            ctr = MetricsCalculator.calculate_ctr(r.impressions, r.clicks)
            cpc = MetricsCalculator.calculate_cpc(Decimal(str(r.spend)), r.clicks)
            cpa = MetricsCalculator.calculate_cpa(Decimal(str(r.spend)), r.conversions)
            roas = MetricsCalculator.calculate_roas(Decimal(str(r.revenue)), Decimal(str(r.spend)))
            
            writer.writerow([
                r.campaign_name or 'No Campaign',  # Handle NULL campaigns
                r.impressions,
                r.clicks,
                r.conversions,
                f"{r.revenue:.2f}",
                f"{r.spend:.2f}",
                f"{ctr:.2f}",
                f"{cpc:.2f}" if cpc else "",
                f"{cpa:.2f}" if cpa else "",
                f"{roas:.2f}" if roas else ""
            ])
        
        csv_content = output.getvalue()
        output.close()
        
        logger.info(f"Exported {len(results)} campaigns to CSV")
        
        return csv_content
