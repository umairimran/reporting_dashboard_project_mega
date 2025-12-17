"""
Dashboard API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
import uuid
from datetime import date, timedelta
from typing import Optional, List
from app.core.database import get_db
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.dashboard.service import DashboardService
from app.dashboard.schemas import (
    ClientDashboard,
    DashboardSummary,
    CampaignBreakdown,
    SourceBreakdown,
    DailyTrend,
    TopPerformersResponse,
    SourceTabOverview,
    DimensionSummary,
    DetailedBreakdown
)
from app.metrics.models import DailyMetrics
from app.campaigns.models import Campaign, Strategy, Placement, Creative
from app.clients.models import Client
from decimal import Decimal


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/top-performers", response_model=TopPerformersResponse)
async def get_top_performers(
    start_date: date = Query(...),
    end_date: date = Query(...),
    client_id: Optional[uuid.UUID] = Query(None),
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get top performers across different metrics."""
    
    if current_user.role == 'client':
        client = db.query(Client).filter(Client.user_id == current_user.id).first()
        if not client:
            raise HTTPException(status_code=403, detail="No client associated with user")
        target_client_id = client.id
    elif client_id:
        target_client_id = client_id
    else:
        raise HTTPException(status_code=400, detail="Client ID required")
    
    return DashboardService.get_top_performers(
        db=db,
        client_id=target_client_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit
    )


# ============================================================================
# NEW ENDPOINTS FOR TAB-BASED DASHBOARD WITH SOURCE FILTERING
# ============================================================================

@router.get("/source/{source}/overview", response_model=SourceTabOverview)
async def get_source_overview(
    source: str,
    start_date: date = Query(..., description="Start date for metrics"),
    end_date: date = Query(..., description="End date for metrics"),
    client_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Dashboard Tab Overview - Returns aggregated stats for a specific source (surfside/facebook/vibe).
    Shows overall metrics for the selected date range filtered by source.
    """
    # Validate source
    if source not in ['surfside', 'facebook', 'vibe']:
        raise HTTPException(status_code=400, detail="Invalid source. Must be surfside, facebook, or vibe")
    
    # Determine client
    if current_user.role == 'client':
        client = db.query(Client).filter(Client.user_id == current_user.id).first()
        if not client:
            raise HTTPException(status_code=403, detail="No client associated with user")
        target_client_id = client.id
    elif client_id:
        target_client_id = client_id
    else:
        raise HTTPException(status_code=400, detail="Client ID required")
    
    # Get aggregated stats for the source
    result = db.query(
        func.sum(DailyMetrics.impressions).label('impressions'),
        func.sum(DailyMetrics.clicks).label('clicks'),
        func.sum(DailyMetrics.conversions).label('conversions'),
        func.sum(DailyMetrics.conversion_revenue).label('revenue'),
        func.sum(DailyMetrics.spend).label('spend')
    ).filter(
        DailyMetrics.client_id == target_client_id,
        DailyMetrics.source == source,
        DailyMetrics.date >= start_date,
        DailyMetrics.date <= end_date
    ).first()
    
    if not result or not result.impressions:
        return SourceTabOverview(
            source=source,
            total_impressions=0,
            total_clicks=0,
            total_conversions=0,
            total_revenue=Decimal('0'),
            total_spend=Decimal('0'),
            overall_ctr=Decimal('0'),
            overall_cpc=Decimal('0'),
            overall_cpa=Decimal('0'),
            overall_roas=Decimal('0')
        )
    
    # Calculate metrics
    from app.metrics.calculator import MetricsCalculator
    
    return SourceTabOverview(
        source=source,
        total_impressions=result.impressions,
        total_clicks=result.clicks,
        total_conversions=result.conversions,
        total_revenue=result.revenue,
        total_spend=result.spend,
        overall_ctr=MetricsCalculator.calculate_ctr(result.impressions, result.clicks),
        overall_cpc=MetricsCalculator.calculate_cpc(Decimal(str(result.spend)), result.clicks),
        overall_cpa=MetricsCalculator.calculate_cpa(Decimal(str(result.spend)), result.conversions),
        overall_roas=MetricsCalculator.calculate_roas(Decimal(str(result.revenue)), Decimal(str(result.spend)))
    )


@router.get("/source/{source}/campaigns/detailed", response_model=List[DetailedBreakdown])
async def get_source_campaigns_detailed(
    source: str,
    start_date: date = Query(...),
    end_date: date = Query(...),
    client_id: Optional[uuid.UUID] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Dashboard Campaign Breakdown - Returns detailed metrics for each campaign in the source.
    Shows CTR, conversions, clicks, impressions, spend, revenue, ROAS for each campaign.
    """
    # Validate and determine client (same pattern as above)
    if source not in ['surfside', 'facebook', 'vibe']:
        raise HTTPException(status_code=400, detail="Invalid source")
    
    if current_user.role == 'client':
        client = db.query(Client).filter(Client.user_id == current_user.id).first()
        if not client:
            raise HTTPException(status_code=403, detail="No client associated with user")
        target_client_id = client.id
    elif client_id:
        target_client_id = client_id
    else:
        raise HTTPException(status_code=400, detail="Client ID required")
    
    # Query campaigns with aggregated metrics
    results = db.query(
        Campaign.name,
        func.sum(DailyMetrics.impressions).label('impressions'),
        func.sum(DailyMetrics.clicks).label('clicks'),
        func.sum(DailyMetrics.conversions).label('conversions'),
        func.sum(DailyMetrics.conversion_revenue).label('revenue'),
        func.sum(DailyMetrics.spend).label('spend')
    ).join(Campaign, DailyMetrics.campaign_id == Campaign.id
    ).filter(
        DailyMetrics.client_id == target_client_id,
        DailyMetrics.source == source,
        DailyMetrics.date >= start_date,
        DailyMetrics.date <= end_date
    ).group_by(Campaign.name
    ).order_by(func.sum(DailyMetrics.conversions).desc()
    ).limit(limit).all()
    
    from app.metrics.calculator import MetricsCalculator
    
    breakdown = []
    for row in results:
        breakdown.append(DetailedBreakdown(
            name=row.name,
            impressions=row.impressions,
            clicks=row.clicks,
            conversions=row.conversions,
            revenue=row.revenue,
            spend=row.spend,
            ctr=MetricsCalculator.calculate_ctr(row.impressions, row.clicks),
            cpc=MetricsCalculator.calculate_cpc(Decimal(str(row.spend)), row.clicks),
            cpa=MetricsCalculator.calculate_cpa(Decimal(str(row.spend)), row.conversions),
            roas=MetricsCalculator.calculate_roas(Decimal(str(row.revenue)), Decimal(str(row.spend)))
        ))
    
    return breakdown


@router.get("/source/{source}/strategies/detailed", response_model=List[DetailedBreakdown])
async def get_source_strategies_detailed(
    source: str,
    start_date: date = Query(...),
    end_date: date = Query(...),
    client_id: Optional[uuid.UUID] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Dashboard Strategy Breakdown - Returns detailed metrics for each strategy in the source.
    Shows CTR, conversions, clicks, impressions, spend, revenue, ROAS for each strategy.
    """
    if source not in ['surfside', 'facebook', 'vibe']:
        raise HTTPException(status_code=400, detail="Invalid source")
    
    if current_user.role == 'client':
        client = db.query(Client).filter(Client.user_id == current_user.id).first()
        if not client:
            raise HTTPException(status_code=403, detail="No client associated with user")
        target_client_id = client.id
    elif client_id:
        target_client_id = client_id
    else:
        raise HTTPException(status_code=400, detail="Client ID required")
    
    results = db.query(
        Strategy.name,
        func.sum(DailyMetrics.impressions).label('impressions'),
        func.sum(DailyMetrics.clicks).label('clicks'),
        func.sum(DailyMetrics.conversions).label('conversions'),
        func.sum(DailyMetrics.conversion_revenue).label('revenue'),
        func.sum(DailyMetrics.spend).label('spend')
    ).join(Strategy, DailyMetrics.strategy_id == Strategy.id
    ).filter(
        DailyMetrics.client_id == target_client_id,
        DailyMetrics.source == source,
        DailyMetrics.date >= start_date,
        DailyMetrics.date <= end_date
    ).group_by(Strategy.name
    ).order_by(func.sum(DailyMetrics.conversions).desc()
    ).limit(limit).all()
    
    from app.metrics.calculator import MetricsCalculator
    
    breakdown = []
    for row in results:
        breakdown.append(DetailedBreakdown(
            name=row.name,
            impressions=row.impressions,
            clicks=row.clicks,
            conversions=row.conversions,
            revenue=row.revenue,
            spend=row.spend,
            ctr=MetricsCalculator.calculate_ctr(row.impressions, row.clicks),
            cpc=MetricsCalculator.calculate_cpc(Decimal(str(row.spend)), row.clicks),
            cpa=MetricsCalculator.calculate_cpa(Decimal(str(row.spend)), row.conversions),
            roas=MetricsCalculator.calculate_roas(Decimal(str(row.revenue)), Decimal(str(row.spend)))
        ))
    
    return breakdown


@router.get("/source/{source}/placements/detailed", response_model=List[DetailedBreakdown])
async def get_source_placements_detailed(
    source: str,
    start_date: date = Query(...),
    end_date: date = Query(...),
    client_id: Optional[uuid.UUID] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Dashboard Placement Breakdown - Returns detailed metrics for each placement in the source.
    Shows CTR, conversions, clicks, impressions, spend, revenue, ROAS for each placement.
    """
    if source not in ['surfside', 'facebook', 'vibe']:
        raise HTTPException(status_code=400, detail="Invalid source")
    
    if current_user.role == 'client':
        client = db.query(Client).filter(Client.user_id == current_user.id).first()
        if not client:
            raise HTTPException(status_code=403, detail="No client associated with user")
        target_client_id = client.id
    elif client_id:
        target_client_id = client_id
    else:
        raise HTTPException(status_code=400, detail="Client ID required")
    
    results = db.query(
        Placement.name,
        func.sum(DailyMetrics.impressions).label('impressions'),
        func.sum(DailyMetrics.clicks).label('clicks'),
        func.sum(DailyMetrics.conversions).label('conversions'),
        func.sum(DailyMetrics.conversion_revenue).label('revenue'),
        func.sum(DailyMetrics.spend).label('spend')
    ).join(Placement, DailyMetrics.placement_id == Placement.id
    ).filter(
        DailyMetrics.client_id == target_client_id,
        DailyMetrics.source == source,
        DailyMetrics.date >= start_date,
        DailyMetrics.date <= end_date
    ).group_by(Placement.name
    ).order_by(func.sum(DailyMetrics.conversions).desc()
    ).limit(limit).all()
    
    from app.metrics.calculator import MetricsCalculator
    
    breakdown = []
    for row in results:
        breakdown.append(DetailedBreakdown(
            name=row.name,
            impressions=row.impressions,
            clicks=row.clicks,
            conversions=row.conversions,
            revenue=row.revenue,
            spend=row.spend,
            ctr=MetricsCalculator.calculate_ctr(row.impressions, row.clicks),
            cpc=MetricsCalculator.calculate_cpc(Decimal(str(row.spend)), row.clicks),
            cpa=MetricsCalculator.calculate_cpa(Decimal(str(row.spend)), row.conversions),
            roas=MetricsCalculator.calculate_roas(Decimal(str(row.revenue)), Decimal(str(row.spend)))
        ))
    
    return breakdown


@router.get("/source/{source}/creatives/detailed", response_model=List[DetailedBreakdown])
async def get_source_creatives_detailed(
    source: str,
    start_date: date = Query(...),
    end_date: date = Query(...),
    client_id: Optional[uuid.UUID] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Dashboard Creative Breakdown - Returns detailed metrics for each creative in the source.
    Shows CTR, conversions, clicks, impressions, spend, revenue, ROAS for each creative.
    """
    if source not in ['surfside', 'facebook', 'vibe']:
        raise HTTPException(status_code=400, detail="Invalid source")
    
    if current_user.role == 'client':
        client = db.query(Client).filter(Client.user_id == current_user.id).first()
        if not client:
            raise HTTPException(status_code=403, detail="No client associated with user")
        target_client_id = client.id
    elif client_id:
        target_client_id = client_id
    else:
        raise HTTPException(status_code=400, detail="Client ID required")
    
    results = db.query(
        Creative.name,
        func.sum(DailyMetrics.impressions).label('impressions'),
        func.sum(DailyMetrics.clicks).label('clicks'),
        func.sum(DailyMetrics.conversions).label('conversions'),
        func.sum(DailyMetrics.conversion_revenue).label('revenue'),
        func.sum(DailyMetrics.spend).label('spend')
    ).join(Creative, DailyMetrics.creative_id == Creative.id
    ).filter(
        DailyMetrics.client_id == target_client_id,
        DailyMetrics.source == source,
        DailyMetrics.date >= start_date,
        DailyMetrics.date <= end_date
    ).group_by(Creative.name
    ).order_by(func.sum(DailyMetrics.conversions).desc()
    ).limit(limit).all()
    
    from app.metrics.calculator import MetricsCalculator
    
    breakdown = []
    for row in results:
        breakdown.append(DetailedBreakdown(
            name=row.name,
            impressions=row.impressions,
            clicks=row.clicks,
            conversions=row.conversions,
            revenue=row.revenue,
            spend=row.spend,
            ctr=MetricsCalculator.calculate_ctr(row.impressions, row.clicks),
            cpc=MetricsCalculator.calculate_cpc(Decimal(str(row.spend)), row.clicks),
            cpa=MetricsCalculator.calculate_cpa(Decimal(str(row.spend)), row.conversions),
            roas=MetricsCalculator.calculate_roas(Decimal(str(row.revenue)), Decimal(str(row.spend)))
        ))
    
    return breakdown
