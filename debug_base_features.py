#!/usr/bin/env python3
"""
Debug base features: model expects 12 but process_single_case returns 11
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from ml_system.prediction_engine import MedicalPredictionEngine
import numpy as np

def main():
    print("🔍 DEBUGGING BASE FEATURES")
    print("=" * 50)
    
    engine = MedicalPredictionEngine()
    
    # Check what base features the model was trained with
    print(f"Model feature_names (first 15): {engine.model.feature_names[:15]}")
    
    # Count base vs TF-IDF features
    tfidf_features = [f for f in engine.model.feature_names if f.startswith('symptom_tfidf_')]
    base_features = [f for f in engine.model.feature_names if not f.startswith('symptom_tfidf_')]
    
    print(f"Model has {len(base_features)} base features: {base_features}")
    print(f"Model has {len(tfidf_features)} TF-IDF features")
    print(f"Total: {len(engine.model.feature_names)}")
    
    # Check what process_single_case returns
    test_symptoms = {
        'description': 'fever cough',
        'severity': 'moderate',
        'temperature': 38.5,
        'age': 30,
        'gender': 'male'
    }
    
    processed = engine.data_processor.process_single_case(test_symptoms)
    print(f"process_single_case returns {len(processed['features'])} features")
    print(f"Base feature values: {processed['features']}")
    print(f"Raw features dict keys: {list(processed['raw_features'].keys())}")
    
    # The issue: process_single_case is missing one base feature
    # Let me check what prepare_training_data does differently
    print(f"\n🔍 MISSING FEATURE ANALYSIS:")
    print(f"Model expects these base features: {base_features}")
    print(f"process_single_case provides: {list(processed['raw_features'].keys())}")
    
    # Find the missing feature
    model_base_set = set(base_features)
    provided_base_set = set(processed['raw_features'].keys())
    missing = model_base_set - provided_base_set
    extra = provided_base_set - model_base_set
    
    if missing:
        print(f"❌ Missing base feature: {list(missing)}")
    if extra:
        print(f"❌ Extra base feature: {list(extra)}")

if __name__ == "__main__":
    main()
