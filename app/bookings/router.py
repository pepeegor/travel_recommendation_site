from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.responses import RedirectResponse
from app.bookings.schemas import BookingCreate, BookingOut, BookingList
from app.bookings.dao import BookingDAO
from app.destinations.dao import DestinationDAO
from app.users.dependencies import get_current_user
from app.users.models import User

router = APIRouter(
    prefix="/bookings",
    tags=["Бронирования"]
)

@router.post("/", status_code=status.HTTP_302_FOUND)
async def create_booking(
    destination_id: int = Form(...),
    slots_reserved: int = Form(...),
    current_user: User = Depends(get_current_user)
):
    """
    Принимает данные из HTML-формы и создаёт бронь.
    После успешного создания — Redirect на страницу «Мои бронирования».
    """
    try:
        booking = await BookingDAO.create(
            user_id=current_user.id,
            destination_id=destination_id,
            slots=slots_reserved
        )
    except ValueError as e:
        return RedirectResponse(
            url=f"/pages/bookings/create?destination_id={destination_id}&error={e}",
            status_code=status.HTTP_302_FOUND
        )

    # После успешной брони — редиректим на страницу списка своих бронирований
    return RedirectResponse(url="/pages/bookings/my", status_code=status.HTTP_302_FOUND)

@router.get(
    "/me",
    response_model=BookingList
)
async def get_my_bookings(
    current_user: User = Depends(get_current_user)
):
    """
    Получить список своих бронирований
    """
    bookings = await BookingDAO.find_by_user(current_user.id)
    return BookingList(
        total=len(bookings),
        bookings=bookings
    )

@router.get(
    "/destination/{destination_id}",
    response_model=BookingList
)
async def get_bookings_by_destination(
    destination_id: int
):
    """
    Получить все бронирования для указанного направления
    """
    bookings = await BookingDAO.find_all(destination_id=destination_id)
    return BookingList(
        total=len(bookings),
        bookings=bookings
    )
    
@router.delete(
    "/{booking_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Удалить бронь: проверяет принадлежность, восстанавливает слоты и удаляет запись.
    """
    # 1. Получаем бронь
    booking = await BookingDAO.find_by_id(booking_id)
    if not booking or booking.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Бронирование не найдено")

    # 2. Восстанавливаем свободные места у направления
    dest = await DestinationDAO.find_by_id(booking.destination_id)
    if dest:
        new_slots = (dest.available_slots or 0) + booking.slots_reserved
        await DestinationDAO.update(dest.id, available_slots=new_slots)

    # 3. Удаляем бронь
    await BookingDAO.delete(booking_id)

    # 4. Возвращаем 204 No Content
    return