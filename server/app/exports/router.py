"""
Export API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.responses import StreamingResponse, Response, FileResponse
from sqlalchemy.orm import Session
import uuid
from datetime import date
from typing import Optional, List
import io
import os
from app.core.database import get_db
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.exports.models import Report
from app.exports.csv_export import CSVExportService
from app.exports.pdf_export import PDFExportService
from app.exports.service import ReportService
from app.exports.schemas import ReportCreate, ReportResponse
from app.core.logging import logger


router = APIRouter(prefix="/exports", tags=["Exports"])


@router.post("/reports", response_model=ReportResponse, status_code=201)
async def create_report(
    report_data: ReportCreate,
    background_tasks: BackgroundTasks,
    client_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate a new async report (Weekly/Monthly).
    """
    # Determine client
    target_client_id = None
    if current_user.role == 'client':
        if current_user.clients:
            target_client_id = current_user.clients[0].id
    else:
        # Admin must provide client_id via query param if simulating
        target_client_id = client_id
        
    if not target_client_id:
        raise HTTPException(status_code=400, detail="Client ID required for report generation.")

    try:
        # Create DB record
        report = ReportService.create_report(db, target_client_id, report_data)
        
        # Trigger background task
        # We pass a new DB session factory or ensure the task manages its own session
        # The service method expects a session. BackgroundTasks runs AFTER response.
        # We need a way to pass a fresh session to background task. 
        # Actually `BackgroundTasks` runs in the same loop. 
        # Best practice: use a dependency injection in the function or handle session inside.
        # Since we can't easily pass 'Depends' to background, we'll manually create session inside wrapper 
        # OR just pass the logic to a function that creates its own session.
        
        # We'll create a wrapper function here to handle session lifecycle for background task
        background_tasks.add_task(run_report_generation, report.id)
        
        return report
    except Exception as e:
        logger.error(f"Failed to start report generation: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

async def run_report_generation(report_id: uuid.UUID):
    """Wrapper to run report generation with its own db session."""
    from app.core.database import SessionLocal
    db = SessionLocal()
    try:
        await ReportService.generate_report_background(db, report_id)
    finally:
        db.close()


@router.get("/reports", response_model=List[ReportResponse])
async def get_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    client_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all reports for the current user's client.
    """
    target_client_id = None
    if current_user.role == 'client':
        if current_user.clients:
            target_client_id = current_user.clients[0].id
    else:
        # Admin can view reports for a specific client if provided
        target_client_id = client_id
    
    if not target_client_id:
        # If no client context, return empty list (or all reports? empty for safety)
        return []

    return ReportService.get_reports(db, target_client_id, skip, limit)


@router.get("/reports/{report_id}/download")
async def download_report(
    report_id: uuid.UUID,
    format: str = Query("pdf", regex="^(pdf|csv)$"),
    db: Session = Depends(get_db),
    client_id: Optional[uuid.UUID] = Query(None), # For admin override if needed
    current_user: User = Depends(get_current_user)
):
    """
    Download a generated report file.
    """
    if current_user.role == 'client':
        if current_user.clients:
            target_client_id = current_user.clients[0].id
        else:
             raise HTTPException(status_code=403, detail="Client User has no linked client")
    else:
        # Admin can access any report, theoretically. 
        # But get_report_file_path checks client_id ownership. 
        # We should fetch the report first to check ownership or pass the report's client_id if admin?
        # Better: let's look up the report to see who owns it, then verify admin access.
        # However, to reuse existing service method which filters by client_id:
        # We need the client_id. 
        # Actually, get_report_file_path enforces client_id match.
        # If admin, we might not know the client_id immediately.
        # Let's do a direct lookup for Admin.
        pass

    # Admin Logic Improvement:
    # If admin, fetch report to get client_id, then proceed.
    target_client_id = None
    if current_user.role == 'client':
         if current_user.clients:
             target_client_id = current_user.clients[0].id
    
    # If admin (target_client_id is None), we skip the client_id filter in a custom query OR
    # We first find the report to get its client_id.
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    # Check permissions
    if current_user.role == 'client':
        if report.client_id != target_client_id:
             raise HTTPException(status_code=403, detail="Access denied")
    
    # Get path directly from report object since we fetched it
    file_path = report.csv_file_path if format == 'csv' else report.pdf_file_path
    
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on server")
        
    filename = os.path.basename(file_path)
    media_type = 'text/csv' if format == 'csv' else 'application/pdf'
    return FileResponse(file_path, filename=filename, media_type=media_type)


@router.get("/csv/daily-metrics")
async def export_daily_metrics_csv(
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    client_id: Optional[uuid.UUID] = Query(None, description="Client ID (admin only)"),
    source: Optional[str] = Query(None, description="Filter by source"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Export daily metrics to CSV file.
    
    Returns a downloadable CSV file with daily metrics data.
    """
    # Determine client
    if current_user.role == 'client':
        target_client_id = current_user.client_id
    elif client_id:
        target_client_id = client_id
    else:
        raise HTTPException(status_code=400, detail="Client ID required")
    
    try:
        # Generate CSV
        csv_content = CSVExportService.export_daily_metrics(
            db=db,
            client_id=target_client_id,
            start_date=start_date,
            end_date=end_date,
            source=source
        )
        
        # Create filename
        filename = f"daily_metrics_{start_date}_{end_date}.csv"
        
        # Return as streaming response
        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"CSV export failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/csv/campaign-summary")
async def export_campaign_summary_csv(
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    client_id: Optional[uuid.UUID] = Query(None, description="Client ID (admin only)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Export campaign summary to CSV file.
    
    Returns a downloadable CSV file with aggregated campaign performance.
    """
    # Determine client
    if current_user.role == 'client':
        target_client_id = current_user.client_id
    elif client_id:
        target_client_id = client_id
    else:
        raise HTTPException(status_code=400, detail="Client ID required")
    
    try:
        # Generate CSV
        csv_content = CSVExportService.export_campaign_summary(
            db=db,
            client_id=target_client_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # Create filename
        filename = f"campaign_summary_{start_date}_{end_date}.csv"
        
        # Return as streaming response
        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"CSV export failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/pdf/dashboard-report")
async def export_dashboard_pdf(
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    client_id: Optional[uuid.UUID] = Query(None, description="Client ID (admin only)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Export dashboard report to PDF file.
    
    Returns a downloadable PDF file with comprehensive dashboard report.
    """
    # Determine client
    if current_user.role == 'client':
        target_client_id = current_user.client_id
    elif client_id:
        target_client_id = client_id
    else:
        raise HTTPException(status_code=400, detail="Client ID required")
    
    try:
        # Generate PDF
        pdf_content = PDFExportService.export_dashboard_report(
            db=db,
            client_id=target_client_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # Create filename
        filename = f"dashboard_report_{start_date}_{end_date}.pdf"
        
        # Return as response
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"PDF export failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")
