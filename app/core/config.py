import secrets
from typing import Any, Literal, Annotated

from pydantic import (
    AnyUrl,
    BeforeValidator,
    computed_field,
    EmailStr,
    field_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Use top level .env file (one level above ./app/)
        env_file="./.env",
        env_ignore_empty=True,
        extra="ignore",
    )

    BACKEND_CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = []

    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    SECRET_KEY: str = secrets.token_urlsafe(32)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Database configuration
    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""

    @field_validator("POSTGRES_PASSWORD", mode="before")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not v:
            raise ValueError("POSTGRES_PASSWORD cannot be empty")
        return v

    @field_validator("POSTGRES_DB", mode="before")
    @classmethod
    def validate_db_name(cls, v: str) -> str:
        if not v:
            raise ValueError("POSTGRES_DB cannot be empty")
        return v

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:  # noqa
        return f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # First superuser configuration
    FIRST_SUPERUSER_EMAIL: EmailStr
    FIRST_SUPERUSER_PASSWORD: str

    @field_validator("FIRST_SUPERUSER_PASSWORD", mode="before")
    @classmethod
    def validate_superuser_password(cls, v: str) -> str:
        if not v or len(v) < 8:
            raise ValueError("FIRST_SUPERUSER_PASSWORD must be at least 8 characters")
        return v


settings = Settings()  # type: ignore
