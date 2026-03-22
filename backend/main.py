from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import case
from typing import Literal

from backend.triage_service import execute_triage
from backend.database import engine, Base, get_db
from backend.models_db import User, TriageRecord
from backend.auth import (
    get_password_hash, verify_password, create_access_token, 
    get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
)
from datetime import timedelta

app = FastAPI(title="Real Estate AI Triage API", version="1.3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Schemas ---
class UserCreate(BaseModel):
    name: str # NEW: Required for registration
    phone_number: str
    password: str
    is_admin: bool = False

class TriageRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Customer inquiry text")

class StatusUpdate(BaseModel):
    status: Literal["Unsolved", "Action Taken", "Solved"]

# --- Endpoints ---

@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    # NEW: Strict 10-digit validation with admin bypass
    if "admin" not in user.phone_number.lower():
        if not user.phone_number.isdigit() or len(user.phone_number) != 10:
            raise HTTPException(status_code=400, detail="Phone number must be exactly 10 digits")

    db_user = db.query(User).filter(User.phone_number == user.phone_number).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Phone number already registered")
    
    hashed_pwd = get_password_hash(user.password)
    # NEW: Save the user's name
    new_user = User(name=user.name, phone_number=user.phone_number, hashed_password=hashed_pwd, is_admin=user.is_admin)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully"}

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone_number == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect phone number or password")
    
    access_token = create_access_token(
        data={"sub": user.phone_number, "is_admin": user.is_admin},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer", "is_admin": user.is_admin}


@app.post("/triage")
def triage(payload: TriageRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    try:
        result = execute_triage(payload.message)
        
        new_record = TriageRecord(
            user_id=current_user.id,
            inquiry=payload.message,
            urgency=result.get("urgency", "Low"),
            intent=result.get("intent", "General Inquiry"),
            property_id=result.get("property_id"),
            appointment_date=result.get("appointment_date"),
            draft_response=result.get("draft_response", ""),
            status="Unsolved"
        )
        db.add(new_record)
        db.commit()

        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

@app.get("/admin/records")
def get_admin_records(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    urgency_order = case(
        (TriageRecord.urgency == 'High', 1),
        (TriageRecord.urgency == 'Medium', 2),
        (TriageRecord.urgency == 'Low', 3),
        else_=4
    )
    
    # 1. Add User.name to the query selection
    results = db.query(TriageRecord, User.phone_number, User.name)\
        .join(User, TriageRecord.user_id == User.id)\
        .order_by(urgency_order, TriageRecord.created_at.desc())\
        .limit(15).all()
        
    formatted_records = []
    # 2. Unpack the name from the query results
    for record, phone, name in results:
        formatted_records.append({
            "id": record.id,
            "name": name, 
            "phone_number": phone,
            "urgency": record.urgency,
            "intent": record.intent,
            "inquiry": record.inquiry,
            "property_id": record.property_id,
            "status": record.status 
        })
        
    return formatted_records

@app.patch("/admin/records/{record_id}/status")
def update_record_status(record_id: int, payload: StatusUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    record = db.query(TriageRecord).filter(TriageRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    record.status = payload.status
    db.commit()
    return {"message": "Status updated successfully", "status": record.status}

# Add this endpoint in backend/main.py

@app.get("/user/records")
def get_user_records(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Fetch records belonging ONLY to the logged-in user
    records = db.query(TriageRecord)\
        .filter(TriageRecord.user_id == current_user.id)\
        .order_by(TriageRecord.created_at.desc())\
        .all()
        
    formatted_records = []
    for r in records:
        formatted_records.append({
            "id": r.id,
            "urgency": r.urgency,
            "intent": r.intent,
            "inquiry": r.inquiry,
            "property_id": r.property_id,
            "status": r.status,
            "created_at": r.created_at.strftime("%Y-%m-%d %H:%M") if r.created_at else "N/A"
        })
        
    return formatted_records