from sqlalchemy import Boolean, DateTime, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime, timezone
from app.database import Base

class Route(Base):
    __tablename__ = "routes"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    trip_id: Mapped[int] = mapped_column(ForeignKey("trips.id"), nullable=True)
    destination_id: Mapped[int] = mapped_column(ForeignKey("destinations.id"), nullable=False)
    total_budget: Mapped[float | None] = mapped_column(Numeric(10,2))
    published: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user = relationship("User", back_populates="routes")
    trip = relationship("Trip", back_populates="routes")
    destination = relationship("Destination", back_populates="routes")
    attractions = relationship(
        "RouteAttraction", back_populates="route", lazy='selectin', cascade="all, delete-orphan"
    )
    
    def __str__(self) -> str:
        return f"{self.name}"