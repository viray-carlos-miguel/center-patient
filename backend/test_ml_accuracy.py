"""
Comprehensive ML Accuracy Test Suite
Tests the prediction engine with diverse real-world medical cases
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from ml.prediction_engine import MedicalPredictionEngine

def test_ml_accuracy():
    """Test ML prediction accuracy with diverse medical cases"""
    print("=" * 80)
    print("🧪 COMPREHENSIVE ML ACCURACY TEST")
    print("=" * 80)
    
    engine = MedicalPredictionEngine()
    
    if not engine.is_trained:
        print("❌ Model not trained. Training first...")
        result = engine.train(n_samples=6000)
        print(f"✅ Training complete. Accuracy: {result['accuracy']}%")
    
    print(f"📊 Model loaded: {len(engine.diseases)} diseases, {engine.accuracy:.2%} accuracy")
    
    # Test cases with expected predictions based on medical knowledge
    test_cases = [
        {
            "name": "Classic COVID-19",
            "symptoms": {
                "description": "fever, dry cough, loss of taste and smell, fatigue, body aches",
                "severity": 6, "duration_hours": 72, "temperature": 38.5, "age": 35, "gender": 1,
                "fever": True, "dry_cough": True, "fatigue": True, "loss_of_taste": True, "loss_of_smell": True
            },
            "expected": ["COVID-19", "Influenza", "Common Cold"]
        },
        {
            "name": "Meningitis Emergency",
            "symptoms": {
                "description": "severe headache, stiff neck, high fever, nausea, confusion, photophobia",
                "severity": 9, "duration_hours": 12, "temperature": 39.8, "age": 22, "gender": 0,
                "severe_headache": True, "stiff_neck": True, "high_fever": True, "nausea": True, "confusion": True
            },
            "expected": ["Meningitis", "Encephalitis", "Subarachnoid Hemorrhage"]
        },
        {
            "name": "Heart Attack",
            "symptoms": {
                "description": "chest pain, shortness of breath, sweating, nausea, left arm pain",
                "severity": 10, "duration_hours": 2, "temperature": 37.0, "age": 55, "gender": 1,
                "chest_pain": True, "shortness_of_breath": True, "sweating": True, "nausea": True
            },
            "expected": ["Heart Attack", "Angina", "Pulmonary Embolism"]
        },
        {
            "name": "Appendicitis",
            "symptoms": {
                "description": "abdominal pain, nausea, vomiting, loss of appetite, fever",
                "severity": 8, "duration_hours": 24, "temperature": 38.2, "age": 28, "gender": 0,
                "abdominal_pain": True, "nausea": True, "vomiting": True, "loss_of_appetite": True, "fever": True
            },
            "expected": ["Appendicitis", "Gastroenteritis", "Pancreatitis"]
        },
        {
            "name": "Allergic Rhinitis",
            "symptoms": {
                "description": "runny nose, sneezing, itchy eyes, nasal congestion, watery eyes",
                "severity": 2, "duration_hours": 168, "temperature": 36.5, "age": 30, "gender": 1,
                "runny_nose": True, "sneezing": True, "itching": True, "nasal_congestion": True
            },
            "expected": ["Allergic Rhinitis", "Common Cold", "Sinusitis"]
        },
        {
            "name": "Pneumonia",
            "symptoms": {
                "description": "high fever, productive cough, chest pain, shortness of breath, fatigue",
                "severity": 8, "duration_hours": 96, "temperature": 39.5, "age": 65, "gender": 0,
                "high_fever": True, "productive_cough": True, "chest_pain": True, "shortness_of_breath": True, "fatigue": True
            },
            "expected": ["Pneumonia", "Bronchitis", "COVID-19"]
        },
        {
            "name": "Migraine",
            "symptoms": {
                "description": "severe headache, nausea, sensitivity to light, sensitivity to sound",
                "severity": 7, "duration_hours": 12, "temperature": 36.8, "age": 35, "gender": 1,
                "severe_headache": True, "nausea": True, "dizziness": True
            },
            "expected": ["Migraine", "Tension Headache", "Cluster Headache"]
        },
        {
            "name": "Food Poisoning",
            "symptoms": {
                "description": "diarrhea, vomiting, stomach pain, nausea, mild fever",
                "severity": 6, "duration_hours": 8, "temperature": 38.0, "age": 25, "gender": 0,
                "diarrhea": True, "vomiting": True, "abdominal_pain": True, "nausea": True, "fever": True
            },
            "expected": ["Food Poisoning", "Gastroenteritis", "Viral Gastroenteritis"]
        },
        {
            "name": "Diabetes Emergency",
            "symptoms": {
                "description": "excessive thirst, frequent urination, fatigue, blurred vision, weight loss",
                "severity": 7, "duration_hours": 168, "temperature": 37.0, "age": 45, "gender": 1,
                "fatigue": True, "blurred_vision": True, "frequent_urination": True, "weight_loss": True
            },
            "expected": ["Diabetes", "Diabetic Ketoacidosis", "Hyperglycemia"]
        },
        {
            "name": "Kidney Stones",
            "symptoms": {
                "description": "severe back pain, blood in urine, nausea, vomiting, fever",
                "severity": 9, "duration_hours": 6, "temperature": 38.5, "age": 40, "gender": 0,
                "back_pain": True, "blood_in_urine": True, "nausea": True, "vomiting": True, "fever": True
            },
            "expected": ["Kidney Stones", "UTI", "Pyelonephritis"]
        }
    ]
    
    correct_predictions = 0
    total_tests = len(test_cases)
    
    print("\n🔍 Running prediction tests...")
    print("-" * 80)
    
    for i, test_case in enumerate(test_cases, 1):
        try:
            result = engine.predict(test_case["symptoms"])
            predictions = result["predictions"]
            top_prediction = predictions[0]
            top_disease = top_prediction["disease"]
            confidence = top_prediction["confidence"]
            risk_level = result["risk_assessment"]["risk_level"]
            
            # Check if prediction is in expected list
            is_correct = top_disease in test_case["expected"]
            if is_correct:
                correct_predictions += 1
                status = "✅"
            else:
                status = "❌"
            
            print(f"{status} Test {i}: {test_case['name']}")
            print(f"   Predicted: {top_disease} ({confidence}%)")
            print(f"   Expected: {', '.join(test_case['expected'])}")
            print(f"   Risk: {risk_level}")
            
            if len(predictions) > 1:
                print(f"   2nd: {predictions[1]['disease']} ({predictions[1]['confidence']}%)")
            
            print()
            
        except Exception as e:
            print(f"❌ Test {i}: {test_case['name']} - ERROR: {e}")
            print()
    
    accuracy = (correct_predictions / total_tests) * 100
    print("=" * 80)
    print(f"📊 ACCURACY RESULTS")
    print("=" * 80)
    print(f"Correct Predictions: {correct_predictions}/{total_tests}")
    print(f"Accuracy: {accuracy:.1f}%")
    
    if accuracy >= 80:
        print("🎉 EXCELLENT: Model accuracy is very good!")
    elif accuracy >= 70:
        print("✅ GOOD: Model accuracy is acceptable")
    elif accuracy >= 60:
        print("⚠️ FAIR: Model accuracy needs improvement")
    else:
        print("❌ POOR: Model accuracy needs significant improvement")
    
    return accuracy

if __name__ == "__main__":
    test_ml_accuracy()
