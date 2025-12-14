"""
Scheduled job for daily Surfside data ingestion.
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session
from typing import List
from datetime import date, timedelta
from app.core.database import SessionLocal
from app.core.config import settings
from app.core.logging import logger
from app.clients.models import Client
from app.auth.models import User
from app.surfside.etl import SurfsideETL


async def run_daily_surfside_ingestion():
    """
    Daily job to ingest Surfside data for all active clients.
    Runs at configured hour (default: 5 AM).
    """
    db = SessionLocal()
    
    try:
        logger.info("Starting daily Surfside ingestion job")
        
        # Get yesterday's date (data is typically available next day)
        target_date = date.today() - timedelta(days=1)
        
        # Get all active clients
        clients = db.query(Client).filter(Client.status == 'active').all()
        
        # Get admin emails for alerts
        admin_users = db.query(User).filter(User.role == 'admin', User.is_active == True).all()
        admin_emails = [user.email for user in admin_users]
        
        logger.info(f"Processing Surfside data for {len(clients)} clients for date {target_date}")
        
        success_count = 0
        failure_count = 0
        
        for client in clients:
            try:
                etl = SurfsideETL(db)
                await etl.run_for_client(
                    client_id=client.id,
                    client_name=client.name,
                    target_date=target_date,
                    client_prefix=f"{client.name.lower().replace(' ', '_')}/",
                    admin_emails=admin_emails
                )
                success_count += 1
                
            except Exception as e:
                logger.error(f"Failed to process Surfside data for {client.name}: {str(e)}")
                failure_count += 1
        
        logger.info(f"Daily Surfside ingestion completed: {success_count} success, {failure_count} failures")
        
    except Exception as e:
        logger.error(f"Daily Surfside ingestion job failed: {str(e)}")
    finally:
        db.close()


def setup_surfside_scheduler(scheduler: AsyncIOScheduler):
    """
    Set up Surfside scheduled jobs.
    
    Args:
        scheduler: APScheduler instance
    """
    # Daily ingestion at configured hour
    scheduler.add_job(
        run_daily_surfside_ingestion,
        trigger='cron',
        hour=settings.SURFSIDE_CRON_HOUR,
        minute=0,
        id='surfside_daily_ingestion',
        name='Surfside Daily Ingestion',
        replace_existing=True
    )
    
    logger.info(f"Surfside scheduler set up - will run daily at {settings.SURFSIDE_CRON_HOUR}:00")
