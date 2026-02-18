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
        self.tfidf_vectorizer = TfidfVectorizer(max_features=150, stop_words='english')
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
        
        # Enhanced symptom keywords with condition-specific identifiers
        symptom_keywords = [
            # COVID-19 specific
            'covid-19', 'covid', 'coronavirus', 'sars-cov-2', 'loss of taste', 'loss of smell', 
            'anosmia', 'ageusia', 'taste loss', 'smell loss',
            # Influenza specific
            'influenza', 'flu', 'seasonal flu', 'body aches', 'muscle pain', 'chills', 'malaise',
            # Pneumonia specific
            'pneumonia', 'lung infection', 'chest infection', 'productive cough', 'crackles', 
            'consolidation', 'dyspnea',
            # Gastroenteritis specific
            'gastroenteritis', 'stomach flu', 'gi infection', 'vomiting', 'diarrhea', 
            'watery diarrhea', 'stomach cramps', 'dehydration',
            # Migraine specific
            'migraine', 'migraine headache', 'unilateral headache', 'throbbing pain', 
            'photophobia', 'phonophobia', 'aura', 'light sensitivity', 'sound sensitivity',
            # Tension Headache specific
            'tension headache', 'stress headache', 'bilateral headache', 'pressure sensation',
            'band-like', 'neck pain', 'scalp tenderness',
            # UTI specific
            'uti', 'urinary tract infection', 'urinary infection', 'dysuria', 'painful urination',
            'burning urination', 'frequency', 'urgency', 'suprapubic pain', 'hematuria',
            # Anxiety specific
            'anxiety', 'anxiety disorder', 'panic attack', 'palpitations', 'heart racing',
            'nervousness', 'restlessness', 'trembling',
            # General symptoms
            'fever', 'high fever', 'cough', 'dry cough', 'chest pain', 'shortness of breath',
            'abdominal pain', 'nausea', 'headache', 'fatigue', 'sore throat', 'wheezing',
            'joint pain', 'back pain', 'rash', 'itching', 'swelling', 'dizziness', 'confusion'
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
            return {'duration_days': 0, 'is_acute': 1, 'is_chronic': 0, 'is_subacute': 0}
        
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
            return np.zeros(100)  # Default vector size
        
        # Combine symptoms and description
        symptom_text = ' '.join(symptoms)
        if description:
            symptom_text += ' ' + description
        
        # Create TF-IDF features
        try:
            if self.is_fitted:
                vector = self.tfidf_vectorizer.transform([symptom_text]).toarray()[0]
            else:
                # For training, we'll fit later - but ensure consistent size
                vector = np.zeros(100)  # Placeholder matching vectorizer max_features
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
        
        # Calculate medical similarity features
        medical_similarity = self.calculate_medical_similarity(all_symptoms)
        
        # Combine all features
        all_features = {**features, **medical_similarity}
        
        # Convert to arrays
        feature_array = np.array(list(all_features.values()))
        symptom_array = symptom_vector
        
        return {
            'features': feature_array,
            'symptom_vector': symptom_array,
            'symptoms': all_symptoms,
            'raw_features': features,
            'medical_similarity': medical_similarity
        }
    
    def prepare_training_data(self, cases: List[Dict[str, Any]]) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Prepare batch of cases for ML training"""
        processed_cases = []
        labels = []
        symptom_texts = []
        
        # First pass: collect all symptom texts and process basic features
        for case in cases:
            processed = self.process_single_case(case['symptoms'])
            
            # Store symptom text for TF-IDF fitting
            text_symptoms = self.extract_symptoms_from_text(case['symptoms'].get('description', ''))
            checkbox_symptoms = [k.replace('has_', '').replace('_', ' ') 
                                for k, v in case['symptoms'].items() 
                                if k.startswith('has_') and v]
            all_symptoms = list(set(text_symptoms + checkbox_symptoms + case['symptoms'].get('symptoms', [])))
            symptom_text = ' '.join(all_symptoms) + ' ' + case['symptoms'].get('description', '')
            symptom_texts.append(symptom_text)
            
            # Store basic features (without symptom vector for now)
            processed_cases.append(processed['features'])
            labels.append(case['diagnosis'])
        
        # Fit TF-IDF vectorizer on all symptom texts
        if not self.is_fitted:
            self.tfidf_vectorizer.fit(symptom_texts)
            self.symptom_encoder.fit(labels)
            self.is_fitted = True
        
        # Create symptom vectors with fitted vectorizer
        symptom_vectors = self.tfidf_vectorizer.transform(symptom_texts).toarray()
        
        # Combine basic features with symptom vectors
        X = np.hstack([np.array(processed_cases), symptom_vectors])
        y = np.array(labels)
        y_encoded = self.symptom_encoder.transform(y)
        
        return X, y_encoded, labels
    
    def calculate_medical_similarity(self, symptoms: List[str]) -> Dict[str, float]:
        """Calculate medical similarity scores for key conditions"""
        # Medical condition keyword patterns
        condition_patterns = {
            'COVID-19': ['covid', 'coronavirus', 'sars-cov-2', 'loss of taste', 'loss of smell', 'anosmia', 'dry cough', 'shortness of breath', 'fever', 'fatigue'],
            'Influenza': ['influenza', 'flu', 'sudden onset', 'muscle aches', 'body aches', 'chills', 'high fever', 'malaise', 'headache', 'fatigue'],
            'Pneumonia': ['pneumonia', 'lung infection', 'productive cough', 'chest pain', 'shortness of breath', 'difficulty breathing', 'fever', 'chills'],
            'Gastroenteritis': ['gastroenteritis', 'stomach flu', 'diarrhea', 'vomiting', 'nausea', 'watery diarrhea', 'abdominal cramps'],
            'Migraine': ['migraine', 'unilateral', 'throbbing', 'photophobia', 'phonophobia', 'aura', 'light sensitivity', 'nausea'],
            'Tension Headache': ['tension headache', 'bilateral', 'pressure', 'band-like', 'stress headache', 'neck pain', 'mild'],
            'Urinary Tract Infection': ['uti', 'burning urination', 'frequency', 'urgency', 'dysuria', 'pelvic pain', 'cloudy urine'],
            'Anxiety Disorder': ['anxiety', 'panic attack', 'palpitations', 'heart racing', 'nervousness', 'restlessness', 'fear', 'sweating']
        }
        
        similarity_scores = {}
        symptom_text = ' '.join(symptoms).lower()
        
        for condition, keywords in condition_patterns.items():
            matches = sum(1 for keyword in keywords if keyword in symptom_text)
            similarity_scores[f'medical_sim_{condition}'] = matches / len(keywords)
        
        return similarity_scores

    def get_feature_names(self) -> List[str]:
        """Get names of all features for interpretability"""
        base_features = [
            'num_symptoms', 'severity_score', 'complexity_score', 'temperature',
            'duration_days', 'is_acute', 'is_chronic', 'is_subacute',
            'age_normalized', 'is_male', 'is_female', 'is_other'
        ]
        
        # Return actual TF-IDF feature count, not theoretical max
        if self.is_fitted and hasattr(self.tfidf_vectorizer, 'vocabulary_'):
            actual_tfidf_features = len(self.tfidf_vectorizer.vocabulary_)
        else:
            actual_tfidf_features = 150  # Default for unfitted state
        
        symptom_features = [f'symptom_tfidf_{i}' for i in range(actual_tfidf_features)]
        
        # Add medical similarity features
        medical_similarity_features = [
            'medical_sim_COVID-19', 'medical_sim_Influenza', 'medical_sim_Pneumonia',
            'medical_sim_Gastroenteritis', 'medical_sim_Migraine', 'medical_sim_Tension Headache',
            'medical_sim_Urinary Tract Infection', 'medical_sim_Anxiety Disorder'
        ]
        
        return base_features + symptom_features + medical_similarity_features
