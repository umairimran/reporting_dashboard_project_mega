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
        
        # Find top campaigns by conversions and revenue
        top_campaigns_by_conversions = db.query(
            Campaign.name,
            func.sum(DailyMetrics.conversions).label('conversions'),
            func.sum(DailyMetrics.conversion_revenue).label('revenue'),
            func.sum(DailyMetrics.spend).label('spend')
        ).join(Campaign, DailyMetrics.campaign_id == Campaign.id
        ).filter(
            DailyMetrics.client_id == client_id,
            DailyMetrics.date >= week_start,
            DailyMetrics.date <= week_end
        ).group_by(Campaign.name
        ).order_by(func.sum(DailyMetrics.conversions).desc()
        ).limit(5).all()
        
        top_campaigns_by_revenue = db.query(
            Campaign.name,
            func.sum(DailyMetrics.conversions).label('conversions'),
            func.sum(DailyMetrics.conversion_revenue).label('revenue'),
            func.sum(DailyMetrics.spend).label('spend')
        ).join(Campaign, DailyMetrics.campaign_id == Campaign.id
        ).filter(
            DailyMetrics.client_id == client_id,
            DailyMetrics.date >= week_start,
            DailyMetrics.date <= week_end
        ).group_by(Campaign.name
        ).order_by(func.sum(DailyMetrics.conversion_revenue).desc()
        ).limit(5).all()
        
        # Find top creatives by conversions and revenue
        top_creatives_by_conversions = db.query(
            Creative.name,
            func.sum(DailyMetrics.conversions).label('conversions'),
            func.sum(DailyMetrics.conversion_revenue).label('revenue'),
            func.sum(DailyMetrics.spend).label('spend')
        ).join(Creative, DailyMetrics.creative_id == Creative.id
        ).filter(
            DailyMetrics.client_id == client_id,
            DailyMetrics.date >= week_start,
            DailyMetrics.date <= week_end
        ).group_by(Creative.name
        ).order_by(func.sum(DailyMetrics.conversions).desc()
        ).limit(5).all()
        
        top_creatives_by_revenue = db.query(
            Creative.name,
            func.sum(DailyMetrics.conversions).label('conversions'),
            func.sum(DailyMetrics.conversion_revenue).label('revenue'),
            func.sum(DailyMetrics.spend).label('spend')
        ).join(Creative, DailyMetrics.creative_id == Creative.id
        ).filter(
            DailyMetrics.client_id == client_id,
            DailyMetrics.date >= week_start,
            DailyMetrics.date <= week_end
        ).group_by(Creative.name
        ).order_by(func.sum(DailyMetrics.conversion_revenue).desc()
        ).limit(5).all()
        
        # Structure top performers as JSONB
        top_campaigns_data = {
            'by_conversions': [
                {
                    'name': row.name,
                    'conversions': int(row.conversions),
                    'revenue': float(row.revenue),
                    'spend': float(row.spend)
                }
                for row in top_campaigns_by_conversions
            ],
            'by_revenue': [
                {
                    'name': row.name,
                    'conversions': int(row.conversions),
                    'revenue': float(row.revenue),
                    'spend': float(row.spend)
                }
                for row in top_campaigns_by_revenue
            ]
        }
        
        top_creatives_data = {
            'by_conversions': [
                {
                    'name': row.name,
                    'conversions': int(row.conversions),
                    'revenue': float(row.revenue),
                    'spend': float(row.spend)
                }
                for row in top_creatives_by_conversions
            ],
            'by_revenue': [
                {
                    'name': row.name,
                    'conversions': int(row.conversions),
                    'revenue': float(row.revenue),
                    'spend': float(row.spend)
                }
                for row in top_creatives_by_revenue
            ]
        }
        
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
        summary.top_campaigns = top_campaigns_data
        summary.top_creatives = top_creatives_data
        
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
        
        # Find top campaigns by conversions and revenue
        top_campaigns_by_conversions = db.query(
            Campaign.name,
            func.sum(DailyMetrics.conversions).label('conversions'),
            func.sum(DailyMetrics.conversion_revenue).label('revenue'),
            func.sum(DailyMetrics.spend).label('spend')
        ).join(Campaign, DailyMetrics.campaign_id == Campaign.id
        ).filter(
            DailyMetrics.client_id == client_id,
            DailyMetrics.date >= month_start,
            DailyMetrics.date <= month_end
        ).group_by(Campaign.name
        ).order_by(func.sum(DailyMetrics.conversions).desc()
        ).limit(5).all()
        
        top_campaigns_by_revenue = db.query(
            Campaign.name,
            func.sum(DailyMetrics.conversions).label('conversions'),
            func.sum(DailyMetrics.conversion_revenue).label('revenue'),
            func.sum(DailyMetrics.spend).label('spend')
        ).join(Campaign, DailyMetrics.campaign_id == Campaign.id
        ).filter(
            DailyMetrics.client_id == client_id,
            DailyMetrics.date >= month_start,
            DailyMetrics.date <= month_end
        ).group_by(Campaign.name
        ).order_by(func.sum(DailyMetrics.conversion_revenue).desc()
        ).limit(5).all()
        
        # Find top creatives by conversions and revenue
        top_creatives_by_conversions = db.query(
            Creative.name,
            func.sum(DailyMetrics.conversions).label('conversions'),
            func.sum(DailyMetrics.conversion_revenue).label('revenue'),
            func.sum(DailyMetrics.spend).label('spend')
        ).join(Creative, DailyMetrics.creative_id == Creative.id
        ).filter(
            DailyMetrics.client_id == client_id,
            DailyMetrics.date >= month_start,
            DailyMetrics.date <= month_end
        ).group_by(Creative.name
        ).order_by(func.sum(DailyMetrics.conversions).desc()
        ).limit(5).all()
        
        top_creatives_by_revenue = db.query(
            Creative.name,
            func.sum(DailyMetrics.conversions).label('conversions'),
            func.sum(DailyMetrics.conversion_revenue).label('revenue'),
            func.sum(DailyMetrics.spend).label('spend')
        ).join(Creative, DailyMetrics.creative_id == Creative.id
        ).filter(
            DailyMetrics.client_id == client_id,
            DailyMetrics.date >= month_start,
            DailyMetrics.date <= month_end
        ).group_by(Creative.name
        ).order_by(func.sum(DailyMetrics.conversion_revenue).desc()
        ).limit(5).all()
        
        # Structure top performers as JSONB
        top_campaigns_data = {
            'by_conversions': [
                {
                    'name': row.name,
                    'conversions': int(row.conversions),
                    'revenue': float(row.revenue),
                    'spend': float(row.spend)
                }
                for row in top_campaigns_by_conversions
            ],
            'by_revenue': [
                {
                    'name': row.name,
                    'conversions': int(row.conversions),
                    'revenue': float(row.revenue),
                    'spend': float(row.spend)
                }
                for row in top_campaigns_by_revenue
            ]
        }
        
        top_creatives_data = {
            'by_conversions': [
                {
                    'name': row.name,
                    'conversions': int(row.conversions),
                    'revenue': float(row.revenue),
                    'spend': float(row.spend)
                }
                for row in top_creatives_by_conversions
            ],
            'by_revenue': [
                {
                    'name': row.name,
                    'conversions': int(row.conversions),
                    'revenue': float(row.revenue),
                    'spend': float(row.spend)
                }
                for row in top_creatives_by_revenue
            ]
        }
        
        # Create or update summary
        summary = db.query(MonthlySummary).filter(
            MonthlySummary.client_id == client_id,
            MonthlySummary.month_start == month_start
        ).first()
        
        if not summary:
            summary = MonthlySummary(
                client_id=client_id,
                month_start=month_start,
                month_end=month_end
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
        summary.top_campaigns = top_campaigns_data
        summary.top_creatives = top_creatives_data
        
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
