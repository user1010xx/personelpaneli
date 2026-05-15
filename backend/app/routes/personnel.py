from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Personnel
from ..schemas.personnel import PersonnelCreate, PersonnelResponse, PersonnelUpdate
from ..services.audit_service import AuditService
from ..services.docs_service import DocsService
from ..services.personnel_service import PersonnelService
from ..utils.auth import get_admin_user, get_current_user
from ..utils.pagination import normalize_pagination
from .docs_links import get_docs_link_config

router = APIRouter(prefix="/api/personnel", tags=["Personnel Management"])
docs_service = DocsService()


def get_row_value(row: dict, *keys: str) -> str:
    normalized_row = {}
    for key, value in row.items():
        normalized_key = str(key).strip().casefold()
        if value is None:
            normalized_row[normalized_key] = ""
            continue
        text_value = str(value).strip()
        if text_value.casefold() in {"none", "nan", "null"}:
            normalized_row[normalized_key] = ""
            continue
        normalized_row[normalized_key] = text_value
    for key in keys:
        normalized_key = str(key).strip().casefold()
        if normalized_key in normalized_row:
            return normalized_row[normalized_key]
    return ""


def parse_optional_date(value: str):
    if not value:
        return None
    for date_format in ("%d.%m.%Y", "%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(value.strip(), date_format).date()
        except ValueError:
            continue
    return None


def parse_optional_email(value: str):
    if not value:
        return None
    candidate = value.strip()
    if not candidate or "@" not in candidate:
        return None
    return candidate


def find_existing_personnel(db: Session, username: str):
    personnel = db.query(Personnel).filter(Personnel.username == username).first()
    if personnel:
        return personnel
    return db.query(Personnel).filter(Personnel.employee_id == username).first()


@router.get("/", response_model=List[PersonnelResponse])
def list_personnel(
    skip: int = 0,
    limit: int = 1000,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    skip, limit = normalize_pagination(skip, limit)
    return db.query(Personnel).order_by(Personnel.name.asc(), Personnel.id.asc()).offset(skip).limit(limit).all()


@router.post("/sync-docs")
def sync_personnel_from_docs(db: Session = Depends(get_db), current_user: dict = Depends(get_admin_user)):
    try:
        docs_link = get_docs_link_config(db, "personnel")
        rows = docs_service.get_sheet_rows_by_gid(docs_link.spreadsheet_id, docs_link.gid)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if not rows:
        raise HTTPException(status_code=400, detail="Google Sheet bos veya okunamadi")

    success = 0
    created = 0
    updated = 0
    skipped = []

    for row in rows:
        name = get_row_value(row, "PERSONEL ADI")
        username = get_row_value(row, "KULLANICI ADI")
        hire_date = parse_optional_date(get_row_value(row, "İŞE GİRİŞ TARİHİ", "ISE GIRIS TARIHI"))
        reference = get_row_value(row, "REFERANSI", "REFERANS")
        department = get_row_value(row, "DEPARTMAN", "DEPARTMENT", "BIRIM")
        position = get_row_value(row, "POZISYON", "GOREV", "UNVAN", "POSITION")
        phone = get_row_value(row, "TELEFON", "TELEFON NUMARASI", "CEP TELEFONU", "PHONE")
        if not name or not username:
            skipped.append({"reason": "missing_name_or_username", "row": row})
            continue

        personnel = find_existing_personnel(db, username)
        if not personnel:
            personnel = Personnel(employee_id=username)
            db.add(personnel)
            created += 1
        else:
            updated += 1

        personnel.name = name
        personnel.employee_id = username
        personnel.username = username
        personnel.hire_date = hire_date
        personnel.reference = reference or None
        personnel.department = department or None
        personnel.position = position or None
        personnel.email = parse_optional_email(get_row_value(row, "MAİL", "MAIL", "E-POSTA", "EPOSTA"))
        personnel.phone = phone or None
        personnel.promotion_date = parse_optional_date(
            get_row_value(row, "TERFİ TARİHİ", "TERFI TARIHI", "TEFİ TARİHİ")
        )
        success += 1

    try:
        AuditService.log(
            db,
            action="personnel_docs_sync",
            entity_type="personnel",
            actor_user_id=current_user.get("user_id"),
            details={"success": success, "created": created, "updated": updated},
        )
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail="Personnel docs sync failed") from exc
    return {
        "detail": f"{success} personnel rows synced successfully. {created} created, {updated} updated.",
        "docs_configured": True,
        "created": created,
        "updated": updated,
        "skipped": skipped,
    }


@router.post("/", response_model=PersonnelResponse)
def create_personnel(
    personnel: PersonnelCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    existing = db.query(Personnel).filter(Personnel.employee_id == personnel.employee_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Employee ID already exists")
    db_personnel = Personnel(**personnel.model_dump())
    db.add(db_personnel)
    try:
        db.flush()
        AuditService.log(
            db,
            action="personnel_create",
            entity_type="personnel",
            entity_id=db_personnel.id,
            actor_user_id=current_user.get("user_id"),
            details={"employee_id": db_personnel.employee_id},
        )
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail="Personnel could not be created") from exc
    db.refresh(db_personnel)
    return db_personnel


@router.get("/{personnel_id}", response_model=PersonnelResponse)
def get_personnel(personnel_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return PersonnelService.get_personnel_or_404(db, personnel_id)


@router.put("/{personnel_id}", response_model=PersonnelResponse)
def update_personnel(
    personnel_id: int,
    personnel_update: PersonnelUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    personnel = PersonnelService.get_personnel_or_404(db, personnel_id)
    update_data = personnel_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(personnel, field, value)
    try:
        AuditService.log(
            db,
            action="personnel_update",
            entity_type="personnel",
            entity_id=personnel.id,
            actor_user_id=current_user.get("user_id"),
            details={"updated_fields": list(update_data.keys())},
        )
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail="Personnel could not be updated") from exc
    db.refresh(personnel)
    return personnel


@router.delete("/{personnel_id}")
def delete_personnel(
    personnel_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    personnel = PersonnelService.get_personnel_or_404(db, personnel_id)
    db.delete(personnel)
    AuditService.log(
        db,
        action="personnel_delete",
        entity_type="personnel",
        entity_id=personnel_id,
        actor_user_id=current_user.get("user_id"),
        details={"name": personnel.name, "employee_id": personnel.employee_id},
    )
    db.commit()
    return {"detail": "Personnel deleted successfully"}
