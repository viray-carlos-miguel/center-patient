"""
Medical ML Data Processor
Handles symptom data preprocessing and feature engineering
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
import re
from datetime import datetime

class MedicalDataProcessor:
    """Processes medical symptom data for ML training"""
    
    def __init__(self):
        self.symptom_encoder = LabelEncoder()
        self.severity_scaler = StandardScaler()
        self.tfidf_vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
        self.age_scaler = StandardScaler()
        self.is_fitted = False
        
        # Symptom severity mapping
        self.severity_mapping = {
            'mild': 1, 'low': 1, 'slight': 1,
            'moderate': 2, 'medium': 2, 'average': 2,
            'severe': 3, 'high': 3, 'intense': 3,
            'very severe': 4, 'extreme': 4, 'critical': 4
        }
        
        # Body system mapping
        self.body_systems = {
            'headache': 'nervous', 'dizziness': 'nervous', 'confusion': 'nervous',
            'chest pain': 'cardiovascular', 'palpitations': 'cardiovascular', 'shortness of breath': 'respiratory',
            'abdominal pain': 'digestive', 'nausea': 'digestive', 'vomiting': 'digestive',
            'fever': 'systemic', 'fatigue': 'systemic', 'weight loss': 'systemic',
            'cough': 'respiratory', 'sore throat': 'respiratory', 'wheezing': 'respiratory',
            'joint pain': 'musculoskeletal', 'muscle pain': 'musculoskeletal', 'back pain': 'musculoskeletal',
            'rash': 'integumentary', 'itching': 'integumentary', 'swelling': 'integumentary'
        }
    
    def extract_symptoms_from_text(self, text: str) -> List[str]:
        """Extract individual symptoms from descriptive text"""
        if not text:
            return []
        
        # Common symptom keywords (CDC/Mayo Clinic validated)
        symptom_keywords = [
            # Gastrointestinal
            'nausea', 'vomiting', 'diarrhea', 'watery diarrhea', 'stomach cramps', 'abdominal pain',
            # Respiratory
            'cough', 'chest pain', 'chest pain when breathing', 'shortness of breath', 'dyspnea',
            'productive cough', 'sore throat', 'wheezing',
            # Neurological
            'headache', 'migraine', 'dizziness', 'confusion', 'light sensitivity', 'sound sensitivity',
            # General
            'fever', 'high fever', 'fatigue', 'body aches', 'chills', 'muscle pain',
            # Urinary
            'painful urination', 'frequent urination', 'burning sensation', 'suprapubic pain',
            # Mental Health
            'anxiety', 'palpitations', 'restlessness',
            # Other
            'back pain', 'joint pain', 'rash', 'itching', 'swelling', 'numbness', 'tingling'
        ]
        
        found_symptoms = []
        text_lower = text.lower()
        
        for symptom in symptom_keywords:
            if symptom in text_lower:
                found_symptoms.append(symptom)
        
        return found_symptoms
    
    def normalize_severity(self, severity_input: Any) -> float:
        """Normalize severity to 0-1 scale"""
        if severity_input is None:
            return 0.5
        
        if isinstance(severity_input, (int, float)):
            # If it's already numeric (1-10 scale)
            return min(max(severity_input / 10.0, 0), 1)
        
        if isinstance(severity_input, str):
            severity_lower = severity_input.lower()
            return self.severity_mapping.get(severity_lower, 2) / 4.0
        
        return 0.5
    
    def calculate_symptom_complexity_score(self, symptoms: List[str]) -> float:
        """Calculate complexity based on number and diversity of symptoms"""
        if not symptoms:
            return 0.0
        
        # Count symptoms per body system
        system_count = {}
        for symptom in symptoms:
            system = self.body_systems.get(symptom, 'other')
            system_count[system] = system_count.get(system, 0) + 1
        
        # Complexity score: more systems involved = higher complexity
        num_systems = len(system_count)
        num_symptoms = len(symptoms)
        
        complexity = (num_systems * 0.6 + np.log1p(num_symptoms) * 0.4) / 5.0
        return min(complexity, 1.0)
    
    def extract_temporal_features(self, duration_hours: float) -> Dict[str, float]:
        """Extract temporal features from symptom duration"""
        if duration_hours is None:
            return {'duration_days': 0, 'is_acute': 1, 'is_chronic': 0}
        
        duration_days = duration_hours / 24.0
        is_acute = 1.0 if duration_days <= 7 else 0.0
        is_chronic = 1.0 if duration_days >= 30 else 0.0
        is_subacute = 1.0 if 7 < duration_days < 30 else 0.0
        
        return {
            'duration_days': np.log1p(duration_days),
            'is_acute': is_acute,
            'is_chronic': is_chronic,
            'is_subacute': is_subacute
        }
    
    def process_patient_demographics(self, age: int, gender: str) -> Dict[str, float]:
        """Process patient demographic features"""
        age_normalized = (age - 50) / 30.0  # Normalize around age 50
        
        gender_features = {
            'is_male': 1.0 if gender.lower() == 'male' else 0.0,
            'is_female': 1.0 if gender.lower() == 'female' else 0.0,
            'is_other': 1.0 if gender.lower() not in ['male', 'female'] else 0.0
        }
        
        return {
            'age_normalized': age_normalized,
            **gender_features
        }
    
    def create_symptom_vector(self, symptoms: List[str], description: str = None) -> np.ndarray:
        """Create numerical vector from symptoms"""
        if not symptoms and not description:
            return np.zeros(50)  # Default vector size
        
        # Combine symptoms and description
        symptom_text = ' '.join(symptoms)
        if description:
            symptom_text += ' ' + description
        
        # Create TF-IDF features
        try:
            if self.is_fitted:
                vector = self.tfidf_vectorizer.transform([symptom_text]).toarray()[0]
            else:
                # For training, we'll fit later
                vector = np.zeros(100)  # Placeholder
        except:
            vector = np.zeros(100)
        
        return vector
    
    def process_single_case(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single medical case for ML input"""
        # Extract symptoms
        text_symptoms = self.extract_symptoms_from_text(case_data.get('description', ''))
        checkbox_symptoms = [k.replace('has_', '').replace('_', ' ') 
                            for k, v in case_data.items() 
                            if k.startswith('has_') and v]
        all_symptoms = list(set(text_symptoms + checkbox_symptoms))
        
        # Process basic features
        severity = self.normalize_severity(case_data.get('severity'))
        complexity = self.calculate_symptom_complexity_score(all_symptoms)
        temporal_features = self.extract_temporal_features(case_data.get('duration_hours'))
        
        # Process demographics
        demographics = self.process_patient_demographics(
            case_data.get('age', 30),
            case_data.get('gender', 'unknown')
        )
        
        # Create symptom vector
        symptom_vector = self.create_symptom_vector(all_symptoms, case_data.get('description'))
        
        # Combine all features
        features = {
            'num_symptoms': len(all_symptoms),
            'severity_score': severity,
            'complexity_score': complexity,
            'temperature': case_data.get('temperature', 37.0) / 40.0,  # Normalize
            **temporal_features,
            **demographics
        }
        
        # Convert to arrays
        feature_array = np.array(list(features.values()))
        symptom_array = symptom_vector
        
        return {
            'features': feature_array,
            'symptom_vector': symptom_array,
            'symptoms': all_symptoms,
            'raw_features': features
        }
    
    def prepare_training_data(self, cases: List[Dict[str, Any]]) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Prepare batch of cases for ML training"""
        processed_cases = []
        labels = []
        
        for case in cases:
            processed = self.process_single_case(case['symptoms'])
            
            # Combine features and symptom vector
            combined_features = np.concatenate([
                processed['features'],
                processed['symptom_vector']
            ])
            
            processed_cases.append(combined_features)
            labels.append(case['diagnosis'])
        
        X = np.array(processed_cases)
        y = np.array(labels)
        
        # Fit label encoder if not already fitted
        if not self.is_fitted:
            self.symptom_encoder.fit(y)
            y_encoded = self.symptom_encoder.transform(y)
            self.is_fitted = True
        else:
            y_encoded = self.symptom_encoder.transform(y)
        
        return X, y_encoded, labels
    
    def get_feature_names(self) -> List[str]:
        """Get names of all features for interpretability"""
        base_features = [
            'num_symptoms', 'severity_score', 'complexity_score', 'temperature',
            'duration_days', 'is_acute', 'is_chronic', 'is_subacute',
            'age_normalized', 'is_male', 'is_female', 'is_other'
        ]
        
        symptom_features = [f'symptom_tfidf_{i}' for i in range(100)]
        
        return base_features + symptom_features
