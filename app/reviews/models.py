from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.destinations.models import Destination
    from app.users.models import User

class Review(Base):
    __tablename__ = "reviews"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    destination_id: Mapped[int] = mapped_column(ForeignKey("destinations.id"))
    rating: Mapped[int] = mapped_column(Integer)
    comment: Mapped[Optional[str]] = mapped_column(String(1000))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    
    # Добавляем ограничение на рейтинг
    __table_args__ = (
        CheckConstraint('rating >= 1 AND rating <= 5', name='valid_rating'),
    )
    
    user = relationship("User", back_populates="reviews")
    destination = relationship("Destination", back_populates="reviews")