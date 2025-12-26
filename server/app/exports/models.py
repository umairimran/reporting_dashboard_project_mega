"""
SQLAlchemy models for exports and reports.
"""
from sqlalchemy import Column, String, Integer, ForeignKey, Date, DateTime, Text
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.core.database import Base

class Report(Base):
    """
    Report model for tracking async generated reports.
    """
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    source = Column(String(50), nullable=True)
    type = Column(String(50), nullable=False)  # weekly, monthly
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    status = Column(String(20), nullable=False, default="generating")  # generating, ready, failed
    pdf_file_path = Column(Text, nullable=True)
    csv_file_path = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # created_at corresponds to 'generatedAt' in frontend interface
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    client = relationship("Client", backref=backref("reports", cascade="all, delete-orphan", passive_deletes=True))
