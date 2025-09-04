from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session

from app.api.deps import CurrentUser, SessionDep
from app.crud.auth import authenticate
from app.crud.user import get_user_by_email, create_user
from app.schemas.common import Token, AuthResponse, RefreshTokenRequest
from app.schemas.user import UserLogin, UserPublic, UserRegister
from app.utils import generate_token_response_data
from app.core.security import create_jwt_token
from app.core.config import settings
import jwt

routes = APIRouter(prefix="/auth", tags=["Auth"])


@routes.post("/login", status_code=status.HTTP_200_OK, response_model=AuthResponse)
async def user_login(session: SessionDep, form_data: UserLogin):
    """
    Login to the system
    """
    user = authenticate(
        session=session, email=form_data.email, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    user.last_login_at = datetime.now(timezone.utc)
    session.add(user)
    session.commit()
    session.refresh(user)

    login_response = AuthResponse(
        token=generate_token_response_data(user), user=UserPublic.model_validate(user)
    )
    return login_response


@routes.post("/token/test", response_model=UserPublic)
async def test_token(current_user: CurrentUser):
    """
    Test access token
    """
    return current_user


@routes.post("/token/refresh", response_model=Token)
async def refresh_tokens(session: SessionDep, token_data: RefreshTokenRequest):
    """
    Refresh user tokens
    """
    try:
        # Decode the refresh token to get user ID
        payload = jwt.decode(
            token_data.refresh_token, 
            settings.SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid refresh token"
            )
        
        # Get user from database
        from app.models.user import User
        user = session.get(User, user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User not found or inactive"
            )
        
        return generate_token_response_data(user)
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid refresh token"
        )


@routes.post("/register", response_model=AuthResponse)
async def register_user(session: SessionDep, user_in: UserRegister) -> Any:
    """
    Create new user without the need to be logged in.
    """
    user = get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )
    user_create = UserRegister.model_validate(user_in)
    user = create_user(session=session, user_create=user_create)

    register_response = AuthResponse(
        token=generate_token_response_data(user), user=UserPublic.model_validate(user)
    )
    return register_response
