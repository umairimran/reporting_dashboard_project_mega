"""
Client and Client Settings models.
"""
from sqlalchemy import Column, String, Boolean, DateTime, Numeric, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base


class Client(Base):
    """Client company entity."""
    
    __tablename__ = "clients"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    status = Column(String(20), nullable=False, default='active')  # 'active' or 'disabled'
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', onupdate='CASCADE', ondelete='RESTRICT'))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="clients")
    settings = relationship("ClientSettings", back_populates="client", cascade="all, delete-orphan", passive_deletes=True)
    campaigns = relationship("Campaign", back_populates="client", cascade="all, delete-orphan", passive_deletes=True)
    daily_metrics = relationship("DailyMetrics", back_populates="client", cascade="all, delete-orphan", passive_deletes=True)
    weekly_summaries = relationship("WeeklySummary", back_populates="client", cascade="all, delete-orphan", passive_deletes=True)
    monthly_summaries = relationship("MonthlySummary", back_populates="client", cascade="all, delete-orphan", passive_deletes=True)
    vibe_credentials = relationship("VibeCredentials", back_populates="client", cascade="all, delete-orphan", passive_deletes=True)
    uploaded_files = relationship("UploadedFile", back_populates="client", cascade="all, delete-orphan", passive_deletes=True)
    ingestion_logs = relationship("IngestionLog", back_populates="client", cascade="all, delete-orphan", passive_deletes=True)
    staging_media = relationship("StagingMediaRaw", back_populates="client", cascade="all, delete-orphan", passive_deletes=True)

    
    def __repr__(self):
        return f"<Client {self.name}>"


class ClientSettings(Base):
    """Client-specific CPM rates and configuration."""
    
    __tablename__ = "client_settings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey('clients.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    source = Column(String(50), nullable=False)  # 'surfside', 'vibe', or 'facebook'
    cpm = Column(Numeric(10, 4), nullable=False)
    currency = Column(String(3), default='USD')
    effective_date = Column(DateTime, default=datetime.utcnow)  # TIMESTAMP for multiple updates per day
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client = relationship("Client", back_populates="settings")
    
    def __repr__(self):
        return f"<ClientSettings client_id={self.client_id} source={self.source} cpm={self.cpm}>"
