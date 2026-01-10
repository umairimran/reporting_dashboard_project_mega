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
from sqlalchemy import func, desc
import uuid
from typing import List
from app.clients.models import Client
from app.dashboard.service import DashboardService
from app.core.logging import logger
from app.metrics.models import DailyMetrics
from app.campaigns.models import Campaign, Strategy, Placement, Creative
from app.metrics.calculator import MetricsCalculator


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
    def _get_dimension_stats(
        db: Session,
        client_id: uuid.UUID,
        start_date: date,
        end_date: date,
        dimension_model,
        fk_column,
        limit: int = 10,
        source: str = None
    ):
        """Helper to fetch performance stats for a specific dimension."""
        query = db.query(
            dimension_model.name,
            func.sum(DailyMetrics.impressions).label('impressions'),
            func.sum(DailyMetrics.clicks).label('clicks'),
            func.sum(DailyMetrics.conversions).label('conversions'),
            func.sum(DailyMetrics.conversion_revenue).label('revenue'),
            func.sum(DailyMetrics.spend).label('spend')
        ).join(dimension_model, fk_column == dimension_model.id).filter(
            DailyMetrics.client_id == client_id,
            DailyMetrics.date >= start_date,
            DailyMetrics.date <= end_date
        )

        if source:
            query = query.filter(DailyMetrics.source == source)

        results = query.group_by(dimension_model.name).order_by(
            desc(func.sum(DailyMetrics.impressions))
        ).limit(limit).all()

        data = []
        for r in results:
             roas = MetricsCalculator.calculate_roas(r.revenue, r.spend)
             data.append({
                 'name': r.name,
                 'impressions': r.impressions,
                 'clicks': r.clicks,
                 'conversions': r.conversions,
                 'revenue': r.revenue,
                 'spend': r.spend,
                 'roas': roas
             })
        return data
    
    @staticmethod
    def export_dashboard_report(
        db: Session,
        client_id: uuid.UUID,
        start_date: date,
        end_date: date,
        source: str = None  # Optional source filter
    ) -> bytes:
        """
        Export dashboard report to PDF.
        
        Returns:
            PDF content as bytes
        """
        logger.info(f"Generating PDF report for client {client_id} (Source: {source})")
        
        # Get client
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise ValueError(f"Client not found: {client_id}")
        
        # Get dashboard data (for Summary, Source, Campaign) - keeping original logic for these
        dashboard = DashboardService.get_client_dashboard(
            db=db,
            client_id=client_id,
            start_date=start_date,
            end_date=end_date,
            source=source
        )
        
        # Fetch additional dimension stats directly (avoiding DashboardService mods per user request)
        strategies = PDFExportService._get_dimension_stats(db, client_id, start_date, end_date, Strategy, DailyMetrics.strategy_id, source=source)
        placements = PDFExportService._get_dimension_stats(db, client_id, start_date, end_date, Placement, DailyMetrics.placement_id, source=source)
        creatives = PDFExportService._get_dimension_stats(db, client_id, start_date, end_date, Creative, DailyMetrics.creative_id, source=source)

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
        
        # Helper function to get display name for source
        def get_source_display_name(source_name: str) -> str:
            """Map source name to display name (surfside -> CTV)."""
            if source_name and source_name.lower() == "surfside":
                return "CTV"
            return source_name.upper() if source_name else "All Sources"
        
        # Format data sources for display
        formatted_data_sources = [
            get_source_display_name(src) for src in dashboard.summary.data_sources
        ] if dashboard.summary.data_sources else ["All Sources"]
        
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
            ['Data Sources', ', '.join(formatted_data_sources)]
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
        
        # Helper to render generic performance table
        def render_performance_table(title, items, name_header="Name"):
             if not items: return
             elements.append(Paragraph(title, heading_style))
             table_data = [[name_header, 'Impressions', 'Clicks', 'Conversions', 'Revenue', 'ROAS']]
             for item in items:
                  # Item is dict or object, using existing campaign object for campaign section below,
                  # but using dict for our new sections. 
                  # Let's standardize or handle both.
                  if isinstance(item, dict):
                       row = [
                            item['name'][:30],
                            PDFExportService._format_number(item['impressions']),
                            PDFExportService._format_number(item['clicks']),
                            PDFExportService._format_number(item['conversions']),
                            PDFExportService._format_currency(item['revenue']),
                            PDFExportService._format_number(item['roas'])
                       ]
                  else:
                        # Existing campaign object
                       row = [
                            item.campaign_name[:30],
                            PDFExportService._format_number(item.impressions),
                            PDFExportService._format_number(item.clicks),
                            PDFExportService._format_number(item.conversions),
                            PDFExportService._format_currency(item.revenue),
                            PDFExportService._format_number(item.roas)
                       ]
                  table_data.append(row)
             
             t = Table(table_data, colWidths=[2 * inch, 1 * inch, 1 * inch, 1 * inch, 1 * inch, 1 * inch])
             t.setStyle(TableStyle([
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
             elements.append(t)
             elements.append(Spacer(1, 0.3 * inch))

        # Campaign Performance Section (Existing)
        render_performance_table("Top Campaign Performance", dashboard.campaigns[:10], "Campaign")

        # Source Breakdown Section
        if dashboard.sources:
            elements.append(Paragraph("Performance by Source", heading_style))
            
            source_data = [['Source', 'Impressions', 'Clicks', 'Conversions', 'CTR']]
            
            for source in dashboard.sources:
                source_data.append([
                    get_source_display_name(source.source),
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
            elements.append(Spacer(1, 0.3 * inch)) # Add spacer

        # NEW SECTIONS
        render_performance_table("Top Strategy Performance", strategies, "Strategy")
        render_performance_table("Top Placement Performance", placements, "Placement")
        render_performance_table("Top Creative Performance", creatives, "Creative")
        
        # Build PDF
        doc.build(elements)
        
        pdf_content = buffer.getvalue()
        buffer.close()
        
        logger.info(f"Generated PDF report ({len(pdf_content)} bytes)")
        
        return pdf_content
