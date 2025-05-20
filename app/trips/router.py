from datetime import datetime, timezone, date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.routes.dao import RouteDAO
from app.routes.schemas import SRouteOut, SRouteCreate
from app.trips.dao import TripDAO
from app.trips.models import Trip
from app.trips.schemas import STripCreate, STripUpdate, STripOut, TripStatus
from app.users.dependencies import get_current_user
from app.users.models import User

router = APIRouter(prefix="/trips", tags=["Путевки"])


@router.post(
    "",
    response_model=STripOut,
    status_code=status.HTTP_201_CREATED,
    summary="Создать поездку",
)
async def create_trip(
    trip_data: STripCreate, current_user: User = Depends(get_current_user)
):
    start = trip_data.start_date
    end = trip_data.end_date
    start = start if start.tzinfo else start.replace(tzinfo=timezone.utc)
    end = end if end.tzinfo else end.replace(tzinfo=timezone.utc)

    if start > end:
        raise HTTPException(400, "Дата начала не может быть позже даты окончания")

    existing = await TripDAO.find_all(user_id=current_user.id)
    for t in existing:
        ts = (
            t.start_date.replace(tzinfo=timezone.utc)
            if not t.start_date.tzinfo
            else t.start_date
        )
        te = (
            t.end_date.replace(tzinfo=timezone.utc)
            if not t.end_date.tzinfo
            else t.end_date
        )
        if start <= te and end >= ts:
            raise HTTPException(400, "Даты пересекаются с существующей поездкой")

    now = datetime.now(timezone.utc)
    status = (
        TripStatus.PAST
        if end < now
        else TripStatus.FUTURE if start > now else TripStatus.CURRENT
    )

    trip = await TripDAO.create(
        user_id=current_user.id,
        destination_id=trip_data.destination_id,
        start_date=start.replace(tzinfo=None),
        end_date=end.replace(tzinfo=None),
        budget=trip_data.budget,
        status=status,
    )
    return STripOut.model_validate(trip)


@router.get("", response_model=List[STripOut])
async def get_user_trips(
    status: Optional[str] = Query(
        None,
        description="planned | in_progress | completed — оставьте пустым, чтобы получить все",
    ),
    current_user: User = Depends(get_current_user),
):
    trips = await TripDAO.find_all(user_id=current_user.id)

    if status:
        try:
            status_enum = TripStatus(status)
            trips = [t for t in trips if t.status == status_enum.value]
        except ValueError:
            pass

    return [STripOut.model_validate(t) for t in trips]


@router.get("/{trip_id}", response_model=STripOut, summary="Детали поездки")
async def get_trip(trip_id: int, current_user: User = Depends(get_current_user)):
    trip = await TripDAO.find_by_id(trip_id)
    if not trip or trip.user_id != current_user.id:
        raise HTTPException(404, "Поездка не найдена")
    return STripOut.model_validate(trip)


@router.put("/{trip_id}", response_model=STripOut, summary="Обновить поездку")
async def update_trip(
    trip_id: int, trip_data: STripUpdate, current_user: User = Depends(get_current_user)
):
    existing = await TripDAO.find_by_id(trip_id)
    if not existing or existing.user_id != current_user.id:
        raise HTTPException(404, "Поездка не найдена")

    update = trip_data.model_dump(exclude_none=True)
    sd = update.get("start_date", existing.start_date)
    ed = update.get("end_date", existing.end_date)
    if sd > ed:
        raise HTTPException(400, "Дата начала не может быть позже даты окончания")

    trip = await TripDAO.update(trip_id, **update)
    return STripOut.model_validate(trip)


@router.delete(
    "/{trip_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Удалить поездку"
)
async def delete_trip(trip_id: int, current_user: User = Depends(get_current_user)):
    trip = await TripDAO.find_by_id(trip_id)
    if not trip or trip.user_id != current_user.id:
        raise HTTPException(404, "Поездка не найдена")
    await TripDAO.delete(trip_id)
    return


@router.get("/{trip_id}/routes", response_model=List[SRouteOut])
async def list_routes_for_trip(
    trip_id: int, current_user: User = Depends(get_current_user)
):
    # Сначала проверяем, что поездка существует и принадлежит текущему пользователю
    trip = await TripDAO.find_by_id(trip_id)
    if not trip or trip.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Путевка не найдена")

    # Получаем только ID маршрутов
    basic_routes = await RouteDAO.find_by_trip(trip_id)
    full_routes: List[SRouteOut] = []
    # Для каждого маршрута загружаем полные данные с selectinload
    for r in basic_routes:
        full = await RouteDAO.find_by_id(r.id)
        if not full:
            continue
        full_routes.append(full)
    return full_routes


@router.post(
    "/{trip_id}/routes",
    response_model=SRouteOut,
    status_code=status.HTTP_201_CREATED,
    summary="Создать маршрут в поездке",
)
async def create_route(
    trip_id: int, data: SRouteCreate, current_user: User = Depends(get_current_user)
):
    trip = await TripDAO.find_by_id(trip_id)
    if not trip or trip.user_id != current_user.id:
        raise HTTPException(404, "Поездка не найдена")
    route = await RouteDAO.create(
        trip_id=trip_id, user_id=current_user.id, **data.model_dump()
    )
    return SRouteOut.model_validate(route)
