from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON # type: ignore
from sqlalchemy.ext.declarative import declarative_base # type: ignore
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    full_name = Column(String(255))
    role = Column(String(50))  # 'patient' or 'doctor'
    hashed_password = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Case(Base):
    __tablename__ = "cases"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, index=True)
    doctor_id = Column(Integer, index=True, nullable=True)
    symptoms = Column(JSON)  # Store symptom data
    ai_assessment = Column(JSON)  # Store AI analysis
    doctor_diagnosis = Column(Text, nullable=True)
    doctor_notes = Column(Text, nullable=True)
    prescription = Column(JSON, nullable=True)  # Store prescription data
    status = Column(String(50), default="pending_review")  # pending_review, in_review, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)
    is_educational = Column(Boolean, default=True)

    # Copy the entire AI models here or import them
from .ai_models import AIAnalysis, DiseasePattern, SymptomLearning