import uuid
from pydantic import EmailStr
from sqlmodel import select

from app.api.deps import SessionDep
from app.core.security import get_password_hash
from app.models.user import User
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