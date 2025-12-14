"""
Pydantic schemas for campaign hierarchy.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid


# Campaign Schemas
class CampaignCreate(BaseModel):
    """Campaign creation schema."""
    name: str = Field(..., min_length=1, max_length=255)
    client_id: uuid.UUID
    source: str = Field(..., pattern="^(surfside|vibe|facebook)$")


class CampaignUpdate(BaseModel):
    """Campaign update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)


class CampaignResponse(BaseModel):
    """Campaign response schema."""
    id: uuid.UUID
    client_id: uuid.UUID
    name: str
    source: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Strategy Schemas
class StrategyCreate(BaseModel):
    """Strategy creation schema."""
    name: str = Field(..., min_length=1, max_length=255)
    campaign_id: uuid.UUID


class StrategyUpdate(BaseModel):
    """Strategy update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)


class StrategyResponse(BaseModel):
    """Strategy response schema."""
    id: uuid.UUID
    campaign_id: uuid.UUID
    name: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Placement Schemas
class PlacementCreate(BaseModel):
    """Placement creation schema."""
    name: str = Field(..., min_length=1, max_length=255)
    strategy_id: uuid.UUID


class PlacementUpdate(BaseModel):
    """Placement update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)


class PlacementResponse(BaseModel):
    """Placement response schema."""
    id: uuid.UUID
    strategy_id: uuid.UUID
    name: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Creative Schemas
class CreativeCreate(BaseModel):
    """Creative creation schema."""
    name: str = Field(..., min_length=1, max_length=255)
    placement_id: uuid.UUID
    preview_url: Optional[str] = None


class CreativeUpdate(BaseModel):
    """Creative update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    preview_url: Optional[str] = None


class CreativeResponse(BaseModel):
    """Creative response schema."""
    id: uuid.UUID
    placement_id: uuid.UUID
    name: str
    preview_url: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Nested Hierarchy Schema
class CreativeWithPlacement(CreativeResponse):
    """Creative with placement details."""
    placement: PlacementResponse


class PlacementWithStrategy(PlacementResponse):
    """Placement with strategy details."""
    strategy: StrategyResponse


class StrategyWithCampaign(StrategyResponse):
    """Strategy with campaign details."""
    campaign: CampaignResponse


class CampaignHierarchy(CampaignResponse):
    """Complete campaign hierarchy."""
    strategies: List[StrategyResponse] = []
