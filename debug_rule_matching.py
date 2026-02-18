#!/usr/bin/env python3
"""
Debug rule-based matching to see why patterns aren't activating
"""
import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

from guaranteed_accuracy_solution import GuaranteedAccuracySystem

def debug_rule_matching():
    """Debug why rule patterns aren't matching"""
    print('🔍 DEBUGGING RULE-BASED MATCHING')
    print('=' * 50)
    
    system = GuaranteedAccuracySystem()
    
    # Test COVID-19 case
    covid_case = {
        'description': 'covid-19 loss of taste dry cough shortness of breath fever',
        'temperature': 38.5, 'severity': 7, 'age': 45, 'gender': 'male',
        'symptoms': ['loss of taste', 'dry cough', 'shortness of breath', 'fever']
    }
    
    print('🧪 Testing COVID-19 Rule Matching:')
    print(f'Description: {covid_case["description"]}')
    print(f'Symptoms: {covid_case["symptoms"]}')
    
    # Check rule-based diagnosis directly
    rule_result = system.rule_based_diagnosis(covid_case)
    print(f'Rule result: {rule_result}')
    
    # Check individual pattern matching
    description = covid_case.get('description', '').lower()
    symptom_list = covid_case.get('symptoms', [])
    all_text = description + ' ' + ' '.join(symptom_list).lower()
    
    print(f'All text for matching: {all_text}')
    
    # Check COVID-19 pattern specifically
    covid_pattern = system.definitive_patterns['COVID-19']
    print(f'COVID-19 pattern: {covid_pattern}')
    
    required_terms = covid_pattern['required_terms']
    any_terms = covid_pattern['any_terms']
    exclusions = covid_pattern['exclusions']
    
    print(f'Required terms: {required_terms}')
    print(f'Any terms: {any_terms}')
    print(f'Exclusions: {exclusions}')
    
    # Check required terms
    required_found = any(term in all_text for term in required_terms)
    print(f'Required terms found: {required_found}')
    
    if required_found:
        found_required = [term for term in required_terms if term in all_text]
        print(f'Found required terms: {found_required}')
    
    # Check any terms
    any_found = [term for term in any_terms if term in all_text]
    print(f'Any terms found: {any_found}')
    print(f'Any terms count: {len(any_found)}')
    
    # Check exclusions
    exclusion_found = [term for term in exclusions if term in all_text]
    print(f'Exclusion terms found: {exclusion_found}')
    
    # Calculate score manually
    score = 0.0
    if required_found:
        score += 0.4  # Base score for required terms
    
    # Add any terms score
    any_score = len(any_found) / len(any_terms) * 0.4
    score += any_score
    
    print(f'Manual score: {score}')
    print(f'Threshold: 0.2')
    print(f'Should match: {score >= 0.2}')
    
    print('\n🧪 Testing Influenza Rule Matching:')
    flu_case = {
        'description': 'influenza sudden onset muscle aches headache fever chills',
        'temperature': 39.0, 'severity': 8, 'age': 35, 'gender': 'female',
        'symptoms': ['sudden onset', 'muscle aches', 'headache', 'fever', 'chills']
    }
    
    flu_result = system.rule_based_diagnosis(flu_case)
    print(f'Flu rule result: {flu_result}')

if __name__ == "__main__":
    debug_rule_matching()
