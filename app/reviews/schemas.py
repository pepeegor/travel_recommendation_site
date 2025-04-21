from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_serializer

from app.users.schemas import SUser


class SReviewCreate(BaseModel):
    destination_id: int
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    comment: Optional[str] = Field(None, max_length=1000)
    
    class Config:
        from_attributes = True
        
        
class SReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=1000)
    
    class Config:
        from_attributes = True
        
class SReviewOut(BaseModel):
    id: int
    rating: int
    comment: str | None = None
    created_at: datetime
    username: str  # Add username field