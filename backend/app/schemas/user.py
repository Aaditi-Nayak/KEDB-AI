from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserCreate(BaseModel):
    username:str
    email:EmailStr
    password:str

class UserResponse(BaseModel):
    id:int
    username:str
    email:EmailStr
    role:str
    status:bool
    last_login:datetime|None
    created_at:datetime

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email:EmailStr
    password:str

class Token(BaseModel):
    access_token:str
    token_type:str