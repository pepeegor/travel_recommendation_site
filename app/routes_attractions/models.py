from sqlalchemy import Boolean, DateTime, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime, timezone
from app.database import Base


class RouteAttraction(Base):
    __tablename__ = "route_attractions"

    id: Mapped[int] = mapped_column(primary_key=True)
    route_id: Mapped[int] = mapped_column(ForeignKey("routes.id"), nullable=False)
    attraction_id: Mapped[int] = mapped_column(ForeignKey("attractions.id"), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False) 

    route = relationship("Route", back_populates="attractions")
    attraction = relationship("Attraction", back_populates="routes")
