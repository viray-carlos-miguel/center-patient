"""
ML System Setup Script
Initializes the ML prediction system
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from ml_system.prediction_engine import MedicalPredictionEngine
from ml_system.training_data import MedicalTrainingDataGenerator
from ml_system.data_processor import MedicalDataProcessor

async def setup_ml_system():
    """Setup the ML prediction system"""
    print("🚀 Setting up Medical ML Prediction System...")
    
    # Create necessary directories
    directories = [
        "backend/ml_system/data",
        "backend/ml_system/models",
        "backend/ml_system/logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  📁 Created directory: {directory}")
    
    # Initialize components
    print("  🔧 Initializing ML components...")
    prediction_engine = MedicalPredictionEngine()
    data_generator = MedicalTrainingDataGenerator()
    
    # Check if model is already trained
    if prediction_engine.is_initialized:
        print("  ✅ ML model already trained and ready")
        model_info = prediction_engine.get_model_info()
        print(f"     Model: {model_info.get('model_types', [])}")
        print(f"     Classes: {model_info.get('num_classes', 0)}")
        print(f"     Features: {model_info.get('num_features', 0)}")
    else:
        print("  🎓 Training new ML model...")
        
        # Generate training data
        training_data = data_generator.generate_training_cases(1000)
        
        # Train the model
        result = prediction_engine.train_from_database(training_data)
        
        if result['success']:
            print(f"  ✅ Model trained successfully!")
            print(f"     Accuracy: {result.get('accuracy', 0):.3f}")
            print(f"     Features: {result.get('num_features', 0)}")
            print(f"     Classes: {result.get('num_classes', 0)}")
        else:
            print(f"  ❌ Training failed: {result.get('message')}")
    
    # Save initial training data
    print("  💾 Saving initial training data...")
    data_generator.save_training_data(training_data, "initial_training_data.json")
    
    # Test prediction
    print("  🧪 Testing prediction system...")
    test_symptoms = {
        'description': 'I have a severe headache with fever and cough',
        'duration_hours': 48,
        'severity': 7,
        'temperature': 38.5,
        'has_fever': True,
        'has_cough': True,
        'has_headache': True
    }
    
    try:
        prediction = await prediction_engine.predict_disease(test_symptoms)
        print(f"  ✅ Test prediction successful!")
        print(f"     Predicted: {prediction.get('ml_prediction', {}).get('primary_condition', 'Unknown')}")
        print(f"     Confidence: {prediction.get('ml_prediction', {}).get('confidence', 0):.3f}")
    except Exception as e:
        print(f"  ⚠️ Test prediction failed: {e}")
    
    print("\n🎉 ML System Setup Complete!")
    print("📋 Next steps:")
    print("   1. Start the backend server")
    print("   2. Test ML predictions via API endpoints")
    print("   3. Train with real patient data for better accuracy")
    
    return prediction_engine

if __name__ == "__main__":
    asyncio.run(setup_ml_system())
