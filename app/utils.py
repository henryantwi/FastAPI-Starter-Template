from app.core.security import create_jwt_token
from app.models.user import User
from app.schemas.common import Token


def generate_token_response_data(user: User) -> Token:
    """
    Generate access and refresh tokens for a user.
    
    Args:
        user: The user object to generate tokens for
        
    Returns:
        Token object containing access_token, refresh_token, and token_type
    """
    access_token = create_jwt_token(subject=user.id)
    refresh_token = create_jwt_token(subject=user.id, refresh=True)
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )