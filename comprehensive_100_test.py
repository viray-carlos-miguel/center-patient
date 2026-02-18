#!/usr/bin/env python3
"""Comprehensive 100-case test suite (basic + complex diseases).

This script stress-tests the current hybrid predictor (rule-based + ML fallback)
with a larger set of cases:
- 50 cases: the 8 in-scope conditions with multiple variations (accuracy expected high)
- 50 cases: out-of-scope / complex diseases (system should safely fall back)

It reports:
- In-scope accuracy
- Out-of-scope safe-fallback rate (General Medical Assessment)
- Overall stability (no crashes)

Run:
  python comprehensive_100_test.py
"""

import os
import sys
import asyncio
import random
from dataclasses import dataclass
from typing import Dict, Any, List, Tuple

import numpy as np

# Ensure backend is on path
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(ROOT, "backend"))

from guaranteed_accuracy_solution import GuaranteedAccuracySystem


@dataclass
class Case:
    expected: str
    symptoms: Dict[str, Any]
    in_scope: bool
    category: str


IN_SCOPE_CONDITIONS = [
    "COVID-19",
    "Influenza",
    "Pneumonia",
    "Gastroenteritis",
    "Migraine",
    "Tension Headache",
    "Urinary Tract Infection",
    "Anxiety Disorder",
]


def _base_symptom_payload(description: str, symptoms_list: List[str], **overrides) -> Dict[str, Any]:
    payload = {
        "description": description,
        "symptoms": symptoms_list,
        "temperature": overrides.pop("temperature", 37.0),
        "duration_hours": overrides.pop("duration_hours", 72),
        "severity": overrides.pop("severity", 5),
        "age": overrides.pop("age", 35),
        "gender": overrides.pop("gender", "female"),
    }
    payload.update(overrides)
    return payload


def build_in_scope_cases() -> List[Case]:
    cases: List[Case] = []

    covid_variants = [
        ("covid-19 loss of taste loss of smell dry cough fever", ["covid", "loss of taste", "loss of smell", "dry cough"], 38.2, 6),
        ("sars-cov-2 coronavirus anosmia ageusia fatigue", ["sars-cov-2", "anosmia", "ageusia", "fatigue"], 37.8, 5),
        ("covid coronavirus taste loss smell loss shortness of breath", ["covid", "taste loss", "smell loss", "shortness of breath"], 38.6, 7),
        ("covid-19 anosmia mild cough low fever", ["covid-19", "anosmia", "mild cough"], 37.6, 4),
        ("coronavirus ageusia fever fatigue", ["coronavirus", "ageusia", "fever", "fatigue"], 38.0, 5),
        ("covid-19 loss of smell dry cough", ["covid", "loss of smell", "dry cough"], 38.1, 5),
    ]

    flu_variants = [
        ("influenza body aches high fever chills headache", ["influenza", "body aches", "high fever", "chills"], 39.2, 8),
        ("flu myalgia chills malaise", ["flu", "myalgia", "chills", "malaise"], 38.9, 7),
        ("h1n1 influenza muscle pain high fever", ["h1n1", "influenza", "muscle pain", "high fever"], 39.5, 8),
        ("influenza chills fatigue body aches", ["influenza", "chills", "fatigue", "body aches"], 38.8, 6),
        ("flu body aches severe headache", ["flu", "body aches", "severe headache"], 39.0, 7),
        ("influenza myalgia fever chills", ["influenza", "myalgia", "fever", "chills"], 39.1, 7),
    ]

    pneumonia_variants = [
        ("pneumonia productive cough chest pain shortness of breath", ["pneumonia", "productive cough", "chest pain"], 39.7, 9),
        ("lung infection pneumonia crackles dyspnea", ["lung infection", "pneumonia", "crackles", "dyspnea"], 39.5, 8),
        ("pneumonia consolidation crackles chest pain", ["pneumonia", "consolidation", "crackles", "chest pain"], 39.6, 9),
        ("pneumonia productive cough high fever", ["pneumonia", "productive cough", "high fever"], 39.2, 8),
        ("lung infection pneumonia shortness of breath", ["lung infection", "pneumonia", "shortness of breath"], 39.1, 7),
        ("pneumonia dyspnea productive cough", ["pneumonia", "dyspnea", "productive cough"], 39.4, 8),
    ]

    gastro_variants = [
        ("gastroenteritis watery diarrhea vomiting nausea", ["gastroenteritis", "watery diarrhea", "vomiting"], 38.2, 6),
        ("stomach flu gi infection vomiting nausea", ["stomach flu", "gi infection", "vomiting", "nausea"], 38.0, 5),
        ("gastroenteritis diarrhea vomiting stomach cramps", ["gastroenteritis", "diarrhea", "vomiting", "stomach cramps"], 37.9, 5),
        ("gi infection gastroenteritis vomiting diarrhea", ["gi infection", "gastroenteritis", "vomiting", "diarrhea"], 38.1, 6),
        ("stomach flu nausea vomiting abdominal cramps", ["stomach flu", "nausea", "vomiting", "abdominal cramps"], 37.7, 4),
        ("gastroenteritis watery diarrhea abdominal pain", ["gastroenteritis", "watery diarrhea", "abdominal pain"], 37.8, 5),
    ]

    migraine_variants = [
        ("migraine unilateral throbbing photophobia light sensitivity", ["migraine", "unilateral", "throbbing", "photophobia"], 36.8, 8),
        ("migraine aura unilateral headache phonophobia", ["migraine", "aura", "unilateral headache", "phonophobia"], 36.9, 7),
        ("migraine photophobia phonophobia unilateral pain nausea", ["migraine", "photophobia", "phonophobia", "unilateral pain"], 36.7, 7),
        ("migraine throbbing headache light sensitivity", ["migraine", "throbbing headache", "light sensitivity"], 36.9, 6),
        ("migraine unilateral sound sensitivity", ["migraine", "unilateral", "sound sensitivity"], 36.8, 7),
        ("migraine unilateral throbbing light sensitivity", ["migraine", "unilateral", "throbbing", "light sensitivity"], 36.8, 7),
    ]

    tension_variants = [
        ("tension headache bilateral pressure band-like neck pain", ["tension", "bilateral", "pressure", "neck pain"], 36.9, 4),
        ("stress headache tension bilateral scalp tenderness", ["stress headache", "tension", "bilateral", "scalp tenderness"], 37.0, 4),
        ("tension headache pressure sensation band-like", ["tension", "pressure sensation", "band-like"], 36.9, 3),
        ("tension bilateral headache neck pain stress", ["tension", "bilateral headache", "neck pain", "stress"], 36.8, 4),
        ("tension headache pressure bilateral mild", ["tension", "pressure", "bilateral", "mild pain"], 36.9, 2),
        ("tension headache bilateral pressure", ["tension", "bilateral", "pressure", "headache"], 36.9, 3),
    ]

    uti_variants = [
        ("uti burning urination frequency urgency dysuria", ["uti", "burning urination", "frequency", "urgency"], 37.6, 5),
        ("urinary tract infection frequency urgency suprapubic pain", ["urinary tract infection", "frequency", "urgency", "suprapubic pain"], 37.8, 6),
        ("uti bladder infection burning urination hematuria", ["uti", "bladder infection", "burning urination", "hematuria"], 37.5, 5),
        ("uti dysuria frequency urgency pelvic pain", ["uti", "dysuria", "frequency", "urgency", "pelvic pain"], 37.7, 5),
        ("urinary tract infection cloudy urine urgency", ["urinary tract infection", "cloudy urine", "urgency"], 37.4, 4),
        ("uti painful urination frequency urgency", ["uti", "painful urination", "frequency", "urgency"], 37.6, 5),
    ]

    anxiety_variants = [
        ("anxiety panic attack palpitations heart racing", ["anxiety", "panic attack", "palpitations", "heart racing"], 37.0, 5),
        ("anxiety disorder nervousness restlessness trembling", ["anxiety disorder", "nervousness", "restlessness", "trembling"], 36.9, 4),
        ("anxiety palpitations shortness of breath chest tightness", ["anxiety", "palpitations", "shortness of breath", "chest tightness"], 37.1, 5),
        ("panic attack anxiety heart racing sweating dizziness", ["panic attack", "anxiety", "heart racing", "sweating", "dizziness"], 37.0, 6),
        ("anxiety disorder nervousness worry sleep problems", ["anxiety disorder", "nervousness", "worry", "sleep problems"], 36.8, 4),
        ("anxiety palpitations trembling shortness of breath", ["anxiety", "palpitations", "trembling", "shortness of breath"], 37.0, 5),
        ("anxiety panic attack heart racing nervousness", ["anxiety", "panic attack", "heart racing", "nervousness"], 36.9, 5),
    ]

    def add(condition: str, variant: Tuple[str, List[str], float, int]):
        desc, sym, temp, sev = variant
        cases.append(
            Case(
                expected=condition,
                symptoms=_base_symptom_payload(
                    desc,
                    sym,
                    temperature=temp,
                    severity=sev,
                    age=random.randint(18, 80),
                    gender=random.choice(["male", "female"]),
                    duration_hours=random.choice([24, 48, 72, 96, 120, 168]),
                ),
                in_scope=True,
                category="in_scope",
            )
        )

    for v in covid_variants:
        add("COVID-19", v)
    for v in flu_variants:
        add("Influenza", v)
    for v in pneumonia_variants:
        add("Pneumonia", v)
    for v in gastro_variants:
        add("Gastroenteritis", v)
    for v in migraine_variants:
        add("Migraine", v)
    for v in tension_variants:
        add("Tension Headache", v)
    for v in uti_variants:
        add("Urinary Tract Infection", v)
    for v in anxiety_variants:
        add("Anxiety Disorder", v)

    # We currently have 6+6+6+6+6+6+6+7 = 49 cases; add one more COVID case to make 50
    cases.append(
        Case(
            expected="COVID-19",
            symptoms=_base_symptom_payload(
                "covid-19 coronavirus anosmia loss of smell fever",
                ["covid-19", "coronavirus", "anosmia", "loss of smell", "fever"],
                temperature=38.4,
                severity=6,
                age=41,
                gender="female",
                duration_hours=96,
            ),
            in_scope=True,
            category="in_scope",
        )
    )

    return cases


def build_out_of_scope_cases() -> List[Case]:
    # 50 out-of-scope cases spanning basic + complex diseases.
    # Expected behavior: mostly safe fallback to General Medical Assessment.
    out: List[Case] = []

    def add(name: str, category: str, description: str, symptoms_list: List[str], temp: float, sev: int):
        out.append(
            Case(
                expected=name,
                symptoms=_base_symptom_payload(
                    description,
                    symptoms_list,
                    temperature=temp,
                    severity=sev,
                    age=random.randint(18, 85),
                    gender=random.choice(["male", "female"]),
                    duration_hours=random.choice([12, 24, 48, 72, 168, 336]),
                ),
                in_scope=False,
                category=category,
            )
        )

    # Respiratory (basic)
    add("Bronchitis", "respiratory", "bronchitis persistent cough mucus chest tightness", ["bronchitis", "persistent cough", "mucus"], 37.7, 5)
    add("Asthma", "respiratory", "asthma wheezing shortness of breath chest tightness", ["asthma", "wheezing", "shortness of breath"], 37.0, 6)
    add("Sinusitis", "respiratory", "sinusitis facial pressure nasal congestion sinus headache", ["sinusitis", "facial pressure", "nasal congestion"], 37.4, 4)
    add("Allergic Rhinitis", "respiratory", "allergic rhinitis sneezing itchy eyes runny nose", ["sneezing", "itchy eyes", "runny nose"], 36.9, 3)
    add("Pulmonary Embolism", "respiratory", "pulmonary embolism sudden shortness of breath pleuritic chest pain", ["shortness of breath", "chest pain", "sudden onset"], 37.2, 9)

    # Cardio (complex)
    add("Myocardial Infarction", "cardiovascular", "crushing chest pain radiating to arm sweating nausea", ["chest pain", "sweating", "nausea"], 37.0, 10)
    add("Heart Failure", "cardiovascular", "heart failure leg swelling orthopnea fatigue", ["leg swelling", "orthopnea", "fatigue"], 37.1, 7)
    add("Arrhythmia", "cardiovascular", "arrhythmia palpitations irregular heartbeat dizziness", ["palpitations", "irregular heartbeat", "dizziness"], 36.8, 6)
    add("Pericarditis", "cardiovascular", "pericarditis sharp chest pain better leaning forward", ["sharp chest pain", "worse lying down"], 37.3, 7)
    add("Hypertensive Crisis", "cardiovascular", "very high blood pressure severe headache vision changes", ["severe headache", "vision changes"], 37.0, 8)

    # GI
    add("GERD", "gastrointestinal", "acid reflux heartburn regurgitation", ["heartburn", "regurgitation"], 36.9, 4)
    add("Peptic Ulcer", "gastrointestinal", "epigastric burning pain nausea worse when hungry", ["epigastric pain", "nausea"], 37.1, 6)
    add("Appendicitis", "gastrointestinal", "right lower quadrant abdominal pain fever nausea", ["abdominal pain", "nausea"], 38.3, 8)
    add("Gallstones", "gastrointestinal", "biliary colic right upper quadrant pain after fatty meals", ["right upper quadrant pain", "nausea"], 37.4, 7)
    add("Pancreatitis", "gastrointestinal", "severe epigastric pain radiating to back vomiting", ["severe abdominal pain", "vomiting"], 38.5, 9)

    # Neuro
    add("Stroke", "neurological", "stroke facial droop weakness slurred speech sudden", ["facial droop", "weakness", "slurred speech"], 37.2, 10)
    add("Meningitis", "neurological", "meningitis fever stiff neck photophobia", ["fever", "stiff neck", "photophobia"], 39.6, 10)
    add("Seizure", "neurological", "seizure convulsions confusion postictal", ["convulsions", "confusion"], 37.0, 9)
    add("Cluster Headache", "neurological", "cluster headache severe unilateral eye pain tearing", ["severe eye pain", "tearing"], 36.9, 9)
    add("Bell Palsy", "neurological", "bell palsy unilateral facial weakness inability to close eye", ["facial weakness", "drooping"], 37.0, 6)

    # Endocrine
    add("Diabetes Type 2", "endocrine", "diabetes fatigue blurred vision frequent urination", ["fatigue", "blurred vision", "frequent urination"], 37.1, 5)
    add("DKA", "endocrine", "diabetic ketoacidosis vomiting abdominal pain fruity breath", ["vomiting", "abdominal pain", "fruity breath"], 38.0, 10)
    add("Hyperthyroidism", "endocrine", "hyperthyroidism weight loss palpitations heat intolerance", ["weight loss", "palpitations", "heat intolerance"], 37.2, 6)
    add("Hypothyroidism", "endocrine", "hypothyroidism fatigue weight gain cold intolerance", ["fatigue", "weight gain", "cold intolerance"], 36.7, 4)
    add("Adrenal Crisis", "endocrine", "adrenal crisis severe weakness low blood pressure vomiting", ["severe weakness", "vomiting"], 37.8, 10)

    # MSK / Rheum
    add("Rheumatoid Arthritis", "musculoskeletal", "joint swelling morning stiffness fatigue", ["joint swelling", "morning stiffness"], 37.3, 6)
    add("Gout", "musculoskeletal", "gout sudden big toe pain redness swelling", ["big toe pain", "redness", "swelling"], 37.4, 8)
    add("Osteoarthritis", "musculoskeletal", "knee pain worse with activity stiffness", ["knee pain", "stiffness"], 37.0, 5)
    add("Fibromyalgia", "musculoskeletal", "widespread pain fatigue sleep problems", ["widespread pain", "fatigue", "sleep problems"], 36.9, 6)
    add("Septic Arthritis", "musculoskeletal", "hot swollen joint fever severe pain", ["hot swollen joint", "fever"], 38.7, 9)

    # Skin
    add("Eczema", "skin", "itchy rash dry skin eczema", ["itchy rash", "dry skin"], 37.0, 4)
    add("Psoriasis", "skin", "psoriasis scaly plaques itchy red skin", ["scaly plaques", "itching"], 37.1, 5)
    add("Cellulitis", "skin", "cellulitis red warm swollen skin fever", ["red skin", "warm", "swelling", "fever"], 38.4, 7)
    add("Shingles", "skin", "shingles painful rash blisters dermatomal", ["painful rash", "blisters"], 37.8, 7)
    add("Anaphylaxis", "skin", "anaphylaxis hives swelling throat tightness wheeze", ["hives", "throat tightness", "wheeze"], 37.0, 10)

    # Infectious
    add("Tuberculosis", "infectious", "tuberculosis weight loss night sweats persistent cough", ["weight loss", "night sweats", "persistent cough"], 37.9, 7)
    add("Hepatitis", "infectious", "hepatitis jaundice fatigue nausea abdominal pain", ["jaundice", "fatigue", "nausea"], 38.0, 6)
    add("Sepsis", "infectious", "sepsis high fever confusion low blood pressure", ["high fever", "confusion"], 40.0, 10)
    add("Malaria", "infectious", "malaria cyclic fevers chills sweats travel", ["fever", "chills", "sweats"], 39.4, 8)
    add("Dengue", "infectious", "dengue fever severe body aches rash", ["fever", "body aches", "rash"], 39.3, 8)

    # Mental health
    add("Depression", "mental_health", "depression sadness anhedonia sleep changes", ["sadness", "loss of interest", "sleep changes"], 36.8, 5)
    add("Bipolar Disorder", "mental_health", "bipolar mood swings decreased sleep high energy", ["mood swings", "decreased sleep", "high energy"], 36.9, 6)
    add("PTSD", "mental_health", "ptsd flashbacks hypervigilance nightmares", ["flashbacks", "nightmares", "hypervigilance"], 36.9, 6)
    add("Schizophrenia", "mental_health", "hallucinations delusions disorganized thinking", ["hallucinations", "delusions"], 37.0, 7)
    add("Panic Disorder", "mental_health", "panic attacks palpitations fear sweating", ["panic attacks", "palpitations", "fear"], 37.0, 7)

    # Other (heme/renal)
    add("Anemia", "other", "anemia fatigue weakness pale skin", ["fatigue", "weakness", "pale skin"], 36.7, 4)
    add("Kidney Disease", "other", "kidney disease swelling fatigue decreased urination", ["swelling", "fatigue", "decreased urination"], 37.1, 6)
    add("Kidney Stone", "other", "kidney stone flank pain hematuria nausea", ["flank pain", "hematuria", "nausea"], 37.2, 9)
    add("Liver Failure", "other", "liver failure jaundice confusion abdominal swelling", ["jaundice", "confusion", "abdominal swelling"], 37.6, 8)
    add("Cancer", "other", "unintentional weight loss night sweats fatigue", ["weight loss", "night sweats", "fatigue"], 37.3, 6)

    # Ensure exactly 50
    return out[:50]


async def run():
    random.seed(42)
    np.random.seed(42)

    system = GuaranteedAccuracySystem()

    cases = build_in_scope_cases() + build_out_of_scope_cases()
    assert len(cases) == 100
    random.shuffle(cases)

    # Metrics
    in_scope_total = 0
    in_scope_correct = 0
    out_scope_total = 0
    out_scope_safe_fallback = 0

    total = 0
    errors = 0

    confs: List[float] = []
    methods: dict = {"rule": 0, "ml": 0, "fallback": 0}

    # Run
    for idx, c in enumerate(cases, 1):
        total += 1
        try:
            res = await system.hybrid_predict(c.symptoms)
            pred = res.get("ml_prediction", {}).get("primary_condition", "Unknown")
            conf = float(res.get("ml_prediction", {}).get("confidence", 0.0) or 0.0)
            method = (res.get("ml_prediction", {}).get("prediction_method") or "").lower()

            confs.append(conf)
            if "rule" in method:
                methods["rule"] += 1
            elif "ml" in method:
                methods["ml"] += 1
            else:
                methods["fallback"] += 1

            if c.in_scope:
                in_scope_total += 1
                if pred == c.expected:
                    in_scope_correct += 1
            else:
                out_scope_total += 1
                if pred == "General Medical Assessment":
                    out_scope_safe_fallback += 1

            # Light per-case output every 10 cases to keep logs readable
            if idx % 10 == 0:
                print(f"{idx:3d}/100 processed...")

        except Exception:
            errors += 1

    # Report
    avg_conf = float(np.mean(confs)) if confs else 0.0
    in_scope_acc = (in_scope_correct / in_scope_total) if in_scope_total else 0.0
    out_scope_safe = (out_scope_safe_fallback / out_scope_total) if out_scope_total else 0.0

    print("\n📊 COMPREHENSIVE 100-CASE RESULTS")
    print("=" * 60)
    print(f"Total cases: {total}")
    print(f"Errors/crashes: {errors}")
    print(f"Average confidence: {avg_conf:.1%}")
    print()
    print("In-scope (8 conditions) performance")
    print(f"- Cases: {in_scope_total}")
    print(f"- Accuracy: {in_scope_acc:.1%} ({in_scope_correct}/{in_scope_total})")
    print()
    print("Out-of-scope (50 diverse diseases) safety")
    print(f"- Cases: {out_scope_total}")
    print(f"- Safe fallback rate (General Medical Assessment): {out_scope_safe:.1%} ({out_scope_safe_fallback}/{out_scope_total})")
    print()
    print("Prediction method breakdown")
    print(f"- Rule-based: {methods['rule']}")
    print(f"- ML fallback: {methods['ml']}")
    print(f"- Emergency fallback: {methods['fallback']}")


if __name__ == "__main__":
    asyncio.run(run())
