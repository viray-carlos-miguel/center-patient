"""
DEPRECATED — Medical ML Prediction Engine (old ensemble model)
================================================================
This module is NO LONGER USED. It has been replaced by:
- ml/urgency_classifier.py  → ML urgency classification (TfidfVectorizer + RandomForest)
- ml/symptom_predictor.py   → ChatGPT disease prediction + ML urgency
- services/gemini_ai.py     → Gemini AI disease prediction + ML urgency

Kept for reference only. Do not import or use this module.
"""

import os
import pickle
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple

from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    VotingClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import classification_report, accuracy_score
from sklearn.calibration import CalibratedClassifierCV

from ml.medical_dataset import generate_dataset, ALL_SYMPTOMS, DISEASE_PROFILES, DISEASE_METADATA

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
MODEL_PATH = os.path.join(MODEL_DIR, "ensemble_model.pkl")


class MedicalPredictionEngine:
    """High-accuracy medical symptom → disease prediction engine."""

    def __init__(self):
        self.model = None
        self.label_encoder: Optional[LabelEncoder] = None
        self.scaler: Optional[StandardScaler] = None
        self.feature_names: List[str] = []
        self.is_trained = False
        self.accuracy = 0.0
        self.diseases: List[str] = []

        # Try to load a pre-trained model
        if os.path.exists(MODEL_PATH):
            self._load_model()

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------

    def train(self, n_samples: int = 6000) -> Dict[str, Any]:
        """Train the ensemble model from scratch."""
        print("📊 Generating training dataset...")
        df = generate_dataset(n_samples)

        # Feature columns = all symptoms + numerical
        self.feature_names = ALL_SYMPTOMS + [
            "severity", "duration_hours", "temperature", "age", "gender"
        ]
        X = df[self.feature_names].values.astype(np.float32)
        y = df["disease"].values

        # Encode labels
        self.label_encoder = LabelEncoder()
        y_encoded = self.label_encoder.fit_transform(y)
        self.diseases = list(self.label_encoder.classes_)

        # Scale numerical features (last 5 columns)
        self.scaler = StandardScaler()
        X[:, -5:] = self.scaler.fit_transform(X[:, -5:])

        # Build ensemble
        print("🔧 Building ensemble model...")
        rf = RandomForestClassifier(
            n_estimators=300,
            max_depth=25,
            min_samples_split=5,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        )
        gb = GradientBoostingClassifier(
            n_estimators=200,
            max_depth=8,
            learning_rate=0.1,
            subsample=0.8,
            random_state=42,
        )
        lr = LogisticRegression(
            max_iter=2000,
            multi_class="multinomial",
            solver="lbfgs",
            class_weight="balanced",
            random_state=42,
        )

        ensemble = VotingClassifier(
            estimators=[("rf", rf), ("gb", gb), ("lr", lr)],
            voting="soft",
            weights=[3, 2, 1],  # RF gets most weight
        )

        # Cross-validate
        print("📈 Cross-validating...")
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        cv_scores = cross_val_score(ensemble, X, y_encoded, cv=cv, scoring="accuracy")
        print(f"   CV Accuracy: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

        # Final fit on full data
        print("🏋️ Training final model on full dataset...")
        ensemble.fit(X, y_encoded)

        # Wrap with probability calibration for better confidence scores
        self.model = CalibratedClassifierCV(ensemble, cv=3, method="isotonic")
        self.model.fit(X, y_encoded)

        # Evaluate
        y_pred = self.model.predict(X)
        self.accuracy = accuracy_score(y_encoded, y_pred)
        print(f"✅ Training accuracy: {self.accuracy:.4f}")

        report = classification_report(
            y_encoded, y_pred,
            target_names=self.diseases,
            output_dict=True,
        )

        self.is_trained = True
        self._save_model()

        return {
            "accuracy": round(self.accuracy * 100, 2),
            "cv_accuracy": round(cv_scores.mean() * 100, 2),
            "cv_std": round(cv_scores.std() * 100, 2),
            "n_samples": n_samples,
            "n_diseases": len(self.diseases),
            "diseases": self.diseases,
            "per_class": {
                name: {
                    "precision": round(report[name]["precision"] * 100, 1),
                    "recall": round(report[name]["recall"] * 100, 1),
                    "f1": round(report[name]["f1-score"] * 100, 1),
                }
                for name in self.diseases
                if name in report
            },
        }

    def predict(self, symptoms: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict disease from symptom input.

        Parameters
        ----------
        symptoms : dict
            Keys can include:
            - description (str): free-text symptom description
            - individual symptom flags (bool/int)
            - severity, duration_hours, temperature, age, gender
        """
        if not self.is_trained:
            raise RuntimeError("Model not trained. Call train() first.")

        feature_vec = self._build_feature_vector(symptoms)
        X = np.array([feature_vec], dtype=np.float32)

        # Scale numerical features
        X[:, -5:] = self.scaler.transform(X[:, -5:])

        # Predict probabilities
        proba = self.model.predict_proba(X)[0]
        top_indices = np.argsort(proba)[::-1]

        # Build predictions list (top 5)
        predictions = []
        for idx in top_indices[:5]:
            disease_name = self.label_encoder.inverse_transform([idx])[0]
            confidence = float(proba[idx])
            if confidence < 0.01:
                continue
            profile = DISEASE_PROFILES.get(disease_name, {})
            metadata = DISEASE_METADATA.get(disease_name, {})
            predictions.append({
                "disease": disease_name,
                "confidence": round(confidence * 100, 2),
                "matching_symptoms": self._get_matching_symptoms(
                    symptoms, profile.get("symptoms", {})
                ),
                "emergency_level": metadata.get("emergency_level", "moderate"),
                "medications": metadata.get("medications", []),
                "home_care": metadata.get("home_care", ""),
                "hospital_advice": metadata.get("hospital_advice", ""),
                "when_to_seek_emergency": metadata.get("when_to_seek_emergency", ""),
            })

        # Risk assessment with enhanced emergency logic
        top_confidence = predictions[0]["confidence"] if predictions else 0
        severity = symptoms.get("severity", 5)
        risk_score = self._calculate_risk(top_confidence, severity, predictions)

        # Build top-level emergency info from the primary prediction
        top_pred = predictions[0] if predictions else {}
        emergency_info = self._build_emergency_info(top_pred, severity)

        return {
            "predictions": predictions,
            "risk_assessment": risk_score,
            "emergency": emergency_info,
            "model_confidence": round(top_confidence, 2),
            "analysis_method": "ensemble_ml",
            "model_accuracy": round(self.accuracy * 100, 2),
            "disclaimer": "This is an educational AI tool, not a substitute for professional medical advice. Always consult a qualified healthcare professional for diagnosis and treatment.",
        }

    # ------------------------------------------------------------------
    # INTERNAL HELPERS
    # ------------------------------------------------------------------

    def _build_feature_vector(self, symptoms: Dict[str, Any]) -> List[float]:
        """Convert symptom dict → fixed-length feature vector."""
        vec = []

        # Parse free-text description into symptom flags
        description = symptoms.get("description", "").lower()
        text_symptoms = self._parse_description(description)

        for s in ALL_SYMPTOMS:
            # Check explicit flag first, then text extraction
            if s in symptoms:
                val = symptoms[s]
                vec.append(1.0 if val else 0.0)
            elif s in text_symptoms:
                vec.append(1.0)
            else:
                vec.append(0.0)

        # Numerical features
        vec.append(float(symptoms.get("severity", 5)))
        vec.append(float(symptoms.get("duration_hours", 48)))
        vec.append(float(symptoms.get("temperature", 37.0)))
        vec.append(float(symptoms.get("age", 30)))
        vec.append(float(symptoms.get("gender", 0)))

        return vec

    def _parse_description(self, text: str) -> set:
        """Extract symptom keywords from free-text description."""
        found = set()
        # Map common phrases to symptom feature names
        keyword_map = {
            "fever": ["fever"],
            "high fever": ["high_fever", "fever"],
            "mild fever": ["mild_fever"],
            "cough": ["cough"],
            "dry cough": ["dry_cough", "cough"],
            "productive cough": ["productive_cough", "cough"],
            "coughing blood": ["cough_with_blood", "cough"],
            "blood in cough": ["cough_with_blood"],
            "sore throat": ["sore_throat"],
            "runny nose": ["runny_nose"],
            "stuffy nose": ["nasal_congestion"],
            "nasal congestion": ["nasal_congestion"],
            "congestion": ["nasal_congestion"],
            "sneezing": ["sneezing"],
            "headache": ["headache"],
            "severe headache": ["severe_headache", "headache"],
            "migraine": ["migraine", "severe_headache", "headache"],
            "body ache": ["body_aches"],
            "body pain": ["body_aches"],
            "muscle pain": ["muscle_pain"],
            "joint pain": ["joint_pain"],
            "back pain": ["back_pain"],
            "tired": ["fatigue"],
            "fatigue": ["fatigue"],
            "exhausted": ["extreme_fatigue", "fatigue"],
            "extreme fatigue": ["extreme_fatigue", "fatigue"],
            "weak": ["weakness"],
            "weakness": ["weakness"],
            "short of breath": ["shortness_of_breath"],
            "shortness of breath": ["shortness_of_breath"],
            "difficulty breathing": ["shortness_of_breath"],
            "breathing difficulty": ["shortness_of_breath"],
            "wheezing": ["wheezing"],
            "chest tight": ["chest_tightness"],
            "chest pain": ["chest_pain"],
            "nausea": ["nausea"],
            "nauseous": ["nausea"],
            "vomiting": ["vomiting"],
            "throwing up": ["vomiting"],
            "diarrhea": ["diarrhea"],
            "loose stool": ["diarrhea"],
            "constipation": ["constipation"],
            "stomach pain": ["abdominal_pain"],
            "abdominal pain": ["abdominal_pain"],
            "belly pain": ["abdominal_pain"],
            "bloating": ["bloating"],
            "bloated": ["bloating"],
            "no appetite": ["loss_of_appetite"],
            "loss of appetite": ["loss_of_appetite"],
            "not hungry": ["loss_of_appetite"],
            "dizzy": ["dizziness"],
            "dizziness": ["dizziness"],
            "lightheaded": ["lightheadedness"],
            "faint": ["fainting"],
            "rash": ["skin_rash"],
            "skin rash": ["skin_rash"],
            "itchy": ["itching"],
            "itching": ["itching"],
            "hives": ["hives"],
            "swelling": ["swelling"],
            "swollen": ["swelling"],
            "chills": ["chills"],
            "night sweat": ["night_sweats"],
            "sweating": ["sweating"],
            "weight loss": ["weight_loss"],
            "losing weight": ["weight_loss"],
            "weight gain": ["weight_gain"],
            "frequent urination": ["frequent_urination"],
            "urinating often": ["frequent_urination"],
            "painful urination": ["painful_urination"],
            "burning urination": ["painful_urination"],
            "blood in urine": ["blood_in_urine"],
            "blurred vision": ["blurred_vision"],
            "blurry vision": ["blurred_vision"],
            "eye pain": ["eye_pain"],
            "red eye": ["eye_redness"],
            "ear pain": ["ear_pain"],
            "earache": ["ear_pain"],
            "hearing loss": ["hearing_loss"],
            "ringing in ear": ["tinnitus"],
            "tinnitus": ["tinnitus"],
            "difficulty swallowing": ["difficulty_swallowing"],
            "hard to swallow": ["difficulty_swallowing"],
            "hoarse": ["hoarseness"],
            "hoarseness": ["hoarseness"],
            "numb": ["numbness"],
            "numbness": ["numbness"],
            "tingling": ["tingling"],
            "pins and needles": ["tingling"],
            "tremor": ["tremor"],
            "shaking": ["tremor"],
            "confused": ["confusion"],
            "confusion": ["confusion"],
            "memory problem": ["memory_problems"],
            "forgetful": ["memory_problems"],
            "anxious": ["anxiety"],
            "anxiety": ["anxiety"],
            "depressed": ["depression"],
            "depression": ["depression"],
            "sad": ["depression"],
            "can't sleep": ["insomnia"],
            "insomnia": ["insomnia"],
            "trouble sleeping": ["insomnia"],
            "swollen lymph": ["swollen_lymph_nodes"],
            "swollen gland": ["swollen_lymph_nodes"],
            "stiff neck": ["stiff_neck"],
            "neck stiff": ["stiff_neck"],
            "loss of taste": ["loss_of_taste"],
            "can't taste": ["loss_of_taste"],
            "loss of smell": ["loss_of_smell"],
            "can't smell": ["loss_of_smell"],
            "heart racing": ["rapid_heartbeat", "palpitations"],
            "palpitation": ["palpitations"],
            "rapid heartbeat": ["rapid_heartbeat"],
            "heart pounding": ["palpitations"],
        }

        for phrase, symptom_keys in keyword_map.items():
            if phrase in text:
                found.update(symptom_keys)

        return found

    def _get_matching_symptoms(
        self, input_symptoms: Dict, disease_symptoms: Dict
    ) -> List[str]:
        """Return list of symptoms the patient has that match the disease profile."""
        description = input_symptoms.get("description", "").lower()
        text_symptoms = self._parse_description(description)
        matches = []
        for s in disease_symptoms:
            if s in ALL_SYMPTOMS:
                if input_symptoms.get(s) or s in text_symptoms:
                    matches.append(s.replace("_", " "))
        return matches

    def _build_emergency_info(
        self, top_prediction: Dict, severity: int
    ) -> Dict[str, Any]:
        """Build comprehensive emergency information based on prediction and severity."""
        if not top_prediction:
            return {
                "level": "low",
                "label": "Non-Urgent",
                "color": "green",
                "go_to_hospital": False,
                "message": "Monitor your symptoms and rest.",
                "hospital_message": "",
            }

        emergency_level = top_prediction.get("emergency_level", "moderate")
        disease = top_prediction.get("disease", "")

        # Escalate emergency level based on severity
        if severity >= 9:
            if emergency_level in ("low", "moderate"):
                emergency_level = "high"
            elif emergency_level == "high":
                emergency_level = "critical"
        elif severity >= 7:
            if emergency_level == "low":
                emergency_level = "moderate"

        # Build response based on emergency level
        level_config = {
            "low": {
                "label": "Non-Urgent",
                "color": "green",
                "go_to_hospital": False,
                "message": "Your symptoms suggest a condition that can likely be managed at home with over-the-counter medications. Monitor your symptoms.",
            },
            "moderate": {
                "label": "Moderate",
                "color": "yellow",
                "go_to_hospital": False,
                "message": "Your symptoms need attention. Consider scheduling a doctor appointment within the next few days. Follow the recommended home care.",
            },
            "high": {
                "label": "Urgent",
                "color": "orange",
                "go_to_hospital": True,
                "message": "Your symptoms indicate a potentially serious condition. Please visit a doctor or urgent care clinic as soon as possible.",
            },
            "critical": {
                "label": "EMERGENCY",
                "color": "red",
                "go_to_hospital": True,
                "message": "⚠️ YOUR SYMPTOMS MAY INDICATE A MEDICAL EMERGENCY. Please go to the nearest hospital emergency room or call emergency services (911) IMMEDIATELY.",
            },
        }

        config = level_config.get(emergency_level, level_config["moderate"])
        hospital_message = ""
        if config["go_to_hospital"]:
            hospital_message = top_prediction.get("when_to_seek_emergency", "")
            if not hospital_message:
                hospital_message = "Please seek immediate medical attention."

        return {
            "level": emergency_level,
            "label": config["label"],
            "color": config["color"],
            "go_to_hospital": config["go_to_hospital"],
            "message": config["message"],
            "hospital_message": hospital_message,
        }

    def _calculate_risk(
        self, confidence: float, severity: int, predictions: List[Dict]
    ) -> Dict[str, Any]:
        """Compute risk assessment."""
        # Critical diseases that need immediate hospital visit
        critical_diseases = {"Meningitis", "Heart Attack", "Appendicitis", "Malaria"}
        high_risk_diseases = {
            "Pneumonia", "Tuberculosis", "Dengue Fever", "Kidney Stones",
            "Allergic Reaction",
        }

        top_disease = predictions[0]["disease"] if predictions else ""
        is_critical = top_disease in critical_diseases
        is_high_risk = top_disease in high_risk_diseases

        if is_critical or (severity >= 9 and is_high_risk):
            level = "critical"
            action = "🚨 GO TO HOSPITAL IMMEDIATELY — Call emergency services (911)"
        elif severity >= 8 or is_high_risk:
            level = "high"
            action = "⚠️ Seek immediate medical attention — Visit ER or urgent care"
        elif severity >= 5 or confidence >= 70:
            level = "medium"
            action = "Schedule a doctor appointment soon"
        else:
            level = "low"
            action = "Monitor symptoms and rest at home"

        return {
            "risk_level": level,
            "risk_score": min(10, max(1, int(severity * (confidence / 100) + (4 if is_critical else 2 if is_high_risk else 0)))),
            "recommended_action": action,
            "is_emergency": is_critical or (is_high_risk and severity >= 8),
        }

    # ------------------------------------------------------------------
    # PERSISTENCE
    # ------------------------------------------------------------------

    def _save_model(self):
        os.makedirs(MODEL_DIR, exist_ok=True)
        data = {
            "model": self.model,
            "label_encoder": self.label_encoder,
            "scaler": self.scaler,
            "feature_names": self.feature_names,
            "accuracy": self.accuracy,
            "diseases": self.diseases,
        }
        with open(MODEL_PATH, "wb") as f:
            pickle.dump(data, f)
        print(f"💾 Model saved to {MODEL_PATH}")

    def _load_model(self):
        try:
            with open(MODEL_PATH, "rb") as f:
                data = pickle.load(f)
            self.model = data["model"]
            self.label_encoder = data["label_encoder"]
            self.scaler = data["scaler"]
            self.feature_names = data["feature_names"]
            self.accuracy = data["accuracy"]
            self.diseases = data["diseases"]
            self.is_trained = True
            print(f"✅ Model loaded from {MODEL_PATH} (accuracy: {self.accuracy:.2%})")
        except Exception as e:
            print(f"⚠️ Could not load model: {e}")
            self.is_trained = False


# Quick CLI test
if __name__ == "__main__":
    engine = MedicalPredictionEngine()

    if not engine.is_trained:
        print("\n" + "=" * 60)
        print("TRAINING MODEL")
        print("=" * 60)
        result = engine.train(n_samples=6000)
        print(f"\n✅ Training complete!")
        print(f"   Accuracy: {result['accuracy']}%")
        print(f"   CV Accuracy: {result['cv_accuracy']}% ± {result['cv_std']}%")
        print(f"   Diseases: {result['n_diseases']}")

    # Test predictions
    print("\n" + "=" * 60)
    print("TEST PREDICTIONS")
    print("=" * 60)

    test_cases = [
        {
            "description": "I have fever, dry cough, and loss of taste and smell for 5 days",
            "severity": 6, "duration_hours": 120, "temperature": 38.5, "age": 35, "gender": 1,
        },
        {
            "description": "severe headache, stiff neck, high fever, nausea, confusion",
            "severity": 9, "duration_hours": 24, "temperature": 39.5, "age": 22, "gender": 0,
        },
        {
            "description": "runny nose, sneezing, itchy eyes, nasal congestion",
            "severity": 2, "duration_hours": 336, "temperature": 36.5, "age": 28, "gender": 1,
        },
        {
            "description": "chest pain, shortness of breath, sweating, nausea, anxiety",
            "severity": 9, "duration_hours": 2, "temperature": 37.0, "age": 55, "gender": 1,
        },
        {
            "description": "diarrhea, vomiting, stomach pain, nausea, mild fever",
            "severity": 6, "duration_hours": 12, "temperature": 38.0, "age": 30, "gender": 0,
        },
    ]

    for i, case in enumerate(test_cases, 1):
        result = engine.predict(case)
        top = result["predictions"][0]
        print(f"\nCase {i}: {case['description'][:60]}...")
        print(f"  → {top['disease']} ({top['confidence']}%)")
        print(f"  Risk: {result['risk_assessment']['risk_level']}")
        if len(result["predictions"]) > 1:
            print(f"  2nd: {result['predictions'][1]['disease']} ({result['predictions'][1]['confidence']}%)")
