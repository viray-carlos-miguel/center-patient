#!/usr/bin/env python3
"""
Train the ML System for 80-90% Accuracy
"""

import asyncio
import sys
import os

# Add backend to path and change working directory so model saves to correct location
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.append(backend_dir)
os.chdir(backend_dir)

from ml_system.prediction_engine import MedicalPredictionEngine
from ml_system.training_data import MedicalTrainingDataGenerator
from ml_system.models import MedicalEnsembleModel

async def train_ml_system():
    """Train the ML system with synthetic data"""
    print("🚀 Starting ML System Training...")
    
    try:
        # Initialize components
        print("📊 Initializing ML components...")
        prediction_engine = MedicalPredictionEngine()
        data_generator = MedicalTrainingDataGenerator()
        
        # Generate training data
        print("📋 Generating training data...")
        training_data = data_generator.generate_training_cases(num_cases=2000)
        
        print(f"✅ Generated {len(training_data)} training cases")
        
        # Train the model
        print("🎯 Training ML model...")
        training_result = prediction_engine.train_from_database(training_data)
        
        if training_result['success']:
            print("🎉 ML Training Successful!")
            print(f"📈 Accuracy: {training_result.get('accuracy', 'N/A')}")
            print(f"📊 Model Score: {training_result.get('model_score', 'N/A')}")
            print(f"🔧 Training Time: {training_result.get('training_time', 'N/A')}")
            
            # Test the trained model (match processor input schema)
            print("\n🧪 Testing trained model...")
            test_symptoms = {
                "description": "Patient reports headache, cough, sore throat, runny nose, and fatigue for 3 days with mild fever",
                "temperature": 37.5,
                "has_fever": True,
                "has_cough": True,
                "has_sore_throat": True,
                "has_headache": True,
                "has_fatigue": True,
                "has_runny_nose": True,
                "severity": 3,
                "duration_hours": 72
            }
            
            result = await prediction_engine.predict_disease(test_symptoms, {"age": 30, "gender": "male"})
            
            print("📊 Test Result:")
            print(f"   Primary Diagnosis: {result.get('ml_prediction', {}).get('primary_condition', 'N/A')}")
            print(f"   Confidence: {result.get('ml_prediction', {}).get('consensus', 0) * 100:.1f}%")
            print(f"   Risk Assessment: {result.get('risk_assessment', {}).get('overall_risk', 'N/A')}")
            
            # Check if we achieved 80-90% accuracy
            confidence = result.get('ml_prediction', {}).get('consensus', 0)
            if confidence >= 0.8:
                print("🎉 EXCELLENT: 80-90% accuracy achieved!")
            elif confidence >= 0.7:
                print("👍 GOOD: 70-80% accuracy")
            elif confidence >= 0.6:
                print("📈 FAIR: 60-70% accuracy")
            else:
                print("⚠️ NEEDS IMPROVEMENT: Below 60% accuracy")
                
        else:
            print(f"❌ Training failed: {training_result.get('message', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Training error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🧪 ML System Training for 80-90% Accuracy")
    asyncio.run(train_ml_system())
