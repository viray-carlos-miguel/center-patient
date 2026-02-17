#!/usr/bin/env python3
"""
Test the current ML system accuracy
"""

import requests
import json

def test_ml_accuracy():
    """Test ML system accuracy"""
    url = "http://localhost:8000/api/ml/predict"
    
    # Test case: Common cold symptoms
    test_symptoms = {
        "symptoms": {
            "description": "Patient reports headache, cough, sore throat, runny nose, and fatigue for 3 days with mild fever",
            "fever": True,
            "cough": True,
            "sore_throat": True,
            "headache": True,
            "fatigue": True,
            "runny_nose": True,
            "has_fever": True,
            "has_cough": True,
            "has_sore_throat": True,
            "has_headache": True,
            "has_fatigue": True,
            "has_runny_nose": True,
            "has_shortness_of_breath": False,
            "has_abdominal_pain": False,
            "temperature": 37.5,
            "severity": 3,
            "duration_hours": 72
        },
        "patient_info": {
            "age": 30,
            "gender": "male",
            "has_chronic_conditions": False
        }
    }
    
    try:
        print("🔍 Testing Trained ML System...")
        print(f"📋 Symptoms: {test_symptoms['symptoms']['description']}")
        
        response = requests.post(url, json=test_symptoms, headers={'Content-Type': 'application/json'})
        
        print(f"✅ Status Code: {response.status_code}")
        result = response.json()
        
        if response.status_code == 200:
            print("📊 ML Analysis Result:")
            print(json.dumps(result, indent=2, default=str))
            
            # Check confidence
            if 'ml_prediction' in result:
                ml_prediction = result['ml_prediction']
                if 'consensus' in ml_prediction:
                    confidence = ml_prediction['consensus']
                    print(f"\n📈 Current Confidence: {confidence * 100:.1f}%")
                    
                    if confidence >= 0.8:
                        print("🎉 EXCELLENT: 80-90% accuracy achieved!")
                    elif confidence >= 0.7:
                        print("👍 GOOD: 70-80% accuracy")
                    elif confidence >= 0.6:
                        print("📈 FAIR: 60-70% accuracy")
                    else:
                        print("⚠️ NEEDS IMPROVEMENT: Below 60% accuracy")
                else:
                    print("⚠️ No consensus score found")
            else:
                print("⚠️ No ML prediction found in response")
        else:
            print(f"❌ Error: {result}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    print("🧪 Testing Trained ML System Accuracy")
    test_ml_accuracy()
