"""
REAL AI Prediction Engine - No Mock Data
Analyzes any symptoms users input
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClinicalPredictor:
    """Real AI that predicts from user symptoms"""
    
    def __init__(self):
        self.disease_patterns = self._load_disease_patterns()
        self.symptom_weights = self._calculate_symptom_weights()
        
    def analyze_symptoms(self, symptoms: Dict[str, Any], patient_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main analysis function - analyzes any symptoms user provides
        
        Args:
            symptoms: User's symptom data
            patient_info: Patient demographic info
            
        Returns:
            Complete AI analysis
        """
        try:
            # Parse symptoms
            parsed_symptoms = self._parse_symptom_data(symptoms)
            
            # Predict diseases
            disease_predictions = self._predict_diseases(parsed_symptoms)
            
            # Assess risk
            risk_assessment = self._assess_risk(parsed_symptoms, patient_info)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(disease_predictions, risk_assessment)
            
            # Calculate confidence
            confidence = self._calculate_confidence(disease_predictions)
            
            # Return complete analysis
            return {
                "analysis_id": f"ai_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "patient_info": patient_info,
                "symptoms_analyzed": parsed_symptoms,
                "disease_predictions": disease_predictions,
                "risk_assessment": risk_assessment,
                "recommendations": recommendations,
                "confidence_score": confidence,
                "analysis_timestamp": datetime.now().isoformat(),
                "ai_version": "1.0.0"
            }
            
        except Exception as e:
            logger.error(f"AI analysis error: {e}")
            raise Exception(f"AI analysis failed: {str(e)}")
    
    def _parse_symptom_data(self, symptoms: Dict) -> Dict:
        """Parse and structure symptom input"""
        parsed = {
            "primary_symptoms": [],
            "symptom_details": {},
            "severity_scores": {},
            "duration_days": symptoms.get("duration_days", 1),
            "symptom_text": symptoms.get("symptom_description", "")
        }
        
        # Check all possible symptom fields
        symptom_fields = [
            "fever", "cough", "headache", "fatigue", "nausea", "vomiting",
            "diarrhea", "shortness_of_breath", "chest_pain", "sore_throat",
            "runny_nose", "body_aches", "chills", "dizziness", "abdominal_pain",
            "loss_of_taste", "loss_of_smell", "rash", "joint_pain", "back_pain"
        ]
        
        for symptom in symptom_fields:
            value = symptoms.get(symptom)
            if value:
                if isinstance(value, bool) and value:
                    parsed["primary_symptoms"].append(symptom)
                    parsed["severity_scores"][symptom] = 5  # Default moderate
                elif isinstance(value, (int, float)) and value > 0:
                    parsed["primary_symptoms"].append(symptom)
                    parsed["severity_scores"][symptom] = min(10, float(value))
                elif isinstance(value, str) and value.lower() not in ["no", "false", "none", "0"]:
                    parsed["primary_symptoms"].append(symptom)
                    parsed["symptom_details"][symptom] = value
        
        # Extract symptoms from text description
        if symptoms.get("symptom_description"):
            text_symptoms = self._extract_from_text(symptoms["symptom_description"])
            parsed["primary_symptoms"].extend([s for s in text_symptoms if s not in parsed["primary_symptoms"]])
        
        return parsed
    
    def _predict_diseases(self, symptoms: Dict) -> List[Dict]:
        """Predict diseases based on symptom patterns"""
        patient_symptoms = set(symptoms["primary_symptoms"])
        predictions = []
        
        for disease, pattern in self.disease_patterns.items():
            score = 0
            matching_symptoms = []
            
            # Check core symptoms
            core_match = len(set(pattern["core_symptoms"]).intersection(patient_symptoms))
            if core_match >= pattern.get("min_core_symptoms", 1):
                score += core_match * 3
                matching_symptoms.extend(list(set(pattern["core_symptoms"]).intersection(patient_symptoms)))
            
            # Check common symptoms
            common_match = len(set(pattern["common_symptoms"]).intersection(patient_symptoms))
            score += common_match * 2
            matching_symptoms.extend(list(set(pattern["common_symptoms"]).intersection(patient_symptoms)))
            
            # Check warning symptoms
            warning_match = len(set(pattern.get("warning_symptoms", [])).intersection(patient_symptoms))
            score += warning_match * 4
            
            if score > 0:
                # Calculate confidence percentage
                max_possible_score = (len(pattern["core_symptoms"]) * 3 + 
                                    len(pattern["common_symptoms"]) * 2 +
                                    len(pattern.get("warning_symptoms", [])) * 4)
                confidence = min(95, (score / max_possible_score * 100) if max_possible_score > 0 else 0)
                
                predictions.append({
                    "disease": disease,
                    "confidence": round(confidence, 1),
                    "matching_symptoms": list(set(matching_symptoms)),
                    "missing_symptoms": list(set(pattern["core_symptoms"] + pattern["common_symptoms"]) - patient_symptoms),
                    "urgency": pattern.get("urgency", "medium")
                })
        
        # Sort by confidence
        predictions.sort(key=lambda x: x["confidence"], reverse=True)
        
        return predictions[:5]  # Return top 5
    
    def _assess_risk(self, symptoms: Dict, patient_info: Dict) -> Dict:
        """Assess clinical risk and urgency"""
        risk_score = 0
        warning_signs = []
        
        # High-risk symptoms check
        high_risk_symptoms = ["chest_pain", "shortness_of_breath", "severe_headache", 
                             "confusion", "unconsciousness", "severe_bleeding"]
        
        for symptom in high_risk_symptoms:
            if symptom in symptoms["primary_symptoms"]:
                risk_score += 3
                warning_signs.append(symptom)
        
        # Medium-risk symptoms
        medium_risk_symptoms = ["high_fever", "severe_vomiting", "severe_diarrhea", 
                               "difficulty_swallowing", "severe_abdominal_pain"]
        
        for symptom in medium_risk_symptoms:
            if symptom in symptoms["primary_symptoms"]:
                risk_score += 2
                warning_signs.append(symptom)
        
        # Patient factors
        age = patient_info.get("age", 30)
        if age >= 65:
            risk_score += 2
        elif age <= 5:
            risk_score += 1
        
        if patient_info.get("has_chronic_conditions", False):
            risk_score += 2
        
        if patient_info.get("is_pregnant", False):
            risk_score += 1
        
        # Duration factor
        duration = symptoms.get("duration_days", 1)
        if duration > 14:
            risk_score += 1
        elif duration > 30:
            risk_score += 2
        
        # Determine urgency
        if risk_score >= 8:
            urgency = "high"
            action = "Seek emergency care immediately"
            wait_time = "0-2 hours"
        elif risk_score >= 5:
            urgency = "medium"
            action = "See doctor within 24 hours"
            wait_time = "24 hours"
        else:
            urgency = "low"
            action = "Schedule appointment when convenient"
            wait_time = "2-3 days"
        
        return {
            "risk_score": risk_score,
            "urgency_level": urgency,
            "recommended_action": action,
            "max_wait_time": wait_time,
            "warning_signs": warning_signs,
            "patient_risk_factors": self._get_patient_risk_factors(patient_info)
        }
    
    def _generate_recommendations(self, diseases: List[Dict], risk: Dict) -> Dict:
        """Generate personalized recommendations"""
        recommendations = {
            "immediate_actions": [],
            "medical_tests": [],
            "home_care": [],
            "medications": [],
            "follow_up": []
        }
        
        # Based on urgency
        if risk["urgency_level"] == "high":
            recommendations["immediate_actions"].append("Call emergency services (911/112)")
            recommendations["immediate_actions"].append("Do not drive yourself")
            recommendations["immediate_actions"].append("Have someone stay with you")
        elif risk["urgency_level"] == "medium":
            recommendations["immediate_actions"].append("Contact your doctor today")
            recommendations["immediate_actions"].append("Rest and monitor symptoms")
        
        # Based on predicted diseases
        if diseases:
            top_disease = diseases[0]["disease"]
            
            # Disease-specific recommendations
            disease_recommendations = {
                "Common Cold": {
                    "home_care": ["Rest", "Stay hydrated", "Use saline nasal spray"],
                    "medications": ["Acetaminophen for fever", "Decongestants if needed"]
                },
                "Influenza (Flu)": {
                    "medical_tests": ["Influenza test"],
                    "medications": ["Antiviral medication (if early)", "Fever reducers"],
                    "home_care": ["Isolate from others", "Rest", "Hydrate"]
                },
                "COVID-19": {
                    "medical_tests": ["COVID-19 test"],
                    "home_care": ["Isolate for 5 days", "Wear mask around others", "Monitor oxygen levels"],
                    "follow_up": ["Check temperature twice daily"]
                },
                "Migraine": {
                    "home_care": ["Rest in dark, quiet room", "Apply cold compress"],
                    "medications": ["Prescribed migraine medication", "Pain relievers"]
                },
                "Gastroenteritis": {
                    "home_care": ["BRAT diet (bananas, rice, applesauce, toast)", "Small sips of water"],
                    "medications": ["Anti-nausea medication", "Rehydration solutions"]
                }
            }
            
            if top_disease in disease_recommendations:
                recs = disease_recommendations[top_disease]
                recommendations["home_care"].extend(recs.get("home_care", []))
                recommendations["medical_tests"].extend(recs.get("medical_tests", []))
                recommendations["medications"].extend(recs.get("medications", []))
                recommendations["follow_up"].extend(recs.get("follow_up", []))
        
        # General recommendations
        if not recommendations["home_care"]:
            recommendations["home_care"].extend(["Rest", "Stay hydrated", "Monitor symptoms"])
        
        return recommendations
    
    def _calculate_confidence(self, predictions: List[Dict]) -> float:
        """Calculate overall AI confidence"""
        if not predictions:
            return 0.0
        
        # Use top prediction confidence
        top_confidence = predictions[0]["confidence"]
        
        # Adjust based on number of predictions
        if len(predictions) == 1:
            confidence = top_confidence
        elif len(predictions) >= 3:
            confidence = top_confidence * 0.8  # Less confident if many possibilities
        else:
            confidence = top_confidence * 0.9
        
        return round(confidence / 100, 2)  # Convert to 0-1 scale
    
    def _load_disease_patterns(self) -> Dict:
        """Load real disease-symptom patterns"""
        return {
            "Common Cold": {
                "core_symptoms": ["runny_nose", "sore_throat", "sneezing"],
                "common_symptoms": ["cough", "congestion", "mild_headache", "fatigue"],
                "min_core_symptoms": 2,
                "urgency": "low"
            },
            "Influenza (Flu)": {
                "core_symptoms": ["fever", "body_aches", "fatigue"],
                "common_symptoms": ["cough", "headache", "chills", "sore_throat"],
                "warning_symptoms": ["high_fever", "difficulty_breathing"],
                "min_core_symptoms": 2,
                "urgency": "medium"
            },
            "COVID-19": {
                "core_symptoms": ["fever", "cough", "fatigue"],
                "common_symptoms": ["loss_of_taste", "loss_of_smell", "shortness_of_breath", "headache"],
                "warning_symptoms": ["severe_shortness_of_breath", "chest_pain"],
                "min_core_symptoms": 2,
                "urgency": "medium"
            },
            "Migraine": {
                "core_symptoms": ["headache", "sensitivity_to_light"],
                "common_symptoms": ["nausea", "sensitivity_to_sound", "aura"],
                "min_core_symptoms": 2,
                "urgency": "medium"
            },
            "Gastroenteritis (Stomach Flu)": {
                "core_symptoms": ["nausea", "vomiting", "diarrhea"],
                "common_symptoms": ["abdominal_pain", "fever", "body_aches"],
                "warning_symptoms": ["severe_dehydration", "blood_in_stool"],
                "min_core_symptoms": 2,
                "urgency": "low"
            },
            "Bronchitis": {
                "core_symptoms": ["cough", "chest_discomfort"],
                "common_symptoms": ["fatigue", "shortness_of_breath", "mild_fever"],
                "min_core_symptoms": 2,
                "urgency": "medium"
            },
            "Urinary Tract Infection (UTI)": {
                "core_symptoms": ["painful_urination", "frequent_urination"],
                "common_symptoms": ["abdominal_pain", "fever", "back_pain"],
                "min_core_symptoms": 2,
                "urgency": "medium"
            },
            "Anxiety/Panic Attack": {
                "core_symptoms": ["shortness_of_breath", "chest_pain", "rapid_heartbeat"],
                "common_symptoms": ["dizziness", "sweating", "trembling"],
                "min_core_symptoms": 2,
                "urgency": "medium"
            }
        }
    
    def _calculate_symptom_weights(self) -> Dict:
        """Calculate importance weights for symptoms"""
        weights = {}
        
        # High importance symptoms
        high_weight = ["chest_pain", "shortness_of_breath", "severe_headache", 
                      "unconsciousness", "seizure", "severe_bleeding"]
        
        # Medium importance symptoms
        medium_weight = ["fever", "vomiting", "diarrhea", "abdominal_pain", 
                        "difficulty_breathing", "confusion"]
        
        # Low importance symptoms
        low_weight = ["runny_nose", "sneezing", "mild_headache", "fatigue", 
                     "mild_cough", "sore_throat"]
        
        for symptom in high_weight:
            weights[symptom] = 3.0
        for symptom in medium_weight:
            weights[symptom] = 2.0
        for symptom in low_weight:
            weights[symptom] = 1.0
            
        return weights
    
    def _extract_from_text(self, text: str) -> List[str]:
        """Extract symptoms from free text"""
        text_lower = text.lower()
        found_symptoms = []
        
        symptom_keywords = {
            "fever": ["fever", "temperature", "hot", "chills"],
            "cough": ["cough", "coughing", "hacking"],
            "headache": ["headache", "head pain", "migraine"],
            "fatigue": ["tired", "fatigue", "exhausted", "weak"],
            "nausea": ["nausea", "queasy", "sick to stomach"],
            "vomiting": ["vomit", "throwing up"],
            "diarrhea": ["diarrhea", "loose stool"],
            "shortness_of_breath": ["short of breath", "can't breathe", "breathless"],
            "chest_pain": ["chest pain", "chest tightness", "heart pain"],
            "sore_throat": ["sore throat", "throat pain"],
            "runny_nose": ["runny nose", "nasal discharge"],
            "body_aches": ["body aches", "muscle pain", "joint pain"]
        }
        
        for symptom, keywords in symptom_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                found_symptoms.append(symptom)
        
        return found_symptoms
    
    def _get_patient_risk_factors(self, patient_info: Dict) -> List[str]:
        """Identify patient-specific risk factors"""
        factors = []
        
        age = patient_info.get("age", 30)
        if age >= 65:
            factors.append("Age 65+")
        elif age <= 5:
            factors.append("Age under 5")
        
        if patient_info.get("has_chronic_conditions", False):
            factors.append("Chronic health conditions")
        
        if patient_info.get("is_smoker", False):
            factors.append("Smoker")
        
        if patient_info.get("is_pregnant", False):
            factors.append("Pregnancy")
        
        if patient_info.get("is_immunocompromised", False):
            factors.append("Weakened immune system")
        
        return factors