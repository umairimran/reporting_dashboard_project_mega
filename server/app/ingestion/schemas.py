"""
Pydantic schemas for ingestion logs.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
import uuid


class IngestionLogResponse(BaseModel):
    """Ingestion log response schema."""
    id: uuid.UUID
    run_date: date
    status: str
    message: Optional[str]
    records_loaded: int
    records_failed: int
    started_at: datetime
    finished_at: Optional[datetime]
    file_name: Optional[str]
    source: str
    client_id: Optional[uuid.UUID]
    resolution_status: Optional[str]
    resolution_notes: Optional[str]
    resolved_at: Optional[datetime]
    resolved_by: Optional[uuid.UUID]
    created_at: datetime
    
    class Config:
        from_attributes = True


class IngestionLogListResponse(BaseModel):
    """Ingestion logs list response schema."""
    total: int
    logs: list[IngestionLogResponse]


class IngestionLogResolution(BaseModel):
    """Schema for resolving ingestion log errors."""
    resolution_status: str = Field(..., pattern="^(resolved|ignored)$")
    resolution_notes: Optional[str] = None
