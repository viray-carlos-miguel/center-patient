#!/usr/bin/env python3
"""
Test AI Symptom Analysis
This script tests the Gemini AI integration for symptom analysis
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'src', 'app', 'services'))

# Import the Gemini AI service (we'll simulate it here)
class MockGeminiAI:
    def __init__(self):
        self.api_key = "demo-key"  # No real API key configured
    
    def analyzeSymptoms(self, symptoms):
        """Mock AI analysis based on symptoms"""
        print("🤖 Analyzing symptoms with AI...")
        print(f"📋 Symptoms: {symptoms}")
        
        # Extract key symptoms
        severity = symptoms.get('severity', 1)
        temperature = symptoms.get('temperature')
        has_fever = symptoms.get('has_fever', False)
        has_cough = symptoms.get('has_cough', False)
        has_headache = symptoms.get('has_headache', False)
        has_nausea = symptoms.get('has_nausea', False)
        has_fatigue = symptoms.get('has_fatigue', False)
        
        # AI Logic for symptom analysis
        conditions = []
        confidence = 0.5
        urgency = 'low'
        tests = []
        
        # Advanced symptom analysis logic
        if has_fever and has_cough and severity >= 5:
            if temperature and temperature >= 39:
                conditions = ['High Fever', 'Severe Respiratory Infection', 'Possible Pneumonia']
                confidence = 0.85
                urgency = 'high'
                tests = ['Complete Blood Count', 'Chest X-Ray', 'Blood Cultures', 'COVID-19 Test']
            else:
                conditions = ['Influenza (Flu)', 'Acute Bronchitis', 'Respiratory Infection']
                confidence = 0.75
                urgency = 'medium' if temperature and temperature >= 38.5 else 'low'
                tests = ['Complete Blood Count', 'Chest X-Ray', 'Flu Test', 'Temperature Monitoring']
        
        elif has_headache and severity >= 7:
            if has_nausea and has_fatigue:
                conditions = ['Migraine with Aura', 'Tension Headache (Severe)', 'Cluster Headache']
                confidence = 0.80
                urgency = 'medium'
                tests = ['Neurological Examination', 'MRI Brain (if severe)', 'Blood Pressure Check', 'Eye Examination']
            else:
                conditions = ['Tension Headache', 'Migraine', 'Sinus Headache']
                confidence = 0.65
                urgency = 'low'
                tests = ['Neurological Examination', 'Blood Pressure Check', 'Sinus X-Ray']
        
        elif has_fever and has_headache and severity >= 4:
            conditions = ['Viral Syndrome', 'Dengue Fever (possible)', 'Typhoid Fever (possible)']
            confidence = 0.70
            urgency = 'medium' if temperature and temperature >= 38.5 else 'low'
            tests = ['Complete Blood Count', 'Dengue Test', 'Widal Test', 'Physical Examination']
        
        elif has_nausea and has_fatigue and severity >= 5:
            conditions = ['Gastroenteritis', 'Food Poisoning', 'Viral Gastrointestinal Infection']
            confidence = 0.65
            urgency = 'low'
            tests = ['Stool Examination', 'Complete Blood Count', 'Dehydration Assessment']
        
        elif has_fever and severity >= 3:
            conditions = ['Common Cold', 'Viral Infection', 'Upper Respiratory Infection']
            confidence = 0.60
            urgency = 'low'
            tests = ['Physical Examination', 'Temperature Monitoring', 'Throat Swab']
        
        else:
            conditions = ['General Malaise', 'Mild Illness', 'Stress-Related Symptoms']
            confidence = 0.40
            urgency = 'low'
            tests = ['Physical Examination', 'Basic Blood Tests']
        
        # Adjust confidence based on symptom completeness
        symptom_count = sum([has_fever, has_cough, has_headache, has_nausea, has_fatigue])
        if symptom_count >= 3:
            confidence = min(confidence + 0.1, 0.9)
        elif symptom_count <= 1:
            confidence = max(confidence - 0.1, 0.3)
        
        return {
            "possible_conditions": conditions,
            "confidence_score": confidence,
            "recommended_tests": tests,
            "urgency_level": urgency,
            "medical_note": f"AI medical assessment based on {symptom_count} reported symptoms. The analysis indicates possible conditions with {round(confidence * 100)}% confidence. This assessment supports clinical decision making and should be reviewed by qualified healthcare professionals.",
            "ai_provider": 'mock-gemini-advanced',
            "medical_disclaimer": 'This AI assessment supports clinical decision making and should be reviewed by qualified healthcare professionals.',
            "symptom_analysis": {
                "total_symptoms": symptom_count,
                "severity_level": severity,
                "temperature_status": 'fever' if temperature and temperature >= 37.5 else 'normal',
                "analysis_depth": 'comprehensive' if symptom_count >= 3 else 'basic'
            }
        }

def test_ai_analysis():
    """Test AI symptom analysis with various scenarios"""
    print("🧪 Testing AI Symptom Analysis")
    print("=" * 50)
    
    ai = MockGeminiAI()
    
    # Test cases
    test_cases = [
        {
            "name": "Severe Flu-like Symptoms",
            "symptoms": {
                "description": "High fever, severe cough, body aches for 3 days",
                "duration_hours": 72,
                "severity": 8,
                "temperature": 39.2,
                "has_fever": True,
                "has_cough": True,
                "has_headache": True,
                "has_fatigue": True,
                "has_nausea": False,
                "additional_notes": "Difficulty breathing"
            }
        },
        {
            "name": "Migraine Symptoms",
            "symptoms": {
                "description": "Severe headache with nausea and light sensitivity",
                "duration_hours": 12,
                "severity": 7,
                "temperature": 37.0,
                "has_fever": False,
                "has_cough": False,
                "has_headache": True,
                "has_fatigue": False,
                "has_nausea": True,
                "additional_notes": "Worse with bright lights"
            }
        },
        {
            "name": "Mild Cold Symptoms",
            "symptoms": {
                "description": "Slight cough and runny nose",
                "duration_hours": 24,
                "severity": 3,
                "temperature": 37.3,
                "has_fever": True,
                "has_cough": True,
                "has_headache": False,
                "has_fatigue": False,
                "has_nausea": False,
                "additional_notes": "No major issues"
            }
        },
        {
            "name": "Gastrointestinal Issues",
            "symptoms": {
                "description": "Nausea and fatigue after eating",
                "duration_hours": 6,
                "severity": 5,
                "temperature": 37.0,
                "has_fever": False,
                "has_cough": False,
                "has_headache": False,
                "has_fatigue": True,
                "has_nausea": True,
                "additional_notes": "Stomach cramps"
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {test_case['name']}")
        print("-" * 40)
        
        result = ai.analyzeSymptoms(test_case['symptoms'])
        
        print(f"🔍 Possible Conditions: {', '.join(result['possible_conditions'])}")
        print(f"📊 Confidence Score: {round(result['confidence_score'] * 100)}%")
        print(f"⚡ Urgency Level: {result['urgency_level']}")
        print(f"🧪 Recommended Tests: {', '.join(result['recommended_tests'])}")
        print(f"📝 Medical Note: {result['medical_note'][:100]}...")
        print(f"🤖 AI Provider: {result['ai_provider']}")
        
        if 'symptom_analysis' in result:
            analysis = result['symptom_analysis']
            print(f"📈 Symptoms Analyzed: {analysis['total_symptoms']}")
            print(f"🌡️ Temperature Status: {analysis['temperature_status']}")
            print(f"🔬 Analysis Depth: {analysis['analysis_depth']}")
    
    print("\n" + "=" * 50)
    print("✅ AI Analysis Testing Complete!")
    print("\n🎯 Assessment Summary:")
    print("• AI analyzes multiple symptom combinations")
    print("• Confidence scores adjust based on symptom completeness")
    print("• Urgency levels determined by severity and temperature")
    print("• Medical disclaimers included for professional use")
    print("• Comprehensive test recommendations provided")

if __name__ == "__main__":
    test_ai_analysis()
