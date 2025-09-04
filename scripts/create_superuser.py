#!/usr/bin/env python3
"""
Script to create the first superuser in the database.
Run this after database migrations.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlmodel import Session, select
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError

from app.core.config import settings
from app.core.security import get_password_hash
from app.db.session import engine
from app.models.user import User


def create_first_superuser():
    """Create the first superuser if it doesn't exist."""
    try:
        # Validate required settings
        if not settings.FIRST_SUPERUSER_EMAIL:
            print("ERROR: FIRST_SUPERUSER_EMAIL is not configured.")
            return False
            
        if not settings.FIRST_SUPERUSER_PASSWORD:
            print("ERROR: FIRST_SUPERUSER_PASSWORD is not configured.")
            return False
            
        print(f"Checking for existing superuser with email: {settings.FIRST_SUPERUSER_EMAIL}")
        
        with Session(engine) as session:
            # Check if user already exists
            statement = select(User).where(User.email == settings.FIRST_SUPERUSER_EMAIL)
            existing_user = session.exec(statement).first()
            
            if existing_user:
                print(f"✓ User with email {settings.FIRST_SUPERUSER_EMAIL} already exists. Skipping creation.")
                return True
            
            # Create new superuser
            print(f"Creating new superuser with email: {settings.FIRST_SUPERUSER_EMAIL}")
            hashed_password = get_password_hash(settings.FIRST_SUPERUSER_PASSWORD)
            
            superuser = User(
                email=settings.FIRST_SUPERUSER_EMAIL,
                hashed_password=hashed_password,
                is_superuser=True,
                is_staff=True,
                is_active=True,
                username="admin",
                first_name="Generic",
                last_name="Admin",
                bio="This is a generic admin user"
            )
            
            session.add(superuser)
            session.commit()
            session.refresh(superuser)
            
            print(f"✅ Superuser created successfully with email: {settings.FIRST_SUPERUSER_EMAIL}")
            return True
            
    except ValidationError as e:
        print(f"ERROR: Invalid user data - {e}")
        return False
    except SQLAlchemyError as e:
        print(f"ERROR: Database error - {e}")
        return False
    except Exception as e:
        print(f"ERROR: Unexpected error creating superuser - {e}")
        return False


if __name__ == "__main__":
    success = create_first_superuser()
    if not success:
        sys.exit(1)
    print("Superuser setup completed successfully.")
