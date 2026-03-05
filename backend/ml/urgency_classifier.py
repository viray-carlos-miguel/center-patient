"""
Symptom Urgency Classifier
===========================
A pure ML-based urgency classifier that predicts urgency levels (low, medium, high, critical)
from symptom text using TfidfVectorizer + RandomForestClassifier.

NO rule-based logic is used — all predictions are learned from training data.

Fallback: When model confidence is below a threshold (default 0.7), the system
calls the ChatGPT API to classify urgency based solely on symptoms.

Setup
-----
1. Ensure CHATGPT_API_KEY is set in backend/.env
2. Run training:
       cd backend
       python -m ml.urgency_classifier --train
3. The trained model is saved to backend/ml/trained_model/urgency_model.joblib
   and the vectorizer to backend/ml/trained_model/urgency_vectorizer.joblib

Usage
-----
    from ml.urgency_classifier import UrgencyClassifier

    clf = UrgencyClassifier()
    result = clf.predict(["fever", "chest pain", "shortness of breath"])
    print(result)
    # {
    #   "urgency": "critical",
    #   "confidence": 0.92,
    #   "probabilities": {"low": 0.02, "medium": 0.03, "high": 0.03, "critical": 0.92},
    #   "method": "ml",
    # }

Improving Accuracy
------------------
- Add more training examples to urgency_training_data.csv
- Re-run training with --tune flag for hyperparameter search
- Increase cross-validation folds (default=5)
- Use --evaluate flag to see per-class metrics

Dependencies
------------
scikit-learn>=1.3.2, numpy>=1.26.2, pandas>=2.0.0, joblib>=1.3.0, openai>=1.0.0
"""

import os
import json
import argparse
import numpy as np
import pandas as pd
import joblib
from typing import List, Dict, Any, Optional, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import (
    cross_val_score,
    StratifiedKFold,
    GridSearchCV,
)
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.pipeline import Pipeline

# ──────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "trained_model")
VECTORIZER_PATH = os.path.join(MODEL_DIR, "urgency_vectorizer.joblib")
MODEL_PATH = os.path.join(MODEL_DIR, "urgency_model.joblib")
META_PATH = os.path.join(MODEL_DIR, "urgency_metadata.json")
TRAINING_DATA_PATH = os.path.join(BASE_DIR, "urgency_training_data.csv")

# Urgency levels ordered by severity
URGENCY_LEVELS = ["low", "medium", "high", "critical"]

# Confidence threshold: below this → ChatGPT fallback
CONFIDENCE_THRESHOLD = 0.70

# ──────────────────────────────────────────────
# Mapping: frontend symptom keys → human-readable text
# Used to convert frontend checkbox IDs into text for TF-IDF
# ──────────────────────────────────────────────
FRONTEND_KEY_TO_TEXT = {
    # General / Systemic
    "fever": "fever",
    "fatigue": "fatigue",
    "malaise": "fatigue malaise",
    "weight_loss": "weight loss",
    "loss_of_appetite": "loss of appetite",
    "night_sweats": "night sweats",
    "chills": "chills",
    "generalized_pain": "pain generalized pain",
    "excessive_sweating": "excessive sweating",
    # Respiratory
    "cough": "cough",
    "cough_dry": "cough dry cough",
    "cough_productive": "productive cough",
    "shortness_of_breath": "shortness of breath",
    "wheezing": "wheezing",
    "chest_tightness": "chest tightness",
    "sore_throat": "sore throat",
    "nasal_congestion": "nasal congestion",
    "runny_nose": "runny nose",
    "sneezing": "sneezing",
    "hoarseness": "hoarseness",
    # Cardiovascular
    "palpitations": "palpitations",
    "chest_pain": "chest pain",
    "syncope": "fainting syncope",
    # Gastrointestinal
    "abdominal_pain": "abdominal pain",
    "nausea": "nausea",
    "vomiting": "vomiting",
    "diarrhea": "diarrhea",
    "constipation": "constipation",
    "bloating": "bloating",
    "heartburn": "heartburn",
    "dysphagia": "difficulty swallowing",
    # Neurological
    "headache": "headache",
    "dizziness": "dizziness",
    "numbness": "numbness",
    "limb_weakness": "muscle weakness limb weakness",
    "coordination_loss": "loss of coordination",
    "memory_loss": "confusion memory loss",
    "seizures": "seizures",
    "sleep_disturbances": "sleep disturbances",
    # Psychiatric
    "anxiety": "anxiety",
    "depression": "depression",
    # Sensory
    "photophobia": "light sensitivity photophobia",
    "vision_changes": "vision changes",
    "hearing_changes": "hearing changes",
    "eye_pain": "eye pain",
    "ear_pain": "ear pain",
    # Musculoskeletal
    "muscle_pain": "muscle pain",
    "muscle_weakness": "muscle weakness",
    "joint_pain": "joint pain",
    "joint_swelling": "swelling joint swelling",
    "back_pain": "back pain",
    # Dermatological
    "skin_rash": "rash skin rash",
    "itching": "itching",
    "bruising": "bruising",
    "swelling": "swelling",
    # Genitourinary
    "frequent_urination": "frequent urination",
    "painful_urination": "painful urination",
    "blood_in_urine": "blood in urine",
    # Endocrine
    "excessive_thirst": "excessive thirst",
    # ENT
    "pharyngitis": "sore throat pharyngitis",
    "swollen_lymph_nodes": "swollen lymph nodes",
    # COVID/Flu-specific
    "loss_of_taste": "loss of taste",
    "loss_of_smell": "loss of smell",
}


def _symptoms_dict_to_text(symptoms: dict) -> str:
    """
    Convert a frontend symptom dictionary (with has_* boolean flags)
    into a space-separated text string suitable for TF-IDF vectorization.

    Also includes the free-text 'description' field if present.
    """
    parts = []

    for key, value in symptoms.items():
        if not value:
            continue
        # Strip "has_" prefix if present
        clean = key.replace("has_", "") if key.startswith("has_") else key
        text = FRONTEND_KEY_TO_TEXT.get(clean)
        if text:
            parts.append(text)

    # Include free-text description
    description = symptoms.get("description", "")
    if description:
        parts.append(description.lower())

    return " ".join(parts)


def _symptom_list_to_text(symptoms: List[str]) -> str:
    """
    Convert a list of symptom names/strings into a single text string
    for TF-IDF vectorization.

    Examples:
        ["fever", "chest pain", "shortness of breath"]
        → "fever chest pain shortness of breath"
    """
    return " ".join(s.lower().strip() for s in symptoms if s)


# ──────────────────────────────────────────────
# Training
# ──────────────────────────────────────────────

def load_training_data(path: str = TRAINING_DATA_PATH) -> Tuple[List[str], List[str]]:
    """
    Load the urgency training CSV.
    Returns (texts, labels) where texts are symptom strings and labels are urgency levels.
    """
    df = pd.read_csv(path)
    texts = df["symptoms"].tolist()
    labels = df["urgency"].tolist()
    print(f"✅ Loaded {len(texts)} training examples from {os.path.basename(path)}")
    label_counts = pd.Series(labels).value_counts()
    for level in URGENCY_LEVELS:
        count = label_counts.get(level, 0)
        print(f"   {level}: {count} examples")
    return texts, labels


def train_model(
    tune_hyperparams: bool = False,
    cv_folds: int = 5,
) -> Dict[str, Any]:
    """
    Train the urgency classifier from the training CSV.

    Steps:
    1. Load training data
    2. Fit TfidfVectorizer on symptom text
    3. Train RandomForestClassifier (with optional hyperparameter tuning)
    4. Evaluate with stratified cross-validation
    5. Save model, vectorizer, and metadata

    Parameters
    ----------
    tune_hyperparams : bool
        If True, run GridSearchCV for hyperparameter tuning (slower but better).
    cv_folds : int
        Number of cross-validation folds (default=5).

    Returns
    -------
    dict with training results (accuracy, cv scores, classification report).
    """
    texts, labels = load_training_data()

    # ── Step 1: TF-IDF Vectorization ──
    # Using unigrams and bigrams to capture symptom phrases like "chest pain"
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),       # Unigrams + bigrams
        max_features=500,         # Limit feature space
        stop_words="english",     # Remove common English words
        sublinear_tf=True,        # Apply sublinear TF scaling
        min_df=1,                 # Keep all terms (small dataset)
    )
    X = vectorizer.fit_transform(texts)
    y = np.array(labels)

    print(f"\n📊 TF-IDF matrix: {X.shape[0]} samples × {X.shape[1]} features")

    # ── Step 2: Model Training ──
    if tune_hyperparams:
        print("\n🔧 Running hyperparameter tuning (GridSearchCV)...")
        param_grid = {
            "n_estimators": [100, 200, 300, 500],
            "max_depth": [None, 10, 20, 30],
            "min_samples_split": [2, 3, 5],
            "min_samples_leaf": [1, 2],
            "class_weight": ["balanced", "balanced_subsample"],
        }
        base_rf = RandomForestClassifier(random_state=42, n_jobs=-1)
        grid_search = GridSearchCV(
            base_rf,
            param_grid,
            cv=StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=42),
            scoring="accuracy",
            n_jobs=-1,
            verbose=1,
        )
        grid_search.fit(X, y)
        model = grid_search.best_estimator_
        print(f"✅ Best parameters: {grid_search.best_params_}")
        print(f"✅ Best CV accuracy: {grid_search.best_score_:.4f}")
    else:
        # Default RandomForest with balanced class weights
        model = RandomForestClassifier(
            n_estimators=300,
            max_depth=None,
            min_samples_split=2,
            min_samples_leaf=1,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
            oob_score=True,
            bootstrap=True,
        )
        model.fit(X, y)

    # ── Step 3: Cross-Validation ──
    print(f"\n📈 {cv_folds}-fold stratified cross-validation...")
    cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=42)
    cv_scores = cross_val_score(model, X, y, cv=cv, scoring="accuracy")
    print(f"   CV Accuracy: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
    print(f"   Per-fold:    {[f'{s:.3f}' for s in cv_scores]}")

    # ── Step 4: Full-data evaluation ──
    y_pred = model.predict(X)
    train_acc = (y_pred == y).mean()
    print(f"\n🎯 Training accuracy: {train_acc:.4f}")

    report_dict = classification_report(y, y_pred, output_dict=True)
    report_text = classification_report(y, y_pred)
    print("\n📋 Classification Report:")
    print(report_text)

    cm = confusion_matrix(y, y_pred, labels=URGENCY_LEVELS)
    print("📊 Confusion Matrix:")
    print(f"   Labels: {URGENCY_LEVELS}")
    for i, row in enumerate(cm):
        print(f"   {URGENCY_LEVELS[i]:>8}: {row}")

    # OOB score (only available when bootstrap=True and no tuning)
    oob = getattr(model, "oob_score_", None)
    if oob is not None:
        print(f"\n📈 OOB accuracy: {oob:.4f}")

    # Top TF-IDF features by importance
    feature_names = vectorizer.get_feature_names_out()
    importances = model.feature_importances_
    top_features = sorted(
        zip(feature_names, importances), key=lambda x: x[1], reverse=True
    )[:20]
    print("\n🔬 Top 20 important TF-IDF features:")
    for fname, imp in top_features:
        print(f"   {fname:>30}: {imp:.4f}")

    # ── Step 5: Save model, vectorizer, metadata ──
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(vectorizer, VECTORIZER_PATH)
    joblib.dump(model, MODEL_PATH)
    print(f"\n💾 Vectorizer saved: {VECTORIZER_PATH}")
    print(f"💾 Model saved: {MODEL_PATH}")

    metadata = {
        "urgency_levels": URGENCY_LEVELS,
        "n_training_samples": len(texts),
        "n_features": X.shape[1],
        "train_accuracy": float(train_acc),
        "cv_accuracy_mean": float(cv_scores.mean()),
        "cv_accuracy_std": float(cv_scores.std()),
        "oob_accuracy": float(oob) if oob is not None else None,
        "confidence_threshold": CONFIDENCE_THRESHOLD,
        "model_type": "RandomForestClassifier",
        "vectorizer_type": "TfidfVectorizer",
        "ngram_range": [1, 2],
        "per_class_f1": {
            level: round(report_dict.get(level, {}).get("f1-score", 0), 4)
            for level in URGENCY_LEVELS
        },
    }
    with open(META_PATH, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"💾 Metadata saved: {META_PATH}")

    print("\n✅ Urgency classifier training complete!")
    return metadata


# ──────────────────────────────────────────────
# Classifier Class
# ──────────────────────────────────────────────

class UrgencyClassifier:
    """
    ML-based symptom urgency classifier.

    Loads a pre-trained TfidfVectorizer + RandomForestClassifier.
    Predicts urgency level (low, medium, high, critical) from symptoms.
    Falls back to ChatGPT API when prediction confidence is below threshold.
    """

    def __init__(self, confidence_threshold: float = CONFIDENCE_THRESHOLD):
        """
        Initialize the classifier.

        Parameters
        ----------
        confidence_threshold : float
            If the highest prediction probability is below this value,
            fall back to ChatGPT. Default = 0.70.
        """
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.model: Optional[RandomForestClassifier] = None
        self.metadata: Optional[dict] = None
        self.confidence_threshold = confidence_threshold
        self.is_loaded = False
        self._openai_client = None

        self._load_model()

    def _load_model(self):
        """Load pre-trained vectorizer and model from disk."""
        if not os.path.exists(VECTORIZER_PATH) or not os.path.exists(MODEL_PATH):
            print("⚠️  Urgency classifier not trained — run: python -m ml.urgency_classifier --train")
            return

        try:
            self.vectorizer = joblib.load(VECTORIZER_PATH)
            self.model = joblib.load(MODEL_PATH)
            if os.path.exists(META_PATH):
                with open(META_PATH, "r") as f:
                    self.metadata = json.load(f)
            self.is_loaded = True
            print(f"✅ UrgencyClassifier loaded (threshold={self.confidence_threshold})")
        except Exception as e:
            print(f"❌ Failed to load urgency classifier: {e}")
            self.is_loaded = False

    # ── ML Prediction ──

    def predict_ml(self, symptom_text: str) -> Optional[Dict[str, Any]]:
        """
        Run the ML model on a symptom text string.

        Parameters
        ----------
        symptom_text : str
            Space-separated symptom description (e.g. "fever chest pain shortness of breath").

        Returns
        -------
        dict with keys: urgency, confidence, probabilities, method
        or None if model is not loaded or text is empty.
        """
        if not self.is_loaded or not symptom_text.strip():
            return None

        # Vectorize input
        X = self.vectorizer.transform([symptom_text])

        # Get prediction probabilities
        probabilities = self.model.predict_proba(X)[0]
        classes = self.model.classes_

        # Build probabilities dict
        prob_dict = {cls: round(float(prob), 4) for cls, prob in zip(classes, probabilities)}

        # Get top prediction
        top_idx = np.argmax(probabilities)
        predicted_urgency = classes[top_idx]
        confidence = float(probabilities[top_idx])

        return {
            "urgency": predicted_urgency,
            "confidence": round(confidence, 4),
            "probabilities": prob_dict,
            "method": "ml",
        }

    # ── ChatGPT Fallback ──

    def _get_openai_client(self):
        """Lazy-initialize the OpenAI client."""
        if self._openai_client is None:
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.getenv("CHATGPT_API_KEY")
            if not api_key:
                raise RuntimeError(
                    "CHATGPT_API_KEY not set in .env — required for low-confidence fallback. "
                    "Set it in backend/.env or export it as an environment variable."
                )
            from openai import OpenAI
            self._openai_client = OpenAI(api_key=api_key)
        return self._openai_client

    def predict_chatgpt(self, symptom_text: str) -> Dict[str, Any]:
        """
        Call ChatGPT to classify urgency when ML confidence is low.

        Parameters
        ----------
        symptom_text : str
            Human-readable symptom description.

        Returns
        -------
        dict with keys: urgency, confidence, probabilities, method, model_used
        """
        try:
            client = self._get_openai_client()
            model_name = os.getenv("CHATGPT_MODEL", "gpt-4o")

            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a medical triage assistant. Given a list of symptoms, "
                            "classify the urgency into EXACTLY one of: low, medium, high, critical.\n\n"
                            "Definitions:\n"
                            "- low: Minor conditions manageable with self-care (e.g., common cold, mild headache, dry skin).\n"
                            "- medium: Conditions needing a doctor visit within days (e.g., UTI, bronchitis, moderate infection).\n"
                            "- high: Urgent conditions needing prompt medical attention (e.g., pneumonia, appendicitis, kidney infection).\n"
                            "- critical: Life-threatening emergencies requiring immediate ER/911 (e.g., heart attack, stroke, sepsis).\n\n"
                            "Respond ONLY in this JSON format:\n"
                            '{"urgency": "<level>", "confidence": <0.0-1.0>, "reasoning": "<brief explanation>"}'
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"Patient symptoms: {symptom_text}\n\nClassify the urgency level.",
                    },
                ],
                temperature=0.2,
                max_tokens=200,
                response_format={"type": "json_object"},
            )

            raw = response.choices[0].message.content
            result = json.loads(raw)

            urgency = result.get("urgency", "medium").lower()
            # Validate urgency level
            if urgency not in URGENCY_LEVELS:
                urgency = "medium"

            confidence = float(result.get("confidence", 0.5))
            reasoning = result.get("reasoning", "")

            return {
                "urgency": urgency,
                "confidence": round(confidence, 4),
                "probabilities": {level: (confidence if level == urgency else round((1 - confidence) / 3, 4)) for level in URGENCY_LEVELS},
                "method": "chatgpt",
                "model_used": model_name,
                "reasoning": reasoning,
            }

        except Exception as e:
            print(f"❌ ChatGPT urgency fallback error: {e}")
            # Safe default: return medium urgency with zero confidence
            return {
                "urgency": "medium",
                "confidence": 0.0,
                "probabilities": {level: 0.25 for level in URGENCY_LEVELS},
                "method": "chatgpt_error",
                "error": str(e),
            }

    # ── Main Predict (ML first → ChatGPT fallback) ──

    def predict(self, symptoms, description: str = "") -> Dict[str, Any]:
        """
        Predict urgency from symptoms.

        Accepts symptoms in multiple formats:
        - List[str]: ["fever", "chest pain", "shortness of breath"]
        - dict: frontend symptom dict with has_* boolean keys
        - str: raw symptom text

        Pipeline:
        1. Convert symptoms → text
        2. Run ML prediction
        3. If confidence < threshold → call ChatGPT
        4. Return result

        Parameters
        ----------
        symptoms : list, dict, or str
            Patient symptoms in any supported format.
        description : str
            Optional free-text description (used with dict input).

        Returns
        -------
        dict with keys:
            urgency (str), confidence (float), probabilities (dict),
            method (str), fallback_reason (str|None)
        """
        # ── Step 1: Convert to text ──
        if isinstance(symptoms, list):
            symptom_text = _symptom_list_to_text(symptoms)
        elif isinstance(symptoms, dict):
            # Add description to dict if provided separately
            if description and "description" not in symptoms:
                symptoms = {**symptoms, "description": description}
            symptom_text = _symptoms_dict_to_text(symptoms)
        elif isinstance(symptoms, str):
            symptom_text = symptoms.lower().strip()
        else:
            symptom_text = str(symptoms).lower().strip()

        if not symptom_text:
            return {
                "urgency": "medium",
                "confidence": 0.0,
                "probabilities": {level: 0.25 for level in URGENCY_LEVELS},
                "method": "none",
                "fallback_reason": "No symptoms provided",
            }

        # ── Step 2: ML prediction ──
        ml_result = self.predict_ml(symptom_text)

        # ── Step 3: Check confidence and decide fallback ──
        use_chatgpt = False
        fallback_reason = None

        if ml_result is None:
            use_chatgpt = True
            fallback_reason = "ML model not loaded"
        elif ml_result["confidence"] < self.confidence_threshold:
            use_chatgpt = True
            fallback_reason = (
                f"ML confidence {ml_result['confidence']:.2f} "
                f"< threshold {self.confidence_threshold:.2f}"
            )

        # ── Step 4: ChatGPT fallback if needed ──
        if use_chatgpt:
            print(f"🤖 Urgency ChatGPT fallback: {fallback_reason}")
            chatgpt_result = self.predict_chatgpt(symptom_text)
            chatgpt_result["fallback_reason"] = fallback_reason
            chatgpt_result["ml_result"] = ml_result
            return chatgpt_result

        # ML result is confident enough
        ml_result["fallback_reason"] = None
        return ml_result

    # ── Convenience: predict from frontend symptom dict ──

    def predict_from_frontend(self, symptoms: dict) -> Dict[str, Any]:
        """
        Predict urgency from a frontend symptom dictionary.
        This is the integration point for symptom_predictor.py.

        Parameters
        ----------
        symptoms : dict
            Frontend symptom dict with has_* boolean keys and optional 'description'.

        Returns
        -------
        dict with urgency prediction result.
        """
        return self.predict(symptoms)


# ──────────────────────────────────────────────
# CLI Entry Point
# ──────────────────────────────────────────────

def main():
    """CLI for training and testing the urgency classifier."""
    parser = argparse.ArgumentParser(description="Symptom Urgency Classifier")
    parser.add_argument("--train", action="store_true", help="Train the model from urgency_training_data.csv")
    parser.add_argument("--tune", action="store_true", help="Enable hyperparameter tuning (GridSearchCV)")
    parser.add_argument("--folds", type=int, default=5, help="Number of CV folds (default=5)")
    parser.add_argument("--test", action="store_true", help="Run test predictions")
    parser.add_argument("--evaluate", action="store_true", help="Show detailed evaluation metrics")
    args = parser.parse_args()

    if args.train or args.tune:
        print("=" * 60)
        print("TRAINING URGENCY CLASSIFIER")
        print("=" * 60)
        result = train_model(tune_hyperparams=args.tune, cv_folds=args.folds)
        print(f"\n📊 Summary:")
        print(f"   Train Accuracy:  {result['train_accuracy']:.4f}")
        print(f"   CV Accuracy:     {result['cv_accuracy_mean']:.4f} ± {result['cv_accuracy_std']:.4f}")
        if result.get("oob_accuracy"):
            print(f"   OOB Accuracy:    {result['oob_accuracy']:.4f}")
        print(f"   Per-class F1:    {result['per_class_f1']}")

    if args.test or (not args.train and not args.tune and not args.evaluate):
        print("\n" + "=" * 60)
        print("TEST PREDICTIONS")
        print("=" * 60)

        clf = UrgencyClassifier()
        if not clf.is_loaded:
            print("❌ Model not trained. Run with --train first.")
            return

        test_cases = [
            # Critical cases
            {
                "name": "Heart attack symptoms",
                "symptoms": ["chest pain", "shortness of breath", "excessive sweating", "nausea", "jaw pain"],
            },
            {
                "name": "Stroke symptoms",
                "symptoms": ["sudden confusion", "numbness", "loss of coordination", "severe headache", "slurred speech"],
            },
            # High cases
            {
                "name": "Pneumonia symptoms",
                "symptoms": ["fever", "productive cough", "chest pain", "shortness of breath", "chills"],
            },
            {
                "name": "Appendicitis symptoms",
                "symptoms": ["fever", "severe abdominal pain", "nausea", "vomiting", "loss of appetite"],
            },
            # Medium cases
            {
                "name": "UTI symptoms",
                "symptoms": ["painful urination", "frequent urination", "abdominal pain", "fever", "cloudy urine"],
            },
            {
                "name": "Migraine symptoms",
                "symptoms": ["headache", "nausea", "light sensitivity", "dizziness"],
            },
            # Low cases
            {
                "name": "Common cold",
                "symptoms": ["mild fever", "runny nose", "sneezing", "sore throat", "fatigue"],
            },
            {
                "name": "Mild headache",
                "symptoms": ["mild headache", "neck tension", "pressure"],
            },
            # Edge cases
            {
                "name": "Mixed severity symptoms",
                "symptoms": ["fever", "headache", "fatigue"],
            },
            {
                "name": "Single vague symptom",
                "symptoms": ["fatigue"],
            },
        ]

        for case in test_cases:
            result = clf.predict(case["symptoms"])
            urgency = result["urgency"]
            confidence = result["confidence"]
            method = result["method"]
            fallback = result.get("fallback_reason", "")
            indicator = {"low": "🟢", "medium": "🟡", "high": "🟠", "critical": "🔴"}.get(urgency, "⚪")
            print(f"\n{indicator} {case['name']}")
            print(f"   Symptoms:   {', '.join(case['symptoms'])}")
            print(f"   Urgency:    {urgency} ({confidence:.0%})")
            print(f"   Method:     {method}")
            if fallback:
                print(f"   Fallback:   {fallback}")
            print(f"   Probabilities: {result['probabilities']}")


if __name__ == "__main__":
    main()
