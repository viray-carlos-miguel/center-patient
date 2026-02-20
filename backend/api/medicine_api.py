"""
Medicine Recommendation API
Endpoints for AI-powered medicine recommendation and treatment analysis
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json

from ml.medicine_recommendation_engine import medicine_engine
from models.doctor_verification import doctor_verification, VerificationStatus
from models.user_evaluation import user_evaluation, UserType, EvaluationType

router = APIRouter(prefix="/api/medicine", tags=["medicine"])
security = HTTPBearer()

# Pydantic models
class PatientProfile(BaseModel):
    id: int
    name: str
    age: int
    weight: float
    email: EmailStr
    symptoms: List[str]
    medical_conditions: List[str] = []
    current_medications: List[str] = []
    allergies: List[str] = []
    pregnancy: bool = False
    breastfeeding: bool = False
    severity: str = "moderate"  # mild, moderate, severe

class MedicineRecommendationRequest(BaseModel):
    patient_profile: PatientProfile
    include_treatment_analysis: bool = True
    include_safety_analysis: bool = True

class DoctorVerificationRequest(BaseModel):
    doctor_id: int
    license_number: str
    password: str
    verification_method: str = "digital_signature"

class PrescriptionApprovalRequest(BaseModel):
    request_id: str
    doctor_id: int
    decision: str  # approve, reject
    notes: Optional[str] = None
    modifications: Optional[List[Dict]] = None

class EvaluationSessionRequest(BaseModel):
    user_id: int
    user_type: str
    name: str
    email: EmailStr
    age: int
    gender: str
    location: str
    profession: Optional[str] = None
    years_experience: Optional[int] = None
    digital_literacy: int = 3
    evaluation_type: str

class EvaluationSubmissionRequest(BaseModel):
    session_id: str
    responses: List[Dict]
    case_evaluations: Optional[List[Dict]] = None

@router.post("/recommend")
async def get_medicine_recommendations(
    request: MedicineRecommendationRequest,
    background_tasks: BackgroundTasks
):
    """Generate AI-powered medicine recommendations"""
    try:
        patient_data = request.patient_profile.dict()
        
        # Generate recommendations
        recommendations = medicine_engine.recommend_medicines(
            symptoms=patient_data["symptoms"],
            patient_profile=patient_data
        )
        
        if not recommendations["success"]:
            raise HTTPException(status_code=400, detail=recommendations["error"])
        
        # If prescription required, create verification request
        if recommendations["requires_prescription"]:
            prescription_request = doctor_verification.create_prescription_request(
                patient_data=patient_data,
                ai_recommendations=recommendations
            )
            recommendations["prescription_request_id"] = prescription_request.id
            recommendations["verification_required"] = True
        else:
            recommendations["verification_required"] = False
        
        # Log for monitoring
        background_tasks.add_task(
            log_recommendation_usage,
            patient_data["id"],
            patient_data["symptoms"],
            recommendations["success"]
        )
        
        return {
            "success": True,
            "data": recommendations,
            "message": "Medicine recommendations generated successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recommendations/{request_id}")
async def get_recommendation_details(request_id: str):
    """Get detailed information about a recommendation request"""
    try:
        verification_record = doctor_verification.get_verification_record(request_id)
        if not verification_record:
            raise HTTPException(status_code=404, detail="Recommendation request not found")
        
        return {
            "success": True,
            "data": verification_record.dict(),
            "message": "Recommendation details retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/doctor/pending-requests")
async def get_pending_prescription_requests(
    doctor_id: Optional[int] = None,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get pending prescription requests for doctor verification"""
    try:
        # Verify doctor credentials (simplified)
        pending_requests = doctor_verification.get_pending_requests(doctor_id)
        
        return {
            "success": True,
            "data": [req.dict() for req in pending_requests],
            "count": len(pending_requests),
            "message": "Pending requests retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/doctor/verify")
async def verify_doctor_credentials(request: DoctorVerificationRequest):
    """Verify doctor credentials for prescription approval"""
    try:
        is_valid = doctor_verification.verify_doctor_credentials(
            doctor_id=request.doctor_id,
            license_number=request.license_number,
            password=request.password
        )
        
        if not is_valid:
            raise HTTPException(status_code=401, detail="Invalid doctor credentials")
        
        # Generate OTP for additional verification
        otp = doctor_verification.generate_otp(request.doctor_id)
        
        return {
            "success": True,
            "data": {
                "doctor_id": request.doctor_id,
                "verified": True,
                "otp_required": True,
                "otp": otp  # In production, would send via SMS/email
            },
            "message": "Doctor credentials verified successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/doctor/approve-prescription")
async def approve_prescription(request: PrescriptionApprovalRequest):
    """Approve or reject prescription request"""
    try:
        if request.decision == "approve":
            record = doctor_verification.approve_prescription(
                request_id=request.request_id,
                doctor_id=request.doctor_id,
                notes=request.notes,
                modifications=request.modifications
            )
        elif request.decision == "reject":
            record = doctor_verification.reject_prescription(
                request_id=request.request_id,
                doctor_id=request.doctor_id,
                reason=request.notes or "No reason provided"
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid decision")
        
        return {
            "success": True,
            "data": record.dict(),
            "message": f"Prescription {request.decision}d successfully"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/doctor/workload/{doctor_id}")
async def get_doctor_workload(doctor_id: int, days: int = 7):
    """Get doctor workload statistics"""
    try:
        workload = doctor_verification.get_doctor_workload(doctor_id, days)
        
        return {
            "success": True,
            "data": workload,
            "message": "Doctor workload retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics")
async def get_prescription_statistics(days: int = 30):
    """Get overall prescription verification statistics"""
    try:
        stats = doctor_verification.get_prescription_statistics(days)
        
        return {
            "success": True,
            "data": stats,
            "message": "Statistics retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/drugs/search")
async def search_drugs(query: str, limit: int = 10):
    """Search drugs by name or indication"""
    try:
        from data.drug_database import drug_db
        
        # Search by drug name
        drug = drug_db.get_drug_by_name(query)
        results = []
        
        if drug:
            results.append(drug)
        
        # Search by indication
        if len(results) < limit:
            indication_results = drug_db.search_drugs_by_indication(query)
            for result in indication_results:
                if result not in results and len(results) < limit:
                    results.append(result)
        
        return {
            "success": True,
            "data": results[:limit],
            "count": len(results),
            "message": f"Found {len(results)} drugs"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/drugs/{drug_name}/info")
async def get_drug_information(drug_name: str):
    """Get detailed information about a specific drug"""
    try:
        from data.drug_database import drug_db
        
        drug_info = drug_db.get_drug_by_name(drug_name)
        if not drug_info:
            raise HTTPException(status_code=404, detail="Drug not found")
        
        # Get additional information
        side_effects = drug_db.get_side_effects(drug_name)
        interactions = drug_db.get_drug_interactions(drug_name)
        
        return {
            "success": True,
            "data": {
                "drug_info": drug_info,
                "side_effects": side_effects,
                "interactions": interactions
            },
            "message": "Drug information retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/evaluation/create-session")
async def create_evaluation_session(request: EvaluationSessionRequest):
    """Create a new user evaluation session"""
    try:
        user_data = request.dict()
        user_data["user_type"] = UserType(request.user_type)
        
        session = user_evaluation.create_evaluation_session(
            user_data=user_data,
            evaluation_type=EvaluationType(request.evaluation_type)
        )
        
        return {
            "success": True,
            "data": session,
            "message": "Evaluation session created successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/evaluation/submit")
async def submit_evaluation(request: EvaluationSubmissionRequest):
    """Submit completed evaluation"""
    try:
        # In a real system, would validate session_id and get session data
        # For now, create a mock session
        session_data = {
            "user_data": {
                "id": 1,
                "user_type": "patient",
                "name": "Test User",
                "email": "test@example.com"
            },
            "evaluation_type": "likert_scale",
            "created_at": datetime.now()
        }
        
        evaluation = user_evaluation.submit_evaluation(
            session_data=session_data,
            responses=request.responses,
            case_evaluations=request.case_evaluations
        )
        
        return {
            "success": True,
            "data": evaluation.dict(),
            "message": "Evaluation submitted successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/evaluation/questions")
async def get_evaluation_questions(user_type: str, evaluation_type: str):
    """Get evaluation questions for user type and evaluation type"""
    try:
        questions = user_evaluation.get_questions_for_user_type(
            UserType(user_type),
            EvaluationType(evaluation_type)
        )
        
        return {
            "success": True,
            "data": [q.dict() for q in questions],
            "count": len(questions),
            "message": "Questions retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/evaluation/case-studies")
async def get_case_studies():
    """Get case studies for evaluation"""
    try:
        case_studies = list(user_evaluation.case_studies.values())
        
        return {
            "success": True,
            "data": case_studies,
            "count": len(case_studies),
            "message": "Case studies retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/evaluation/report")
async def get_evaluation_report():
    """Generate comprehensive evaluation report"""
    try:
        report = user_evaluation.generate_evaluation_report()
        
        return {
            "success": True,
            "data": report,
            "message": "Evaluation report generated successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/evaluation/export")
async def export_evaluation_data():
    """Export evaluation data for analysis"""
    try:
        data = user_evaluation.export_data_for_analysis()
        
        return {
            "success": True,
            "data": data,
            "message": "Evaluation data exported successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "medicine_recommendation_api",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# Background task
async def log_recommendation_usage(patient_id: int, symptoms: List[str], success: bool):
    """Log recommendation usage for monitoring"""
    # In production, would log to database or monitoring system
    print(f"Recommendation usage: Patient {patient_id}, Symptoms: {symptoms}, Success: {success}")

# Dependency for doctor authentication (simplified)
async def get_current_doctor(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated doctor (simplified)"""
    # In production, would validate JWT token and return doctor info
    return {"id": 1, "name": "Dr. Test", "verified": True}
