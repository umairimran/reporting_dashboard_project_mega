"""
Export API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse, Response
from sqlalchemy.orm import Session
import uuid
from datetime import date
from typing import Optional
import io
from app.core.database import get_db
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.exports.csv_export import CSVExportService
from app.exports.pdf_export import PDFExportService
from app.core.logging import logger


router = APIRouter(prefix="/exports", tags=["Exports"])


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
