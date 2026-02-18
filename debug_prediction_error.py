#!/usr/bin/env python3
"""
Debug the prediction error: '>=' not supported between instances of 'str' and 'int'
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from ml_system.prediction_engine import MedicalPredictionEngine
import traceback

async def main():
    print("🔍 DEBUGGING PREDICTION ERROR")
    print("=" * 50)
    
    engine = MedicalPredictionEngine()
    
    # Simple test case
    symptoms = {
        'description': 'covid-19 loss of taste',
        'severity': 'moderate',
        'temperature': 38.0,
        'duration_hours': 72,
        'age': 35,
        'gender': 'male'
    }
    
    try:
        result = await engine.predict_disease(symptoms)
        print(f"✅ Prediction successful: {result}")
    except Exception as e:
        print(f"❌ Prediction failed: {e}")
        print("\nFull traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
