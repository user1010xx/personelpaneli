from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..utils.auth import get_current_user, get_admin_user
from ..models import TrainingData
from ..schemas.training import TrainingDataResponse, TrainingDataCreate, TrainingDataUpdate
from ..utils.db import safe_commit
from ..utils.pagination import normalize_pagination

router = APIRouter(prefix="/api/training", tags=["Eğitim ve Geribildirim"])

@router.get("", response_model=List[TrainingDataResponse])
def list_training(
    personnel_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List training records with optional personnel filter"""
    skip, limit = normalize_pagination(skip, limit)
    
    query = db.query(TrainingData)
    
    if personnel_id:
        query = query.filter(TrainingData.personnel_id == personnel_id)
    
    training = query.order_by(TrainingData.date.desc()).offset(skip).limit(limit).all()
    return training

@router.get("/personnel/{personnel_id}", response_model=List[TrainingDataResponse])
def get_personnel_training(
    personnel_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all training records for specific personnel"""
    
    training = db.query(TrainingData).filter(
        TrainingData.personnel_id == personnel_id
    ).order_by(TrainingData.date.desc()).all()
    
    return training

@router.post("/", response_model=TrainingDataResponse)
def create_training(
    training: TrainingDataCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_admin_user)
):
    """Create training record (manual entry)"""
    
    db_training = TrainingData(**training.model_dump())
    db.add(db_training)
    safe_commit(db, message="Training record could not be created")
    db.refresh(db_training)
    return db_training

@router.put("/{training_id}", response_model=TrainingDataResponse)
def update_training(
    training_id: int,
    training_update: TrainingDataUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_admin_user)
):
    """Update training record"""
    
    training = db.query(TrainingData).filter(TrainingData.id == training_id).first()
    if not training:
        raise HTTPException(status_code=404, detail="Training record not found")
    
    update_data = training_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(training, field, value)
    
    safe_commit(db, message="Training record could not be updated")
    db.refresh(training)
    return training

@router.delete("/{training_id}")
def delete_training(
    training_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_admin_user)
):
    """Delete training record"""
    
    training = db.query(TrainingData).filter(TrainingData.id == training_id).first()
    if not training:
        raise HTTPException(status_code=404, detail="Training record not found")
    
    db.delete(training)
    safe_commit(db, message="Training record could not be deleted")
    return {"detail": "Training record deleted"}
