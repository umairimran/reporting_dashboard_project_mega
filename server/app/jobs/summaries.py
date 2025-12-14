"""
Weekly and monthly summary aggregation jobs.
"""
from datetime import date, timedelta
from app.core.database import SessionLocal
from app.core.logging import logger
from app.metrics.aggregator import AggregatorService


async def run_weekly_aggregation():
    """Run weekly summary aggregation for all clients."""
    db = SessionLocal()
    
    try:
        logger.info("=" * 60)
        logger.info("STARTING WEEKLY AGGREGATION")
        logger.info("=" * 60)
        
        # Calculate last complete week (Monday to Sunday)
        today = date.today()
        days_since_monday = today.weekday()
        last_monday = today - timedelta(days=days_since_monday + 7)
        
        logger.info(f"Aggregating week starting: {last_monday}")
        
        summaries = AggregatorService.aggregate_all_clients_week(db, last_monday)
        
        logger.info("=" * 60)
        logger.info(f"Weekly aggregation completed: {len(summaries)} summaries created")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Weekly aggregation failed: {str(e)}", exc_info=True)
    
    finally:
        db.close()


async def run_monthly_aggregation():
    """Run monthly summary aggregation for all clients."""
    db = SessionLocal()
    
    try:
        logger.info("=" * 60)
        logger.info("STARTING MONTHLY AGGREGATION")
        logger.info("=" * 60)
        
        # Calculate last complete month
        today = date.today()
        if today.month == 1:
            year = today.year - 1
            month = 12
        else:
            year = today.year
            month = today.month - 1
        
        logger.info(f"Aggregating month: {year}-{month:02d}")
        
        summaries = AggregatorService.aggregate_all_clients_month(db, year, month)
        
        logger.info("=" * 60)
        logger.info(f"Monthly aggregation completed: {len(summaries)} summaries created")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Monthly aggregation failed: {str(e)}", exc_info=True)
    
    finally:
        db.close()


async def run_all_aggregations():
    """Run all aggregation jobs (weekly and monthly)."""
    logger.info("=" * 60)
    logger.info("RUNNING ALL AGGREGATIONS")
    logger.info("=" * 60)
    
    await run_weekly_aggregation()
    await run_monthly_aggregation()
    
    logger.info("=" * 60)
    logger.info("ALL AGGREGATIONS COMPLETED")
    logger.info("=" * 60)
