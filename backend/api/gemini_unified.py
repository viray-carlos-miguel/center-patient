"""
Comprehensive Gemini AI Analysis Endpoint
Replaces ML system with unified AI-powered analysis
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import asyncio
from services.gemini_ai import gemini_ai

router = APIRouter(prefix="/api/gemini", tags=["gemini-unified"])

class ComprehensiveAnalysisRequest(BaseModel):
    symptoms: Dict[str, Any]
    patient_profile: Dict[str, Any]

class DiseasePrediction(BaseModel):
    disease: str
    confidence: float
    possible_conditions: List[str]
    urgency_level: str
    emergency_level: str

class EmergencyAssessment(BaseModel):
    level: str
    label: str
    color: str
    go_to_hospital: bool
    message: str
    hospital_message: str

class MedicineDetails(BaseModel):
    name: str
    dosage: str
    frequency: str
    duration: str
    purpose: str
    alternatives: List[str]
    precautions: List[str]
    effectiveness_score: float
    side_effects: List[str]

class TreatmentPlan(BaseModel):
    primary_treatment: str
    alternative_treatments: List[str]
    treatment_duration: str
    success_probability: float
    lifestyle_recommendations: List[str]
    follow_up_care: List[str]
    emergency_indicators: List[str]

class SideEffectAnalysis(BaseModel):
    common_side_effects: List[str]
    rare_side_effects: List[str]
    severe_reactions: List[str]
    drug_interactions: List[str]
    contraindications: List[str]
    monitoring_parameters: List[str]
    risk_level: str

class ComprehensiveAnalysisResponse(BaseModel):
    success: bool
    analysis: Dict[str, Any]
    disclaimer: str

@router.post("/comprehensive-analysis")
async def comprehensive_analysis(request: ComprehensiveAnalysisRequest):
    """Unified Gemini AI analysis for all medical aspects"""
    try:
        # Step 1: Get disease prediction from Gemini
        disease_prediction = await gemini_ai.predict_disease(
            symptoms=request.symptoms,
            patient_profile=request.patient_profile
        )
        
        # Step 2: Get emergency assessment from Gemini
        emergency_assessment = await gemini_ai.assess_emergency(
            symptoms=request.symptoms,
            disease=disease_prediction.disease,
            patient_profile=request.patient_profile
        )
        
        # Step 3: Get medicine recommendations from Gemini
        medicine_recommendations = await gemini_ai.generate_medicine_recommendations(
            symptoms=request.symptoms,
            patient_profile=request.patient_profile,
            primary_diagnosis=disease_prediction.disease
        )
        
        # Step 4: Get treatment analysis from Gemini
        treatment_analysis = await gemini_ai.analyze_treatment(
            diagnosis=disease_prediction.disease,
            symptoms=request.symptoms,
            patient_profile=request.patient_profile
        )
        
        # Step 5: Get side effect predictions for recommended medicines
        medications = [med.name for med in medicine_recommendations]
        side_effects = await gemini_ai.predict_side_effects(
            medications=medications,
            patient_profile=request.patient_profile
        )
        
        # Combine all results
        comprehensive_result = {
            # Disease Prediction (Gemini AI)
            disease_prediction: {
                disease: disease_prediction.disease,
                confidence: disease_prediction.confidence,
                possible_conditions: disease_prediction.possible_conditions,
                urgency_level: disease_prediction.urgency_level,
                model_confidence: disease_prediction.confidence,
                analysis_method: "gemini_ai"
            },
            
            # Emergency Assessment (Gemini AI)
            emergency: {
                level: emergency_assessment.level,
                label: emergency_assessment.label,
                color: emergency_assessment.color,
                go_to_hospital: emergency_assessment.go_to_hospital,
                message: emergency_assessment.message,
                hospital_message: emergency_assessment.hospital_message
            },
            
            # Medicine Details (Gemini AI)
            medications: [
                {
                    name: med.name,
                    dosage: med.dosage,
                    frequency: med.frequency,
                    duration: med.duration,
                    purpose: med.purpose,
                    alternatives: med.alternatives,
                    precautions: med.precautions,
                    effectiveness_score: med.effectiveness_score,
                    side_effects: med.side_effects
                } for med in medicine_recommendations
            ],
            
            # Treatment Planning (Gemini AI)
            treatment: {
                primary_treatment: treatment_analysis.primary_treatment,
                alternative_treatments: treatment_analysis.alternative_treatments,
                treatment_duration: treatment_analysis.treatment_duration,
                success_probability: treatment_analysis.success_probability,
                lifestyle_recommendations: treatment_analysis.lifestyle_recommendations,
                follow_up_care: treatment_analysis.follow_up_care,
                emergency_indicators: treatment_analysis.emergency_indicators,
                home_care: treatment_analysis.primary_treatment,
                hospital_advice: "Seek immediate care if emergency indicators present",
                when_to_seek_emergency: ", ".join(treatment_analysis.emergency_indicators)
            },
            
            # Side Effects (Gemini AI)
            side_effects: {
                common_side_effects: side_effects.common_side_effects,
                rare_side_effects: side_effects.rare_side_effects,
                severe_reactions: side_effects.severe_reactions,
                drug_interactions: side_effects.drug_interactions,
                contraindications: side_effects.contraindications,
                monitoring_parameters: side_effects.monitoring_parameters,
                risk_level: side_effects.risk_level
            },
            
            # Overall Risk Assessment (Gemini AI)
            risk_assessment: {
                overall_risk: emergency_assessment.level,
                urgency_level: disease_prediction.urgency_level,
                confidence_level: "High" if disease_prediction.confidence > 0.8 else "Medium" if disease_prediction.confidence > 0.6 else "Low"
            },
            
            # Recommendations (Gemini AI)
            recommendations: treatment_analysis.follow_up_care + treatment_analysis.emergency_indicators,
            
            # Model Information
            model_info: {
                model: "gemini-2.5-flash",
                analysis_type: "comprehensive_ai",
                confidence: disease_prediction.confidence,
                educational_disclaimer: "AI-generated analysis for educational purposes only"
            }
        }
        
        return {
            "success": True,
            "analysis": comprehensive_result,
            "disclaimer": "This comprehensive analysis is generated by Google Gemini 2.5 Flash AI for educational purposes only. Always consult qualified healthcare professionals for medical decisions."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comprehensive analysis failed: {str(e)}")

@router.get("/health")
async def gemini_health():
    """Check Gemini AI service health"""
    try:
        response = await gemini_ai.model.generate_content_async('Respond with "OK" to test connection')
        return {
            "status": "healthy",
            "gemini_connected": "OK" in response.text,
            "model": "gemini-2.5-flash",
            "analysis_type": "comprehensive_ai"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "model": "gemini-2.5-flash"
        }
