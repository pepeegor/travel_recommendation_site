from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.destinations.dao import DestinationDAO
from app.destinations.models import Destination
from app.destinations.schemas import SDestinationCreate, SDestinationUpdate
from app.users.dependencies import get_current_admin_user
from app.users.models import User

router = APIRouter(
    prefix="/destinations",
    tags=["Пути"]
)

@router.post("")
async def create_destination(
    destination_data: SDestinationCreate,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Создание нового направления (только для администраторов).
    """
    try:
        new_destination = await DestinationDAO.add(
            name=destination_data.name,
            description=destination_data.description,
            country=destination_data.country,
            climate=destination_data.climate,
            approximate_price=destination_data.approximate_price,
            latitude=destination_data.latitude,
            longitude=destination_data.longitude,
            image_url=destination_data.image_url
        )
        new_dest = await DestinationDAO.find_one_or_none(name=destination_data.name) 
        return new_dest
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("")  # Обратите внимание на response_class
async def get_destinations(
    country: Optional[str] = None,
    min_budget: Optional[float] = None,
    max_budget: Optional[float] = None,
    search: Optional[str] = None,  # Добавляем параметр search
    page: int = 1,
    limit: int = 20,
):
    """
    API endpoint для получения списка направлений с фильтрацией и поиском.
    """
    filters = {}
    if country:
        filters["country"] = country

    if search:
        filters["search"] = search  # Добавляем search в фильтры

    destinations = await DestinationDAO.find_all(**filters)

    if min_budget is not None or max_budget is not None:
        filtered_destinations = []
        for dest in destinations:
            trips = dest.trips

            valid_budget = True
            if trips:
                avg_budget = (
                    sum(trip.budget for trip in trips if trip.budget) / len(trips)
                    if trips
                    else 0
                )
                if min_budget and avg_budget < min_budget:
                    valid_budget = False
                if max_budget and avg_budget > max_budget:
                    valid_budget = False

            if valid_budget:
                filtered_destinations.append(dest)

        destinations = filtered_destinations

    start_idx = (page - 1) * limit
    end_idx = start_idx + limit

    return destinations[start_idx:end_idx]



@router.get("/popular")
async def get_popular_destinations():
    return await DestinationDAO.get_popular(limit=10)


@router.get("/search")
async def search_destinations(query: str):
    
    if not query or len(query.strip()) < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Поисковый запрос не может быть пустым"
        )
    
    destinations = await DestinationDAO.find_all(name=query)
    return destinations[:20]


@router.get("/{destination_id}")
async def get_destination_by_id(destination_id: int):
    
    destination = await DestinationDAO.find_by_id(destination_id)
    if not destination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Направление не найдено"
        )
        
    return destination


@router.put("/{destination_id}")
async def update_destination(
    destination_id: int,
    destination_data: SDestinationUpdate,  # Используем схему для валидации
    current_user: User = Depends(get_current_admin_user)  # Только для администраторов
):
    """
    Обновление данных направления (только для администраторов).
    """
    destination = await DestinationDAO.update(destination_id, **destination_data.dict())
    if not destination:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Destination not found")
    return destination


@router.delete("/{destination_id}")
async def delete_destination(
    destination_id: int,
    current_user: User = Depends(get_current_admin_user)  # Только для администраторов
):
    """
    Удаление направления (только для администраторов)
    """
    await DestinationDAO.delete(destination_id)
    return {"message": "Destination deleted successfully"}

