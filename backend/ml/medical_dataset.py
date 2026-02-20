"""
Medical Training Dataset Generator
Based on real symptom-disease mappings from WHO, CDC, Mayo Clinic, MedlinePlus, and MSD Manual.

Each disease entry contains:
- Canonical symptoms with frequency weights (how often that symptom appears in that disease)
- Typical patient demographics
- Severity and duration ranges
- Risk factors

This produces a large labeled dataset for supervised classification.
"""

import random
import numpy as np
import pandas as pd
from typing import List, Dict, Any

# ============================================================
# SYMPTOM UNIVERSE – 65 binary features the model will learn
# ============================================================
ALL_SYMPTOMS = [
    "fever", "high_fever", "mild_fever",
    "cough", "dry_cough", "productive_cough", "cough_with_blood",
    "sore_throat", "runny_nose", "nasal_congestion", "sneezing",
    "headache", "severe_headache", "migraine",
    "body_aches", "muscle_pain", "joint_pain", "back_pain",
    "fatigue", "extreme_fatigue", "weakness",
    "shortness_of_breath", "wheezing", "chest_tightness", "chest_pain",
    "nausea", "vomiting", "diarrhea", "constipation", "abdominal_pain",
    "bloating", "loss_of_appetite",
    "dizziness", "lightheadedness", "fainting",
    "skin_rash", "itching", "hives", "swelling",
    "chills", "night_sweats", "sweating",
    "weight_loss", "weight_gain",
    "frequent_urination", "painful_urination", "blood_in_urine",
    "blurred_vision", "eye_pain", "eye_redness",
    "ear_pain", "hearing_loss", "tinnitus",
    "difficulty_swallowing", "hoarseness",
    "numbness", "tingling", "tremor",
    "confusion", "memory_problems", "anxiety", "depression", "insomnia",
    "swollen_lymph_nodes", "stiff_neck",
    "loss_of_taste", "loss_of_smell",
    "palpitations", "rapid_heartbeat",
]

# ============================================================
# DISEASE DEFINITIONS – 42 conditions
# Each maps symptoms to probability of occurrence (0.0–1.0)
# Sources: Mayo Clinic, CDC, WHO ICD-11, MSD Manual, MedlinePlus
# ============================================================
DISEASE_PROFILES: Dict[str, Dict[str, Any]] = {
    # ---- RESPIRATORY ----
    "Common Cold": {
        "symptoms": {
            "runny_nose": 0.95, "nasal_congestion": 0.90, "sneezing": 0.85,
            "sore_throat": 0.80, "cough": 0.60, "mild_fever": 0.30,
            "headache": 0.40, "body_aches": 0.30, "fatigue": 0.40,
        },
        "severity_range": (1, 4), "duration_range": (48, 240),
        "temp_range": (36.5, 37.8), "age_range": (1, 90),
        "prevalence": 0.15,
    },
    "Influenza": {
        "symptoms": {
            "high_fever": 0.90, "fever": 0.95, "body_aches": 0.85,
            "headache": 0.80, "fatigue": 0.85, "extreme_fatigue": 0.50,
            "cough": 0.80, "dry_cough": 0.60, "sore_throat": 0.50,
            "chills": 0.75, "sweating": 0.40, "runny_nose": 0.40,
            "muscle_pain": 0.70, "loss_of_appetite": 0.55,
        },
        "severity_range": (4, 8), "duration_range": (72, 336),
        "temp_range": (38.0, 40.5), "age_range": (1, 90),
        "prevalence": 0.10,
    },
    "COVID-19": {
        "symptoms": {
            "fever": 0.60, "dry_cough": 0.45, "fatigue": 0.40,
            "loss_of_taste": 0.35, "loss_of_smell": 0.30,
            "shortness_of_breath": 0.25, "body_aches": 0.30,
            "headache": 0.25, "sore_throat": 0.15, "diarrhea": 0.10,
            "chills": 0.20, "nausea": 0.10, "nasal_congestion": 0.15,
        },
        "severity_range": (2, 9), "duration_range": (120, 504),
        "temp_range": (37.5, 40.0), "age_range": (5, 95),
        "prevalence": 0.02
    },
    "Pneumonia": {
        "symptoms": {
            "fever": 0.90, "high_fever": 0.65, "productive_cough": 0.85,
            "shortness_of_breath": 0.75, "chest_pain": 0.60,
            "fatigue": 0.70, "chills": 0.55, "sweating": 0.40,
            "body_aches": 0.40, "loss_of_appetite": 0.50,
            "nausea": 0.25, "confusion": 0.15,
        },
        "severity_range": (5, 10), "duration_range": (168, 672),
        "temp_range": (38.5, 41.0), "age_range": (1, 95),
        "prevalence": 0.04,
    },
    "Bronchitis": {
        "symptoms": {
            "cough": 0.95, "productive_cough": 0.80, "fatigue": 0.60,
            "chest_tightness": 0.55, "shortness_of_breath": 0.40,
            "mild_fever": 0.35, "body_aches": 0.30, "sore_throat": 0.35,
            "wheezing": 0.30, "chills": 0.20,
        },
        "severity_range": (3, 7), "duration_range": (120, 504),
        "temp_range": (36.8, 38.5), "age_range": (5, 85),
        "prevalence": 0.05,
    },
    "Asthma": {
        "symptoms": {
            "wheezing": 0.90, "shortness_of_breath": 0.88,
            "chest_tightness": 0.80, "cough": 0.75, "dry_cough": 0.60,
            "fatigue": 0.30, "anxiety": 0.25, "insomnia": 0.20,
        },
        "severity_range": (3, 9), "duration_range": (1, 168),
        "temp_range": (36.2, 37.2), "age_range": (3, 80),
        "prevalence": 0.05,
    },
    "Sinusitis": {
        "symptoms": {
            "nasal_congestion": 0.95, "headache": 0.80,
            "facial_pain": 0.0,  # not in our list, skip
            "runny_nose": 0.70, "productive_cough": 0.40,
            "mild_fever": 0.35, "fatigue": 0.40, "sore_throat": 0.30,
            "loss_of_smell": 0.35, "ear_pain": 0.20,
        },
        "severity_range": (3, 6), "duration_range": (168, 672),
        "temp_range": (36.5, 38.0), "age_range": (10, 75),
        "prevalence": 0.05,
    },
    "Tuberculosis": {
        "symptoms": {
            "cough": 0.90, "productive_cough": 0.70, "cough_with_blood": 0.30,
            "fever": 0.70, "night_sweats": 0.75, "weight_loss": 0.65,
            "fatigue": 0.70, "extreme_fatigue": 0.40, "chest_pain": 0.35,
            "loss_of_appetite": 0.60, "chills": 0.30,
        },
        "severity_range": (5, 9), "duration_range": (504, 2160),
        "temp_range": (37.5, 39.5), "age_range": (15, 80),
        "prevalence": 0.02,
    },

    # ---- GASTROINTESTINAL ----
    "Gastroenteritis": {
        "symptoms": {
            "diarrhea": 0.90, "nausea": 0.85, "vomiting": 0.75,
            "abdominal_pain": 0.80, "fever": 0.50, "mild_fever": 0.40,
            "fatigue": 0.50, "loss_of_appetite": 0.60,
            "body_aches": 0.30, "headache": 0.25, "chills": 0.20,
        },
        "severity_range": (3, 7), "duration_range": (24, 168),
        "temp_range": (37.0, 39.0), "age_range": (1, 90),
        "prevalence": 0.06,
    },
    "Gastritis": {
        "symptoms": {
            "abdominal_pain": 0.90, "nausea": 0.70, "vomiting": 0.40,
            "bloating": 0.65, "loss_of_appetite": 0.55,
            "fatigue": 0.30, "weight_loss": 0.15,
        },
        "severity_range": (3, 7), "duration_range": (48, 720),
        "temp_range": (36.3, 37.5), "age_range": (18, 80),
        "prevalence": 0.04,
    },
    "Irritable Bowel Syndrome": {
        "symptoms": {
            "abdominal_pain": 0.92, "bloating": 0.85,
            "diarrhea": 0.55, "constipation": 0.50,
            "nausea": 0.30, "fatigue": 0.40, "anxiety": 0.35,
            "loss_of_appetite": 0.25, "back_pain": 0.20,
        },
        "severity_range": (2, 6), "duration_range": (168, 4320),
        "temp_range": (36.2, 37.2), "age_range": (15, 65),
        "prevalence": 0.04,
    },
    "Food Poisoning": {
        "symptoms": {
            "nausea": 0.95, "vomiting": 0.90, "diarrhea": 0.85,
            "abdominal_pain": 0.85, "fever": 0.45, "chills": 0.30,
            "fatigue": 0.50, "headache": 0.30, "sweating": 0.25,
        },
        "severity_range": (4, 8), "duration_range": (6, 72),
        "temp_range": (37.0, 39.0), "age_range": (2, 90),
        "prevalence": 0.04,
    },
    "Appendicitis": {
        "symptoms": {
            "abdominal_pain": 0.95, "nausea": 0.75, "vomiting": 0.65,
            "fever": 0.60, "loss_of_appetite": 0.80,
            "bloating": 0.30, "constipation": 0.25, "diarrhea": 0.15,
        },
        "severity_range": (6, 10), "duration_range": (12, 72),
        "temp_range": (37.5, 39.5), "age_range": (5, 50),
        "prevalence": 0.02,
    },

    # ---- NEUROLOGICAL ----
    "Migraine": {
        "symptoms": {
            "severe_headache": 0.95, "headache": 0.98, "migraine": 0.90,
            "nausea": 0.70, "vomiting": 0.40, "blurred_vision": 0.45,
            "dizziness": 0.40, "fatigue": 0.50, "sensitivity_to_light": 0.0,
            "loss_of_appetite": 0.30,
        },
        "severity_range": (5, 10), "duration_range": (4, 72),
        "temp_range": (36.2, 37.2), "age_range": (12, 65),
        "prevalence": 0.05,
    },
    "Tension Headache": {
        "symptoms": {
            "headache": 0.98, "fatigue": 0.45, "muscle_pain": 0.35,
            "stiff_neck": 0.40, "insomnia": 0.25, "anxiety": 0.30,
            "dizziness": 0.15,
        },
        "severity_range": (2, 6), "duration_range": (1, 168),
        "temp_range": (36.2, 37.0), "age_range": (15, 75),
        "prevalence": 0.06,
    },
    "Meningitis": {
        "symptoms": {
            "severe_headache": 0.90, "headache": 0.95, "high_fever": 0.85,
            "fever": 0.92, "stiff_neck": 0.85, "nausea": 0.65,
            "vomiting": 0.55, "confusion": 0.40, "skin_rash": 0.25,
            "fatigue": 0.50, "eye_pain": 0.20, "chills": 0.40,
        },
        "severity_range": (7, 10), "duration_range": (24, 336),
        "temp_range": (39.0, 41.5), "age_range": (1, 60),
        "prevalence": 0.01,
    },

    # ---- CARDIOVASCULAR ----
    "Hypertension": {
        "symptoms": {
            "headache": 0.50, "dizziness": 0.45, "blurred_vision": 0.30,
            "shortness_of_breath": 0.25, "chest_pain": 0.20,
            "palpitations": 0.30, "fatigue": 0.35, "nausea": 0.15,
        },
        "severity_range": (2, 7), "duration_range": (168, 8760),
        "temp_range": (36.2, 37.2), "age_range": (30, 90),
        "prevalence": 0.04,
    },
    "Heart Attack": {
        "symptoms": {
            "chest_pain": 0.92, "shortness_of_breath": 0.75,
            "sweating": 0.70, "nausea": 0.55, "dizziness": 0.45,
            "fatigue": 0.40, "palpitations": 0.35, "anxiety": 0.50,
            "back_pain": 0.25, "numbness": 0.20, "vomiting": 0.25,
        },
        "severity_range": (8, 10), "duration_range": (1, 24),
        "temp_range": (36.5, 37.8), "age_range": (35, 90),
        "prevalence": 0.01,
    },
    "Anemia": {
        "symptoms": {
            "fatigue": 0.92, "extreme_fatigue": 0.60, "weakness": 0.80,
            "dizziness": 0.55, "shortness_of_breath": 0.45,
            "palpitations": 0.40, "headache": 0.35,
            "lightheadedness": 0.40, "chest_pain": 0.15,
        },
        "severity_range": (2, 7), "duration_range": (336, 4320),
        "temp_range": (36.0, 37.2), "age_range": (10, 80),
        "prevalence": 0.03,
    },

    # ---- MUSCULOSKELETAL ----
    "Arthritis": {
        "symptoms": {
            "joint_pain": 0.95, "swelling": 0.70, "stiff_neck": 0.25,
            "fatigue": 0.50, "muscle_pain": 0.40, "weakness": 0.30,
            "mild_fever": 0.15, "weight_loss": 0.10,
        },
        "severity_range": (3, 8), "duration_range": (336, 8760),
        "temp_range": (36.2, 37.5), "age_range": (25, 90),
        "prevalence": 0.04,
    },
    "Fibromyalgia": {
        "symptoms": {
            "body_aches": 0.95, "muscle_pain": 0.90, "fatigue": 0.88,
            "extreme_fatigue": 0.55, "insomnia": 0.65, "headache": 0.55,
            "anxiety": 0.45, "depression": 0.40, "numbness": 0.30,
            "tingling": 0.30, "memory_problems": 0.35,
        },
        "severity_range": (4, 8), "duration_range": (720, 8760),
        "temp_range": (36.2, 37.2), "age_range": (20, 65),
        "prevalence": 0.02,
    },

    # ---- INFECTIOUS ----
    "Urinary Tract Infection": {
        "symptoms": {
            "painful_urination": 0.90, "frequent_urination": 0.85,
            "abdominal_pain": 0.50, "fever": 0.40, "mild_fever": 0.35,
            "back_pain": 0.30, "nausea": 0.20, "blood_in_urine": 0.25,
            "fatigue": 0.30, "chills": 0.20,
        },
        "severity_range": (3, 7), "duration_range": (24, 168),
        "temp_range": (36.8, 39.0), "age_range": (15, 80),
        "prevalence": 0.05,
    },
    "Strep Throat": {
        "symptoms": {
            "sore_throat": 0.95, "fever": 0.80, "high_fever": 0.45,
            "headache": 0.55, "swollen_lymph_nodes": 0.70,
            "difficulty_swallowing": 0.65, "body_aches": 0.35,
            "nausea": 0.25, "loss_of_appetite": 0.40, "chills": 0.30,
        },
        "severity_range": (4, 8), "duration_range": (48, 240),
        "temp_range": (38.0, 40.0), "age_range": (3, 50),
        "prevalence": 0.04,
    },
    "Mononucleosis": {
        "symptoms": {
            "extreme_fatigue": 0.90, "fatigue": 0.95, "fever": 0.80,
            "sore_throat": 0.85, "swollen_lymph_nodes": 0.80,
            "headache": 0.50, "body_aches": 0.45, "skin_rash": 0.20,
            "loss_of_appetite": 0.40, "night_sweats": 0.25,
        },
        "severity_range": (4, 8), "duration_range": (336, 1440),
        "temp_range": (37.5, 39.5), "age_range": (12, 35),
        "prevalence": 0.02,
    },
    "Malaria": {
        "symptoms": {
            "high_fever": 0.92, "fever": 0.95, "chills": 0.88,
            "sweating": 0.80, "headache": 0.75, "body_aches": 0.65,
            "nausea": 0.55, "vomiting": 0.45, "fatigue": 0.70,
            "diarrhea": 0.25, "abdominal_pain": 0.30, "confusion": 0.10,
        },
        "severity_range": (5, 10), "duration_range": (48, 336),
        "temp_range": (38.5, 41.0), "age_range": (1, 80),
        "prevalence": 0.02,
    },
    "Dengue Fever": {
        "symptoms": {
            "high_fever": 0.90, "fever": 0.95, "severe_headache": 0.80,
            "headache": 0.85, "body_aches": 0.80, "muscle_pain": 0.75,
            "joint_pain": 0.70, "skin_rash": 0.50, "nausea": 0.50,
            "vomiting": 0.35, "fatigue": 0.65, "eye_pain": 0.55,
            "loss_of_appetite": 0.45,
        },
        "severity_range": (5, 10), "duration_range": (48, 336),
        "temp_range": (38.5, 41.0), "age_range": (3, 75),
        "prevalence": 0.02,
    },

    # ---- ALLERGIC / IMMUNE ----
    "Allergic Rhinitis": {
        "symptoms": {
            "sneezing": 0.92, "runny_nose": 0.90, "nasal_congestion": 0.85,
            "itching": 0.60, "eye_redness": 0.50, "fatigue": 0.30,
            "headache": 0.25, "sore_throat": 0.20,
        },
        "severity_range": (1, 5), "duration_range": (24, 4320),
        "temp_range": (36.2, 37.0), "age_range": (5, 70),
        "prevalence": 0.06,
    },
    "Allergic Reaction": {
        "symptoms": {
            "skin_rash": 0.80, "hives": 0.70, "itching": 0.85,
            "swelling": 0.60, "shortness_of_breath": 0.30,
            "nausea": 0.25, "dizziness": 0.20, "anxiety": 0.20,
        },
        "severity_range": (2, 9), "duration_range": (1, 72),
        "temp_range": (36.2, 37.5), "age_range": (2, 80),
        "prevalence": 0.03,
    },

    # ---- DERMATOLOGICAL ----
    "Eczema": {
        "symptoms": {
            "skin_rash": 0.95, "itching": 0.92, "swelling": 0.30,
            "insomnia": 0.30, "fatigue": 0.20, "anxiety": 0.20,
        },
        "severity_range": (2, 7), "duration_range": (168, 8760),
        "temp_range": (36.2, 37.0), "age_range": (1, 60),
        "prevalence": 0.03,
    },
    "Chickenpox": {
        "symptoms": {
            "skin_rash": 0.98, "itching": 0.90, "fever": 0.80,
            "mild_fever": 0.50, "fatigue": 0.60, "headache": 0.45,
            "loss_of_appetite": 0.50, "body_aches": 0.30,
        },
        "severity_range": (3, 7), "duration_range": (120, 336),
        "temp_range": (37.5, 39.5), "age_range": (1, 50),
        "prevalence": 0.02,
    },

    # ---- ENDOCRINE ----
    "Diabetes": {
        "symptoms": {
            "frequent_urination": 0.80, "fatigue": 0.75, "blurred_vision": 0.50,
            "weight_loss": 0.40, "numbness": 0.35, "tingling": 0.35,
            "weakness": 0.40, "loss_of_appetite": 0.20,
            "dizziness": 0.25, "insomnia": 0.20,
        },
        "severity_range": (2, 6), "duration_range": (720, 8760),
        "temp_range": (36.2, 37.2), "age_range": (30, 85),
        "prevalence": 0.04,
    },
    "Hyperthyroidism": {
        "symptoms": {
            "weight_loss": 0.75, "rapid_heartbeat": 0.80,
            "palpitations": 0.70, "anxiety": 0.65, "tremor": 0.60,
            "sweating": 0.65, "fatigue": 0.50, "insomnia": 0.55,
            "diarrhea": 0.30, "weakness": 0.40, "eye_pain": 0.20,
        },
        "severity_range": (3, 7), "duration_range": (336, 4320),
        "temp_range": (36.5, 37.8), "age_range": (20, 65),
        "prevalence": 0.02,
    },
    "Hypothyroidism": {
        "symptoms": {
            "fatigue": 0.85, "extreme_fatigue": 0.50, "weight_gain": 0.70,
            "constipation": 0.55, "depression": 0.45, "muscle_pain": 0.40,
            "joint_pain": 0.30, "dry_cough": 0.15, "memory_problems": 0.35,
            "numbness": 0.20, "hoarseness": 0.30,
        },
        "severity_range": (2, 6), "duration_range": (720, 8760),
        "temp_range": (35.5, 36.8), "age_range": (25, 75),
        "prevalence": 0.03,
    },

    # ---- MENTAL HEALTH ----
    "Generalized Anxiety Disorder": {
        "symptoms": {
            "anxiety": 0.95, "insomnia": 0.70, "fatigue": 0.65,
            "headache": 0.50, "muscle_pain": 0.40, "nausea": 0.30,
            "dizziness": 0.35, "palpitations": 0.45, "tremor": 0.25,
            "sweating": 0.30, "shortness_of_breath": 0.25,
        },
        "severity_range": (3, 8), "duration_range": (336, 8760),
        "temp_range": (36.2, 37.2), "age_range": (15, 65),
        "prevalence": 0.03,
    },
    "Depression": {
        "symptoms": {
            "depression": 0.95, "fatigue": 0.80, "extreme_fatigue": 0.45,
            "insomnia": 0.70, "loss_of_appetite": 0.60,
            "weight_loss": 0.30, "weight_gain": 0.25,
            "headache": 0.35, "body_aches": 0.30, "anxiety": 0.50,
            "memory_problems": 0.35, "confusion": 0.15,
        },
        "severity_range": (3, 9), "duration_range": (336, 8760),
        "temp_range": (36.0, 37.0), "age_range": (12, 80),
        "prevalence": 0.04,
    },

    # ---- KIDNEY ----
    "Kidney Stones": {
        "symptoms": {
            "abdominal_pain": 0.90, "back_pain": 0.85,
            "painful_urination": 0.60, "blood_in_urine": 0.55,
            "nausea": 0.65, "vomiting": 0.50, "fever": 0.30,
            "frequent_urination": 0.40, "chills": 0.20,
        },
        "severity_range": (6, 10), "duration_range": (1, 168),
        "temp_range": (36.5, 38.5), "age_range": (20, 70),
        "prevalence": 0.02,
    },

    # ---- ENT ----
    "Otitis Media": {
        "symptoms": {
            "ear_pain": 0.95, "fever": 0.60, "mild_fever": 0.40,
            "headache": 0.40, "hearing_loss": 0.35,
            "nasal_congestion": 0.30, "fatigue": 0.25,
            "loss_of_appetite": 0.30, "dizziness": 0.15,
        },
        "severity_range": (3, 7), "duration_range": (48, 336),
        "temp_range": (37.0, 39.0), "age_range": (1, 40),
        "prevalence": 0.03,
    },
    "Tonsillitis": {
        "symptoms": {
            "sore_throat": 0.95, "difficulty_swallowing": 0.80,
            "fever": 0.75, "high_fever": 0.40, "headache": 0.50,
            "swollen_lymph_nodes": 0.65, "hoarseness": 0.35,
            "fatigue": 0.45, "ear_pain": 0.30, "loss_of_appetite": 0.40,
        },
        "severity_range": (4, 8), "duration_range": (72, 240),
        "temp_range": (38.0, 40.0), "age_range": (3, 40),
        "prevalence": 0.03,
    },

    # ---- OTHER ----
    "Iron Deficiency": {
        "symptoms": {
            "fatigue": 0.90, "weakness": 0.80, "dizziness": 0.55,
            "headache": 0.45, "shortness_of_breath": 0.35,
            "chest_pain": 0.15, "palpitations": 0.30,
            "numbness": 0.20, "tingling": 0.20,
        },
        "severity_range": (2, 6), "duration_range": (336, 4320),
        "temp_range": (36.0, 37.0), "age_range": (12, 70),
        "prevalence": 0.03,
    },
    "Vertigo": {
        "symptoms": {
            "dizziness": 0.95, "lightheadedness": 0.70, "nausea": 0.65,
            "vomiting": 0.35, "tinnitus": 0.40, "hearing_loss": 0.25,
            "headache": 0.30, "sweating": 0.25, "anxiety": 0.30,
        },
        "severity_range": (3, 8), "duration_range": (1, 168),
        "temp_range": (36.2, 37.2), "age_range": (20, 80),
        "prevalence": 0.02,
    },
    "Chronic Fatigue Syndrome": {
        "symptoms": {
            "extreme_fatigue": 0.95, "fatigue": 0.98, "weakness": 0.70,
            "muscle_pain": 0.60, "headache": 0.55, "joint_pain": 0.45,
            "insomnia": 0.55, "memory_problems": 0.50, "sore_throat": 0.30,
            "swollen_lymph_nodes": 0.25, "dizziness": 0.30,
            "depression": 0.35,
        },
        "severity_range": (4, 9), "duration_range": (4320, 8760),
        "temp_range": (36.0, 37.5), "age_range": (18, 60),
        "prevalence": 0.01,
    },
}


# ============================================================
# DISEASE METADATA – emergency levels, medications, hospital advice
# Sources: WHO Essential Medicines, FDA, Mayo Clinic, MSD Manual
# emergency_level: "low" | "moderate" | "high" | "critical"
# ============================================================
DISEASE_METADATA: Dict[str, Dict[str, Any]] = {
    # ---- RESPIRATORY ----
    "Common Cold": {
        "emergency_level": "low",
        "medications": [
            {"name": "Paracetamol (Acetaminophen)", "dosage": "500mg every 4-6 hours", "purpose": "Fever and pain relief"},
            {"name": "Phenylephrine nasal decongestant", "dosage": "As directed on packaging", "purpose": "Nasal congestion"},
            {"name": "Dextromethorphan (cough syrup)", "dosage": "10-20mg every 4 hours", "purpose": "Cough suppression"},
            {"name": "Vitamin C supplement", "dosage": "500-1000mg daily", "purpose": "Immune support"},
        ],
        "home_care": "Rest, stay hydrated, use saline nasal spray. Usually resolves in 7-10 days.",
        "hospital_advice": "Not usually needed. See a doctor if symptoms last more than 10 days or worsen significantly.",
        "when_to_seek_emergency": "High fever above 39.5°C, difficulty breathing, or symptoms lasting over 2 weeks.",
    },
    "Influenza": {
        "emergency_level": "moderate",
        "medications": [
            {"name": "Oseltamivir (Tamiflu)", "dosage": "75mg twice daily for 5 days", "purpose": "Antiviral (most effective within 48hrs of onset)"},
            {"name": "Paracetamol (Acetaminophen)", "dosage": "500-1000mg every 4-6 hours", "purpose": "Fever and body ache relief"},
            {"name": "Ibuprofen", "dosage": "200-400mg every 6-8 hours", "purpose": "Pain and inflammation relief"},
        ],
        "home_care": "Complete bed rest, drink plenty of fluids, isolate to prevent spread.",
        "hospital_advice": "See a doctor within 48 hours of symptom onset for antiviral treatment. Vulnerable groups (elderly, pregnant, immunocompromised) should seek medical care promptly.",
        "when_to_seek_emergency": "Difficulty breathing, persistent chest pain, confusion, severe vomiting, or fever above 40°C.",
    },
    "COVID-19": {
        "emergency_level": "moderate",
        "medications": [
            {"name": "Paracetamol (Acetaminophen)", "dosage": "500-1000mg every 4-6 hours", "purpose": "Fever and pain relief"},
            {"name": "Dextromethorphan", "dosage": "10-20mg every 4 hours", "purpose": "Cough relief"},
            {"name": "Zinc supplement", "dosage": "75mg daily", "purpose": "Immune support"},
            {"name": "Vitamin D supplement", "dosage": "1000-2000 IU daily", "purpose": "Immune system support"},
        ],
        "home_care": "Self-isolate, rest, stay hydrated, monitor oxygen levels with pulse oximeter if available.",
        "hospital_advice": "Seek medical attention if oxygen saturation drops below 94%, or if breathing becomes difficult.",
        "when_to_seek_emergency": "Oxygen level below 92%, persistent chest pain, confusion, inability to stay awake, bluish lips or face.",
    },
    "Pneumonia": {
        "emergency_level": "high",
        "medications": [
            {"name": "Amoxicillin", "dosage": "500mg three times daily for 5-7 days", "purpose": "Antibiotic (bacterial pneumonia)"},
            {"name": "Azithromycin", "dosage": "500mg day 1, then 250mg days 2-5", "purpose": "Antibiotic (atypical pneumonia)"},
            {"name": "Paracetamol", "dosage": "500-1000mg every 4-6 hours", "purpose": "Fever reduction"},
            {"name": "Guaifenesin", "dosage": "200-400mg every 4 hours", "purpose": "Expectorant to clear mucus"},
        ],
        "home_care": "Rest, drink warm fluids, use a humidifier. Take all prescribed antibiotics even if feeling better.",
        "hospital_advice": "⚠️ SEEK MEDICAL ATTENTION PROMPTLY. Pneumonia requires professional diagnosis and may need prescription antibiotics or hospitalization.",
        "when_to_seek_emergency": "Severe difficulty breathing, high fever above 40°C, confusion, rapid heartbeat, or coughing up blood.",
    },
    "Bronchitis": {
        "emergency_level": "low",
        "medications": [
            {"name": "Dextromethorphan", "dosage": "10-20mg every 4 hours", "purpose": "Cough suppression"},
            {"name": "Guaifenesin", "dosage": "200-400mg every 4 hours", "purpose": "Loosen mucus"},
            {"name": "Ibuprofen", "dosage": "200-400mg every 6-8 hours", "purpose": "Pain and inflammation relief"},
            {"name": "Honey with warm water", "dosage": "1-2 tablespoons as needed", "purpose": "Soothe irritated throat"},
        ],
        "home_care": "Rest, drink plenty of fluids, use a humidifier, avoid smoking and irritants.",
        "hospital_advice": "See a doctor if cough lasts more than 3 weeks, or if you develop fever above 38.5°C.",
        "when_to_seek_emergency": "Coughing up blood, severe difficulty breathing, or high persistent fever.",
    },
    "Asthma": {
        "emergency_level": "moderate",
        "medications": [
            {"name": "Salbutamol (Albuterol) inhaler", "dosage": "2 puffs every 4-6 hours as needed", "purpose": "Quick-relief bronchodilator"},
            {"name": "Beclomethasone inhaler", "dosage": "As prescribed by doctor", "purpose": "Long-term anti-inflammatory control"},
            {"name": "Montelukast", "dosage": "10mg once daily", "purpose": "Leukotriene receptor antagonist"},
        ],
        "home_care": "Use rescue inhaler as needed. Avoid triggers (dust, smoke, cold air). Follow asthma action plan.",
        "hospital_advice": "See a doctor if rescue inhaler is needed more than twice per week or symptoms worsen.",
        "when_to_seek_emergency": "Severe breathing difficulty, lips or fingernails turning blue, rescue inhaler not helping, cannot speak full sentences.",
    },
    "Sinusitis": {
        "emergency_level": "low",
        "medications": [
            {"name": "Saline nasal spray", "dosage": "2-3 sprays each nostril, 3-4 times daily", "purpose": "Flush sinuses"},
            {"name": "Pseudoephedrine", "dosage": "60mg every 4-6 hours", "purpose": "Decongestant"},
            {"name": "Paracetamol", "dosage": "500mg every 4-6 hours", "purpose": "Pain relief"},
            {"name": "Steam inhalation", "dosage": "10-15 minutes, 2-3 times daily", "purpose": "Relieve congestion"},
        ],
        "home_care": "Use warm compresses on face, stay hydrated, sleep with head elevated.",
        "hospital_advice": "See a doctor if symptoms last more than 10 days or if severe facial pain develops.",
        "when_to_seek_emergency": "Severe headache, high fever, swelling around eyes, or vision changes.",
    },
    "Tuberculosis": {
        "emergency_level": "high",
        "medications": [
            {"name": "Isoniazid + Rifampicin", "dosage": "As prescribed (6-9 month course)", "purpose": "First-line TB treatment"},
            {"name": "Pyrazinamide", "dosage": "As prescribed (first 2 months)", "purpose": "TB combination therapy"},
            {"name": "Ethambutol", "dosage": "As prescribed (first 2 months)", "purpose": "TB combination therapy"},
        ],
        "home_care": "Complete full course of medication even if feeling better. Wear a mask, ensure good ventilation.",
        "hospital_advice": "⚠️ REQUIRES IMMEDIATE MEDICAL TREATMENT. TB is a serious infectious disease that needs prescribed antibiotic therapy for months. Do NOT self-medicate.",
        "when_to_seek_emergency": "Coughing up blood, severe weight loss, persistent high fever, or extreme weakness.",
    },

    # ---- GASTROINTESTINAL ----
    "Gastroenteritis": {
        "emergency_level": "moderate",
        "medications": [
            {"name": "Oral Rehydration Salts (ORS)", "dosage": "Sip frequently throughout the day", "purpose": "Prevent dehydration"},
            {"name": "Loperamide (Imodium)", "dosage": "2mg after each loose stool, max 8mg/day", "purpose": "Anti-diarrheal"},
            {"name": "Ondansetron", "dosage": "4-8mg every 8 hours", "purpose": "Anti-nausea (prescription)"},
            {"name": "Paracetamol", "dosage": "500mg every 4-6 hours", "purpose": "Fever and pain relief"},
        ],
        "home_care": "Stay hydrated with clear fluids, eat bland foods (BRAT diet: bananas, rice, applesauce, toast). Rest.",
        "hospital_advice": "See a doctor if unable to keep fluids down for 24 hours, blood in stool, or fever above 39°C.",
        "when_to_seek_emergency": "Signs of severe dehydration (very dry mouth, no urination, rapid heartbeat), bloody diarrhea, or severe abdominal pain.",
    },
    "Gastritis": {
        "emergency_level": "low",
        "medications": [
            {"name": "Omeprazole", "dosage": "20mg once daily before breakfast", "purpose": "Reduce stomach acid"},
            {"name": "Antacid (Aluminum/Magnesium hydroxide)", "dosage": "As directed after meals", "purpose": "Neutralize stomach acid"},
            {"name": "Sucralfate", "dosage": "1g four times daily before meals", "purpose": "Protect stomach lining"},
        ],
        "home_care": "Eat smaller meals, avoid spicy/acidic foods, alcohol, and NSAIDs. Don't eat 2-3 hours before bed.",
        "hospital_advice": "See a doctor if symptoms persist more than 2 weeks or if you notice blood in vomit/stool.",
        "when_to_seek_emergency": "Vomiting blood, black/tarry stools, severe abdominal pain, or feeling faint.",
    },
    "Irritable Bowel Syndrome": {
        "emergency_level": "low",
        "medications": [
            {"name": "Mebeverine", "dosage": "135mg three times daily before meals", "purpose": "Antispasmodic for cramps"},
            {"name": "Psyllium husk (Metamucil)", "dosage": "1 tablespoon in water daily", "purpose": "Fiber supplement"},
            {"name": "Peppermint oil capsules", "dosage": "1-2 capsules before meals", "purpose": "Relieve bloating and cramping"},
        ],
        "home_care": "Identify and avoid trigger foods. Regular exercise, stress management, and adequate sleep help manage symptoms.",
        "hospital_advice": "Consult a gastroenterologist for proper diagnosis and management plan.",
        "when_to_seek_emergency": "Rectal bleeding, unexplained weight loss, persistent vomiting, or severe pain that won't go away.",
    },
    "Food Poisoning": {
        "emergency_level": "moderate",
        "medications": [
            {"name": "Oral Rehydration Salts (ORS)", "dosage": "Sip frequently", "purpose": "Replace lost fluids and electrolytes"},
            {"name": "Bismuth subsalicylate (Pepto-Bismol)", "dosage": "30ml every 30 mins, max 8 doses", "purpose": "Reduce nausea and diarrhea"},
            {"name": "Paracetamol", "dosage": "500mg every 4-6 hours", "purpose": "Fever and pain relief"},
        ],
        "home_care": "Rest, sip clear fluids. Avoid solid food until vomiting stops. Gradually reintroduce bland foods.",
        "hospital_advice": "See a doctor if symptoms last more than 3 days, high fever, or unable to keep any fluids down.",
        "when_to_seek_emergency": "Blood in vomit or stool, signs of severe dehydration, blurred vision, muscle weakness, or fever above 39.5°C.",
    },
    "Appendicitis": {
        "emergency_level": "critical",
        "medications": [
            {"name": "DO NOT self-medicate", "dosage": "N/A", "purpose": "Surgery is usually required"},
        ],
        "home_care": "DO NOT eat or drink anything. Do NOT take laxatives or pain medications that mask symptoms.",
        "hospital_advice": "🚨 GO TO THE EMERGENCY ROOM IMMEDIATELY. Appendicitis is a surgical emergency. A ruptured appendix can be life-threatening.",
        "when_to_seek_emergency": "Sharp pain in lower right abdomen that worsens, fever, nausea/vomiting — seek emergency care NOW.",
    },

    # ---- NEUROLOGICAL ----
    "Migraine": {
        "emergency_level": "moderate",
        "medications": [
            {"name": "Sumatriptan", "dosage": "50-100mg at onset of migraine", "purpose": "Triptan for acute migraine relief"},
            {"name": "Ibuprofen", "dosage": "400-600mg at onset", "purpose": "Pain and inflammation relief"},
            {"name": "Metoclopramide", "dosage": "10mg as needed", "purpose": "Anti-nausea"},
            {"name": "Paracetamol + Caffeine", "dosage": "As directed", "purpose": "Mild migraine relief"},
        ],
        "home_care": "Rest in a dark, quiet room. Apply cold compress to forehead. Stay hydrated.",
        "hospital_advice": "See a doctor if migraines occur more than 4 times per month or last more than 72 hours.",
        "when_to_seek_emergency": "Sudden 'worst headache of your life', headache with fever and stiff neck, vision loss, confusion, or weakness on one side.",
    },
    "Tension Headache": {
        "emergency_level": "low",
        "medications": [
            {"name": "Paracetamol", "dosage": "500-1000mg every 4-6 hours", "purpose": "Pain relief"},
            {"name": "Ibuprofen", "dosage": "200-400mg every 6-8 hours", "purpose": "Pain and inflammation relief"},
            {"name": "Aspirin", "dosage": "300-600mg every 4-6 hours", "purpose": "Pain relief (adults only)"},
        ],
        "home_care": "Rest, reduce stress, gentle neck stretches, adequate sleep, stay hydrated.",
        "hospital_advice": "See a doctor if headaches occur more than 15 days per month or OTC medicines don't help.",
        "when_to_seek_emergency": "Sudden severe headache, headache with fever/stiff neck, confusion, or weakness.",
    },
    "Meningitis": {
        "emergency_level": "critical",
        "medications": [
            {"name": "DO NOT self-medicate", "dosage": "N/A", "purpose": "Requires IV antibiotics in hospital"},
        ],
        "home_care": "DO NOT attempt home treatment. This is a medical emergency.",
        "hospital_advice": "🚨 CALL EMERGENCY SERVICES (911/999) IMMEDIATELY. Meningitis can be fatal within hours without treatment.",
        "when_to_seek_emergency": "Severe headache + stiff neck + fever + confusion = MEDICAL EMERGENCY. Go to hospital NOW.",
    },

    # ---- CARDIOVASCULAR ----
    "Hypertension": {
        "emergency_level": "moderate",
        "medications": [
            {"name": "Amlodipine", "dosage": "5-10mg once daily", "purpose": "Calcium channel blocker (prescription)"},
            {"name": "Losartan", "dosage": "50-100mg once daily", "purpose": "ARB blood pressure medication (prescription)"},
            {"name": "Hydrochlorothiazide", "dosage": "12.5-25mg once daily", "purpose": "Diuretic (prescription)"},
        ],
        "home_care": "Reduce salt intake, exercise 30 min/day, maintain healthy weight, limit alcohol, manage stress.",
        "hospital_advice": "See a doctor for proper diagnosis and prescription medication. Regular blood pressure monitoring is essential.",
        "when_to_seek_emergency": "Blood pressure above 180/120, severe headache, chest pain, vision changes, or difficulty breathing.",
    },
    "Heart Attack": {
        "emergency_level": "critical",
        "medications": [
            {"name": "Aspirin 300mg", "dosage": "Chew one tablet immediately", "purpose": "Blood thinner (while waiting for ambulance)"},
            {"name": "Nitroglycerin (if prescribed)", "dosage": "As previously prescribed", "purpose": "Open blood vessels"},
        ],
        "home_care": "DO NOT attempt home treatment. Call emergency services immediately.",
        "hospital_advice": "🚨 CALL 911/EMERGENCY SERVICES NOW. Every minute matters. Chew an aspirin while waiting. Do NOT drive yourself to the hospital.",
        "when_to_seek_emergency": "Chest pain/pressure, pain radiating to arm/jaw, shortness of breath, cold sweat, nausea — CALL 911 IMMEDIATELY.",
    },
    "Anemia": {
        "emergency_level": "low",
        "medications": [
            {"name": "Ferrous sulfate (Iron supplement)", "dosage": "325mg once or twice daily with vitamin C", "purpose": "Iron replacement"},
            {"name": "Vitamin B12 supplement", "dosage": "1000mcg daily", "purpose": "B12 deficiency anemia"},
            {"name": "Folic acid", "dosage": "400-800mcg daily", "purpose": "Folate deficiency anemia"},
        ],
        "home_care": "Eat iron-rich foods (red meat, spinach, beans, fortified cereals). Take iron with vitamin C for better absorption.",
        "hospital_advice": "See a doctor for blood tests to determine the type and cause of anemia.",
        "when_to_seek_emergency": "Severe fatigue with chest pain, rapid heartbeat, shortness of breath at rest, or fainting.",
    },

    # ---- MUSCULOSKELETAL ----
    "Arthritis": {
        "emergency_level": "low",
        "medications": [
            {"name": "Ibuprofen", "dosage": "200-400mg every 6-8 hours with food", "purpose": "Anti-inflammatory pain relief"},
            {"name": "Naproxen", "dosage": "250-500mg twice daily with food", "purpose": "Anti-inflammatory"},
            {"name": "Topical diclofenac gel", "dosage": "Apply to affected joints 3-4 times daily", "purpose": "Local pain relief"},
        ],
        "home_care": "Gentle exercise, warm/cold compresses, maintain healthy weight, joint protection techniques.",
        "hospital_advice": "See a rheumatologist for proper diagnosis and long-term management plan.",
        "when_to_seek_emergency": "Sudden joint swelling with fever, inability to move a joint, or severe unexplained joint pain.",
    },
    "Fibromyalgia": {
        "emergency_level": "low",
        "medications": [
            {"name": "Pregabalin", "dosage": "75-150mg twice daily (prescription)", "purpose": "Nerve pain relief"},
            {"name": "Duloxetine", "dosage": "30-60mg daily (prescription)", "purpose": "Pain and mood management"},
            {"name": "Paracetamol", "dosage": "500-1000mg every 4-6 hours", "purpose": "Mild pain relief"},
        ],
        "home_care": "Regular gentle exercise (swimming, walking), good sleep hygiene, stress management, pacing activities.",
        "hospital_advice": "See a rheumatologist or pain specialist for comprehensive management plan.",
        "when_to_seek_emergency": "Severe depression with suicidal thoughts, chest pain, or new neurological symptoms.",
    },

    # ---- INFECTIOUS ----
    "Urinary Tract Infection": {
        "emergency_level": "moderate",
        "medications": [
            {"name": "Nitrofurantoin", "dosage": "100mg twice daily for 5 days (prescription)", "purpose": "Antibiotic for UTI"},
            {"name": "Trimethoprim", "dosage": "200mg twice daily for 3 days (prescription)", "purpose": "Antibiotic for UTI"},
            {"name": "Phenazopyridine", "dosage": "200mg three times daily for 2 days", "purpose": "Urinary pain relief"},
        ],
        "home_care": "Drink plenty of water, urinate frequently, cranberry supplements may help prevention.",
        "hospital_advice": "See a doctor for urine test and antibiotic prescription. UTIs require antibiotics.",
        "when_to_seek_emergency": "Fever above 38.5°C, severe back/flank pain, blood in urine, vomiting, or confusion (signs of kidney infection).",
    },
    "Strep Throat": {
        "emergency_level": "moderate",
        "medications": [
            {"name": "Penicillin V", "dosage": "500mg twice daily for 10 days (prescription)", "purpose": "Antibiotic"},
            {"name": "Amoxicillin", "dosage": "500mg three times daily for 10 days (prescription)", "purpose": "Antibiotic alternative"},
            {"name": "Paracetamol", "dosage": "500mg every 4-6 hours", "purpose": "Fever and pain relief"},
            {"name": "Warm salt water gargle", "dosage": "Every 2-3 hours", "purpose": "Soothe sore throat"},
        ],
        "home_care": "Rest, drink warm fluids, soft foods, complete full antibiotic course.",
        "hospital_advice": "See a doctor for rapid strep test and antibiotic prescription. Untreated strep can lead to serious complications.",
        "when_to_seek_emergency": "Difficulty breathing, inability to swallow, severe swelling in throat, or rash spreading over body.",
    },
    "Mononucleosis": {
        "emergency_level": "moderate",
        "medications": [
            {"name": "Paracetamol", "dosage": "500-1000mg every 4-6 hours", "purpose": "Fever and pain relief"},
            {"name": "Ibuprofen", "dosage": "200-400mg every 6-8 hours", "purpose": "Pain and inflammation relief"},
        ],
        "home_care": "Rest (may need weeks), drink fluids, avoid contact sports for at least 4 weeks (risk of spleen rupture).",
        "hospital_advice": "See a doctor for blood test confirmation. Avoid strenuous activity for several weeks.",
        "when_to_seek_emergency": "Sharp sudden pain in upper left abdomen (possible spleen rupture), difficulty breathing, or jaundice.",
    },
    "Malaria": {
        "emergency_level": "critical",
        "medications": [
            {"name": "Artemisinin-based combination therapy (ACT)", "dosage": "As prescribed by doctor", "purpose": "First-line malaria treatment"},
            {"name": "Chloroquine", "dosage": "As prescribed", "purpose": "For chloroquine-sensitive malaria"},
        ],
        "home_care": "DO NOT rely on home treatment. Malaria requires medical diagnosis and prescription antimalarials.",
        "hospital_advice": "🚨 SEEK MEDICAL CARE IMMEDIATELY. Malaria can become fatal rapidly. Blood test needed for diagnosis.",
        "when_to_seek_emergency": "High fever with chills after travel to endemic area, confusion, seizures, dark urine, or jaundice.",
    },
    "Dengue Fever": {
        "emergency_level": "high",
        "medications": [
            {"name": "Paracetamol ONLY", "dosage": "500mg every 4-6 hours", "purpose": "Fever relief (do NOT use Aspirin or Ibuprofen)"},
            {"name": "Oral Rehydration Salts", "dosage": "Sip frequently", "purpose": "Prevent dehydration"},
        ],
        "home_care": "Rest, drink plenty of fluids. DO NOT take Aspirin, Ibuprofen, or Naproxen (increases bleeding risk).",
        "hospital_advice": "⚠️ SEEK MEDICAL ATTENTION. Dengue needs monitoring as it can progress to severe dengue (hemorrhagic).",
        "when_to_seek_emergency": "Severe abdominal pain, persistent vomiting, bleeding gums/nose, blood in stool, extreme fatigue, or restlessness.",
    },

    # ---- ALLERGIC / IMMUNE ----
    "Allergic Rhinitis": {
        "emergency_level": "low",
        "medications": [
            {"name": "Cetirizine (Zyrtec)", "dosage": "10mg once daily", "purpose": "Antihistamine"},
            {"name": "Loratadine (Claritin)", "dosage": "10mg once daily", "purpose": "Non-drowsy antihistamine"},
            {"name": "Fluticasone nasal spray", "dosage": "2 sprays each nostril daily", "purpose": "Nasal corticosteroid"},
        ],
        "home_care": "Avoid allergens, keep windows closed during high pollen, shower after being outdoors, use air purifier.",
        "hospital_advice": "See an allergist if symptoms are persistent or significantly affect quality of life.",
        "when_to_seek_emergency": "Difficulty breathing, swelling of throat/tongue, or widespread hives (may indicate anaphylaxis).",
    },
    "Allergic Reaction": {
        "emergency_level": "high",
        "medications": [
            {"name": "Diphenhydramine (Benadryl)", "dosage": "25-50mg immediately", "purpose": "Fast-acting antihistamine"},
            {"name": "Epinephrine auto-injector (EpiPen)", "dosage": "0.3mg IM if prescribed", "purpose": "Severe allergic reaction (anaphylaxis)"},
            {"name": "Prednisolone", "dosage": "As prescribed by doctor", "purpose": "Reduce severe inflammation"},
        ],
        "home_care": "Remove allergen source. Take antihistamine. Monitor breathing closely.",
        "hospital_advice": "⚠️ SEEK MEDICAL ATTENTION if swelling, difficulty breathing, or widespread reaction.",
        "when_to_seek_emergency": "Difficulty breathing, throat swelling, dizziness/fainting, rapid pulse — USE EPIPEN AND CALL 911.",
    },

    # ---- DERMATOLOGICAL ----
    "Eczema": {
        "emergency_level": "low",
        "medications": [
            {"name": "Hydrocortisone cream 1%", "dosage": "Apply thin layer twice daily for up to 7 days", "purpose": "Reduce inflammation and itching"},
            {"name": "Cetirizine", "dosage": "10mg at bedtime", "purpose": "Reduce itching"},
            {"name": "Emollient moisturizer", "dosage": "Apply liberally multiple times daily", "purpose": "Maintain skin barrier"},
        ],
        "home_care": "Keep skin moisturized, avoid harsh soaps, wear soft fabrics, keep nails short to prevent scratching.",
        "hospital_advice": "See a dermatologist if eczema is widespread, infected (oozing, crusting), or not responding to OTC treatment.",
        "when_to_seek_emergency": "Signs of skin infection (red streaks, pus, fever), or widespread painful rash.",
    },
    "Chickenpox": {
        "emergency_level": "moderate",
        "medications": [
            {"name": "Calamine lotion", "dosage": "Apply to itchy spots as needed", "purpose": "Soothe itching"},
            {"name": "Paracetamol", "dosage": "As directed by age/weight", "purpose": "Fever relief (DO NOT use Aspirin in children)"},
            {"name": "Cetirizine", "dosage": "As directed by age", "purpose": "Reduce itching"},
            {"name": "Acyclovir", "dosage": "As prescribed (high-risk patients)", "purpose": "Antiviral"},
        ],
        "home_care": "Keep cool, trim nails, oatmeal baths, avoid scratching. Isolate patient until all blisters have crusted.",
        "hospital_advice": "See a doctor if adult onset, pregnant, immunocompromised, or if complications develop.",
        "when_to_seek_emergency": "Difficulty breathing, high fever above 39°C, rash near eyes, confusion, or stiff neck.",
    },

    # ---- ENDOCRINE ----
    "Diabetes": {
        "emergency_level": "moderate",
        "medications": [
            {"name": "Metformin", "dosage": "500-1000mg twice daily with meals (prescription)", "purpose": "Blood sugar control (Type 2)"},
            {"name": "Insulin (if prescribed)", "dosage": "As prescribed by endocrinologist", "purpose": "Blood sugar management"},
        ],
        "home_care": "Monitor blood sugar regularly, balanced diet low in refined sugars, regular exercise, maintain healthy weight.",
        "hospital_advice": "See an endocrinologist for proper diagnosis, A1C testing, and treatment plan.",
        "when_to_seek_emergency": "Very high blood sugar (>300 mg/dL), fruity breath odor, confusion, vomiting, rapid breathing (diabetic ketoacidosis).",
    },
    "Hyperthyroidism": {
        "emergency_level": "moderate",
        "medications": [
            {"name": "Methimazole", "dosage": "As prescribed by doctor", "purpose": "Reduce thyroid hormone production"},
            {"name": "Propranolol", "dosage": "20-40mg 3-4 times daily (prescription)", "purpose": "Control rapid heartbeat"},
        ],
        "home_care": "Avoid caffeine and iodine-rich foods. Regular follow-up blood tests essential.",
        "hospital_advice": "See an endocrinologist for thyroid function tests and treatment plan.",
        "when_to_seek_emergency": "Rapid irregular heartbeat, high fever, confusion, or extreme agitation (thyroid storm).",
    },
    "Hypothyroidism": {
        "emergency_level": "low",
        "medications": [
            {"name": "Levothyroxine", "dosage": "25-200mcg once daily on empty stomach (prescription)", "purpose": "Thyroid hormone replacement"},
        ],
        "home_care": "Take medication at same time daily, on empty stomach. Regular blood tests to monitor levels.",
        "hospital_advice": "See an endocrinologist for TSH testing and medication dosing.",
        "when_to_seek_emergency": "Severe fatigue with very low body temperature, extreme swelling, confusion, or slow heartbeat.",
    },

    # ---- MENTAL HEALTH ----
    "Generalized Anxiety Disorder": {
        "emergency_level": "moderate",
        "medications": [
            {"name": "Sertraline", "dosage": "50-200mg daily (prescription)", "purpose": "SSRI for anxiety management"},
            {"name": "Buspirone", "dosage": "5-10mg 2-3 times daily (prescription)", "purpose": "Anti-anxiety medication"},
            {"name": "Chamomile tea", "dosage": "As desired", "purpose": "Natural calming aid"},
        ],
        "home_care": "Regular exercise, deep breathing exercises, adequate sleep, limit caffeine and alcohol.",
        "hospital_advice": "See a psychiatrist or therapist. Cognitive Behavioral Therapy (CBT) is highly effective.",
        "when_to_seek_emergency": "Panic attack that won't resolve, chest pain, suicidal thoughts, or inability to function.",
    },
    "Depression": {
        "emergency_level": "moderate",
        "medications": [
            {"name": "Sertraline", "dosage": "50-200mg daily (prescription)", "purpose": "SSRI antidepressant"},
            {"name": "Fluoxetine", "dosage": "20-80mg daily (prescription)", "purpose": "SSRI antidepressant"},
        ],
        "home_care": "Regular physical activity, maintain social connections, regular sleep schedule, balanced diet.",
        "hospital_advice": "See a psychiatrist or therapist. Combination of therapy and medication is most effective.",
        "when_to_seek_emergency": "Suicidal thoughts or self-harm urges — CALL 988 (Suicide Hotline) or go to nearest ER immediately.",
    },

    # ---- KIDNEY ----
    "Kidney Stones": {
        "emergency_level": "high",
        "medications": [
            {"name": "Ibuprofen", "dosage": "400-600mg every 6-8 hours", "purpose": "Pain and inflammation relief"},
            {"name": "Tamsulosin", "dosage": "0.4mg daily (prescription)", "purpose": "Relax ureter to help pass stone"},
            {"name": "Paracetamol + Codeine", "dosage": "As prescribed", "purpose": "Strong pain relief"},
        ],
        "home_care": "Drink 2-3 liters of water daily to help pass the stone. Strain urine to catch the stone for analysis.",
        "hospital_advice": "⚠️ SEEK MEDICAL ATTENTION. Kidney stones may need imaging and medical/surgical intervention.",
        "when_to_seek_emergency": "Severe unbearable pain, fever with chills, blood in urine, inability to urinate, or persistent vomiting.",
    },

    # ---- ENT ----
    "Otitis Media": {
        "emergency_level": "low",
        "medications": [
            {"name": "Paracetamol", "dosage": "As directed by age/weight", "purpose": "Pain and fever relief"},
            {"name": "Ibuprofen", "dosage": "As directed by age/weight", "purpose": "Pain and inflammation relief"},
            {"name": "Amoxicillin (if prescribed)", "dosage": "As prescribed for 7-10 days", "purpose": "Antibiotic for bacterial infection"},
        ],
        "home_care": "Warm compress on ear, rest, keep ear dry. Many ear infections resolve on their own in 2-3 days.",
        "hospital_advice": "See a doctor if symptoms don't improve in 2-3 days, or if child is under 2 years old.",
        "when_to_seek_emergency": "Pus or blood draining from ear, severe ear pain, high fever, swelling behind ear, or hearing loss.",
    },
    "Tonsillitis": {
        "emergency_level": "moderate",
        "medications": [
            {"name": "Paracetamol", "dosage": "500mg every 4-6 hours", "purpose": "Pain and fever relief"},
            {"name": "Ibuprofen", "dosage": "200-400mg every 6-8 hours", "purpose": "Reduce inflammation"},
            {"name": "Amoxicillin (if bacterial)", "dosage": "500mg three times daily for 10 days", "purpose": "Antibiotic"},
            {"name": "Warm salt water gargle", "dosage": "Every 2-3 hours", "purpose": "Soothe throat pain"},
        ],
        "home_care": "Rest, warm fluids, soft foods, throat lozenges, salt water gargles.",
        "hospital_advice": "See a doctor for proper diagnosis (viral vs bacterial). Bacterial tonsillitis needs antibiotics.",
        "when_to_seek_emergency": "Difficulty breathing or swallowing, drooling, severe throat swelling, or high fever above 39.5°C.",
    },

    # ---- OTHER ----
    "Iron Deficiency": {
        "emergency_level": "low",
        "medications": [
            {"name": "Ferrous sulfate", "dosage": "325mg once or twice daily", "purpose": "Iron replacement"},
            {"name": "Vitamin C", "dosage": "250mg with iron supplement", "purpose": "Enhance iron absorption"},
        ],
        "home_care": "Iron-rich diet (red meat, spinach, lentils, fortified cereals). Avoid tea/coffee with iron supplements.",
        "hospital_advice": "See a doctor for blood tests to confirm and find the cause of iron deficiency.",
        "when_to_seek_emergency": "Severe shortness of breath, chest pain, rapid heartbeat, or fainting.",
    },
    "Vertigo": {
        "emergency_level": "moderate",
        "medications": [
            {"name": "Meclizine", "dosage": "25-50mg every 6 hours", "purpose": "Anti-vertigo and anti-nausea"},
            {"name": "Dimenhydrinate (Dramamine)", "dosage": "50mg every 4-6 hours", "purpose": "Motion sickness and vertigo relief"},
            {"name": "Betahistine", "dosage": "16mg three times daily (prescription)", "purpose": "Improve inner ear blood flow"},
        ],
        "home_care": "Move slowly when changing positions, sit down immediately when dizzy, Epley maneuver for BPPV.",
        "hospital_advice": "See a doctor if vertigo is recurrent, severe, or accompanied by hearing changes.",
        "when_to_seek_emergency": "Vertigo with slurred speech, vision changes, arm/leg weakness, or severe headache (stroke symptoms).",
    },
    "Chronic Fatigue Syndrome": {
        "emergency_level": "low",
        "medications": [
            {"name": "Paracetamol", "dosage": "500mg every 4-6 hours", "purpose": "Pain relief for muscle/joint aches"},
            {"name": "Melatonin", "dosage": "1-3mg at bedtime", "purpose": "Improve sleep quality"},
            {"name": "Low-dose naltrexone (prescription)", "dosage": "As prescribed", "purpose": "May reduce fatigue and pain"},
        ],
        "home_care": "Activity pacing, good sleep hygiene, gentle exercise within tolerance, stress reduction.",
        "hospital_advice": "See a specialist for comprehensive evaluation and management plan.",
        "when_to_seek_emergency": "New severe symptoms, suicidal thoughts, inability to perform basic daily activities.",
    },
}


def generate_dataset(n_samples: int = 6000, seed: int = 42) -> pd.DataFrame:
    """
    Generate a labeled medical dataset.
    Each row = one patient case with binary symptom features + metadata → disease label.
    """
    rng = random.Random(seed)
    np_rng = np.random.RandomState(seed)

    diseases = list(DISEASE_PROFILES.keys())
    # Compute sampling weights from prevalence
    prevalences = np.array([DISEASE_PROFILES[d]["prevalence"] for d in diseases])
    weights = prevalences / prevalences.sum()

    rows = []
    for _ in range(n_samples):
        # Pick disease weighted by prevalence
        disease = np_rng.choice(diseases, p=weights)
        profile = DISEASE_PROFILES[disease]

        # Build symptom vector
        symptom_vec = {}
        for s in ALL_SYMPTOMS:
            prob = profile["symptoms"].get(s, 0.0)
            # Add noise: occasionally add/remove symptoms for realism
            if prob > 0:
                # Symptom present with its probability ± noise
                noisy_prob = max(0.0, min(1.0, prob + rng.gauss(0, 0.08)))
                symptom_vec[s] = 1 if rng.random() < noisy_prob else 0
            else:
                # Small chance of random symptom (noise / comorbidity)
                symptom_vec[s] = 1 if rng.random() < 0.03 else 0

        # Numerical features
        sev_lo, sev_hi = profile["severity_range"]
        dur_lo, dur_hi = profile["duration_range"]
        temp_lo, temp_hi = profile["temp_range"]
        age_lo, age_hi = profile["age_range"]

        severity = rng.randint(sev_lo, sev_hi)
        duration = rng.randint(dur_lo, dur_hi)
        temperature = round(rng.uniform(temp_lo, temp_hi), 1)
        age = rng.randint(age_lo, age_hi)
        gender = rng.choice([0, 1])  # 0=female, 1=male

        row = {
            **symptom_vec,
            "severity": severity,
            "duration_hours": duration,
            "temperature": temperature,
            "age": age,
            "gender": gender,
            "disease": disease,
        }
        rows.append(row)

    df = pd.DataFrame(rows)
    return df


if __name__ == "__main__":
    df = generate_dataset(6000)
    print(f"Dataset shape: {df.shape}")
    print(f"Diseases: {df['disease'].nunique()}")
    print(f"\nDisease distribution:")
    print(df["disease"].value_counts())
    print(f"\nSample row:\n{df.iloc[0]}")
