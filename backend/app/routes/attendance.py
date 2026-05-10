from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from ..database import get_db
from ..utils.auth import get_current_user
from ..models import AttendanceData
from ..schemas.attendance import AttendanceDataResponse, AttendanceDataCreate, AttendanceDataUpdate

router = APIRouter(prefix="/api/attendance", tags=["Attendance Management"])

@router.get("/", response_model=List[AttendanceDataResponse])
def list_attendance(
    personnel_id: int = None,
    month: int = None,
    year: int = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List attendance records with optional filters"""
    
    query = db.query(AttendanceData)
    
    if personnel_id:
        query = query.filter(AttendanceData.personnel_id == personnel_id)
    if month:
        query = query.filter(AttendanceData.month == month)
    if year:
        query = query.filter(AttendanceData.year == year)
    
    attendance = query.all()
    return attendance

@router.get("/{personnel_id}/{month}/{year}", response_model=AttendanceDataResponse)
def get_personnel_attendance(
    personnel_id: int,
    month: int,
    year: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get attendance for specific personnel and month"""
    
    attendance = db.query(AttendanceData).filter(
        AttendanceData.personnel_id == personnel_id,
        AttendanceData.month == month,
        AttendanceData.year == year
    ).first()
    
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    
    return attendance

@router.post("/", response_model=AttendanceDataResponse)
def create_attendance(
    attendance: AttendanceDataCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create attendance record"""
    
    # Check for existing
    existing = db.query(AttendanceData).filter(
        AttendanceData.personnel_id == attendance.personnel_id,
        AttendanceData.month == attendance.month,
        AttendanceData.year == attendance.year
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Attendance record already exists for this month")
    
    db_attendance = AttendanceData(**attendance.dict())
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    return db_attendance

@router.put("/{attendance_id}", response_model=AttendanceDataResponse)
def update_attendance(
    attendance_id: int,
    attendance_update: AttendanceDataUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update attendance record"""
    
    attendance = db.query(AttendanceData).filter(AttendanceData.id == attendance_id).first()
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    
    update_data = attendance_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(attendance, field, value)
    
    db.commit()
    db.refresh(attendance)
    return attendance

@router.delete("/{attendance_id}")
def delete_attendance(
    attendance_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete attendance record"""
    
    attendance = db.query(AttendanceData).filter(AttendanceData.id == attendance_id).first()
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    
    db.delete(attendance)
    db.commit()
    return {"detail": "Attendance record deleted"}
