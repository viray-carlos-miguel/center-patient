#!/usr/bin/env python3
"""
Debug feature mismatch: model expects 60 features but getting 59
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from ml_system.prediction_engine import MedicalPredictionEngine
import numpy as np

def main():
    print("🔍 DEBUGGING FEATURE MISMATCH")
    print("=" * 50)
    
    # Create engine 
    engine = MedicalPredictionEngine()
    
    print(f"Engine initialized: {engine.is_initialized}")
    print(f"Model feature count: {len(engine.model.feature_names)}")
    print(f"First few feature names: {engine.model.feature_names[:15]}")
    
    # Test a simple case
    test_symptoms = {
        'description': 'fever cough loss of taste',
        'severity': 'moderate',
        'temperature': 38.5,
        'age': 30,
        'gender': 'male'
    }
    
    # Check what process_single_case returns
    processed = engine.data_processor.process_single_case(test_symptoms)
    print(f"Base features from process_single_case: {len(processed['features'])}")
    print(f"Base feature values: {processed['features']}")
    
    # Show the raw features breakdown
    print(f"Raw features keys: {list(processed['raw_features'].keys())}")
    print(f"Medical similarity keys: {list(processed['medical_similarity'].keys())}")
    print(f"Raw features count: {len(processed['raw_features'])}")
    print(f"Medical similarity count: {len(processed['medical_similarity'])}")
    print(f"Expected base features: {len(processed['raw_features'])} + {len(processed['medical_similarity'])} = {len(processed['raw_features']) + len(processed['medical_similarity'])}")
    
    # Check what get_feature_names returns
    all_feature_names = engine.data_processor.get_feature_names()
    print(f"Data processor feature count: {len(all_feature_names)}")
    print(f"Data processor feature names: {all_feature_names}")
    
    # Check the symptom vector
    print(f"Symptom vector length: {len(processed['symptom_vector'])}")
    print(f"Symptom vector shape: {np.array(processed['symptom_vector']).shape}")
    
    # Check if there are any zero values in the symptom vector
    symptom_array = np.array(processed['symptom_vector'])
    non_zero_count = np.count_nonzero(symptom_array)
    print(f"Non-zero elements in symptom vector: {non_zero_count}")
    
    # Total features
    total_features = len(processed['features']) + len(processed['symptom_vector'])
    print(f"Total features we're sending: {total_features}")
    print(f"Model expects: {len(engine.model.feature_names)}")
    
    # Check if the issue is in feature combination
    print(f"Base features count: {len(processed['features'])}")
    print(f"Symptom vector count: {len(processed['symptom_vector'])}")
    print(f"Expected total: {len(processed['features'])} + {len(processed['symptom_vector'])} = {len(processed['features']) + len(processed['symptom_vector'])}")
    
    # Check which features are missing/extra
    if len(engine.model.feature_names) != total_features:
        print("❌ FEATURE MISMATCH DETECTED!")
        print(f"Model expects {len(engine.model.feature_names)} features")
        print(f"We're providing {total_features} features")
        
        # Show the difference
        model_set = set(engine.model.feature_names)
        our_set = set(all_feature_names)
        
        missing = model_set - our_set
        extra = our_set - model_set
        
        if missing:
            print(f"Missing features: {list(missing)}")
            print(f"Missing count: {len(missing)}")
        if extra:
            print(f"Extra features: {list(extra)}")
            print(f"Extra count: {len(extra)}")
            
        # Show last few features from both lists for comparison
        print(f"\nModel last 10 features: {list(engine.model.feature_names)[-10:]}")
        print(f"Our last 10 features: {list(all_feature_names)[-10:]}")
    else:
        print("✅ FEATURE MATCH SUCCESSFUL!")

if __name__ == "__main__":
    main()
