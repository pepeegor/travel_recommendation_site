from sqlalchemy import delete, func, or_, select, update
from sqlalchemy.orm import selectinload
from app.attractions.models import Attraction
from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.routes.models import Route
from app.routes_attractions.models import RouteAttraction


class RouteDAO(BaseDAO):
    model = Route

    @classmethod
    async def find_by_id(cls, route_id: int) -> Route | None:
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .options(
                    selectinload(cls.model.destination),
                    selectinload(cls.model.trip),
                    selectinload(cls.model.attractions).selectinload(
                        RouteAttraction.attraction
                    ),
                )
                .filter(cls.model.id == route_id)
            )
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def find_by_user(cls, user_id: int) -> list[Route]:
        async with async_session_maker() as session:
            result = await session.execute(select(cls.model).filter_by(user_id=user_id))
            return result.scalars().all()

    @classmethod
    async def find_by_trip(cls, trip_id: int) -> list[Route]:
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(trip_id=trip_id)
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def find_published(
        cls,
        min_budget: float | None = None,
        max_budget: float | None = None,
        types: list[str] | None = None,
        destination_id: int | None = None,
        offset: int | None = None,
        limit: int | None = None,
    ) -> list[Route]:
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .options(
                    selectinload(cls.model.attractions).selectinload(
                        RouteAttraction.attraction
                    )
                )
                .where(cls.model.published == True)
            )

            if destination_id:
                query = query.filter_by(destination_id=destination_id)

            if min_budget is not None:
                query = query.filter(
                    or_(
                        cls.model.total_budget >= min_budget,
                        cls.model.total_budget.is_(None),
                    )
                )
            if max_budget is not None:
                query = query.filter(
                    or_(
                        cls.model.total_budget <= max_budget,
                        cls.model.total_budget.is_(None),
                    )
                )

            if types:
                query = (
                    query.join(RouteAttraction)
                    .join(Attraction)
                    .filter(Attraction.type.in_(types))
                )

            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)

            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def add_attraction(
        cls, route_id: int, attraction_id: int, position: int
    ) -> RouteAttraction:
        """
        Добавляем точку, а затем пересчитываем total_budget маршрута.
        """
        async with async_session_maker() as session:
            # 1) создаём связь
            assoc = RouteAttraction(
                route_id=route_id, attraction_id=attraction_id, position=position
            )
            session.add(assoc)
            await session.flush()

            # 2) пересчитываем суммарный бюджет по всем точкам этого маршрута
            total = (
                await session.execute(
                    select(func.coalesce(func.sum(Attraction.approximate_price), 0.0))
                    .join(
                        RouteAttraction, Attraction.id == RouteAttraction.attraction_id
                    )
                    .where(RouteAttraction.route_id == route_id)
                )
            ).scalar_one()

            # 3) обновляем маршрут
            await session.execute(
                update(Route).where(Route.id == route_id).values(total_budget=total)
            )

            await session.commit()
            await session.refresh(assoc)
            return assoc

    @classmethod
    async def publish_route(cls, route_id: int) -> Route:
        return await cls.update(route_id, published=True)

    @classmethod
    async def create(cls, trip_id: int, **data) -> Route:
        async with async_session_maker() as session:
            obj = cls.model(trip_id=trip_id, **data)
            session.add(obj)
            await session.commit()
            await session.refresh(obj)
            return obj

    @classmethod
    async def move_attraction(
        cls, route_id: int, assoc_id: int, position: int
    ) -> RouteAttraction:
        async with async_session_maker() as session:
            q = (
                update(RouteAttraction)
                .where(RouteAttraction.id == assoc_id)
                .values(position=position)
                .returning(RouteAttraction)
            )
            result = await session.execute(q)
            await session.commit()
            return result.scalar_one_or_none()

    @classmethod
    async def remove_attraction(cls, route_id: int, assoc_id: int) -> None:
        async with async_session_maker() as session:
            q = delete(RouteAttraction).where(RouteAttraction.id == assoc_id)
            await session.execute(q)
            await session.commit()

    @classmethod
    async def search(cls, q: str, limit: int = 20) -> list[Route]:
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .where(cls.model.published.is_(True), cls.model.name.ilike(f"%{q}%"))
                .limit(limit)
            )
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def update(cls, id: int, **data) -> Route | None:
        async with async_session_maker() as session:
            # 1) обновляем поля routes (кроме списка attractions)
            fields = {k: v for k, v in data.items() if k != "attractions"}
            if fields:
                await session.execute(
                    update(Route).where(Route.id == id).values(**fields)
                )

            # 2) полностью перезаписываем связи с достопримечательностями
            if "attractions" in data:
                # удаляем старые
                await session.execute(
                    delete(RouteAttraction).where(RouteAttraction.route_id == id)
                )
                # вставляем новые
                assoc_list = data["attractions"]
                for assoc in assoc_list:
                    session.add(
                        RouteAttraction(
                            route_id=id,
                            attraction_id=assoc["attraction_id"],
                            position=assoc["position"],
                        )
                    )

                # 3) считаем новый total_budget
                # собираем все id аттракшенов
                ids = [assoc["attraction_id"] for assoc in assoc_list]
                if ids:
                    # достаём все approximate_price
                    result = await session.execute(
                        select(Attraction.approximate_price).where(
                            Attraction.id.in_(ids)
                        )
                    )
                    prices = [row[0] or 0 for row in result.all()]
                    total = sum(prices)
                else:
                    total = None

                # обновляем поле в таблице routes
                await session.execute(
                    update(Route).where(Route.id == id).values(total_budget=total)
                )

            # 4) сохраняем и возвращаем полностью загруженный маршрут
            await session.commit()
            return await cls.find_by_id(id)
