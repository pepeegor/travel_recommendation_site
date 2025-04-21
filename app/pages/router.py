from datetime import datetime, timedelta
from typing import Counter
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.destinations.dao import DestinationDAO
from app.reviews.dao import ReviewDAO
from app.trips.dao import TripDAO
from app.users.dao import UserDAO
from app.users.dependencies import get_current_admin_user, get_current_user, get_token
from app.users.models import User
from app.exceptions import ExpiredTokenException, AbsentTokenException, IncorrectTokenFormatException, UserIsNotPresentException

router = APIRouter(
    prefix="/pages",
    tags=["Фронтенд"]
)

templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Главная страница доступна всем пользователям.
    Пытаемся получить текущего пользователя, но не требуем авторизации
    """
    try:
        token = get_token(request)
        current_user = await get_current_user(token)
    except HTTPException:
        current_user = None
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "current_user": current_user
    })

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {
        "request": request,
        "current_user": None
    })

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("auth/register.html", {
        "request": request,
        "current_user": None
    })

@router.get("/trips/create", response_class=HTMLResponse)
async def create_trip_page(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
    Страница создания путешествия доступна только авторизованным пользователям.
    FastAPI автоматически вернет 401 при отсутствии валидного токена.
    """
    destinations = await DestinationDAO.find_all()
    return templates.TemplateResponse("trips/create_trip.html", {
        "request": request,
        "current_user": current_user,
        "destinations": destinations
    })
    
@router.get("/trips/{trip_id}", response_class=HTMLResponse)
async def trip_details_page(
    request: Request,
    trip_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Страница с подробной информацией о путешествии.
    """
    try:
        trip = await TripDAO.find_by_id(trip_id)
        destination = await DestinationDAO.find_by_id(trip.destination_id)
    except UserIsNotPresentException:
        raise HTTPException(status_code=404, detail="Trip not found")
    return templates.TemplateResponse("trips/trip_details.html", {
        "request": request,
        "current_user": current_user,
        "trip": trip,
        "destination": destination
    })
    
@router.get("/trips", response_class=HTMLResponse)
async def trips_page(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
    Страница путешествий доступна только авторизованным пользователям.
    FastAPI автоматически вернет 401 при отсутствии валидного токена.
    """
    return templates.TemplateResponse("trips/index.html", {
        "request": request,
        "current_user": current_user
    })
    


@router.get("/profile", response_class=HTMLResponse)
async def profile_page(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
    Страница профиля доступна только авторизованным пользователям.
    FastAPI автоматически вернет 401 при отсутствии валидного токена.
    """
    destinations = await DestinationDAO.find_all()  # Fetch destinations here
    return templates.TemplateResponse("profile/index.html", {
        "request": request,
        "current_user": current_user,
        "destinations": destinations  # Pass destinations to the template
    })
    


@router.get("/destinations/{destination_id}", response_class=HTMLResponse)
async def destination_details_page(
    request: Request,
    destination_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Страница с подробной информацией о направлении.
    """
    try:
        destination = await DestinationDAO.find_by_id(destination_id)
        reviews = await ReviewDAO.find_by_destination_id(destination_id)
    except UserIsNotPresentException:
        raise HTTPException(status_code=404, detail="Destination not found")
    return templates.TemplateResponse("destinations/destination_details.html", {
        "request": request,
        "current_user": current_user,
        "destination": destination,
        "reviews": reviews
    })
    


@router.get("/destinations", response_class=HTMLResponse)
async def destinations_page(request: Request, current_user: User = Depends(get_current_user)):
    """
    Страница со списком направлений.
    """
    destinations = await DestinationDAO.find_all()
    return templates.TemplateResponse(
        "destinations/index.html",
        {
            "request": request,
            "current_user": current_user,
            "destinations": destinations,
        },
    )

@router.get("/reviews/{review_id}", response_class=HTMLResponse)
async def review_details_page(
    request: Request,
    review_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Страница с подробной информацией об отзыве.
    """
    try:
        review = await ReviewDAO.find_by_id(review_id)
        if not review:
            raise HTTPException(status_code=404, detail="Отзыв не найден")
        destination = await DestinationDAO.find_by_id(review.destination_id)
    except UserIsNotPresentException:
        raise HTTPException(status_code=404, detail="Review not found")
    return templates.TemplateResponse("profile/review_details.html", {
        "request": request,
        "current_user": current_user,
        "review": review,
        "destination": destination
    })
    

@router.get("/admin", response_class=HTMLResponse)
async def admin_panel_page(
    request: Request,
    current_user: User = Depends(get_current_admin_user)  # Используем get_current_admin_user
):
    """
    Страница админ панели доступна только администраторам.
    """
    users = await UserDAO.find_all()  # Получаем всех пользователей
    destinations = await DestinationDAO.find_all()  # Получаем все направления

    return templates.TemplateResponse("admin/index.html", {
        "request": request,
        "current_user": current_user,
        "users": users,
        "destinations": destinations
    })
    

from collections import Counter
from datetime import datetime, timedelta

# ... твои импорты ...

@router.get("/statistics")
async def get_statistics():
    # 1. Количество поездок по месяцам за последний год
    current_date = datetime.now()
    one_year_ago = current_date - timedelta(days=365) 
    trips = await TripDAO.find_all()

    trips_per_month = dict(Counter(trip.start_date.month for trip in trips if trip.start_date >= one_year_ago))

    # 2. Топ 5 самых популярных направлений (с количеством поездок)
    top_destinations = await DestinationDAO.get_popular(limit=5) 
    #  Преобразуем данные для графика 2
    top_destinations_data = []
    for dest in top_destinations:
        trip_count = len(dest.trips)  #  Получаем количество поездок из списка trips
        top_destinations_data.append({
            "name": dest.name,
            "trip_count": trip_count
        })

    # 3. Средний рейтинг направлений
    avg_ratings = {}
    destinations = await DestinationDAO.find_all()
    for destination in destinations:
        avg_rating = await ReviewDAO.get_average_rating(destination.id) 
        if avg_rating is not None:
            avg_ratings[destination.name] = avg_rating 
    # 4. Распределение рейтинга по всем отзывам
    reviews = await ReviewDAO.find_all()
    rating_distribution = dict(Counter(review.rating for review in reviews))

    # 5.  Соотношение цены и рейтинга направлений
    price_rating_relation = []
    for destination in top_destinations:
        destination_reviews = await ReviewDAO.find_by_destination_id(destination.id)
        if destination_reviews:
            avg_rating = sum(review.rating for review in destination_reviews) / len(destination_reviews)
            price_rating_relation.append({
                "price": destination.approximate_price,
                "rating": avg_rating
            })

    return {
        "trips_per_month": trips_per_month,
        "top_destinations": top_destinations_data,
        "avg_ratings": avg_ratings,
        "rating_distribution": rating_distribution,
        "price_rating_relation": price_rating_relation
    }