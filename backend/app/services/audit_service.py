from typing import Any

from sqlalchemy.orm import Session

from ..models import AuditLog


class AuditService:
    @staticmethod
    def log(
        db: Session,
        action: str,
        entity_type: str,
        actor_user_id: int | None = None,
        entity_id: Any = None,
        details: dict | None = None,
    ) -> AuditLog:
        entry = AuditLog(
            actor_user_id=actor_user_id,
            action=action,
            entity_type=entity_type,
            entity_id=str(entity_id) if entity_id is not None else None,
            details=details or {},
        )
        db.add(entry)
        db.flush()
        return entry


def log_audit(
    db: Session,
    action: str,
    entity_type: str,
    actor_user_id: int | None = None,
    entity_id: Any = None,
    details: dict | None = None,
) -> AuditLog:
    return AuditService.log(
        db=db,
        action=action,
        entity_type=entity_type,
        actor_user_id=actor_user_id,
        entity_id=entity_id,
        details=details,
    )