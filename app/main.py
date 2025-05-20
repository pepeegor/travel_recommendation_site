from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqladmin import Admin

from app.adminpanel.views import (
    BookingAdmin,
    UserAdmin,
    DestinationAdmin,
    AttractionAdmin,
    TripAdmin,
    RouteAdmin,
    RouteAttractionAdmin,
    ReviewAdmin,
)

from app.destinations.router import router as destinations_router
from app.reviews.router import router as reviews_router
from app.trips.router import router as trips_router
from app.users.router import router as users_router
from app.pages.router import router as pages_router
from app.attractions.router import router as attractions_router
from app.routes.router import router as routes_router
from app.bookings.router import router as routes_bookings
from app.adminpanel.auth import authentication_backend
from app.database import engine


app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

admin = Admin(app, engine, authentication_backend=authentication_backend)


admin.add_view(UserAdmin)
admin.add_view(DestinationAdmin)
admin.add_view(AttractionAdmin)
admin.add_view(TripAdmin)
admin.add_view(RouteAdmin)
admin.add_view(RouteAttractionAdmin)
admin.add_view(ReviewAdmin)
admin.add_view(BookingAdmin)


app.include_router(destinations_router)
app.include_router(reviews_router)
app.include_router(trips_router)
app.include_router(users_router)
app.include_router(pages_router)
app.include_router(attractions_router)
app.include_router(routes_router)
app.include_router(routes_bookings)
