from sqladmin import ModelView

from app.bookings.models import Booking
from app.users.models import User
from app.destinations.models import Destination
from app.attractions.models import Attraction
from app.trips.models import Trip
from app.routes.models import Route
from app.routes_attractions.models import RouteAttraction
from app.reviews.models import Review


class UserAdmin(ModelView, model=User):
    name = "Пользователь"
    name_plural = "Пользователи"
    icon = "fa-solid fa-user"

    column_list = [
        User.id,
        User.username,
        User.email,
        User.role,
        User.registration_date,
    ]
    column_searchable_list = [User.username, User.email]
    column_filters = [User.role]
    column_details_exclude_list = [User.password_hash]

    can_create = True
    can_edit = True
    can_delete = False


class DestinationAdmin(ModelView, model=Destination):
    name = "Направление"
    name_plural = "Направления"
    icon = "fa-solid fa-flag"

    column_list = [
        Destination.id,
        Destination.name,
        Destination.country,
        Destination.climate,
        Destination.approximate_price,
    ]
    column_searchable_list = [
        Destination.name,
        Destination.country,
        Destination.climate,
    ]
    column_filters = [Destination.country, Destination.climate]

    can_create = True
    can_edit = True
    can_delete = True


class AttractionAdmin(ModelView, model=Attraction):
    name = "Достопримечательность"
    name_plural = "Достопримечательности"
    icon = "fa-solid fa-compass"

    column_list = [
        Attraction.id,
        Attraction.name,
        Attraction.type,
        Attraction.destination_id,
        Attraction.approximate_price,
    ]
    column_searchable_list = [Attraction.name, Attraction.type]
    column_filters = [Attraction.type]

    form_columns = [
        "name",
        "type",
        "description",
        "approximate_price",
        "latitude",
        "longitude",
        "destination",  # <-- вот так
    ]

    can_create = True
    can_edit = True
    can_delete = True


class TripAdmin(ModelView, model=Trip):
    name = "Поездка"
    name_plural = "Поездки"
    icon = "fa-solid fa-suitcase-rolling"

    column_list = [
        Trip.id,
        Trip.user_id,
        Trip.destination_id,
        Trip.start_date,
        Trip.end_date,
        Trip.budget,
        Trip.status,
    ]
    column_searchable_list = [Trip.status]
    column_filters = [Trip.status, Trip.start_date, Trip.end_date]

    form_columns = [
        "user_id",
        "destination_id",
        "start_date",
        "end_date",
        "budget",
        "status",
    ]

    can_create = True
    can_edit = True
    can_delete = True


class RouteAdmin(ModelView, model=Route):
    name = "Маршрут"
    name_plural = "Маршруты"
    icon = "fa-solid fa-route"

    column_list = [
        Route.id,
        Route.name,
        Route.user_id,
        Route.trip_id,
        Route.destination_id,
        Route.total_budget,
        Route.published,
        Route.created_at,
    ]
    column_searchable_list = [Route.name]
    column_filters = [Route.published, Route.created_at]

    form_columns = [
        "name",
        "user_id",
        "trip_id",
        "destination_id",
        "total_budget",
        "published",
    ]

    can_create = True
    can_edit = True
    can_delete = True


class RouteAttractionAdmin(ModelView, model=RouteAttraction):
    name = "Точка маршрута"
    name_plural = "Точки маршрутов"
    icon = "fa-solid fa-map-pin"

    column_list = [
        RouteAttraction.id,
        RouteAttraction.route_id,
        RouteAttraction.attraction_id,
        RouteAttraction.position,
    ]
    column_searchable_list = []
    column_filters = [RouteAttraction.route_id]

    form_columns = ["route_id", "attraction_id", "position"]

    can_create = False  # манипулируем через RouteAdmin
    can_edit = True
    can_delete = True


class ReviewAdmin(ModelView, model=Review):
    name = "Отзыв"
    name_plural = "Отзывы"
    icon = "fa-solid fa-star"

    column_list = [
        Review.id,
        Review.user_id,
        Review.destination_id,
        Review.rating,
        Review.created_at,
    ]
    column_searchable_list = []
    column_filters = [Review.rating, Review.created_at]

    form_columns = ["user_id", "destination_id", "rating", "comment"]

    can_create = False  # создаются через пользовательский интерфейс
    can_edit = True
    can_delete = True

class BookingAdmin(ModelView, model=Booking):
    name = "Бронирование"
    name_plural = "Бронирования"
    icon = "fa-solid fa-calendar-check"

    column_list = [
        Booking.id,
        Booking.user_id,
        Booking.destination_id,
        Booking.slots_reserved,
        Booking.created_at,
    ]
    column_searchable_list = []
    column_filters = [Booking.user_id, Booking.destination_id]

    form_columns = [
        "user_id",
        "destination_id",
        "slots_reserved",
    ]

    can_create = True
    can_edit = True
    can_delete = True