"""
Dashboard service for complex queries and data aggregation.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
import uuid
from datetime import date, timedelta
from typing import List, Optional, Tuple
from decimal import Decimal
from app.metrics.models import DailyMetrics, WeeklySummary, MonthlySummary
from app.campaigns.models import Campaign
from app.clients.models import Client
from app.metrics.calculator import MetricsCalculator
from app.dashboard.schemas import (
    DashboardSummary,
    CampaignBreakdown,
    SourceBreakdown,
    DailyTrend,
    WeeklyComparison,
    MonthlyComparison,
    TopPerformer,
    TopPerformersResponse,
    ClientDashboard
)
from app.core.logging import logger


class DashboardService:
    """Service for dashboard data queries."""
    
    @staticmethod
    def _get_aggregated_metrics(
        db: Session,
        client_id: uuid.UUID,
        start_date: date,
        end_date: date,
        source: Optional[str] = None
    ):
        query = db.query(
            func.sum(DailyMetrics.impressions).label('impressions'),
            func.sum(DailyMetrics.clicks).label('clicks'),
            func.sum(DailyMetrics.conversions).label('conversions'),
            func.sum(DailyMetrics.conversion_revenue).label('revenue'),
            func.sum(DailyMetrics.spend).label('spend'),
            func.count(func.distinct(DailyMetrics.campaign_id)).label('active_campaigns'),
            func.array_agg(func.distinct(DailyMetrics.source)).label('sources')
        ).filter(
            DailyMetrics.client_id == client_id,
            DailyMetrics.date >= start_date,
            DailyMetrics.date <= end_date
        )

        if source:
            query = query.filter(DailyMetrics.source == source)

        result = query.first()
        
        if not result or not result.impressions:
            return None
            
        ctr = MetricsCalculator.calculate_ctr(result.impressions, result.clicks)
        cpc = MetricsCalculator.calculate_cpc(result.spend, result.clicks)
        cpa = MetricsCalculator.calculate_cpa(result.spend, result.conversions)
        roas = MetricsCalculator.calculate_roas(result.revenue, result.spend)
        
        return {
            "result": result,
            "metrics": {
                "total_impressions": result.impressions,
                "total_clicks": result.clicks,
                "total_conversions": result.conversions,
                "total_revenue": result.revenue,
                "total_spend": result.spend,
                "overall_ctr": ctr,
                "overall_cpc": cpc,
                "overall_cpa": cpa,
                "overall_roas": roas
            }
        }

    @staticmethod
    def get_dashboard_summary(
        db: Session,
        client_id: uuid.UUID,
        start_date: date,
        end_date: date,
        source: Optional[str] = None
    ) -> DashboardSummary:
        """Get high-level dashboard summary with previous period comparison."""
        
        # 1. Current Period
        current = DashboardService._get_aggregated_metrics(db, client_id, start_date, end_date, source=source)
        
        if not current:
            # Return empty response
            from app.dashboard.schemas import PeriodMetrics
            empty_metrics = {
                "total_impressions": 0,
                "total_clicks": 0,
                "total_conversions": 0,
                "total_revenue": Decimal('0'),
                "total_spend": Decimal('0'),
                "overall_ctr": Decimal('0'),
                "overall_cpc": None,
                "overall_cpa": None,
                "overall_roas": None
            }
            return DashboardSummary(
                **empty_metrics,
                active_campaigns=0,
                data_sources=[],
                previous_period=None
            )

        # 2. Previous Period (Same Duration, immediately preceding)
        duration = (end_date - start_date).days
        prev_end_date = start_date - timedelta(days=1)
        prev_start_date = prev_end_date - timedelta(days=duration)
        
        prev = DashboardService._get_aggregated_metrics(db, client_id, prev_start_date, prev_end_date, source=source)
        
        previous_period_data = None
        if prev:
            from app.dashboard.schemas import PeriodMetrics
            previous_period_data = PeriodMetrics(**prev["metrics"])

        # 3. Construct Response
        return DashboardSummary(
            **current["metrics"],
            active_campaigns=current["result"].active_campaigns or 0,
            data_sources=[s for s in (current["result"].sources or []) if s],
            previous_period=previous_period_data
        )
    
    @staticmethod
    def get_campaign_breakdown(
        db: Session,
        client_id: uuid.UUID,
        start_date: date,
        end_date: date,
        limit: int = 10,
        source: Optional[str] = None
    ) -> List[CampaignBreakdown]:
        """Get performance breakdown by campaign."""
        from app.campaigns.models import Campaign
        
        results = db.query(
            Campaign.name.label('campaign_name'),
            func.sum(DailyMetrics.impressions).label('impressions'),
            func.sum(DailyMetrics.clicks).label('clicks'),
            func.sum(DailyMetrics.conversions).label('conversions'),
            func.sum(DailyMetrics.conversion_revenue).label('revenue'),
            func.sum(DailyMetrics.spend).label('spend')
        ).join(Campaign, DailyMetrics.campaign_id == Campaign.id
        ).filter(
            DailyMetrics.client_id == client_id,
            DailyMetrics.date >= start_date,
            DailyMetrics.date <= end_date
        )

        if source:
            results = results.filter(DailyMetrics.source == source)
            
        results = results.group_by(
            Campaign.name
        ).order_by(
            desc(func.sum(DailyMetrics.impressions))
        ).limit(limit).all()
        
        breakdowns = []
        for r in results:
            ctr = MetricsCalculator.calculate_ctr(r.impressions, r.clicks)
            cpc = MetricsCalculator.calculate_cpc(r.spend, r.clicks)
            cpa = MetricsCalculator.calculate_cpa(r.spend, r.conversions)
            roas = MetricsCalculator.calculate_roas(r.revenue, r.spend)
            
            breakdowns.append(CampaignBreakdown(
                campaign_name=r.campaign_name,
                impressions=r.impressions,
                clicks=r.clicks,
                conversions=r.conversions,
                revenue=r.revenue,
                spend=r.spend,
                ctr=ctr,
                cpc=cpc,
                cpa=cpa,
                roas=roas
            ))
        
        return breakdowns
    
    @staticmethod
    def get_source_breakdown(
        db: Session,
        client_id: uuid.UUID,
        start_date: date,
        end_date: date,
        source: Optional[str] = None
    ) -> List[SourceBreakdown]:
        """Get performance breakdown by data source."""
        
        results = db.query(
            DailyMetrics.source,
            func.sum(DailyMetrics.impressions).label('impressions'),
            func.sum(DailyMetrics.clicks).label('clicks'),
            func.sum(DailyMetrics.conversions).label('conversions'),
            func.sum(DailyMetrics.conversion_revenue).label('revenue'),
            func.sum(DailyMetrics.spend).label('spend')
        ).filter(
            DailyMetrics.client_id == client_id,
            DailyMetrics.date >= start_date,
            DailyMetrics.date <= end_date
        )

        if source:
             # If filtering by source, this query becomes trivial (1 row), but still valid.
             results = results.filter(DailyMetrics.source == source)

        results = results.group_by(
            DailyMetrics.source
        ).all()
        
        breakdowns = []
        for r in results:
            ctr = MetricsCalculator.calculate_ctr(r.impressions, r.clicks)
            
            breakdowns.append(SourceBreakdown(
                source=r.source,
                impressions=r.impressions,
                clicks=r.clicks,
                conversions=r.conversions,
                revenue=r.revenue,
                spend=r.spend,
                ctr=ctr
            ))
        
        return breakdowns
    
    @staticmethod
    def get_daily_trends(
        db: Session,
        client_id: uuid.UUID,
        start_date: date,
        end_date: date,
        source: Optional[str] = None
    ) -> List[DailyTrend]:
        """Get daily trend data."""
        
        results = db.query(
            DailyMetrics.date,
            func.sum(DailyMetrics.impressions).label('impressions'),
            func.sum(DailyMetrics.clicks).label('clicks'),
            func.sum(DailyMetrics.conversions).label('conversions'),
            func.sum(DailyMetrics.conversion_revenue).label('revenue'),
            func.sum(DailyMetrics.spend).label('spend')
        ).filter(
            DailyMetrics.client_id == client_id,
            DailyMetrics.date >= start_date,
            DailyMetrics.date <= end_date
        )
        
        if source:
            results = results.filter(DailyMetrics.source == source)
            
        results = results.group_by(
            DailyMetrics.date
        ).order_by(
            DailyMetrics.date
        ).all()
        
        trends = []
        for r in results:
            ctr = MetricsCalculator.calculate_ctr(r.impressions, r.clicks)
            roas = MetricsCalculator.calculate_roas(r.revenue, r.spend)
            
            trends.append(DailyTrend(
                date=r.date,
                impressions=r.impressions,
                clicks=r.clicks,
                conversions=r.conversions,
                revenue=r.revenue,
                spend=r.spend,
                ctr=ctr,
                roas=roas
            ))
        
        return trends
    
    @staticmethod
    def get_top_performers(
        db: Session,
        client_id: uuid.UUID,
        start_date: date,
        end_date: date,
        limit: int = 5,
        source: Optional[str] = None
    ) -> TopPerformersResponse:
        """Get top performers across different metrics."""
        
        # Top by impressions
        from app.campaigns.models import Campaign
        
        by_impressions_results = db.query(
            Campaign.name.label('campaign_name'),
            func.sum(DailyMetrics.impressions).label('impressions'),
            func.sum(DailyMetrics.conversions).label('conversions'),
            func.sum(DailyMetrics.conversion_revenue).label('revenue')
        ).join(Campaign, DailyMetrics.campaign_id == Campaign.id
        ).filter(
        ).filter(
            DailyMetrics.client_id == client_id,
            DailyMetrics.date >= start_date,
            DailyMetrics.date <= end_date
        )
        
        if source:
            by_impressions_results = by_impressions_results.filter(DailyMetrics.source == source)
            
        by_impressions_results = by_impressions_results.group_by(
            Campaign.name
        ).order_by(
            desc(func.sum(DailyMetrics.impressions))
        ).limit(limit).all()
        
        by_impressions = [
            TopPerformer(
                name=r.campaign_name,
                metric_value=Decimal(str(r.impressions)),
                impressions=r.impressions,
                conversions=r.conversions,
                revenue=r.revenue
            )
            for r in by_impressions_results
        ]
        
        # Top by conversions
        by_conversions_results = db.query(
            Campaign.name.label('campaign_name'),
            func.sum(DailyMetrics.impressions).label('impressions'),
            func.sum(DailyMetrics.conversions).label('conversions'),
            func.sum(DailyMetrics.conversion_revenue).label('revenue')
        ).join(Campaign, DailyMetrics.campaign_id == Campaign.id
        ).filter(
        ).filter(
            DailyMetrics.client_id == client_id,
            DailyMetrics.date >= start_date,
            DailyMetrics.date <= end_date
        )
        
        if source:
           by_conversions_results = by_conversions_results.filter(DailyMetrics.source == source)

        by_conversions_results = by_conversions_results.group_by(
            Campaign.name
        ).order_by(
            desc(func.sum(DailyMetrics.conversions))
        ).limit(limit).all()
        
        by_conversions = [
            TopPerformer(
                name=r.campaign_name,
                metric_value=Decimal(str(r.conversions)),
                impressions=r.impressions,
                conversions=r.conversions,
                revenue=r.revenue
            )
            for r in by_conversions_results
        ]
        
        # Top by revenue
        by_revenue_results = db.query(
            Campaign.name.label('campaign_name'),
            func.sum(DailyMetrics.impressions).label('impressions'),
            func.sum(DailyMetrics.conversions).label('conversions'),
            func.sum(DailyMetrics.conversion_revenue).label('revenue')
        ).join(Campaign, DailyMetrics.campaign_id == Campaign.id
        ).filter(
        ).filter(
            DailyMetrics.client_id == client_id,
            DailyMetrics.date >= start_date,
            DailyMetrics.date <= end_date
        )
        
        if source:
            by_revenue_results = by_revenue_results.filter(DailyMetrics.source == source)

        by_revenue_results = by_revenue_results.group_by(
            Campaign.name
        ).order_by(
            desc(func.sum(DailyMetrics.conversion_revenue))
        ).limit(limit).all()
        
        by_revenue = [
            TopPerformer(
                name=r.campaign_name,
                metric_value=r.revenue,
                impressions=r.impressions,
                conversions=r.conversions,
                revenue=r.revenue
            )
            for r in by_revenue_results
        ]
        
        # Top by ROAS
        by_roas_results = db.query(
            Campaign.name.label('campaign_name'),
            func.sum(DailyMetrics.impressions).label('impressions'),
            func.sum(DailyMetrics.conversions).label('conversions'),
            func.sum(DailyMetrics.conversion_revenue).label('revenue'),
            func.sum(DailyMetrics.spend).label('spend')
        ).join(Campaign, DailyMetrics.campaign_id == Campaign.id
        ).filter(
        ).filter(
            DailyMetrics.client_id == client_id,
            DailyMetrics.date >= start_date,
            DailyMetrics.date <= end_date
        )
        
        if source:
            by_roas_results = by_roas_results.filter(DailyMetrics.source == source)

        by_roas_results = by_roas_results.group_by(
            Campaign.name
        ).having(
            func.sum(DailyMetrics.spend) > 0
        ).all()
        
        # Calculate ROAS and sort
        roas_data = []
        for r in by_roas_results:
            roas = MetricsCalculator.calculate_roas(r.revenue, r.spend)
            if roas:
                roas_data.append((r.campaign_name, roas, r.impressions, r.conversions, r.revenue))
        
        roas_data.sort(key=lambda x: x[1], reverse=True)
        
        by_roas = [
            TopPerformer(
                name=name,
                metric_value=roas_val,
                impressions=imp,
                conversions=conv,
                revenue=rev
            )
            for name, roas_val, imp, conv, rev in roas_data[:limit]
        ]
        
        return TopPerformersResponse(
            by_impressions=by_impressions,
            by_conversions=by_conversions,
            by_revenue=by_revenue,
            by_roas=by_roas
        )
    
    @staticmethod
    def get_client_dashboard(
        db: Session,
        client_id: uuid.UUID,
        start_date: date,
        end_date: date,
        source: Optional[str] = None
    ) -> ClientDashboard:
        """Get complete dashboard for a client."""
        
        client = db.query(Client).filter(Client.id == client_id).first()
        
        if not client:
            raise ValueError(f"Client not found: {client_id}")
        
        return ClientDashboard(
            client_id=client_id,
            client_name=client.name,
            date_range_start=start_date,
            date_range_end=end_date,
            summary=DashboardService.get_dashboard_summary(db, client_id, start_date, end_date, source=source),
            campaigns=DashboardService.get_campaign_breakdown(db, client_id, start_date, end_date, source=source),
            sources=DashboardService.get_source_breakdown(db, client_id, start_date, end_date, source=source),
            daily_trends=DashboardService.get_daily_trends(db, client_id, start_date, end_date, source=source),
            top_performers=DashboardService.get_top_performers(db, client_id, start_date, end_date, source=source)
        )
