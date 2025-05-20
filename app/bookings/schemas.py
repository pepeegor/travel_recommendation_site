from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import List, Optional

class BookingCreate(BaseModel):
    destination_id: int = Field(..., description="ID направления для бронирования")
    slots_reserved: int = Field(..., gt=0, description="Количество бронируемых мест")

class BookingOut(BaseModel):
    id: int
    user_id: int
    destination_id: int
    slots_reserved: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)



class BookingList(BaseModel):
    total: int
    bookings: List[BookingOut]