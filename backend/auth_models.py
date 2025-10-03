"""
Authentication Models and Utilities for BCM Market Map Generator
Restricts access to @beebyclarkmeyler.com email domain
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime, timezone, timedelta
import uuid


class User(BaseModel):
    """User model for MongoDB storage"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    name: str
    picture: Optional[str] = None
    is_active: bool = True
    is_admin: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login: Optional[datetime] = None
    
    @validator('email')
    def validate_email_domain(cls, v):
        """Ensure email is from @beebyclarkmeyler.com domain"""
        if not v.endswith('@beebyclarkmeyler.com'):
            raise ValueError('Only @beebyclarkmeyler.com email addresses are allowed')
        return v.lower()


class Session(BaseModel):
    """Session model for MongoDB storage"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    session_token: str
    expires_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    @staticmethod
    def create_expiry():
        """Create session expiry (7 days from now)"""
        return datetime.now(timezone.utc) + timedelta(days=7)


class SessionData(BaseModel):
    """Session data from Emergent Auth"""
    id: str
    email: str
    name: str
    picture: Optional[str] = None
    session_token: str


class UserResponse(BaseModel):
    """User response for API"""
    id: str
    email: str
    name: str
    picture: Optional[str] = None
    is_active: bool
    is_admin: bool
    created_at: datetime
    last_login: Optional[datetime] = None


class AdminUserUpdate(BaseModel):
    """Model for admin to update user status"""
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None