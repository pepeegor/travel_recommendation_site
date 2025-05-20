from typing import Optional
from sqlalchemy import select
from app.attractions.models import Attraction
from app.dao.base import BaseDAO
from app.database import async_session_maker


class AttractionDAO(BaseDAO):
    model = Attraction

    @classmethod
    async def find_by_destination(cls, destination_id: int) -> list[Attraction]:
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(destination_id=destination_id)
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def find_by_type(cls, type_name: str) -> list[Attraction]:
        async with async_session_maker() as session:
            query = select(cls.model).filter(cls.model.type.ilike(f"%{type_name}%"))
            result = await session.execute(query)
            return result.scalars().all()
        
    @classmethod
    async def create(
        cls,
        *,
        name: str,
        type: str,
        latitude: float,
        longitude: float,
        destination_id: int,
        description: Optional[str] = None,
        approximate_price: Optional[float] = None,
    ) -> Attraction:
        async with async_session_maker() as session:
            attraction = cls.model(
                name=name,
                type=type,
                description=description,
                approximate_price=approximate_price,
                latitude=latitude,
                longitude=longitude,
                destination_id=destination_id
            )
            session.add(attraction)
            await session.commit()
            await session.refresh(attraction)
            return attraction