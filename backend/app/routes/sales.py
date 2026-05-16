from datetime import date
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..models import SalesData
from ..services.audit_service import AuditService
from ..services.personnel_service import PersonnelService
from ..schemas.sales import SalesDataCreate, SalesDataResponse, SalesDataUpdate
from ..services.sales_service import SalesService
from ..utils.auth import get_admin_user, get_current_user
from ..utils.db import commit_or_raise
from ..utils.dates import validate_date_range
from ..utils.pagination import normalize_pagination
from ..utils.excel import ExcelService

router = APIRouter(prefix="/api/sales", tags=["Sales Management"])


@router.get("", response_model=List[SalesDataResponse])
def list_sales(
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

    query = db.query(SalesData).options(joinedload(SalesData.personnel))

    if personnel_id:
        query = query.filter(SalesData.personnel_id == personnel_id)
    if start_date:
        query = query.filter(SalesData.date >= start_date)
    if end_date:
        query = query.filter(SalesData.date <= end_date)

    return query.order_by(SalesData.date.desc(), SalesData.id.desc()).offset(skip).limit(limit).all()


@router.get("/personnel/{personnel_id}/summary")
def get_personnel_sales_summary(
    personnel_id: int,
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    PersonnelService.get_personnel_or_404(db, personnel_id)
    validate_date_range(start_date, end_date)
    total_sales = SalesService.get_sales_by_personnel_and_date_range(
        db, personnel_id, start_date, end_date
    )

    days = (end_date - start_date).days + 1
    average = total_sales / days if days > 0 else 0

    return {
        "personnel_id": personnel_id,
        "start_date": start_date,
        "end_date": end_date,
        "total_sales": total_sales,
        "average_daily_sales": average,
        "days": days
    }


@router.get("/summary")
def get_all_sales_summary(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    validate_date_range(start_date, end_date)
    return SalesService.get_all_personnel_sales_summary(db, start_date, end_date)


@router.post("/upload-excel")
def upload_sales_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_admin_user)
):
    try:
        content = file.file.read()
        ExcelService.validate_excel_upload(file.filename, file.content_type, len(content))
        sales_data = ExcelService.parse_sales_excel(content)
        records = [(item.personnel_name, item.date, item.sales_count) for item in sales_data]
        result = SalesService.add_bulk_sales_data(db, records)
        unique_dates = sorted({str(item.date) for item in sales_data})
        AuditService.log(
            db,
            action="sales_excel_upload",
            entity_type="sales_data",
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
            action="sales_excel_upload_rejected",
            entity_type="sales_data",
            actor_user_id=current_user.get("user_id"),
            details={"filename": file.filename, "reason": str(exc)},
        )
        db.commit()
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(exc)}")


@router.post("/", response_model=SalesDataResponse)
def create_sales_record(
    sales: SalesDataCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_admin_user)
):
    PersonnelService.get_personnel_or_404(db, sales.personnel_id)
    db_sales = SalesData(**sales.model_dump())
    db.add(db_sales)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail="Sales record could not be created") from exc
    db.refresh(db_sales)
    return db_sales


@router.put("/{sales_id}", response_model=SalesDataResponse)
def update_sales_record(
    sales_id: int,
    sales_update: SalesDataUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_admin_user)
):
    sales = db.query(SalesData).filter(SalesData.id == sales_id).first()
    if not sales:
        raise HTTPException(status_code=404, detail="Sales record not found")

    update_data = sales_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(sales, field, value)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail="Sales record could not be updated") from exc
    db.refresh(sales)
    return sales


@router.delete("/{sales_id}")
def delete_sales_record(
    sales_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_admin_user)
):
    sales = db.query(SalesData).filter(SalesData.id == sales_id).first()
    if not sales:
        raise HTTPException(status_code=404, detail="Sales record not found")

    db.delete(sales)
    AuditService.log(
        db,
        action="sales_delete",
        entity_type="sales_data",
        entity_id=sales_id,
        actor_user_id=current_user.get("user_id"),
        details={"personnel_id": sales.personnel_id, "date": str(sales.date)},
    )
    commit_or_raise(db, message="Sales record could not be deleted")
    return {"detail": "Sales record deleted"}