"""
ML API Router – FastAPI endpoints for the medical prediction engine.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime

from ml.prediction_engine import MedicalPredictionEngine

# Initialise engine (loads saved model if available)
engine = MedicalPredictionEngine()

router = APIRouter(prefix="/api/ml", tags=["machine-learning"])


# ── Request / Response models ────────────────────────────────────────

class SymptomInput(BaseModel):
    description: str = ""
    severity: Optional[int] = 5
    duration_hours: Optional[int] = 48
    temperature: Optional[float] = 37.0
    age: Optional[int] = 30
    gender: Optional[int] = 0  # 0=female, 1=male
    # Individual symptom flags (all optional)
    fever: Optional[bool] = False
    high_fever: Optional[bool] = False
    cough: Optional[bool] = False
    dry_cough: Optional[bool] = False
    sore_throat: Optional[bool] = False
    runny_nose: Optional[bool] = False
    nasal_congestion: Optional[bool] = False
    sneezing: Optional[bool] = False
    headache: Optional[bool] = False
    body_aches: Optional[bool] = False
    muscle_pain: Optional[bool] = False
    joint_pain: Optional[bool] = False
    fatigue: Optional[bool] = False
    shortness_of_breath: Optional[bool] = False
    wheezing: Optional[bool] = False
    chest_pain: Optional[bool] = False
    nausea: Optional[bool] = False
    vomiting: Optional[bool] = False
    diarrhea: Optional[bool] = False
    abdominal_pain: Optional[bool] = False
    dizziness: Optional[bool] = False
    skin_rash: Optional[bool] = False
    itching: Optional[bool] = False
    chills: Optional[bool] = False
    loss_of_appetite: Optional[bool] = False
    loss_of_taste: Optional[bool] = False
    loss_of_smell: Optional[bool] = False
    anxiety: Optional[bool] = False
    depression: Optional[bool] = False
    insomnia: Optional[bool] = False
    swelling: Optional[bool] = False
    night_sweats: Optional[bool] = False
    blurred_vision: Optional[bool] = False
    palpitations: Optional[bool] = False
    rapid_heartbeat: Optional[bool] = False
    numbness: Optional[bool] = False
    tingling: Optional[bool] = False
    confusion: Optional[bool] = False
    stiff_neck: Optional[bool] = False
    swollen_lymph_nodes: Optional[bool] = False
    weight_loss: Optional[bool] = False
    frequent_urination: Optional[bool] = False


class PredictionRequest(BaseModel):
    symptoms: SymptomInput
    patient_info: Optional[Dict[str, Any]] = None


# ── Endpoints ────────────────────────────────────────────────────────

@router.post("/predict")
async def predict_disease(request: PredictionRequest):
    """Predict disease from symptoms using the trained ML ensemble model."""
    if not engine.is_trained:
        raise HTTPException(status_code=503, detail="ML model not trained yet. POST /api/ml/train first.")

    # Merge symptom input into a flat dict the engine expects
    symptoms_dict = request.symptoms.model_dump()
    if request.patient_info:
        symptoms_dict.update(request.patient_info)

    try:
        result = engine.predict(symptoms_dict)
        return {
            "success": True,
            "prediction": result,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.post("/train")
async def train_model(n_samples: int = 6000):
    """Train (or retrain) the ML model."""
    try:
        result = engine.train(n_samples=n_samples)
        return {
            "success": True,
            "training_result": result,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")


@router.get("/health")
async def ml_health():
    """Check ML system health."""
    return {
        "status": "healthy" if engine.is_trained else "not_trained",
        "model_trained": engine.is_trained,
        "model_accuracy": round(engine.accuracy * 100, 2) if engine.is_trained else 0,
        "n_diseases": len(engine.diseases),
        "diseases": engine.diseases,
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/info")
async def ml_info():
    """Get ML system information."""
    return {
        "system_name": "Medical ML Prediction Engine",
        "version": "3.0",
        "architecture": "Ensemble (Random Forest + Gradient Boosting + Logistic Regression)",
        "calibration": "Isotonic regression",
        "training_data": "6000 synthetic cases based on WHO/CDC/Mayo Clinic symptom profiles",
        "n_diseases": len(engine.diseases),
        "n_features": len(engine.feature_names) if engine.feature_names else 70,
        "accuracy": round(engine.accuracy * 100, 2) if engine.is_trained else 0,
        "diseases": engine.diseases,
        "status": "operational" if engine.is_trained else "needs_training",
    }
