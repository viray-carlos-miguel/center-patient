"""
Symptom Predictor Service
- Loads trained Random Forest model
- Maps frontend symptom flags to model feature vector
- Predicts disease with confidence
- Falls back to ChatGPT (OpenAI) when confidence is low, using ONLY input symptoms
"""

import os
import json
import numpy as np
import joblib
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "trained_model")

# Confidence threshold: below this → ChatGPT fallback
# Note: model trained on small dataset (1 sample/class) so scores are inherently low
CONFIDENCE_THRESHOLD = 0.20

# ──────────────────────────────────────────────
# Mapping: frontend symptom checkbox IDs → CSV column names
# The frontend sends boolean fields like has_fever, has_cough_dry, etc.
# We map them to the CSV feature columns used during training.
# ──────────────────────────────────────────────
FRONTEND_TO_FEATURE = {
    # General / Systemic
    "fever": "Fever",
    "fatigue": "Fatigue",
    "malaise": "Fatigue",  # maps to nearest
    "weight_loss": "WeightLoss",
    "loss_of_appetite": "LossOfAppetite",
    "night_sweats": "NightSweats",
    "chills": "Chills",
    "generalized_pain": "Pain",
    "excessive_sweating": "ExcessiveSweating",
    # Respiratory
    "cough": "Cough",
    "cough_dry": "Cough",
    "cough_productive": "ProductiveCough",
    "shortness_of_breath": "ShortnessBreath",
    "wheezing": "Wheezing",
    "chest_tightness": "ChestTightness",
    "sore_throat": "SoreThroat",
    "nasal_congestion": "NasalCongestion",
    # Cardiovascular
    "palpitations": "Palpitations",
    "chest_pain": "ChestPain",
    "syncope": "Fainting",
    # Gastrointestinal
    "abdominal_pain": "AbdominalPain",
    "nausea": "Nausea",
    "vomiting": "Vomiting",
    "diarrhea": "Diarrhea",
    "constipation": "Constipation",
    "bloating": "Bloating",
    "heartburn": "Heartburn",
    "dysphagia": "DifficultySwallowing",
    # Neurological
    "headache": "Headache",
    "dizziness": "Dizziness",
    "numbness": "Numbness",
    "limb_weakness": "MuscleWeakness",
    "coordination_loss": "LossOfCoordination",
    "memory_loss": "Confusion",
    "seizures": "Seizures",
    "sleep_disturbances": "SleepDisturbances",
    # Psychiatric
    "anxiety": "Anxiety",
    # Sensory
    "photophobia": "LightSensitivity",
    # Musculoskeletal
    "muscle_pain": "MusclePain",
    "muscle_weakness": "MuscleWeakness",
    "joint_pain": "JointPain",
    "joint_swelling": "Swelling",
    # Dermatological
    "skin_rash": "Rash",
    "itching": "Itching",
    "bruising": "Bruising",
    # Genitourinary
    "frequent_urination": "FrequentUrination",
    "painful_urination": "PainfulUrination",
    "blood_in_urine": "BloodInUrine",
    # Endocrine
    "excessive_thirst": "ExcessiveThirst",
    # ENT
    "pharyngitis": "SoreThroat",
    "swollen_lymph_nodes": "Swelling",
}


class SymptomPredictor:
    """Loads the trained RF model and provides predict() with ChatGPT fallback."""

    def __init__(self):
        self.model = None
        self.metadata = None
        self.feature_columns = []
        self.classes = []
        self.urgency_map = {}
        self._load_model()

        # OpenAI client (lazy – only created when needed)
        self._openai_client = None

    # ── Model loading ──────────────────────────
    def _load_model(self):
        model_path = os.path.join(MODEL_DIR, "symptom_rf_model.joblib")
        meta_path = os.path.join(MODEL_DIR, "model_metadata.json")

        if not os.path.exists(model_path) or not os.path.exists(meta_path):
            print("⚠️  Trained model not found – run train_symptom_model.py first")
            return

        self.model = joblib.load(model_path)
        with open(meta_path, "r") as f:
            self.metadata = json.load(f)
        self.feature_columns = self.metadata["feature_columns"]
        self.classes = self.metadata["classes"]
        self.urgency_map = self.metadata.get("urgency_map", {})
        print(f"✅ SymptomPredictor loaded: {len(self.classes)} diseases, {len(self.feature_columns)} features")

    # ── Build feature vector from frontend symptoms ──
    def _build_feature_vector(self, symptoms: dict) -> np.ndarray:
        """Convert frontend symptom dict to model feature vector."""
        vec = np.zeros(len(self.feature_columns), dtype=int)
        col_index = {col: i for i, col in enumerate(self.feature_columns)}

        activated = []
        for key, value in symptoms.items():
            if not value:
                continue
            # Strip "has_" prefix if present
            clean = key.replace("has_", "") if key.startswith("has_") else key
            feature_name = FRONTEND_TO_FEATURE.get(clean)
            if feature_name and feature_name in col_index:
                vec[col_index[feature_name]] = 1
                activated.append(feature_name)

        return vec, activated

    # ── ML Prediction ──────────────────────────
    def predict_ml(self, symptoms: dict):
        """Run Random Forest prediction. Returns top predictions with confidence."""
        if self.model is None:
            return None

        vec, activated_features = self._build_feature_vector(symptoms)

        if sum(vec) == 0:
            return None  # no recognized symptoms

        probas = self.model.predict_proba(vec.reshape(1, -1))[0]
        top_indices = np.argsort(probas)[::-1]

        results = []
        for idx in top_indices[:5]:
            conf = float(probas[idx])
            if conf < 0.01:
                break
            disease = self.classes[idx]
            results.append({
                "disease": disease,
                "confidence": round(conf * 100, 1),
                "urgency_level": self.urgency_map.get(disease, "LEVEL 4"),
            })

        return {
            "predictions": results,
            "top_confidence": results[0]["confidence"] if results else 0,
            "activated_features": activated_features,
            "method": "random_forest",
        }

    # ── ChatGPT Fallback ──────────────────────
    def _get_openai_client(self):
        if self._openai_client is None:
            api_key = os.getenv("CHATGPT_API_KEY")
            if not api_key:
                raise RuntimeError("CHATGPT_API_KEY not set in .env")
            self._openai_client = OpenAI(api_key=api_key)
        return self._openai_client

    async def predict_chatgpt(self, symptom_names: list[str], description: str = ""):
        """Ask ChatGPT to predict based ONLY on the provided symptoms."""
        client = self._get_openai_client()
        model = os.getenv("CHATGPT_MODEL", "gpt-4o")

        symptom_list = ", ".join(symptom_names) if symptom_names else "none specified"
        user_message = (
            f"A patient reports the following symptoms ONLY: {symptom_list}.\n"
        )
        if description:
            user_message += f'Additional description from the patient: "{description}"\n'

        user_message += (
            "\nBased STRICTLY and ONLY on the symptoms listed above, provide:\n"
            "1. Top 3 most likely diseases/conditions (with estimated confidence % each)\n"
            "2. Urgency level for each (LEVEL 1 = Emergency, LEVEL 2 = Urgent, LEVEL 3 = Moderate, LEVEL 4 = Mild, LEVEL 5 = Self-care)\n"
            "3. Brief reasoning for each\n"
            "4. Recommended next steps\n"
            "\nIMPORTANT: Do NOT assume any symptoms that were not listed. "
            "Base your analysis EXCLUSIVELY on the provided symptoms.\n"
            "\nRespond in this exact JSON format:\n"
            '{\n'
            '  "predictions": [\n'
            '    {"disease": "...", "confidence": 75.0, "urgency_level": "LEVEL 3", "reasoning": "..."}\n'
            '  ],\n'
            '  "recommended_actions": ["..."],\n'
            '  "disclaimer": "This is an AI-assisted assessment for educational purposes only."\n'
            '}'
        )

        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a medical diagnosis assistant. You must ONLY analyze "
                            "the symptoms explicitly provided by the patient. Do NOT infer, "
                            "assume, or add any symptoms that were not mentioned. "
                            "Respond strictly in the JSON format requested."
                        ),
                    },
                    {"role": "user", "content": user_message},
                ],
                temperature=0.3,
                max_tokens=1000,
                response_format={"type": "json_object"},
            )

            raw = response.choices[0].message.content
            result = json.loads(raw)
            result["method"] = "chatgpt"
            result["model_used"] = model
            return result

        except Exception as e:
            print(f"❌ ChatGPT fallback error: {e}")
            return {
                "predictions": [],
                "recommended_actions": ["Please consult a healthcare professional."],
                "error": str(e),
                "method": "chatgpt_error",
            }

    # ── Main predict (ML first → ChatGPT fallback) ──
    async def predict(self, symptoms: dict, description: str = ""):
        """
        Primary prediction pipeline:
        1. Try ML (Random Forest) first
        2. If confidence < threshold OR no result → fall back to ChatGPT
        3. Return combined result
        """
        ml_result = self.predict_ml(symptoms)

        use_chatgpt = False
        chatgpt_reason = ""

        if ml_result is None:
            use_chatgpt = True
            chatgpt_reason = "No recognized symptoms for ML model"
        elif ml_result["top_confidence"] < CONFIDENCE_THRESHOLD * 100:
            use_chatgpt = True
            chatgpt_reason = f"ML confidence too low ({ml_result['top_confidence']:.1f}% < {CONFIDENCE_THRESHOLD*100:.0f}%)"

        chatgpt_result = None
        if use_chatgpt:
            # Build human-readable symptom names for ChatGPT
            symptom_names = []
            for key, value in symptoms.items():
                if value and key.startswith("has_"):
                    clean = key.replace("has_", "").replace("_", " ").title()
                    symptom_names.append(clean)
            # Also include description
            if description:
                symptom_names.append(f"(described as: {description})")

            print(f"🤖 ChatGPT fallback triggered: {chatgpt_reason}")
            chatgpt_result = await self.predict_chatgpt(symptom_names, description)

        # Build final response
        if use_chatgpt and chatgpt_result and chatgpt_result.get("predictions"):
            primary_predictions = chatgpt_result["predictions"]
            analysis_method = "chatgpt"
            recommended_actions = chatgpt_result.get("recommended_actions", [])
        elif ml_result and ml_result.get("predictions"):
            primary_predictions = ml_result["predictions"]
            analysis_method = "random_forest"
            recommended_actions = self._get_ml_recommendations(primary_predictions)
        else:
            primary_predictions = []
            analysis_method = "none"
            recommended_actions = ["Please consult a healthcare professional for proper diagnosis."]

        return {
            "success": True,
            "analysis_method": analysis_method,
            "predictions": primary_predictions,
            "top_prediction": primary_predictions[0] if primary_predictions else None,
            "recommended_actions": recommended_actions,
            "ml_result": ml_result,
            "chatgpt_result": chatgpt_result,
            "chatgpt_reason": chatgpt_reason if use_chatgpt else None,
            "confidence_threshold": CONFIDENCE_THRESHOLD * 100,
            "disclaimer": "This is an AI-assisted assessment for educational/clinical support purposes only. Always consult qualified healthcare professionals.",
        }

    def _get_ml_recommendations(self, predictions):
        """Generate recommendations based on ML predictions."""
        if not predictions:
            return ["Consult a healthcare professional."]

        top = predictions[0]
        urgency = top.get("urgency_level", "LEVEL 4")
        recs = []

        if urgency == "LEVEL 1":
            recs.append("⚠️ EMERGENCY: Seek immediate medical attention or call emergency services.")
            recs.append("Do not delay – go to the nearest hospital immediately.")
        elif urgency == "LEVEL 2":
            recs.append("🏥 URGENT: Visit a doctor or urgent care as soon as possible.")
            recs.append("Monitor symptoms closely and seek help if they worsen.")
        elif urgency == "LEVEL 3":
            recs.append("🩺 Schedule an appointment with your doctor soon.")
            recs.append("Rest and monitor your symptoms.")
        elif urgency == "LEVEL 4":
            recs.append("💊 Mild condition – home care may be sufficient.")
            recs.append("Take over-the-counter medication if appropriate.")
            recs.append("See a doctor if symptoms persist or worsen.")
        else:
            recs.append("🏠 Self-care recommended.")
            recs.append("Rest, stay hydrated, and monitor symptoms.")

        return recs


# Singleton instance
predictor = SymptomPredictor()
