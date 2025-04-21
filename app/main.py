from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.destinations.router import router as destinations_router
from app.reviews.router import router as reviews_router
from app.trips.router import router as trips_router
from app.users.router import router as users_router
from app.pages.router import router as pages_router


app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(destinations_router)
app.include_router(reviews_router)
app.include_router(trips_router)
app.include_router(users_router)
app.include_router(pages_router)


