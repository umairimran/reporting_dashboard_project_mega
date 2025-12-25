"""
Service for managing reports.
"""
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
import os
import asyncio
from typing import List, Optional
from app.exports.models import Report
from app.exports.schemas import ReportCreate, ReportType, ReportStatus
from app.exports.pdf_export import PDFExportService
from app.exports.csv_export import CSVExportService
from app.core.logging import logger

STORAGE_DIR = "storage/reports"

class ReportService:
    """Service for managing reports."""

    @staticmethod
    def create_report(db: Session, client_id: uuid.UUID, report_data: ReportCreate) -> Report:
        """
        Create a new report record and start generation task.
        """
        # Create DB record
        report = Report(
            client_id=client_id,
            type=report_data.type,
            source=report_data.source,
            period_start=report_data.period_start,
            period_end=report_data.period_end,
            status=ReportStatus.GENERATING
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        
        return report

    @staticmethod
    async def generate_report_background(db: Session, report_id: uuid.UUID):
        """
        Background task to generate report file.
        """
        logger.info(f"Starting background report generation for {report_id}")
        
        try:
            # Get report from new session (to be safe with threads/async)
            report = db.query(Report).filter(Report.id == report_id).first()
            if not report:
                logger.error(f"Report {report_id} not found in background task")
                return

            # Ensure storage directory exists
            os.makedirs(STORAGE_DIR, exist_ok=True)
            
            # Base Filename
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            base_filename = f"{report.type}_report_{report.source or 'all'}_{timestamp}"
            
            # 1. Generate PDF
            logger.info("Generating PDF...")
            pdf_content = PDFExportService.export_dashboard_report(
                db=db, 
                client_id=report.client_id,
                start_date=report.period_start,
                end_date=report.period_end,
                source=report.source
            )
            
            pdf_filename = f"{base_filename}.pdf"
            pdf_path = os.path.join(STORAGE_DIR, pdf_filename)
            with open(pdf_path, "wb") as f:
                f.write(pdf_content)
                
            # 2. Generate CSV
            logger.info("Generating CSV...")
            # For report CSV, we likely want the Aggregated Campaign/Source breakdown or Daily Metrics?
            # User wants "the report" in CSV. Usually users want the raw data corresponding to the report.
            # Let's use export_daily_metrics which is comprehensive, OR export_campaign_summary.
            # daily_metrics is most granular and useful.
            csv_content = CSVExportService.export_daily_metrics(
                db=db,
                client_id=report.client_id,
                start_date=report.period_start,
                end_date=report.period_end,
                source=report.source
            )
            
            csv_filename = f"{base_filename}.csv"
            csv_path = os.path.join(STORAGE_DIR, csv_filename)
            with open(csv_path, "w", newline='') as f:
                f.write(csv_content)
                
            # Update report status
            report.status = ReportStatus.READY
            report.pdf_file_path = pdf_path
            report.csv_file_path = csv_path
            report.updated_at = datetime.utcnow()
            db.commit()
            
            logger.info(f"Report {report_id} generated successfully. PDF: {pdf_path}, CSV: {csv_path}")
            
        except Exception as e:
            logger.error(f"Failed to generate report {report_id}: {str(e)}", exc_info=True)
            # Update status to failed
            try:
                report = db.query(Report).filter(Report.id == report_id).first()
                if report:
                    report.status = ReportStatus.FAILED
                    report.error_message = str(e)
                    report.updated_at = datetime.utcnow()
                    db.commit()
            except Exception as db_e:
                logger.error(f"Failed to update report failure status: {str(db_e)}")

    @staticmethod
    def get_reports(db: Session, client_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Report]:
        """
        Get all reports for a client.
        """
        return db.query(Report).filter(
            Report.client_id == client_id
        ).order_by(Report.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_report_file_path(db: Session, report_id: uuid.UUID, client_id: uuid.UUID, format: str = 'pdf') -> Optional[str]:
        """
        Get file path for a report if ready and belongs to client.
        """
        report = db.query(Report).filter(
            Report.id == report_id,
            Report.client_id == client_id,
            Report.status == ReportStatus.READY
        ).first()
        
        if report:
            if format.lower() == 'csv':
                return report.csv_file_path
            return report.pdf_file_path
        return None
