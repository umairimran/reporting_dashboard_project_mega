"""
Pydantic schemas for dashboard API responses.
"""
from pydantic import BaseModel, Field
from datetime import date
from decimal import Decimal
from typing import List, Optional
import uuid


class DashboardSummary(BaseModel):
    """High-level dashboard summary."""
    total_impressions: int
    total_clicks: int
    total_conversions: int
    total_revenue: Decimal
    total_spend: Decimal
    overall_ctr: Decimal
    overall_cpc: Optional[Decimal]
    overall_cpa: Optional[Decimal]
    overall_roas: Optional[Decimal]
    active_campaigns: int
    data_sources: List[str]


class CampaignBreakdown(BaseModel):
    """Campaign-level performance breakdown."""
    campaign_name: str
    impressions: int
    clicks: int
    conversions: int
    revenue: Decimal
    spend: Decimal
    ctr: Decimal
    cpc: Optional[Decimal]
    cpa: Optional[Decimal]
    roas: Optional[Decimal]


class SourceBreakdown(BaseModel):
    """Performance breakdown by data source."""
    source: str
    impressions: int
    clicks: int
    conversions: int
    revenue: Decimal
    spend: Decimal
    ctr: Decimal


class DailyTrend(BaseModel):
    """Daily trend data point."""
    date: date
    impressions: int
    clicks: int
    conversions: int
    revenue: Decimal
    spend: Decimal
    ctr: Decimal
    roas: Optional[Decimal]


class WeeklyComparison(BaseModel):
    """Week-over-week comparison."""
    current_week_start: date
    current_week_end: date
    previous_week_start: date
    previous_week_end: date
    
    current_impressions: int
    previous_impressions: int
    impressions_change_pct: Decimal
    
    current_clicks: int
    previous_clicks: int
    clicks_change_pct: Decimal
    
    current_conversions: int
    previous_conversions: int
    conversions_change_pct: Decimal
    
    current_revenue: Decimal
    previous_revenue: Decimal
    revenue_change_pct: Decimal
    
    current_spend: Decimal
    previous_spend: Decimal
    spend_change_pct: Decimal


class MonthlyComparison(BaseModel):
    """Month-over-month comparison."""
    current_year: int
    current_month: int
    previous_year: int
    previous_month: int
    
    current_impressions: int
    previous_impressions: int
    impressions_change_pct: Decimal
    
    current_clicks: int
    previous_clicks: int
    clicks_change_pct: Decimal
    
    current_conversions: int
    previous_conversions: int
    conversions_change_pct: Decimal
    
    current_revenue: Decimal
    previous_revenue: Decimal
    revenue_change_pct: Decimal
    
    current_spend: Decimal
    previous_spend: Decimal
    spend_change_pct: Decimal


class TopPerformer(BaseModel):
    """Top performing entity."""
    name: str
    metric_value: Decimal
    impressions: int
    conversions: int
    revenue: Decimal


class TopPerformersResponse(BaseModel):
    """Response with top performers across different metrics."""
    by_impressions: List[TopPerformer]
    by_conversions: List[TopPerformer]
    by_revenue: List[TopPerformer]
    by_roas: List[TopPerformer]


class ClientDashboard(BaseModel):
    """Complete dashboard for a client."""
    client_id: uuid.UUID
    client_name: str
    date_range_start: date
    date_range_end: date
    
    summary: DashboardSummary
    campaigns: List[CampaignBreakdown]
    sources: List[SourceBreakdown]
    daily_trends: List[DailyTrend]
    top_performers: TopPerformersResponse


# ============================================================================
# NEW SCHEMAS FOR TAB-BASED DASHBOARD
# ============================================================================

class SourceTabOverview(BaseModel):
    """Overview metrics for a specific source tab (surfside/facebook/vibe)."""
    source: str
    total_impressions: int
    total_clicks: int
    total_conversions: int
    total_revenue: Decimal
    total_spend: Decimal
    overall_ctr: Decimal
    overall_cpc: Decimal
    overall_cpa: Decimal
    overall_roas: Decimal


class DimensionSummary(BaseModel):
    """Summary metrics for a dimension (campaign/strategy/placement/creative)."""
    conversions: int
    clicks: int
    revenue: Decimal
    spend: Decimal


class DetailedBreakdown(BaseModel):
    """Detailed breakdown for individual entities (campaign/strategy/placement/creative)."""
    name: str
    impressions: int
    clicks: int
    conversions: int
    revenue: Decimal
    spend: Decimal
    ctr: Decimal
    cpc: Decimal
    cpa: Decimal
    roas: Decimal
