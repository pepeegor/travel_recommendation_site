from datetime import datetime, timedelta
from typing import Counter
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.bookings.dao import BookingDAO
from app.destinations.dao import DestinationDAO
from app.reviews.dao import ReviewDAO
from app.routes.dao import RouteDAO
from app.trips.dao import TripDAO
from app.users.dao import UserDAO
from app.users.dependencies import get_current_admin_user, get_current_user, get_token
from app.users.models import User
from app.exceptions import (
    ExpiredTokenException,
    AbsentTokenException,
    IncorrectTokenFormatException,
    UserIsNotPresentException,
)

from collections import Counter
from datetime import datetime, timedelta

router = APIRouter(prefix="/pages", tags=["Фронтенд"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    try:
        token = get_token(request)
        current_user = await get_current_user(token)
    except HTTPException:
        current_user = None

    return templates.TemplateResponse(
        "index.html", {"request": request, "current_user": current_user}
    )


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(
        "auth/login.html", {"request": request, "current_user": None}
    )


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse(
        "auth/register.html", {"request": request, "current_user": None}
    )


@router.get("/trips/create", response_class=HTMLResponse)
async def create_trip_page(
    request: Request, current_user: User = Depends(get_current_user)
):
    destinations = await DestinationDAO.find_all()
    return templates.TemplateResponse(
        "trips/create_trip.html",
        {
            "request": request,
            "current_user": current_user,
            "destinations": destinations,
        },
    )


@router.get("/trips/{trip_id}", response_class=HTMLResponse)
async def trip_details_page(
    request: Request, trip_id: int, current_user: User = Depends(get_current_user)
):
    try:
        trip = await TripDAO.find_by_id(trip_id)
        destination = await DestinationDAO.find_by_id(trip.destination_id)
    except UserIsNotPresentException:
        raise HTTPException(status_code=404, detail="Trip not found")
    return templates.TemplateResponse(
        "trips/trip_details.html",
        {
            "request": request,
            "current_user": current_user,
            "trip": trip,
            "destination": destination,
        },
    )


@router.get("/trips", response_class=HTMLResponse)
async def trips_page(request: Request, current_user: User = Depends(get_current_user)):
    return templates.TemplateResponse(
        "trips/index.html", {"request": request, "current_user": current_user}
    )


@router.get("/profile", response_class=HTMLResponse)
async def profile_page(
    request: Request, current_user: User = Depends(get_current_user)
):
    destinations = await DestinationDAO.find_all()
    return templates.TemplateResponse(
        "profile/index.html",
        {
            "request": request,
            "current_user": current_user,
            "destinations": destinations,
        },
    )


@router.get("/destinations/{destination_id}", response_class=HTMLResponse)
async def destination_details_page(
    request: Request,
    destination_id: int,
    current_user: User = Depends(get_current_user),
):
    try:
        destination = await DestinationDAO.find_by_id(destination_id)
        reviews = await ReviewDAO.find_by_destination_id(destination_id)
    except UserIsNotPresentException:
        raise HTTPException(status_code=404, detail="Destination not found")
    return templates.TemplateResponse(
        "destinations/destination_details.html",
        {
            "request": request,
            "current_user": current_user,
            "destination": destination,
            "reviews": reviews,
        },
    )


@router.get("/destinations", response_class=HTMLResponse)
async def destinations_page(
    request: Request, current_user: User = Depends(get_current_user)
):
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
    request: Request, review_id: int, current_user: User = Depends(get_current_user)
):
    try:
        review = await ReviewDAO.find_by_id(review_id)
        if not review:
            raise HTTPException(status_code=404, detail="Отзыв не найден")
        destination = await DestinationDAO.find_by_id(review.destination_id)
    except UserIsNotPresentException:
        raise HTTPException(status_code=404, detail="Review not found")
    return templates.TemplateResponse(
        "profile/review_details.html",
        {
            "request": request,
            "current_user": current_user,
            "review": review,
            "destination": destination,
        },
    )


@router.get("/admin", response_class=HTMLResponse)
async def admin_panel_page(
    request: Request,
    current_user: User = Depends(get_current_admin_user),
):
    users = await UserDAO.find_all()
    destinations = await DestinationDAO.find_all()

    return templates.TemplateResponse(
        "admin/index.html",
        {
            "request": request,
            "current_user": current_user,
            "users": users,
            "destinations": destinations,
        },
    )


@router.get("/statistics")
async def get_statistics():
    current_date = datetime.now()
    one_year_ago = current_date - timedelta(days=365)
    trips = await TripDAO.find_all()

    trips_per_month = dict(
        Counter(
            trip.start_date.month for trip in trips if trip.start_date >= one_year_ago
        )
    )

    top_destinations = await DestinationDAO.get_popular(limit=5)
    top_destinations_data = []
    for dest in top_destinations:
        trip_count = len(dest.trips)
        top_destinations_data.append({"name": dest.name, "trip_count": trip_count})

    avg_ratings = {}
    destinations = await DestinationDAO.find_all()
    for destination in destinations:
        avg_rating = await ReviewDAO.get_average_rating(destination.id)
        if avg_rating is not None:
            avg_ratings[destination.name] = avg_rating
    reviews = await ReviewDAO.find_all()
    rating_distribution = dict(Counter(review.rating for review in reviews))

    price_rating_relation = []
    for destination in top_destinations:
        destination_reviews = await ReviewDAO.find_by_destination_id(destination.id)
        if destination_reviews:
            avg_rating = sum(review.rating for review in destination_reviews) / len(
                destination_reviews
            )
            price_rating_relation.append(
                {"price": destination.approximate_price, "rating": avg_rating}
            )

    return {
        "trips_per_month": trips_per_month,
        "top_destinations": top_destinations_data,
        "avg_ratings": avg_ratings,
        "rating_distribution": rating_distribution,
        "price_rating_relation": price_rating_relation,
    }


@router.get("/routes", response_class=HTMLResponse)
async def public_routes_page(request: Request):
    try:
        token = get_token(request)
        current_user = await get_current_user(token)
    except HTTPException:
        current_user = None

    destinations = await DestinationDAO.find_all()
    return templates.TemplateResponse(
        "routes/routes.html",
        {
            "request": request,
            "current_user": current_user,
            "destinations": destinations,
        },
    )


@router.get("/my-routes", response_class=HTMLResponse)
async def my_routes_page(
    request: Request, current_user: User = Depends(get_current_user)
):
    # получаем все маршруты пользователя
    routes = await RouteDAO.find_by_user(current_user.id)
    # загружаем все направления один раз
    destinations = await DestinationDAO.find_all()

    # собираем непустые группы: [(destination, [route, ...]), ...]
    groups: list[dict] = []
    for dest in destinations:
        dest_routes = [r for r in routes if r.destination_id == dest.id]
        if dest_routes:
            groups.append({"destination": dest, "routes": dest_routes})

    return templates.TemplateResponse(
        "routes/my_routes.html",
        {"request": request, "current_user": current_user, "groups": groups},
    )


@router.get("/routes/create", response_class=HTMLResponse)
async def create_route_page(
    request: Request, current_user: User = Depends(get_current_user)
):
    trips = await TripDAO.find_all(user_id=current_user.id)
    destinations = await DestinationDAO.find_all()
    return templates.TemplateResponse(
        "routes/routes_create.html",
        {
            "request": request,
            "current_user": current_user,
            "trips": trips,
            "destinations": destinations,
        },
    )


@router.get("/routes/{route_id}/edit", response_class=HTMLResponse)
async def edit_route_page(
    request: Request,
    route_id: int,
    current_user: User = Depends(get_current_user),
):
    # 1) достаём маршрут
    route = await RouteDAO.find_by_id(route_id)
    if not route or route.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Маршрут не найден")

    # 2) список поездок пользователя
    trips = await TripDAO.find_all(user_id=current_user.id)

    # 3) строим JSON со всеми точками
    points = []
    for assoc in sorted(route.attractions, key=lambda a: a.position):
        att = assoc.attraction
        points.append(
            {
                "position": assoc.position,
                "attraction": {
                    "id": att.id,
                    "name": att.name,
                    "type": att.type,
                    "latitude": float(att.latitude),
                    "longitude": float(att.longitude),
                },
            }
        )

    route_json = {
        "id": route.id,
        "name": route.name,
        "trip_id": route.trip_id,
        "destination_id": route.destination_id,
        "points": points,
    }

    return templates.TemplateResponse(
        "routes/routes_edit.html",
        {
            "request": request,
            "current_user": current_user,
            "trips": trips,
            "route_json": route_json,
        },
    )


@router.get(
    "/trips/{trip_id}/routes",
    response_class=HTMLResponse,
    summary="Маршруты поездки"
)
async def trip_routes_page(
    request: Request,
    trip_id: int,
    current_user: User = Depends(get_current_user)
):
    trip = await TripDAO.find_by_id(trip_id)
    if not trip or trip.user_id != current_user.id:
        raise HTTPException(404, "Путешествие не найдено")

    routes = await RouteDAO.find_by_trip(trip_id)

    return templates.TemplateResponse(
        "routes/trip_routes.html",
        {
            "request": request,
            "current_user": current_user,
            "trip": trip,
            "destination": trip.destination, 
            "routes": routes,
        },
    )


@router.get("/routes/{route_id}", response_class=HTMLResponse)
async def route_detail_page(
    request: Request,
    route_id: int,
    current_user: User = Depends(get_current_user),
):
    route = await RouteDAO.find_by_id(route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Маршрут не найден")
    if not route.published and route.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Нет доступа к этому маршруту")

    # Собираем JSON-представление
    route_dict = {
        "id": route.id,
        "name": route.name,
        "user_id": route.user_id,
        "trip_id": route.trip_id,
        "destination_id": route.destination_id,
        "total_budget": (
            float(route.total_budget) if route.total_budget is not None else None
        ),
        "published": route.published,
        "created_at": route.created_at.isoformat(),
        "points": [
            {
                "id": assoc.id,
                "position": assoc.position,
                "attraction": {
                    "id": assoc.attraction.id,
                    "name": assoc.attraction.name,
                    "type": assoc.attraction.type,
                    "latitude": float(assoc.attraction.latitude),
                    "longitude": float(assoc.attraction.longitude),
                },
            }
            for assoc in route.attractions
        ],
    }

    return templates.TemplateResponse(
        "routes/route_detail.html",
        {
            "request": request,
            "current_user": current_user,
            "route": route,
            "route_json": route_dict,
        },
    )

@router.get("/bookings/create", response_class=HTMLResponse)
async def create_booking_page(
    request: Request,
    destination_id: int,
    current_user: User = Depends(get_current_user)   # <-- добавлено
):
    dest = await DestinationDAO.find_by_id(destination_id)
    if not dest:
        raise HTTPException(404, "Направление не найдено")
    return templates.TemplateResponse(
        "bookings/create_booking.html",
        {
            "request": request,
            "current_user": current_user,             
            "destination": dest
        },
    )


@router.get("/bookings/my", response_class=HTMLResponse)
async def my_bookings_page(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    # Получаем все бронирования пользователя
    bookings = await BookingDAO.find_by_user(current_user.id)
    # Для каждого бронирования подтягиваем название направления
    bookings_data = []
    for b in bookings:
        dest = await DestinationDAO.find_by_id(b.destination_id)
        bookings_data.append({
            "id": b.id,
            "destination": dest.name if dest else "-",
            "slots": b.slots_reserved,
            "created_at": b.created_at.strftime("%d.%m.%Y %H:%M")
        })
    return templates.TemplateResponse(
        "bookings/my_bookings.html",
        {
            "request": request,
            "current_user": current_user,
            "bookings": bookings_data
        }
    )