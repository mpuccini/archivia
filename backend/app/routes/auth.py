from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.auth import AuthService
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.schemas.auth import Token
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()
auth_service = AuthService()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security), 
    db: Session = Depends(get_db)
) -> User:
    """Dependency to get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    username = auth_service.verify_token(credentials.credentials)
    if username is None:
        raise credentials_exception
    
    user = auth_service.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user


@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Register a new user (admin only)"""
    # Only allow admin to create new users
    if current_user.username != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admin can create new users"
        )

    # Check if user already exists
    db_user = auth_service.get_user_by_username(db, user_data.username)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )

    # Create new user
    db_user = auth_service.create_user(db, user_data)
    return UserResponse.model_validate(db_user)


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Login user and return access token"""
    user = auth_service.authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse.model_validate(current_user)


@router.get("/verify")
async def verify_token(current_user: User = Depends(get_current_user)):
    """Verify if token is valid"""
    return {"message": "Token is valid", "user": current_user.username}
