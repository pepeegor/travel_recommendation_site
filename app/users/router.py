from fastapi import APIRouter, Depends, HTTPException, Response

from app.users.auth import authenticate_user, create_access_token, get_password_hash, verify_password
from app.users.dao import UserDAO
from app.users.dependencies import get_current_admin_user, get_current_user
from app.users.models import User
from app.users.schemas import SUser, SUserAuth, SUserRegister, SUserUpdate
from app.exceptions import UserAlreadyExistsException, IncorrectEmailOrPasswordException

router = APIRouter(
    prefix="/auth",
    tags=["Auth & Пользователи"]
)


@router.post("/register")
async def register_user(user_data: SUserRegister):
    existing_user_email = await UserDAO.find_one_or_none(email=user_data.email)
    if existing_user_email:
        raise UserAlreadyExistsException
    existing_username = await UserDAO.find_one_or_none(username=user_data.username)
    if existing_username:
        raise UserAlreadyExistsException
    hashed_password = get_password_hash(user_data.password)
    await UserDAO.add(username=user_data.username, email=user_data.email, password_hash=hashed_password, role=user_data.role)
    new_user = await UserDAO.find_one_or_none(email=user_data.email)  
    
    return new_user
    

@router.post("/login")
async def login_user(response: Response, user_data: SUserAuth):
    user = await authenticate_user(user_data.email, user_data.password)
    if not user:
        raise IncorrectEmailOrPasswordException
    access_token = create_access_token({"sub": str(user.id)})
    response.set_cookie("travels_access_token", access_token, httponly=True)
    return {"access_token": access_token}

@router.post("/logout")
async def logout_user(response: Response):
    response.delete_cookie("travels_access_token")
    
@router.get("/me")
async def read_users_me(user: User = Depends(get_current_user)):
    return user

@router.put("/me")
async def update_users_me(
    user_data: SUserUpdate,
    current_user: User = Depends(get_current_user)
):
    update_data = {}
    
    if user_data.username is not None:
        existing_user = await UserDAO.find_one_or_none(username=user_data.username)
        if existing_user and existing_user.id != current_user.id:
            raise UserAlreadyExistsException
        update_data["username"] = user_data.username
        
    if user_data.email is not None:
        existing_user = await UserDAO.find_one_or_none(email=user_data.email)
        if existing_user and existing_user.id != current_user.id:
            raise UserAlreadyExistsException
        update_data["email"] = user_data.email
        
    if user_data.password is not None:
        update_data["password_hash"] = get_password_hash(user_data.password)
    
    if update_data:
        await UserDAO.update(current_user.id, **update_data)
        
    return await UserDAO.find_by_id(current_user.id)

@router.get("/{user_id}")
async def get_user_by_id(user_id: int, user: User = Depends(get_current_admin_user)) -> SUser:
    return await UserDAO.find_by_id(user_id)
    
@router.get("/users/{user_id}")
async def get_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_admin_user)  # Только для администраторов
):
    """
    Получение пользователя по ID (только для администраторов).
    """
    user = await UserDAO.find_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/users/{user_id}")
async def update_user(
    user_id: int,
    user_data: SUserUpdate,  #  Схема данных для обновления пользователя
    current_user: User = Depends(get_current_admin_user)  # Только для администраторов
):
    """
    Обновление данных пользователя (только для администраторов).
    """
    update_data = {}
    if user_data.username is not None:
        existing_user = await UserDAO.find_one_or_none(username=user_data.username)
        if existing_user and existing_user.id != user_id:
            raise UserAlreadyExistsException
        update_data["username"] = user_data.username
        
    if user_data.email is not None:
        existing_user = await UserDAO.find_one_or_none(email=user_data.email)
        if existing_user and existing_user.id != user_id:
            raise UserAlreadyExistsException
        update_data["email"] = user_data.email
        
    if user_data.password is not None:
        update_data["password_hash"] = get_password_hash(user_data.password)
    
    if update_data:
        user = await UserDAO.update(user_id, **update_data)
    else:
        user = await UserDAO.find_by_id(user_id)
        
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user)
):
    await UserDAO.delete(user_id)
    return {"message": "User deleted successfully"}

