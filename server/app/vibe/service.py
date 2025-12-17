"""
Vibe service with client-specific credential management.
"""
from sqlalchemy.orm import Session
from typing import Optional
import uuid
from app.vibe.models import VibeCredentials, VibeReportRequest
from app.vibe.api_client import VibeAPIClient
from app.core.logging import logger
from app.core.exceptions import VibeAPIError
from app.core.encryption import encrypt_api_key


class VibeService:
    """Service for managing Vibe API interactions with client-specific credentials."""
    
    @staticmethod
    def get_credentials(db: Session, client_id: uuid.UUID) -> Optional[VibeCredentials]:
        """Get active Vibe credentials for a client."""
        return db.query(VibeCredentials).filter(
            VibeCredentials.client_id == client_id,
            VibeCredentials.is_active == True
        ).first()
    
    @staticmethod
    def get_api_client(db: Session, client_id: uuid.UUID) -> VibeAPIClient:
        """Get configured API client for a client."""
        creds = VibeService.get_credentials(db, client_id)
        
        if not creds:
            raise VibeAPIError(f"No active Vibe credentials for client {client_id}")
        
        return VibeAPIClient(
            api_key=creds.decrypted_api_key,  # Use decrypted key
            advertiser_id=creds.advertiser_id
        )
    
    @staticmethod
    def create_credentials(
        db: Session,
        client_id: uuid.UUID,
        api_key: str,
        advertiser_id: str
    ) -> VibeCredentials:
        """Create new Vibe credentials for a client."""
        # Deactivate existing credentials
        existing = db.query(VibeCredentials).filter(
            VibeCredentials.client_id == client_id
        ).all()
        
        for cred in existing:
            cred.is_active = False
        
        # Create new credentials with encrypted API key
        new_creds = VibeCredentials(
            client_id=client_id,
            api_key=encrypt_api_key(api_key),  # Encrypt before saving
            advertiser_id=advertiser_id,
            is_active=True
        )
        
        db.add(new_creds)
        db.commit()
        db.refresh(new_creds)
        
        logger.info(f"Created Vibe credentials for client {client_id}")
        return new_creds
    
    @staticmethod
    def update_credentials(
        db: Session,
        credential_id: uuid.UUID,
        api_key: Optional[str] = None,
        advertiser_id: Optional[str] = None
    ) -> VibeCredentials:
        """Update existing Vibe credentials."""
        creds = db.query(VibeCredentials).filter(
            VibeCredentials.id == credential_id
        ).first()
        
        if not creds:
            raise VibeAPIError(f"Credentials {credential_id} not found")
        
        if api_key:
            creds.api_key = encrypt_api_key(api_key)  # Encrypt before saving
        if advertiser_id:
            creds.advertiser_id = advertiser_id
        
        db.commit()
        db.refresh(creds)
        
        logger.info(f"Updated Vibe credentials {credential_id}")
        return creds
