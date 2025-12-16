"""
Ingestion logs API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import Optional
from datetime import datetime, date
import uuid

from app.core.database import get_db
from app.auth.dependencies import require_admin
from app.auth.models import User
from app.metrics.models import IngestionLog
from app.ingestion.schemas import (
    IngestionLogResponse,
    IngestionLogListResponse,
    IngestionLogResolution
)

router = APIRouter(prefix="/ingestion-logs", tags=["Ingestion Logs"])


@router.get("", response_model=IngestionLogListResponse)
async def get_ingestion_logs(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    status: Optional[str] = Query(None, pattern="^(success|failed|partial|processing)$", description="Filter by status"),
    source: Optional[str] = Query(None, pattern="^(surfside|vibe|facebook)$", description="Filter by source"),
    client_id: Optional[uuid.UUID] = Query(None, description="Filter by client ID"),
    resolution_status: Optional[str] = Query(None, pattern="^(unresolved|resolved|ignored)$", description="Filter by resolution status"),
    start_date: Optional[date] = Query(None, description="Filter logs from this date onwards"),
    end_date: Optional[date] = Query(None, description="Filter logs up to this date"),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Get all ingestion logs with filtering and pagination (admin only).
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        status: Optional status filter
        source: Optional source filter
        client_id: Optional client filter
        resolution_status: Optional resolution status filter
        start_date: Optional start date filter
        end_date: Optional end date filter
        db: Database session
        admin: Current admin user
        
    Returns:
        List of ingestion logs with total count
    """
    query = db.query(IngestionLog)
    
    # Apply filters
    if status:
        query = query.filter(IngestionLog.status == status)
    
    if source:
        query = query.filter(IngestionLog.source == source)
    
    if client_id:
        query = query.filter(IngestionLog.client_id == client_id)
    
    if resolution_status:
        query = query.filter(IngestionLog.resolution_status == resolution_status)
    
    if start_date:
        query = query.filter(IngestionLog.run_date >= start_date)
    
    if end_date:
        query = query.filter(IngestionLog.run_date <= end_date)
    
    # Get total count
    total = query.count()
    
    # Get paginated results
    logs = query.order_by(desc(IngestionLog.created_at)).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "logs": logs
    }


@router.get("/stats", response_model=dict)
async def get_ingestion_stats(
    start_date: Optional[date] = Query(None, description="Stats from this date onwards"),
    end_date: Optional[date] = Query(None, description="Stats up to this date"),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Get ingestion statistics summary (admin only).
    
    Args:
        start_date: Optional start date filter
        end_date: Optional end date filter
        db: Database session
        admin: Current admin user
        
    Returns:
        Ingestion statistics
    """
    query = db.query(IngestionLog)
    
    if start_date:
        query = query.filter(IngestionLog.run_date >= start_date)
    
    if end_date:
        query = query.filter(IngestionLog.run_date <= end_date)
    
    # Get counts by status
    status_counts = {}
    for status_value in ['success', 'failed', 'partial', 'processing']:
        count = query.filter(IngestionLog.status == status_value).count()
        status_counts[status_value] = count
    
    # Get counts by source
    source_counts = {}
    for source_value in ['surfside', 'vibe', 'facebook']:
        count = query.filter(IngestionLog.source == source_value).count()
        source_counts[source_value] = count
    
    # Get resolution stats
    resolution_counts = {
        'unresolved': query.filter(IngestionLog.resolution_status == 'unresolved').count(),
        'resolved': query.filter(IngestionLog.resolution_status == 'resolved').count(),
        'ignored': query.filter(IngestionLog.resolution_status == 'ignored').count(),
        'no_errors': query.filter(IngestionLog.resolution_status.is_(None)).count()
    }
    
    # Get aggregate metrics
    totals = db.query(
        func.sum(IngestionLog.records_loaded).label('total_loaded'),
        func.sum(IngestionLog.records_failed).label('total_failed')
    ).filter(IngestionLog.id.in_(query.with_entities(IngestionLog.id))).first()
    
    return {
        "total_logs": query.count(),
        "by_status": status_counts,
        "by_source": source_counts,
        "by_resolution": resolution_counts,
        "total_records_loaded": int(totals.total_loaded or 0),
        "total_records_failed": int(totals.total_failed or 0)
    }


@router.get("/{log_id}", response_model=IngestionLogResponse)
async def get_ingestion_log(
    log_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Get a specific ingestion log by ID (admin only).
    
    Args:
        log_id: Ingestion log UUID
        db: Database session
        admin: Current admin user
        
    Returns:
        Ingestion log details
        
    Raises:
        HTTPException: If log not found
    """
    log = db.query(IngestionLog).filter(IngestionLog.id == log_id).first()
    
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ingestion log not found"
        )
    
    return log


@router.put("/{log_id}/resolve", response_model=IngestionLogResponse)
async def resolve_ingestion_error(
    log_id: uuid.UUID,
    resolution_data: IngestionLogResolution,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Mark an ingestion error as resolved or ignored (admin only).
    
    Args:
        log_id: Ingestion log UUID
        resolution_data: Resolution information
        db: Database session
        admin: Current admin user
        
    Returns:
        Updated ingestion log
        
    Raises:
        HTTPException: If log not found
    """
    log = db.query(IngestionLog).filter(IngestionLog.id == log_id).first()
    
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ingestion log not found"
        )
    
    log.resolution_status = resolution_data.resolution_status
    log.resolution_notes = resolution_data.resolution_notes
    log.resolved_at = datetime.utcnow()
    log.resolved_by = admin.id
    
    db.commit()
    db.refresh(log)
    
    return log
