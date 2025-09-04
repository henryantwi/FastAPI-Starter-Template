import uuid
from typing import Any

from fastapi import APIRouter, status, Depends, HTTPException, Query

from app.api.deps import get_current_active_staff, SessionDep
from app.crud.user import (
    get_users,
    get_users_count,
    get_user_by_id,
)
from app.models.user import User
from app.schemas.user import (
    UserPublic,
    UsersPublic,
)

routes = APIRouter(prefix="/staff", tags=["Staff - Limited User Management"])


@routes.get("/users", description="Get all users (staff access)", status_code=status.HTTP_200_OK)
async def get_all_users_staff(
    session: SessionDep,
    skip: int = Query(default=0, ge=0, description="Number of users to skip"),
    limit: int = Query(default=100, ge=1, le=1000, description="Number of users to return"),
    current_user: User = Depends(get_current_active_staff),
) -> UsersPublic:
    """
    Get all users with pagination.
    Accessible by staff and superusers.
    Staff can view users but cannot modify them.
    """
    users = get_users(session, skip=skip, limit=limit)
    count = get_users_count(session)
    
    return UsersPublic(
        data=[UserPublic.model_validate(user) for user in users],
        count=count
    )


@routes.get("/users/{user_id}", description="Get user by ID (staff access)", status_code=status.HTTP_200_OK)
async def get_user_by_id_staff(
    session: SessionDep,
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_active_staff),
) -> UserPublic:
    """
    Get a specific user by ID.
    Accessible by staff and superusers.
    Staff can view user details but cannot modify them.
    """
    user = get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return UserPublic.model_validate(user)


@routes.get("/dashboard", description="Get staff dashboard info", status_code=status.HTTP_200_OK)
async def get_staff_dashboard(
    session: SessionDep,
    current_user: User = Depends(get_current_active_staff),
) -> dict[str, Any]:
    """
    Get basic statistics for staff dashboard.
    Accessible by staff and superusers.
    Limited information compared to admin stats.
    """
    from sqlmodel import select, func
    
    # Total users
    total_users = get_users_count(session)
    
    # Active users
    active_users_stmt = select(func.count(User.id)).where(User.is_active == True)
    active_users = session.exec(active_users_stmt).first() or 0
    
    # Inactive users
    inactive_users = total_users - active_users
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": inactive_users,
        "staff_name": current_user.full_name or current_user.username or "Staff User",
        "staff_permissions": "full_admin" if current_user.is_superuser else "read_only",
        "is_superuser": current_user.is_superuser,
        "has_staff_privileges": current_user.has_staff_privileges
    }
