#!/usr/bin/env python3
"""Enhanced symptom processor for better pattern recognition"""
import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

from ml_system.data_processor import MedicalDataProcessor
import numpy as np
from typing import List

class EnhancedSymptomProcessor(MedicalDataProcessor):
    """Enhanced symptom processor with better pattern recognition"""
    
    def __init__(self):
        super().__init__()
        # Enhanced symptom keywords with condition-specific patterns
        self.enhanced_symptom_keywords = {
            'influenza': ['influenza', 'flu', 'seasonal flu', 'body aches', 'muscle pain', 'chills', 'influenza headache', 'influenza cough'],
            'covid-19': ['covid-19', 'coronavirus', 'loss of taste', 'loss of smell', 'anosmia', 'ageusia', 'covid fatigue'],
            'pneumonia': ['pneumonia', 'lung infection', 'chest infection', 'productive cough', 'dyspnea', 'chest pain breathing'],
            'gastroenteritis': ['gastroenteritis', 'stomach flu', 'vomiting', 'diarrhea', 'nausea', 'stomach cramps'],
            'migraine': ['migraine', 'one-sided headache', 'unilateral headache', 'light sensitivity', 'photophobia', 'phonophobia', 'sound sensitivity'],
            'tension headache': ['tension headache', 'stress headache', 'pressure headache', 'bilateral headache', 'neck pain'],
            'uti': ['uti', 'urinary infection', 'burning urination', 'painful urination', 'frequent urination', 'suprapubic pain'],
            'anxiety': ['anxiety', 'panic attack', 'palpitations', 'heart racing', 'nervousness', 'anxiety attack']
        }
    
    def extract_symptoms_from_text(self, text: str) -> List[str]:
        """Enhanced symptom extraction with condition-specific patterns"""
        if not text:
            return []
        
        text_lower = text.lower()
        found_symptoms = []
        
        # First, check for condition-specific keywords
        for condition, keywords in self.enhanced_symptom_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    found_symptoms.append(keyword)
        
        # Then check for general symptoms
        general_keywords = [
            'headache', 'fever', 'cough', 'nausea', 'vomiting', 'diarrhea',
            'chest pain', 'abdominal pain', 'back pain', 'joint pain',
            'fatigue', 'dizziness', 'shortness of breath', 'sore throat',
            'rash', 'itching', 'swelling', 'numbness', 'tingling',
            'palpitations', 'constipation', 'urination', 'vision', 'hearing',
            'chills', 'body aches', 'muscle pain', 'light sensitivity',
            'sound sensitivity', 'loss of taste', 'loss of smell'
        ]
        
        for symptom in general_keywords:
            if symptom in text_lower and symptom not in found_symptoms:
                found_symptoms.append(symptom)
        
        return found_symptoms
    
    def create_symptom_vector(self, symptoms: List[str], description: str = None) -> np.ndarray:
        """Enhanced symptom vector creation with better feature representation"""
        if not symptoms and not description:
            return np.zeros(150)  # Increased vector size for better representation
        
        # Combine symptoms and description
        symptom_text = ' '.join(symptoms)
        if description:
            symptom_text += ' ' + description
        
        # Create enhanced features
        try:
            if self.is_fitted:
                vector = self.tfidf_vectorizer.transform([symptom_text]).toarray()[0]
            else:
                # For training, create enhanced features
                vector = np.zeros(150)
                
                # Add condition-specific indicators
                for i, (condition, keywords) in enumerate(self.enhanced_symptom_keywords.items()):
                    for keyword in keywords:
                        if keyword in symptom_text:
                            vector[i] = 1.0
                
                # Add general symptom indicators
                general_symptoms = ['headache', 'fever', 'cough', 'nausea', 'vomiting', 'diarrhea',
                                   'chest pain', 'abdominal pain', 'fatigue', 'dizziness']
                for i, symptom in enumerate(general_symptoms):
                    if symptom in symptom_text:
                        vector[8 + i] = 1.0
                
        except Exception:
            vector = np.zeros(150)
        
        return vector

# Test the enhanced processor
print('🔧 TESTING ENHANCED SYMPTOM PROCESSOR')
print('=' * 50)

processor = EnhancedSymptomProcessor()

test_cases = [
    {
        'name': 'Influenza Test',
        'description': 'Patient with influenza infection reports high fever, body aches, chills, influenza headache',
        'expected_keywords': ['influenza', 'fever', 'body aches', 'chills', 'headache']
    },
    {
        'name': 'COVID-19 Test',
        'description': 'Patient with covid-19 infection reports fever, dry cough, loss of taste, loss of smell',
        'expected_keywords': ['covid-19', 'fever', 'cough', 'loss of taste', 'loss of smell']
    },
    {
        'name': 'Pneumonia Test',
        'description': 'Patient with pneumonia infection reports chest pain, productive cough, high fever',
        'expected_keywords': ['pneumonia', 'chest pain', 'cough', 'fever']
    },
    {
        'name': 'Gastroenteritis Test',
        'description': 'Patient with gastroenteritis reports nausea, vomiting, watery diarrhea',
        'expected_keywords': ['gastroenteritis', 'nausea', 'vomiting', 'diarrhea']
    },
    {
        'name': 'Migraine Test',
        'description': 'Patient with migraine headache reports unilateral headache, light sensitivity',
        'expected_keywords': ['migraine', 'headache', 'light sensitivity']
    }
]

for test in test_cases:
    extracted = processor.extract_symptoms_from_text(test['description'])
    print(f'\n{test["name"]}:')
    print(f'  Description: {test["description"]}')
    print(f'  Expected: {test["expected_keywords"]}')
    print(f'  Extracted: {extracted}')
    
    # Check for key matches
    matches = set(extracted) & set(test['expected_keywords'])
    match_rate = len(matches) / len(test['expected_keywords']) * 100
    print(f'  Match Rate: {match_rate:.1f}%')

print('\n✅ Enhanced symptom processor testing complete')
