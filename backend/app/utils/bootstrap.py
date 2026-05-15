import logging

from sqlalchemy.orm import Session

from ..config import settings
from ..models import User
from .auth import hash_password

logger = logging.getLogger(__name__)


def ensure_initial_admin(db: Session):
    if db.query(User).filter(User.role == "admin").first():
        return
    if not settings.INITIAL_ADMIN_USERNAME or not settings.INITIAL_ADMIN_EMAIL or not settings.INITIAL_ADMIN_PASSWORD:
        logger.warning("No admin user exists and INITIAL_ADMIN_* variables are not fully configured")
        return

    admin_user = User(
        username=settings.INITIAL_ADMIN_USERNAME,
        email=settings.INITIAL_ADMIN_EMAIL,
        full_name=settings.INITIAL_ADMIN_FULL_NAME,
        role="admin",
        hashed_password=hash_password(settings.INITIAL_ADMIN_PASSWORD),
        is_active=True,
    )
    db.add(admin_user)
    db.commit()
    logger.info("Initial admin user created: %s", settings.INITIAL_ADMIN_USERNAME)