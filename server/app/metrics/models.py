"""
Metrics and aggregation models.
"""
from sqlalchemy import Column, String, DateTime, Date, BigInteger, Numeric, ForeignKey, UniqueConstraint, Integer, Text, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base


class DailyMetrics(Base):
    """Daily performance metrics from all sources."""
    
    __tablename__ = "daily_metrics"
    __table_args__ = (
        UniqueConstraint(
            'client_id', 'date', 'campaign_id', 'strategy_id', 
            'placement_id', 'creative_id', 'source',
            name='uq_daily_metrics_full'
        ),
        Index('idx_daily_metrics_client_date', 'client_id', 'date'),
        Index('idx_daily_metrics_client_source_date', 'client_id', 'source', 'date'),
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey('clients.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    date = Column(Date, nullable=False, index=True)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey('campaigns.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=True)
    strategy_id = Column(UUID(as_uuid=True), ForeignKey('strategies.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=True)
    placement_id = Column(UUID(as_uuid=True), ForeignKey('placements.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=True)
    creative_id = Column(UUID(as_uuid=True), ForeignKey('creatives.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    region_id = Column(UUID(as_uuid=True), ForeignKey('regions.id', onupdate='CASCADE', ondelete='SET NULL'), nullable=True)
    
    source = Column(String(50), nullable=False, index=True)
    
    # Raw metrics
    impressions = Column(BigInteger, nullable=False, default=0)
    clicks = Column(BigInteger, nullable=False, default=0)
    conversions = Column(BigInteger, nullable=False, default=0)
    conversion_revenue = Column(Numeric(12, 2), nullable=False, default=0)
    
    # Calculated metrics
    ctr = Column(Numeric(12, 6), nullable=False, default=0)
    spend = Column(Numeric(12, 2), nullable=False, default=0)
    cpc = Column(Numeric(12, 4), nullable=False, default=0)
    cpa = Column(Numeric(12, 4), nullable=False, default=0)
    roas = Column(Numeric(12, 4), nullable=False, default=0)
    
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client = relationship("Client", back_populates="daily_metrics")
    campaign = relationship("Campaign", back_populates="daily_metrics")
    strategy = relationship("Strategy", back_populates="daily_metrics")
    placement = relationship("Placement", back_populates="daily_metrics")
    creative = relationship("Creative", back_populates="daily_metrics")
    region = relationship("Region", back_populates="daily_metrics")

    
    def __repr__(self):
        return f"<DailyMetrics {self.date} - {self.source}>"


class WeeklySummary(Base):
    """Aggregated weekly performance summaries."""
    
    __tablename__ = "weekly_summaries"
    __table_args__ = (
        UniqueConstraint('client_id', 'week_start', name='uq_weekly_summary_client_week'),
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey('clients.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    week_start = Column(Date, nullable=False, index=True)
    week_end = Column(Date, nullable=False)
    
    # Aggregated metrics
    impressions = Column(BigInteger, nullable=False, default=0)
    clicks = Column(BigInteger, nullable=False, default=0)
    conversions = Column(BigInteger, nullable=False, default=0)
    revenue = Column(Numeric(12, 2), nullable=False, default=0)
    spend = Column(Numeric(12, 2), nullable=False, default=0)
    
    # Calculated metrics
    ctr = Column(Numeric(12, 6))
    cpc = Column(Numeric(12, 4))
    cpa = Column(Numeric(12, 4))
    roas = Column(Numeric(12, 4))
    
    # Top performers (JSON)
    top_campaigns = Column(JSONB)
    top_creatives = Column(JSONB)
    
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    client = relationship("Client", back_populates="weekly_summaries")
    
    def __repr__(self):
        return f"<WeeklySummary {self.week_start}>"


class MonthlySummary(Base):
    """Aggregated monthly performance summaries."""
    
    __tablename__ = "monthly_summaries"
    __table_args__ = (
        UniqueConstraint('client_id', 'month_start', name='uq_monthly_summary_client_month'),
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey('clients.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    month_start = Column(Date, nullable=False, index=True)
    month_end = Column(Date, nullable=False)
    
    # Aggregated metrics
    impressions = Column(BigInteger, nullable=False, default=0)
    clicks = Column(BigInteger, nullable=False, default=0)
    conversions = Column(BigInteger, nullable=False, default=0)
    revenue = Column(Numeric(12, 2), nullable=False, default=0)
    spend = Column(Numeric(12, 2), nullable=False, default=0)
    
    # Calculated metrics
    ctr = Column(Numeric(12, 6), nullable=False, default=0)
    cpc = Column(Numeric(12, 4), nullable=False, default=0)
    cpa = Column(Numeric(12, 4), nullable=False, default=0)
    roas = Column(Numeric(12, 4), nullable=False, default=0)
    
    # Top performers (JSON)
    top_campaigns = Column(JSONB)
    top_creatives = Column(JSONB)
    
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    client = relationship("Client", back_populates="monthly_summaries")
    
    def __repr__(self):
        return f"<MonthlySummary {self.month_start}>"


class StagingMediaRaw(Base):
    """Temporary staging table for data ingestion."""
    
    __tablename__ = "staging_media_raw"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ingestion_run_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    client_id = Column(UUID(as_uuid=True), ForeignKey('clients.id', onupdate='CASCADE', ondelete='CASCADE'))
    source = Column(String(50), nullable=False, index=True)
    
    # Raw CSV/API data
    date = Column(Date, nullable=False)
    campaign_name = Column(String(255))
    strategy_name = Column(String(255))
    placement_name = Column(String(255))
    creative_name = Column(String(255))
    
    # Raw metrics
    impressions = Column(BigInteger, default=0)
    clicks = Column(BigInteger, default=0)
    ctr = Column(Numeric(12, 6))
    conversions = Column(BigInteger, default=0)
    conversion_revenue = Column(Numeric(12, 2), default=0)
    
    # Source-specific data
    raw_data = Column(JSONB)
    
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    client = relationship("Client", back_populates="staging_media")
    
    def __repr__(self):
        return f"<StagingMediaRaw {self.source} - {self.date}>"


class IngestionLog(Base):
    """Tracks all data ingestion attempts."""
    
    __tablename__ = "ingestion_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_date = Column(Date, nullable=False, index=True)
    status = Column(String(20), nullable=False, index=True)  # 'success', 'failed', 'partial', 'processing'
    message = Column(Text)
    records_loaded = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)
    started_at = Column(DateTime, nullable=False)
    finished_at = Column(DateTime)
    file_name = Column(String(255))
    source = Column(String(50), nullable=False, index=True)
    client_id = Column(UUID(as_uuid=True), ForeignKey('clients.id', onupdate='CASCADE', ondelete='SET NULL'))
    
    # Error resolution tracking
    resolution_status = Column(String(20))  # 'unresolved', 'resolved', 'ignored'
    resolution_notes = Column(Text)
    resolved_at = Column(DateTime)
    resolved_by = Column(UUID(as_uuid=True), ForeignKey('users.id', onupdate='CASCADE', ondelete='SET NULL'))
    
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    client = relationship("Client", back_populates="ingestion_logs")
    
    def __repr__(self):
        return f"<IngestionLog {self.source} - {self.run_date} ({self.status})>"


class AuditLog(Base):
    """Tracks all user actions for security and compliance."""
    
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', onupdate='CASCADE', ondelete='SET NULL'), index=True)
    action = Column(String(100), nullable=False, index=True)
    entity_type = Column(String(50), index=True)
    entity_id = Column(UUID(as_uuid=True), index=True)
    old_values = Column(JSONB)
    new_values = Column(JSONB)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog {self.action} by user {self.user_id}>"
