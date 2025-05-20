from app.dao.base import BaseDAO
from app.destinations.models import Destination
from sqlalchemy import func, or_, select
from app.database import async_session_maker
from app.reviews.models import Review
from app.trips.models import Trip

class DestinationDAO(BaseDAO):  
    model = Destination

    @classmethod
    async def find_all(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model)

            search_term = filter_by.pop('search', None)  
            if search_term:
                query = query.filter(
                    or_(
                        cls.model.name.ilike(f"%{search_term}%"),
                        cls.model.description.ilike(f"%{search_term}%"),
                        cls.model.country.ilike(f"%{search_term}%"),
                        cls.model.climate.ilike(f"%{search_term}%") 
                    )
                )

            min_budget = filter_by.pop('min_budget', None)
            max_budget = filter_by.pop('max_budget', None)
            if min_budget is not None or max_budget is not None:
                subquery = select(Trip.destination_id, func.avg(Trip.budget).label('avg_budget')).group_by(Trip.destination_id).subquery()
                query = query.outerjoin(subquery, cls.model.id == subquery.c.destination_id)
                if min_budget:
                    query = query.filter(or_(subquery.c.avg_budget >= min_budget, subquery.c.avg_budget.is_(None)))
                if max_budget:
                    query = query.filter(or_(subquery.c.avg_budget <= max_budget, subquery.c.avg_budget.is_(None)))

            for attr, value in filter_by.items():
                if isinstance(value, str):
                    query = query.filter(getattr(cls.model, attr).ilike(f"%{value}%"))
                else:
                    query = query.filter_by(**{attr: value})

            result = await session.execute(query)
            return result.scalars().all()
    
    @classmethod
    async def get_popular(cls, limit: int = 10):
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .join(cls.model.reviews)
                .group_by(cls.model.id)
                .order_by(func.count(Review.id).desc())
                .limit(limit)
            )
            
            result = await session.execute(query)
            return result.scalars().all()