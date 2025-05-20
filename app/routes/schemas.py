from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime
from app.attractions.schemas import SAttractionOut


class SRouteAttractionOut(BaseModel):
    id: int
    position: int = Field(..., example=0)
    attraction: SAttractionOut

    class Config:
        from_attributes = True


class SRouteCreate(BaseModel):
    name: str = Field(..., example="День в Париже")
    destination_id: int = Field(..., example=1)
    total_budget: Optional[float] = Field(None, example=200.00)


class SRouteAttractionCreate(BaseModel):
    attraction_id: int
    position: int


class SRouteUpdate(BaseModel):
    name: Optional[str]
    trip_id: Optional[int]
    destination_id: Optional[int]
    attractions: Optional[List[SRouteAttractionCreate]]


class SRouteOut(BaseModel):
    id: int
    name: str
    user_id: int
    trip_id: Optional[int]
    destination_id: int
    total_budget: Optional[float]
    published: bool
    created_at: datetime

    attractions: List[SRouteAttractionOut] = []

    class Config:
        from_attributes = True


class SRouteAttractionCreate(BaseModel):
    attraction_id: int
    position: int


class SRouteAttractionMove(BaseModel):
    position: int = Field(..., example=1)


class RouteAttractionOut(BaseModel):
    attraction_id: int
    position: int

    model_config = ConfigDict(from_attributes=True)


class RouteOut(BaseModel):
    id: int
    name: str
    user_id: int
    trip_id: int
    destination_id: int
    total_budget: Optional[Decimal]
    published: bool
    created_at: datetime
    points: List[RouteAttractionOut]

    model_config = ConfigDict(from_attributes=True)
