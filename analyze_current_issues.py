#!/usr/bin/env python3
"""Analyze current ML system issues and create improvement plan"""
import requests
import json

def analyze_current_predictions():
    """Analyze current prediction patterns"""
    
    print('🔍 ANALYZING CURRENT ML SYSTEM ISSUES')
    print('=' * 60)
    
    # Test cases that are failing
    failing_cases = [
        {
            'name': 'Influenza',
            'symptoms': {
                'description': 'High fever, body aches, chills, headache, dry cough',
                'temperature': 39.2,
                'has_fever': True,
                'has_cough': True,
                'has_headache': True,
                'has_fatigue': True,
                'severity': 7,
                'duration_hours': 72
            },
            'expected': 'Influenza'
        },
        {
            'name': 'Pneumonia',
            'symptoms': {
                'description': 'Chest pain, productive cough, high fever, shortness of breath',
                'temperature': 39.8,
                'has_fever': True,
                'has_cough': True,
                'has_chest_pain': True,
                'has_shortness_of_breath': True,
                'severity': 9,
                'duration_hours': 168
            },
            'expected': 'Pneumonia'
        },
        {
            'name': 'Gastroenteritis',
            'symptoms': {
                'description': 'Nausea, vomiting, watery diarrhea, stomach cramps',
                'temperature': 38.0,
                'has_fever': True,
                'has_nausea': True,
                'has_abdominal_pain': True,
                'severity': 5,
                'duration_hours': 48
            },
            'expected': 'Gastroenteritis'
        },
        {
            'name': 'Migraine',
            'symptoms': {
                'description': 'Unilateral headache, throbbing pain, light sensitivity, sound sensitivity',
                'temperature': 36.8,
                'has_headache': True,
                'has_nausea': True,
                'severity': 8,
                'duration_hours': 24
            },
            'expected': 'Migraine'
        }
    ]
    
    print('Current Prediction Patterns:')
    for case in failing_cases:
        payload = {
            'symptoms': case['symptoms'],
            'patient_info': {'age': 35, 'gender': 'male'}
        }
        
        try:
            resp = requests.post('http://localhost:8000/api/ml/predict', json=payload)
            data = resp.json()
            ml = data['prediction']['ml_prediction']
            
            condition = ml['primary_condition']
            confidence = ml['confidence'] * 100
            
            status = '✅' if condition == case['expected'] else '❌'
            print(f'{status} {case["name"]}: {condition} ({confidence:.1f}%) - Expected: {case["expected"]}')
            
        except Exception as e:
            print(f'❌ {case["name"]}: Error - {e}')
    
    print()
    print('🔧 IDENTIFIED ISSUES:')
    print('1. Symptom overlap between conditions')
    print('2. Training data may not have distinctive patterns')
    print('3. Feature extraction needs improvement')
    print('4. Model weights may need adjustment')
    print()
    print('📋 IMPROVEMENT PLAN:')
    print('1. Create highly distinctive training data')
    print('2. Enhance symptom processing')
    print('3. Adjust ensemble weights')
    print('4. Increase training data volume')
    print('5. Add more specific symptom keywords')

if __name__ == '__main__':
    analyze_current_predictions()
