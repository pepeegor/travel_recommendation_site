from enum import Enum
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class TripStatus(str, Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class STripBase(BaseModel):
    destination_id: int = Field(..., ge=1)
    start_date: datetime
    end_date: datetime
    budget: Optional[float] = None

    model_config = ConfigDict()


class STripCreate(STripBase):
    pass


class STripUpdate(BaseModel):
    destination_id: Optional[int] = Field(None, ge=1)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    budget: Optional[float] = None
    status: Optional[TripStatus] = None

    model_config = ConfigDict()


class STripOut(STripBase):
    id: int
    user_id: int
    status: TripStatus

    model_config = ConfigDict(from_attributes=True)
