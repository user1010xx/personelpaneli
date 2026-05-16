from datetime import date
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..models import CallProcessData
from ..schemas.call_process import CallProcessDataCreate, CallProcessDataResponse, CallProcessDataUpdate
from ..services.audit_service import AuditService
from ..services.call_process_service import CallProcessService
from ..services.personnel_service import PersonnelService
from ..utils.auth import get_admin_user, get_current_user
from ..utils.db import commit_or_raise
from ..utils.dates import validate_date_range
from ..utils.excel import ExcelService
from ..utils.pagination import normalize_pagination

router = APIRouter(prefix="/api/call-process", tags=["Call Process"])


@router.get("", response_model=List[CallProcessDataResponse])
def list_call_process(
    personnel_id: int = None,
    start_date: date = None,
    end_date: date = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    validate_date_range(start_date, end_date)
    skip, limit = normalize_pagination(skip, limit)

    query = db.query(CallProcessData).options(joinedload(CallProcessData.personnel))

    if personnel_id:
        query = query.filter(CallProcessData.personnel_id == personnel_id)
    if start_date:
        query = query.filter(CallProcessData.date >= start_date)
    if end_date:
        query = query.filter(CallProcessData.date <= end_date)

    return query.order_by(CallProcessData.date.desc(), CallProcessData.id.desc()).offset(skip).limit(limit).all()


@router.get("/summary")
def get_all_call_process_summary(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    validate_date_range(start_date, end_date)
    return CallProcessService.get_all_personnel_summary(db, start_date, end_date)


@router.post("/upload-excel")
def upload_call_process_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_admin_user)
):
    try:
        content = file.file.read()
        ExcelService.validate_excel_upload(file.filename, file.content_type, len(content))
        records = ExcelService.parse_call_process_excel(content)
        payload = [
            (record.personnel_name, record.date, record.call_count, record.talk_duration, record.average_ring_duration)
            for record in records
        ]
        result = CallProcessService.add_bulk_call_process_data(db, payload)
        unique_dates = sorted({str(record.date) for record in records})
        AuditService.log(
            db,
            action="call_process_excel_upload",
            entity_type="call_process_data",
            actor_user_id=current_user.get("user_id"),
            details={
                "filename": file.filename,
                "content_type": file.content_type,
                "success": result["success"],
                "failed": result["failed"],
                "target_dates": unique_dates,
            },
        )
        db.commit()

        return {
            "success": result["success"],
            "failed": result["failed"],
            "errors": result["errors"],
            "message": f"Uploaded {result['success']} records successfully",
            "target_dates": unique_dates,
        }
    except ValueError as exc:
        db.rollback()
        AuditService.log(
            db,
            action="call_process_excel_upload_rejected",
            entity_type="call_process_data",
            actor_user_id=current_user.get("user_id"),
            details={"filename": file.filename, "reason": str(exc)},
        )
        db.commit()
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(exc)}")


@router.post("/", response_model=CallProcessDataResponse)
def create_call_process_record(
    call_process: CallProcessDataCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_admin_user)
):
    PersonnelService.get_personnel_or_404(db, call_process.personnel_id)
    db_record = CallProcessData(**call_process.model_dump())
    db.add(db_record)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail="Call process record could not be created") from exc
    db.refresh(db_record)
    return db_record


@router.put("/{record_id}", response_model=CallProcessDataResponse)
def update_call_process_record(
    record_id: int,
    call_process_update: CallProcessDataUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_admin_user)
):
    record = db.query(CallProcessData).filter(CallProcessData.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Call process record not found")

    for field, value in call_process_update.model_dump(exclude_unset=True).items():
        setattr(record, field, value)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail="Call process record could not be updated") from exc
    db.refresh(record)
    return record


@router.delete("/{record_id}")
def delete_call_process_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_admin_user)
):
    record = db.query(CallProcessData).filter(CallProcessData.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Call process record not found")

    db.delete(record)
    AuditService.log(
        db,
        action="call_process_delete",
        entity_type="call_process_data",
        entity_id=record_id,
        actor_user_id=current_user.get("user_id"),
        details={"personnel_id": record.personnel_id, "date": str(record.date)},
    )
    commit_or_raise(db, message="Call process record could not be deleted")
    return {"detail": "Call process record deleted"}