from typing import Optional
from datetime import date
from pydantic import BaseModel, field_validator
import re


class StaffBase(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    role: str
    joined_date: date
    address: Optional[str] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not re.match(r"^[6-9]\d{9}$", v):
            raise ValueError("Invalid Indian phone number")
        return v


class StaffCreate(StaffBase):
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class StaffUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None


class StaffResponse(StaffBase):
    id: str
    staff_code: str
    is_active: bool
    created_at: str

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    phone: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    staff_id: str
    role: str
    name: str
