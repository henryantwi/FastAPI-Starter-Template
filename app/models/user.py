# models.py
import uuid
from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlmodel import SQLModel, Field, Relationship


class User(SQLModel, table=True):
    __tablename__ = "user"  # keep table name to match existing FK

    # Primary key as UUID (server-side type: Postgres UUID)
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True),
    )

    username: Optional[str] = Field(default=None)
    # Unique + indexed email per your original model
    email: str = Field(sa_column=Column(String, unique=True, nullable=False, index=True))
    hashed_password: Optional[str] = Field(default=None)  # Nullable for SSO users

    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    is_staff: bool = Field(default=False)
    last_login_at: Optional[datetime] = Field(default=None)

    first_name: Optional[str] = Field(default=None)
    last_name: Optional[str] = Field(default=None)
    profile_picture: Optional[str] = Field(default=None)  # URL
    bio: Optional[str] = Field(default=None)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime, default=datetime.now(timezone.utc)),
    )

    # One-to-many: a user can have multiple provider tokens
    auth_provider_token: List["UserAuthProviderToken"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

    def __repr__(self) -> str:
        return f"<User(username={self.username}, email={self.email})>"

    @property
    def full_name(self) -> str:
        # Gracefully handles None names
        first = self.first_name or ""
        last = self.last_name or ""
        return f"{first} {last}".strip()
    
    @property
    def has_staff_privileges(self) -> bool:
        """
        Check if user has staff privileges.
        Superusers automatically have staff privileges.
        """
        return self.is_superuser or self.is_staff


class UserAuthProviderToken(SQLModel, table=True):
    __tablename__ = "userauthprovidertoken"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    )

    # Use sa_column to attach ondelete="CASCADE" like your original SQLAlchemy model
    user_id: uuid.UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("user.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )
    )

    # e.g., 'google', 'facebook', 'twitter', 'form'
    provider_name: str = Field(sa_column=Column(String, nullable=False))
    access_token: str = Field(sa_column=Column(String, nullable=False))
    refresh_token: Optional[str] = Field(default=None)
    expires_at: Optional[datetime] = Field(default=None)

    # Relationship back to the parent user
    user: Optional[User] = Relationship(back_populates="auth_provider_token")

    def __repr__(self) -> str:
        return f"<UserAuthToken(user_id={self.user_id}, provider_name={self.provider_name})>"
