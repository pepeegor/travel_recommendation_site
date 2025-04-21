from sqlalchemy import select
from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.users.models import User

class UserDAO(BaseDAO):
    
    model = User