"""
ML System API Integration
Integrates ML prediction engine with FastAPI backend - Advanced Version
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import asyncio
from datetime import datetime

from .prediction_engine import MedicalPredictionEngine
from .training_data import MedicalTrainingDataGenerator
from .advanced_training import AdvancedMLTrainingSystem
from .imaging_analyzer import MedicalImagingAnalyzer
from .continuous_learner import ContinuousLearningSystem

# Create router
ml_router = APIRouter(prefix="/api/ml", tags=["machine-learning"])

# Initialize ML components
prediction_engine = MedicalPredictionEngine()
data_generator = MedicalTrainingDataGenerator()
advanced_system = AdvancedMLTrainingSystem()
imaging_analyzer = MedicalImagingAnalyzer()
continuous_learner = ContinuousLearningSystem()

# Pydantic models
class SymptomInput(BaseModel):
    description: str
    duration_hours: Optional[int] = None
    severity: Optional[int] = 1
    temperature: Optional[float] = None
    has_fever: Optional[bool] = False
    has_cough: Optional[bool] = False
    has_headache: Optional[bool] = False
    has_nausea: Optional[bool] = False
    has_fatigue: Optional[bool] = False
    has_chest_pain: Optional[bool] = False
    has_shortness_of_breath: Optional[bool] = False
    has_abdominal_pain: Optional[bool] = False
    additional_notes: Optional[str] = None

class PatientInfo(BaseModel):
    age: Optional[int] = 30
    gender: Optional[str] = 'unknown'
    has_chronic_conditions: Optional[bool] = False

class PredictionRequest(BaseModel):
    symptoms: SymptomInput
    patient_info: Optional[PatientInfo] = None
    include_imaging: Optional[bool] = False
    imaging_data: Optional[Dict[str, Any]] = None

class TrainingRequest(BaseModel):
    num_cases: Optional[int] = 1000
    use_real_data: Optional[bool] = True
    augmentation_factor: Optional[int] = 2
    include_imaging: Optional[bool] = False

class FeedbackData(BaseModel):
    case_id: str
    prediction: Dict[str, Any]
    actual_diagnosis: Optional[str] = None
    confidence: Optional[float] = None
    feedback_type: str
    feedback_source: str
    feedback_data: Dict[str, Any]

class ImagingAnalysisRequest(BaseModel):
    image_path: str
    modality: str
    symptoms: Optional[Dict[str, Any]] = None

@ml_router.post("/predict", response_model=Dict[str, Any])
async def predict_disease(request: PredictionRequest):
    """
    Predict disease using ML ensemble model with advanced features
    """
    try:
        # Convert Pydantic models to dictionaries
        symptoms_dict = request.symptoms.dict()
        patient_dict = request.patient_info.dict() if request.patient_info else None
        
        # Make prediction
        result = await prediction_engine.predict_disease(symptoms_dict, patient_dict)
        
        # Add imaging analysis if requested
        if request.include_imaging and request.imaging_data:
            imaging_result = await imaging_analyzer.analyze_medical_image(
                request.imaging_data.get('image_path'),
                request.imaging_data.get('modality', 'X-ray')
            )
            result['imaging_analysis'] = imaging_result
        
        return {
            "success": True,
            "prediction": result,
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "model_version": "2.0",
                "prediction_method": "ensemble_ml",
                "requires_medical_review": result.get("metadata", {}).get("requires_medical_review", True),
                "advanced_features": {
                    "imaging_analysis": request.include_imaging,
                    "continuous_learning": continuous_learner.is_initialized
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )

@ml_router.post("/predict/advanced", response_model=Dict[str, Any])
async def predict_disease_advanced(request: PredictionRequest):
    """
    Advanced disease prediction with all features enabled
    """
    try:
        # Convert to dictionaries
        symptoms_dict = request.symptoms.dict()
        patient_dict = request.patient_info.dict() if request.patient_info else None
        
        # Enhanced prediction with all features
        result = await prediction_engine.predict_disease(symptoms_dict, patient_dict)
        
        # Add differential diagnoses
        differential = prediction_engine.knowledge_base.get_differential_diagnosis(
            symptoms_dict.get('symptoms', []),
            result.get('ml_prediction', {}).get('primary_condition', 'Unknown')
        )
        result['differential_diagnoses'] = differential
        
        # Add risk stratification
        risk_assessment = result.get('risk_assessment', {})
        risk_assessment['detailed_analysis'] = {
            'age_risk': 'high' if patient_dict and patient_dict.get('age', 30) >= 65 else 'low',
            'symptom_complexity': prediction_engine.data_processor.calculate_symptom_complexity_score(
                symptoms_dict.get('symptoms', [])
            ),
            'temporal_risk': 'high' if symptoms_dict.get('duration_hours', 0) > 168 else 'low'
        }
        
        # Add treatment pathways
        primary_condition = result.get('ml_prediction', {}).get('primary_condition')
        if primary_condition:
            condition_info = prediction_engine.knowledge_base.get_condition_info(primary_condition)
            result['treatment_pathways'] = {
                'first_line': condition_info.get('treatment_options', [])[:2],
                'second_line': condition_info.get('treatment_options', [])[2:4],
                'specialist_referral': condition_info.get('specialist_referral', 'Primary care')
            }
        
        return {
            "success": True,
            "prediction": result,
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "prediction_method": "advanced_ensemble_ml",
                "features_used": ["symptoms", "patient_info", "medical_knowledge", "risk_assessment"],
                "confidence_level": result.get('ml_prediction', {}).get('confidence', 0)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Advanced prediction failed: {str(e)}"
        )

@ml_router.post("/train/advanced", response_model=Dict[str, Any])
async def train_advanced_model(request: TrainingRequest):
    """
    Train the ML model with real data, expanded conditions, and continuous learning
    """
    try:
        # Run complete advanced setup
        results = await advanced_system.run_complete_advanced_setup()
        
        return {
            "success": True,
            "message": "Advanced ML training completed successfully",
            "training_results": results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Advanced training failed: {str(e)}"
        )

@ml_router.post("/imaging/analyze", response_model=Dict[str, Any])
async def analyze_medical_image(request: ImagingAnalysisRequest):
    """
    Analyze medical image for disease detection
    """
    try:
        if not imaging_analyzer.is_initialized:
            return {
                "success": False,
                "error": "Imaging analyzer not initialized"
            }
        
        # Analyze image
        result = await imaging_analyzer.analyze_medical_image(
            request.image_path,
            request.modality
        )
        
        # If symptoms provided, correlate with imaging findings
        if request.symptoms:
            correlation = await _correlate_symptoms_with_imaging(
                request.symptoms,
                result.get('findings', [])
            )
            result['symptom_correlation'] = correlation
        
        return {
            "success": True,
            "imaging_analysis": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Imaging analysis failed: {str(e)}"
        )

@ml_router.post("/imaging/upload", response_model=Dict[str, Any])
async def upload_and_analyze_image(
    image: UploadFile = File(...),
    modality: str = "X-ray",
    symptoms: Optional[str] = None
):
    """
    Upload and analyze medical image
    """
    try:
        # Save uploaded image
        image_path = f"backend/ml_system/temp_images/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{image.filename}"
        
        with open(image_path, "wb") as buffer:
            content = await image.read()
            buffer.write(content)
        
        # Parse symptoms if provided
        symptoms_dict = {}
        if symptoms:
            # Simple symptom parsing (in production, would use more sophisticated parsing)
            symptoms_dict = {'description': symptoms}
        
        # Analyze image
        result = await imaging_analyzer.analyze_medical_image(image_path, modality)
        
        return {
            "success": True,
            "image_path": image_path,
            "modality": modality,
            "analysis": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Image upload and analysis failed: {str(e)}"
        )

@ml_router.post("/feedback/submit", response_model=Dict[str, Any])
async def submit_feedback(feedback: FeedbackData):
    """
    Submit feedback for continuous learning
    """
    try:
        if not continuous_learner.is_initialized:
            return {
                "success": False,
                "error": "Continuous learning system not initialized"
            }
        
        # Collect feedback
        result = await continuous_learner.collect_feedback(feedback.dict())
        
        return {
            "success": True,
            "feedback_id": result.get('feedback_id'),
            "timestamp": result.get('timestamp'),
            "message": "Feedback submitted successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Feedback submission failed: {str(e)}"
        )

@ml_router.post("/feedback/process", response_model=Dict[str, Any])
async def process_feedback_queue():
    """
    Process feedback queue for learning
    """
    try:
        if not continuous_learner.is_initialized:
            return {
                "success": False,
                "error": "Continuous learning system not initialized"
            }
        
        # Process feedback queue
        result = await continuous_learner.process_feedback_queue()
        
        return {
            "success": True,
            "processed_count": result['processed_count'],
            "queue_size": result['queue_size'],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Feedback processing failed: {str(e)}"
        )

@ml_router.post("/learning/retrain", response_model=Dict[str, Any])
async def retrain_model():
    """
    Trigger model retraining with new data
    """
    try:
        if not continuous_learner.is_initialized:
            return {
                "success": False,
                "error": "Continuous learning system not initialized"
            }
        
        # Check if retraining should be triggered
        trigger_check = await continuous_learner.check_retraining_trigger()
        
        if not trigger_check['trigger_retraining']:
            return {
                "success": False,
                "message": "Retraining not triggered",
                "reason": trigger_check['reason'],
                "details": trigger_check
            }
        
        # Execute retraining
        retraining_result = await continuous_learner.retrain_model()
        
        return {
            "success": True,
            "retraining_result": retraining_result,
            "trigger_reason": trigger_check['reason'],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Model retraining failed: {str(e)}"
        )

@ml_router.get("/learning/status", response_model=Dict[str, Any])
async def get_learning_status():
    """
    Get continuous learning system status
    """
    try:
        if not continuous_learner.is_initialized:
            return {
                "success": False,
                "error": "Continuous learning system not initialized"
            }
        
        status = await continuous_learner.get_learning_status()
        
        return {
            "success": True,
            "learning_status": status,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Learning status check failed: {str(e)}"
        )

@ml_router.get("/imaging/capabilities", response_model=Dict[str, Any])
async def get_imaging_capabilities():
    """
    Get imaging analysis capabilities
    """
    try:
        capabilities = imaging_analyzer.get_imaging_summary()
        
        return {
            "success": True,
            "imaging_capabilities": capabilities,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Imaging capabilities check failed: {str(e)}"
        )

@ml_router.get("/conditions/expanded", response_model=Dict[str, Any])
async def get_expanded_conditions():
    """
    Get list of expanded medical conditions
    """
    try:
        conditions = advanced_system.expanded_conditions
        
        condition_details = {}
        for condition, info in conditions.items():
            condition_details[condition] = {
                "category": info.get("category", "unknown"),
                "severity": info.get("severity", "unknown"),
                "common_symptoms": info.get("common_symptoms", []),
                "imaging_findings": info.get("imaging_findings", []),
                "lab_tests": info.get("lab_tests", []),
                "treatment": info.get("treatment", [])
            }
        
        return {
            "success": True,
            "conditions": condition_details,
            "total_conditions": len(conditions),
            "categories": list(set(info.get("category", "unknown") for info in conditions.values())),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get expanded conditions: {str(e)}"
        )

@ml_router.get("/performance/dashboard", response_model=Dict[str, Any])
async def get_performance_dashboard():
    """
    Get comprehensive performance dashboard
    """
    try:
        # Get model info
        model_info = prediction_engine.get_model_info()
        
        # Get learning status
        learning_status = {}
        if continuous_learner.is_initialized:
            learning_status = await continuous_learner.get_learning_status()
        
        # Get imaging capabilities
        imaging_capabilities = imaging_analyzer.get_imaging_summary()
        
        # Get system health
        system_health = {
            "prediction_engine": "operational" if prediction_engine.is_initialized else "needs_training",
            "imaging_analyzer": "operational" if imaging_analyzer.is_initialized else "not_initialized",
            "continuous_learner": "operational" if continuous_learner.is_initialized else "not_initialized",
            "advanced_system": "operational"
        }
        
        return {
            "success": True,
            "dashboard": {
                "model_performance": model_info,
                "learning_status": learning_status,
                "imaging_capabilities": imaging_capabilities,
                "system_health": system_health,
                "total_conditions": len(advanced_system.expanded_conditions),
                "supported_modalities": imaging_analyzer.supported_modalities
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Performance dashboard failed: {str(e)}"
        )

async def _correlate_symptoms_with_imaging(symptoms: Dict[str, Any], imaging_findings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Correlate symptoms with imaging findings"""
    correlation_score = 0.0
    correlations = []
    
    symptom_list = symptoms.get('symptoms', [])
    
    for finding in imaging_findings:
        finding_type = finding.get('type', '')
        finding_conditions = finding.get('conditions', [])
        
        # Check if symptoms match imaging findings
        for condition in finding_conditions:
            # Simple correlation logic (in production, would be more sophisticated)
            if any(symptom in condition.lower() for symptom in symptom_list):
                correlation_score += 0.2
                correlations.append({
                    "symptom": symptom,
                    "finding": finding_type,
                    "condition": condition,
                    "correlation_strength": 0.8
                })
    
    return {
        "correlation_score": min(correlation_score, 1.0),
        "correlations": correlations,
        "interpretation": "Strong correlation" if correlation_score > 0.6 else "Weak correlation"
    }

# Existing endpoints remain the same...
@ml_router.post("/train", response_model=Dict[str, Any])
async def train_model(request: TrainingRequest):
    """
    Train the ML model with synthetic or existing data
    """
    try:
        # Generate or load training data
        if request.use_existing_data:
            # Try to load existing data first
            training_data = []
            # TODO: Load from database
            if len(training_data) < 50:
                # Generate synthetic data if insufficient
                training_data = data_generator.generate_training_cases(request.num_cases)
        else:
            # Generate new synthetic data
            training_data = data_generator.generate_training_cases(request.num_cases)
        
        # Train the model
        result = prediction_engine.train_from_database(training_data)
        
        return {
            "success": result["success"],
            "message": result["message"],
            "training_stats": data_generator.get_data_statistics(training_data),
            "performance": result.get("performance", {}),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Training failed: {str(e)}"
        )

@ml_router.get("/model/info", response_model=Dict[str, Any])
async def get_model_info():
    """
    Get information about the current ML model
    """
    try:
        info = prediction_engine.get_model_info()
        
        return {
            "success": True,
            "model_info": info,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get model info: {str(e)}"
        )

@ml_router.get("/health", response_model=Dict[str, Any])
async def ml_health_check():
    """
    Check ML system health
    """
    try:
        model_info = prediction_engine.get_model_info()
        
        health_status = {
            "ml_system": "operational" if prediction_engine.is_initialized else "needs_training",
            "model_status": model_info.get("status", "unknown"),
            "data_processor": "operational",
            "knowledge_base": "operational",
            "imaging_analyzer": "operational" if imaging_analyzer.is_initialized else "not_initialized",
            "continuous_learner": "operational" if continuous_learner.is_initialized else "not_initialized",
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "health": health_status,
            "recommendations": _get_health_recommendations(health_status)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Health check failed: {str(e)}"
        )

def _get_health_recommendations(health_status: Dict[str, Any]) -> List[str]:
    """Get health recommendations based on status"""
    recommendations = []
    
    if health_status["ml_system"] == "needs_training":
        recommendations.append("Train the ML model with at least 50 medical cases")
    
    if health_status["model_status"] == "not_trained":
        recommendations.append("Initialize and train the prediction model")
    
    if health_status["imaging_analyzer"] == "not_initialized":
        recommendations.append("Initialize medical imaging analyzer")
    
    if health_status["continuous_learner"] == "not_initialized":
        recommendations.append("Setup continuous learning system")
    
    if not recommendations:
        recommendations.append("ML system is healthy and ready for predictions")
    
    return recommendations

# Dependency to ensure ML system is ready
async def ensure_ml_ready():
    """Ensure ML system is ready for predictions"""
    if not prediction_engine.is_initialized:
        # Try to auto-train with synthetic data
        try:
            training_data = data_generator.generate_training_cases(500)
            prediction_engine.train_from_database(training_data)
        except Exception:
            pass  # If training fails, system will use fallback
    
    return prediction_engine
