# backend/ai_system/core/gemini_predictor.py
import google.generativeai as genai
import os
from dotenv import load_dotenv
from typing import Dict, List, Any
import json

load_dotenv()

class GeminiClinicalPredictor:
    def __init__(self):
        # Configure Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        
        # Initialize the model
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Medical context prompt
        self.system_prompt = """You are a medical AI assistant for educational purposes only. 
        Analyze patient symptoms and provide:
        1. Possible conditions with confidence scores
        2. Recommended medical tests
        3. Urgency level (low, medium, high)
        4. Educational notes
        
        IMPORTANT DISCLAIMERS:
        - This is for EDUCATIONAL purposes only
        - NOT for real medical diagnosis
        - ALWAYS consult a real doctor
        - This is a simulation for medical training
        
        Format your response as a JSON object with:
        {
            "possible_conditions": [
                {"condition": "Condition Name", "confidence": 0.85, "reasoning": "Brief explanation"}
            ],
            "recommended_tests": ["Test 1", "Test 2"],
            "urgency_level": "low/medium/high",
            "educational_notes": "Educational explanation"
        }
        
        Keep responses concise and educational."""
    
    def analyze_symptoms(self, symptoms: Dict[str, Any], patient_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze symptoms using Gemini AI"""
        
        # Prepare patient info
        if not patient_info:
            patient_info = {"age": 30, "has_chronic_conditions": False}
        
        # Create symptom description
        symptom_text = self._format_symptoms(symptoms)
        patient_text = self._format_patient_info(patient_info)
        
        # Create prompt
        prompt = f"""{self.system_prompt}

        PATIENT INFORMATION:
        {patient_text}

        SYMPTOMS:
        {symptom_text}

        Please analyze these symptoms and provide the JSON response as specified above."""
        
        try:
            # Call Gemini API
            response = self.model.generate_content(prompt)
            
            # Extract JSON from response
            response_text = response.text
            
            # Clean the response (remove markdown code blocks if present)
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0].strip()
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0].strip()
            
            # Parse JSON
            result = json.loads(response_text)
            
            # Format for our system
            formatted_result = {
                "disease_predictions": [
                    {
                        "disease": condition.get("condition", "Unknown"),
                        "confidence": condition.get("confidence", 0.5),
                        "matching_symptoms": [],
                        "urgency": result.get("urgency_level", "low")
                    }
                    for condition in result.get("possible_conditions", [])[:3]  # Top 3 only
                ],
                "risk_assessment": {
                    "risk_score": self._calculate_risk_score(result.get("urgency_level", "low")),
                    "urgency_level": result.get("urgency_level", "low"),
                    "recommended_action": "Consult a healthcare professional"
                },
                "recommendations": {
                    "medical_tests": result.get("recommended_tests", ["Physical Examination"]),
                    "self_care": ["Rest", "Hydration", "Monitor symptoms"],
                    "when_to_seek_help": "If symptoms worsen or don't improve in 48 hours"
                },
                "confidence_score": self._calculate_overall_confidence(result.get("possible_conditions", [])),
                "educational_notes": result.get("educational_notes", "AI analysis for educational purposes only")
            }
            
            return formatted_result
            
        except Exception as e:
            print(f"❌ Gemini API error: {e}")
            # Return fallback response
            return self._get_fallback_response(symptoms)
    
    def _format_symptoms(self, symptoms: Dict[str, Any]) -> str:
        """Format symptoms for the prompt"""
        lines = []
        
        # Basic symptoms
        if symptoms.get('description'):
            lines.append(f"Description: {symptoms['description']}")
        
        if symptoms.get('duration_hours'):
            days = symptoms['duration_hours'] / 24
            lines.append(f"Duration: {symptoms['duration_hours']} hours ({days:.1f} days)")
        
        if symptoms.get('severity'):
            lines.append(f"Severity: {symptoms['severity']}/10")
        
        if symptoms.get('temperature'):
            lines.append(f"Temperature: {symptoms['temperature']}°C")
        
        # Boolean symptoms
        bool_symptoms = []
        for key, value in symptoms.items():
            if key.startswith('has_') and value:
                symptom_name = key[4:].replace('_', ' ')
                bool_symptoms.append(symptom_name)
        
        if bool_symptoms:
            lines.append(f"Specific symptoms: {', '.join(bool_symptoms)}")
        
        if symptoms.get('additional_notes'):
            lines.append(f"Additional notes: {symptoms['additional_notes']}")
        
        return "\n".join(lines)
    
    def _format_patient_info(self, patient_info: Dict[str, Any]) -> str:
        """Format patient information"""
        lines = []
        
        if patient_info.get('age'):
            lines.append(f"Age: {patient_info['age']}")
        
        if patient_info.get('has_chronic_conditions'):
            lines.append("Has chronic conditions: Yes")
        else:
            lines.append("Has chronic conditions: No")
        
        if patient_info.get('gender'):
            lines.append(f"Gender: {patient_info['gender']}")
        
        return "\n".join(lines)
    
    def _calculate_risk_score(self, urgency_level: str) -> float:
        """Convert urgency level to risk score"""
        urgency_scores = {
            'low': 0.3,
            'medium': 0.6,
            'high': 0.9
        }
        return urgency_scores.get(urgency_level.lower(), 0.5)
    
    def _calculate_overall_confidence(self, conditions: List[Dict]) -> float:
        """Calculate overall confidence score"""
        if not conditions:
            return 0.5
        
        confidences = [cond.get('confidence', 0.5) for cond in conditions]
        return sum(confidences) / len(confidences)
    
    def _get_fallback_response(self, symptoms: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback response if Gemini fails"""
        # Simple rule-based fallback
        has_fever = symptoms.get('has_fever', False)
        has_cough = symptoms.get('has_cough', False)
        has_headache = symptoms.get('has_headache', False)
        
        if has_fever and has_cough:
            conditions = [{"condition": "Viral Infection", "confidence": 0.7}]
            urgency = "medium"
        elif has_headache:
            conditions = [{"condition": "Tension Headache", "confidence": 0.6}]
            urgency = "low"
        else:
            conditions = [{"condition": "General Medical Assessment Needed", "confidence": 0.5}]
            urgency = "low"
        
        return {
            "disease_predictions": [
                {
                    "disease": cond["condition"],
                    "confidence": cond["confidence"],
                    "matching_symptoms": [],
                    "urgency": urgency
                }
                for cond in conditions
            ],
            "risk_assessment": {
                "risk_score": 0.5,
                "urgency_level": urgency,
                "recommended_action": "Consult a healthcare professional"
            },
            "recommendations": {
                "medical_tests": ["Physical Examination"],
                "self_care": ["Rest", "Hydration"],
                "when_to_seek_help": "If symptoms worsen"
            },
            "confidence_score": conditions[0]["confidence"],
            "educational_notes": "Fallback analysis - AI service unavailable. For educational purposes only."
        }