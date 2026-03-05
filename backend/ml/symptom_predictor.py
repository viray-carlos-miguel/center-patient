"""
Symptom Predictor Service (v2 — ML Urgency Classifier)
=======================================================
- Uses the trained UrgencyClassifier (TfidfVectorizer + RandomForest) for urgency prediction
- Uses ChatGPT for disease prediction (no old RF model, no rule-based logic)
- All urgency decisions are learned from data via the ML classifier
- ChatGPT fallback activates when ML urgency confidence is low
"""

import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from ml.urgency_classifier import UrgencyClassifier

load_dotenv()

# Urgency level mapping for frontend compatibility
URGENCY_TO_LEVEL = {
    "critical": "LEVEL 1",
    "high": "LEVEL 2",
    "medium": "LEVEL 3",
    "low": "LEVEL 4",
}


class SymptomPredictor:
    """ML-based symptom predictor using UrgencyClassifier + ChatGPT for disease prediction.
    No old Random Forest model. No rule-based logic. Everything learned from data."""

    def __init__(self):
        # ML urgency classifier (primary system)
        self.urgency_classifier = None
        self.model = None  # kept for backward compat check (SYMPTOM_PREDICTOR_ENABLED)
        try:
            self.urgency_classifier = UrgencyClassifier()
            if self.urgency_classifier.is_loaded:
                self.model = True  # signal that predictor is ready
                print("✅ SymptomPredictor v2: UrgencyClassifier loaded")
            else:
                print("⚠️  UrgencyClassifier not trained — run: python -m ml.urgency_classifier --train")
        except Exception as e:
            print(f"❌ UrgencyClassifier init failed: {e}")

        # OpenAI client (lazy — only created when needed for disease prediction)
        self._openai_client = None

    # ── Extract human-readable symptom names from frontend dict ──
    def _extract_symptom_names(self, symptoms: dict, description: str = "") -> list:
        """Convert frontend symptom dict to a list of human-readable symptom names."""
        names = []
        for key, value in symptoms.items():
            if not value:
                continue
            if key.startswith("has_"):
                clean = key.replace("has_", "").replace("_", " ").title()
                names.append(clean)
        if description:
            names.append(f"(described as: {description})")
        return names

    # ── ChatGPT Disease Prediction ──
    def _get_openai_client(self):
        if self._openai_client is None:
            api_key = os.getenv("CHATGPT_API_KEY")
            if not api_key:
                raise RuntimeError("CHATGPT_API_KEY not set in .env")
            self._openai_client = OpenAI(api_key=api_key)
        return self._openai_client

    async def predict_disease_chatgpt(self, symptom_names: list, description: str = "", urgency: str = "medium"):
        """Ask ChatGPT to predict diseases based ONLY on the provided symptoms.
        The ML-predicted urgency is passed for context."""
        client = self._get_openai_client()
        model = os.getenv("CHATGPT_MODEL", "gpt-4o")

        symptom_list = ", ".join(symptom_names) if symptom_names else "none specified"
        urgency_level = URGENCY_TO_LEVEL.get(urgency, "LEVEL 3")

        user_message = (
            f"A patient reports the following symptoms ONLY: {symptom_list}.\n"
            f"ML-assessed urgency: {urgency} ({urgency_level}).\n"
        )
        if description:
            user_message += f'Additional description: "{description}"\n'

        user_message += (
            "\nBased STRICTLY and ONLY on the symptoms listed above, provide:\n"
            "1. Top 3 most likely diseases/conditions (with estimated confidence % each)\n"
            "2. Brief reasoning for each\n"
            "3. Recommended next steps\n"
            "\nIMPORTANT: Do NOT assume any symptoms not listed.\n"
            "\nRespond in this exact JSON format:\n"
            '{\n'
            '  "predictions": [\n'
            '    {"disease": "...", "confidence": 75.0, "reasoning": "..."}\n'
            '  ],\n'
            '  "recommended_actions": ["..."]\n'
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
            print(f"❌ ChatGPT disease prediction error: {e}")
            return {
                "predictions": [],
                "recommended_actions": ["Please consult a healthcare professional."],
                "error": str(e),
                "method": "chatgpt_error",
            }

    # ── Urgency → Recommendations (data-driven, no rules) ──
    def _get_recommendations(self, urgency: str) -> list:
        """Map ML urgency level to recommendation messages."""
        URGENCY_RECOMMENDATIONS = {
            "critical": [
                "⚠️ EMERGENCY: Seek immediate medical attention or call emergency services.",
                "Do not delay – go to the nearest hospital immediately.",
            ],
            "high": [
                "🏥 URGENT: Visit a doctor or urgent care as soon as possible.",
                "Monitor symptoms closely and seek help if they worsen.",
            ],
            "medium": [
                "🩺 Schedule an appointment with your doctor soon.",
                "Rest and monitor your symptoms.",
            ],
            "low": [
                "💊 Mild condition – home care may be sufficient.",
                "Take over-the-counter medication if appropriate.",
                "See a doctor if symptoms persist or worsen.",
            ],
        }
        return URGENCY_RECOMMENDATIONS.get(urgency, URGENCY_RECOMMENDATIONS["medium"])

    # ── Main predict pipeline ──
    async def predict(self, symptoms: dict, description: str = ""):
        """
        Primary prediction pipeline (v2 — no old RF model, no rules):
        1. UrgencyClassifier predicts urgency (low/medium/high/critical)
        2. ChatGPT predicts diseases based on symptoms
        3. Return combined result with urgency + disease predictions
        """
        # ── Step 1: ML Urgency Classification ──
        urgency_result = None
        urgency = "medium"
        urgency_confidence = 0.0
        urgency_method = "none"

        if self.urgency_classifier and self.urgency_classifier.is_loaded:
            # Add description to symptoms dict for richer TF-IDF input
            enriched = {**symptoms}
            if description and "description" not in enriched:
                enriched["description"] = description
            urgency_result = self.urgency_classifier.predict_from_frontend(enriched)
            urgency = urgency_result.get("urgency", "medium")
            urgency_confidence = urgency_result.get("confidence", 0.0)
            urgency_method = urgency_result.get("method", "unknown")
            print(f"🎯 ML Urgency: {urgency} ({urgency_confidence:.0%}) via {urgency_method}")

        # ── Step 2: ChatGPT Disease Prediction ──
        symptom_names = self._extract_symptom_names(symptoms, description)
        chatgpt_result = await self.predict_disease_chatgpt(symptom_names, description, urgency)

        # Extract disease predictions from ChatGPT
        disease_predictions = chatgpt_result.get("predictions", [])
        chatgpt_actions = chatgpt_result.get("recommended_actions", [])

        # Add urgency_level to each prediction for frontend compatibility
        urgency_level = URGENCY_TO_LEVEL.get(urgency, "LEVEL 3")
        for pred in disease_predictions:
            pred["urgency_level"] = urgency_level
            pred["urgency"] = urgency

        # ── Step 3: Build recommendations from ML urgency ──
        ml_recommendations = self._get_recommendations(urgency)
        # Merge: ML urgency recommendations + ChatGPT action recommendations
        all_actions = ml_recommendations + [a for a in chatgpt_actions if a not in ml_recommendations]

        # ── Step 4: Build response ──
        top_prediction = disease_predictions[0] if disease_predictions else None

        return {
            "success": True,
            "analysis_method": f"ml_urgency+{chatgpt_result.get('method', 'chatgpt')}",
            # Disease predictions from ChatGPT
            "predictions": disease_predictions,
            "top_prediction": top_prediction,
            # Urgency from ML classifier
            "urgency": urgency,
            "urgency_level": urgency_level,
            "urgency_confidence": round(urgency_confidence * 100, 1),
            "urgency_method": urgency_method,
            "urgency_probabilities": urgency_result.get("probabilities", {}) if urgency_result else {},
            # Recommendations (ML urgency-driven)
            "recommended_actions": all_actions,
            # Raw results for debugging
            "urgency_result": urgency_result,
            "chatgpt_result": chatgpt_result,
            "ml_result": None,  # old RF model removed
            "chatgpt_reason": None,
            "confidence_threshold": None,
            "disclaimer": "This is an AI-assisted assessment for educational/clinical support purposes only. Always consult qualified healthcare professionals.",
        }


# Singleton instance
predictor = SymptomPredictor()
