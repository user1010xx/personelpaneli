from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..schemas.user import UserCreate, UserResponse
from ..utils.auth import hash_password

router = APIRouter(prefix="/api/setup", tags=["Setup"])

@router.post("/create-admin", response_model=UserResponse)
def create_initial_admin(user: UserCreate, db: Session = Depends(get_db)):
    """Create initial admin user (only if no admin exists)"""

    # Check if admin already exists
    existing_admin = db.query(User).filter(User.role == "admin").first()
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin user already exists"
        )

    # Check if any user exists
    any_user = db.query(User).first()
    if any_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Users already exist. Cannot create admin via setup endpoint."
        )

    # Create admin user
    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role="admin",
        hashed_password=hash_password(user.password),
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
