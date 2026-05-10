from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..utils.auth import get_current_user
from ..models import WhatsAppData
from ..schemas.whatsapp import WhatsAppDataResponse, WhatsAppDataCreate, WhatsAppDataUpdate

router = APIRouter(prefix="/api/whatsapp", tags=["WhatsApp Tracking"])

@router.get("/", response_model=List[WhatsAppDataResponse])
def list_whatsapp_data(
    personnel_id: int = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List WhatsApp records with optional personnel filter"""
    
    query = db.query(WhatsAppData)
    
    if personnel_id:
        query = query.filter(WhatsAppData.personnel_id == personnel_id)
    
    records = query.order_by(WhatsAppData.date.desc()).all()
    return records

@router.get("/personnel/{personnel_id}", response_model=List[WhatsAppDataResponse])
def get_personnel_whatsapp(
    personnel_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all WhatsApp records for specific personnel"""
    
    records = db.query(WhatsAppData).filter(
        WhatsAppData.personnel_id == personnel_id
    ).order_by(WhatsAppData.date.desc()).all()
    
    return records

@router.get("/personnel/{personnel_id}/summary")
def get_personnel_whatsapp_summary(
    personnel_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get WhatsApp summary for personnel"""
    
    records = db.query(WhatsAppData).filter(
        WhatsAppData.personnel_id == personnel_id
    ).all()
    
    total_unanswered = sum(r.unanswered_count for r in records)
    
    return {
        "personnel_id": personnel_id,
        "total_unanswered_messages": total_unanswered,
        "records_count": len(records),
        "records": records
    }

@router.post("/", response_model=WhatsAppDataResponse)
def create_whatsapp_record(
    whatsapp: WhatsAppDataCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create WhatsApp record (manual entry or from Docs sync)"""
    
    # Check for existing record for same date
    existing = db.query(WhatsAppData).filter(
        WhatsAppData.personnel_id == whatsapp.personnel_id,
        WhatsAppData.date == whatsapp.date
    ).first()
    
    if existing:
        # Update existing
        existing.unanswered_count = whatsapp.unanswered_count
        db.commit()
        db.refresh(existing)
        return existing
    
    db_whatsapp = WhatsAppData(**whatsapp.dict())
    db.add(db_whatsapp)
    db.commit()
    db.refresh(db_whatsapp)
    return db_whatsapp

@router.put("/{whatsapp_id}", response_model=WhatsAppDataResponse)
def update_whatsapp_record(
    whatsapp_id: int,
    whatsapp_update: WhatsAppDataUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update WhatsApp record"""
    
    whatsapp = db.query(WhatsAppData).filter(WhatsAppData.id == whatsapp_id).first()
    if not whatsapp:
        raise HTTPException(status_code=404, detail="WhatsApp record not found")
    
    update_data = whatsapp_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(whatsapp, field, value)
    
    db.commit()
    db.refresh(whatsapp)
    return whatsapp

@router.delete("/{whatsapp_id}")
def delete_whatsapp_record(
    whatsapp_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete WhatsApp record"""
    
    whatsapp = db.query(WhatsAppData).filter(WhatsAppData.id == whatsapp_id).first()
    if not whatsapp:
        raise HTTPException(status_code=404, detail="WhatsApp record not found")
    
    db.delete(whatsapp)
    db.commit()
    return {"detail": "WhatsApp record deleted"}
