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
        
        db.commit()
        db.refresh(client)
        
        logger.info(f"Updated client: {client.name} (ID: {client.id})")
        return client
    
    @staticmethod
    def delete_client(db: Session, client_id: uuid.UUID) -> bool:
        """
        Delete a client (soft delete by setting status to disabled).
        
        Args:
            db: Database session
            client_id: Client UUID
            
        Returns:
            True if deleted, False if not found
        """
        client = db.query(Client).filter(Client.id == client_id).first()
        
        if not client:
            return False
        
        client.status = 'disabled'
        db.commit()
        
        logger.info(f"Disabled client: {client.name} (ID: {client.id})")
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
            cpm=settings_data.cpm,
            currency=settings_data.currency,
            effective_date=settings_data.effective_date or date.today()
        )
        
        db.add(settings)
        db.commit()
        db.refresh(settings)
        
        logger.info(f"Added CPM settings for client {client.name}: {settings.cpm} {settings.currency}")
        return settings
    
    @staticmethod
    def get_current_cpm(db: Session, client_id: uuid.UUID, target_date: date = None) -> Optional[ClientSettings]:
        """
        Get current CPM settings for a client on a specific date.
        
        Args:
            db: Database session
            client_id: Client UUID
            target_date: Date to get CPM for (defaults to today)
            
        Returns:
            Current CPM settings if found, None otherwise
        """
        if target_date is None:
            target_date = date.today()
        
        settings = db.query(ClientSettings).filter(
            ClientSettings.client_id == client_id,
            ClientSettings.effective_date <= target_date
        ).order_by(desc(ClientSettings.effective_date)).first()
        
        return settings
    
    @staticmethod
    def get_cpm_history(
        db: Session, 
        client_id: uuid.UUID
    ) -> List[ClientSettings]:
        """
        Get CPM history for a client.
        
        Args:
            db: Database session
            client_id: Client UUID
            
        Returns:
            List of CPM settings ordered by effective date
        """
        return db.query(ClientSettings).filter(
            ClientSettings.client_id == client_id
        ).order_by(desc(ClientSettings.effective_date)).all()
    
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
        
        current_settings = ClientService.get_current_cpm(db, client_id)
        
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
