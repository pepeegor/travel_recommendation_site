from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.users.models import User
    from app.destinations.models import Destination

class Trip(Base):
    __tablename__ = "trips"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    destination_id: Mapped[int] = mapped_column(ForeignKey("destinations.id"))
    start_date: Mapped[datetime] = mapped_column(DateTime)
    end_date: Mapped[datetime] = mapped_column(DateTime)
    budget: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    status: Mapped[str] = mapped_column(String(50))
    
    user = relationship("User", back_populates="trips")
    destination = relationship("Destination", back_populates="trips")