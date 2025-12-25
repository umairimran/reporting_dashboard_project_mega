"""
Client management business logic.
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import date, datetime
from app.clients.models import Client, ClientSettings
from app.clients.schemas import (
    ClientCreate, ClientUpdate, ClientSettingsCreate, 
    ClientSettingsUpdate, ClientWithSettings
)
from app.auth.models import User
from app.core.exceptions import ValidationError
from app.core.logging import logger
import uuid


class ClientService:
    """Service for client CRUD operations."""
    
    @staticmethod
    def create_client(db: Session, client_data: ClientCreate) -> Client:
        """
        Create a new client.
        
        Args:
            db: Database session
            client_data: Client creation data
            
        Returns:
            Created client
        """
        client = Client(
            name=client_data.name,
            user_id=client_data.user_id,
            status=client_data.status
        )
        
        db.add(client)
        db.commit()
        db.refresh(client)
        
        logger.info(f"Created client: {client.name} (ID: {client.id})")
        return client
    
    @staticmethod
    def get_client(db: Session, client_id: uuid.UUID) -> Optional[Client]:
        """
        Get client by ID.
        
        Args:
            db: Database session
            client_id: Client UUID
            
        Returns:
            Client if found, None otherwise
        """
        return db.query(Client).filter(Client.id == client_id).first()
    
    @staticmethod
    def get_all_clients(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[Client]:
        """
        Get all clients with optional filtering.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Optional status filter ('active' or 'disabled')
            
        Returns:
            List of clients
        """
        query = db.query(Client)
        
        if status:
            query = query.filter(Client.status == status)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update_client(
        db: Session, 
        client_id: uuid.UUID, 
        client_data: ClientUpdate
    ) -> Optional[Client]:
        """
        Update client details.
        
        Args:
            db: Database session
            client_id: Client UUID
            client_data: Update data
            
        Returns:
            Updated client if found, None otherwise
        """
        client = db.query(Client).filter(Client.id == client_id).first()
        
        if not client:
            return None
        
        if client_data.name is not None:
            client.name = client_data.name
        
        if client_data.status is not None:
            client.status = client_data.status
            
            # Sync user active status
            if client.user_id:
                user = db.query(User).filter(User.id == client.user_id).first()
                if user:
                    user.is_active = (client_data.status == 'active')
                    logger.info(f"Updated user {user.id} active status to {user.is_active} to match client {client.id}")
        
        db.commit()
        db.refresh(client)
        
        logger.info(f"Updated client: {client.name} (ID: {client.id})")
        return client
    
    @staticmethod
    def delete_client(db: Session, client_id: uuid.UUID) -> bool:
        """
        Delete a client and their associated user account.
        
        Args:
            db: Database session
            client_id: Client UUID
            
        Returns:
            True if deleted, False if not found
        """
        client = db.query(Client).filter(Client.id == client_id).first()
        
        if not client:
            return False
            
        user_id = client.user_id
        client_name = client.name

        # 1. Delete Client first 
        # This removes the Foreign Key constraint that blocks User deletion (ON DELETE RESTRICT)
        # It also triggers ON DELETE CASCADE for all client data (settings, campaigns, metrics, etc.)
        db.delete(client)
        
        # 2. Delete the associated User if it exists
        # We must flush/commit the client deletion first? 
        # Actually in SQLAlchemy session, order of operations matters. 
        # db.delete(client) issues the DELETE CLIENT SQL.
        # db.delete(user) issues the DELETE USER SQL.
        # Since we are in a transaction, the constraint checks happen at the end (or immediately depending on DB config).
        # Postgres constraints are usually immediate unless DEFERRABLE is set.
        # But logically, deleting client row removes the referencing row. So deleting user row after should be fine in same transaction.
        
        if user_id:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                db.delete(user)
                logger.info(f"Deleted associated user for client {client_name} (User ID: {user_id})")

        db.commit()
        
        logger.info(f"Deleted client: {client_name} (ID: {client_id}) and cleaned up all data.")
        return True
    
    @staticmethod
    def add_cpm_settings(
        db: Session, 
        client_id: uuid.UUID, 
        settings_data: ClientSettingsCreate
    ) -> ClientSettings:
        """
        Add new CPM settings for a client.
        
        Args:
            db: Database session
            client_id: Client UUID
            settings_data: CPM settings data
            
        Returns:
            Created settings
            
        Raises:
            ValidationError: If client not found
        """
        client = db.query(Client).filter(Client.id == client_id).first()
        
        if not client:
            raise ValidationError("Client not found")
        
        settings = ClientSettings(
            client_id=client_id,
            source=settings_data.source,
            cpm=settings_data.cpm,
            currency=settings_data.currency,
            effective_date=settings_data.effective_date or datetime.utcnow()
        )
        
        db.add(settings)
        db.commit()
        db.refresh(settings)
        
        logger.info(f"Added CPM settings for client {client.name} ({settings_data.source}): {settings.cpm} {settings.currency}")
        return settings
    
    @staticmethod
    def get_current_cpm(db: Session, client_id: uuid.UUID, source: str, target_datetime: datetime = None) -> Optional[ClientSettings]:
        """
        Get current CPM settings for a client on a specific datetime and source.
        
        Args:
            db: Database session
            client_id: Client UUID
            source: Data source ('surfside', 'vibe', or 'facebook')
            target_datetime: Datetime to get CPM for (defaults to now)
            
        Returns:
            Current CPM settings if found, None otherwise
        """
        if target_datetime is None:
            target_datetime = datetime.utcnow()
        
        settings = db.query(ClientSettings).filter(
            ClientSettings.client_id == client_id,
            ClientSettings.source == source,
            ClientSettings.effective_date <= target_datetime
        ).order_by(desc(ClientSettings.effective_date)).first()
        
        return settings
    
    @staticmethod
    def get_cpm_history(
        db: Session, 
        client_id: uuid.UUID,
        source: Optional[str] = None
    ) -> List[ClientSettings]:
        """
        Get CPM history for a client.
        
        Args:
            db: Database session
            client_id: Client UUID
            source: Optional source filter ('surfside', 'vibe', or 'facebook')
            
        Returns:
            List of CPM settings ordered by source and effective date
        """
        query = db.query(ClientSettings).filter(
            ClientSettings.client_id == client_id
        )
        
        if source:
            query = query.filter(ClientSettings.source == source)
        
        return query.order_by(ClientSettings.source, desc(ClientSettings.effective_date)).all()
    
    @staticmethod
    def update_cpm_settings(
        db: Session,
        client_id: uuid.UUID,
        settings_data: ClientSettingsUpdate
    ) -> ClientSettings:
        """
        Update CPM settings for a client and source.
        
        Args:
            db: Database session
            client_id: Client UUID
            settings_data: CPM update data (includes source)
            
        Returns:
            Updated or created settings
            
        Raises:
            ValidationError: If client not found
        """
        client = db.query(Client).filter(Client.id == client_id).first()
        
        if not client:
            raise ValidationError("Client not found")
        
        # Get the most recent setting for this client and source
        current_settings = db.query(ClientSettings).filter(
            ClientSettings.client_id == client_id,
            ClientSettings.source == settings_data.source
        ).order_by(desc(ClientSettings.effective_date)).first()
        
        effective_datetime = settings_data.effective_date or datetime.utcnow()
        
        # Always create new settings entry with current timestamp (allows multiple updates per day)
        new_settings = ClientSettings(
            client_id=client_id,
            source=settings_data.source,
            cpm=settings_data.cpm,
            currency=current_settings.currency if current_settings else "USD",
            effective_date=effective_datetime
        )
        db.add(new_settings)
        db.commit()
        db.refresh(new_settings)
        logger.info(f"Created new CPM for client {client.name} ({settings_data.source}): {new_settings.cpm} (effective: {effective_datetime})")
        return new_settings
    
    @staticmethod
    def get_client_with_cpm(
        db: Session, 
        client_id: uuid.UUID
    ) -> Optional[ClientWithSettings]:
        """
        Get client with current CPM settings.
        
        Args:
            db: Database session
            client_id: Client UUID
            
        Returns:
            Client with current CPM if found, None otherwise
        """
        client = db.query(Client).filter(Client.id == client_id).first()
        
        if not client:
            return None
        
        # For backward compatibility, get surfside CPM as default
        current_settings = ClientService.get_current_cpm(db, client_id, 'surfside')
        
        client_dict = {
            "id": client.id,
            "name": client.name,
            "status": client.status,
            "user_id": client.user_id,
            "created_at": client.created_at,
            "updated_at": client.updated_at,
            "current_cpm": current_settings.cpm if current_settings else None,
            "current_currency": current_settings.currency if current_settings else "USD"
        }
        
        return ClientWithSettings(**client_dict)

    @staticmethod
    def get_latest_cpms(
        db: Session,
        client_id: uuid.UUID
    ) -> dict:
        """
        Get latest CPM settings for a client for all sources.
        
        Args:
            db: Database session
            client_id: Client UUID
            
        Returns:
            Dictionary with source as key and settings object as value
        """
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            return {"surfside": None, "facebook": None}

        surfside = ClientService.get_current_cpm(db, client_id, "surfside")
        facebook = ClientService.get_current_cpm(db, client_id, "facebook")

        return {
            "surfside": surfside,
            "facebook": facebook
        }
