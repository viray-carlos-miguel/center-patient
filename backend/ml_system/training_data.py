"""
Training Data Generator and Manager
Creates synthetic medical cases for ML training when real data is limited
"""

import random
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
import numpy as np

class MedicalTrainingDataGenerator:
    """Generates realistic medical training cases for ML model training"""
    
    def __init__(self):
        self.medical_conditions = self._initialize_conditions()
        self.symptom_templates = self._initialize_symptom_templates()
        self.patient_demographics = self._initialize_demographics()
    
    def _initialize_conditions(self) -> Dict[str, Dict[str, Any]]:
        """Initialize medical conditions with symptom patterns"""
        return {
            'Influenza': {
                'base_symptoms': ['fever', 'cough', 'headache', 'fatigue', 'muscle pain'],
                'common_variations': ['sore throat', 'runny nose', 'chills', 'body aches'],
                'severity_range': (5, 8),
                'duration_range': (48, 168),  # 2-7 days
                'temperature_range': (37.5, 40.0),
                'age_groups': ['all'],
                'prevalence': 0.25
            },
            'COVID-19': {
                'base_symptoms': ['fever', 'cough', 'fatigue'],
                'common_variations': ['loss of taste', 'loss of smell', 'shortness of breath', 'sore throat'],
                'severity_range': (3, 9),
                'duration_range': (72, 336),  # 3-14 days
                'temperature_range': (37.0, 40.5),
                'age_groups': ['all'],
                'prevalence': 0.20
            },
            'Pneumonia': {
                'base_symptoms': ['chest pain', 'cough', 'fever', 'shortness of breath'],
                'common_variations': ['fatigue', 'nausea', 'vomiting', 'diarrhea', 'confusion'],
                'severity_range': (6, 10),
                'duration_range': (168, 672),  # 1-4 weeks
                'temperature_range': (38.0, 41.0),
                'age_groups': ['adult', 'elderly'],
                'prevalence': 0.15
            },
            'Migraine': {
                'base_symptoms': ['headache', 'nausea'],
                'common_variations': ['light sensitivity', 'sound sensitivity', 'visual aura', 'fatigue'],
                'severity_range': (7, 10),
                'duration_range': (4, 72),  # 4 hours - 3 days
                'temperature_range': (36.5, 37.5),
                'age_groups': ['adult'],
                'prevalence': 0.10
            },
            'Tension Headache': {
                'base_symptoms': ['headache'],
                'common_variations': ['neck pain', 'scalp tenderness', 'fatigue', 'stress'],
                'severity_range': (3, 7),
                'duration_range': (1, 48),  # 1 hour - 2 days
                'temperature_range': (36.5, 37.2),
                'age_groups': ['all'],
                'prevalence': 0.12
            },
            'Gastroenteritis': {
                'base_symptoms': ['nausea', 'vomiting', 'watery diarrhea', 'stomach cramps'],
                'common_variations': ['low-grade fever', 'muscle aches', 'headache', 'abdominal pain'],
                'severity_range': (3, 7),
                'duration_range': (24, 336),  # 1-14 days (per Mayo Clinic)
                'temperature_range': (37.0, 38.8),  # Low-grade fever per Mayo Clinic
                'age_groups': ['all'],
                'prevalence': 0.08
            },
            'Urinary Tract Infection': {
                'base_symptoms': ['painful urination', 'frequent urination'],
                'common_variations': ['abdominal pain', 'fever', 'fatigue', 'blood in urine'],
                'severity_range': (3, 7),
                'duration_range': (48, 336),  # 2-14 days
                'temperature_range': (36.5, 39.0),
                'age_groups': ['adult', 'elderly', 'female'],
                'prevalence': 0.06
            },
            'Anxiety Disorder': {
                'base_symptoms': ['anxiety', 'palpitations'],
                'common_variations': ['shortness of breath', 'dizziness', 'fatigue', 'sleep problems'],
                'severity_range': (4, 8),
                'duration_range': (168, 8760),  # 1 week - chronic
                'temperature_range': (36.5, 37.5),
                'age_groups': ['adult'],
                'prevalence': 0.04
            }
        }
    
    def _initialize_symptom_templates(self) -> Dict[str, List[str]]:
        """Initialize symptom description templates"""
        return {
            'headache': [
                'Sharp pain on the right side of head',
                'Dull aching pain across forehead',
                'Throbbing pain behind eyes',
                'Pressure-like pain at temples',
                'Stabbing pain in one spot'
            ],
            'fever': [
                'Feeling hot and sweaty',
                'Chills and body aches',
                'High temperature with fatigue',
                'Mild fever with headache',
                'Fever that comes and goes'
            ],
            'cough': [
                'Dry persistent cough',
                'Productive cough with yellow phlegm',
                'Wet cough with chest congestion',
                'Hacking cough that hurts chest',
                'Occasional light cough'
            ],
            'abdominal pain': [
                'Sharp pain in lower right abdomen',
                'Cramping pain in upper abdomen',
                'Dull ache in stomach area',
                'Burning pain in upper abdomen',
                'Colicky pain that comes in waves'
            ],
            'fatigue': [
                'Extreme exhaustion and weakness',
                'Mild tiredness throughout day',
                'Lack of energy for daily activities',
                'Overwhelming need to sleep',
                'General feeling of being run down'
            ]
        }
    
    def _initialize_demographics(self) -> Dict[str, Dict[str, Any]]:
        """Initialize patient demographic patterns"""
        return {
            'child': {'age_range': (5, 17), 'gender_distribution': {'male': 0.51, 'female': 0.49}},
            'adult': {'age_range': (18, 64), 'gender_distribution': {'male': 0.49, 'female': 0.51}},
            'elderly': {'age_range': (65, 90), 'gender_distribution': {'male': 0.47, 'female': 0.53}}
        }
    
    def generate_training_cases(self, num_cases: int = 1000) -> List[Dict[str, Any]]:
        """Generate synthetic medical training cases"""
        print(f"🏥 Generating {num_cases} synthetic medical cases...")
        
        cases = []
        
        for i in range(num_cases):
            # Select condition based on prevalence
            condition = self._select_condition_by_prevalence()
            case = self._generate_single_case(condition)
            cases.append(case)
        
        print(f"✅ Generated {len(cases)} training cases")
        return cases
    
    def _select_condition_by_prevalence(self) -> str:
        """Select a medical condition based on prevalence weights"""
        conditions = list(self.medical_conditions.keys())
        weights = [self.medical_conditions[cond]['prevalence'] for cond in conditions]
        
        return random.choices(conditions, weights=weights)[0]
    
    def _generate_single_case(self, condition: str) -> Dict[str, Any]:
        """Generate a single medical case"""
        condition_info = self.medical_conditions[condition]
        
        # Generate patient demographics
        age, gender = self._generate_demographics(condition_info['age_groups'])
        
        # Generate symptoms
        symptoms = self._generate_symptoms(condition, condition_info)
        
        # Generate clinical parameters
        severity = random.randint(*condition_info['severity_range'])
        duration = random.randint(*condition_info['duration_range'])
        temperature = random.uniform(*condition_info['temperature_range'])
        
        # Generate symptom description
        description = self._generate_symptom_description(symptoms)
        
        # Create case
        case = {
            'symptoms': {
                'description': description,
                'duration_hours': duration,
                'severity': severity,
                'temperature': temperature,
                'has_fever': 'fever' in symptoms or temperature >= 37.5,
                'has_cough': 'cough' in symptoms,
                'has_headache': 'headache' in symptoms,
                'has_nausea': 'nausea' in symptoms or 'vomiting' in symptoms,
                'has_fatigue': 'fatigue' in symptoms,
                'has_chest_pain': 'chest pain' in symptoms,
                'has_shortness_of_breath': 'shortness of breath' in symptoms,
                'has_abdominal_pain': 'abdominal pain' in symptoms,
                'symptoms': symptoms
            },
            'patient_info': {
                'age': age,
                'gender': gender,
                'has_chronic_conditions': random.random() < 0.3  # 30% have chronic conditions
            },
            'diagnosis': condition,
            'timestamp': datetime.now().isoformat(),
            'case_id': f"case_{random.randint(10000, 99999)}"
        }
        
        return case
    
    def _generate_demographics(self, age_groups: List[str]) -> tuple[int, str]:
        """Generate patient age and gender"""
        # Select age group
        if 'all' in age_groups:
            age_group = random.choice(['child', 'adult', 'elderly'])
        elif 'female' in age_groups:
            age_group = random.choice(['adult', 'elderly'])  # Female-specific conditions
        else:
            age_group = random.choice(age_groups)
        
        # Generate age within group range
        age_range = self.patient_demographics[age_group]['age_range']
        age = random.randint(*age_range)
        
        # Generate gender based on distribution
        gender_dist = self.patient_demographics[age_group]['gender_distribution']
        gender = random.choices(['male', 'female'], 
                              weights=[gender_dist['male'], gender_dist['female']])[0]
        
        return age, gender
    
    def _generate_symptoms(self, condition: str, condition_info: Dict[str, Any]) -> List[str]:
        """Generate symptom list for a condition"""
        base_symptoms = condition_info['base_symptoms'].copy()
        variations = condition_info['common_variations']
        
        # Always include base symptoms
        symptoms = base_symptoms
        
        # Add some variations (30-60% chance for each — less noise for cleaner boundaries)
        for variation in variations:
            if random.random() < random.uniform(0.3, 0.6):
                symptoms.append(variation)
        
        # Remove duplicates and shuffle
        symptoms = list(set(symptoms))
        random.shuffle(symptoms)
        
        # Ensure condition-specific dominant symptoms (CDC/Mayo Clinic validated)
        if condition == 'Influenza':
            symptoms.extend(['high fever', 'body aches', 'chills', 'respiratory symptoms'])
        elif condition == 'COVID-19':
            symptoms.extend(['loss of taste', 'loss of smell', 'dry cough', 'fever'])
        elif condition == 'Pneumonia':
            symptoms.extend(['chest pain', 'productive cough', 'high fever', 'shortness of breath'])
        elif condition == 'Migraine':
            symptoms.extend(['light sensitivity', 'sound sensitivity', 'visual aura', 'unilateral headache'])
        elif condition == 'Tension Headache':
            symptoms.extend(['neck pain', 'stress', 'bilateral headache', 'pressure sensation'])
        elif condition == 'Gastroenteritis':
            symptoms.extend(['watery diarrhea', 'stomach cramps', 'nausea', 'vomiting', 'low-grade fever'])
        elif condition == 'Urinary Tract Infection':
            symptoms.extend(['painful urination', 'frequent urination', 'burning sensation', 'suprapubic pain'])
        elif condition == 'Anxiety Disorder':
            symptoms.extend(['palpitations', 'anxiety', 'shortness of breath', 'dizziness', 'restlessness'])
        
        return list(set(symptoms))
    
    def _generate_symptom_description(self, symptoms: List[str]) -> str:
        """Generate natural language symptom description"""
        descriptions = []
        
        for symptom in symptoms:
            if symptom in self.symptom_templates:
                template = random.choice(self.symptom_templates[symptom])
                descriptions.append(template)
            else:
                # Generate generic description
                if symptom == 'fever':
                    descriptions.append(f"Feeling feverish with temperature")
                elif symptom == 'fatigue':
                    descriptions.append("Feeling very tired and weak")
                elif symptom == 'nausea':
                    descriptions.append("Feeling sick to stomach")
                else:
                    descriptions.append(f"Experiencing {symptom}")
        
        # Combine into natural description
        if len(descriptions) == 1:
            return descriptions[0]
        elif len(descriptions) == 2:
            return f"{descriptions[0]} and {descriptions[1]}"
        else:
            return f"{', '.join(descriptions[:-1])}, and {descriptions[-1]}"
    
    def save_training_data(self, cases: List[Dict[str, Any]], filename: str = None) -> str:
        """Save training data to file"""
        if filename is None:
            filename = f"medical_training_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = f"backend/ml_system/data/{filename}"
        
        with open(filepath, 'w') as f:
            json.dump(cases, f, indent=2, default=str)
        
        print(f"💾 Training data saved to {filepath}")
        return filepath
    
    def load_training_data(self, filepath: str) -> List[Dict[str, Any]]:
        """Load training data from file"""
        with open(filepath, 'r') as f:
            cases = json.load(f)
        
        print(f"📂 Loaded {len(cases)} training cases from {filepath}")
        return cases
    
    def augment_existing_data(self, existing_cases: List[Dict[str, Any]], 
                            augmentation_factor: int = 2) -> List[Dict[str, Any]]:
        """Augment existing training data with variations"""
        print(f"🔄 Augmenting {len(existing_cases)} cases by factor {augmentation_factor}...")
        
        augmented_cases = existing_cases.copy()
        
        for _ in range(augmentation_factor):
            for case in existing_cases:
                # Create variation of the case
                variation = self._create_case_variation(case)
                augmented_cases.append(variation)
        
        print(f"✅ Augmented to {len(augmented_cases)} total cases")
        return augmented_cases
    
    def _create_case_variation(self, original_case: Dict[str, Any]) -> Dict[str, Any]:
        """Create a variation of an existing case"""
        variation = {
            'symptoms': original_case['symptoms'].copy(),
            'patient_info': original_case['patient_info'].copy(),
            'diagnosis': original_case['diagnosis'],
            'timestamp': datetime.now().isoformat(),
            'case_id': f"case_{random.randint(10000, 99999)}_var"
        }
        
        # Vary severity slightly
        current_severity = variation['symptoms']['severity']
        variation['symptoms']['severity'] = max(1, min(10, 
            current_severity + random.randint(-2, 2)))
        
        # Vary duration slightly
        current_duration = variation['symptoms']['duration_hours']
        variation['symptoms']['duration_hours'] = max(1, 
            current_duration + random.randint(-24, 48))
        
        # Vary temperature slightly
        current_temp = variation['symptoms']['temperature']
        variation['symptoms']['temperature'] = max(35.0, min(42.0,
            current_temp + random.uniform(-1.0, 1.0)))
        
        # Occasionally add/remove a minor symptom
        if random.random() < 0.3:  # 30% chance
            symptoms = variation['symptoms']['symptoms']
            if len(symptoms) > 3 and random.random() < 0.5:
                # Remove a symptom
                symptoms.remove(random.choice(symptoms))
            else:
                # Add a common variation
                condition_info = self.medical_conditions[variation['diagnosis']]
                variations = condition_info['common_variations']
                if variations:
                    new_symptom = random.choice(variations)
                    if new_symptom not in symptoms:
                        symptoms.append(new_symptom)
        
        return variation
    
    def get_data_statistics(self, cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics about the training data"""
        if not cases:
            return {}
        
        # Condition distribution
        condition_counts = {}
        for case in cases:
            diagnosis = case['diagnosis']
            condition_counts[diagnosis] = condition_counts.get(diagnosis, 0) + 1
        
        # Age distribution
        ages = [case['patient_info']['age'] for case in cases]
        gender_counts = {'male': 0, 'female': 0}
        for case in cases:
            gender = case['patient_info']['gender']
            gender_counts[gender] += 1
        
        # Symptom statistics
        all_symptoms = []
        for case in cases:
            all_symptoms.extend(case['symptoms']['symptoms'])
        
        symptom_counts = {}
        for symptom in all_symptoms:
            symptom_counts[symptom] = symptom_counts.get(symptom, 0) + 1
        
        return {
            'total_cases': len(cases),
            'condition_distribution': condition_counts,
            'age_stats': {
                'mean': np.mean(ages),
                'min': min(ages),
                'max': max(ages),
                'std': np.std(ages)
            },
            'gender_distribution': gender_counts,
            'most_common_symptoms': sorted(symptom_counts.items(), 
                                         key=lambda x: x[1], reverse=True)[:10],
            'unique_conditions': len(condition_counts),
            'unique_symptoms': len(symptom_counts)
        }
