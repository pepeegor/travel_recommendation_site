# app/attractions/schemas.py

from pydantic import BaseModel, ConfigDict
from typing import Optional
from decimal import Decimal


class SAttractionBase(BaseModel):
    name: str
    type: str
    description: Optional[str] = None
    approximate_price: Optional[Decimal] = None
    latitude: float
    longitude: float


class SAttractionCreate(SAttractionBase):
    pass


class SAttractionUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    approximate_price: Optional[Decimal] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class SAttractionOut(SAttractionBase):
    id: int
    destination_id: int

    model_config = ConfigDict(from_attributes=True)
