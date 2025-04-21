from datetime import date, datetime
from typing import Literal, Optional
from pydantic import BaseModel, EmailStr, field_serializer
from sqlalchemy import Enum


class TripStatus(str, Enum):
    FUTURE = "planned"
    PAST = "completed"
    CURRENT = "in_progress"


class STripCreate(BaseModel):
    destination_id: int
    start_date: datetime
    end_date: datetime
    budget: Optional[float]
    status: Optional[Literal["planned", "completed", "in_progress"]] = None
    
    class Config:
        from_attributes = True
        
class STripUpdate(BaseModel):
    budget: Optional[float] = None
    status: Optional[Literal["planned", "completed", "in_progress"]] = None

    class Config:
        from_attributes = True
        
class TripResponse(BaseModel):
    id: int
    destination_id: int
    start_date: datetime
    end_date: datetime
    budget: Optional[float] = None
    
    
    class Config:
        from_attributes = True

