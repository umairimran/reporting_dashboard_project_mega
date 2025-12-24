"""
Pydantic schemas for client management.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
import uuid


class ClientSettingsCreate(BaseModel):
    """Client settings creation schema."""
    source: str = Field(..., pattern="^(surfside|vibe|facebook)$", description="Data source")
    cpm: Decimal = Field(..., gt=0, description="CPM rate must be positive")
    currency: str = Field(default="USD", max_length=3)
    effective_date: Optional[datetime] = None


class ClientSettingsUpdate(BaseModel):
    """Client settings update schema."""
    source: str = Field(..., pattern="^(surfside|vibe|facebook)$", description="Data source")
    cpm: Decimal = Field(..., gt=0, description="CPM rate must be positive")
    effective_date: Optional[datetime] = None


class ClientSettingsResponse(BaseModel):
    """Client settings response schema."""
    id: uuid.UUID
    client_id: uuid.UUID
    source: str
    cpm: Decimal
    currency: str
    effective_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ClientCreate(BaseModel):
    """Client creation schema."""
    name: str = Field(..., min_length=1, max_length=255)
    user_id: uuid.UUID
    status: str = Field(default="active", pattern="^(active|disabled)$")


class ClientUpdate(BaseModel):
    """Client update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[str] = Field(None, pattern="^(active|disabled)$")


class ClientResponse(BaseModel):
    """Client response schema."""
    id: uuid.UUID
    name: str
    status: str
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ClientWithSettings(ClientResponse):
    """Client response with current CPM settings."""
    current_cpm: Optional[Decimal] = None
    current_currency: str = "USD"


class ClientListResponse(BaseModel):
    """Client list response schema."""
    total: int
    clients: List[ClientResponse]


class ClientCpmsResponse(BaseModel):
    """Response schema for latest CPMs."""
    surfside: Optional[ClientSettingsResponse] = None
    facebook: Optional[ClientSettingsResponse] = None

