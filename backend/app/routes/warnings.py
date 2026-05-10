from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..utils.auth import get_current_user
from ..models import WarningData
from ..schemas.warning import WarningDataResponse, WarningDataCreate, WarningDataUpdate

router = APIRouter(prefix="/api/warnings", tags=["Warnings Management"])

@router.get("/", response_model=List[WarningDataResponse])
def list_warnings(
    personnel_id: int = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List warnings with optional personnel filter"""
    
    query = db.query(WarningData)
    
    if personnel_id:
        query = query.filter(WarningData.personnel_id == personnel_id)
    
    warnings = query.all()
    return warnings

@router.get("/personnel/{personnel_id}", response_model=List[WarningDataResponse])
def get_personnel_warnings(
    personnel_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all warnings for specific personnel"""
    
    warnings = db.query(WarningData).filter(
        WarningData.personnel_id == personnel_id
    ).order_by(WarningData.date.desc()).all()
    
    return warnings

@router.get("/personnel/{personnel_id}/summary")
def get_personnel_warnings_summary(
    personnel_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get warning summary for personnel"""
    
    warnings = db.query(WarningData).filter(
        WarningData.personnel_id == personnel_id
    ).all()
    
    return {
        "personnel_id": personnel_id,
        "total_warnings": len(warnings),
        "warnings": warnings
    }

@router.post("/", response_model=WarningDataResponse)
def create_warning(
    warning: WarningDataCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create warning record (manual entry or from Docs sync)"""
    
    db_warning = WarningData(**warning.dict())
    db.add(db_warning)
    db.commit()
    db.refresh(db_warning)
    return db_warning

@router.put("/{warning_id}", response_model=WarningDataResponse)
def update_warning(
    warning_id: int,
    warning_update: WarningDataUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update warning record"""
    
    warning = db.query(WarningData).filter(WarningData.id == warning_id).first()
    if not warning:
        raise HTTPException(status_code=404, detail="Warning not found")
    
    update_data = warning_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(warning, field, value)
    
    db.commit()
    db.refresh(warning)
    return warning

@router.delete("/{warning_id}")
def delete_warning(
    warning_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete warning record"""
    
    warning = db.query(WarningData).filter(WarningData.id == warning_id).first()
    if not warning:
        raise HTTPException(status_code=404, detail="Warning not found")
    
    db.delete(warning)
    db.commit()
    return {"detail": "Warning deleted"}
