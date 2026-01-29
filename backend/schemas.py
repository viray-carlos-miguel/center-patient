from pydantic import BaseModel, Field
from typing import Any, Optional, List, Dict
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    PATIENT = "patient"
    DOCTOR = "doctor"

class SymptomBase(BaseModel):
    description: str = Field(..., description="Description of symptoms")
    duration_hours: int = Field(..., ge=1, le=720, description="Duration in hours (1-720)")
    severity: int = Field(..., ge=1, le=10, description="Severity 1-10")
    temperature: Optional[float] = Field(None, ge=35, le=42, description="Body temperature in Celsius")
    has_fever: bool = Field(default=False)
    has_cough: bool = Field(default=False)
    has_headache: bool = Field(default=False)
    has_nausea: bool = Field(default=False)
    has_fatigue: bool = Field(default=False)
    additional_notes: Optional[str] = None

class SymptomSubmission(SymptomBase):
    patient_id: Optional[int] = None

class AIAssessment(BaseModel):
    possible_conditions: List[str]
    confidence_score: float = Field(..., ge=0, le=1) 
    recommended_tests: List[str]
    urgency_level: str = Field(..., regex="^(low|medium|high)$")
    educational_note: str = "This AI assessment is for educational purposes only and is not a real diagnosis."

class CaseReview(BaseModel):
    doctor_diagnosis: str = Field(..., min_length=3)
    doctor_notes: Optional[str] = None
    prescription: Optional[Dict] = None
    follow_up_required: bool = False
    follow_up_days: Optional[int] = Field(None, ge=1, le=365)

class PrescriptionDraft(BaseModel):
    medication_name: str
    dosage: str
    frequency: str
    duration_days: int = Field(..., ge=1, le=90)
    instructions: Optional[str] = None
    warning: str = "This is a simulated prescription for educational purposes only. Do not use for actual medical treatment."

class CaseStatus(str, Enum):
    PENDING = "pending_review"
    IN_REVIEW = "in_review"
    COMPLETED = "completed"

# AI Schemas
class SymptomAnalysisRequest(BaseModel):
    # Symptoms
    fever: Optional[float] = Field(None, ge=35, le=45, description="Temperature in Celsius")
    cough: bool = False
    headache: bool = False
    fatigue: bool = False
    nausea: bool = False
    vomiting: bool = False
    diarrhea: bool = False
    shortness_of_breath: bool = False
    chest_pain: bool = False
    sore_throat: bool = False
    runny_nose: bool = False
    body_aches: bool = False
    chills: bool = False
    dizziness: bool = False
    abdominal_pain: bool = False
    loss_of_taste: bool = False
    loss_of_smell: bool = False
    
    # Additional info
    symptom_description: Optional[str] = Field(None, description="Free text description of symptoms")
    duration_days: int = Field(1, ge=1, le=365, description="How many days symptoms have lasted")
    
    # Patient info for better predictions
    age: int = Field(..., ge=0, le=120)
    gender: Optional[str] = Field(None, pattern="^(male|female|other)$")
    has_chronic_conditions: bool = False
    is_smoker: bool = False
    is_pregnant: bool = False
    is_immunocompromised: bool = False

class AIFeedback(BaseModel):
    accurate: bool = Field(..., description="Was the AI accurate?")
    actual_diagnosis: Optional[str] = Field(None, description="Actual diagnosis if different")
    notes: Optional[str] = Field(None, description="Additional notes")

class DiseasePrediction(BaseModel):
    disease: str
    confidence: float = Field(..., ge=0, le=100)
    matching_symptoms: List[str]
    missing_symptoms: List[str]
    urgency: str

class RiskAssessment(BaseModel):
    risk_score: int
    urgency_level: str
    recommended_action: str
    max_wait_time: str
    warning_signs: List[str]
    patient_risk_factors: List[str]

class Recommendations(BaseModel):
    immediate_actions: List[str]
    medical_tests: List[str]
    home_care: List[str]
    medications: List[str]
    follow_up: List[str]

class AIAnalysisResponse(BaseModel):
    analysis_id: str
    case_id: int
    patient_info: Dict[str, Any]
    symptoms_analyzed: Dict[str, Any]
    disease_predictions: List[DiseasePrediction]
    risk_assessment: RiskAssessment
    recommendations: Recommendations
    confidence_score: float = Field(..., ge=0, le=1)
    analysis_timestamp: str
    ai_version: str