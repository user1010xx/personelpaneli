from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from ..database import get_db
from ..utils.auth import get_current_user
from ..models import SalesData
from ..schemas.sales import SalesDataResponse, SalesDataCreate, SalesDataBulkUpload
from ..services.sales_service import SalesService
from ..utils.excel import ExcelService

router = APIRouter(prefix="/api/sales", tags=["Sales Management"])

@router.get("/", response_model=List[SalesDataResponse])
def list_sales(
    personnel_id: int = None,
    start_date: date = None,
    end_date: date = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List sales data with optional filters and pagination"""
    
    if limit > 1000:
        limit = 1000  # Max 1000 records per request
    
    query = db.query(SalesData).options(joinedload(SalesData.personnel))
    
    if personnel_id:
        query = query.filter(SalesData.personnel_id == personnel_id)
    if start_date:
        query = query.filter(SalesData.date >= start_date)
    if end_date:
        query = query.filter(SalesData.date <= end_date)
    
    sales = query.order_by(SalesData.date.desc()).offset(skip).limit(limit).all()
    return sales

@router.get("/personnel/{personnel_id}/summary")
def get_personnel_sales_summary(
    personnel_id: int,
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get sales summary for specific personnel in date range"""
    
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
    """Get sales summary for all personnel"""
    
    summary = SalesService.get_all_personnel_sales_summary(db, start_date, end_date)
    return summary

@router.post("/upload-excel")
def upload_sales_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Upload sales data from Excel file"""
    
    try:
        # Read file content
        content = file.file.read()
        
        # Parse Excel
        sales_data = ExcelService.parse_sales_excel(content)
        
        # Convert to tuples for service
        records = [(sd.personnel_name, sd.date, sd.sales_count) for sd in sales_data]
        
        # Add to database
        result = SalesService.add_bulk_sales_data(db, records)
        
        return {
            "success": result["success"],
            "failed": result["failed"],
            "errors": result["errors"],
            "message": f"Uploaded {result['success']} records successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.post("/", response_model=SalesDataResponse)
def create_sales_record(
    sales: SalesDataCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create individual sales record"""
    
    db_sales = SalesData(**sales.dict())
    db.add(db_sales)
    db.commit()
    db.refresh(db_sales)
    return db_sales

@router.put("/{sales_id}", response_model=SalesDataResponse)
def update_sales_record(
    sales_id: int,
    sales_update: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update sales record"""
    
    sales = db.query(SalesData).filter(SalesData.id == sales_id).first()
    if not sales:
        raise HTTPException(status_code=404, detail="Sales record not found")
    
    if "sales_count" in sales_update:
        sales.sales_count = sales_update["sales_count"]
    
    db.commit()
    db.refresh(sales)
    return sales
