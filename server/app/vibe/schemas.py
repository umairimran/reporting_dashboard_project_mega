"""
Vibe API schemas.
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid


class VibeCredentialsBase(BaseModel):
    api_key: str
    advertiser_id: Optional[str] = None


class VibeCredentialsCreate(VibeCredentialsBase):
    pass


class VibeCredentialsResponse(VibeCredentialsBase):
    id: uuid.UUID
    client_id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True



class VibeIngestionResponse(BaseModel):
    status: str
    client_id: Optional[uuid.UUID] = None
    message: str
    records_processed: Optional[int] = 0


class VibeAdvertiser(BaseModel):
    advertiser_id: uuid.UUID
    advertiser_name: str


class VibeAppList(BaseModel):
    app_ids: list[str]

