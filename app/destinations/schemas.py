from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from decimal import Decimal


class SDestinationBase(BaseModel):
    name: str
    description: Optional[str] = None
    country: str
    climate: str
    approximate_price: Decimal
    latitude: float
    longitude: float
    image_url: Optional[str] = None
    available_slots: int = Field(..., description="Количество свободных мест")


class SDestinationCreate(SDestinationBase):
    """Поля для создания направления"""
    pass


class SDestinationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    country: Optional[str] = None
    climate: Optional[str] = None
    approximate_price: Optional[Decimal] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    image_url: Optional[str] = None
    available_slots: Optional[int] = Field(None, ge=0)


class SDestinationOut(SDestinationBase):
    id: int
    other_images: List[str] = []  # если вы отдаёте дополнительные картинки

    model_config = ConfigDict(from_attributes=True)
