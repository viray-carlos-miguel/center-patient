#!/usr/bin/env python3
"""
Debug TF-IDF persistence: verify that the fitted vectorizer is actually saved and restored
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from ml_system.prediction_engine import MedicalPredictionEngine
import numpy as np

def main():
    print("🔍 DEBUGGING TF-IDF PERSISTENCE")
    print("=" * 50)
    
    # Create engine (this should load model and restore data processor)
    engine = MedicalPredictionEngine()
    
    print(f"Engine initialized: {engine.is_initialized}")
    print(f"Data processor fitted: {engine.data_processor.is_fitted}")
    
    if engine.data_processor.is_fitted:
        print(f"TF-IDF vocabulary size: {len(engine.data_processor.tfidf_vectorizer.vocabulary_)}")
        print(f"Label encoder classes: {list(engine.data_processor.symptom_encoder.classes_)}")
        
        # Test a simple case
        test_symptoms = {
            'description': 'fever cough loss of taste',
            'severity': 'moderate',
            'temperature': 38.5
        }
        
        # Check what the symptom vector looks like
        processed = engine.data_processor.process_single_case(test_symptoms)
        print(f"Base features shape: {processed['features'].shape}")
        print(f"Symptom vector from process_single_case: {processed['symptom_vector'][:5]}... (sum={np.sum(processed['symptom_vector'])})")
        
        # Now test the prediction path
        import asyncio
        result = asyncio.run(engine.predict_disease(test_symptoms))
        print(f"Prediction: {result['predicted_condition']} ({result['confidence']:.1%})")
        
        # Check if TF-IDF is actually being used in prediction
        text_symptoms = engine.data_processor.extract_symptoms_from_text(test_symptoms.get('description', ''))
        symptom_text = ' '.join(text_symptoms) + ' ' + test_symptoms.get('description', '')
        print(f"Symptom text for TF-IDF: '{symptom_text}'")
        
        if engine.data_processor.is_fitted:
            tfidf_vector = engine.data_processor.tfidf_vectorizer.transform([symptom_text]).toarray()[0]
            print(f"Direct TF-IDF vector: {tfidf_vector[:5]}... (sum={np.sum(tfidf_vector)})")
    else:
        print("❌ Data processor is NOT fitted - TF-IDF persistence failed!")

if __name__ == "__main__":
    main()
