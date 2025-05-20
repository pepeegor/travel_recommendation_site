from sqlalchemy import String, Numeric, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.database import Base

class Attraction(Base):
    __tablename__ = "attractions"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000))
    approximate_price: Mapped[float | None] = mapped_column(Numeric(10,2))
    latitude: Mapped[float] = mapped_column(Numeric(10,8), nullable=False)
    longitude: Mapped[float] = mapped_column(Numeric(11,8), nullable=False)
    destination_id: Mapped[int] = mapped_column(ForeignKey("destinations.id"), nullable=False)

    destination = relationship("Destination", back_populates="attractions")
    routes = relationship(
        "RouteAttraction", back_populates="attraction", lazy='selectin'
    )
    
    def __str__(self) -> str:
        return f"{self.name} ({self.type})"