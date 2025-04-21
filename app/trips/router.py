from datetime import date, datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException

from app.trips.dao import TripDAO
from app.trips.schemas import STripCreate, STripUpdate, TripResponse, TripStatus
from app.users.dependencies import get_current_user
from app.users.models import User

router = APIRouter(
    prefix="/trips",
    tags=["Путевки"]
)


@router.post("")
async def create_trip(
    trip_data: STripCreate,
    current_user: User = Depends(get_current_user)
):
    start_date = trip_data.start_date if trip_data.start_date.tzinfo else trip_data.start_date.replace(tzinfo=timezone.utc)
    end_date = trip_data.end_date if trip_data.end_date.tzinfo else trip_data.end_date.replace(tzinfo=timezone.utc)
    
    if start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail="Дата начала не может быть позже даты окончания"
        )
    
    existing_trips = await TripDAO.find_all(user_id=current_user.id)
    for trip in existing_trips:
        trip_start = trip.start_date if trip.start_date.tzinfo else trip.start_date.replace(tzinfo=timezone.utc)
        trip_end = trip.end_date if trip.end_date.tzinfo else trip.end_date.replace(tzinfo=timezone.utc)
        
        if (start_date <= trip_end and end_date >= trip_start):
            raise HTTPException(
                status_code=400,
                detail="Даты пересекаются с существующим путешествием"
            )
    
    now = datetime.now(timezone.utc)
    if end_date < now:
        status = TripStatus.PAST
    elif start_date > now:
        status = TripStatus.FUTURE
    else:
        status = TripStatus.CURRENT
    
    new_trip = await TripDAO.add(
        user_id=current_user.id,
        destination_id=trip_data.destination_id,
        start_date=start_date.replace(tzinfo=None),
        end_date=end_date.replace(tzinfo=None),
        budget=trip_data.budget,
        status=status
    )
    
    return new_trip
    
    

@router.get("")
async def get_user_trips(
    status: str,
    current_user: User = Depends(get_current_user),
):
    trips = await TripDAO.find_all(user_id=current_user.id)
    
    if status:
        today = date.today()
        filtered_trips = []
        
        for trip in trips:
            if status == TripStatus.FUTURE and trip.start_date > today:
                filtered_trips.append(trip)
            elif status == TripStatus.PAST and trip.end_date < today:
                filtered_trips.append(trip)
            elif status == TripStatus.CURRENT and trip.start_date <= today <= trip.end_date:
                filtered_trips.append(trip)
        
        return filtered_trips
    
    return trips
    

@router.get("/{trip_id}")
async def get_trip(
    trip_id: int,
    current_user: User = Depends(get_current_user)
):
    trip = await TripDAO.find_by_id(trip_id)
    
    if not trip:
        raise HTTPException(
            status_code=404,
            detail="Путешествие не найдено"
        )
    
    if trip.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Нет прав для просмотра этого путешествия"
        )
    
    return trip
    

@router.put("/{trip_id}")
async def update_trip(
    trip_id: int,
    trip_data: STripUpdate,
    current_user: User = Depends(get_current_user)
):
    existing_trip = await TripDAO.find_by_id(trip_id)
    if not existing_trip:
        raise HTTPException(status_code=404, detail="Путешествие не найдено")

    if existing_trip.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Нет прав для редактирования этого путешествия")

    # Изменения здесь:
    update_data = trip_data.model_dump(exclude_unset=True)

    if "start_date" in update_data and "end_date" in update_data:
        if update_data["start_date"] > update_data["end_date"]:
            raise HTTPException(status_code=400, detail="Дата начала не может быть позже даты окончания")
    elif "start_date" in update_data and existing_trip.end_date:
        if update_data["start_date"] > existing_trip.end_date:
            raise HTTPException(status_code=400, detail="Дата начала не может быть позже даты окончания")
    elif "end_date" in update_data and existing_trip.start_date:
        if existing_trip.start_date > update_data["end_date"]:
            raise HTTPException(status_code=400, detail="Дата начала не может быть позже даты окончания")

    updated_trip = await TripDAO.update(trip_id, **update_data)

    return updated_trip

@router.delete("/{trip_id}")
async def delete_trip(
    trip_id: int,
    current_user: User = Depends(get_current_user)
):
    trip = await TripDAO.find_by_id(trip_id)
    
    if not trip:
        raise HTTPException(
            status_code=404,
            detail="Путешествие не найдено"
        )
    
    if trip.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Нет прав для удаления этого путешествия"
        )
    
    await TripDAO.delete(trip_id)
    
    return {"message": "Путешествие успешно удалено"}
    
