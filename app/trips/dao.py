from typing import Optional
from sqlalchemy import select
from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.destinations.models import Destination
from app.trips.models import Trip

class TripDAO(BaseDAO):
    
    model = Trip
    
    @classmethod
    async def get_destination_name_by_trip_id(cls, trip_id: int) -> Optional[str]:
        async with async_session_maker() as session:
            query = (
                select(Destination.name)
                .join(Trip, Trip.destination_id == Destination.id)
                .filter(Trip.id == trip_id)
            )
            result = await session.execute(query)
            destination_name = result.scalar_one_or_none()
            return destination_name