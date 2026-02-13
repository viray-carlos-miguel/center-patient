"""
Medical Knowledge Base
Provides medical domain knowledge to enhance ML predictions
"""

from typing import Dict, List, Any, Optional
import json

class MedicalKnowledgeBase:
    """Medical knowledge base for disease prediction enhancement"""
    
    def __init__(self):
        self.condition_database = self._initialize_condition_database()
        self.symptom_database = self._initialize_symptom_database()
        self.risk_factors = self._initialize_risk_factors()
    
    def _initialize_condition_database(self) -> Dict[str, Dict[str, Any]]:
        """Initialize comprehensive medical condition database"""
        return {
            'Influenza': {
                'description': 'Viral respiratory infection causing fever, cough, and body aches',
                'risk_level': 'medium',
                'common_symptoms': ['fever', 'cough', 'headache', 'fatigue', 'muscle pain'],
                'key_symptoms': ['fever', 'cough', 'sudden onset'],
                'diagnostic_tests': ['Rapid influenza test', 'Complete blood count', 'Chest X-ray'],
                'treatment_options': ['Antiviral medications', 'Supportive care', 'Rest and hydration'],
                'warning_signs': ['High fever >103°F', 'Difficulty breathing', 'Chest pain', 'Confusion'],
                'specialist_referral': 'Pulmonologist if severe',
                'recovery_time': '1-2 weeks',
                'contagious': True
            },
            'COVID-19': {
                'description': 'Coronavirus infection affecting respiratory system and multiple organs',
                'risk_level': 'high',
                'common_symptoms': ['fever', 'cough', 'fatigue', 'loss of taste', 'loss of smell', 'shortness of breath'],
                'key_symptoms': ['fever', 'cough', 'loss of taste/smell'],
                'diagnostic_tests': ['PCR test', 'Antigen test', 'CT scan', 'Blood work'],
                'treatment_options': ['Antiviral therapy', 'Supportive care', 'Oxygen therapy', 'Monoclonal antibodies'],
                'warning_signs': ['Severe shortness of breath', 'Chest pain', 'Confusion', 'Bluish lips'],
                'specialist_referral': 'Infectious disease specialist',
                'recovery_time': '2-6 weeks',
                'contagious': True
            },
            'Pneumonia': {
                'description': 'Infection of the lungs causing inflammation and fluid buildup',
                'risk_level': 'high',
                'common_symptoms': ['cough', 'fever', 'chest pain', 'shortness of breath', 'fatigue'],
                'key_symptoms': ['productive cough', 'fever', 'chest pain'],
                'diagnostic_tests': ['Chest X-ray', 'CT scan', 'Blood cultures', 'Sputum culture'],
                'treatment_options': ['Antibiotics', 'Antivirals', 'Oxygen therapy', 'Chest physiotherapy'],
                'warning_signs': ['Severe chest pain', 'High fever', 'Confusion', 'Rapid breathing'],
                'specialist_referral': 'Pulmonologist',
                'recovery_time': '1-4 weeks',
                'contagious': False
            },
            'Migraine': {
                'description': 'Neurological condition causing severe headaches and sensory disturbances',
                'risk_level': 'low',
                'common_symptoms': ['headache', 'nausea', 'light sensitivity', 'sound sensitivity', 'visual aura'],
                'key_symptoms': ['severe headache', 'light sensitivity', 'nausea'],
                'diagnostic_tests': ['Neurological examination', 'MRI if atypical', 'CT scan if needed'],
                'treatment_options': ['Triptans', 'Preventive medications', 'Lifestyle modifications', 'Biofeedback'],
                'warning_signs': ['Sudden severe headache', 'Fever with headache', 'Neurological deficits'],
                'specialist_referral': 'Neurologist',
                'recovery_time': 'Hours to days',
                'contagious': False
            },
            'Tension Headache': {
                'description': 'Most common type of headache characterized by dull pain and pressure',
                'risk_level': 'low',
                'common_symptoms': ['headache', 'neck pain', 'scalp tenderness', 'stress'],
                'key_symptoms': ['bilateral headache', 'pressure sensation', 'stress related'],
                'diagnostic_tests': ['Physical examination', 'Neurological exam'],
                'treatment_options': ['Over-the-counter pain relievers', 'Stress management', 'Physical therapy'],
                'warning_signs': ['Sudden severe headache', 'Headache with fever', 'Vision changes'],
                'specialist_referral': 'Primary care',
                'recovery_time': 'Hours to days',
                'contagious': False
            },
            'Gastroenteritis': {
                'description': 'Inflammation of the stomach and intestines causing vomiting and diarrhea',
                'risk_level': 'medium',
                'common_symptoms': ['nausea', 'vomiting', 'diarrhea', 'abdominal pain', 'fever'],
                'key_symptoms': ['vomiting', 'diarrhea', 'abdominal cramps'],
                'diagnostic_tests': ['Stool sample', 'Blood tests', 'Hydration assessment'],
                'treatment_options': ['Oral rehydration', 'Anti-nausea medications', 'Rest', 'Dietary modifications'],
                'warning_signs': ['Severe dehydration', 'High fever', 'Bloody diarrhea', 'Severe abdominal pain'],
                'specialist_referral': 'Gastroenterologist if severe',
                'recovery_time': '1-3 days',
                'contagious': True
            },
            'Urinary Tract Infection': {
                'description': 'Infection of the urinary system causing painful urination',
                'risk_level': 'medium',
                'common_symptoms': ['painful urination', 'frequent urination', 'abdominal pain', 'fever'],
                'key_symptoms': ['painful urination', 'urgency', 'frequency'],
                'diagnostic_tests': ['Urinalysis', 'Urine culture', 'Ultrasound if complicated'],
                'treatment_options': ['Antibiotics', 'Pain relievers', 'Increased fluid intake'],
                'warning_signs': ['High fever', 'Back pain', 'Blood in urine', 'Confusion in elderly'],
                'specialist_referral': 'Urologist if recurrent',
                'recovery_time': '3-7 days',
                'contagious': False
            },
            'Appendicitis': {
                'description': 'Inflammation of the appendix requiring surgical intervention',
                'risk_level': 'high',
                'common_symptoms': ['abdominal pain', 'nausea', 'vomiting', 'fever', 'loss of appetite'],
                'key_symptoms': ['right lower quadrant pain', 'rebound tenderness', 'fever'],
                'diagnostic_tests': ['CT scan', 'Ultrasound', 'Blood tests', 'Physical examination'],
                'treatment_options': ['Surgical removal', 'Antibiotics', 'Pain management'],
                'warning_signs': ['Severe abdominal pain', 'High fever', 'Ruptured appendix signs'],
                'specialist_referral': 'Surgeon',
                'recovery_time': '2-4 weeks',
                'contagious': False
            },
            'Hypertension': {
                'description': 'High blood pressure increasing risk of cardiovascular disease',
                'risk_level': 'high',
                'common_symptoms': ['headache', 'dizziness', 'vision changes', 'chest pain'],
                'key_symptoms': ['elevated blood pressure', 'headache', 'vision changes'],
                'diagnostic_tests': ['Blood pressure measurement', 'Blood tests', 'ECG', 'Echocardiogram'],
                'treatment_options': ['Antihypertensive medications', 'Lifestyle changes', 'Dietary modifications'],
                'warning_signs': ['Severe headache', 'Chest pain', 'Shortness of breath', 'Vision loss'],
                'specialist_referral': 'Cardiologist',
                'recovery_time': 'Chronic management',
                'contagious': False
            },
            'Diabetes Type 2': {
                'description': 'Metabolic disorder causing high blood sugar levels',
                'risk_level': 'medium',
                'common_symptoms': ['fatigue', 'increased thirst', 'frequent urination', 'weight loss'],
                'key_symptoms': ['increased thirst', 'frequent urination', 'fatigue'],
                'diagnostic_tests': ['Blood glucose test', 'HbA1c test', 'Oral glucose tolerance test'],
                'treatment_options': ['Oral medications', 'Insulin therapy', 'Diet and exercise', 'Blood sugar monitoring'],
                'warning_signs': ['Very high blood sugar', 'Ketones in urine', 'Frequent infections'],
                'specialist_referral': 'Endocrinologist',
                'recovery_time': 'Chronic management',
                'contagious': False
            },
            'Anxiety Disorder': {
                'description': 'Mental health condition characterized by excessive worry and fear',
                'risk_level': 'low',
                'common_symptoms': ['anxiety', 'palpitations', 'shortness of breath', 'dizziness', 'fatigue'],
                'key_symptoms': ['excessive worry', 'physical symptoms', 'avoidance behavior'],
                'diagnostic_tests': ['Psychological evaluation', 'Physical exam to rule out other causes'],
                'treatment_options': ['Psychotherapy', 'Medications', 'Stress management', 'Lifestyle changes'],
                'warning_signs': ['Suicidal thoughts', 'Severe panic attacks', 'Depression'],
                'specialist_referral': 'Psychiatrist or Psychologist',
                'recovery_time': 'Months to years',
                'contagious': False
            },
            'Depression': {
                'description': 'Mood disorder causing persistent sadness and loss of interest',
                'risk_level': 'medium',
                'common_symptoms': ['fatigue', 'sadness', 'loss of interest', 'sleep changes', 'appetite changes'],
                'key_symptoms': ['persistent sadness', 'loss of interest', 'fatigue'],
                'diagnostic_tests': ['Psychological evaluation', 'Blood tests to rule out other causes'],
                'treatment_options': ['Antidepressants', 'Psychotherapy', 'Lifestyle changes', 'Support groups'],
                'warning_signs': ['Suicidal thoughts', 'Severe functional impairment', 'Psychosis'],
                'specialist_referral': 'Psychiatrist',
                'recovery_time': 'Months to years',
                'contagious': False
            }
        }
    
    def _initialize_symptom_database(self) -> Dict[str, Dict[str, Any]]:
        """Initialize symptom database with importance ratings"""
        return {
            'chest pain': {
                'description': 'Pain or discomfort in the chest area',
                'urgency': 'high',
                'associated_conditions': ['Heart attack', 'Pneumonia', 'Pulmonary embolism', 'Anxiety'],
                'body_system': 'cardiovascular',
                'red_flag': True
            },
            'shortness of breath': {
                'description': 'Difficulty breathing or feeling of not getting enough air',
                'urgency': 'high',
                'associated_conditions': ['Asthma', 'Heart failure', 'Pneumonia', 'Anxiety'],
                'body_system': 'respiratory',
                'red_flag': True
            },
            'fever': {
                'description': 'Elevated body temperature above normal range',
                'urgency': 'medium',
                'associated_conditions': ['Influenza', 'COVID-19', 'Pneumonia', 'UTI'],
                'body_system': 'systemic',
                'red_flag': False
            },
            'headache': {
                'description': 'Pain in the head or neck region',
                'urgency': 'low',
                'associated_conditions': ['Migraine', 'Tension headache', 'Hypertension', 'Meningitis'],
                'body_system': 'nervous',
                'red_flag': False
            },
            'abdominal pain': {
                'description': 'Pain in the abdominal area',
                'urgency': 'medium',
                'associated_conditions': ['Appendicitis', 'Gastroenteritis', 'Kidney stones', 'Pancreatitis'],
                'body_system': 'digestive',
                'red_flag': False
            },
            'nausea': {
                'description': 'Feeling of sickness with an inclination to vomit',
                'urgency': 'low',
                'associated_conditions': ['Gastroenteritis', 'Migraine', 'Pregnancy', 'Food poisoning'],
                'body_system': 'digestive',
                'red_flag': False
            },
            'fatigue': {
                'description': 'Feeling of tiredness or lack of energy',
                'urgency': 'low',
                'associated_conditions': ['Anemia', 'Depression', 'Diabetes', 'Hypothyroidism'],
                'body_system': 'systemic',
                'red_flag': False
            },
            'cough': {
                'description': 'Forceful expulsion of air from the lungs',
                'urgency': 'low',
                'associated_conditions': ['Influenza', 'COVID-19', 'Pneumonia', 'Asthma'],
                'body_system': 'respiratory',
                'red_flag': False
            },
            'dizziness': {
                'description': 'Feeling of lightheadedness or unsteadiness',
                'urgency': 'medium',
                'associated_conditions': ['Anemia', 'Hypotension', 'Vertigo', 'Heart conditions'],
                'body_system': 'nervous',
                'red_flag': False
            },
            'palpitations': {
                'description': 'Awareness of heartbeat or feeling of irregular heartbeat',
                'urgency': 'medium',
                'associated_conditions': ['Anxiety', 'Arrhythmia', 'Hyperthyroidism', 'Heart disease'],
                'body_system': 'cardiovascular',
                'red_flag': False
            }
        }
    
    def _initialize_risk_factors(self) -> Dict[str, List[str]]:
        """Initialize risk factor database"""
        return {
            'cardiovascular': ['age > 65', 'smoking', 'hypertension', 'diabetes', 'obesity', 'family history'],
            'respiratory': ['smoking', 'asthma', 'COPD', 'allergies', 'pollution exposure'],
            'digestive': ['alcohol use', 'spicy foods', 'stress', 'medications', 'infections'],
            'neurological': ['age > 50', 'head trauma', 'family history', 'stress', 'sleep deprivation'],
            'systemic': ['autoimmune disease', 'immunocompromised', 'travel history', 'exposure to sick people']
        }
    
    def get_condition_info(self, condition: str) -> Dict[str, Any]:
        """Get detailed information about a medical condition"""
        return self.condition_database.get(condition, {
            'description': 'Condition information not available',
            'risk_level': 'unknown',
            'common_symptoms': [],
            'warning_signs': ['Seek medical evaluation']
        })
    
    def get_symptom_importance(self, symptom: str, condition: str) -> float:
        """Calculate importance score of a symptom for a specific condition"""
        condition_info = self.condition_database.get(condition, {})
        symptom_info = self.symptom_database.get(symptom, {})
        
        # Base importance from symptom urgency
        urgency_scores = {'high': 0.9, 'medium': 0.6, 'low': 0.3}
        base_importance = urgency_scores.get(symptom_info.get('urgency', 'low'), 0.5)
        
        # Boost if symptom is key for the condition
        key_symptoms = condition_info.get('key_symptoms', [])
        if symptom in key_symptoms:
            base_importance += 0.3
        
        # Boost if it's a red flag symptom
        if symptom_info.get('red_flag', False):
            base_importance += 0.2
        
        return min(base_importance, 1.0)
    
    def get_symptom_description(self, symptom: str) -> str:
        """Get description of a symptom"""
        symptom_info = self.symptom_database.get(symptom, {})
        return symptom_info.get('description', f'Symptom: {symptom}')
    
    def get_differential_diagnosis(self, symptoms: List[str], primary_condition: str) -> List[Dict[str, Any]]:
        """Get differential diagnoses based on symptoms"""
        differentials = []
        
        # Find conditions that match the symptoms
        for condition, info in self.condition_database.items():
            if condition == primary_condition:
                continue
            
            # Calculate symptom overlap
            condition_symptoms = set(info.get('common_symptoms', []))
            patient_symptoms = set(symptoms)
            
            overlap = len(condition_symptoms.intersection(patient_symptoms))
            if overlap > 0:
                confidence = overlap / len(condition_symptoms)
                
                differentials.append({
                    'condition': condition,
                    'confidence': confidence,
                    'matching_symptoms': list(condition_symptoms.intersection(patient_symptoms)),
                    'risk_level': info.get('risk_level', 'unknown')
                })
        
        # Sort by confidence and return top 5
        differentials.sort(key=lambda x: x['confidence'], reverse=True)
        return differentials[:5]
    
    def get_condition_risk(self, condition: str) -> str:
        """Get risk level for a condition"""
        condition_info = self.condition_database.get(condition, {})
        return condition_info.get('risk_level', 'medium')
    
    def get_condition_recommendations(self, condition: str) -> Dict[str, List[str]]:
        """Get treatment and diagnostic recommendations for a condition"""
        condition_info = self.condition_database.get(condition, {})
        
        return {
            'diagnostic_tests': condition_info.get('diagnostic_tests', ['Physical examination']),
            'treatment_options': condition_info.get('treatment_options', ['Symptomatic treatment']),
            'specialist_referral': [condition_info.get('specialist_referral', 'Primary care physician')],
            'lifestyle': ['Rest and hydration', 'Monitor symptoms']
        }
    
    def get_symptom_recommendations(self, symptoms: List[str]) -> Dict[str, List[str]]:
        """Get recommendations based on symptoms"""
        recommendations = {
            'diagnostic_tests': [],
            'lifestyle': [],
            'monitoring': []
        }
        
        for symptom in symptoms:
            symptom_info = self.symptom_database.get(symptom, {})
            urgency = symptom_info.get('urgency', 'low')
            
            if urgency == 'high':
                recommendations['diagnostic_tests'].append('Urgent medical evaluation')
            elif urgency == 'medium':
                recommendations['diagnostic_tests'].append('Medical evaluation recommended')
            
            recommendations['lifestyle'].append('Monitor symptom progression')
        
        return recommendations
    
    def get_condition_warning_signs(self, condition: str) -> List[str]:
        """Get warning signs for a specific condition"""
        condition_info = self.condition_database.get(condition, {})
        return condition_info.get('warning_signs', ['Seek medical attention if symptoms worsen'])
    
    def get_emergency_symptoms(self) -> List[str]:
        """Get list of emergency symptoms requiring immediate attention"""
        emergency_symptoms = []
        for symptom, info in self.symptom_database.items():
            if info.get('urgency') == 'high' or info.get('red_flag', False):
                emergency_symptoms.append(symptom)
        return emergency_symptoms
