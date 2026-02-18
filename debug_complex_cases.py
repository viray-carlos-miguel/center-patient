#!/usr/bin/env python3
"""
Debug complex cases to see why Hypertension and Diabetes patterns aren't activating
"""
import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

from guaranteed_accuracy_solution import GuaranteedAccuracySystem

def debug_complex_cases():
    """Debug complex cases pattern matching"""
    print('🔍 DEBUGGING COMPLEX CASES')
    print('=' * 50)
    
    system = GuaranteedAccuracySystem()
    
    # Test Hypertension case
    hypertension_case = {
        'description': 'hypertension high blood pressure headache dizziness no symptoms',
        'temperature': 36.9, 'severity': 3, 'age': 55, 'gender': 'male',
        'symptoms': ['high blood pressure', 'headache', 'dizziness', 'no symptoms']
    }
    
    print('🧪 Testing Hypertension Case:')
    print(f'Description: {hypertension_case["description"]}')
    print(f'Symptoms: {hypertension_case["symptoms"]}')
    
    rule_result = system.rule_based_diagnosis(hypertension_case)
    print(f'Rule result: {rule_result}')
    
    # Test Diabetes case
    diabetes_case = {
        'description': 'diabetes hypertension fatigue blurred vision frequent urination',
        'temperature': 37.1, 'severity': 6, 'age': 60, 'gender': 'female',
        'symptoms': ['diabetes', 'hypertension', 'fatigue', 'blurred vision', 'frequent urination']
    }
    
    print('\n🧪 Testing Diabetes Case:')
    print(f'Description: {diabetes_case["description"]}')
    print(f'Symptoms: {diabetes_case["symptoms"]}')
    
    diabetes_result = system.rule_based_diagnosis(diabetes_case)
    print(f'Diabetes rule result: {diabetes_result}')
    
    # Check pattern scores manually
    print('\n🔍 Manual Pattern Scoring for Hypertension:')
    description = hypertension_case.get('description', '').lower()
    symptom_list = hypertension_case.get('symptoms', [])
    all_text = description + ' ' + ' '.join(symptom_list).lower()
    
    print(f'All text: {all_text}')
    
    # Check each pattern
    for condition, pattern in system.definitive_patterns.items():
        required_terms = pattern['required_terms']
        any_terms = pattern['any_terms']
        exclusions = pattern['exclusions']
        
        required_found = any(term in all_text for term in required_terms)
        any_found = [term for term in any_terms if term in all_text]
        exclusion_found = [term for term in exclusions if term in all_text]
        
        # Use same scoring as actual rule system
        score = 0.0
        if required_found:
            score += 0.3  # Reduced from 0.5
        score += (len(any_found) / len(any_terms)) * 0.2  # Reduced from 0.3
        
        # Add severity adjustment (assuming medium severity = 0.05)
        if condition in ['COVID-19', 'Influenza', 'Pneumonia']:
            score += 0.05  # Medium severity
        elif condition in ['Gastroenteritis', 'Urinary Tract Infection']:
            score += 0.05  # Medium severity
        else:
            score += 0.05  # Default medium severity
        
        if exclusion_found:
            score -= 0.2
        
        print(f'{condition}: required={required_found}, any_found={len(any_found)}, exclusions={len(exclusion_found)}, score={score:.3f}')

if __name__ == "__main__":
    debug_complex_cases()
