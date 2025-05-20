from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.attractions.dao import AttractionDAO
from app.attractions.schemas import SAttractionCreate, SAttractionOut
from app.destinations.dao import DestinationDAO
from app.destinations.schemas import SDestinationCreate, SDestinationOut, SDestinationUpdate
from app.users.dependencies import get_current_admin_user, get_current_user
from app.users.models import User

router = APIRouter(
    prefix="/destinations",
    tags=["Пути"]
)

# Создать новое направление (только админ)
@router.post(
    "",
    response_model=SDestinationOut,
    status_code=status.HTTP_201_CREATED
)
async def create_destination(
    destination_data: SDestinationCreate,
    current_user: User = Depends(get_current_admin_user)
):
    try:
        await DestinationDAO.add(
            name=destination_data.name,
            description=destination_data.description,
            country=destination_data.country,
            climate=destination_data.climate,
            approximate_price=destination_data.approximate_price,
            latitude=destination_data.latitude,
            longitude=destination_data.longitude,
            image_url=destination_data.image_url
        )
        dest = await DestinationDAO.find_one_or_none(name=destination_data.name)
        return dest
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# Список достопримечательностей по направлению
@router.get(
    "/{destination_id}/attractions",
    response_model=List[SAttractionOut]
)
async def list_attractions(
    destination_id: int,
    current_user: User = Depends(get_current_user)
):
    dest = await DestinationDAO.find_by_id(destination_id)
    if not dest:
        raise HTTPException(status_code=404, detail="Направление не найдено")
    return await AttractionDAO.find_by_destination(destination_id)

# Создать достопримечательность в направлении (только админ)
@router.post(
    "/{destination_id}/attractions",
    response_model=SAttractionOut,
    status_code=status.HTTP_201_CREATED
)
async def create_attraction(
    destination_id: int,
    data: SAttractionCreate,
    current_user: User = Depends(get_current_admin_user)
):
    dest = await DestinationDAO.find_by_id(destination_id)
    if not dest:
        raise HTTPException(status_code=404, detail="Направление не найдено")
    return await AttractionDAO.add(
        name=data.name,
        type=data.type,
        description=data.description,
        approximate_price=data.approximate_price,
        latitude=data.latitude,
        longitude=data.longitude,
        destination_id=destination_id
    )

# Получить списковое представление направлений
@router.get(
    "",
    response_model=List[SDestinationOut]
)
async def get_destinations(
    country: Optional[str] = Query(None),
    min_budget: Optional[float] = Query(None, ge=0),
    max_budget: Optional[float] = Query(None, ge=0),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    filters = {}
    if country:
        filters["country"] = country
    if search:
        filters["search"] = search

    dests = await DestinationDAO.find_all(**filters)

    # Фильтрация по бюджету
    if min_budget is not None or max_budget is not None:
        filtered = []
        for d in dests:
            trips = d.trips
            if trips:
                avg = sum(t.budget or 0 for t in trips) / len(trips)
            else:
                avg = 0
            if (min_budget is None or avg >= min_budget) and \
               (max_budget is None or avg <= max_budget):
                filtered.append(d)
        dests = filtered

    start = (page - 1) * limit
    return dests[start:start + limit]

# Популярные направления
@router.get(
    "/popular",
    response_model=List[SDestinationOut]
)
async def get_popular_destinations():
    return await DestinationDAO.get_popular(limit=10)

# Поиск направлений
@router.get(
    "/search",
    response_model=List[SDestinationOut]
)
async def search_destinations(
    query: str = Query(..., min_length=1)
):
    dests = await DestinationDAO.find_all(search=query)
    return dests[:20]

# Детали одного направления
@router.get(
    "/{destination_id}",
    response_model=SDestinationOut
)
async def get_destination_by_id(destination_id: int):
    dest = await DestinationDAO.find_by_id(destination_id)
    if not dest:
        raise HTTPException(status_code=404, detail="Направление не найдено")
    return dest

# Обновить направление (только админ)
@router.put(
    "/{destination_id}",
    response_model=SDestinationOut
)
async def update_destination(
    destination_id: int,
    destination_data: SDestinationUpdate,
    current_user: User = Depends(get_current_admin_user)
):
    updated = await DestinationDAO.update(destination_id, **destination_data.dict())
    if not updated:
        raise HTTPException(status_code=404, detail="Направление не найдено")
    return updated

@router.delete(
    "/{destination_id}",
    response_model=dict
)
async def delete_destination(
    destination_id: int,
    current_user: User = Depends(get_current_admin_user)
):
    await DestinationDAO.delete(destination_id)
    return {"detail": "Destination deleted successfully"}
