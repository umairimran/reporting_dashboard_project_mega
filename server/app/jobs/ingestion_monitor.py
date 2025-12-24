"""
Background job to monitor and process pending ingestion logs.
"""
from app.core.database import SessionLocal
from app.metrics.models import IngestionLog
from app.facebook.models import UploadedFile
from app.clients.models import Client
from app.auth.models import User
from app.core.logging import logger
from app.facebook.upload_handler import process_facebook_upload_background
from app.surfside.upload_handler import process_surfside_upload_background
import asyncio

async def check_pending_uploads():
    """
    Check for pending ingestion logs and trigger processing.
    """
    db = SessionLocal()
    try:
        # Find logs that are 'processing' but not finished
        # We might want a check to ensure we don't pick up 'stale' logs or logs that are actually running?
        # Since this job runs sequentially (max_instances=1), we can just process them.
        # But if the server was restarted, old 'processing' logs will be picked up. This is DESIRED behavior (recovery).
        
        pending_logs = db.query(IngestionLog).filter(
            IngestionLog.status == 'processing',
            IngestionLog.finished_at.is_(None)
        ).all()
        
        if not pending_logs:
            return

        # Get admin emails for alerts
        admin_users = db.query(User).filter(
            User.role == 'admin',
            User.is_active == True
        ).all()
        admin_emails = [user.email for user in admin_users]
        
        for log in pending_logs:
            logger.info(f"Monitor found pending ingestion: {log.id} ({log.source})")
            
            # Find associated uploaded file to get path
            # We match on file_name and client_id because that's the link we have
            uploaded_file = db.query(UploadedFile).filter(
                UploadedFile.file_name == log.file_name,
                UploadedFile.client_id == log.client_id
            ).order_by(UploadedFile.created_at.desc()).first()
            
            if not uploaded_file:
                logger.error(f"Could not find uploaded file record for log {log.id}")
                log.status = 'failed'
                log.message = 'Source file record not found'
                log.finished_at = log.created_at
                db.commit()
                continue
                
            # Get Client Name
            client = db.query(Client).filter(Client.id == log.client_id).first()
            client_name = client.name if client else "Unknown Client"
            
            try:
                if log.source == 'facebook':
                    await process_facebook_upload_background(
                        upload_id=uploaded_file.id,
                        file_path=uploaded_file.file_path,
                        file_name=log.file_name,
                        client_id=log.client_id,
                        client_name=client_name,
                        ingestion_log_id=log.id,
                        admin_emails=admin_emails
                    )
                elif log.source == 'surfside':
                    await process_surfside_upload_background(
                        upload_id=uploaded_file.id,
                        file_path=uploaded_file.file_path,
                        file_name=log.file_name,
                        client_id=log.client_id,
                        client_name=client_name,
                        ingestion_log_id=log.id,
                        admin_emails=admin_emails
                    )
            except Exception as e:
                logger.error(f"Monitor failed to process log {log.id}: {str(e)}")
                # The process_..._background functions handle their own error logging/db updates usually,
                # but if they crash completely, we catch it here.
                
    except Exception as e:
        logger.error(f"Error in upload monitor: {str(e)}")
    finally:
        db.close()
