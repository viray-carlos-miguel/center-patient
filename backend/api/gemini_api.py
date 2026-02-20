"""
Gemini AI API Endpoints for Advanced Medical Features
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio
from services.gemini_ai import gemini_ai, MedicineRecommendation, TreatmentAnalysis, DoctorVerification, SideEffectPrediction

router = APIRouter(prefix="/api/gemini", tags=["gemini-ai"])

class MedicineRequest(BaseModel):
    symptoms: Dict[str, Any]
    patient_profile: Dict[str, Any]
    primary_diagnosis: str

class TreatmentRequest(BaseModel):
    diagnosis: str
    symptoms: Dict[str, Any]
    patient_profile: Dict[str, Any]

class VerificationRequest(BaseModel):
    patient_case: Dict[str, Any]
    ai_diagnosis: str
    doctor_diagnosis: Optional[str] = None

class SideEffectRequest(BaseModel):
    medications: List[str]
    patient_profile: Dict[str, Any]

class SymptomAnalysisRequest(BaseModel):
    symptoms: Dict[str, Any]

class ComprehensiveAnalysisRequest(BaseModel):
    symptoms: Dict[str, Any]
    patient_profile: Dict[str, Any]

@router.post("/medicine-recommendations")
async def get_medicine_recommendations(request: MedicineRequest):
    """Get AI-powered medicine recommendations"""
    try:
        recommendations = await gemini_ai.generate_medicine_recommendations(
            symptoms=request.symptoms,
            patient_profile=request.patient_profile,
            primary_diagnosis=request.primary_diagnosis
        )
        
        return {
            "success": True,
            "recommendations": [
                {
                    "name": rec.name,
                    "dosage": rec.dosage,
                    "frequency": rec.frequency,
                    "duration": rec.duration,
                    "purpose": rec.purpose,
                    "alternatives": rec.alternatives,
                    "precautions": rec.precautions,
                    "effectiveness_score": rec.effectiveness_score,
                    "side_effects": rec.side_effects
                } for rec in recommendations
            ],
            "disclaimer": "AI-generated recommendations for educational purposes only. Always consult qualified healthcare professionals."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")

@router.post("/treatment-analysis")
async def analyze_treatment(request: TreatmentRequest):
    """Get comprehensive treatment analysis"""
    try:
        analysis = await gemini_ai.analyze_treatment_approach(
            diagnosis=request.diagnosis,
            symptoms=request.symptoms,
            patient_profile=request.patient_profile
        )
        
        return {
            "success": True,
            "analysis": {
                "primary_treatment": analysis.primary_treatment,
                "alternative_treatments": analysis.alternative_treatments,
                "treatment_duration": analysis.treatment_duration,
                "success_probability": analysis.success_probability,
                "lifestyle_recommendations": analysis.lifestyle_recommendations,
                "follow_up_care": analysis.follow_up_care,
                "emergency_indicators": analysis.emergency_indicators
            },
            "disclaimer": "AI-generated analysis for educational purposes only. Professional medical judgment required."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing treatment: {str(e)}")

@router.post("/doctor-verification")
async def verify_doctor_assessment(request: VerificationRequest):
    """Get AI assistance for doctor verification"""
    try:
        verification = await gemini_ai.verify_medical_assessment(
            patient_case=request.patient_case,
            ai_diagnosis=request.ai_diagnosis,
            doctor_diagnosis=request.doctor_diagnosis
        )
        
        return {
            "success": True,
            "verification": {
                "verification_score": verification.verification_score,
                "confidence_level": verification.confidence_level,
                "recommended_actions": verification.recommended_actions,
                "additional_tests": verification.additional_tests,
                "specialist_referral": verification.specialist_referral,
                "red_flags": verification.red_flags
            },
            "disclaimer": "AI verification assistance for educational purposes. Not a substitute for professional medical judgment."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in verification: {str(e)}")

@router.post("/side-effect-prediction")
async def predict_side_effects(request: SideEffectRequest):
    """Predict potential side effects and interactions"""
    try:
        prediction = await gemini_ai.predict_side_effects(
            medications=request.medications,
            patient_profile=request.patient_profile
        )
        
        return {
            "success": True,
            "prediction": {
                "common_side_effects": prediction.common_side_effects,
                "rare_side_effects": prediction.rare_side_effects,
                "severe_reactions": prediction.severe_reactions,
                "drug_interactions": prediction.drug_interactions,
                "contraindications": prediction.contraindications,
                "monitoring_parameters": prediction.monitoring_parameters,
                "risk_level": prediction.risk_level
            },
            "disclaimer": "AI-predicted side effects for educational purposes. Actual effects may vary. Consult healthcare professionals."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error predicting side effects: {str(e)}")

@router.post("/analyze-symptoms")
async def analyze_symptoms(request: SymptomAnalysisRequest):
    """Get accurate disease analysis using Gemini AI"""
    try:
        analysis = await gemini_ai.analyze_symptoms_for_disease(
            symptoms=request.symptoms
        )
        
        return {
            "success": True,
            "analysis": analysis,
            "message": "Symptom analysis completed successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze symptoms: {str(e)}"
        )

@router.post("/comprehensive-analysis")
async def get_comprehensive_analysis(request: ComprehensiveAnalysisRequest):
    """Get comprehensive medical analysis including all Gemini AI insights"""
    try:
        # Get primary symptom analysis
        symptom_analysis = await gemini_ai.analyze_symptoms_for_disease(
            symptoms=request.symptoms
        )
        
        # Get medicine recommendations
        primary_diagnosis = symptom_analysis.get('primary_prediction', {}).get('condition', 'Unknown')
        medicine_recommendations = await gemini_ai.generate_medicine_recommendations(
            symptoms=request.symptoms,
            patient_profile=request.patient_profile,
            primary_diagnosis=primary_diagnosis
        )
        
        # Get treatment analysis
        treatment_analysis = await gemini_ai.analyze_treatment_approach(
            diagnosis=primary_diagnosis,
            symptoms=request.symptoms,
            patient_profile=request.patient_profile
        )
        
        return {
            "success": True,
            "comprehensive_analysis": {
                "symptom_analysis": symptom_analysis,
                "medicine_recommendations": [
                    {
                        "name": rec.name,
                        "dosage": rec.dosage,
                        "frequency": rec.frequency,
                        "duration": rec.duration,
                        "purpose": rec.purpose,
                        "effectiveness_score": rec.effectiveness_score,
                        "alternatives": rec.alternatives,
                        "precautions": rec.precautions,
                        "side_effects": rec.side_effects
                    } for rec in medicine_recommendations
                ],
                "treatment_analysis": {
                    "primary_treatment": treatment_analysis.primary_treatment,
                    "alternative_treatments": treatment_analysis.alternative_treatments,
                    "treatment_duration": treatment_analysis.treatment_duration,
                    "success_probability": treatment_analysis.success_probability,
                    "lifestyle_recommendations": treatment_analysis.lifestyle_recommendations,
                    "follow_up_care": treatment_analysis.follow_up_care,
                    "emergency_indicators": treatment_analysis.emergency_indicators
                }
            },
            "message": "Comprehensive analysis completed successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get comprehensive analysis: {str(e)}"
        )

@router.get("/health")
async def gemini_health():
    """Check Gemini AI service health"""
    try:
        # Test basic functionality
        test_response = await gemini_ai.model.generate_content_async("Respond with 'OK' to test connection")
        return {
            "status": "healthy",
            "gemini_connected": "OK" in test_response.text,
            "model": "gemini-2.5-flash"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "model": "gemini-2.5-flash"
        }
