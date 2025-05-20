from sqlalchemy import select
from app.attractions.models import Attraction
from app.dao.base import BaseDAO
from app.database import async_session_maker