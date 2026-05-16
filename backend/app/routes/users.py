from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas.user import UserResponse, UserCreate, UserUpdate
from ..services.audit_service import log_audit
from ..utils.auth import get_admin_user
from ..utils.dates import utc_now
from ..utils.db import safe_commit
from ..utils.pagination import normalize_pagination

router = APIRouter(prefix="/api/users", tags=["User Management"])

@router.get("", response_model=List[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    """List all users (admin only)"""
    skip, limit = normalize_pagination(skip, limit)
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db), admin: dict = Depends(get_admin_user)):
    """Create new user (admin only)"""
    from ..utils.auth import hash_password
    
    # Check if user exists
    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        hashed_password=hash_password(user.password)
    )
    db.add(db_user)
    log_audit(
        db,
        action="user_create",
        entity_type="user",
        entity_id=None,
        actor_user_id=admin.get("user_id"),
        details={"username": db_user.username, "email": db_user.email, "role": db_user.role},
    )
    safe_commit(db, message="User could not be created")
    db.refresh(db_user)
    return db_user

@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db), admin: dict = Depends(get_admin_user)):
    """Update user (admin only)"""
    from ..models import RefreshToken
    from ..utils.auth import hash_password
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_update.username and user_update.username != user.username:
        existing_username = db.query(User).filter(User.username == user_update.username).first()
        if existing_username:
            raise HTTPException(status_code=400, detail="Username already exists")
        user.username = user_update.username

    if user_update.email and user_update.email != user.email:
        existing_email = db.query(User).filter(User.email == user_update.email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already exists")
        user.email = user_update.email

    if user_update.full_name is not None:
        user.full_name = user_update.full_name
    if user_update.role:
        if user_update.role != user.role:
            now = utc_now()
            db.query(RefreshToken).filter(
                RefreshToken.user_id == user.id,
                RefreshToken.revoked_at.is_(None),
            ).update({"revoked_at": now}, synchronize_session=False)
        user.role = user_update.role
    if user_update.password:
        user.hashed_password = hash_password(user_update.password)
        now = utc_now()
        db.query(RefreshToken).filter(
            RefreshToken.user_id == user.id,
            RefreshToken.revoked_at.is_(None),
        ).update({"revoked_at": now}, synchronize_session=False)

    log_audit(
        db,
        action="user_update",
        entity_type="user",
        entity_id=user.id,
        actor_user_id=admin.get("user_id"),
        details={"updated_fields": list(user_update.model_dump(exclude_unset=True).keys())},
    )
    safe_commit(db, message="User could not be updated")
    db.refresh(user)
    return user

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), admin: dict = Depends(get_admin_user)):
    """Delete user (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == admin.get("user_id"):
        raise HTTPException(status_code=400, detail="Active admin user cannot be deleted")
    
    user_details = {"username": user.username, "email": user.email, "role": user.role}
    db.delete(user)
    log_audit(
        db,
        action="user_delete",
        entity_type="user",
        entity_id=user_id,
        actor_user_id=admin.get("user_id"),
        details=user_details,
    )
    safe_commit(db, message="User could not be deleted")
    return {"detail": "User deleted successfully"}
