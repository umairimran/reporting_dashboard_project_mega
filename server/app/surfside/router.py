"""
Surfside upload API endpoints.
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Query
from sqlalchemy.orm import Session
import uuid
from typing import List
from app.core.database import get_db
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.surfside.upload_handler import SurfsideUploadHandler
from app.facebook.models import UploadedFile
from app.clients.models import Client
from pydantic import BaseModel
from datetime import datetime


router = APIRouter(prefix="/surfside", tags=["Surfside"])


class UploadResponse(BaseModel):
    """Response model for file upload."""
    upload_id: uuid.UUID
    file_name: str
    status: str
    records_count: int | None
    created_at: datetime
    processed_at: datetime | None
    error_message: str | None


class UploadHistoryResponse(BaseModel):
    """Response model for upload history."""
    uploads: List[UploadResponse]
    total: int


@router.post("/upload", response_model=UploadResponse)
async def upload_surfside_file(
    client_id: uuid.UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload Surfside data file for a client.
    
    - **client_id**: ID of the client
    - **file**: CSV or XLSX file with Surfside data
    
    File must contain columns: Date, Campaign, Strategy, Placement, Creative,
    Impressions, Clicks, Conversions, Conversion Revenue
    """
    # Get client
    client = db.query(Client).filter(Client.id == client_id).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client not found: {client_id}"
        )
    
    # Check permissions - only admins or the client's own user can upload
    if current_user.role != 'admin' and current_user.client_id != client_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to upload files for this client"
        )
    
    # Get admin emails for alerts
    admin_users = db.query(User).filter(
        User.role == 'admin',
        User.is_active == True
    ).all()
    admin_emails = [user.email for user in admin_users]
    
    # Process upload
    handler = SurfsideUploadHandler(db)
    uploaded_file = await handler.process_upload(
        file=file,
        client_id=client_id,
        client_name=client.name,
        user_id=current_user.id,
        admin_emails=admin_emails
    )
    
    return UploadResponse(
        upload_id=uploaded_file.id,
        file_name=uploaded_file.file_name,
        status=uploaded_file.upload_status,
        records_count=uploaded_file.records_count,
        created_at=uploaded_file.created_at,
        processed_at=uploaded_file.processed_at,
        error_message=uploaded_file.error_message
    )


@router.get("/uploads/{client_id}", response_model=UploadHistoryResponse)
async def get_upload_history(
    client_id: uuid.UUID,
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get upload history for a client.
    
    - **client_id**: ID of the client
    - **limit**: Maximum number of records to return (default 50, max 100)
    """
    # Check permissions
    if current_user.role != 'admin' and current_user.client_id != client_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view uploads for this client"
        )
    
    handler = SurfsideUploadHandler(db)
    uploads = handler.get_upload_history(client_id, limit)
    
    upload_responses = [
        UploadResponse(
            upload_id=upload.id,
            file_name=upload.file_name,
            status=upload.upload_status,
            records_count=upload.records_count,
            created_at=upload.created_at,
            processed_at=upload.processed_at,
            error_message=upload.error_message
        )
        for upload in uploads
    ]
    
    return UploadHistoryResponse(
        uploads=upload_responses,
        total=len(upload_responses)
    )


@router.get("/upload/{upload_id}", response_model=UploadResponse)
async def get_upload_details(
    upload_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get details of a specific upload.
    
    - **upload_id**: ID of the upload
    """
    handler = SurfsideUploadHandler(db)
    upload = handler.get_upload_by_id(upload_id)
    
    if not upload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Upload not found: {upload_id}"
        )
    
    # Check permissions
    if current_user.role != 'admin' and current_user.client_id != upload.client_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this upload"
        )
    
    return UploadResponse(
        upload_id=upload.id,
        file_name=upload.file_name,
        status=upload.upload_status,
        records_count=upload.records_count,
        created_at=upload.created_at,
        processed_at=upload.processed_at,
        error_message=upload.error_message
    )
