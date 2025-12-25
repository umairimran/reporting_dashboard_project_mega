"""
Pydantic schemas for exports and reports.
"""
from pydantic import BaseModel, ConfigDict, field_validator, computed_field
from datetime import date, datetime
from typing import Optional
import uuid

class ReportBase(BaseModel):
    type: str
    source: Optional[str] = None
    period_start: date
    period_end: date

    @field_validator('source')
    @classmethod
    def validate_source(cls, v: Optional[str]) -> Optional[str]:
        if v and v not in ['facebook', 'surfside']:
            raise ValueError("Source must be one of: facebook, surfside")
        return v

class ReportCreate(ReportBase):
    pass

class ReportResponse(ReportBase):
    id: uuid.UUID
    client_id: uuid.UUID
    status: str
    created_at: datetime
    
    @computed_field
    @property
    def generatedAt(self) -> str:
        return self.created_at.isoformat()

    @computed_field
    @property
    def periodStart(self) -> str:
        return self.period_start.isoformat()

    @computed_field
    @property
    def periodEnd(self) -> str:
        return self.period_end.isoformat()

    @computed_field
    @property
    def clientId(self) -> str:
        return str(self.client_id)
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

# Schema for valid report types
class ReportType:
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class ReportStatus:
    GENERATING = "generating"
    READY = "ready"
    FAILED = "failed"
