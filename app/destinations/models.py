from typing import TYPE_CHECKING, Optional
from sqlalchemy import Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.trips.models import Trip
    from app.reviews.models import Review
    from app.bookings.models import Booking


class Destination(Base):
    __tablename__ = "destinations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(String(1000))
    country: Mapped[str] = mapped_column(String(100))
    climate: Mapped[str] = mapped_column(String(100))
    approximate_price: Mapped[float] = mapped_column(Numeric(10, 2))
    latitude: Mapped[float] = mapped_column(Numeric(10, 8))
    longitude: Mapped[float] = mapped_column(Numeric(11, 8))
    image_url: Mapped[Optional[str]] = mapped_column(String(500))
    available_slots: Mapped[int] = mapped_column(Integer, default=0, nullable=True)

    trips = relationship("Trip", back_populates="destination", lazy="selectin")
    reviews = relationship("Review", back_populates="destination", lazy="selectin")
    attractions = relationship(
        "Attraction",
        back_populates="destination",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    routes = relationship("Route", back_populates="destination", lazy="selectin")
    bookings = relationship("Booking", back_populates="destination")

    def __str__(self) -> str:
        return f"{self.name} - {self.country}"
