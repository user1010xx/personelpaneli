from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import AttendanceData
from ..schemas.attendance import AttendanceDataCreate, AttendanceDataResponse, AttendanceDataUpdate
from ..services.audit_service import AuditService
from ..services.docs_service import DocsService
from ..services.personnel_service import PersonnelService
from ..utils.auth import get_admin_user, get_current_user
from ..utils.dates import utc_now
from ..utils.pagination import normalize_pagination
from .docs_links import get_docs_link_config

router = APIRouter(prefix="/api/attendance", tags=["Puantaj"])
docs_service = DocsService()


def extract_month_year(headers: list[str]):
    for header in headers:
        try:
            parsed = datetime.strptime(header.strip(), "%d.%m.%Y")
            return parsed.month, parsed.year
        except ValueError:
            continue
    now = datetime.now()
    return now.month, now.year


def calculate_totals(row: dict):
    worked_days = 0.0
    leave_days = 0.0

    for key, value in row.items():
        cell = PersonnelService.normalize_cell_value(value)
        if not key or key == "PERSONEL ADI":
            continue
        try:
            datetime.strptime(key.strip(), "%d.%m.%Y")
        except ValueError:
            continue

        if cell == "VAR":
            worked_days += 1.0
        elif "HAFTALIK IZIN" in cell:
            worked_days += 1.0
        elif "YARIM" in cell:
            worked_days += 0.5
            leave_days += 0.5
        elif cell == "YOK":
            leave_days += 1.0
        elif "MESAI" in cell:
            worked_days += 1.0
        elif cell:
            leave_days += 1.0

    return round(worked_days, 1), round(leave_days, 1)


@router.get("", response_model=List[AttendanceDataResponse])
def list_attendance(
    personnel_id: int = None,
    month: int = None,
    year: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    skip, limit = normalize_pagination(skip, limit)
    query = db.query(AttendanceData)
    if personnel_id:
        query = query.filter(AttendanceData.personnel_id == personnel_id)
    if month:
        query = query.filter(AttendanceData.month == month)
    if year:
        query = query.filter(AttendanceData.year == year)
    return query.order_by(AttendanceData.year.desc(), AttendanceData.month.desc(), AttendanceData.id.desc()).offset(skip).limit(limit).all()


@router.get("/{personnel_id}/{month}/{year}", response_model=AttendanceDataResponse)
def get_personnel_attendance(personnel_id: int, month: int, year: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    PersonnelService.get_personnel_or_404(db, personnel_id)
    attendance = db.query(AttendanceData).filter(
        AttendanceData.personnel_id == personnel_id,
        AttendanceData.month == month,
        AttendanceData.year == year,
    ).first()
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    return attendance


@router.post("/", response_model=AttendanceDataResponse)
def create_attendance(attendance: AttendanceDataCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_admin_user)):
    PersonnelService.get_personnel_or_404(db, attendance.personnel_id)
    existing = db.query(AttendanceData).filter(
        AttendanceData.personnel_id == attendance.personnel_id,
        AttendanceData.month == attendance.month,
        AttendanceData.year == attendance.year,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Attendance record already exists for this month")
    db_attendance = AttendanceData(**attendance.model_dump())
    db.add(db_attendance)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail="Attendance record could not be created") from exc
    db.refresh(db_attendance)
    return db_attendance


@router.put("/{attendance_id}", response_model=AttendanceDataResponse)
def update_attendance(attendance_id: int, attendance_update: AttendanceDataUpdate, db: Session = Depends(get_db), current_user: dict = Depends(get_admin_user)):
    attendance = db.query(AttendanceData).filter(AttendanceData.id == attendance_id).first()
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    try:
        attendance_update.validate_with_existing(attendance)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    update_data = attendance_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(attendance, field, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail="Attendance record could not be updated") from exc
    db.refresh(attendance)
    return attendance


@router.delete("/{attendance_id}")
def delete_attendance(attendance_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_admin_user)):
    attendance = db.query(AttendanceData).filter(AttendanceData.id == attendance_id).first()
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    db.delete(attendance)
    db.commit()
    return {"detail": "Attendance record deleted"}


@router.post("/sync-docs")
def sync_attendance_from_docs(db: Session = Depends(get_db), current_user: dict = Depends(get_admin_user)):
    try:
        docs_link = get_docs_link_config(db, "attendance")
        rows = docs_service.get_sheet_rows_by_gid(docs_link.spreadsheet_id, docs_link.gid)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if not rows:
        raise HTTPException(status_code=400, detail="Google Sheet bos veya okunamadi")

    headers = list(rows[0].keys())
    month, year = extract_month_year(headers)

    success = 0
    for row in rows:
        personnel_name = (row.get("PERSONEL ADI", "") or "").strip()
        if not personnel_name:
            continue

        personnel = PersonnelService.resolve_personnel(db, personnel_name)
        if not personnel:
            continue

        working_days, leave_days = calculate_totals(row)
        attendance = db.query(AttendanceData).filter(
            AttendanceData.personnel_id == personnel.id,
            AttendanceData.month == month,
            AttendanceData.year == year,
        ).first()

        if not attendance:
            attendance = AttendanceData(
                personnel_id=personnel.id,
                month=month,
                year=year,
            )
            db.add(attendance)

        attendance.working_days = working_days
        attendance.leave_days = leave_days
        attendance.leave_type = "docs"
        attendance.docs_sync_date = utc_now()
        success += 1

    try:
        AuditService.log(
            db,
            action="attendance_docs_sync",
            entity_type="attendance_data",
            actor_user_id=current_user.get("user_id"),
            details={"synced_rows": success, "month": month, "year": year},
        )
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail="Attendance docs sync failed") from exc
    return {
        "detail": f"{success} attendance rows synced successfully.",
        "docs_configured": True,
        "month": month,
        "year": year,
    }