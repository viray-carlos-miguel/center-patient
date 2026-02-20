#!/usr/bin/env python3
"""Retrain the ML model and verify predictions with emergency + medication output."""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from ml.prediction_engine import MedicalPredictionEngine

def main():
    print("=" * 70)
    print("  RETRAINING ML MODEL")
    print("=" * 70)

    engine = MedicalPredictionEngine()
    result = engine.train(n_samples=8000)

    print(f"\n Training complete!")
    print(f"   Accuracy: {result['accuracy']}%")
    print(f"   CV Accuracy: {result['cv_accuracy']}% +/- {result['cv_std']}%")
    print(f"   Diseases: {result['n_diseases']}")

    # ---------- diverse test cases ----------
    tests = [
        ("Flu (fever+chills+body aches+cough)", {
            "description": "high fever, chills, body aches, cough, fatigue",
            "severity": 7, "duration_hours": 48, "temperature": 39.0, "age": 30, "gender": 0,
            "fever": True, "cough": True, "fatigue": True, "body_aches": True, "chills": True,
        }),
        ("COVID-19 (loss of taste/smell)", {
            "description": "fever, dry cough, fatigue, loss of taste and smell",
            "severity": 5, "duration_hours": 120, "temperature": 38.2, "age": 35, "gender": 1,
            "fever": True, "dry_cough": True, "fatigue": True, "loss_of_taste": True, "loss_of_smell": True,
        }),
        ("Heart Attack (chest pain+breath)", {
            "description": "chest pain, shortness of breath, sweating, nausea",
            "severity": 10, "duration_hours": 2, "temperature": 37.0, "age": 58, "gender": 1,
            "chest_pain": True, "shortness_of_breath": True, "sweating": True, "nausea": True,
        }),
        ("Migraine (headache+nausea+vision)", {
            "description": "severe headache, nausea, blurred vision",
            "severity": 7, "duration_hours": 12, "temperature": 36.8, "age": 32, "gender": 0,
            "severe_headache": True, "headache": True, "nausea": True, "blurred_vision": True,
        }),
        ("Gastroenteritis (vomit+diarrhea)", {
            "description": "nausea, vomiting, diarrhea, stomach pain",
            "severity": 6, "duration_hours": 18, "temperature": 38.0, "age": 25, "gender": 0,
            "nausea": True, "vomiting": True, "diarrhea": True, "abdominal_pain": True,
        }),
        ("Allergic Rhinitis (sneezing+runny)", {
            "description": "sneezing, runny nose, congestion, itchy eyes",
            "severity": 2, "duration_hours": 168, "temperature": 36.5, "age": 28, "gender": 1,
            "sneezing": True, "runny_nose": True, "nasal_congestion": True, "itching": True,
        }),
        ("Appendicitis (abdom pain+nausea)", {
            "description": "sharp abdominal pain, nausea, vomiting, fever",
            "severity": 9, "duration_hours": 18, "temperature": 38.5, "age": 22, "gender": 0,
            "abdominal_pain": True, "nausea": True, "vomiting": True, "fever": True, "loss_of_appetite": True,
        }),
        ("Common Cold (runny+sore throat)", {
            "description": "runny nose, sore throat, sneezing, mild cough",
            "severity": 2, "duration_hours": 72, "temperature": 37.2, "age": 30, "gender": 1,
            "runny_nose": True, "sore_throat": True, "sneezing": True, "cough": True,
        }),
    ]

    print("\n" + "=" * 70)
    print("  PREDICTION TESTS")
    print("=" * 70)

    for label, syms in tests:
        r = engine.predict(syms)
        top = r["predictions"][0]
        em = r["emergency"]
        meds = top.get("medications", [])
        med_names = ", ".join(m["name"] for m in meds[:2]) if meds else "N/A"
        print(f"\n{label}")
        print(f"  -> {top['disease']} ({top['confidence']}%)")
        print(f"  Emergency: {em['label']} ({em['level']}) | Hospital: {'YES' if em['go_to_hospital'] else 'No'}")
        print(f"  Meds: {med_names}")
        if em["go_to_hospital"]:
            msg = em.get("hospital_message", "")
            print(f"  !! {msg[:80]}")

    print("\nDone!")

if __name__ == "__main__":
    main()
