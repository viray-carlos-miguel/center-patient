"""
AI Database Models
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, Float # type: ignore
from datetime import datetime
from .database import Base

class AIAnalysis(Base):
    """Stores AI analysis results"""
    __tablename__ = "ai_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, index=True)
    patient_id = Column(Integer, index=True)
    
    # Input data
    input_symptoms = Column(JSON)
    patient_info = Column(JSON)
    
    # AI Output
    disease_predictions = Column(JSON)
    risk_assessment = Column(JSON)
    recommendations = Column(JSON)
    confidence_score = Column(Float)
    
    # Metadata
    ai_model_version = Column(String(50))
    analysis_timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Doctor feedback
    doctor_accurate = Column(Boolean, nullable=True)
    doctor_diagnosis = Column(String(255), nullable=True)
    doctor_notes = Column(Text, nullable=True)
    feedback_timestamp = Column(DateTime, nullable=True)

class DiseasePattern(Base):
    """Stores learned disease patterns from cases"""
    __tablename__ = "disease_patterns"
    
    id = Column(Integer, primary_key=True, index=True)
    disease_name = Column(String(255), index=True)
    
    # Symptoms
    core_symptoms = Column(JSON)
    common_symptoms = Column(JSON)
    warning_symptoms = Column(JSON)
    
    # Statistics
    total_cases = Column(Integer, default=0)
    confirmed_cases = Column(Integer, default=0)
    accuracy_rate = Column(Float, default=0.0)
    
    # Metadata
    urgency_level = Column(String(50))
    last_updated = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class SymptomLearning(Base):
    """Stores symptom correlations learned from data"""
    __tablename__ = "symptom_learnings"
    
    id = Column(Integer, primary_key=True, index=True)
    symptom_a = Column(String(100), index=True)
    symptom_b = Column(String(100), index=True)
    correlation_score = Column(Float)
    co_occurrence_count = Column(Integer, default=0)
    last_observed = Column(DateTime, default=datetime.utcnow)