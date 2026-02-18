#!/usr/bin/env python3
"""
Debug what's actually in the saved model file
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import joblib

def main():
    print("🔍 DEBUGGING MODEL FILE CONTENTS")
    print("=" * 50)
    
    model_path = "ml_system/models/medical_ensemble_model.pkl"
    
    if os.path.exists(model_path):
        print(f"✅ Model file exists: {model_path}")
        
        try:
            model_data = joblib.load(model_path)
            print(f"Keys in model file: {list(model_data.keys())}")
            
            if 'data_processor_state' in model_data:
                print("✅ data_processor_state found!")
                dp_state = model_data['data_processor_state']
                print(f"Data processor keys: {list(dp_state.keys())}")
                print(f"TF-IDF fitted: {dp_state['tfidf_vectorizer'].vocabulary_ is not None}")
                print(f"Is fitted flag: {dp_state['is_fitted']}")
            else:
                print("❌ data_processor_state NOT found in model file!")
                print("Available keys:", list(model_data.keys()))
                
        except Exception as e:
            print(f"❌ Error loading model file: {e}")
    else:
        print("❌ Model file does not exist!")

if __name__ == "__main__":
    main()
