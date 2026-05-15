from datetime import date, datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import WhatsAppData
from ..schemas.whatsapp import WhatsAppDataCreate, WhatsAppDataResponse, WhatsAppDataUpdate
from ..services.audit_service import AuditService
from ..services.docs_service import DocsService
from ..services.personnel_service import PersonnelService
from ..utils.auth import get_admin_user, get_current_user
from ..utils.dates import utc_now, validate_date_range
from ..utils.pagination import normalize_pagination
from .docs_links import get_docs_link_config

router = APIRouter(prefix="/api/whatsapp", tags=["WhatsApp Tracking"])
docs_service = DocsService()


def parse_whatsapp_date_from_headers(headers) -> date:
    parsed_dates = []
    for header in headers:
        try:
            parsed_dates.append(datetime.strptime(str(header).strip(), "%d.%m.%Y").date())
        except ValueError:
            continue

    if not parsed_dates:
        return utc_now().date()

    parsed_dates.sort()
    today = utc_now().date()
    eligible_dates = [value for value in parsed_dates if value <= today]

    if eligible_dates:
        return eligible_dates[-1]

    return parsed_dates[0]


def parse_int_value(value) -> int:
    text = str(value or "").strip()
    if not text or text.startswith("#"):
        return 0
    text = text.replace(".", "").replace(",", ".")
    try:
        return int(float(text))
    except ValueError:
        return 0


def extract_row_value(row: dict, keys: list[str]) -> str:
    for key in keys:
        if key in row:
            return row.get(key, "")
    return ""


@router.get("/", response_model=List[WhatsAppDataResponse])
def list_whatsapp_data(
    personnel_id: int = None,
    start_date: date = None,
    end_date: date = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    validate_date_range(start_date, end_date)
    skip, limit = normalize_pagination(skip, limit)

    query = db.query(WhatsAppData)

    if personnel_id:
        query = query.filter(WhatsAppData.personnel_id == personnel_id)
    if start_date:
        query = query.filter(WhatsAppData.date >= start_date)
    if end_date:
        query = query.filter(WhatsAppData.date <= end_date)

    return query.order_by(WhatsAppData.date.desc(), WhatsAppData.id.desc()).offset(skip).limit(limit).all()


@router.get("/personnel/{personnel_id}", response_model=List[WhatsAppDataResponse])
def get_personnel_whatsapp(
    personnel_id: int,
    start_date: date = None,
    end_date: date = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    PersonnelService.get_personnel_or_404(db, personnel_id)
    validate_date_range(start_date, end_date)
    skip, limit = normalize_pagination(skip, limit)

    query = db.query(WhatsAppData).filter(WhatsAppData.personnel_id == personnel_id)
    if start_date:
        query = query.filter(WhatsAppData.date >= start_date)
    if end_date:
        query = query.filter(WhatsAppData.date <= end_date)

    return query.order_by(WhatsAppData.date.desc(), WhatsAppData.id.desc()).offset(skip).limit(limit).all()


@router.get("/personnel/{personnel_id}/summary")
def get_personnel_whatsapp_summary(
    personnel_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    PersonnelService.get_personnel_or_404(db, personnel_id)
    records = db.query(WhatsAppData).filter(WhatsAppData.personnel_id == personnel_id).all()

    return {
        "personnel_id": personnel_id,
        "total_whatsapp_count": sum(record.whatsapp_count for record in records),
        "total_device_count": sum(record.device_count for record in records),
        "total_unanswered_messages": sum(record.unanswered_count for record in records),
        "records_count": len(records),
        "records": records,
    }


@router.post("/", response_model=WhatsAppDataResponse)
def create_whatsapp_record(
    whatsapp: WhatsAppDataCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    PersonnelService.get_personnel_or_404(db, whatsapp.personnel_id)
    existing = db.query(WhatsAppData).filter(
        WhatsAppData.personnel_id == whatsapp.personnel_id,
        WhatsAppData.date == whatsapp.date,
    ).first()

    if existing:
        existing.whatsapp_count = whatsapp.whatsapp_count
        existing.device_count = whatsapp.device_count
        existing.average_unanswered_count = whatsapp.average_unanswered_count
        existing.unanswered_count = whatsapp.unanswered_count
        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise HTTPException(status_code=400, detail="WhatsApp record could not be updated") from exc
        db.refresh(existing)
        return existing

    db_whatsapp = WhatsAppData(**whatsapp.model_dump())
    db.add(db_whatsapp)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail="WhatsApp record could not be created") from exc
    db.refresh(db_whatsapp)
    return db_whatsapp


@router.put("/{whatsapp_id}", response_model=WhatsAppDataResponse)
def update_whatsapp_record(
    whatsapp_id: int,
    whatsapp_update: WhatsAppDataUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    whatsapp = db.query(WhatsAppData).filter(WhatsAppData.id == whatsapp_id).first()
    if not whatsapp:
        raise HTTPException(status_code=404, detail="WhatsApp record not found")

    update_data = whatsapp_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(whatsapp, field, value)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail="WhatsApp record could not be updated") from exc
    db.refresh(whatsapp)
    return whatsapp


@router.delete("/{whatsapp_id}")
def delete_whatsapp_record(
    whatsapp_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    whatsapp = db.query(WhatsAppData).filter(WhatsAppData.id == whatsapp_id).first()
    if not whatsapp:
        raise HTTPException(status_code=404, detail="WhatsApp record not found")

    db.delete(whatsapp)
    db.commit()
    return {"detail": "WhatsApp record deleted"}


@router.post("/sync-docs")
def sync_whatsapp_from_docs(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_admin_user),
):
    try:
        docs_link = get_docs_link_config(db, "whatsapp")
        rows = docs_service.get_sheet_rows_by_gid(docs_link.spreadsheet_id, docs_link.gid)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if not rows:
        raise HTTPException(status_code=400, detail="Google Sheet bos veya okunamadi")

    sync_date = parse_whatsapp_date_from_headers(rows[0].keys())
    payload_by_key = {}

    for row in rows:
        personnel_name = (row.get("PERSONEL ADI", "") or "").strip()
        if not personnel_name:
            continue

        personnel = PersonnelService.resolve_personnel(db, personnel_name)
        if not personnel:
            continue

        payload_by_key[(personnel.id, sync_date)] = {
            "personnel_id": personnel.id,
            "whatsapp_count": parse_int_value(
                extract_row_value(row, ["TOTAL WHATSAPP ADEDI"])
            ),
            "device_count": parse_int_value(
                extract_row_value(row, ["TOTAL CIHAZ ADEDI"])
            ),
            "average_unanswered_count": parse_int_value(
                extract_row_value(row, ["ORTALAMA WHATSAPP CEVAPSIZ"])
            ),
            "unanswered_count": parse_int_value(
                extract_row_value(row, ["TOTAL WHATSAPP CEVAPSIZ"])
            ),
            "date": sync_date,
            "docs_sync_date": utc_now(),
        }

    created = 0
    updated = 0
    for payload in payload_by_key.values():
        existing = db.query(WhatsAppData).filter(
            WhatsAppData.personnel_id == payload["personnel_id"],
            WhatsAppData.date == payload["date"],
        ).first()

        if existing:
            existing.whatsapp_count = payload["whatsapp_count"]
            existing.device_count = payload["device_count"]
            existing.average_unanswered_count = payload["average_unanswered_count"]
            existing.unanswered_count = payload["unanswered_count"]
            existing.docs_sync_date = payload["docs_sync_date"]
            updated += 1
            continue

        db.add(WhatsAppData(**payload))
        created += 1

    try:
        AuditService.log(
            db,
            action="whatsapp_docs_sync",
            entity_type="whatsapp_data",
            actor_user_id=current_user.get("user_id"),
            details={"created": created, "updated": updated, "sync_date": str(sync_date)},
        )
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail="WhatsApp docs sync failed") from exc
    return {
        "detail": f"{created} WhatsApp rows eklendi, {updated} WhatsApp rows guncellendi.",
        "sync_date": str(sync_date),
    }
