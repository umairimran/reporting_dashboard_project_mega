"""
Pydantic schemas for metrics API responses.
"""
from pydantic import BaseModel, Field
from datetime import date
from decimal import Decimal
from typing import Optional
import uuid


class DailyMetricsResponse(BaseModel):
    """Response schema for daily metrics."""
    id: uuid.UUID
    client_id: uuid.UUID
    client_name: str
    campaign_name: str
    strategy_name: str
    placement_name: str
    creative_name: str
    date: date
    impressions: int
    clicks: int
    conversions: int
    conversion_revenue: Decimal
    ctr: Decimal
    spend: Decimal
    cpc: Decimal
    cpa: Decimal
    roas: Decimal
    source: str
    
    class Config:
        from_attributes = True


class WeeklySummaryResponse(BaseModel):
    """Response schema for weekly summary."""
    id: uuid.UUID
    client_id: uuid.UUID
    week_start: date
    week_end: date
    impressions: int
    clicks: int
    conversions: int
    revenue: Decimal
    spend: Decimal
    ctr: Decimal
    cpc: Decimal
    cpa: Decimal
    roas: Decimal
    
    class Config:
        from_attributes = True


class MonthlySummaryResponse(BaseModel):
    """Response schema for monthly summary."""
    id: uuid.UUID
    client_id: uuid.UUID
    year: int
    month: int
    impressions: int
    clicks: int
    conversions: int
    revenue: Decimal
    spend: Decimal
    ctr: Decimal
    cpc: Decimal
    cpa: Decimal
    roas: Decimal
    
    class Config:
        from_attributes = True


class MetricsSummary(BaseModel):
    """Summary statistics for metrics."""
    total_impressions: int
    total_clicks: int
    total_conversions: int
    total_revenue: Decimal
    total_spend: Decimal
    avg_ctr: Decimal
    avg_cpc: Decimal
    avg_cpa: Decimal
    avg_roas: Decimal


class DateRangeMetrics(BaseModel):
    """Metrics for a date range."""
    start_date: date
    end_date: date
    metrics: MetricsSummary
    daily_breakdown: list[DailyMetricsResponse]


class CampaignPerformance(BaseModel):
    """Performance metrics by campaign."""
    campaign_name: str
    impressions: int
    clicks: int
    conversions: int
    revenue: Decimal
    spend: Decimal
    ctr: Decimal
    cpc: Decimal
    cpa: Decimal
    roas: Decimal


class TopPerformers(BaseModel):
    """Top performing entities."""
    by_impressions: list[CampaignPerformance]
    by_conversions: list[CampaignPerformance]
    by_roas: list[CampaignPerformance]
    by_revenue: list[CampaignPerformance]
