"""
Train a Random Forest classifier on disease_symptom_dataset.csv.
Saves:
  - ml/trained_model/symptom_rf_model.joblib   (the classifier)
  - ml/trained_model/model_metadata.json        (feature names, classes, accuracy, mapping)
"""

import os, json, sys, csv
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.preprocessing import LabelEncoder
import joblib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "disease_symptom_dataset.csv")
MODEL_DIR = os.path.join(BASE_DIR, "trained_model")


def _load_dataset():
    """Load CSV handling potential header/data column count mismatch."""
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)

    # Determine widest row
    max_cols = max(len(header), max(len(r) for r in rows))

    # Pad header if data rows are wider
    if len(header) < max_cols:
        extra = max_cols - len(header)
        # Insert extra symptom columns before the last header field (UrgencyLevel)
        urgency_hdr = header[-1]  # "UrgencyLevel"
        base_symptoms = header[1:-1]
        for i in range(1, extra + 1):
            base_symptoms.append(f"ExtraSymptom_{i}")
        header = [header[0]] + base_symptoms + [urgency_hdr]
        print(f"⚠️  Padded header with {extra} extra column(s) → {len(header)} columns")

    # Pad short rows
    for i, row in enumerate(rows):
        if len(row) < len(header):
            rows[i] = row + ["0"] * (len(header) - len(row))

    df = pd.DataFrame(rows, columns=header)

    # Convert symptom columns to int (everything between Disease and UrgencyLevel)
    symptom_cols = header[1:-1]
    for c in symptom_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)

    return df, symptom_cols


def train():
    # ---- Load dataset ----
    df, feature_cols = _load_dataset()
    print(f"✅ Loaded dataset: {df.shape[0]} rows, {df.shape[1]} columns, {len(feature_cols)} features")

    disease_col = "Disease"
    urgency_col = "UrgencyLevel"

    X = df[feature_cols].values.astype(int)
    y_disease = df[disease_col].values

    # Urgency mapping (keep for metadata)
    urgency_map = dict(zip(df[disease_col], df[urgency_col]))

    # Encode disease labels
    le = LabelEncoder()
    y_encoded = le.fit_transform(y_disease)

    print(f"📊 Features: {len(feature_cols)}")
    print(f"🏥 Diseases: {len(le.classes_)}")
    print(f"   Classes: {list(le.classes_)}")

    # ---- Train Random Forest ----
    # Note: dataset has 1 sample per disease, so cross-validation is not feasible.
    # We use oob_score as a proxy quality metric and train on the full dataset.
    rf = RandomForestClassifier(
        n_estimators=500,
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        random_state=42,
        class_weight="balanced",
        oob_score=True,
        bootstrap=True,
        n_jobs=-1,
    )

    rf.fit(X, y_encoded)
    train_acc = rf.score(X, y_encoded)
    oob_acc = rf.oob_score_
    print(f"🎯 Training accuracy: {train_acc:.2%}")
    print(f"📈 OOB accuracy (proxy for generalization): {oob_acc:.2%}")

    # Feature importances
    importances = rf.feature_importances_
    top_features = sorted(zip(feature_cols, importances), key=lambda x: x[1], reverse=True)[:15]
    print("🔬 Top 15 important features:")
    for fname, imp in top_features:
        print(f"   {fname}: {imp:.4f}")

    # ---- Save model ----
    os.makedirs(MODEL_DIR, exist_ok=True)
    model_path = os.path.join(MODEL_DIR, "symptom_rf_model.joblib")
    joblib.dump(rf, model_path)
    print(f"💾 Model saved: {model_path}")

    # ---- Save metadata ----
    # Convert all values to plain Python types for JSON serialization
    metadata = {
        "feature_columns": list(feature_cols),
        "classes": [str(c) for c in le.classes_],
        "urgency_map": {str(k): str(v) for k, v in urgency_map.items()},
        "oob_accuracy": float(oob_acc),
        "train_accuracy": float(train_acc),
        "n_estimators": 200,
        "n_features": len(feature_cols),
        "n_classes": len(le.classes_),
    }
    meta_path = os.path.join(MODEL_DIR, "model_metadata.json")
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"💾 Metadata saved: {meta_path}")

    print("\n✅ Training complete!")
    return rf, metadata


if __name__ == "__main__":
    train()
