from typing import List

from sqlalchemy import func, select, update
from app.dao.base import BaseDAO
from app.reviews.models import Review
from app.reviews.schemas import SReviewOut
from app.database import async_session_maker
from app.users.models import User


class ReviewDAO(BaseDAO):
    
    model = Review
    
    @classmethod
    async def update(cls, id: int, **data):
        async with async_session_maker() as session:
            query = (
                update(cls.model)
                .where(cls.model.id == id)
                .values(**data)
                .returning(cls.model)
            )
            result = await session.execute(query)
            await session.commit()
            return result.scalar_one_or_none()
    
    @classmethod
    async def find_all(
        cls,
        where_clause=None,
        order_by=None,
        offset=None,
        limit=None
    ):
        async with async_session_maker() as session:
            query = select(cls.model)
            if where_clause:
                for key, value in where_clause.items():
                    query = query.where(getattr(cls.model, key) == value)
            if order_by:
                query = query.order_by(*order_by)
            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)
            result = await session.execute(query)
            return result.scalars().all()
        
    @classmethod
    async def find_by_destination_id(cls, destination_id: int) -> List[SReviewOut]:
        async with async_session_maker() as session:
            q = (
                select(
                    Review.id,
                    Review.user_id,
                    Review.destination_id,
                    Review.rating,
                    Review.comment,
                    Review.created_at,
                    User.username,
                )
                .join(User, Review.user_id == User.id)
                .where(Review.destination_id == destination_id)
            )
            result = await session.execute(q)
            reviews: List[SReviewOut] = []
            for id_, user_id, dest_id, rating, comment, created_at, username in result.all():
                reviews.append(
                    SReviewOut(
                        id=id_,
                        user_id=user_id,
                        destination_id=dest_id,
                        rating=rating,
                        comment=comment,
                        created_at=created_at,
                        username=username,
                    )
                )
            return reviews
        
    @classmethod
    async def count(cls, where_clause=None):
        async with async_session_maker() as session:
            query = select(func.count()).select_from(cls.model)
            if where_clause:
                query = query.where(where_clause)
            result = await session.execute(query)
            return result.scalar_one()
        
    @classmethod
    async def get_average_rating(cls, destination_id: int):
        async with async_session_maker() as session:
            query = (
                select(func.avg(Review.rating).label("average_rating"))
                .where(Review.destination_id == destination_id)
            )
            result = await session.execute(query)
            return result.scalar_one_or_none()
    