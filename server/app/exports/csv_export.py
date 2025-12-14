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
        
        # Query metrics
        query = db.query(DailyMetrics).filter(
            DailyMetrics.client_id == client_id,
            DailyMetrics.date >= start_date,
            DailyMetrics.date <= end_date
        )
        
        if source:
            query = query.filter(DailyMetrics.source == source)
        
        metrics = query.order_by(DailyMetrics.date.desc()).all()
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Date',
            'Campaign',
            'Strategy',
            'Placement',
            'Creative',
            'Source',
            'Impressions',
            'Clicks',
            'Conversions',
            'Revenue',
            'CTR (%)',
            'Spend',
            'CPC',
            'CPA',
            'ROAS'
        ])
        
        # Write data
        for metric in metrics:
            writer.writerow([
                metric.date.strftime('%Y-%m-%d'),
                metric.campaign_name,
                metric.strategy_name,
                metric.placement_name,
                metric.creative_name,
                metric.source,
                metric.impressions,
                metric.clicks,
                metric.conversions,
                f"{metric.conversion_revenue:.2f}",
                f"{metric.ctr:.2f}",
                f"{metric.spend:.2f}",
                f"{metric.cpc:.2f}" if metric.cpc else "",
                f"{metric.cpa:.2f}" if metric.cpa else "",
                f"{metric.roas:.2f}" if metric.roas else ""
            ])
        
        csv_content = output.getvalue()
        output.close()
        
        logger.info(f"Exported {len(metrics)} records to CSV")
        
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
        
        logger.info(f"Exporting campaign summary for client {client_id}")
        
        # Aggregate by campaign
        results = db.query(
            DailyMetrics.campaign_name,
            func.sum(DailyMetrics.impressions).label('impressions'),
            func.sum(DailyMetrics.clicks).label('clicks'),
            func.sum(DailyMetrics.conversions).label('conversions'),
            func.sum(DailyMetrics.conversion_revenue).label('revenue'),
            func.sum(DailyMetrics.spend).label('spend')
        ).filter(
            DailyMetrics.client_id == client_id,
            DailyMetrics.date >= start_date,
            DailyMetrics.date <= end_date
        ).group_by(
            DailyMetrics.campaign_name
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
                r.campaign_name,
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
