import uuid

from pydantic import BaseModel, Field

from app.models.student import UserRole


class UserCreate(BaseModel):
    email: str = Field(min_length=5, max_length=260)
    password: str = Field(min_length=10, max_length=128)
    full_name: str | None = Field(default=None, max_length=180)
    role: UserRole = UserRole.admin


class LoginRequest(BaseModel):
    email: str
    password: str


class UserRead(BaseModel):
    id: uuid.UUID
    email: str
    role: UserRole
    full_name: str | None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead
