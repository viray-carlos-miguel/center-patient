#!/usr/bin/env python3
"""
Debug what's actually in the saved model file (correct path)
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import joblib

def main():
    print("🔍 DEBUGGING MODEL FILE CONTENTS (CORRECT PATH)")
    print("=" * 50)
    
    model_path = "backend/ml_system/models/medical_ensemble_model.pkl"
    
    if os.path.exists(model_path):
        print(f"✅ Model file exists: {model_path}")
        
        try:
            model_data = joblib.load(model_path)
            print(f"Keys in model file: {list(model_data.keys())}")
            
            if 'data_processor_state' in model_data:
                print("✅ data_processor_state found!")
                dp_state = model_data['data_processor_state']
                print(f"Data processor keys: {list(dp_state.keys())}")
                print(f"Is fitted flag: {dp_state['is_fitted']}")
                
                # Check TF-IDF
                tfidf = dp_state['tfidf_vectorizer']
                if hasattr(tfidf, 'vocabulary_') and tfidf.vocabulary_:
                    print(f"✅ TF-IDF vocabulary size: {len(tfidf.vocabulary_)}")
                else:
                    print("❌ TF-IDF vocabulary not fitted!")
                    
                # Check label encoder
                encoder = dp_state['symptom_encoder']
                if hasattr(encoder, 'classes_') and len(encoder.classes_) > 0:
                    print(f"✅ Label encoder classes: {list(encoder.classes_)}")
                else:
                    print("❌ Label encoder not fitted!")
            else:
                print("❌ data_processor_state NOT found in model file!")
                print("Available keys:", list(model_data.keys()))
                
        except Exception as e:
            print(f"❌ Error loading model file: {e}")
    else:
        print("❌ Model file does not exist!")

if __name__ == "__main__":
    main()
