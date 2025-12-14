"""
Dashboard module.
"""
from app.dashboard.schemas import (
    DashboardSummary,
    CampaignBreakdown,
    SourceBreakdown,
    DailyTrend,
    WeeklyComparison,
    MonthlyComparison,
    TopPerformer,
    TopPerformersResponse,
    ClientDashboard
)
from app.dashboard.service import DashboardService
from app.dashboard.router import router


__all__ = [
    'DashboardSummary',
    'CampaignBreakdown',
    'SourceBreakdown',
    'DailyTrend',
    'WeeklyComparison',
    'MonthlyComparison',
    'TopPerformer',
    'TopPerformersResponse',
    'ClientDashboard',
    'DashboardService',
    'router'
]
