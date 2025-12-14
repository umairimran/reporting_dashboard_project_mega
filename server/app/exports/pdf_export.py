"""
PDF export service for reports.
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
import io
from datetime import date
from decimal import Decimal
from sqlalchemy.orm import Session
import uuid
from typing import List
from app.clients.models import Client
from app.dashboard.service import DashboardService
from app.core.logging import logger


class PDFExportService:
    """Service for exporting data to PDF format."""
    
    @staticmethod
    def _format_number(value) -> str:
        """Format number for display."""
        if value is None:
            return "N/A"
        if isinstance(value, Decimal):
            return f"{value:,.2f}"
        if isinstance(value, (int, float)):
            return f"{value:,}"
        return str(value)
    
    @staticmethod
    def _format_currency(value) -> str:
        """Format currency for display."""
        if value is None:
            return "N/A"
        return f"${value:,.2f}"
    
    @staticmethod
    def export_dashboard_report(
        db: Session,
        client_id: uuid.UUID,
        start_date: date,
        end_date: date
    ) -> bytes:
        """
        Export dashboard report to PDF.
        
        Returns:
            PDF content as bytes
        """
        logger.info(f"Generating PDF report for client {client_id}")
        
        # Get client
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise ValueError(f"Client not found: {client_id}")
        
        # Get dashboard data
        dashboard = DashboardService.get_client_dashboard(
            db=db,
            client_id=client_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # Create PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#34495E'),
            spaceAfter=12
        )
        
        # Title
        elements.append(Paragraph(f"Performance Report - {client.name}", title_style))
        elements.append(Paragraph(
            f"{start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}",
            styles['Normal']
        ))
        elements.append(Spacer(1, 0.3 * inch))
        
        # Summary Section
        elements.append(Paragraph("Executive Summary", heading_style))
        
        summary_data = [
            ['Metric', 'Value'],
            ['Total Impressions', PDFExportService._format_number(dashboard.summary.total_impressions)],
            ['Total Clicks', PDFExportService._format_number(dashboard.summary.total_clicks)],
            ['Total Conversions', PDFExportService._format_number(dashboard.summary.total_conversions)],
            ['Total Revenue', PDFExportService._format_currency(dashboard.summary.total_revenue)],
            ['Total Spend', PDFExportService._format_currency(dashboard.summary.total_spend)],
            ['Overall CTR', f"{dashboard.summary.overall_ctr}%"],
            ['Overall CPC', PDFExportService._format_currency(dashboard.summary.overall_cpc)],
            ['Overall CPA', PDFExportService._format_currency(dashboard.summary.overall_cpa)],
            ['Overall ROAS', PDFExportService._format_number(dashboard.summary.overall_roas)],
            ['Active Campaigns', str(dashboard.summary.active_campaigns)],
            ['Data Sources', ', '.join(dashboard.summary.data_sources)]
        ]
        
        summary_table = Table(summary_data, colWidths=[3 * inch, 3 * inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 0.3 * inch))
        
        # Campaign Performance Section
        if dashboard.campaigns:
            elements.append(Paragraph("Top Campaign Performance", heading_style))
            
            campaign_data = [['Campaign', 'Impressions', 'Clicks', 'Conversions', 'Revenue', 'ROAS']]
            
            for campaign in dashboard.campaigns[:10]:  # Top 10
                campaign_data.append([
                    campaign.campaign_name[:30],  # Truncate long names
                    PDFExportService._format_number(campaign.impressions),
                    PDFExportService._format_number(campaign.clicks),
                    PDFExportService._format_number(campaign.conversions),
                    PDFExportService._format_currency(campaign.revenue),
                    PDFExportService._format_number(campaign.roas)
                ])
            
            campaign_table = Table(campaign_data, colWidths=[2 * inch, 1 * inch, 1 * inch, 1 * inch, 1 * inch, 1 * inch])
            campaign_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
            ]))
            
            elements.append(campaign_table)
            elements.append(Spacer(1, 0.3 * inch))
        
        # Source Breakdown Section
        if dashboard.sources:
            elements.append(Paragraph("Performance by Source", heading_style))
            
            source_data = [['Source', 'Impressions', 'Clicks', 'Conversions', 'CTR']]
            
            for source in dashboard.sources:
                source_data.append([
                    source.source.upper(),
                    PDFExportService._format_number(source.impressions),
                    PDFExportService._format_number(source.clicks),
                    PDFExportService._format_number(source.conversions),
                    f"{source.ctr}%"
                ])
            
            source_table = Table(source_data, colWidths=[2 * inch, 1.5 * inch, 1.5 * inch, 1.5 * inch, 1 * inch])
            source_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ]))
            
            elements.append(source_table)
        
        # Build PDF
        doc.build(elements)
        
        pdf_content = buffer.getvalue()
        buffer.close()
        
        logger.info(f"Generated PDF report ({len(pdf_content)} bytes)")
        
        return pdf_content
