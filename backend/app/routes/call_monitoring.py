from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..utils.auth import get_current_user, get_admin_user
from ..models import CallMonitoring
from ..schemas.call_monitoring import CallMonitoringResponse, CallMonitoringCreate, CallMonitoringUpdate
from ..utils.db import safe_commit
from ..utils.pagination import normalize_pagination

router = APIRouter(prefix="/api/call-monitoring", tags=["Kalite Puanlaması"])

@router.get("", response_model=List[CallMonitoringResponse])
def list_call_records(
    personnel_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List call monitoring records with optional personnel filter"""
    skip, limit = normalize_pagination(skip, limit)
    
    query = db.query(CallMonitoring)
    
    if personnel_id:
        query = query.filter(CallMonitoring.personnel_id == personnel_id)
    
    records = query.order_by(CallMonitoring.date.desc()).offset(skip).limit(limit).all()
    return records

@router.get("/personnel/{personnel_id}", response_model=List[CallMonitoringResponse])
def get_personnel_calls(
    personnel_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all call records for specific personnel"""
    
    records = db.query(CallMonitoring).filter(
        CallMonitoring.personnel_id == personnel_id
    ).order_by(CallMonitoring.date.desc()).all()
    
    return records

@router.get("/personnel/{personnel_id}/summary")
def get_personnel_call_summary(
    personnel_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get call quality summary for personnel"""
    
    records = db.query(CallMonitoring).filter(
        CallMonitoring.personnel_id == personnel_id
    ).all()
    
    if not records:
        return {
            "personnel_id": personnel_id,
            "total_calls": 0,
            "average_score": 0,
            "min_score": 0,
            "max_score": 0
        }
    
    scores = [r.quality_score for r in records]
    
    return {
        "personnel_id": personnel_id,
        "total_calls": len(records),
        "average_score": sum(scores) / len(scores),
        "min_score": min(scores),
        "max_score": max(scores),
        "records": records
    }

@router.post("/", response_model=CallMonitoringResponse)
def create_call_record(
    call: CallMonitoringCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_admin_user)
):
    """Create call monitoring record (manual entry)"""
    
    db_call = CallMonitoring(**call.model_dump())
    db.add(db_call)
    safe_commit(db, message="Call monitoring record could not be created")
    db.refresh(db_call)
    return db_call

@router.put("/{call_id}", response_model=CallMonitoringResponse)
def update_call_record(
    call_id: int,
    call_update: CallMonitoringUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_admin_user)
):
    """Update call monitoring record"""
    
    call = db.query(CallMonitoring).filter(CallMonitoring.id == call_id).first()
    if not call:
        raise HTTPException(status_code=404, detail="Call record not found")
    
    update_data = call_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(call, field, value)
    
    safe_commit(db, message="Call monitoring record could not be updated")
    db.refresh(call)
    return call

@router.delete("/{call_id}")
def delete_call_record(
    call_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_admin_user)
):
    """Delete call monitoring record"""
    
    call = db.query(CallMonitoring).filter(CallMonitoring.id == call_id).first()
    if not call:
        raise HTTPException(status_code=404, detail="Call record not found")
    
    db.delete(call)
    safe_commit(db, message="Call monitoring record could not be deleted")
    return {"detail": "Call record deleted"}
