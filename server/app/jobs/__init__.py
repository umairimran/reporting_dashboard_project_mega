"""
Scheduled jobs module.
"""
from app.jobs.daily_ingestion import run_all_daily_ingestions
from app.jobs.summaries import (
    run_weekly_aggregation,
    run_monthly_aggregation,
    run_all_aggregations
)
from app.jobs.scheduler import setup_all_jobs, get_scheduler_status


__all__ = [
    'run_all_daily_ingestions',
    'run_weekly_aggregation',
    'run_monthly_aggregation',
    'run_all_aggregations',
    'setup_all_jobs',
    'get_scheduler_status'
]
