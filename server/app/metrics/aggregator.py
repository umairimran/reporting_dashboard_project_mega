"""
Weekly and monthly aggregation service.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import date, timedelta
import uuid
from typing import Optional, List
from decimal import Decimal
from app.metrics.models import DailyMetrics, WeeklySummary, MonthlySummary
from app.campaigns.models import Campaign, Strategy, Placement, Creative
from app.metrics.calculator import MetricsCalculator
from app.core.logging import logger


class AggregatorService:
    """Service for aggregating metrics into weekly and monthly summaries."""
    
    @staticmethod
    def get_week_start(target_date: date) -> date:
        """Get the Monday of the week containing the target date."""
        days_since_monday = target_date.weekday()
        return target_date - timedelta(days=days_since_monday)
    
    @staticmethod
    def aggregate_week(db: Session, client_id: uuid.UUID, week_start: date) -> Optional[WeeklySummary]:
        """
        Aggregate daily metrics into weekly summary.
        
        Args:
            db: Database session
            client_id: Client ID
            week_start: Monday of the week to aggregate
            
        Returns:
            WeeklySummary record or None if no data
        """
        week_end = week_start + timedelta(days=6)
        
        logger.info(f"Aggregating week {week_start} to {week_end} for client {client_id}")
        
        # Aggregate metrics from daily data
        result = db.query(
            func.sum(DailyMetrics.impressions).label('impressions'),
            func.sum(DailyMetrics.clicks).label('clicks'),
            func.sum(DailyMetrics.conversions).label('conversions'),
            func.sum(DailyMetrics.conversion_revenue).label('revenue'),
            func.sum(DailyMetrics.spend).label('spend')
        ).filter(
            DailyMetrics.client_id == client_id,
            DailyMetrics.date >= week_start,
            DailyMetrics.date <= week_end
        ).first()
        
        # Check if we have data
        if not result or not result.impressions:
            logger.info(f"No data found for week {week_start}")
            return None
        
        # Calculate derived metrics
        ctr = MetricsCalculator.calculate_ctr(result.impressions, result.clicks)
        cpc = MetricsCalculator.calculate_cpc(Decimal(str(result.spend)), result.clicks)
        cpa = MetricsCalculator.calculate_cpa(Decimal(str(result.spend)), result.conversions)
        roas = MetricsCalculator.calculate_roas(Decimal(str(result.revenue)), Decimal(str(result.spend)))
        
        # Create or update summary
        summary = db.query(WeeklySummary).filter(
            WeeklySummary.client_id == client_id,
            WeeklySummary.week_start == week_start
        ).first()
        
        if not summary:
            summary = WeeklySummary(
                client_id=client_id,
                week_start=week_start,
                week_end=week_end
            )
            db.add(summary)
        
        # Update metrics
        summary.impressions = result.impressions
        summary.clicks = result.clicks
        summary.conversions = result.conversions
        summary.revenue = result.revenue
        summary.spend = result.spend
        summary.ctr = ctr
        summary.cpc = cpc
        summary.cpa = cpa
        summary.roas = roas
        
        db.commit()
        db.refresh(summary)
        
        logger.info(f"Weekly summary created/updated: {summary.id}")
        return summary
    
    @staticmethod
    def aggregate_month(db: Session, client_id: uuid.UUID, year: int, month: int) -> Optional[MonthlySummary]:
        """
        Aggregate daily metrics into monthly summary.
        
        Args:
            db: Database session
            client_id: Client ID
            year: Year
            month: Month (1-12)
            
        Returns:
            MonthlySummary record or None if no data
        """
        logger.info(f"Aggregating month {year}-{month:02d} for client {client_id}")
        
        # Get month date range
        month_start = date(year, month, 1)
        if month == 12:
            month_end = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = date(year, month + 1, 1) - timedelta(days=1)
        
        # Aggregate metrics from daily data
        result = db.query(
            func.sum(DailyMetrics.impressions).label('impressions'),
            func.sum(DailyMetrics.clicks).label('clicks'),
            func.sum(DailyMetrics.conversions).label('conversions'),
            func.sum(DailyMetrics.conversion_revenue).label('revenue'),
            func.sum(DailyMetrics.spend).label('spend')
        ).filter(
            DailyMetrics.client_id == client_id,
            DailyMetrics.date >= month_start,
            DailyMetrics.date <= month_end
        ).first()
        
        # Check if we have data
        if not result or not result.impressions:
            logger.info(f"No data found for month {year}-{month:02d}")
            return None
        
        # Calculate derived metrics
        ctr = MetricsCalculator.calculate_ctr(result.impressions, result.clicks)
        cpc = MetricsCalculator.calculate_cpc(Decimal(str(result.spend)), result.clicks)
        cpa = MetricsCalculator.calculate_cpa(Decimal(str(result.spend)), result.conversions)
        roas = MetricsCalculator.calculate_roas(Decimal(str(result.revenue)), Decimal(str(result.spend)))
        
        # Create or update summary
        summary = db.query(MonthlySummary).filter(
            MonthlySummary.client_id == client_id,
            MonthlySummary.year == year,
            MonthlySummary.month == month
        ).first()
        
        if not summary:
            summary = MonthlySummary(
                client_id=client_id,
                year=year,
                month=month
            )
            db.add(summary)
        
        # Update metrics
        summary.impressions = result.impressions
        summary.clicks = result.clicks
        summary.conversions = result.conversions
        summary.revenue = result.revenue
        summary.spend = result.spend
        summary.ctr = ctr
        summary.cpc = cpc
        summary.cpa = cpa
        summary.roas = roas
        
        db.commit()
        db.refresh(summary)
        
        logger.info(f"Monthly summary created/updated: {summary.id}")
        return summary
    
    @staticmethod
    def aggregate_all_clients_week(db: Session, week_start: date) -> List[WeeklySummary]:
        """Aggregate weekly summaries for all active clients."""
        from app.clients.models import Client
        
        clients = db.query(Client).filter(Client.status == 'active').all()
        summaries = []
        
        for client in clients:
            summary = AggregatorService.aggregate_week(db, client.id, week_start)
            if summary:
                summaries.append(summary)
        
        logger.info(f"Aggregated week {week_start} for {len(summaries)} clients")
        return summaries
    
    @staticmethod
    def aggregate_all_clients_month(db: Session, year: int, month: int) -> List[MonthlySummary]:
        """Aggregate monthly summaries for all active clients."""
        from app.clients.models import Client
        
        clients = db.query(Client).filter(Client.status == 'active').all()
        summaries = []
        
        for client in clients:
            summary = AggregatorService.aggregate_month(db, client.id, year, month)
            if summary:
                summaries.append(summary)
        
        logger.info(f"Aggregated month {year}-{month:02d} for {len(summaries)} clients")
        return summaries
