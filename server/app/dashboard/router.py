"""
Dashboard API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import uuid
from datetime import date, timedelta
from typing import Optional
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
    TopPerformersResponse
)


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/", response_model=ClientDashboard)
async def get_dashboard(
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    client_id: Optional[uuid.UUID] = Query(None, description="Client ID (admin only)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get complete dashboard for a client.
    
    Includes summary, campaign breakdown, source breakdown, daily trends, and top performers.
    """
    # Determine which client to show
    if current_user.role == 'client':
        target_client_id = current_user.client_id
    elif client_id:
        target_client_id = client_id
    else:
        raise HTTPException(
            status_code=400,
            detail="Client ID required for admin users"
        )
    
    try:
        dashboard = DashboardService.get_client_dashboard(
            db=db,
            client_id=target_client_id,
            start_date=start_date,
            end_date=end_date
        )
        return dashboard
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/summary", response_model=DashboardSummary)
async def get_summary(
    start_date: date = Query(...),
    end_date: date = Query(...),
    client_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get high-level dashboard summary."""
    
    if current_user.role == 'client':
        target_client_id = current_user.client_id
    elif client_id:
        target_client_id = client_id
    else:
        raise HTTPException(status_code=400, detail="Client ID required")
    
    return DashboardService.get_dashboard_summary(
        db=db,
        client_id=target_client_id,
        start_date=start_date,
        end_date=end_date
    )


@router.get("/campaigns", response_model=list[CampaignBreakdown])
async def get_campaigns(
    start_date: date = Query(...),
    end_date: date = Query(...),
    client_id: Optional[uuid.UUID] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get campaign performance breakdown."""
    
    if current_user.role == 'client':
        target_client_id = current_user.client_id
    elif client_id:
        target_client_id = client_id
    else:
        raise HTTPException(status_code=400, detail="Client ID required")
    
    return DashboardService.get_campaign_breakdown(
        db=db,
        client_id=target_client_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit
    )


@router.get("/sources", response_model=list[SourceBreakdown])
async def get_sources(
    start_date: date = Query(...),
    end_date: date = Query(...),
    client_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get performance breakdown by data source."""
    
    if current_user.role == 'client':
        target_client_id = current_user.client_id
    elif client_id:
        target_client_id = client_id
    else:
        raise HTTPException(status_code=400, detail="Client ID required")
    
    return DashboardService.get_source_breakdown(
        db=db,
        client_id=target_client_id,
        start_date=start_date,
        end_date=end_date
    )


@router.get("/trends", response_model=list[DailyTrend])
async def get_trends(
    start_date: date = Query(...),
    end_date: date = Query(...),
    client_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get daily trend data."""
    
    if current_user.role == 'client':
        target_client_id = current_user.client_id
    elif client_id:
        target_client_id = client_id
    else:
        raise HTTPException(status_code=400, detail="Client ID required")
    
    return DashboardService.get_daily_trends(
        db=db,
        client_id=target_client_id,
        start_date=start_date,
        end_date=end_date
    )


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
        target_client_id = current_user.client_id
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


@router.get("/quick-stats")
async def get_quick_stats(
    client_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get quick stats for today, this week, and this month."""
    
    if current_user.role == 'client':
        target_client_id = current_user.client_id
    elif client_id:
        target_client_id = client_id
    else:
        raise HTTPException(status_code=400, detail="Client ID required")
    
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    month_start = date(today.year, today.month, 1)
    
    return {
        "today": DashboardService.get_dashboard_summary(db, target_client_id, today, today),
        "this_week": DashboardService.get_dashboard_summary(db, target_client_id, week_start, today),
        "this_month": DashboardService.get_dashboard_summary(db, target_client_id, month_start, today)
    }
