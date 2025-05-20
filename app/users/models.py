from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(255), default="user")
    registration_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    trips = relationship("Trip", back_populates="user")
    reviews = relationship("Review", back_populates="user")
    routes = relationship("Route", back_populates="user")
    bookings = relationship("Booking", back_populates="user")

    def __str__(self) -> str:
        return f"{self.id}: {self.username} ({self.email}) - {self.role}"
