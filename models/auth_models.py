# models/auth_models.py
from pydantic import BaseModel, EmailStr, Field

class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int | None = None         # SQL id (int) or None for Mongo
    user_id: int | None = None    # Mongo incremental user id (if you want one)
    email: EmailStr
