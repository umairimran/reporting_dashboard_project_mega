"""
Daily data ingestion jobs for all sources.
"""
from datetime import date, timedelta
from app.core.database import SessionLocal
from app.core.config import settings
from app.core.logging import logger
from app.clients.models import Client
from app.auth.models import User
from app.surfside.etl import SurfsideETL
from app.vibe.etl import VibeETL
from app.vibe.models import VibeCredentials


async def run_all_daily_ingestions():
    """
    Run daily data ingestion for all sources (Surfside, Vibe).
    Facebook is manual upload only.
    """
    db = SessionLocal()
    
    try:
        logger.info("=" * 60)
        logger.info("STARTING ALL DAILY DATA INGESTIONS")
        logger.info("=" * 60)
        
        # Target date is yesterday
        target_date = date.today() - timedelta(days=1)
        logger.info(f"Target date: {target_date}")
        
        # Get admin emails for alerts
        admin_users = db.query(User).filter(
            User.role == 'admin',
            User.is_active == True
        ).all()
        admin_emails = [user.email for user in admin_users]
        
        logger.info(f"Admin emails for alerts: {admin_emails}")
        
        # === SURFSIDE INGESTION ===
        logger.info("\n" + "=" * 60)
        logger.info("SURFSIDE DATA INGESTION")
        logger.info("=" * 60)
        
        surfside_clients = db.query(Client).filter(
            Client.status == 'active',
            Client.surfside_s3_prefix.isnot(None)
        ).all()
        
        logger.info(f"Found {len(surfside_clients)} clients with Surfside enabled")
        
        surfside_success = 0
        surfside_failed = 0
        
        for client in surfside_clients:
            try:
                logger.info(f"Processing Surfside for: {client.name}")
                
                etl = SurfsideETL(db)
                await etl.run_for_client(
                    client_id=client.id,
                    client_name=client.name,
                    target_date=target_date,
                    admin_emails=admin_emails
                )
                
                surfside_success += 1
                logger.info(f"✓ Surfside successful for {client.name}")
                
            except Exception as e:
                surfside_failed += 1
                logger.error(f"✗ Surfside failed for {client.name}: {str(e)}")
        
        logger.info(f"Surfside complete: {surfside_success} success, {surfside_failed} failed")
        
        # === VIBE INGESTION ===
        logger.info("\n" + "=" * 60)
        logger.info("VIBE DATA INGESTION")
        logger.info("=" * 60)
        
        vibe_clients = db.query(Client).join(VibeCredentials).filter(
            Client.status == 'active',
            VibeCredentials.is_active == True
        ).all()
        
        logger.info(f"Found {len(vibe_clients)} clients with Vibe enabled")
        
        vibe_success = 0
        vibe_failed = 0
        
        for client in vibe_clients:
            try:
                logger.info(f"Processing Vibe for: {client.name}")
                
                etl = VibeETL(db)
                await etl.run_for_client(
                    client_id=client.id,
                    client_name=client.name,
                    start_date=target_date,
                    end_date=target_date,
                    admin_emails=admin_emails
                )
                
                vibe_success += 1
                logger.info(f"✓ Vibe successful for {client.name}")
                
            except Exception as e:
                vibe_failed += 1
                logger.error(f"✗ Vibe failed for {client.name}: {str(e)}")
        
        logger.info(f"Vibe complete: {vibe_success} success, {vibe_failed} failed")
        
        # === SUMMARY ===
        logger.info("\n" + "=" * 60)
        logger.info("DAILY INGESTION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Surfside: {surfside_success} success, {surfside_failed} failed")
        logger.info(f"Vibe: {vibe_success} success, {vibe_failed} failed")
        logger.info(f"Total: {surfside_success + vibe_success} success, {surfside_failed + vibe_failed} failed")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Critical error in daily ingestion: {str(e)}", exc_info=True)
    
    finally:
        db.close()
