from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

class SReviewCreate(BaseModel):
    destination_id: int = Field(..., ge=1)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None

    model_config = ConfigDict()

class SReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None

    model_config = ConfigDict()

class SReviewOut(BaseModel):
    id: int
    user_id: int
    destination_id: int
    rating: int
    comment: Optional[str]
    created_at: datetime
    username: str

    model_config = ConfigDict(from_attributes=True)

class SReviewList(BaseModel):
    total: int
    page: int
    pages: int
    average_rating: float
    reviews: List[SReviewOut]

    model_config = ConfigDict()

class SUserReviewOut(BaseModel):
    id: int
    rating: int
    comment: Optional[str]
    created_at: datetime
    destination: dict  # {id, name, country, image_url}

    model_config = ConfigDict()

class SUserReviewsList(BaseModel):
    total: int
    reviews: List[SUserReviewOut]

    model_config = ConfigDict()
