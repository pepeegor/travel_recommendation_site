from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.database import async_session_maker
from app.bookings.models import Booking
from app.destinations.models import Destination
from app.dao.base import BaseDAO 


class BookingDAO(BaseDAO):
    model = Booking

    @classmethod
    async def create(cls, user_id: int, destination_id: int, slots: int):
        """
        Создать бронь: проверить, что destination существует и хватает available_slots,
        уменьшить available_slots и сохранить запись в bookings.
        """
        async with async_session_maker() as session:
            dest = await session.get(Destination, destination_id)
            if not dest:
                raise ValueError("Destination not found")

            if dest.available_slots < slots:
                raise ValueError("Not enough slots available")

            dest.available_slots -= slots
            booking = Booking(
                user_id=user_id,
                destination_id=destination_id,
                slots_reserved=slots
            )
            session.add(booking)

            try:
                await session.commit()
            except IntegrityError:
                await session.rollback()
                raise

            return booking

    @classmethod
    async def find_by_user(cls, user_id: int):
        """
        Вернуть все бронирования заданного пользователя.
        """
        return await cls.find_all(user_id=user_id)
