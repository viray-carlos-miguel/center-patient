from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

router = APIRouter(prefix="/api/ai", tags=["AI"])

class AIRequest(BaseModel):
    symptoms: str
    medical_history: str = ""
    age: int = 30
    gender: str = "not specified"

class AIResponse(BaseModel):
    assessment: str
    recommendations: str
    confidence: float
    educational_note: str

@router.post("/assess", response_model=AIResponse)
async def ai_assess(request: AIRequest):
    """Simulated AI assessment for educational purposes"""
    
    # Mock AI responses based on symptoms
    symptoms_lower = request.symptoms.lower()
    
    if any(word in symptoms_lower for word in ["fever", "headache", "fatigue"]):
        return AIResponse(
            assessment="Possible viral infection or flu-like illness",
            recommendations="Rest, hydration, monitor temperature. Seek medical attention if fever persists beyond 3 days.",
            confidence=0.75,
            educational_note="This is a simulated AI assessment for educational purposes only."
        )
    elif any(word in symptoms_lower for word in ["cough", "sore throat", "congestion"]):
        return AIResponse(
            assessment="Upper respiratory infection likely",
            recommendations="Rest, warm fluids, over-the-counter cough medicine if appropriate.",
            confidence=0.80,
            educational_note="Simulated response - not medical advice."
        )
    elif any(word in symptoms_lower for word in ["rash", "itching", "swelling"]):
        return AIResponse(
            assessment="Possible allergic reaction or skin condition",
            recommendations="Avoid potential allergens, monitor for breathing difficulties.",
            confidence=0.65,
            educational_note="Educational simulation - urgent cases should seek real medical care."
        )
    else:
        return AIResponse(
            assessment="General symptoms requiring medical evaluation",
            recommendations="Consult with a healthcare provider for proper diagnosis.",
            confidence=0.60,
            educational_note="This system is for educational demonstration only."
        )

@router.get("/health")
async def ai_health():
    return {"status": "AI module active", "mode": "simulation"}
