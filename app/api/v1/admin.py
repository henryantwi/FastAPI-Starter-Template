import uuid
from typing import Any

from fastapi import APIRouter, status, Depends, HTTPException, Query

from app.api.deps import get_current_active_superuser, get_current_active_staff, SessionDep
from app.crud.user import (
    get_users,
    get_users_count,
    get_user_by_id,
    get_user_by_email,
    create_user_by_superuser,
    update_user,
    update_user_password,
    delete_user,
)
from app.models.user import User
from app.schemas.user import (
    UserPublic,
    UsersPublic,
    UserCreate,
    UserUpdate,
    UserUpdatePassword,
)

routes = APIRouter(prefix="/admin", tags=["Admin - User Management"])


@routes.get("/users", description="Get all users", status_code=status.HTTP_200_OK)
async def get_all_users(
    session: SessionDep,
    skip: int = Query(default=0, ge=0, description="Number of users to skip"),
    limit: int = Query(default=100, ge=1, le=1000, description="Number of users to return"),
    current_user: User = Depends(get_current_active_superuser),
) -> UsersPublic:
    """
    Get all users with pagination.
    Only accessible by superusers.
    """
    users = get_users(session, skip=skip, limit=limit)
    count = get_users_count(session)
    
    return UsersPublic(
        data=[UserPublic.model_validate(user) for user in users],
        count=count
    )


@routes.get("/users/{user_id}", description="Get user by ID", status_code=status.HTTP_200_OK)
async def get_user_by_id_route(
    session: SessionDep,
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_active_superuser),
) -> UserPublic:
    """
    Get a specific user by ID.
    Only accessible by superusers.
    """
    user = get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return UserPublic.model_validate(user)


@routes.post("/users", description="Create new user", status_code=status.HTTP_201_CREATED)
async def create_user_route(
    session: SessionDep,
    user_in: UserCreate,
    current_user: User = Depends(get_current_active_superuser),
) -> UserPublic:
    """
    Create a new user.
    Only accessible by superusers.
    """
    # Check if user already exists
    existing_user = get_user_by_email(session, user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    user = create_user_by_superuser(session, user_in)
    return UserPublic.model_validate(user)


@routes.put("/users/{user_id}", description="Update user", status_code=status.HTTP_200_OK)
async def update_user_route(
    session: SessionDep,
    user_id: uuid.UUID,
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_superuser),
) -> UserPublic:
    """
    Update a user's information.
    Only accessible by superusers.
    """
    # Check if email is being changed and already exists
    if user_in.email:
        existing_user = get_user_by_email(session, user_in.email)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
    
    user = update_user(session, user_id, user_in)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserPublic.model_validate(user)


@routes.put("/users/{user_id}/password", description="Update user password", status_code=status.HTTP_200_OK)
async def update_user_password_route(
    session: SessionDep,
    user_id: uuid.UUID,
    password_in: UserUpdatePassword,
    current_user: User = Depends(get_current_active_superuser),
) -> UserPublic:
    """
    Update a user's password.
    Only accessible by superusers.
    """
    user = update_user_password(session, user_id, password_in.new_password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserPublic.model_validate(user)


@routes.put("/users/{user_id}/activate", description="Activate user", status_code=status.HTTP_200_OK)
async def activate_user(
    session: SessionDep,
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_active_superuser),
) -> UserPublic:
    """
    Activate a user account.
    Only accessible by superusers.
    """
    user_update = UserUpdate(is_active=True)
    user = update_user(session, user_id, user_update)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserPublic.model_validate(user)


@routes.put("/users/{user_id}/deactivate", description="Deactivate user", status_code=status.HTTP_200_OK)
async def deactivate_user(
    session: SessionDep,
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_active_superuser),
) -> UserPublic:
    """
    Deactivate a user account.
    Only accessible by superusers.
    """
    # Prevent superuser from deactivating themselves
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    user_update = UserUpdate(is_active=False)
    user = update_user(session, user_id, user_update)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserPublic.model_validate(user)


@routes.put("/users/{user_id}/promote", description="Promote user to superuser", status_code=status.HTTP_200_OK)
async def promote_user_to_superuser(
    session: SessionDep,
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_active_superuser),
) -> UserPublic:
    """
    Promote a user to superuser status.
    Only accessible by superusers.
    """
    user_update = UserUpdate(is_superuser=True)
    user = update_user(session, user_id, user_update)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserPublic.model_validate(user)


@routes.put("/users/{user_id}/demote", description="Demote superuser to regular user", status_code=status.HTTP_200_OK)
async def demote_superuser(
    session: SessionDep,
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_active_superuser),
) -> UserPublic:
    """
    Demote a superuser to regular user status.
    Only accessible by superusers.
    """
    # Prevent superuser from demoting themselves
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot demote your own superuser status"
        )
    
    user_update = UserUpdate(is_superuser=False)
    user = update_user(session, user_id, user_update)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserPublic.model_validate(user)


@routes.delete("/users/{user_id}", description="Delete user", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_route(
    session: SessionDep,
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_active_superuser),
) -> None:
    """
    Delete a user account permanently.
    Only accessible by superusers.
    """
    # Prevent superuser from deleting themselves
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    success = delete_user(session, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )


@routes.put("/users/{user_id}/make-staff", description="Promote user to staff", status_code=status.HTTP_200_OK)
async def promote_user_to_staff(
    session: SessionDep,
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_active_superuser),
) -> UserPublic:
    """
    Promote a user to staff status.
    Only accessible by superusers.
    """
    user_update = UserUpdate(is_staff=True)
    user = update_user(session, user_id, user_update)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserPublic.model_validate(user)


@routes.put("/users/{user_id}/remove-staff", description="Remove staff privileges", status_code=status.HTTP_200_OK)
async def remove_staff_privileges(
    session: SessionDep,
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_active_superuser),
) -> UserPublic:
    """
    Remove staff privileges from a user.
    Only accessible by superusers.
    Cannot remove staff privileges from superusers (they automatically have them).
    """
    # Prevent superuser from removing staff privileges from themselves
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify your own privileges"
        )
    
    # Check if the target user is a superuser
    target_user = get_user_by_id(session, user_id)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if target_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove staff privileges from superusers (they automatically have staff privileges)"
        )
    
    user_update = UserUpdate(is_staff=False)
    user = update_user(session, user_id, user_update)
    
    return UserPublic.model_validate(user)


@routes.get("/stats", description="Get user statistics", status_code=status.HTTP_200_OK)
async def get_user_stats(
    session: SessionDep,
    current_user: User = Depends(get_current_active_superuser),
) -> dict[str, Any]:
    """
    Get user statistics and counts.
    Only accessible by superusers.
    """
    from sqlmodel import select, func
    
    # Total users
    total_users = get_users_count(session)
    
    # Active users
    active_users_stmt = select(func.count(User.id)).where(User.is_active == True)
    active_users = session.exec(active_users_stmt).first() or 0
    
    # Inactive users
    inactive_users = total_users - active_users
    
    # Superusers
    superusers_stmt = select(func.count(User.id)).where(User.is_superuser == True)
    superusers = session.exec(superusers_stmt).first() or 0
    
    # Staff users
    staff_stmt = select(func.count(User.id)).where(User.is_staff == True)
    staff_users = session.exec(staff_stmt).first() or 0
    
    # Regular users (not staff and not superuser)
    regular_users = total_users - superusers - staff_users
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": inactive_users,
        "superusers": superusers,
        "staff_users": staff_users,
        "regular_users": regular_users,
    }
