from typing import Any, Generator

from sqlmodel import create_engine, Session, SQLModel

from app.core.config import settings

if not settings.SQLALCHEMY_DATABASE_URI:
    raise ValueError("DATABASE_URL is not set")

# Create engine with proper configuration for production
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=300,    # Recycle connections every 5 minutes
    echo=settings.ENVIRONMENT == "local"  # Only echo SQL in local environment
)


def init_db():
    """Initialize the database by creating all tables."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, Any, None]:
    """Dependency to get a database session."""
    with Session(engine) as session:
        yield session
        