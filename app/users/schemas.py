from datetime import date, datetime
from typing import Annotated, Optional
from pydantic import BaseModel, EmailStr, StringConstraints


class SUserAuth(BaseModel):
    username: Optional[str] = None
    email: EmailStr
    password: str
    
    class Config:
        from_attributes = True


class SUserRegister(BaseModel):
    email: EmailStr
    username: Annotated[str, StringConstraints(min_length=3, max_length=20)] 
    password: Annotated[str, StringConstraints(min_length=6, max_length=20)]
    role: Optional[str] = 'user'
    
    class Config:
        from_attributes = True

class SUser(BaseModel):
    id: int
    username: str
    email: str
    password_hash: str
    role: str
    registration_date: datetime
    
    
    class Config:
        from_attributes = True
        
class SUserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    
    class Config:
        from_attributes = True
