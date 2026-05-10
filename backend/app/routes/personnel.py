from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..utils.auth import get_current_user
from ..models import Personnel
from ..schemas.personnel import PersonnelResponse, PersonnelCreate, PersonnelUpdate

router = APIRouter(prefix="/api/personnel", tags=["Personnel Management"])

@router.get("/", response_model=List[PersonnelResponse])
def list_personnel(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """List all personnel"""
    personnel = db.query(Personnel).all()
    return personnel

@router.get("/{personnel_id}", response_model=PersonnelResponse)
def get_personnel(personnel_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Get personnel details"""
    personnel = db.query(Personnel).filter(Personnel.id == personnel_id).first()
    if not personnel:
        raise HTTPException(status_code=404, detail="Personnel not found")
    return personnel

@router.post("/", response_model=PersonnelResponse)
def create_personnel(personnel: PersonnelCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Create new personnel record"""
    
    # Check if employee_id already exists
    existing = db.query(Personnel).filter(Personnel.employee_id == personnel.employee_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Employee ID already exists")
    
    db_personnel = Personnel(**personnel.dict())
    db.add(db_personnel)
    db.commit()
    db.refresh(db_personnel)
    return db_personnel

@router.put("/{personnel_id}", response_model=PersonnelResponse)
def update_personnel(personnel_id: int, personnel_update: PersonnelUpdate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Update personnel record"""
    
    personnel = db.query(Personnel).filter(Personnel.id == personnel_id).first()
    if not personnel:
        raise HTTPException(status_code=404, detail="Personnel not found")
    
    update_data = personnel_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(personnel, field, value)
    
    db.commit()
    db.refresh(personnel)
    return personnel

@router.delete("/{personnel_id}")
def delete_personnel(personnel_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Delete personnel record"""
    
    personnel = db.query(Personnel).filter(Personnel.id == personnel_id).first()
    if not personnel:
        raise HTTPException(status_code=404, detail="Personnel not found")
    
    db.delete(personnel)
    db.commit()
    return {"detail": "Personnel deleted successfully"}
