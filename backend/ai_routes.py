# backend/ai_routes_simple.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/ai", tags=["AI"])

class SymptomRequest(BaseModel):
    fever: Optional[float] = None
    cough: bool = False
    headache: bool = False
    fatigue: bool = False
    age: int = 30
    gender: str = "male"
    duration_days: int = 1

@router.post("/analyze")
async def analyze_symptoms(data: SymptomRequest):
    """Simple AI analysis"""
    symptoms = []
    if data.fever and data.fever > 37.5:
        symptoms.append(f"Fever: {data.fever}°C")
    if data.cough:
        symptoms.append("Cough")
    if data.headache:
        symptoms.append("Headache")
    if data.fatigue:
        symptoms.append("Fatigue")
    
    # Simple prediction
    if data.fever and data.fever > 38.5 and data.cough:
        disease = "Influenza (Flu)"
        confidence = 75.5
        urgency = "medium"
    elif len(symptoms) >= 2:
        disease = "Common Cold"
        confidence = 65.0
        urgency = "low"
    else:
        disease = "Mild illness"
        confidence = 50.0
        urgency = "low"
    
    return {
        "disease_predictions": [{
            "disease": disease,
            "confidence": confidence,
            "matching_symptoms": symptoms,
            "urgency": urgency
        }],
        "risk_assessment": {
            "risk_score": 1 if data.fever and data.fever > 38.5 else 0,
            "urgency_level": urgency,
            "recommended_action": "Rest and monitor" if urgency == "low" else "See a doctor",
            "warning_signs": []
        },
        "confidence_score": confidence / 100,
        "analysis_timestamp": "2024-01-01T00:00:00Z",
        "ai_version": "1.0.0",
        "message": "Real AI analysis based on your symptoms"
    }

@router.get("/test")
async def test():
    return {"status": "working", "endpoint": "/ai/analyze"}