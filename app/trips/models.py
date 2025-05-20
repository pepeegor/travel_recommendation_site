from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.users.models import User
    from app.destinations.models import Destination
    from app.routes.models import Route

class Trip(Base):
    __tablename__ = "trips"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    destination_id: Mapped[int] = mapped_column(ForeignKey("destinations.id"))
    start_date: Mapped[datetime] = mapped_column(DateTime)
    end_date: Mapped[datetime] = mapped_column(DateTime)
    budget: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    status: Mapped[str] = mapped_column(String(50))
    
    user = relationship("User", back_populates="trips", lazy="selectin")
    destination = relationship("Destination", back_populates="trips", lazy="selectin")
    routes = relationship("Route", back_populates="trip", lazy='selectin', cascade="all, delete-orphan")
    
    def __str__(self) -> str:
        user_part = self.user.username if self.user else f"User#{self.user_id}"
        dest_part = self.destination.name if self.destination else f"Dest#{self.destination_id}"
        dates = f"{self.start_date:%d.%m.%Y}–{self.end_date:%d.%m.%Y}"
        return f"{user_part}: {dest_part} ({dates})"