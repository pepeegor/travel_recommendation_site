from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Integer, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.users.models import User
    from app.destinations.models import Destination
    

class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    destination_id: Mapped[int] = mapped_column(ForeignKey("destinations.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    slots_reserved: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint("slots_reserved > 0", name="positive_slots"),
    )

    user = relationship("User", back_populates="bookings")
    destination = relationship("Destination", back_populates="bookings")
    
    def __str__(self) -> str:
        return (
            f"Booking {self.id}: "
            f"user_id={self.user_id}, "
            f"destination_id={self.destination_id}, "
            f"slots_reserved={self.slots_reserved}"
        )







