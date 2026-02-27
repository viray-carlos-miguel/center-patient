"""
Comprehensive Test for All 55 Medical Conditions
Tests the hybrid system with full symptom descriptions for each condition
"""

import requests
import json
import time

def test_all_55_cases():
    """Test all 55 medical conditions with comprehensive symptom descriptions"""
    
    print("🏥 COMPREHENSIVE TEST: ALL 55 MEDICAL CONDITIONS")
    print("=" * 80)
    print("📋 Testing hybrid ML+Rules system with full symptom descriptions")
    print("=" * 80)
    
    # All 55 medical conditions with comprehensive symptom descriptions
    test_cases = [
        {
            "name": "COVID-19",
            "symptoms": {
                "description": "fever, dry cough, loss of taste and smell, fatigue, body aches, sore throat, difficulty breathing",
                "temperature": "38.5",
                "duration_hours": "72",
                "severity": "6",
                "has_fever": True,
                "has_cough": True,
                "has_loss_taste": True,
                "has_loss_smell": True,
                "has_fatigue": True
            }
        },
        {
            "name": "Influenza Type A",
            "symptoms": {
                "description": "high fever, severe body aches, headache, fatigue, dry cough, sore throat, runny nose",
                "temperature": "39.0",
                "duration_hours": "48",
                "severity": "7",
                "has_fever": True,
                "has_headache": True,
                "has_fatigue": True,
                "has_muscle_pain": True,
                "has_cough": True
            }
        },
        {
            "name": "Community-Acquired Pneumonia",
            "symptoms": {
                "description": "high fever, productive cough with green phlegm, chest pain, shortness of breath, fatigue, confusion",
                "temperature": "39.5",
                "duration_hours": "96",
                "severity": "8",
                "has_fever": True,
                "has_cough": True,
                "has_chest_pain": True,
                "has_shortness_of_breath": True,
                "has_fatigue": True
            }
        },
        {
            "name": "Acute Bronchitis",
            "symptoms": {
                "description": "persistent cough, mild fever, chest discomfort, fatigue, clear or white sputum",
                "temperature": "37.8",
                "duration_hours": "120",
                "severity": "5",
                "has_fever": True,
                "has_cough": True,
                "has_chest_pain": True,
                "has_fatigue": True
            }
        },
        {
            "name": "Acute Sinusitis",
            "symptoms": {
                "description": "facial pain and pressure, nasal congestion, thick nasal discharge, headache, fever, reduced sense of smell",
                "temperature": "38.2",
                "duration_hours": "72",
                "severity": "6",
                "has_fever": True,
                "has_headache": True,
                "has_nasal_congestion": True
            }
        },
        {
            "name": "Strep Pharyngitis",
            "symptoms": {
                "description": "severe sore throat, fever, swollen tonsils, difficulty swallowing, swollen lymph nodes",
                "temperature": "39.0",
                "duration_hours": "48",
                "severity": "7",
                "has_fever": True,
                "has_sore_throat": True
            }
        },
        {
            "name": "Infectious Mononucleosis",
            "symptoms": {
                "description": "severe fatigue, fever, sore throat, swollen lymph nodes, swollen spleen, headache",
                "temperature": "38.5",
                "duration_hours": "168",
                "severity": "6",
                "has_fever": True,
                "has_fatigue": True,
                "has_sore_throat": True
            }
        },
        {
            "name": "Acute Tonsillitis",
            "symptoms": {
                "description": "severe sore throat, swollen tonsils, difficulty swallowing, fever, bad breath",
                "temperature": "38.8",
                "duration_hours": "72",
                "severity": "7",
                "has_fever": True,
                "has_sore_throat": True
            }
        },
        {
            "name": "Acute Otitis Media",
            "symptoms": {
                "description": "ear pain, fever, hearing loss, irritability, fluid drainage from ear",
                "temperature": "38.5",
                "duration_hours": "48",
                "severity": "6",
                "has_fever": True
            }
        },
        {
            "name": "Seasonal Allergies",
            "symptoms": {
                "description": "sneezing, runny nose, itchy eyes, nasal congestion, post-nasal drip, fatigue",
                "temperature": "37.0",
                "duration_hours": "240",
                "severity": "3",
                "has_fever": False,
                "has_nasal_congestion": True,
                "has_itching": True,
                "has_sneezing": True
            }
        },
        {
            "name": "Allergic Rhinitis",
            "symptoms": {
                "description": "runny nose, sneezing, itchy eyes, nasal congestion, watery eyes, sinus pressure",
                "temperature": "36.8",
                "duration_hours": "168",
                "severity": "2",
                "has_fever": False,
                "has_nasal_congestion": True,
                "has_itching": True,
                "has_sneezing": True
            }
        },
        {
            "name": "Common Cold",
            "symptoms": {
                "description": "runny or stuffy nose, sore throat, cough, congestion, slight body aches, sneezing, low-grade fever",
                "temperature": "37.5",
                "duration_hours": "72",
                "severity": "3",
                "has_fever": True,
                "has_nasal_congestion": True,
                "has_runny_nose": True,
                "has_sore_throat": True,
                "has_cough_dry": True,
                "has_sneezing": True
            }
        },
        {
            "name": "Acute Gastroenteritis",
            "symptoms": {
                "description": "diarrhea, vomiting, abdominal cramps, nausea, fever, headache",
                "temperature": "38.0",
                "duration_hours": "48",
                "severity": "6",
                "has_fever": True,
                "has_vomiting": True,
                "has_diarrhea": True,
                "has_abdominal_pain": True,
                "has_nausea": True
            }
        },
        {
            "name": "Acute Food Poisoning",
            "symptoms": {
                "description": "sudden nausea, vomiting, diarrhea, abdominal pain, fever, weakness after eating contaminated food",
                "temperature": "38.0",
                "duration_hours": "12",
                "severity": "6",
                "has_fever": False,
                "has_vomiting": True,
                "has_diarrhea": True,
                "has_abdominal_pain": True,
                "has_nausea": True
            }
        },
        {
            "name": "Irritable Bowel Syndrome",
            "symptoms": {
                "description": "abdominal pain, bloating, gas, diarrhea, constipation, mucus in stool, chronic symptoms",
                "temperature": "37.0",
                "duration_hours": "4320",
                "severity": "4",
                "has_fever": False,
                "has_abdominal_pain": True,
                "has_bloating": True,
                "has_diarrhea": True
            }
        },
        {
            "name": "Peptic Ulcer Disease",
            "symptoms": {
                "description": "burning stomach pain, bloating, heartburn, nausea, dark stools, vomiting blood",
                "temperature": "37.0",
                "duration_hours": "168",
                "severity": "5",
                "has_fever": False,
                "has_abdominal_pain": True,
                "has_heartburn": True,
                "has_nausea": True,
                "has_vomiting": True
            }
        },
        {
            "name": "Gastroesophageal Reflux Disease",
            "symptoms": {
                "description": "frequent heartburn, chest pain, difficulty swallowing, regurgitation, chronic cough",
                "temperature": "37.0",
                "duration_hours": "2160",
                "severity": "4",
                "has_fever": False,
                "has_heartburn": True,
                "has_chest_pain": True,
                "has_cough": True
            }
        },
        {
            "name": "Acute Cholecystitis",
            "symptoms": {
                "description": "severe right upper abdominal pain, fever, nausea, vomiting, jaundice",
                "temperature": "38.5",
                "duration_hours": "48",
                "severity": "8",
                "has_fever": True,
                "has_abdominal_pain": True,
                "has_nausea": True,
                "has_vomiting": True
            }
        },
        {
            "name": "Acute Pancreatitis",
            "symptoms": {
                "description": "severe upper abdominal pain radiating to back, nausea, vomiting, fever, rapid pulse",
                "temperature": "38.8",
                "duration_hours": "24",
                "severity": "9",
                "has_fever": True,
                "has_abdominal_pain": True,
                "has_nausea": True,
                "has_vomiting": True
            }
        },
        {
            "name": "Acute Appendicitis",
            "symptoms": {
                "description": "sudden pain near navel shifting to lower right abdomen, pain worsens with movement, nausea, vomiting, low-grade fever",
                "temperature": "38.0",
                "duration_hours": "24",
                "severity": "8",
                "has_fever": True,
                "has_abdominal_pain": True,
                "has_nausea": True,
                "has_vomiting": True,
                "has_loss_of_appetite": True
            }
        },
        {
            "name": "Urinary Tract Infection",
            "symptoms": {
                "description": "painful urination, frequent urination, urgency, cloudy urine, fever, pelvic pain",
                "temperature": "38.2",
                "duration_hours": "48",
                "severity": "6",
                "has_fever": True,
                "has_painful_urination": True,
                "has_frequent_urination": True
            }
        },
        {
            "name": "Nephrolithiasis",
            "symptoms": {
                "description": "severe sharp pain in side and back below ribs, pain radiating to lower abdomen and groin, pain waves, painful urination, pink/red urine",
                "temperature": "37.0",
                "duration_hours": "12",
                "severity": "9",
                "has_fever": False,
                "has_abdominal_pain": True,
                "has_back_pain": True,
                "has_nausea": True,
                "has_vomiting": True,
                "has_painful_urination": True
            }
        },
        {
            "name": "Type 2 Diabetes Mellitus",
            "symptoms": {
                "description": "excessive thirst, frequent urination, extreme hunger, unexplained weight loss, fatigue, blurred vision",
                "temperature": "37.0",
                "duration_hours": "8760",
                "severity": "5",
                "has_fever": False,
                "has_excessive_thirst": True,
                "has_frequent_urination": True,
                "has_fatigue": True,
                "has_vision_changes": True
            }
        },
        {
            "name": "Essential Hypertension",
            "symptoms": {
                "description": "severe headaches, nosebleeds, fatigue, vision problems, chest pain, difficulty breathing, irregular heartbeat",
                "temperature": "37.0",
                "duration_hours": "8760",
                "severity": "4",
                "has_fever": False,
                "has_headache": True,
                "has_nosebleeds": True,
                "has_fatigue": True,
                "has_vision_changes": True,
                "has_chest_pain": True
            }
        },
        {
            "name": "Bronchial Asthma",
            "symptoms": {
                "description": "wheezing, shortness of breath, chest tightness, coughing, difficulty sleeping, anxiety",
                "temperature": "37.0",
                "duration_hours": "168",
                "severity": "6",
                "has_fever": False,
                "has_wheezing": True,
                "has_shortness_of_breath": True,
                "has_chest_tightness": True,
                "has_cough": True
            }
        },
        {
            "name": "Chronic Obstructive Pulmonary Disease",
            "symptoms": {
                "description": "chronic cough, shortness of breath, wheezing, chest tightness, frequent respiratory infections, fatigue",
                "temperature": "37.0",
                "duration_hours": "8760",
                "severity": "6",
                "has_fever": False,
                "has_shortness_of_breath": True,
                "has_wheezing": True,
                "has_cough": True,
                "has_fatigue": True
            }
        },
        {
            "name": "Angina Pectoris",
            "symptoms": {
                "description": "chest pain during exertion, pressure in chest, pain radiating to arm, neck, jaw, shortness of breath",
                "temperature": "37.0",
                "duration_hours": "48",
                "severity": "7",
                "has_fever": False,
                "has_chest_pain": True,
                "has_shortness_of_breath": True
            }
        },
        {
            "name": "Acute Myocardial Infarction",
            "symptoms": {
                "description": "crushing chest pain, pain radiating to left arm, sweating, shortness of breath, nausea, lightheadedness",
                "temperature": "37.0",
                "duration_hours": "2",
                "severity": "10",
                "has_fever": False,
                "has_chest_pain": True,
                "has_shortness_of_breath": True,
                "has_nausea": True,
                "has_vomiting": True
            }
        },
        {
            "name": "Cardiac Arrhythmia",
            "symptoms": {
                "description": "irregular heartbeat, palpitations, chest pain, shortness of breath, dizziness, sweating",
                "temperature": "37.0",
                "duration_hours": "24",
                "severity": "6",
                "has_fever": False,
                "has_palpitations": True,
                "has_chest_pain": True,
                "has_shortness_of_breath": True,
                "has_dizziness": True
            }
        },
        {
            "name": "Congestive Heart Failure",
            "symptoms": {
                "description": "shortness of breath, fatigue, swelling in legs, rapid heartbeat, persistent cough, fluid retention",
                "temperature": "37.0",
                "duration_hours": "168",
                "severity": "7",
                "has_fever": False,
                "has_shortness_of_breath": True,
                "has_leg_swelling": True,
                "has_fatigue": True,
                "has_cough": True
            }
        },
        {
            "name": "Aortic Dissection",
            "symptoms": {
                "description": "sudden severe chest or back pain, tearing sensation, pain radiating to back, sweating, shortness of breath",
                "temperature": "37.0",
                "duration_hours": "1",
                "severity": "10",
                "has_fever": False,
                "has_chest_pain": True,
                "has_shortness_of_breath": True
            }
        },
        {
            "name": "Pulmonary Embolism",
            "symptoms": {
                "description": "sudden sharp chest pain when breathing deeply, rapid heartbeat, shortness of breath, coughing up blood, leg pain and swelling",
                "temperature": "37.0",
                "duration_hours": "3",
                "severity": "9",
                "has_fever": False,
                "has_chest_pain": True,
                "has_shortness_of_breath": True,
                "has_leg_swelling": True,
                "has_cough": True
            }
        },
        {
            "name": "Deep Vein Thrombosis",
            "symptoms": {
                "description": "leg pain or swelling, warmth in affected area, red or discolored skin, leg cramps, visible veins",
                "temperature": "37.0",
                "duration_hours": "168",
                "severity": "6",
                "has_fever": False,
                "has_leg_swelling": True
            }
        },
        {
            "name": "Acute Stroke",
            "symptoms": {
                "description": "sudden numbness or weakness in face, arm, or leg, confusion, trouble speaking, vision problems, sudden severe headache",
                "temperature": "37.0",
                "duration_hours": "1",
                "severity": "10",
                "has_fever": False,
                "has_numbness": True,
                "has_limb_weakness": True,
                "has_headache": True
            }
        },
        {
            "name": "Epileptic Seizure",
            "symptoms": {
                "description": "uncontrollable jerking movements, loss of consciousness, confusion, staring spell, fear, anxiety",
                "temperature": "37.0",
                "duration_hours": "1",
                "severity": "8",
                "has_fever": False,
                "has_seizures": True,
                "has_confusion": True
            }
        },
        {
            "name": "Parkinson's Disease",
            "symptoms": {
                "description": "tremor, slowed movement, rigid muscles, impaired posture, loss of automatic movements, speech changes",
                "temperature": "37.0",
                "duration_hours": "8760",
                "severity": "5",
                "has_fever": False,
                "has_tremors": True,
                "has_fatigue": True
            }
        },
        {
            "name": "Multiple Sclerosis",
            "symptoms": {
                "description": "numbness or weakness in limbs, electric shock sensations, vision problems, tremor, fatigue, dizziness",
                "temperature": "37.0",
                "duration_hours": "4320",
                "severity": "6",
                "has_fever": False,
                "has_numbness": True,
                "has_vision_changes": True,
                "has_tremors": True,
                "has_fatigue": True,
                "has_dizziness": True
            }
        },
        {
            "name": "Major Depressive Disorder",
            "symptoms": {
                "description": "persistent sadness, loss of interest, sleep disturbances, fatigue, worthlessness, concentration problems",
                "temperature": "37.0",
                "duration_hours": "2160",
                "severity": "5",
                "has_fever": False,
                "has_depression": True,
                "has_fatigue": True,
                "has_sleep_disturbances": True
            }
        },
        {
            "name": "Generalized Anxiety Disorder",
            "symptoms": {
                "description": "excessive worry, restlessness, fatigue, difficulty concentrating, irritability, muscle tension, sleep problems",
                "temperature": "37.0",
                "duration_hours": "2160",
                "severity": "4",
                "has_fever": False,
                "has_anxiety": True,
                "has_fatigue": True,
                "has_sleep_disturbances": True
            }
        },
        {
            "name": "Insomnia Disorder",
            "symptoms": {
                "description": "difficulty falling asleep, waking up during night, waking up too early, daytime fatigue, irritability",
                "temperature": "37.0",
                "duration_hours": "168",
                "severity": "4",
                "has_fever": False,
                "has_sleep_disturbances": True,
                "has_fatigue": True
            }
        },
        {
            "name": "Hypothyroidism",
            "symptoms": {
                "description": "fatigue, weight gain, cold intolerance, dry skin, constipation, depression, slowed heart rate",
                "temperature": "36.5",
                "duration_hours": "4320",
                "severity": "4",
                "has_fever": False,
                "has_fatigue": True,
                "has_weight_gain": True,
                "has_depression": True
            }
        },
        {
            "name": "Hyperthyroidism",
            "symptoms": {
                "description": "weight loss, rapid heartbeat, anxiety, irritability, heat intolerance, sweating, fatigue",
                "temperature": "37.5",
                "duration_hours": "168",
                "severity": "5",
                "has_fever": False,
                "has_weight_loss": True,
                "has_palpitations": True,
                "has_anxiety": True,
                "has_fatigue": True
            }
        },
        {
            "name": "Atopic Dermatitis",
            "symptoms": {
                "description": "dry skin, itching especially at night, red to brownish-gray patches, small raised bumps, thickened cracked scaly skin",
                "temperature": "37.0",
                "duration_hours": "2160",
                "severity": "5",
                "has_fever": False,
                "has_skin_rash": True,
                "has_itching": True
            }
        },
        {
            "name": "Psoriasis",
            "symptoms": {
                "description": "red patches of skin covered with thick silvery scales, dry cracked skin that may bleed, itching burning or soreness",
                "temperature": "37.0",
                "duration_hours": "4320",
                "severity": "5",
                "has_fever": False,
                "has_skin_rash": True,
                "has_itching": True
            }
        },
        {
            "name": "Cellulitis",
            "symptoms": {
                "description": "red, swollen, warm skin area, pain, fever, chills, red streaks from infection, skin breakdown",
                "temperature": "38.5",
                "duration_hours": "72",
                "severity": "7",
                "has_fever": True,
                "has_skin_rash": True
            }
        },
        {
            "name": "Contact Dermatitis",
            "symptoms": {
                "description": "red rash, itching, dry scaly skin, swelling, burning, tenderness, blisters after exposure to allergen",
                "temperature": "37.0",
                "duration_hours": "48",
                "severity": "4",
                "has_fever": False,
                "has_skin_rash": True,
                "has_itching": True
            }
        },
        {
            "name": "Urticaria",
            "symptoms": {
                "description": "hives, wheals, red or skin-colored welts, itching, burning or stinging, swelling of lips, tongue, face",
                "temperature": "37.0",
                "duration_hours": "48",
                "severity": "4",
                "has_fever": False,
                "has_skin_rash": True,
                "has_itching": True
            }
        },
        {
            "name": "Acne Vulgaris",
            "symptoms": {
                "description": "whiteheads, blackheads, pimples, cysts, nodules, oily skin, scarring, redness",
                "temperature": "37.0",
                "duration_hours": "4320",
                "severity": "3",
                "has_fever": False,
                "has_skin_rash": True
            }
        },
        {
            "name": "Rosacea",
            "symptoms": {
                "description": "facial redness, swollen red bumps, visible blood vessels, burning or stinging sensation, eye problems",
                "temperature": "37.0",
                "duration_hours": "4320",
                "severity": "4",
                "has_fever": False,
                "has_skin_rash": True
            }
        },
        {
            "name": "Folliculitis",
            "symptoms": {
                "description": "small red bumps or white-headed pimples around hair follicles, itching, tenderness, pain, crusty sores",
                "temperature": "38.0",
                "duration_hours": "72",
                "severity": "5",
                "has_fever": True,
                "has_skin_rash": True
            }
        },
        {
            "name": "Herpes Zoster",
            "symptoms": {
                "description": "pain burning numbness tingling, sensitivity to touch, red rash with fluid-filled blisters, itching, fever, headache",
                "temperature": "38.0",
                "duration_hours": "72",
                "severity": "7",
                "has_fever": True,
                "has_skin_rash": True,
                "has_headache": True,
                "has_fatigue": True
            }
        },
        {
            "name": "Impetigo",
            "symptoms": {
                "description": "red sores on face, especially around nose and mouth, honey-colored crusts, fever, itching, blisters",
                "temperature": "38.0",
                "duration_hours": "48",
                "severity": "5",
                "has_fever": True,
                "has_skin_rash": True
            }
        },
        {
            "name": "Scabies",
            "symptoms": {
                "description": "intense itching especially at night, burrows in skin, pimple-like irritations, rash, sores from scratching",
                "temperature": "37.0",
                "duration_hours": "168",
                "severity": "6",
                "has_fever": False,
                "has_itching": True,
                "has_skin_rash": True
            }
        },
        {
            "name": "Tinea Corporis",
            "symptoms": {
                "description": "ring-shaped rash, red, itchy, scaly skin, slightly raised, expanding rings, clear skin inside",
                "temperature": "37.0",
                "duration_hours": "72",
                "severity": "3",
                "has_fever": False,
                "has_skin_rash": True,
                "has_itching": True
            }
        },
        {
            "name": "Tinea Pedis",
            "symptoms": {
                "description": "itching, stinging, burning between toes, cracking, peeling skin, raw skin, blisters, dry scaly skin",
                "temperature": "37.0",
                "duration_hours": "168",
                "severity": "3",
                "has_fever": False,
                "has_skin_rash": True,
                "has_itching": True
            }
        },
        {
            "name": "Vaginal Candidiasis",
            "symptoms": {
                "description": "genital itching, burning, redness, swelling, vaginal rash, watery vaginal discharge, thick white discharge",
                "temperature": "37.0",
                "duration_hours": "72",
                "severity": "4",
                "has_fever": False,
                "has_itching": True
            }
        },
        {
            "name": "Meningitis",
            "symptoms": {
                "description": "severe headache with stiff neck, high fever, sensitivity to light, confusion, nausea and vomiting, seizures",
                "temperature": "39.5",
                "duration_hours": "12",
                "severity": "9",
                "has_fever": True,
                "has_headache": True,
                "has_nausea": True,
                "has_vomiting": True,
                "has_confusion": True,
                "has_photophobia": True
            }
        },
        {
            "name": "Sepsis",
            "symptoms": {
                "description": "high fever with chills, rapid heart rate, rapid breathing, confusion, extreme pain, clammy skin, shortness of breath",
                "temperature": "39.8",
                "duration_hours": "8",
                "severity": "10",
                "has_fever": True,
                "has_confusion": True,
                "has_shortness_of_breath": True,
                "has_chills": True
            }
        }
    ]
    
    passed = 0
    failed = 0
    results = []
    
    print(f'Testing {len(test_cases)} medical conditions...')
    print()
    
    for i, test in enumerate(test_cases, 1):
        name = test['name']
        symptoms = test['symptoms']
        
        try:
            response = requests.post(
                'http://localhost:8000/api/gemini/analyze-symptoms',
                json={'symptoms': symptoms},
                timeout=30
            )
            result = response.json()
            
            predicted = result['analysis']['primary_prediction']['condition']
            confidence = result['analysis']['primary_prediction']['confidence']
            ai_model = result['analysis'].get('ai_model', 'unknown')
            complexity = result['analysis'].get('complexity_analysis', {})
            
            status = '✅' if predicted == name else '❌'
            comp_score = complexity.get('score', 0) if complexity else 0
            method = complexity.get('prediction_method', 'unknown') if complexity else 'unknown'
            
            print(f'{i:2d}. {status} {name}')
            print(f'    Predicted: {predicted} ({confidence}%)')
            print(f'    Model: {ai_model}')
            print(f'    Complexity: {comp_score:.0f} - Method: {method}')
            print()
            
            if predicted == name:
                passed += 1
            else:
                failed += 1
            
            results.append({
                'expected': name,
                'predicted': predicted,
                'correct': predicted == name,
                'confidence': confidence,
                'model': ai_model,
                'complexity': comp_score
            })
            
        except Exception as e:
            print(f'{i:2d}. ❌ {name}: ERROR - {str(e)}')
            failed += 1
            results.append({
                'expected': name,
                'predicted': 'ERROR',
                'correct': False,
                'confidence': 0,
                'model': 'error',
                'complexity': 0
            })
    
    print('=' * 80)
    print(f'📊 FINAL RESULTS: {passed}/{len(test_cases)} ({passed/len(test_cases)*100:.1f}%)')
    print(f'✅ Correct: {passed} | ❌ Incorrect: {failed}')
    print('=' * 80)
    
    # Analysis by complexity
    simple_cases = [r for r in results if r['complexity'] < 40]
    complex_cases = [r for r in results if r['complexity'] >= 40]
    
    if simple_cases:
        simple_correct = sum(1 for r in simple_cases if r['correct'])
        print(f'📋 Simple Cases (<40 complexity): {simple_correct}/{len(simple_cases)} ({simple_correct/len(simple_cases)*100:.1f}%)')
    
    if complex_cases:
        complex_correct = sum(1 for r in complex_cases if r['correct'])
        print(f'🧠 Complex Cases (≥40 complexity): {complex_correct}/{len(complex_cases)} ({complex_correct/len(complex_cases)*100:.1f}%)')
    
    print()
    if passed >= 50:
        print('🎉 EXCELLENT: Near-perfect accuracy across all conditions!')
    elif passed >= 45:
        print('✅ VERY GOOD: High accuracy across most conditions')
    elif passed >= 40:
        print('⚠️  GOOD: Decent accuracy but room for improvement')
    elif passed >= 30:
        print('⚠️  MODERATE: Some accuracy issues need attention')
    else:
        print('❌ POOR: Significant accuracy issues require fixes')
    
    # Show failed cases
    failed_cases = [r for r in results if not r['correct'] and r['predicted'] != 'ERROR']
    if failed_cases:
        print('\n🔍 FAILED CASES ANALYSIS:')
        for case in failed_cases[:10]:  # Show first 10 failed cases
            print(f'   {case["expected"]} → {case["predicted"]} ({case["confidence"]}%)')
        if len(failed_cases) > 10:
            print(f'   ... and {len(failed_cases) - 10} more failed cases')
    
    return passed, failed, results

if __name__ == '__main__':
    test_all_55_cases()
