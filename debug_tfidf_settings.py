#!/usr/bin/env python3
"""
Debug TF-IDF settings mismatch between training and prediction
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from ml_system.prediction_engine import MedicalPredictionEngine
import joblib

def main():
    print("🔍 DEBUGGING TF-IDF SETTINGS MISMATCH")
    print("=" * 50)
    
    # Load the model directly to check the saved TF-IDF
    model_path = "backend/ml_system/models/medical_ensemble_model.pkl"
    model_data = joblib.load(model_path)
    
    saved_tfidf = model_data['data_processor_state']['tfidf_vectorizer']
    print(f"Saved TF-IDF max_features: {saved_tfidf.max_features}")
    print(f"Saved TF-IDF vocabulary size: {len(saved_tfidf.vocabulary_)}")
    
    # Check current data processor
    engine = MedicalPredictionEngine()
    current_tfidf = engine.data_processor.tfidf_vectorizer
    print(f"Current TF-IDF max_features: {current_tfidf.max_features}")
    print(f"Current TF-IDF vocabulary size: {len(current_tfidf.vocabulary_) if current_tfidf.vocabulary_ else 0}")
    
    # The issue: saved TF-IDF has 48 features but model expects 100
    # This means the training script used a different max_features setting
    print("\n🔍 ANALYSIS:")
    print(f"- Model was trained with 100 TF-IDF features (12 base + 100 = 112 total)")
    print(f"- Saved TF-IDF only has 48 features in vocabulary")
    print(f"- This suggests training used max_features=100 but actual vocabulary was only 48")
    print(f"- But the model still expects 100 TF-IDF features!")
    
    # Check if we can reconstruct the full 100-feature vector
    if engine.data_processor.is_fitted:
        test_text = "fever cough loss of taste"
        vector = engine.data_processor.tfidf_vectorizer.transform([test_text]).toarray()[0]
        print(f"Current TF-IDF vector length: {len(vector)}")
        print(f"Expected TF-IDF vector length: 100")
        
        # Pad with zeros to match expected size
        if len(vector) < 100:
            padded = np.pad(vector, (0, 100 - len(vector)), 'constant')
            print(f"Padded vector length: {len(padded)}")

if __name__ == "__main__":
    main()
