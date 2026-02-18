#!/usr/bin/env python3
"""
Debug severity type issue in risk assessment
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from ml_system.prediction_engine import MedicalPredictionEngine
import traceback

async def main():
    print("🔍 DEBUGGING SEVERITY TYPE")
    print("=" * 50)
    
    engine = MedicalPredictionEngine()
    
    # Test with string severity
    symptoms = {
        'description': 'covid-19 loss of taste',
        'severity': 'moderate',  # This is a string
        'temperature': 38.0,
        'duration_hours': 72,
        'age': 35,
        'gender': 'male'
    }
    
    print(f"Symptoms dict: {symptoms}")
    print(f"Severity type: {type(symptoms['severity'])}")
    print(f"Severity value: {symptoms['severity']}")
    
    # Test the problematic comparison
    try:
        result = symptoms.get('severity', 5) >= 8
        print(f"Comparison result: {result}")
    except Exception as e:
        print(f"❌ Comparison failed: {e}")
        print(f"Type of severity: {type(symptoms.get('severity', 5))}")
    
    # Test with numeric severity
    symptoms['severity'] = 6  # Numeric
    print(f"\nWith numeric severity: {symptoms['severity']} (type: {type(symptoms['severity'])})")
    try:
        result = symptoms.get('severity', 5) >= 8
        print(f"Comparison result: {result}")
    except Exception as e:
        print(f"❌ Comparison failed: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
