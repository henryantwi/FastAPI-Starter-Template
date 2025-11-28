import uuid
from datetime import datetime, timezone
from pydantic import EmailStr
from sqlmodel import select

from app.api.deps import SessionDep
from app.core.security import get_password_hash
from app.models.user import User, UserAuthProviderToken
from app.schemas.user import UserRegister, UserCreate, UserUpdate


def get_user_by_email(session: SessionDep, email: EmailStr) -> User | None:
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()
    return user


def get_user_by_id(session: SessionDep, user_id: uuid.UUID) -> User | None:
    return session.get(User, user_id)


def get_users(session: SessionDep, skip: int = 0, limit: int = 100) -> list[User]:
    statement = select(User).offset(skip).limit(limit)
    return session.exec(statement).all()


def get_users_count(session: SessionDep) -> int:
    statement = select(User)
    return len(session.exec(statement).all())


def create_user(session: SessionDep, user_create: UserRegister):
    hashed_password = get_password_hash(user_create.password)
    user_data = user_create.model_dump()

    user = User()
    user.email = user_data["email"]
    user.hashed_password = hashed_password
    user.username = user_data.get("username")
    user.first_name = user_data.get("first_name")
    user.last_name = user_data.get("last_name")
    # user.profile_picture = user_data.get('profile_picture')
    user.bio = user_data.get("bio")

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


def create_user_by_superuser(session: SessionDep, user_create: UserCreate) -> User:
    """Create a new user by superuser with all fields"""
    hashed_password = get_password_hash(user_create.password)
    
    # If creating a superuser, automatically set is_staff to True
    is_staff = user_create.is_staff or user_create.is_superuser
    
    user = User(
        email=user_create.email,
        hashed_password=hashed_password,
        username=user_create.username,
        first_name=user_create.first_name,
        last_name=user_create.last_name,
        bio=user_create.bio,
        is_active=user_create.is_active,
        is_superuser=user_create.is_superuser,
        is_staff=is_staff
    )
    
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def update_user(session: SessionDep, user_id: uuid.UUID, user_update: UserUpdate) -> User | None:
    """Update user by superuser"""
    user = session.get(User, user_id)
    if not user:
        return None
    
    update_data = user_update.model_dump(exclude_unset=True)
    
    # If promoting to superuser, automatically set is_staff to True
    if update_data.get('is_superuser') is True:
        update_data['is_staff'] = True
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    session.commit()
    session.refresh(user)
    return user


def update_user_password(session: SessionDep, user_id: uuid.UUID, new_password: str) -> User | None:
    """Update user password by superuser"""
    user = session.get(User, user_id)
    if not user:
        return None
    
    hashed_password = get_password_hash(new_password)
    user.hashed_password = hashed_password
    
    session.commit()
    session.refresh(user)
    return user


def delete_user(session: SessionDep, user_id: uuid.UUID) -> bool:
    """Delete user by superuser"""
    user = session.get(User, user_id)
    if not user:
        return False
    
    session.delete(user)
    session.commit()
    return True


def create_or_update_oauth_user(
    session: SessionDep,
    email: str,
    provider_name: str,
    access_token: str,
    refresh_token: str | None = None,
    expires_at: datetime | None = None,
    first_name: str | None = None,
    last_name: str | None = None,
    profile_picture: str | None = None
) -> User:
    """Create or update a user from OAuth provider"""
    
    # Check if user exists
    user = get_user_by_email(session, email)
    
    if not user:
        # Create new user
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            profile_picture=profile_picture,
            is_active=True,
            hashed_password=None  # OAuth users don't have passwords
        )
        session.add(user)
        session.commit()
        session.refresh(user)
    else:
        # Update existing user info if provided
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if profile_picture:
            user.profile_picture = profile_picture
        
        user.last_login_at = datetime.now(timezone.utc)
        session.add(user)
        session.commit()
        session.refresh(user)
    
    # Check if provider token already exists
    statement = select(UserAuthProviderToken).where(
        UserAuthProviderToken.user_id == user.id,
        UserAuthProviderToken.provider_name == provider_name
    )
    provider_token = session.exec(statement).first()
    
    if provider_token:
        # Update existing token
        provider_token.access_token = access_token
        provider_token.refresh_token = refresh_token
        provider_token.expires_at = expires_at
    else:
        # Create new token
        provider_token = UserAuthProviderToken(
            user_id=user.id,
            provider_name=provider_name,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at
        )
        session.add(provider_token)
    
    session.commit()
    session.refresh(user)
    
    return user