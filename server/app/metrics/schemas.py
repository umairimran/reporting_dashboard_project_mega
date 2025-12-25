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
    campaign_name: Optional[str] = None
    strategy_name: Optional[str] = None
    placement_name: Optional[str] = None
    creative_name: str
    region_name: Optional[str] = None

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
    ctr: Decimal = Field(default=Decimal('0'))
    cpc: Decimal = Field(default=Decimal('0'))
    cpa: Decimal = Field(default=Decimal('0'))
    roas: Decimal = Field(default=Decimal('0'))
    
    class Config:
        from_attributes = True


class MonthlySummaryResponse(BaseModel):
    """Response schema for monthly summary."""
    id: uuid.UUID
    client_id: uuid.UUID
    month_start: date
    month_end: date
    year: int = Field(default=0, description="Derived from month_start")
    month: int = Field(default=0, description="Derived from month_start")
    impressions: int
    clicks: int
    conversions: int
    revenue: Decimal
    spend: Decimal
    ctr: Decimal = Field(default=Decimal('0'))
    cpc: Decimal = Field(default=Decimal('0'))
    cpa: Decimal = Field(default=Decimal('0'))
    roas: Decimal = Field(default=Decimal('0'))
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm(cls, obj):
        """Create response with derived year and month from month_start."""
        data = {
            'id': obj.id,
            'client_id': obj.client_id,
            'month_start': obj.month_start,
            'month_end': obj.month_end,
            'year': obj.month_start.year,
            'month': obj.month_start.month,
            'impressions': obj.impressions,
            'clicks': obj.clicks,
            'conversions': obj.conversions,
            'revenue': obj.revenue,
            'spend': obj.spend,
            'ctr': obj.ctr,
            'cpc': obj.cpc,
            'cpa': obj.cpa,
            'roas': obj.roas
        }
        return cls(**data)


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
