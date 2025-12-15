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
    Set up all scheduled jobs per documentation requirements.
    
    Jobs:
    - Daily data ingestion (all sources) - 3:30 AM Eastern
    - Weekly aggregation - Monday 5:00 AM Eastern
    - Monthly aggregation - 1st of month 5:00 AM Eastern
    """
    
    # === DAILY DATA INGESTION ===
    # Runs all data ingestions (Surfside + Vibe) in one job
    # Documentation: 3:00-4:00 AM Eastern (using 3:30 AM)
    scheduler.add_job(
        run_all_daily_ingestions,
        trigger='cron',
        hour=settings.DAILY_INGESTION_HOUR,
        minute=settings.DAILY_INGESTION_MINUTE,
        id='daily_data_ingestion',
        replace_existing=True,
        max_instances=1
    )
    logger.info(f"✓ Daily data ingestion scheduled at {settings.DAILY_INGESTION_HOUR}:{settings.DAILY_INGESTION_MINUTE:02d} Eastern")
    
    # === WEEKLY AGGREGATION ===
    # Runs every Monday at 5:00 AM to aggregate the previous week
    # Documentation: Monday at 5:00 AM Eastern
    scheduler.add_job(
        run_weekly_aggregation,
        trigger='cron',
        day_of_week='mon',
        hour=settings.WEEKLY_AGGREGATION_HOUR,
        minute=0,
        id='weekly_aggregation',
        replace_existing=True,
        max_instances=1
    )
    logger.info(f"✓ Weekly aggregation scheduled for Mondays at {settings.WEEKLY_AGGREGATION_HOUR:02d}:00 Eastern")
    
    # === MONTHLY AGGREGATION ===
    # Runs on the 1st of each month at 5:00 AM to aggregate the previous month
    # Documentation: 1st of month at 5:00 AM Eastern
    scheduler.add_job(
        run_monthly_aggregation,
        trigger='cron',
        day=1,
        hour=settings.MONTHLY_AGGREGATION_HOUR,
        minute=0,
        id='monthly_aggregation',
        replace_existing=True,
        max_instances=1
    )
    logger.info(f"✓ Monthly aggregation scheduled for 1st of month at {settings.MONTHLY_AGGREGATION_HOUR:02d}:00 Eastern")
    
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
