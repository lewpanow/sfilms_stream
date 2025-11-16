from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class FilmsDTO(BaseModel):
    film_id: UUID
    name: str
    description: str
    release_year: int


class UsersDTO(BaseModel):
    user_id: UUID
    username: str
    email: str
    password_hash: str
    created_at: datetime
    updated_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserRegistration(BaseModel):
    username: str
    email: str
    password: str
    repeat_password: str


class UserAuthorization(BaseModel):
    username: str
    password: str
    repeat_password: str
