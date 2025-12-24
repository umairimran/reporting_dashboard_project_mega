"""
Client management API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from app.core.database import get_db
from app.auth.dependencies import require_admin, get_current_user
from app.auth.models import User
from app.clients.models import Client
from app.clients.schemas import (
    ClientCreate, ClientUpdate, ClientResponse, ClientListResponse,
    ClientSettingsCreate, ClientSettingsUpdate, ClientSettingsResponse,
    ClientWithSettings, ClientCpmsResponse
)
from app.clients.service import ClientService

router = APIRouter(prefix="/clients", tags=["Clients"])


@router.post("", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    client_data: ClientCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Create a new client (admin only).
    
    Args:
        client_data: Client creation data
        db: Database session
        admin: Current admin user
        
    Returns:
        Created client
    """
    client = ClientService.create_client(db, client_data)
    return client


@router.get("", response_model=ClientListResponse)
async def get_clients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None, pattern="^(active|disabled)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all clients with pagination.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        status: Optional status filter
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List of clients
    """
    clients = ClientService.get_all_clients(db, skip, limit, status)
    total = db.query(Client).count()
    
    return {"total": total, "clients": clients}


@router.get("/id-by-name-and-user")
async def get_client_id_by_name_and_user(
    name: str = Query(..., description="Client name"),
    user_id: uuid.UUID = Query(..., description="User ID associated with the client"),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get client ID by name and user ID (admin only).
    
    Args:
        name: Client name
        user_id: User ID associated with the client
        admin: Current admin user
        db: Database session
        
    Returns:
        Client ID, name, user_id, and status
        
    Raises:
        HTTPException: If client not found
    """
    client = db.query(Client).filter(
        Client.name == name,
        Client.user_id == user_id
    ).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with name '{name}' and user_id '{user_id}' not found"
        )
    
    return {
        "id": str(client.id),
        "name": client.name,
        "user_id": str(client.user_id),
        "status": client.status
    }


@router.get("/{client_id}", response_model=ClientWithSettings)
async def get_client(
    client_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get client by ID with current CPM.
    
    Args:
        client_id: Client UUID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Client with current CPM
        
    Raises:
        HTTPException: If client not found
    """
    client = ClientService.get_client_with_cpm(db, client_id)
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    return client


@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: uuid.UUID,
    client_data: ClientUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Update client details (admin only).
    
    Args:
        client_id: Client UUID
        client_data: Update data
        db: Database session
        admin: Current admin user
        
    Returns:
        Updated client
        
    Raises:
        HTTPException: If client not found
    """
    client = ClientService.update_client(db, client_id, client_data)
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    return client


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Disable a client (admin only).
    
    Args:
        client_id: Client UUID
        db: Database session
        admin: Current admin user
        
    Raises:
        HTTPException: If client not found
    """
    success = ClientService.delete_client(db, client_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )


@router.post("/{client_id}/cpm", response_model=ClientSettingsResponse, status_code=status.HTTP_201_CREATED)
async def add_cpm_settings(
    client_id: uuid.UUID,
    settings_data: ClientSettingsCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Add new CPM settings for a client (admin only).
    
    Args:
        client_id: Client UUID
        settings_data: CPM settings data
        db: Database session
        admin: Current admin user
        
    Returns:
        Created CPM settings
        
    Raises:
        HTTPException: If client not found
    """
    try:
        settings = ClientService.add_cpm_settings(db, client_id, settings_data)
        return settings
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{client_id}/cpm/history", response_model=List[ClientSettingsResponse])
async def get_cpm_history(
    client_id: uuid.UUID,
    source: Optional[str] = Query(None, pattern="^(surfside|vibe|facebook)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get CPM history for a client.
    
    Args:
        client_id: Client UUID
        source: Optional source filter
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List of CPM settings
    """
    history = ClientService.get_cpm_history(db, client_id, source)
    return history


@router.put("/{client_id}/cpm", response_model=ClientSettingsResponse)
async def update_cpm_settings(
    client_id: uuid.UUID,
    settings_data: ClientSettingsUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Update CPM settings for a client and source (admin only).
    
    This endpoint updates the CPM for a specific client and source.
    If a setting with the same effective_date exists, it will be updated.
    Otherwise, a new setting entry will be created.
    
    Args:
        client_id: Client UUID
        settings_data: CPM update data (must include source)
        db: Database session
        admin: Current admin user
        
    Returns:
        Updated or created CPM settings
        
    Raises:
        HTTPException: If client not found
    """
    try:
        settings = ClientService.update_cpm_settings(db, client_id, settings_data)
        return settings
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{client_id}/cpm/latest", response_model=ClientCpmsResponse)
async def get_latest_cpms(
    client_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get latest CPM settings for both Surfside and Facebook.
    
    Args:
        client_id: Client UUID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Object containing latest settings for each source
    """
    return ClientService.get_latest_cpms(db, client_id)

