"""
Campaign hierarchy models (Campaign, Strategy, Placement, Creative).
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base


class Campaign(Base):
    """Top-level campaign entity."""
    
    __tablename__ = "campaigns"
    __table_args__ = (
        UniqueConstraint('client_id', 'name', 'source', name='uq_campaign_client_name_source'),
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey('clients.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    name = Column(String(255), nullable=False)
    source = Column(String(50), nullable=False)  # 'surfside', 'vibe', 'facebook'
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client = relationship("Client", back_populates="campaigns")
    strategies = relationship("Strategy", back_populates="campaign", cascade="all, delete-orphan")
    creatives = relationship("Creative", back_populates="campaign", cascade="all, delete-orphan") # New relationship
    daily_metrics = relationship("DailyMetrics", back_populates="campaign")

    
    def __repr__(self):
        return f"<Campaign {self.name} ({self.source})>"


class Strategy(Base):
    """Second-level strategy entity."""
    
    __tablename__ = "strategies"
    __table_args__ = (
        UniqueConstraint('campaign_id', 'name', name='uq_strategy_campaign_name'),
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey('campaigns.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    campaign = relationship("Campaign", back_populates="strategies")
    placements = relationship("Placement", back_populates="strategy", cascade="all, delete-orphan")
    daily_metrics = relationship("DailyMetrics", back_populates="strategy")
    
    def __repr__(self):
        return f"<Strategy {self.name}>"


class Placement(Base):
    """Third-level placement entity."""
    
    __tablename__ = "placements"
    __table_args__ = (
        UniqueConstraint('strategy_id', 'name', name='uq_placement_strategy_name'),
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    strategy_id = Column(UUID(as_uuid=True), ForeignKey('strategies.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    strategy = relationship("Strategy", back_populates="placements")
    creatives = relationship("Creative", back_populates="placement", cascade="all, delete-orphan")
    daily_metrics = relationship("DailyMetrics", back_populates="placement")
    
    def __repr__(self):
        return f"<Placement {self.name}>"


class Region(Base):
    """Region entity for geo-targeting."""
    
    __tablename__ = "regions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    daily_metrics = relationship("DailyMetrics", back_populates="region")
    
    def __repr__(self):
        return f"<Region {self.name}>"


class Creative(Base):
    """Fourth-level creative entity. Can belong to Placement (Surfside) or Campaign (Facebook)."""
    
    __tablename__ = "creatives"
    # Unique constraint removed due to mixed hierarchy
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    placement_id = Column(UUID(as_uuid=True), ForeignKey('placements.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=True)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey('campaigns.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=True) # New: direct link to campaign
    name = Column(String(255), nullable=False)
    preview_url = Column(Text)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    placement = relationship("Placement", back_populates="creatives")
    campaign = relationship("Campaign", back_populates="creatives") # New relationship
    daily_metrics = relationship("DailyMetrics", back_populates="creative")
    
    def __repr__(self):
        return f"<Creative {self.name}>"

