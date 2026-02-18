#!/usr/bin/env python3
"""
Debug the exact training flow to see where 60 features comes from
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from ml_system.prediction_engine import MedicalPredictionEngine
from ml_system.data_processor import MedicalDataProcessor
import numpy as np

def main():
    print("🔍 DEBUGGING TRAINING FLOW")
    print("=" * 50)
    
    # Create exactly what the training script creates
    engine = MedicalPredictionEngine()
    processor = MedicalDataProcessor()
    
    # Create a small sample of training data like the script does
    sample_training_data = [
        {
            'symptoms': {
                'description': 'fever dry cough loss of taste loss of smell',
                'temperature': 38.5,
                'duration_hours': 120,
                'severity': 6,
                'age': 30,
                'gender': 'male',
                'symptoms': ['fever', 'dry cough', 'loss of taste', 'loss of smell'],
                'has_fever': True,
                'has_cough': True,
                'has_headache': False,
                'has_nausea': False,
                'has_fatigue': False,
                'has_chest_pain': False,
                'has_shortness_of_breath': False,
                'has_abdominal_pain': False
            },
            'diagnosis': 'COVID-19'
        },
        {
            'symptoms': {
                'description': 'high fever body aches chills headache',
                'temperature': 39.2,
                'duration_hours': 72,
                'severity': 7,
                'age': 35,
                'gender': 'female',
                'symptoms': ['high fever', 'body aches', 'chills', 'headache'],
                'has_fever': True,
                'has_cough': False,
                'has_headache': True,
                'has_nausea': False,
                'has_fatigue': False,
                'has_chest_pain': False,
                'has_shortness_of_breath': False,
                'has_abdominal_pain': False
            },
            'diagnosis': 'Influenza'
        }
    ]
    
    print(f"Sample training data: {len(sample_training_data)} cases")
    
    # Step 1: Call prepare_training_data exactly like the engine does
    X, y, labels = processor.prepare_training_data(sample_training_data)
    print(f"prepare_training_data result:")
    print(f"  X shape: {X.shape}")
    print(f"  y shape: {y.shape}")
    print(f"  labels: {labels}")
    
    # Step 2: Get feature names
    feature_names = processor.get_feature_names()
    print(f"Feature names count: {len(feature_names)}")
    print(f"Feature names: {feature_names}")
    
    # Step 3: Check what the model would actually train on
    print(f"\n🔍 ANALYSIS:")
    print(f"Training data has {X.shape[1]} features")
    print(f"Feature names list has {len(feature_names)} items")
    print(f"Match: {X.shape[1] == len(feature_names)}")
    
    # The issue might be in how the model saves feature_names
    # Let me check what happens during model.save_model
    
    # Check the base features vs TF-IDF features
    print(f"\n🔍 FEATURE BREAKDOWN:")
    base_feature_count = 12  # Based on data_processor.get_feature_names
    tfidf_feature_count = 100  # Based on data_processor.get_feature_names
    expected_total = base_feature_count + tfidf_feature_count
    print(f"Expected: {base_feature_count} base + {tfidf_feature_count} TF-IDF = {expected_total}")
    print(f"Actual: {X.shape[1]}")
    
    # Check if TF-IDF actually has 48 or 100 features
    print(f"TF-IDF max_features: {processor.tfidf_vectorizer.max_features}")
    print(f"TF-IDF actual vocabulary size: {len(processor.tfidf_vectorizer.vocabulary_)}")
    
    # The actual TF-IDF matrix should have 48 features, not 100
    # So the total should be 12 + 48 = 60, which matches what the model expects!
    actual_tfidf_features = len(processor.tfidf_vectorizer.vocabulary_)
    actual_total = base_feature_count + actual_tfidf_features
    print(f"Actual should be: {base_feature_count} base + {actual_tfidf_features} TF-IDF = {actual_total}")

if __name__ == "__main__":
    main()
