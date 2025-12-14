"""
Main scheduler setup for all background jobs.
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.core.config import settings
from app.core.logging import logger
from app.jobs.daily_ingestion import run_all_daily_ingestions
from app.jobs.summaries import run_weekly_aggregation, run_monthly_aggregation


def setup_all_jobs(scheduler: AsyncIOScheduler):
    """
    Set up all scheduled jobs.
    
    Jobs:
    - Daily data ingestion (all sources) - 5:00 AM
    - Weekly aggregation - Sunday 7:00 AM
    - Monthly aggregation - 1st of month 8:00 AM
    """
    
    # === DAILY DATA INGESTION ===
    # Runs all data ingestions (Surfside + Vibe) in one job
    scheduler.add_job(
        run_all_daily_ingestions,
        trigger='cron',
        hour=settings.SURFSIDE_CRON_HOUR,  # 5 AM by default
        minute=0,
        id='daily_data_ingestion',
        replace_existing=True,
        max_instances=1
    )
    logger.info(f"✓ Daily data ingestion scheduled at {settings.SURFSIDE_CRON_HOUR}:00")
    
    # === WEEKLY AGGREGATION ===
    # Runs every Sunday at 7 AM to aggregate the previous week
    scheduler.add_job(
        run_weekly_aggregation,
        trigger='cron',
        day_of_week='sun',
        hour=7,
        minute=0,
        id='weekly_aggregation',
        replace_existing=True,
        max_instances=1
    )
    logger.info("✓ Weekly aggregation scheduled for Sundays at 07:00")
    
    # === MONTHLY AGGREGATION ===
    # Runs on the 1st of each month at 8 AM to aggregate the previous month
    scheduler.add_job(
        run_monthly_aggregation,
        trigger='cron',
        day=1,
        hour=8,
        minute=0,
        id='monthly_aggregation',
        replace_existing=True,
        max_instances=1
    )
    logger.info("✓ Monthly aggregation scheduled for 1st of month at 08:00")
    
    logger.info("=" * 60)
    logger.info("ALL SCHEDULED JOBS CONFIGURED")
    logger.info("=" * 60)


def get_scheduler_status(scheduler: AsyncIOScheduler) -> dict:
    """Get status of all scheduled jobs."""
    jobs = scheduler.get_jobs()
    
    return {
        "running": scheduler.running,
        "jobs_count": len(jobs),
        "jobs": [
            {
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            }
            for job in jobs
        ]
    }
