from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=100)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    id: int
    email: EmailStr
    role: str
    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead


class SubjectBase(BaseModel):
    title: str = Field(min_length=2, max_length=120)
    description: str = ""
    price: Decimal = Field(ge=0)
    duration_minutes: int = Field(default=60, ge=15, le=480)
    is_active: bool = True


class SubjectCreate(SubjectBase):
    pass


class SubjectUpdate(SubjectBase):
    pass


class SubjectRead(SubjectBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class BookingCreate(BaseModel):
    subject_id: int
    start_time: datetime
    comment: str = ""
    user_id: int | None = None


class BookingUpdate(BaseModel):
    subject_id: int
    start_time: datetime
    status: str = Field(default="planned", max_length=30)
    comment: str = ""


class BookingRead(BaseModel):
    id: int
    user_id: int
    client_email: str
    subject_id: int
    subject_title: str
    start_time: datetime
    status: str
    comment: str
