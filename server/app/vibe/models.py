"""
Vibe-specific models for credentials and report tracking.
"""
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base
from app.core.encryption import decrypt_api_key


class VibeCredentials(Base):
    """Stores Vibe API credentials per client."""
    
    __tablename__ = "vibe_credentials"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey('clients.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    api_key = Column(Text, nullable=False)  # Stored encrypted
    advertiser_id = Column(String(255))
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client = relationship("Client", back_populates="vibe_credentials")
    
    @property
    def decrypted_api_key(self) -> str:
        """Get the decrypted API key."""
        return decrypt_api_key(self.api_key)
    
    def __repr__(self):
        return f"<VibeCredentials client_id={self.client_id}>"


class VibeReportRequest(Base):
    """Tracks Vibe API async report requests."""
    
    __tablename__ = "vibe_report_requests"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey('clients.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    report_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    status = Column(String(20), nullable=False, index=True)  # 'created', 'processing', 'done', 'failed'
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    download_url = Column(Text)
    error_message = Column(Text)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<VibeReportRequest {self.report_id} - {self.status}>"
