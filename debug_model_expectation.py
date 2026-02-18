#!/usr/bin/env python3
"""
Debug what the model ACTUALLY expects vs what we think it expects
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from ml_system.prediction_engine import MedicalPredictionEngine
import numpy as np

def main():
    print("🔍 DEBUGGING MODEL FEATURE EXPECTATION")
    print("=" * 50)
    
    engine = MedicalPredictionEngine()
    
    # Check model info
    print(f"Model feature_names length: {len(engine.model.feature_names)}")
    print(f"Model class_names length: {len(engine.model.class_names)}")
    
    # Check the actual ensemble model
    ensemble = engine.model.ensemble
    print(f"Ensemble type: {type(ensemble)}")
    
    # Try to check the underlying models
    if hasattr(ensemble, 'named_estimators_'):
        rf = ensemble.named_estimators_['rf']
        print(f"RandomForest n_features_in_: {rf.n_features_in_}")
        print(f"RandomForest expects: {rf.n_features_in_} features")
    
    # Test our feature construction
    test_symptoms = {
        'description': 'fever cough loss of taste',
        'severity': 'moderate',
        'temperature': 38.5,
        'duration_hours': 72,
        'age': 30,
        'gender': 'male'
    }
    
    processed = engine.data_processor.process_single_case(test_symptoms)
    print(f"Base features: {len(processed['features'])}")
    
    # Build symptom text like predict_disease does
    text_symptoms = engine.data_processor.extract_symptoms_from_text(test_symptoms.get('description', ''))
    checkbox_symptoms = [k.replace('has_', '').replace('_', ' ')
                        for k, v in test_symptoms.items()
                        if k.startswith('has_') and v]
    all_symptoms = list(set(text_symptoms + checkbox_symptoms + test_symptoms.get('symptoms', [])))
    symptom_text = ' '.join(all_symptoms) + ' ' + test_symptoms.get('description', '')
    
    # Create TF-IDF vector (using fixed logic)
    if engine.data_processor.is_fitted:
        symptom_vector = engine.data_processor.tfidf_vectorizer.transform([symptom_text]).toarray()[0]
        print(f"TF-IDF vector length: {len(symptom_vector)}")
    else:
        symptom_vector = processed['symptom_vector']
        print(f"Using process_single_case symptom vector: {len(symptom_vector)}")
    
    # Total
    total_features = len(processed['features']) + len(symptom_vector)
    print(f"Total features we will send: {total_features}")
    
    # Try to predict and see the exact error
    try:
        X = np.concatenate([processed['features'], symptom_vector]).reshape(1, -1)
        print(f"Final X shape: {X.shape}")
        result = engine.model.predict(X)
        print(f"✅ Prediction successful: {result}")
    except Exception as e:
        print(f"❌ Prediction failed: {e}")

if __name__ == "__main__":
    main()
