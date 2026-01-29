from typing import Dict, List
import random
from schemas import SymptomSubmission, AIAssessment

def generate_ai_assessment(symptoms: SymptomSubmission) -> Dict:
    """
    Generate AI assessment based on symptoms.
    FOR EDUCATIONAL PURPOSES ONLY - Not real medical advice.
    """
    
    # Rule-based symptom analysis
    conditions = []
    confidence = 0.5  # Base confidence
    
    # Simple rule-based diagnosis (educational only)
    if symptoms.has_fever and symptoms.has_cough:
        conditions.extend(["Common Cold", "Influenza", "COVID-19"])
        confidence += 0.2
    elif symptoms.has_headache and not symptoms.has_fever:
        conditions.extend(["Tension Headache", "Migraine", "Stress-related"])
        confidence += 0.1
    elif symptoms.has_nausea and symptoms.has_fatigue:
        conditions.extend(["Gastroenteritis", "Food Poisoning", "Viral Infection"])
        confidence += 0.15
    
    # Add general conditions if none specific matched
    if not conditions:
        conditions = ["Viral Infection", "Bacterial Infection", "General Malaise"]
    
    # Determine urgency based on severity and symptoms
    if symptoms.severity >= 8 or symptoms.temperature and symptoms.temperature > 39:
        urgency = "high"
    elif symptoms.severity >= 5:
        urgency = "medium"
    else:
        urgency = "low"
    
    # Suggested tests (educational only)
    recommended_tests = ["Physical Examination", "Patient History Review"]
    if symptoms.has_fever:
        recommended_tests.append("Temperature Measurement")
    if symptoms.severity >= 7:
        recommended_tests.append("Blood Test")
    
    # Ensure confidence is between 0 and 1
    confidence = min(max(confidence, 0.1), 0.95)
    
    return {
        "possible_conditions": conditions[:3],  # Top 3 likely conditions
        "confidence_score": round(confidence, 2),
        "recommended_tests": recommended_tests,
        "urgency_level": urgency,
        "educational_note": "⚠️ AI ASSESSMENT FOR EDUCATIONAL PURPOSES ONLY ⚠️\nThis is not a real medical diagnosis. Always consult a qualified healthcare provider."
    }

def generate_prescription_suggestion(diagnosis: str) -> Dict:
    """
    Generate prescription suggestions based on diagnosis.
    FOR EDUCATIONAL SIMULATION ONLY.
    """
    # Educational prescription templates
    templates = {
        "common_cold": {
            "medication_name": "Acetaminophen",
            "dosage": "500mg",
            "frequency": "Every 6 hours as needed",
            "duration_days": 3,
            "instructions": "Take with food. Rest and hydrate.",
            "warning": "SIMULATED PRESCRIPTION - FOR EDUCATIONAL USE ONLY"
        },
        "headache": {
            "medication_name": "Ibuprofen",
            "dosage": "400mg",
            "frequency": "Every 8 hours as needed",
            "duration_days": 3,
            "instructions": "Take with food. Avoid if allergic to NSAIDs.",
            "warning": "SIMULATED PRESCRIPTION - FOR EDUCATIONAL USE ONLY"
        },
        "generic": {
            "medication_name": "General Symptom Relief",
            "dosage": "As directed",
            "frequency": "As needed",
            "duration_days": 5,
            "instructions": "Follow doctor's advice. Get plenty of rest.",
            "warning": "SIMULATED PRESCRIPTION - FOR EDUCATIONAL USE ONLY"
        }
    }
    
    diagnosis_lower = diagnosis.lower()
    if "cold" in diagnosis_lower or "flu" in diagnosis_lower:
        return templates["common_cold"]
    elif "headache" in diagnosis_lower or "migraine" in diagnosis_lower:
        return templates["headache"]
    else:
        return templates["generic"]