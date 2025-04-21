
from datetime import datetime, timezone
from fastapi import Depends, HTTPException, Request, status
from jose import jwt, JWTError
from app.config import settings
from app.users.dao import UserDAO
from app.users.models import User
from app.exceptions import ExpiredTokenException, AbsentTokenException, IncorrectTokenFormatException, UserIsNotPresentException, UserIsNotAdmin


def get_token(request: Request):
    token = request.cookies.get('travels_access_token')
    if not token:
        raise ExpiredTokenException
    return token


async def get_current_user(token: str = Depends(get_token)):
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, settings.ALGORITHM
        )
    except JWTError:
        raise AbsentTokenException
    expire: str = payload.get("exp")
    if not expire or (int(expire) < datetime.now(timezone.utc).timestamp()):
        raise IncorrectTokenFormatException
    user_id: str = payload.get("sub")
    if not user_id:
        raise UserIsNotPresentException
    user = await UserDAO.find_by_id(int(user_id))
    if not user:
        raise UserIsNotPresentException
    return user


async def get_current_admin_user(user: User = Depends(get_current_user)):
    if user.role != 'admin':
        raise UserIsNotAdmin
    return user