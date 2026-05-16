from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import WarningData
from ..schemas.warning import WarningDataCreate, WarningDataResponse, WarningDataUpdate
from ..services.audit_service import AuditService
from ..services.docs_service import DocsService
from ..services.personnel_service import PersonnelService
from ..utils.auth import get_admin_user, get_current_user
from ..utils.dates import utc_now
from ..utils.pagination import normalize_pagination
from .docs_links import get_docs_link_config

router = APIRouter(prefix="/api/warnings", tags=["Uyari Kesinti"])
docs_service = DocsService()


def parse_warning_date(value: str):
    if not value:
        return None
    for date_format in ("%d.%m.%Y", "%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(value.strip(), date_format).date()
        except ValueError:
            continue
    return None


@router.get("", response_model=List[WarningDataResponse])
def list_warnings(
    personnel_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    skip, limit = normalize_pagination(skip, limit)
    query = db.query(WarningData)
    if personnel_id:
        query = query.filter(WarningData.personnel_id == personnel_id)
    return query.order_by(WarningData.date.desc(), WarningData.id.desc()).offset(skip).limit(limit).all()


@router.get("/personnel/{personnel_id}", response_model=List[WarningDataResponse])
def get_personnel_warnings(
    personnel_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    PersonnelService.get_personnel_or_404(db, personnel_id)
    return db.query(WarningData).filter(WarningData.personnel_id == personnel_id).order_by(
        WarningData.date.desc(),
        WarningData.id.desc(),
    ).all()


@router.get("/personnel/{personnel_id}/summary")
def get_personnel_warnings_summary(
    personnel_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    PersonnelService.get_personnel_or_404(db, personnel_id)
    warnings = db.query(WarningData).filter(WarningData.personnel_id == personnel_id).all()
    return {
        "personnel_id": personnel_id,
        "total_warnings": len(warnings),
        "warnings": warnings,
    }


@router.post("/", response_model=WarningDataResponse)
def create_warning(
    warning: WarningDataCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    PersonnelService.get_personnel_or_404(db, warning.personnel_id)
    db_warning = WarningData(**warning.model_dump())
    db.add(db_warning)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail="Warning could not be created") from exc
    db.refresh(db_warning)
    return db_warning


@router.put("/{warning_id}", response_model=WarningDataResponse)
def update_warning(
    warning_id: int,
    warning_update: WarningDataUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    warning = db.query(WarningData).filter(WarningData.id == warning_id).first()
    if not warning:
        raise HTTPException(status_code=404, detail="Warning not found")
    update_data = warning_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(warning, field, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail="Warning could not be updated") from exc
    db.refresh(warning)
    return warning


@router.delete("/{warning_id}")
def delete_warning(
    warning_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    warning = db.query(WarningData).filter(WarningData.id == warning_id).first()
    if not warning:
        raise HTTPException(status_code=404, detail="Warning not found")
    db.delete(warning)
    db.commit()
    return {"detail": "Warning deleted"}


@router.post("/sync-docs")
def sync_warnings_from_docs(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    try:
        docs_link = get_docs_link_config(db, "warnings")
        rows = docs_service.get_sheet_rows_by_gid(docs_link.spreadsheet_id, docs_link.gid)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if not rows:
        raise HTTPException(status_code=400, detail="Google Sheet bos veya okunamadi")

    payloads = {}
    for row in rows:
        personnel_name = (row.get("PERSONEL ADI", "") or "").strip()
        deduction = (row.get("KESINTI", "") or "").strip()
        subject = (row.get("KONU", "") or "").strip()
        warning_date = parse_warning_date((row.get("TARIH", "") or "").strip())

        if not personnel_name or not subject or warning_date is None:
            continue

        personnel = PersonnelService.resolve_personnel(db, personnel_name, include_username=True)
        if not personnel:
            continue

        payloads[(personnel.id, subject, warning_date)] = {
            "personnel_id": personnel.id,
            "deduction": deduction or None,
            "subject": subject,
            "date": warning_date,
            "notes": None,
            "docs_id": docs_link.spreadsheet_id,
            "docs_sync_date": utc_now(),
        }

    created = 0
    updated = 0
    for payload in payloads.values():
        existing = db.query(WarningData).filter(
            WarningData.personnel_id == payload["personnel_id"],
            WarningData.subject == payload["subject"],
            WarningData.date == payload["date"],
        ).first()

        if existing:
            existing.deduction = payload["deduction"]
            existing.notes = payload["notes"]
            existing.docs_id = payload["docs_id"]
            existing.docs_sync_date = payload["docs_sync_date"]
            updated += 1
            continue

        db.add(WarningData(**payload))
        created += 1

    try:
        AuditService.log(
            db,
            action="warnings_docs_sync",
            entity_type="warning_data",
            actor_user_id=current_user.get("user_id"),
            details={"created": created, "updated": updated},
        )
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail="Warnings docs sync failed") from exc
    return {
        "detail": f"{created} warning rows eklendi, {updated} warning rows guncellendi.",
        "docs_configured": True,
    }
