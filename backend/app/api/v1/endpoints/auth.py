"""
Authentication endpoints for user registration and login.

Provides endpoints for:
- User registration
- User login
- Get current user information
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token
from app.core.deps import get_current_user
from app.db.session import get_db
from app.schemas.user import User, UserCreate
from app.schemas.token import Token
from app.services.auth_service import create_user, authenticate_user
from app.models.user import User as UserModel

router = APIRouter()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user. Creates a new user account and returns an access token.

    Args:
        user_data: User registration data (email, password, full_name)
        db: Database session

    Returns:
        Access token for the newly created user

    Raises:
        HTTPException: 400 if email already exists
    """
    # Create user (raises HTTPException if email exists)
    user = create_user(db, user_data)

    # Generate access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login with email and password. Authenticates user and returns an access token.

    Args:
        form_data: OAuth2 form with username (email) and password
        db: Database session

    Returns:
        Access token for authenticated user

    Raises:
        HTTPException: 401 if credentials are invalid
    """
    # Authenticate user (username field contains email)
    user = authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=User)
async def get_me(
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get current user information. Returns information about the currently authenticated user.

    Args:
        current_user: Current authenticated user from token

    Returns:
        User information (id, email, full_name, is_active, timestamps)

    """
    return current_user
