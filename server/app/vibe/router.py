"""
Vibe API router for credentials and ingestion control.
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
import uuid
from typing import List, Optional
from datetime import date, timedelta

from app.core.database import get_db
from app.auth.dependencies import require_admin
from app.auth.models import User
from app.vibe.schemas import VibeCredentialsCreate, VibeCredentialsResponse, VibeIngestionResponse, VibeAdvertiser, VibeAppList
from app.vibe.api_client import VibeAPIClient
from app.vibe.service import VibeService
from app.vibe.etl import VibeETL
from app.clients.models import Client

router = APIRouter(prefix="/vibe", tags=["Vibe"])


@router.post("/credentials/{client_id}", response_model=VibeCredentialsResponse)
async def configure_vibe_credentials(
    client_id: uuid.UUID,
    creds_data: VibeCredentialsCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Configure Vibe API credentials for a client (Admin only).
    """
    # Check if client exists
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # Create credentials
    creds = VibeService.create_credentials(
        db=db,
        client_id=client_id,
        api_key=creds_data.api_key,
        advertiser_id=creds_data.advertiser_id
    )
    return creds


@router.get("/credentials/{client_id}", response_model=VibeCredentialsResponse)
async def get_vibe_credentials(
    client_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Get Vibe credentials for a client.
    """
    creds = VibeService.get_credentials(db, client_id)
    if not creds:
        raise HTTPException(status_code=404, detail="Vibe credentials not found for this client")
    return creds


@router.post("/ingest/{client_id}", response_model=VibeIngestionResponse)
async def trigger_client_ingestion(
    client_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    target_date: Optional[date] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Trigger manual Vibe ingestion for a specific client.
    Runs in background unless 'background_tasks' is removed (which we won't do for API responsiveness).
    """
    # Check client and credentials
    creds = VibeService.get_credentials(db, client_id)
    if not creds:
        raise HTTPException(status_code=400, detail="Client has no active Vibe credentials")

    client = db.query(Client).filter(Client.id == client_id).first()
    
    # Default date to yesterday if not provided
    if not target_date:
        target_date = date.today() - timedelta(days=1)
    
    # Vibe API requires start_date < end_date, so we use a date range
    start_date = target_date
    end_date = target_date + timedelta(days=1)  # Next day to create a valid range

    # Get admin emails
    admin_users = db.query(User).filter(User.role == 'admin', User.is_active == True).all()
    admin_emails = [user.email for user in admin_users]

    # Instantiate ETL
    etl = VibeETL(db)
    
    try:
        # Run ETL synchronously for immediate feedback in testing
        ingestion_log = await etl.run_for_client(
            client_id=client_id,
            client_name=client.name,
            start_date=start_date,
            end_date=end_date,
            admin_emails=admin_emails
        )
        
        return VibeIngestionResponse(
            status="success",
            client_id=client_id,
            message=f"Successfully ingested Vibe data for {start_date.strftime('%Y-%m-%d')}",
            records_processed=ingestion_log.records_loaded if ingestion_log else 0
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/utils/advertisers", response_model=List[VibeAdvertiser])
async def list_vibe_advertisers(
    api_key: str,
    admin: User = Depends(require_admin)
):
    """
    Utility: Fetch available advertisers using a raw API key.
    Useful for looking up IDs before configuring credentials.
    """
    client = VibeAPIClient(api_key=api_key)
    try:
        advertisers_data = await client.get_advertiser_ids()
        # Convert to VibeAdvertiser objects
        return [
            VibeAdvertiser(
                advertiser_id=adv.get('advertiser_id'),
                advertiser_name=adv.get('advertiser_name', 'Unknown')
            )
            for adv in advertisers_data
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await client.close()


@router.get("/utils/apps", response_model=VibeAppList)
async def list_vibe_apps(
    api_key: str,
    advertiser_id: str,
    admin: User = Depends(require_admin)
):
    """
    Utility: Fetch available App IDs for a specific advertiser.
    """
    client = VibeAPIClient(api_key=api_key, advertiser_id=advertiser_id)
    try:
        app_ids = await client.get_app_ids(advertiser_id)
        return {"app_ids": app_ids}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await client.close()
