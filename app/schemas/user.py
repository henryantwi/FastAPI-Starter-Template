import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, ConfigDict, model_validator
from typing import Self


class UserBase(BaseModel):
    username: str | None = None
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False
    is_staff: bool = False
    first_name: str | None = None
    last_name: str | None = None
    last_login_at: datetime | None = None
    profile_picture: str | None = None
    bio: str | None = None


class UpdateMe(BaseModel):
    first_name: str | None = Field(default=None, max_length=255)
    last_name: str | None = Field(default=None, max_length=255)
    profile_picture: str | None = None
    bio: str | None = None
    username: str | None = Field(default=None, max_length=50)


class UpdatePassword(BaseModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)

    @model_validator(mode="after")
    def validate_passwords(self) -> Self:
        # Check if current_password is not the same as new_password
        if self.current_password == self.new_password:
            raise ValueError(
                "New password must not be the same as the current password."
            )
        return self


class UserPublic(UserBase):
    id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


class UserRegister(BaseModel):
    username: str | None = Field(default=None, max_length=50)
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    first_name: str | None = Field(default=None, max_length=255)
    last_name: str | None = Field(default=None, max_length=255)
    bio: str | None = Field(default=None, max_length=1000)


class UserLogin(BaseModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)


# Superuser schemas for user management
class UserCreate(BaseModel):
    username: str | None = Field(default=None, max_length=50)
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    first_name: str | None = Field(default=None, max_length=255)
    last_name: str | None = Field(default=None, max_length=255)
    bio: str | None = Field(default=None, max_length=1000)
    is_active: bool = True
    is_superuser: bool = False
    is_staff: bool = False


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, max_length=50)
    email: EmailStr | None = None
    first_name: str | None = Field(default=None, max_length=255)
    last_name: str | None = Field(default=None, max_length=255)
    bio: str | None = Field(default=None, max_length=1000)
    profile_picture: str | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None
    is_staff: bool | None = None


class UserUpdatePassword(BaseModel):
    new_password: str = Field(min_length=8, max_length=128)


class UsersPublic(BaseModel):
    data: list[UserPublic]
    count: int