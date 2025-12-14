"""
Campaign hierarchy API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from app.core.database import get_db
from app.auth.dependencies import get_current_user, require_admin
from app.auth.models import User
from app.campaigns.schemas import (
    CampaignCreate, CampaignUpdate, CampaignResponse,
    StrategyCreate, StrategyUpdate, StrategyResponse,
    PlacementCreate, PlacementUpdate, PlacementResponse,
    CreativeCreate, CreativeUpdate, CreativeResponse
)
from app.campaigns.service import CampaignService

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])


# Campaign Endpoints
@router.post("", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign_data: CampaignCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new campaign."""
    campaign = CampaignService.find_or_create_campaign(
        db,
        campaign_data.client_id,
        campaign_data.name,
        campaign_data.source
    )
    db.commit()
    return campaign


@router.get("", response_model=List[CampaignResponse])
async def get_campaigns(
    client_id: uuid.UUID = Query(...),
    source: Optional[str] = Query(None, pattern="^(surfside|vibe|facebook)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all campaigns for a client."""
    campaigns = CampaignService.get_campaigns_by_client(db, client_id, source)
    return campaigns


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get campaign by ID."""
    campaign = CampaignService.get_campaign_by_id(db, campaign_id)
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    return campaign


@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: uuid.UUID,
    campaign_data: CampaignUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Update a campaign (Admin only)."""
    campaign = CampaignService.update_campaign(db, campaign_id, campaign_data)
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    return campaign


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign(
    campaign_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Delete a campaign (Admin only)."""
    success = CampaignService.delete_campaign(db, campaign_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )


# Strategy Endpoints
@router.post("/strategies", response_model=StrategyResponse, status_code=status.HTTP_201_CREATED)
async def create_strategy(
    strategy_data: StrategyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new strategy."""
    strategy = CampaignService.find_or_create_strategy(
        db,
        strategy_data.campaign_id,
        strategy_data.name
    )
    db.commit()
    return strategy


@router.get("/strategies/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(
    strategy_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get strategy by ID."""
    strategy = CampaignService.get_strategy_by_id(db, strategy_id)
    
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found"
        )
    
    return strategy


@router.put("/strategies/{strategy_id}", response_model=StrategyResponse)
async def update_strategy(
    strategy_id: uuid.UUID,
    strategy_data: StrategyUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Update a strategy (Admin only)."""
    strategy = CampaignService.update_strategy(db, strategy_id, strategy_data)
    
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found"
        )
    
    return strategy


@router.delete("/strategies/{strategy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_strategy(
    strategy_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Delete a strategy (Admin only)."""
    success = CampaignService.delete_strategy(db, strategy_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found"
        )


# Placement Endpoints
@router.post("/placements", response_model=PlacementResponse, status_code=status.HTTP_201_CREATED)
async def create_placement(
    placement_data: PlacementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new placement."""
    placement = CampaignService.find_or_create_placement(
        db,
        placement_data.strategy_id,
        placement_data.name
    )
    db.commit()
    return placement


@router.get("/placements/{placement_id}", response_model=PlacementResponse)
async def get_placement(
    placement_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get placement by ID."""
    placement = CampaignService.get_placement_by_id(db, placement_id)
    
    if not placement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Placement not found"
        )
    
    return placement


@router.put("/placements/{placement_id}", response_model=PlacementResponse)
async def update_placement(
    placement_id: uuid.UUID,
    placement_data: PlacementUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Update a placement (Admin only)."""
    placement = CampaignService.update_placement(db, placement_id, placement_data)
    
    if not placement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Placement not found"
        )
    
    return placement


@router.delete("/placements/{placement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_placement(
    placement_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Delete a placement (Admin only)."""
    success = CampaignService.delete_placement(db, placement_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Placement not found"
        )


# Creative Endpoints
@router.post("/creatives", response_model=CreativeResponse, status_code=status.HTTP_201_CREATED)
async def create_creative(
    creative_data: CreativeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new creative."""
    creative = CampaignService.find_or_create_creative(
        db,
        creative_data.placement_id,
        creative_data.name,
        creative_data.preview_url
    )
    db.commit()
    return creative


@router.get("/creatives/{creative_id}", response_model=CreativeResponse)
async def get_creative(
    creative_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get creative by ID."""
    creative = CampaignService.get_creative_by_id(db, creative_id)
    
    if not creative:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creative not found"
        )
    
    return creative


@router.put("/creatives/{creative_id}", response_model=CreativeResponse)
async def update_creative(
    creative_id: uuid.UUID,
    creative_data: CreativeUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Update a creative (Admin only)."""
    creative = CampaignService.update_creative(db, creative_id, creative_data)
    
    if not creative:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creative not found"
        )
    
    return creative


@router.delete("/creatives/{creative_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_creative(
    creative_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Delete a creative (Admin only)."""
    success = CampaignService.delete_creative(db, creative_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creative not found"
        )
