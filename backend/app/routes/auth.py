import uuid
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address
from ..database import get_db
from ..utils.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    hash_token,
    decode_token,
    get_active_user,
    get_admin_user,
)
from ..utils.dates import ensure_aware_utc, utc_now
from ..models import User, RefreshToken
from ..schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse, RefreshTokenRequest
from ..config import settings

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


def _rate_limit_key(request: Request):
    """Return the remote address for rate limiting, or a unique key for OPTIONS preflight requests.

    slowapi does not honour a None return value as a skip signal — the request is still
    processed and can raise a 400/429.  Returning a per-request UUID means every OPTIONS
    preflight gets its own isolated bucket that will never accumulate enough hits to
    trigger the configured limit, effectively bypassing rate limiting for those requests.
    """
    if request.method == "OPTIONS":
        return str(uuid.uuid4())
    return get_remote_address(request)


limiter = Limiter(key_func=_rate_limit_key, enabled=settings.RATE_LIMIT_ENABLED, default_limits=[])


def issue_token_pair(user: User, db: Session):
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role},
        expires_delta=access_token_expires
    )
    refresh_token, refresh_expires_at = create_refresh_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role},
        expires_delta=refresh_token_expires
    )
    db_refresh_token = RefreshToken(
        user_id=user.id,
        token_hash=hash_token(refresh_token),
        expires_at=refresh_expires_at,
    )
    db.add(db_refresh_token)
    db.flush()
    return access_token, refresh_token

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db), admin: dict = Depends(get_admin_user)):
    """Register new user (admin only)"""
    
    # Check if user exists
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email exists
    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        hashed_password=hash_password(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/me", response_model=UserResponse)
def get_me(db: Session = Depends(get_db), current_user: dict = Depends(get_active_user)):
    """Get current authenticated user"""
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
def login(request: Request, user_credentials: UserLogin, db: Session = Depends(get_db)):
    """User login"""
    
    # Find user by username
    user = db.query(User).filter(User.username == user_credentials.username).first()
    
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    try:
        access_token, refresh_token = issue_token_pair(user, db)
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login could not be completed") from exc
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Refresh access token using rotating refresh tokens"""
    refresh_token_value = payload.refresh_token
    if not refresh_token_value:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is required")

    decoded = decode_token(refresh_token_value, token_type="refresh")
    if decoded is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

    db_token = db.query(RefreshToken).filter(RefreshToken.token_hash == hash_token(refresh_token_value)).first()
    if not db_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token not recognized")

    if db_token.revoked_at is not None or db_token.replaced_by_token_id is not None:
        user_tokens = db.query(RefreshToken).filter(
            RefreshToken.user_id == db_token.user_id,
            RefreshToken.revoked_at.is_(None),
        ).all()
        now = utc_now()
        for user_token in user_tokens:
            user_token.revoked_at = now
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token has already been rotated or revoked")

    now = utc_now()
    if ensure_aware_utc(db_token.expires_at) <= now:
        db_token.revoked_at = now
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token has expired")

    user = db.query(User).filter(User.id == decoded.get("user_id")).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not available for refresh")

    try:
        access_token, new_refresh_token = issue_token_pair(user, db)
        new_db_token = db.query(RefreshToken).filter(RefreshToken.token_hash == hash_token(new_refresh_token)).first()
        db_token.revoked_at = now
        db_token.last_used_at = now
        if new_db_token:
            db_token.replaced_by_token_id = new_db_token.id
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Refresh could not be completed") from exc

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@router.post("/logout")
def logout(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Logout user and revoke active refresh tokens for the submitted token owner"""
    refresh_token_value = payload.refresh_token
    if refresh_token_value:
        token_hash = hash_token(refresh_token_value)
        now = utc_now()
        db_token = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()
        if db_token:
            db.query(RefreshToken).filter(
                RefreshToken.user_id == db_token.user_id,
                RefreshToken.revoked_at.is_(None),
            ).update(
                {"revoked_at": now, "last_used_at": now},
                synchronize_session=False,
            )
            db.commit()
    return {"message": "Successfully logged out"}
