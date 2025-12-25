"""
Campaign hierarchy management business logic.
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, Tuple
import uuid
from app.campaigns.models import Campaign, Strategy, Placement, Creative, Region
from app.campaigns.schemas import CampaignUpdate, StrategyUpdate, PlacementUpdate, CreativeUpdate
from app.core.logging import logger
from app.core.exceptions import ValidationError


class CampaignService:
    """Service for campaign hierarchy operations."""
    
    @staticmethod
    def find_or_create_region(
        db: Session,
        region_name: str
    ) -> Region:
        """Find existing region or create new one."""
        region = db.query(Region).filter(Region.name == region_name).first()
        
        if not region:
            region = Region(name=region_name)
            db.add(region)
            db.flush()
            logger.debug(f"Created region: {region_name}")
            
        return region

    
    @staticmethod
    def find_or_create_campaign(
        db: Session,
        client_id: uuid.UUID,
        campaign_name: str,
        source: str
    ) -> Campaign:
        """
        Find existing campaign or create new one.
        
        Args:
            db: Database session
            client_id: Client UUID
            campaign_name: Campaign name
            source: Data source ('surfside', 'vibe', 'facebook')
            
        Returns:
            Campaign entity
        """
        campaign = db.query(Campaign).filter(
            Campaign.client_id == client_id,
            Campaign.name == campaign_name,
            Campaign.source == source
        ).first()
        
        if not campaign:
            campaign = Campaign(
                client_id=client_id,
                name=campaign_name,
                source=source
            )
            db.add(campaign)
            db.flush()
            logger.debug(f"Created campaign: {campaign_name} ({source})")
        
        return campaign
    
    @staticmethod
    def update_campaign(
        db: Session,
        campaign_id: uuid.UUID,
        campaign_data: CampaignUpdate
    ) -> Optional[Campaign]:
        """Update a campaign."""
        campaign = CampaignService.get_campaign_by_id(db, campaign_id)
        if not campaign:
            return None
        
        if campaign_data.name:
            campaign.name = campaign_data.name
        
        db.commit()
        db.refresh(campaign)
        return campaign

    @staticmethod
    def delete_campaign(db: Session, campaign_id: uuid.UUID) -> bool:
        """Delete a campaign."""
        campaign = CampaignService.get_campaign_by_id(db, campaign_id)
        if not campaign:
            return False
            
        db.delete(campaign)
        db.commit()
        return True

    @staticmethod
    def find_or_create_strategy(
        db: Session,
        campaign_id: uuid.UUID,
        strategy_name: str
    ) -> Strategy:
        """
        Find existing strategy or create new one.
        
        Args:
            db: Database session
            campaign_id: Campaign UUID
            strategy_name: Strategy name
            
        Returns:
            Strategy entity
        """
        strategy = db.query(Strategy).filter(
            Strategy.campaign_id == campaign_id,
            Strategy.name == strategy_name
        ).first()
        
        if not strategy:
            strategy = Strategy(
                campaign_id=campaign_id,
                name=strategy_name
            )
            db.add(strategy)
            db.flush()
            logger.debug(f"Created strategy: {strategy_name}")
        
        return strategy
    
    @staticmethod
    def update_strategy(
        db: Session,
        strategy_id: uuid.UUID,
        strategy_data: StrategyUpdate
    ) -> Optional[Strategy]:
        """Update a strategy."""
        strategy = CampaignService.get_strategy_by_id(db, strategy_id)
        if not strategy:
            return None
        
        if strategy_data.name:
            strategy.name = strategy_data.name
            
        db.commit()
        db.refresh(strategy)
        return strategy

    @staticmethod
    def delete_strategy(db: Session, strategy_id: uuid.UUID) -> bool:
        """Delete a strategy."""
        strategy = CampaignService.get_strategy_by_id(db, strategy_id)
        if not strategy:
            return False
            
        db.delete(strategy)
        db.commit()
        return True

    @staticmethod
    def find_or_create_placement(
        db: Session,
        strategy_id: uuid.UUID,
        placement_name: str
    ) -> Placement:
        """
        Find existing placement or create new one.
        
        Args:
            db: Database session
            strategy_id: Strategy UUID
            placement_name: Placement name
            
        Returns:
            Placement entity
        """
        placement = db.query(Placement).filter(
            Placement.strategy_id == strategy_id,
            Placement.name == placement_name
        ).first()
        
        if not placement:
            placement = Placement(
                strategy_id=strategy_id,
                name=placement_name
            )
            db.add(placement)
            db.flush()
            logger.debug(f"Created placement: {placement_name}")
        
        return placement
    
    @staticmethod
    def update_placement(
        db: Session,
        placement_id: uuid.UUID,
        placement_data: PlacementUpdate
    ) -> Optional[Placement]:
        """Update a placement."""
        placement = CampaignService.get_placement_by_id(db, placement_id)
        if not placement:
            return None
        
        if placement_data.name:
            placement.name = placement_data.name
            
        db.commit()
        db.refresh(placement)
        return placement

    @staticmethod
    def delete_placement(db: Session, placement_id: uuid.UUID) -> bool:
        """Delete a placement."""
        placement = CampaignService.get_placement_by_id(db, placement_id)
        if not placement:
            return False
            
        db.delete(placement)
        db.commit()
        return True

    @staticmethod
    def find_or_create_creative(
        db: Session,
        creative_name: str,
        placement_id: Optional[uuid.UUID] = None,
        campaign_id: Optional[uuid.UUID] = None,
        preview_url: Optional[str] = None
    ) -> Creative:
        """
        Find existing creative or create new one.
        
        Args:
            db: Database session
            creative_name: Creative name
            placement_id: Optional Placement UUID (for Surfside)
            campaign_id: Optional Campaign UUID (for Facebook)
            preview_url: Optional preview URL
            
        Returns:
            Creative entity
        """
        if not placement_id and not campaign_id:
            raise ValidationError("Creative must be linked to either a Placement or a Campaign")
            
        query = db.query(Creative).filter(Creative.name == creative_name)
        
        if placement_id:
            query = query.filter(Creative.placement_id == placement_id)
        if campaign_id:
            query = query.filter(Creative.campaign_id == campaign_id)
            
        creative = query.first()
        
        if not creative:
            creative = Creative(
                placement_id=placement_id,
                campaign_id=campaign_id,
                name=creative_name,
                preview_url=preview_url
            )
            db.add(creative)
            db.flush()
            logger.debug(f"Created creative: {creative_name}")
        
        return creative
    
    @staticmethod
    def update_creative(
        db: Session,
        creative_id: uuid.UUID,
        creative_data: CreativeUpdate
    ) -> Optional[Creative]:
        """Update a creative."""
        creative = CampaignService.get_creative_by_id(db, creative_id)
        if not creative:
            return None
        
        if creative_data.name:
            creative.name = creative_data.name
        if creative_data.preview_url is not None:
            creative.preview_url = creative_data.preview_url
            
        db.commit()
        db.refresh(creative)
        return creative

    @staticmethod
    def delete_creative(db: Session, creative_id: uuid.UUID) -> bool:
        """Delete a creative."""
        creative = CampaignService.get_creative_by_id(db, creative_id)
        if not creative:
            return False
            
        db.delete(creative)
        db.commit()
        return True

    def create_hierarchy(
        db: Session,
        client_id: uuid.UUID,
        source: str,
        creative_name: str,
        campaign_name: Optional[str] = None,
        strategy_name: Optional[str] = None,
        placement_name: Optional[str] = None,
        region_name: Optional[str] = None,
        preview_url: Optional[str] = None
    ) -> Tuple[Optional[Campaign], Optional[Strategy], Optional[Placement], Creative, Optional[Region]]:

        """
        Create hierarchy entities based on source logic.
        
        Returns:
            Tuple of (campaign, strategy, placement, creative, region)
        """
        campaign = None
        strategy = None
        placement = None
        region = None
        creative = None
        
        # 1. Handle Regions (Common)
        if region_name:
            region = CampaignService.find_or_create_region(db, region_name)
            
        # 2. Logic per Source
        if source == 'facebook':
            # Facebook: Campaign -> Region (via Metric) -> Creative (linked to Campaign)
            # Strategy/Placement are None
            if not campaign_name:
                raise ValidationError("Facebook data requires campaign_name")
                
            campaign = CampaignService.find_or_create_campaign(db, client_id, campaign_name, source)
            
            # Creative linked to Campaign
            creative = CampaignService.find_or_create_creative(
                db=db,
                creative_name=creative_name,
                campaign_id=campaign.id,
                preview_url=preview_url
            )
            
        elif source == 'surfside':
            # Surfside: (Campaign? NULL) -> Strategy -> Placement -> Creative
            # Campaign is NULL for Surfside as requested.
            
            if not strategy_name or not placement_name:
                # Fallback if missing? Or raise error? Assumed present.
                 if not strategy_name: strategy_name = "Unknown Strategy"
                 if not placement_name: placement_name = "Unknown Placement"

            # Must have a parent campaign even if dummy?
            # Model says Strategy needs CampaignID.
            # User said "campaign name is also not avaiable for surfside".
            # BUT Strategy model has `campaign_id` which is NOT NULL in original schema.
            # I made `campaign_id` nullable in `daily_metrics`, but DID I make `campaign_id` nullable in `strategies`?
            # Checking schema... `strategies.campaign_id` is NOT NULL REFERENCES campaigns(id).
            # Constraint: We need a dummy campaign for Surfside strategies.
            
            dummy_campaign = CampaignService.find_or_create_campaign(db, client_id, "Surfside General", source)
            
            strategy = CampaignService.find_or_create_strategy(db, dummy_campaign.id, strategy_name)
            placement = CampaignService.find_or_create_placement(db, strategy.id, placement_name)
            
            creative = CampaignService.find_or_create_creative(
                db=db,
                creative_name=creative_name,
                placement_id=placement.id,
                preview_url=preview_url
            )
            
        else:
            # Default/Fallback (legacy hierarchy)
            if campaign_name:
                campaign = CampaignService.find_or_create_campaign(db, client_id, campaign_name, source)
                if strategy_name:
                    strategy = CampaignService.find_or_create_strategy(db, campaign.id, strategy_name)
                    if placement_name:
                        placement = CampaignService.find_or_create_placement(db, strategy.id, placement_name)
                        creative = CampaignService.find_or_create_creative(
                            db=db,
                            creative_name=creative_name,
                            placement_id=placement.id,
                            preview_url=preview_url
                        )
            
            if not creative:
                 # Minimal fallback if logic fails
                 raise ValidationError(f"Could not construct hierarchy for source {source}")

        return campaign, strategy, placement, creative, region
    
    @staticmethod
    def get_campaign_by_id(db: Session, campaign_id: uuid.UUID) -> Optional[Campaign]:
        """Get campaign by ID."""
        return db.query(Campaign).filter(Campaign.id == campaign_id).first()
    
    @staticmethod
    def get_campaigns_by_client(
        db: Session,
        client_id: uuid.UUID,
        source: Optional[str] = None
    ):
        """Get all campaigns for a client, optionally filtered by source."""
        query = db.query(Campaign).filter(Campaign.client_id == client_id)
        
        if source:
            query = query.filter(Campaign.source == source)
        
        return query.all()
    
    @staticmethod
    def get_strategy_by_id(db: Session, strategy_id: uuid.UUID) -> Optional[Strategy]:
        """Get strategy by ID."""
        return db.query(Strategy).filter(Strategy.id == strategy_id).first()
    
    @staticmethod
    def get_placement_by_id(db: Session, placement_id: uuid.UUID) -> Optional[Placement]:
        """Get placement by ID."""
        return db.query(Placement).filter(Placement.id == placement_id).first()
    
    @staticmethod
    def get_creative_by_id(db: Session, creative_id: uuid.UUID) -> Optional[Creative]:
        """Get creative by ID."""
        return db.query(Creative).filter(Creative.id == creative_id).first()
