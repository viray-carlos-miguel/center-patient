#!/usr/bin/env python3
"""
Debug feature ordering in process_single_case
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from ml_system.data_processor import MedicalDataProcessor

def main():
    print("🔍 DEBUGGING FEATURE ORDERING")
    print("=" * 50)
    
    processor = MedicalDataProcessor()
    
    test_symptoms = {
        'description': 'fever cough',
        'severity': 'moderate',
        'temperature': 38.5,
        'duration_hours': 72,
        'age': 30,
        'gender': 'male'
    }
    
    processed = processor.process_single_case(test_symptoms)
    
    print(f"Raw features dict: {processed['raw_features']}")
    print(f"Raw features keys: {list(processed['raw_features'].keys())}")
    print(f"Raw features count: {len(processed['raw_features'])}")
    
    print(f"Feature array: {processed['features']}")
    print(f"Feature array length: {len(processed['features'])}")
    
    # Check if all expected keys are in raw_features
    expected_keys = [
        'num_symptoms', 'severity_score', 'complexity_score', 'temperature',
        'duration_days', 'is_acute', 'is_chronic', 'is_subacute',
        'age_normalized', 'is_male', 'is_female', 'is_other'
    ]
    
    print(f"\nExpected keys: {expected_keys}")
    print(f"Actual keys: {list(processed['raw_features'].keys())}")
    
    missing = set(expected_keys) - set(processed['raw_features'].keys())
    extra = set(processed['raw_features'].keys()) - set(expected_keys)
    
    if missing:
        print(f"❌ Missing keys: {list(missing)}")
    if extra:
        print(f"❌ Extra keys: {list(extra)}")
    
    # The issue might be that the dict order is different than expected
    # Let's check the actual order
    print(f"\nActual feature order:")
    for i, key in enumerate(processed['raw_features'].keys()):
        print(f"  {i}: {key}")

if __name__ == "__main__":
    main()
