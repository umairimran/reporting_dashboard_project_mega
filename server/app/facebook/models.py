"""
Facebook file upload models.
"""
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base


class UploadedFile(Base):
    """Tracks manually uploaded files (Facebook, etc.)."""
    
    __tablename__ = "uploaded_files"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey('clients.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    source = Column(String(50), nullable=False, index=True)  # 'facebook'
    file_name = Column(String(255), nullable=False)
    file_path = Column(Text, nullable=False)
    file_size = Column(Integer, nullable=False)
    upload_status = Column(String(20), nullable=False, default='pending', index=True)  # 'pending', 'processing', 'processed', 'failed'
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey('users.id', onupdate='CASCADE', ondelete='SET NULL'))
    processed_at = Column(DateTime)
    error_message = Column(Text)
    records_count = Column(Integer)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    client = relationship("Client", back_populates="uploaded_files")
    
    def __repr__(self):
        return f"<UploadedFile {self.file_name} - {self.upload_status}>"
