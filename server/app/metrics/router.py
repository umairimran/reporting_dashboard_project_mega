"""
Metrics API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
import uuid
from datetime import date, timedelta
from typing import List, Optional
from app.core.database import get_db
from app.auth.dependencies import get_current_user, get_current_client
from app.auth.models import User
from app.metrics.models import DailyMetrics, WeeklySummary, MonthlySummary
from app.metrics.schemas import (
    DailyMetricsResponse,
    WeeklySummaryResponse,
    MonthlySummaryResponse,
    MetricsSummary,
    DateRangeMetrics,
    CampaignPerformance,
    TopPerformers
)
from app.metrics.aggregator import AggregatorService
from app.clients.models import Client
from decimal import Decimal


router = APIRouter(prefix="/metrics", tags=["Metrics"])


@router.get("/daily", response_model=List[DailyMetricsResponse])
async def get_daily_metrics(
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    client_id: Optional[uuid.UUID] = Query(None, description="Filter by client ID"),
    campaign_name: Optional[str] = Query(None, description="Filter by campaign"),
    source: Optional[str] = Query(None, description="Filter by source (surfside/vibe/facebook)"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get daily metrics with optional filters."""
    from app.campaigns.models import Campaign, Strategy, Placement, Creative
    
    query = db.query(
        DailyMetrics,
        Client.name.label('client_name'),
        Campaign.name.label('campaign_name'),
        Strategy.name.label('strategy_name'),
        Placement.name.label('placement_name'),
        Creative.name.label('creative_name')
    ).join(Client, DailyMetrics.client_id == Client.id
    ).outerjoin(Campaign, DailyMetrics.campaign_id == Campaign.id
    ).outerjoin(Strategy, DailyMetrics.strategy_id == Strategy.id
    ).outerjoin(Placement, DailyMetrics.placement_id == Placement.id
    ).outerjoin(Creative, DailyMetrics.creative_id == Creative.id)
    
    # Apply date range filter
    query = query.filter(
        DailyMetrics.date >= start_date,
        DailyMetrics.date <= end_date
    )
    
    # Apply client filter based on user role
    if current_user.role == 'client':
        # Client users should have exactly one client associated
        if not current_user.clients:
            raise HTTPException(status_code=403, detail="No client associated with user")
        query = query.filter(DailyMetrics.client_id == current_user.clients[0].id)
    elif client_id:
        query = query.filter(DailyMetrics.client_id == client_id)
    
    # Apply optional filters
    if campaign_name:
        query = query.filter(Campaign.name.ilike(f"%{campaign_name}%"))
    
    if source:
        query = query.filter(DailyMetrics.source == source)
    
    # Order by date desc
    query = query.order_by(DailyMetrics.date.desc())
    
    # Apply pagination
    results = query.offset(offset).limit(limit).all()
    
    return [
        DailyMetricsResponse(
            id=m.id,
            client_id=m.client_id,
            client_name=c_name,
            campaign_name=camp_name,
            strategy_name=strat_name,
            placement_name=place_name,
            creative_name=creat_name,
            date=m.date,
            impressions=m.impressions,
            clicks=m.clicks,
            conversions=m.conversions,
            conversion_revenue=m.conversion_revenue,
            ctr=m.ctr,
            spend=m.spend,
            cpc=m.cpc,
            cpa=m.cpa,
            roas=m.roas,
            source=m.source
        )
        for m, c_name, camp_name, strat_name, place_name, creat_name in results
    ]


@router.get("/weekly", response_model=List[WeeklySummaryResponse])
async def get_weekly_summaries(
    client_id: Optional[uuid.UUID] = Query(None),
    limit: int = Query(52, ge=1, le=104),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get weekly summaries."""
    query = db.query(WeeklySummary)
    
    # Apply client filter
    if current_user.role == 'client':
        if not current_user.clients:
            raise HTTPException(status_code=403, detail="No client associated with user")
        query = query.filter(WeeklySummary.client_id == current_user.clients[0].id)
    elif client_id:
        query = query.filter(WeeklySummary.client_id == client_id)
    
    summaries = query.order_by(WeeklySummary.week_start.desc()).limit(limit).all()
    
    return [WeeklySummaryResponse.from_orm(s) for s in summaries]


@router.get("/monthly", response_model=List[MonthlySummaryResponse])
async def get_monthly_summaries(
    client_id: Optional[uuid.UUID] = Query(None),
    year: Optional[int] = Query(None),
    limit: int = Query(12, ge=1, le=24),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get monthly summaries."""
    query = db.query(MonthlySummary)
    
    # Apply client filter
    if current_user.role == 'client':
        if not current_user.clients:
            raise HTTPException(status_code=403, detail="No client associated with user")
        query = query.filter(MonthlySummary.client_id == current_user.clients[0].id)
    elif client_id:
        query = query.filter(MonthlySummary.client_id == client_id)
    
    if year:
        query = query.filter(func.extract('year', MonthlySummary.month_start) == year)
    
    summaries = query.order_by(MonthlySummary.month_start.desc()).limit(limit).all()
    
    return [MonthlySummaryResponse.from_orm(s) for s in summaries]


@router.get("/summary", response_model=MetricsSummary)
async def get_metrics_summary(
    start_date: date = Query(...),
    end_date: date = Query(...),
    client_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get aggregated metrics summary for a date range."""
    query = db.query(
        func.sum(DailyMetrics.impressions).label('impressions'),
        func.sum(DailyMetrics.clicks).label('clicks'),
        func.sum(DailyMetrics.conversions).label('conversions'),
        func.sum(DailyMetrics.conversion_revenue).label('revenue'),
        func.sum(DailyMetrics.spend).label('spend')
    ).filter(
        DailyMetrics.date >= start_date,
        DailyMetrics.date <= end_date
    )
    
    # Apply client filter
    if current_user.role == 'client':
        if not current_user.clients:
            raise HTTPException(status_code=403, detail="No client associated with user")
        query = query.filter(DailyMetrics.client_id == current_user.clients[0].id)
    elif client_id:
        query = query.filter(DailyMetrics.client_id == client_id)
    
    result = query.first()
    
    if not result or not result.impressions:
        return MetricsSummary(
            total_impressions=0,
            total_clicks=0,
            total_conversions=0,
            total_revenue=Decimal('0'),
            total_spend=Decimal('0'),
            avg_ctr=Decimal('0'),
            avg_cpc=None,
            avg_cpa=None,
            avg_roas=None
        )
    
    from app.metrics.calculator import MetricsCalculator
    
    return MetricsSummary(
        total_impressions=result.impressions,
        total_clicks=result.clicks,
        total_conversions=result.conversions,
        total_revenue=result.revenue,
        total_spend=result.spend,
        avg_ctr=MetricsCalculator.calculate_ctr(result.impressions, result.clicks),
        avg_cpc=MetricsCalculator.calculate_cpc(result.spend, result.clicks),
        avg_cpa=MetricsCalculator.calculate_cpa(result.spend, result.conversions),
        avg_roas=MetricsCalculator.calculate_roas(result.revenue, result.spend)
    )


@router.post("/aggregate/week")
async def trigger_weekly_aggregation(
    week_start: date = Query(..., description="Monday of the week"),
    client_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Manually trigger weekly aggregation (admin only)."""
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if client_id:
        summary = AggregatorService.aggregate_week(db, client_id, week_start)
        return {"status": "success", "summary_id": summary.id if summary else None}
    else:
        summaries = AggregatorService.aggregate_all_clients_week(db, week_start)
        return {"status": "success", "count": len(summaries)}


@router.post("/aggregate/month")
async def trigger_monthly_aggregation(
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12),
    client_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Manually trigger monthly aggregation (admin only)."""
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if client_id:
        summary = AggregatorService.aggregate_month(db, client_id, year, month)
        return {"status": "success", "summary_id": summary.id if summary else None}
    else:
        summaries = AggregatorService.aggregate_all_clients_month(db, year, month)
        return {"status": "success", "count": len(summaries)}
