from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from backend.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True) # NEW: Name field
    phone_number = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)

class TriageRecord(Base):
    __tablename__ = "triage_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    inquiry = Column(Text, nullable=False)
    urgency = Column(String, nullable=False)
    intent = Column(String, nullable=False)
    property_id = Column(String, nullable=True)
    appointment_date = Column(String, nullable=True)
    draft_response = Column(Text, nullable=False)
    status = Column(String, default="Unsolved")
    created_at = Column(DateTime(timezone=True), server_default=func.now())