from collections.abc import Callable

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


def commit_or_raise(
    db: Session,
    message: str = "Database operation failed",
    rollback: bool = True,
    on_error: Callable[[], None] | None = None,
):
    try:
        db.commit()
    except IntegrityError as exc:
        if rollback:
            db.rollback()
        if on_error:
            on_error()
        raise HTTPException(status_code=400, detail=message) from exc


def safe_commit(
    db: Session,
    message: str = "Database operation failed",
    rollback: bool = True,
    on_error: Callable[[], None] | None = None,
):
    return commit_or_raise(
        db=db,
        message=message,
        rollback=rollback,
        on_error=on_error,
    )