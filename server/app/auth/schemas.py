"""
Pydantic schemas for authentication requests and responses.
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
import uuid


class UserLogin(BaseModel):
    """Login request schema."""
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserCreate(BaseModel):
    """User creation request schema."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: str = Field(..., pattern="^(admin|client)$")


class UserUpdate(BaseModel):
    """User update request schema."""
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    role: Optional[str] = None
    
    @validator('role')
    def validate_role(cls, v):
        if v and v not in ('admin', 'client'):
            raise ValueError('Role must be admin or client')
        return v


class UserResponse(BaseModel):
    """User response schema."""
    id: uuid.UUID
    email: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """JWT token response schema."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """JWT token payload data."""
    email: Optional[str] = None
    user_id: Optional[str] = None


class PasswordChange(BaseModel):
    """Password change request schema."""
    old_password: str
    new_password: str = Field(..., min_length=8)


class PasswordReset(BaseModel):
    """Password reset request schema (admin only)."""
    new_password: str = Field(..., min_length=8)
