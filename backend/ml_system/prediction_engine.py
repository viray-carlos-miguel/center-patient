"""
Medical ML Prediction Engine
Main interface for ML-based disease prediction
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from .data_processor import MedicalDataProcessor
from .models import MedicalEnsembleModel
from .medical_knowledge import MedicalKnowledgeBase
import asyncio
from datetime import datetime
import json

class MedicalPredictionEngine:
    """Main engine for medical disease prediction using ML"""
    
    def __init__(self):
        self.data_processor = MedicalDataProcessor()
        self.model = MedicalEnsembleModel()
        self.knowledge_base = MedicalKnowledgeBase()
        self.is_initialized = False
        
        # Load existing model if available
        self._initialize()
    
    def _initialize(self):
        """Initialize the prediction engine"""
        try:
            # Try to load existing model
            if self.model.load_model():
                self.is_initialized = True
                print("✅ Medical ML Engine initialized with existing model")
            else:
                print("🔧 Medical ML Engine ready for training")
                self.is_initialized = False
        except Exception as e:
            print(f"⚠️ ML Engine initialization warning: {e}")
            self.is_initialized = False
    
    def train_from_database(self, training_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Train the ML model from database cases"""
        print(f"🚀 Starting ML training with {len(training_data)} cases...")
        
        if len(training_data) < 50:
            return {
                'success': False,
                'message': f'Insufficient training data: {len(training_data)} cases (minimum 50 required)'
            }
        
        try:
            # Prepare training data
            X, y, labels = self.data_processor.prepare_training_data(training_data)
            
            # Get feature and class names
            feature_names = self.data_processor.get_feature_names()
            class_names = list(set(labels))
            
            # Train the model
            performance = self.model.train(X, y, feature_names, class_names)
            
            self.is_initialized = True
            
            return {
                'success': True,
                'message': f'Model trained successfully on {len(training_data)} cases',
                'performance': performance,
                'num_features': len(feature_names),
                'num_classes': len(class_names),
                'accuracy': performance['Ensemble']['accuracy_mean']
            }
            
        except Exception as e:
            print(f"❌ Training error: {e}")
            return {
                'success': False,
                'message': f'Training failed: {str(e)}'
            }
    
    async def predict_disease(self, symptoms: Dict[str, Any], patient_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Predict disease from symptoms using ML"""
        if not self.is_initialized:
            return self._fallback_prediction(symptoms)
        
        try:
            # Process the input symptoms
            processed = self.data_processor.process_single_case(symptoms)
            
            # Combine features
            X = np.concatenate([processed['features'], processed['symptom_vector']]).reshape(1, -1)
            
            # Make prediction
            prediction_result = self.model.predict(X)
            prediction = prediction_result['predictions'][0]
            
            # Get detailed explanation
            explanation = self.model.explain_prediction(X, 0)
            
            # Enhance with medical knowledge
            enhanced_result = await self._enhance_with_knowledge(prediction, explanation, symptoms, patient_info)
            
            return enhanced_result
            
        except Exception as e:
            print(f"❌ Prediction error: {e}")
            return self._fallback_prediction(symptoms)
    
    async def _enhance_with_knowledge(self, prediction: Dict[str, Any], explanation: Dict[str, Any], 
                                    symptoms: Dict[str, Any], patient_info: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Enhance ML prediction with medical knowledge base"""
        
        predicted_condition = prediction['predicted_class']
        confidence = prediction['confidence']
        
        # Get medical knowledge about the predicted condition
        condition_info = self.knowledge_base.get_condition_info(predicted_condition)
        
        # Get differential diagnoses
        differential_diagnoses = self.knowledge_base.get_differential_diagnosis(
            symptoms.get('symptoms', []), predicted_condition
        )
        
        # Risk assessment
        risk_assessment = self._comprehensive_risk_assessment(
            symptoms, patient_info, predicted_condition, confidence
        )
        
        # Recommendations
        recommendations = self._generate_recommendations(
            predicted_condition, symptoms, risk_assessment
        )
        
        # Build comprehensive result
        result = {
            'ml_prediction': {
                'primary_condition': predicted_condition,
                'confidence': confidence,
                'consensus': confidence,  # Use confidence as consensus for now
                'probability_breakdown': prediction['probabilities']
            },
            'medical_analysis': {
                'condition_info': condition_info,
                'differential_diagnoses': differential_diagnoses,
                'key_symptoms': self._identify_key_symptoms(symptoms, predicted_condition),
                'symptom_analysis': self._analyze_symptom_patterns(symptoms)
            },
            'risk_assessment': risk_assessment,
            'recommendations': recommendations,
            'explanation': {
                'top_contributing_factors': explanation.get('top_contributing_features', [])[:5],
                'model_confidence': explanation.get('confidence', confidence),
                'model_consensus': explanation.get('consensus', confidence),
                'prediction_risk': explanation.get('risk_assessment', 'medium')
            },
            'metadata': {
                'prediction_method': 'ensemble_ml',
                'model_version': '2.0',
                'timestamp': datetime.now().isoformat(),
                'requires_medical_review': confidence < 0.7
            }
        }
        
        return result
    
    def _identify_key_symptoms(self, symptoms: Dict[str, Any], predicted_condition: str) -> List[Dict[str, Any]]:
        """Identify the most important symptoms for the prediction"""
        symptom_list = symptoms.get('symptoms', [])
        
        key_symptoms = []
        for symptom in symptom_list:
            importance = self.knowledge_base.get_symptom_importance(symptom, predicted_condition)
            key_symptoms.append({
                'symptom': symptom,
                'importance': importance,
                'description': self.knowledge_base.get_symptom_description(symptom)
            })
        
        # Sort by importance
        key_symptoms.sort(key=lambda x: x['importance'], reverse=True)
        
        return key_symptoms[:5]  # Top 5 key symptoms
    
    def _analyze_symptom_patterns(self, symptoms: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze patterns in symptom presentation"""
        symptom_list = symptoms.get('symptoms', [])
        duration = symptoms.get('duration_hours', 0)
        severity = symptoms.get('severity', 5)
        
        # Pattern analysis
        patterns = {
            'acute_onset': duration < 48,
            'gradual_onset': 48 <= duration < 168,  # 2-7 days
            'chronic': duration >= 168,  # > 1 week
            'high_severity': severity >= 7,
            'multi_system': self._count_affected_systems(symptom_list) >= 2,
            'progressive': self._is_progressive_pattern(symptom_list, duration)
        }
        
        return {
            'patterns': patterns,
            'temporal_profile': self._get_temporal_profile(duration),
            'severity_profile': self._get_severity_profile(severity),
            'complexity_score': self.data_processor.calculate_symptom_complexity_score(symptom_list)
        }
    
    def _count_affected_systems(self, symptoms: List[str]) -> int:
        """Count how many body systems are affected"""
        systems = set()
        for symptom in symptoms:
            system = self.data_processor.body_systems.get(symptom, 'other')
            systems.add(system)
        return len(systems)
    
    def _is_progressive_pattern(self, symptoms: List[str], duration: float) -> bool:
        """Determine if symptoms suggest progressive condition"""
        progressive_symptoms = ['fatigue', 'weight loss', 'weakness', 'declining function']
        return any(symptom in symptoms for symptom in progressive_symptoms) and duration > 72
    
    def _get_temporal_profile(self, duration_hours: float) -> str:
        """Get temporal profile classification"""
        if duration_hours < 24:
            return 'hyperacute'
        elif duration_hours < 72:
            return 'acute'
        elif duration_hours < 168:
            return 'subacute'
        else:
            return 'chronic'
    
    def _get_severity_profile(self, severity: float) -> str:
        """Get severity profile classification"""
        if severity <= 3:
            return 'mild'
        elif severity <= 6:
            return 'moderate'
        elif severity <= 8:
            return 'severe'
        else:
            return 'critical'
    
    def _comprehensive_risk_assessment(self, symptoms: Dict[str, Any], patient_info: Optional[Dict[str, Any]], 
                                     predicted_condition: str, confidence: float) -> Dict[str, Any]:
        """Comprehensive risk assessment"""
        
        # Base risk from ML confidence
        ml_risk = 'low' if confidence >= 0.8 else 'medium' if confidence >= 0.6 else 'high'
        
        # Medical knowledge risk
        medical_risk = self.knowledge_base.get_condition_risk(predicted_condition)
        
        # Patient-specific risk factors
        patient_risk = self._assess_patient_risk_factors(patient_info, symptoms)
        
        # Symptom risk indicators
        symptom_risk = self._assess_symptom_risk(symptoms)
        
        # Overall risk calculation
        risk_scores = {'low': 1, 'medium': 2, 'high': 3}
        overall_score = (risk_scores[ml_risk] + risk_scores[medical_risk] + 
                        risk_scores[patient_risk] + risk_scores[symptom_risk]) / 4.0
        
        overall_risk = 'low' if overall_score <= 1.5 else 'medium' if overall_score <= 2.5 else 'high'
        
        return {
            'overall_risk': overall_risk,
            'risk_score': overall_score,
            'ml_confidence_risk': ml_risk,
            'medical_condition_risk': medical_risk,
            'patient_risk_factors': patient_risk,
            'symptom_risk_indicators': symptom_risk,
            'recommendation': self._get_risk_recommendation(overall_risk)
        }
    
    def _assess_patient_risk_factors(self, patient_info: Optional[Dict[str, Any]], symptoms: Dict[str, Any]) -> str:
        """Assess patient-specific risk factors"""
        if not patient_info:
            return 'low'
        
        risk_factors = 0
        
        # Age risk
        age = patient_info.get('age', 30)
        if age >= 65:
            risk_factors += 1
        elif age <= 5:
            risk_factors += 1
        
        # Chronic conditions
        if patient_info.get('has_chronic_conditions', False):
            risk_factors += 1
        
        # Symptom severity
        if symptoms.get('severity', 5) >= 8:
            risk_factors += 1
        
        # Temperature
        temp = symptoms.get('temperature', 37.0)
        if temp >= 39.0 or temp <= 35.0:
            risk_factors += 1
        
        if risk_factors >= 3:
            return 'high'
        elif risk_factors >= 2:
            return 'medium'
        else:
            return 'low'
    
    def _assess_symptom_risk(self, symptoms: Dict[str, Any]) -> str:
        """Assess risk based on symptom patterns"""
        high_risk_symptoms = ['chest pain', 'shortness of breath', 'severe headache', 'confusion']
        symptom_list = symptoms.get('symptoms', [])
        
        if any(symptom in symptom_list for symptom in high_risk_symptoms):
            return 'high'
        
        if symptoms.get('severity', 5) >= 8:
            return 'medium'
        
        return 'low'
    
    def _get_risk_recommendation(self, risk_level: str) -> str:
        """Get recommendation based on risk level"""
        recommendations = {
            'low': 'Monitor symptoms, seek care if worsens',
            'medium': 'Medical evaluation recommended within 24-48 hours',
            'high': 'Immediate medical evaluation recommended'
        }
        return recommendations.get(risk_level, 'Consult healthcare provider')
    
    def _generate_recommendations(self, predicted_condition: str, symptoms: Dict[str, Any], 
                               risk_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive recommendations"""
        
        # Get condition-specific recommendations
        condition_recs = self.knowledge_base.get_condition_recommendations(predicted_condition)
        
        # Get symptom-specific recommendations
        symptom_recs = self.knowledge_base.get_symptom_recommendations(symptoms.get('symptoms', []))
        
        # Risk-based recommendations
        risk_recs = self._get_risk_based_recommendations(risk_assessment['overall_risk'])
        
        return {
            'immediate_actions': risk_recs['immediate'],
            'diagnostic_tests': condition_recs.get('diagnostic_tests', []),
            'treatment_options': condition_recs.get('treatment_options', []),
            'lifestyle_recommendations': symptom_recs.get('lifestyle', []),
            'follow_up_care': risk_recs['follow_up'],
            'warning_signs': self._get_warning_signs(predicted_condition, symptoms),
            'emergency_indicators': self._get_emergency_indicators(symptoms)
        }
    
    def _get_risk_based_recommendations(self, risk_level: str) -> Dict[str, List[str]]:
        """Get recommendations based on risk level"""
        recommendations = {
            'low': {
                'immediate': ['Monitor symptoms', 'Rest and hydrate'],
                'follow_up': ['Follow up with primary care if symptoms persist']
            },
            'medium': {
                'immediate': ['Seek medical evaluation', 'Monitor vital signs'],
                'follow_up': ['Follow up within 24-48 hours', 'Consider specialist referral']
            },
            'high': {
                'immediate': ['Seek immediate medical attention', 'Call emergency services if severe'],
                'follow_up': ['Emergency department evaluation', 'Possible hospital admission']
            }
        }
        return recommendations.get(risk_level, recommendations['low'])
    
    def _get_warning_signs(self, condition: str, symptoms: Dict[str, Any]) -> List[str]:
        """Get warning signs for the condition"""
        return self.knowledge_base.get_condition_warning_signs(condition)
    
    def _get_emergency_indicators(self, symptoms: Dict[str, Any]) -> List[str]:
        """Get emergency indicators from symptoms"""
        emergency_symptoms = [
            'chest pain', 'shortness of breath', 'severe headache', 
            'confusion', 'difficulty speaking', 'vision changes',
            'severe abdominal pain', 'high fever', 'unconsciousness'
        ]
        
        symptom_list = symptoms.get('symptoms', [])
        return [symptom for symptom in emergency_symptoms if symptom in symptom_list]
    
    def _fallback_prediction(self, symptoms: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback prediction when ML is not available"""
        return {
            'ml_prediction': {
                'primary_condition': 'General Medical Assessment',
                'confidence': 0.5,
                'consensus': 0.5,
                'probability_breakdown': {'General Medical Assessment': 1.0}
            },
            'medical_analysis': {
                'condition_info': 'ML model not available - using rule-based assessment',
                'differential_diagnoses': [],
                'key_symptoms': [],
                'symptom_analysis': {}
            },
            'risk_assessment': {
                'overall_risk': 'medium',
                'recommendation': 'Medical evaluation recommended'
            },
            'recommendations': {
                'immediate_actions': ['Seek medical evaluation'],
                'diagnostic_tests': ['Physical examination'],
                'treatment_options': ['Symptomatic treatment'],
                'warning_signs': ['Fever, severe pain, difficulty breathing']
            },
            'metadata': {
                'prediction_method': 'fallback_rule_based',
                'model_version': '1.0',
                'timestamp': datetime.now().isoformat(),
                'requires_medical_review': True
            }
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        if not self.is_initialized:
            return {
                'status': 'not_initialized',
                'message': 'ML model not trained yet',
                'recommendation': 'Train model with at least 50 medical cases'
            }
        
        model_info = self.model.get_model_info()
        model_info['data_processor'] = {
            'feature_count': len(self.data_processor.get_feature_names()),
            'body_systems_supported': list(set(self.data_processor.body_systems.values()))
        }
        
        return model_info
