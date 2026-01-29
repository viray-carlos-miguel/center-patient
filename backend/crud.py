from sqlalchemy.orm import Session
from typing import List, Optional, Dict
import json

# In-memory storage for demo purposes
demo_cases = []

def get_db():
    """Dependency to get DB session"""
    # For demo, we'll use in-memory storage
    # In production, yield actual DB session
    return None

def create_user(db: Session, username: str, email: str, full_name: str, role: str):
    """Create a new user (simulated)"""
    user = {
        "id": len(demo_cases) + 100,
        "username": username,
        "email": email,
        "full_name": full_name,
        "role": role
    }
    return user

def get_cases(status: Optional[str] = None) -> List[Dict]:
    """Get all cases, optionally filtered by status"""
    if not demo_cases:
        # Initialize with some demo cases
        demo_cases.extend([
            {
                "id": 1,
                "patient_id": 1,
                "patient_name": "John Doe",
                "symptoms": {
                    "description": "Fever and cough for 2 days",
                    "duration_hours": 48,
                    "severity": 6,
                    "temperature": 38.5,
                    "has_fever": True,
                    "has_cough": True,
                    "has_headache": True
                },
                "ai_assessment": {
                    "possible_conditions": ["Common Cold", "Influenza", "COVID-19"],
                    "confidence_score": 0.75,
                    "recommended_tests": ["Physical exam", "Temperature check"],
                    "urgency_level": "medium",
                    "educational_note": "AI assessment for educational purposes only"
                },
                "status": "pending_review",
                "created_at": "2024-01-15T09:00:00",
                "doctor_notes": None,
                "prescription": None,
                "final_diagnosis": None
            },
            {
                "id": 2,
                "patient_id": 3,
                "patient_name": "Jane Smith",
                "symptoms": {
                    "description": "Headache and nausea",
                    "duration_hours": 24,
                    "severity": 4,
                    "temperature": 37.0,
                    "has_fever": False,
                    "has_headache": True,
                    "has_nausea": True
                },
                "ai_assessment": {
                    "possible_conditions": ["Migraine", "Tension Headache", "Viral Infection"],
                    "confidence_score": 0.65,
                    "recommended_tests": ["Blood pressure check", "Neurological exam"],
                    "urgency_level": "low",
                    "educational_note": "AI assessment for educational purposes only"
                },
                "status": "completed",
                "created_at": "2024-01-14T14:30:00",
                "doctor_notes": "Likely tension headache. Recommended rest and hydration.",
                "prescription": {
                    "medication_name": "Acetaminophen",
                    "dosage": "500mg",
                    "frequency": "Every 6 hours as needed",
                    "duration_days": 3,
                    "instructions": "Take with food",
                    "warning": "Educational purposes only"
                },
                "final_diagnosis": "Tension Headache"
            }
        ])
    
    if status:
        return [case for case in demo_cases if case["status"] == status]
    return demo_cases

def update_case(case_id: int, updates: Dict) -> Optional[Dict]:
    """Update a case with new information"""
    for i, case in enumerate(demo_cases):
        if case["id"] == case_id:
            demo_cases[i].update(updates)
            demo_cases[i]["status"] = "completed"
            return demo_cases[i]
    return None