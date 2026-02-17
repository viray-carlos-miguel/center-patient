"""
Medical ML Prediction Models
Ensemble of models for high-accuracy disease prediction
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
import os
from datetime import datetime

class MedicalEnsembleModel:
    """Ensemble of ML models for medical diagnosis prediction"""
    
    def __init__(self, model_dir: str = "ml_system/models"):
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        
        # Initialize individual models
        self.rf_model = RandomForestClassifier(
            n_estimators=300,
            max_depth=20,
            min_samples_split=3,
            min_samples_leaf=1,
            random_state=42,
            class_weight='balanced'
        )
        
        self.gb_model = GradientBoostingClassifier(
            n_estimators=200,
            learning_rate=0.1,
            max_depth=10,
            min_samples_split=3,
            random_state=42
        )
        
        self.nn_model = MLPClassifier(
            hidden_layer_sizes=(128, 64, 32),
            activation='relu',
            solver='adam',
            learning_rate='adaptive',
            max_iter=500,
            random_state=42,
            early_stopping=True
        )
        
        self.svm_model = SVC(
            kernel='rbf',
            C=1.0,
            gamma='scale',
            probability=True,
            random_state=42
        )
        
        self.nb_model = GaussianNB()
        
        # Create ensemble
        self.ensemble = VotingClassifier(
            estimators=[
                ('rf', self.rf_model),
                ('gb', self.gb_model),
                ('nn', self.nn_model),
                ('svm', self.svm_model),
                ('nb', self.nb_model)
            ],
            voting='soft',
            weights=[4.0, 4.0, 1.0, 0.3, 0.3]  # Dominate with RF and GB (highest accuracy)
        )
        
        self.is_trained = False
        self.feature_names = []
        self.class_names = []
        self.model_performance = {}
    
    def train(self, X: np.ndarray, y: np.ndarray, feature_names: List[str], class_names: List[str]) -> Dict[str, Any]:
        """Train the ensemble model"""
        print(f"🚀 Training ML ensemble on {X.shape[0]} cases, {X.shape[1]} features...")
        
        self.feature_names = feature_names
        self.class_names = class_names
        
        # Cross-validation for performance estimation
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        
        # Train individual models and collect performance
        models = {
            'RandomForest': self.rf_model,
            'GradientBoosting': self.gb_model,
            'NeuralNetwork': self.nn_model,
            'SVM': self.svm_model,
            'NaiveBayes': self.nb_model
        }
        
        for name, model in models.items():
            print(f"  📊 Training {name}...")
            scores = cross_val_score(model, X, y, cv=cv, scoring='accuracy')
            self.model_performance[name] = {
                'accuracy_mean': scores.mean(),
                'accuracy_std': scores.std(),
                'accuracy_scores': scores.tolist()
            }
            print(f"    ✅ {name}: {scores.mean():.3f} ± {scores.std():.3f}")
        
        # Train the ensemble
        print("  🎯 Training ensemble...")
        ensemble_scores = cross_val_score(self.ensemble, X, y, cv=cv, scoring='accuracy')
        
        # Fit the ensemble on full dataset
        self.ensemble.fit(X, y)
        
        # Sync individual models from the fitted ensemble
        self.rf_model = self.ensemble.named_estimators_['rf']
        self.gb_model = self.ensemble.named_estimators_['gb']
        self.nn_model = self.ensemble.named_estimators_['nn']
        self.svm_model = self.ensemble.named_estimators_['svm']
        self.nb_model = self.ensemble.named_estimators_['nb']
        
        self.is_trained = True
        
        self.model_performance['Ensemble'] = {
            'accuracy_mean': ensemble_scores.mean(),
            'accuracy_std': ensemble_scores.std(),
            'accuracy_scores': ensemble_scores.tolist()
        }
        
        print(f"    ✅ Ensemble: {ensemble_scores.mean():.3f} ± {ensemble_scores.std():.3f}")
        
        # Save the model
        self.save_model()
        
        return self.model_performance
    
    def predict(self, X: np.ndarray, return_probabilities: bool = True) -> Dict[str, Any]:
        """Make predictions with confidence scores"""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        # Get ensemble predictions
        predictions = self.ensemble.predict(X)
        probabilities = self.ensemble.predict_proba(X)
        
        # Calculate prediction confidence
        confidence_scores = np.max(probabilities, axis=1)
        
        # Calculate real consensus from individual fitted sub-models
        try:
            individual_preds = {}
            for name in ['rf', 'gb', 'nn', 'svm', 'nb']:
                sub = self.ensemble.named_estimators_[name]
                individual_preds[name] = sub.predict(X)
            consensus_scores = self._calculate_consensus(individual_preds)
        except Exception:
            consensus_scores = confidence_scores
        
        results = []
        for i in range(len(X)):
            result = {
                'predicted_class_index': int(predictions[i]),
                'predicted_class': self.class_names[predictions[i]] if predictions[i] < len(self.class_names) else 'Unknown',
                'confidence': float(confidence_scores[i]),
                'consensus': float(consensus_scores[i]),
                'probabilities': {
                    class_name: float(probabilities[i][j]) 
                    for j, class_name in enumerate(self.class_names)
                },
                'model_agreement': {
                    'ensemble_confidence': float(confidence_scores[i])
                },
                'risk_assessment': self._assess_prediction_risk({
                    'predicted_class': predictions[i],
                    'confidence': confidence_scores[i]
                })
            }
            results.append(result)
        
        return {
            'predictions': results,
            'ensemble_confidence': float(np.mean(confidence_scores)),
            'overall_consensus': float(np.mean(consensus_scores))
        }
    
    def _calculate_consensus(self, individual_predictions: Dict[str, np.ndarray]) -> np.ndarray:
        """Calculate consensus score among individual models"""
        n_models = len(individual_predictions)
        consensus_scores = []
        
        for i in range(len(list(individual_predictions.values())[0])):
            predictions_at_i = [pred[i] for pred in individual_predictions.values()]
            # Calculate the proportion of models that agree with the majority
            unique_preds, counts = np.unique(predictions_at_i, return_counts=True)
            max_count = np.max(counts)
            consensus = max_count / n_models
            consensus_scores.append(consensus)
        
        return np.array(consensus_scores)
    
    def get_feature_importance(self, top_n: int = 20) -> Dict[str, Any]:
        """Get feature importance from tree-based models"""
        if not self.is_trained:
            return {}
        
        # Use RF + GB feature importance (most reliable)
        try:
            rf_imp = self.rf_model.feature_importances_
            gb_imp = self.gb_model.feature_importances_
            importance = (rf_imp + gb_imp) / 2.0
        except Exception:
            # Fallback: create dummy importance
            importance = np.ones(len(self.feature_names)) / len(self.feature_names)
        
        # Create feature importance ranking
        feature_importance = []
        for i, imp in enumerate(importance):
            feature_name = self.feature_names[i] if i < len(self.feature_names) else f'feature_{i}'
            feature_importance.append({
                'feature': feature_name,
                'importance': float(imp)
            })
        
        # Sort by importance
        feature_importance.sort(key=lambda x: x['importance'], reverse=True)
        
        return {
            'top_features': feature_importance[:top_n],
            'all_features': feature_importance
        }
    
    def explain_prediction(self, X: np.ndarray, case_index: int = 0) -> Dict[str, Any]:
        """Explain why a specific prediction was made"""
        if not self.is_trained:
            return {}
        
        # Get ensemble predictions
        predictions = self.ensemble.predict(X)
        probabilities = self.ensemble.predict_proba(X)
        
        # Get feature importance
        feature_importance = self.get_feature_importance(10)['top_features']
        
        explanation = {
            'predicted_condition': self.class_names[predictions[case_index]] if predictions[case_index] < len(self.class_names) else 'Unknown',
            'confidence': float(np.max(probabilities[case_index])),
            'consensus': float(np.max(probabilities[case_index])),
            'top_contributing_features': feature_importance,
            'probability_breakdown': {
                class_name: float(probabilities[case_index][j]) 
                for j, class_name in enumerate(self.class_names)
            },
            'risk_assessment': 'medium'
        }
        
        return explanation
    
    def _assess_prediction_risk(self, prediction: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the risk level of a prediction"""
        confidence = prediction['confidence']
        consensus = prediction.get('consensus', confidence)
        
        # Risk categories based on confidence and consensus
        if confidence >= 0.8 and consensus >= 0.7:
            risk_level = 'low'
            recommendation = 'High confidence prediction suitable for clinical support'
        elif confidence >= 0.6 and consensus >= 0.5:
            risk_level = 'medium'
            recommendation = 'Moderate confidence - recommend clinical review'
        else:
            risk_level = 'high'
            recommendation = 'Low confidence - requires immediate clinical evaluation'
        
        return {
            'risk_level': risk_level,
            'recommendation': recommendation,
            'confidence_score': confidence,
            'consensus_score': consensus
        }
    
    def save_model(self):
        """Save the trained model"""
        if not self.is_trained:
            return
        
        model_data = {
            'ensemble': self.ensemble,
            'rf_model': self.rf_model,
            'gb_model': self.gb_model,
            'nn_model': self.nn_model,
            'svm_model': self.svm_model,
            'nb_model': self.nb_model,
            'feature_names': self.feature_names,
            'class_names': self.class_names,
            'performance': self.model_performance,
            'is_trained': self.is_trained,
            'timestamp': datetime.now().isoformat()
        }
        
        model_path = os.path.join(self.model_dir, 'medical_ensemble_model.pkl')
        joblib.dump(model_data, model_path)
        print(f"💾 Model saved to {model_path}")
    
    def load_model(self) -> bool:
        """Load a trained model"""
        model_path = os.path.join(self.model_dir, 'medical_ensemble_model.pkl')
        
        if not os.path.exists(model_path):
            return False
        
        try:
            model_data = joblib.load(model_path)
            self.ensemble = model_data['ensemble']
            self.feature_names = model_data['feature_names']
            self.class_names = model_data['class_names']
            self.model_performance = model_data['performance']
            self.is_trained = model_data['is_trained']
            
            # Restore individual fitted models
            if 'rf_model' in model_data:
                self.rf_model = model_data['rf_model']
                self.gb_model = model_data['gb_model']
                self.nn_model = model_data['nn_model']
                self.svm_model = model_data['svm_model']
                self.nb_model = model_data['nb_model']
            elif hasattr(self.ensemble, 'named_estimators_'):
                self.rf_model = self.ensemble.named_estimators_['rf']
                self.gb_model = self.ensemble.named_estimators_['gb']
                self.nn_model = self.ensemble.named_estimators_['nn']
                self.svm_model = self.ensemble.named_estimators_['svm']
                self.nb_model = self.ensemble.named_estimators_['nb']
            
            print(f"📂 Model loaded from {model_path}")
            return True
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the trained model"""
        if not self.is_trained:
            return {'status': 'not_trained'}
        
        return {
            'status': 'trained',
            'num_features': len(self.feature_names),
            'num_classes': len(self.class_names),
            'performance': self.model_performance,
            'model_types': list(self.ensemble.named_estimators.keys()),
            'timestamp': datetime.now().isoformat()
        }
