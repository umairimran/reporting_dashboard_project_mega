"""
Scheduled job for daily Vibe data ingestion.
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import date, timedelta
from app.core.database import SessionLocal
from app.core.config import settings
from app.core.logging import logger
from app.clients.models import Client
from app.auth.models import User
from app.vibe.etl import VibeETL
from app.vibe.models import VibeCredentials


async def run_daily_vibe_ingestion():
    """Daily job to ingest Vibe data for all clients with credentials."""
    db = SessionLocal()
    
    try:
        logger.info("=" * 50)
        logger.info("Starting daily Vibe ingestion job")
        logger.info("=" * 50)
        
        # Target date is yesterday
        target_date = date.today() - timedelta(days=1)
        logger.info(f"Target date: {target_date}")
        
        # Get all active clients with Vibe credentials
        clients_with_vibe = db.query(Client).join(VibeCredentials).filter(
            Client.status == 'active',
            VibeCredentials.is_active == True
        ).all()
        
        # Get admin emails for alerts
        admin_users = db.query(User).filter(
            User.role == 'admin',
            User.is_active == True
        ).all()
        admin_emails = [user.email for user in admin_users]
        
        logger.info(f"Found {len(clients_with_vibe)} clients with active Vibe credentials")
        
        # Process each client
        success_count = 0
        failure_count = 0
        
        for client in clients_with_vibe:
            try:
                logger.info(f"Processing Vibe data for client: {client.name}")
                
                etl = VibeETL(db)
                await etl.run_for_client(
                    client_id=client.id,
                    client_name=client.name,
                    start_date=target_date,
                    end_date=target_date,
                    admin_emails=admin_emails
                )
                
                success_count += 1
                logger.info(f"✓ Successfully processed {client.name}")
                
            except Exception as e:
                failure_count += 1
                logger.error(f"✗ Failed to process {client.name}: {str(e)}")
        
        logger.info("=" * 50)
        logger.info(f"Daily Vibe ingestion completed")
        logger.info(f"Success: {success_count}, Failed: {failure_count}")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"Critical error in daily Vibe ingestion: {str(e)}", exc_info=True)
    
    finally:
        db.close()


def setup_vibe_scheduler(scheduler: AsyncIOScheduler):
    """Set up Vibe scheduled jobs."""
    scheduler.add_job(
        run_daily_vibe_ingestion,
        trigger='cron',
        hour=settings.VIBE_CRON_HOUR,
        minute=0,
        id='vibe_daily_ingestion',
        replace_existing=True
    )
    
    logger.info(f"✓ Vibe scheduler configured - runs daily at {settings.VIBE_CRON_HOUR}:00")
