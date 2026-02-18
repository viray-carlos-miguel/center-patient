#!/usr/bin/env python3
"""
Debug Feature Extraction
Find the exact mismatch between training and prediction feature extraction
"""
import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

from ml_system.data_processor import MedicalDataProcessor
import numpy as np

def debug_feature_extraction():
    """Debug feature extraction to find mismatches"""
    print('🔍 DEBUGGING FEATURE EXTRACTION')
    print('=' * 60)
    
    processor = MedicalDataProcessor()
    
    # Test case data
    test_symptoms = {
        'description': 'covid-19 patient reports loss of taste, loss of smell, fever',
        'temperature': 38.5,
        'duration_hours': 120,
        'severity': 6,
        'age': 35,
        'gender': 'male',
        'has_fever': True,
        'has_cough': True,
        'has_headache': False,
        'has_nausea': False,
        'has_fatigue': True,
        'has_chest_pain': False,
        'has_shortness_of_breath': False,
        'has_abdominal_pain': False,
        'symptoms': ['covid-19', 'loss of taste', 'loss of smell', 'fever']
    }
    
    print('📊 Input Symptoms:')
    for key, value in test_symptoms.items():
        print(f'   {key}: {value}')
    print()
    
    # Process the case
    processed = processor.process_single_case(test_symptoms)
    
    print('🔧 Processed Features:')
    print(f'   Features shape: {processed["features"].shape}')
    print(f'   Symptom vector shape: {processed["symptom_vector"].shape}')
    print(f'   Combined shape: {np.concatenate([processed["features"], processed["symptom_vector"]]).shape}')
    print()
    
    print('📋 Feature Values:')
    feature_names = processor.get_feature_names()
    combined_features = np.concatenate([processed["features"], processed["symptom_vector"]])
    
    print('   Base Features:')
    base_features = processed["features"]
    base_feature_names = feature_names[:len(base_features)]
    for i, (name, value) in enumerate(zip(base_feature_names, base_features)):
        print(f'     {i:2d}: {name:20s} = {value:8.4f}')
    
    print(f'   Symptom Features (first 20):')
    symptom_features = processed["symptom_vector"]
    symptom_feature_names = feature_names[len(base_features):len(base_features)+20]
    for i, (name, value) in enumerate(zip(symptom_feature_names, symptom_features[:20])):
        print(f'     {i+len(base_features):2d}: {name:20s} = {value:8.4f}')
    
    print()
    print('🧪 Extracted Symptoms from Text:')
    text_symptoms = processor.extract_symptoms_from_text(test_symptoms['description'])
    print(f'   Found: {text_symptoms}')
    
    print()
    print('🔍 Checkbox Symptoms:')
    checkbox_symptoms = [k.replace('has_', '').replace('_', ' ') 
                        for k, v in test_symptoms.items() 
                        if k.startswith('has_') and v]
    print(f'   Found: {checkbox_symptoms}')
    
    print()
    print('📝 All Symptoms Combined:')
    all_symptoms = list(set(text_symptoms + checkbox_symptoms + test_symptoms.get('symptoms', [])))
    print(f'   Combined: {all_symptoms}')
    print(f'   Count: {len(all_symptoms)}')
    
    print()
    print('🎯 Key Insights:')
    print(f'   • Total features: {len(combined_features)}')
    print(f'   • Base features: {len(base_features)}')
    print(f'   • Symptom features: {len(symptom_features)}')
    print(f'   • Non-zero symptom features: {np.count_nonzero(symptom_features)}')
    print(f'   • Symptom vector sum: {np.sum(symptom_features):.4f}')
    
    return processed

if __name__ == '__main__':
    debug_feature_extraction()
