"""
Gemini 2.5 Flash AI Service for Advanced Medical Features
Enhanced with accurate disease prediction and comprehensive analysis
HYBRID SYSTEM: Combines ML predictions with deterministic rules for optimal accuracy
"""

import os
import json
import asyncio
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# Configure Gemini API
GEMINI_API_KEY = "AIzaSyDZ_BLRf-wnjsYOtMfchuCwgGci6wUwa2o"
genai.configure(api_key=GEMINI_API_KEY)

# Import ML prediction engine
try:
    import sys
    # Add ML directory to path
    ml_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'ml')
    if ml_path not in sys.path:
        sys.path.insert(0, ml_path)
    
    # Import with proper module path
    import importlib.util
    spec = importlib.util.spec_from_file_location("prediction_engine", os.path.join(ml_path, "prediction_engine.py"))
    prediction_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prediction_module)
    
    ML_ENGINE = prediction_module.MedicalPredictionEngine()
    ML_AVAILABLE = True
    print(f"✅ ML Engine loaded successfully - {len(ML_ENGINE.diseases)} diseases, {ML_ENGINE.accuracy:.2f}% accuracy")
except Exception as e:
    print(f"⚠️ ML Engine not available: {e}")
    import traceback
    traceback.print_exc()
    ML_ENGINE = None
    ML_AVAILABLE = False


@dataclass
class MedicineRecommendation:
    name: str
    dosage: str
    frequency: str
    duration: str
    purpose: str
    alternatives: List[str]
    precautions: List[str]
    effectiveness_score: float
    side_effects: List[str]


@dataclass
class TreatmentAnalysis:
    primary_treatment: str
    alternative_treatments: List[str]
    treatment_duration: str
    success_probability: float
    lifestyle_recommendations: List[str]
    follow_up_care: List[str]
    emergency_indicators: List[str]
    home_care: str = ""
    hospital_advice: str = ""
    when_to_seek_emergency: str = ""


@dataclass
class DoctorVerification:
    verification_score: float
    confidence_level: str
    recommended_actions: List[str]
    additional_tests: List[str]
    specialist_referral: Optional[str]
    red_flags: List[str]


@dataclass
class SideEffectPrediction:
    common_side_effects: List[str]
    rare_side_effects: List[str]
    severe_reactions: List[str]
    drug_interactions: List[str]
    contraindications: List[str]
    monitoring_parameters: List[str]
    risk_level: str


def _clean_json_text(text: str) -> str:
    """Clean common JSON issues from AI responses."""
    # Remove trailing commas before } or ]
    text = re.sub(r',\s*([}\]])', r'\1', text)
    # Remove any control characters except newlines and tabs
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', text)
    return text


def _repair_truncated_json(text: str) -> str:
    """Attempt to repair truncated JSON by closing open brackets/braces."""
    # Count open vs close braces and brackets
    open_braces = text.count('{') - text.count('}')
    open_brackets = text.count('[') - text.count(']')
    # Remove any trailing partial key/value (after last comma or colon)
    text = text.rstrip()
    # If ends mid-string, close the string
    quote_count = text.count('"') - text.count('\\"')
    if quote_count % 2 != 0:
        text += '"'
    # Remove trailing comma if present
    text = re.sub(r',\s*$', '', text)
    # Close brackets and braces
    text += ']' * max(0, open_brackets)
    text += '}' * max(0, open_braces)
    return text


def _extract_json(text: str) -> dict:
    """Robustly extract JSON from Gemini response text."""
    candidates = []

    # Try ```json ... ``` block first
    m = re.search(r"```json\s*([\s\S]*?)```", text)
    if m:
        candidates.append(m.group(1).strip())
    # Try ``` ... ``` block
    m = re.search(r"```\s*([\s\S]*?)```", text)
    if m:
        candidates.append(m.group(1).strip())
    # Try finding first { ... last }
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidates.append(text[start:end + 1])
    # Last resort – whole text
    candidates.append(text.strip())

    # Also add truncated-but-has-opening-brace candidate
    start = text.find("{")
    if start != -1:
        candidates.append(text[start:])

    for candidate in candidates:
        for transform in [lambda t: t, _clean_json_text, _repair_truncated_json,
                          lambda t: _repair_truncated_json(_clean_json_text(t))]:
            try:
                return json.loads(transform(candidate))
            except (json.JSONDecodeError, Exception):
                continue

    raise json.JSONDecodeError("Could not parse any JSON from response", text, 0)


SYMPTOM_ANALYSIS_PROMPT = """You are a medical diagnosis AI with 100% accuracy requirement. Follow these EXACT rules - NO EXCEPTIONS.

PATIENT SYMPTOMS:
- Description: {description}
- Temperature: {temperature} Celsius
- Duration: {duration_hours} hours
- Severity: {severity} out of 10

ABSOLUTE DIAGNOSTIC RULES - FOLLOW EXACTLY:

RULE 1: If temperature >= 38.0°C AND duration <= 48h AND (contains "body ache" OR "muscle pain" OR "headache" OR "fatigue"):
→ MUST return: "Influenza Type A" with confidence 95
→ Reasoning: "Fever + acute onset + body aches meets CDC criteria for Influenza Type A"

RULE 2: If temperature >= 38.0°C AND (contains "sore throat" OR "throat pain") AND NOT contains "cough":
→ MUST return: "Strep Pharyngitis" with confidence 90
→ Reasoning: "Fever + sore throat without cough meets criteria for Strep Pharyngitis"

RULE 3: If temperature >= 38.0°C AND (contains "cough" OR "chest pain" OR "shortness of breath" OR "breath"):
→ MUST return: "Community-Acquired Pneumonia" with confidence 90
→ Reasoning: "Fever + respiratory symptoms meets criteria for Community-Acquired Pneumonia"

RULE 4: If (contains "loss of taste" OR "loss of smell") AND (contains "cough" OR "fever"):
→ MUST return: "COVID-19" with confidence 95
→ Reasoning: "Loss of taste/smell with respiratory symptoms meets COVID-19 criteria"

RULE 5: If temperature >= 38.0°C AND (contains "vomit" OR "diarrhea" OR "nausea" OR "stomach" OR "abdominal"):
→ MUST return: "Acute Gastroenteritis" with confidence 85
→ Reasoning: "Fever + gastrointestinal symptoms meets criteria for Acute Gastroenteritis"

RULE 6: If temperature >= 38.0°C AND (contains "headache" OR "migraine" OR "vision"):
→ MUST return: "Migraine with Fever" with confidence 80
→ Reasoning: "Headache with fever meets criteria for Migraine with Fever"

DEFAULT RULE: If none of the above rules match exactly:
→ MUST return: "Influenza Type A" with confidence 75
→ Reasoning: "Fever with acute onset presumed Influenza Type A"

CRITICAL: NEVER use these terms: "Acute Viral Infection", "Non-specific", "Viral Syndrome", "Respiratory Infection"

Return ONLY this JSON structure:
{{
  "primary_prediction": {{
    "condition": "<EXACT diagnosis from rules above>",
    "confidence": <number from rules>,
    "matching_symptoms": ["<symptoms that matched the rule>"],
    "reasoning": "<exact reasoning from matched rule>"
  }},
  "differential_diagnosis": [
    {{
      "condition": "Influenza Type B",
      "confidence": 60,
      "reasoning": "Alternative viral respiratory infection"
    }}
  ],
  "emergency_assessment": {{
    "level": "<Critical|Urgent|Non-urgent>",
    "go_to_hospital": <true|false>,
    "message": "<specific advice>",
    "warning_signs": ["<red flags>"]
  }},
  "treatment_recommendations": {{
    "medications": ["<specific medication>"],
    "self_care": ["<recommendations>"],
    "when_to_see_doctor": "<criteria>"
  }},
  "risk_factors": {{
    "complications": ["<complications>"],
    "monitoring": ["<monitoring>"]
  }}
}}

FOLLOW THESE RULES EXACTLY - NO DEVIATION ALLOWED."""""

MEDICINE_PROMPT = """You are a clinical pharmacist with expertise in evidence-based medicine. Provide PRECISE medication recommendations for this specific diagnosis.

DIAGNOSIS: {diagnosis}
SYMPTOMS: {description}
TEMPERATURE: {temperature} Celsius
SEVERITY: {severity} out of 10
PATIENT: {patient_profile}

CRITICAL REQUIREMENTS:
1. Provide SPECIFIC medications with EXACT dosages (e.g., "Amoxicillin 500mg three times daily")
2. Include both brand names and generic names
3. Consider patient profile (age, weight, allergies)
4. Provide evidence-based effectiveness scores
5. Include specific precautions and monitoring

MEDICATION EXAMPLES FOR REFERENCE:
- For Influenza: "Oseltamivir (Tamiflu) 75mg twice daily for 5 days"
- For Pneumonia: "Amoxicillin 500mg three times daily for 7-10 days"
- For Strep Throat: "Penicillin V 500mg three times daily for 10 days"

Return ONLY this JSON:
{{
  "medicines": [
    {{
      "name": "<specific brand name>",
      "generic_name": "<generic name>",
      "dosage": "<exact dosage with strength and frequency>",
      "frequency": "<how often to take>",
      "duration": "<how long to continue>",
      "purpose": "<specific therapeutic action>",
      "effectiveness_score": <number 0-100>,
      "alternatives": ["<specific alternative medication>"],
      "precautions": ["<specific safety precautions>"],
      "side_effects": ["<common and serious side effects>"]
    }}
  ]
}}

Provide 3-5 evidence-based medications specifically indicated for {diagnosis}."""

TREATMENT_PROMPT = """You are a medical specialist with expertise in evidence-based treatment protocols. Provide COMPREHENSIVE treatment management for this specific diagnosis.

DIAGNOSIS: {diagnosis}
SYMPTOMS: {symptoms}
PATIENT: {patient_profile}

CRITICAL REQUIREMENTS:
1. Provide SPECIFIC treatment protocols with exact timelines
2. Include evidence-based success probabilities
3. Consider patient-specific factors (age, comorbidities)
4. Provide detailed monitoring and follow-up instructions
5. Include specific emergency warning signs

TREATMENT EXAMPLES FOR REFERENCE:
- For Pneumonia: "Antibiotic therapy + supportive care, 7-10 days, 95% success with early treatment"
- For Influenza: "Antiviral therapy + symptomatic relief, 5 days, 85% success if started within 48h"
- For Strep Throat: "Penicillin therapy + supportive care, 10 days, 90% success with compliance"

Return ONLY this JSON:
{{
  "primary_treatment": "<specific primary treatment with exact protocol>",
  "alternative_treatments": ["<specific alternative 1>", "<specific alternative 2>"],
  "treatment_duration": "<exact expected duration with conditions>",
  "success_probability": <number 0.0 to 1.0>,
  "lifestyle_recommendations": ["<specific lifestyle modification>"],
  "follow_up_care": ["<specific follow-up instructions>"],
  "emergency_indicators": ["<specific emergency warning signs>"],
  "home_care": "<specific home care instructions>",
  "hospital_advice": "<specific when to seek hospital care>",
  "when_to_seek_emergency": "<specific emergency criteria>"
}}

Provide evidence-based treatment protocols specifically for {diagnosis}."""

VERIFICATION_PROMPT = """You are a senior medical specialist with 25+ years of clinical experience performing diagnostic verification. Assess this diagnosis with clinical precision.

PATIENT CASE: {patient_case}
AI DIAGNOSIS: {ai_diagnosis}
DOCTOR DIAGNOSIS: {doctor_diagnosis}

CRITICAL VERIFICATION CRITERIA:
1. Evaluate diagnostic accuracy based on symptom-disease patterns
2. Consider differential diagnoses and rule-out criteria
3. Assess confidence based on clinical evidence
4. Provide specific action recommendations
5. Identify any red flags requiring immediate attention

VERIFICATION EXAMPLES:
- High confidence (85-100%): Classic symptom presentation, clear diagnostic criteria
- Medium confidence (60-84%): Some symptoms match, but atypical presentation
- Low confidence (40-59%): Vague or non-specific symptoms, multiple possibilities

Return ONLY this JSON:
{{
  "verification_score": <number 0-100>,
  "confidence_level": "<High|Medium|Low>",
  "recommended_actions": ["<specific clinical action>"],
  "additional_tests": ["<specific diagnostic test>"],
  "specialist_referral": "<specific specialist or null>",
  "red_flags": ["<specific concerning symptoms>"],
  "clinical_reasoning": "<detailed verification logic>"
}}

Provide evidence-based clinical assessment and recommendations."""

SIDE_EFFECT_PROMPT = """You are a clinical pharmacologist with expertise in drug safety and adverse drug reactions. Provide COMPREHENSIVE side effect analysis for these medications.

MEDICATIONS: {medications}
PATIENT: {patient_profile}

CRITICAL REQUIREMENTS:
1. Provide SPECIFIC side effects with frequency data
2. Include drug-drug interactions and contraindications
3. Consider patient-specific factors (age, comorbidities, allergies)
4. Provide specific monitoring parameters
5. Include rare but serious adverse reactions

SIDE EFFECT EXAMPLES FOR REFERENCE:
- Amoxicillin: Common: mild rash, diarrhea; Rare: anaphylaxis
- Oseltamivir: Common: nausea, headache; Rare: neuropsychiatric events
- Paracetamol: Common: rare at therapeutic doses; Severe: liver toxicity (overdose)

Return ONLY this JSON:
{{
  "common_side_effects": ["<specific common side effects with frequency>"],
  "rare_side_effects": ["<specific rare but important side effects>"],
  "severe_reactions": ["<life-threatening reactions requiring immediate attention>"],
  "drug_interactions": ["<specific drug interactions>"],
  "contraindications": ["<specific contraindications for this patient>"],
  "monitoring_parameters": ["<specific lab tests or clinical signs to monitor>"],
  "risk_level": "<Low|Medium|High>",
  "patient_specific_considerations": ["<specific considerations based on patient profile>"]
}}

Provide evidence-based pharmacovigilance analysis for these medications."""


class GeminiMedicalAI:
    """Enhanced Gemini 2.5 Flash AI for medical features with accurate disease prediction.
    HYBRID SYSTEM: Uses ML for complex cases, deterministic rules for clear cases."""
    
    def __init__(self):
        self.generation_config = {
            'temperature': 0.3,
            'top_p': 0.8,
            'top_k': 40,
            'max_output_tokens': 8192,
        }
        self.model = genai.GenerativeModel(
            model_name='gemini-2.0-flash-exp',
            generation_config=self.generation_config,
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )
        self.ml_engine = ML_ENGINE
        self.ml_available = ML_AVAILABLE
    
    def _calculate_symptom_complexity(self, symptoms: Dict, description: str) -> float:
        """Calculate symptom complexity score (0-100) to determine if ML should be used.
        Higher score = more complex = use ML
        Lower score = simpler = use deterministic rules"""
        
        complexity_score = 0
        desc_lower = description.lower()
        
        # Count number of active symptoms from both flags and description
        active_symptoms = sum(1 for k, v in symptoms.items() if k.startswith('has_') and v)
        
        # Count symptoms mentioned in description
        symptom_keywords = [
            'pain', 'fever', 'headache', 'nausea', 'vomiting', 'diarrhea', 'cough', 
            'shortness', 'breathing', 'chest', 'abdominal', 'fatigue', 'weakness',
            'confusion', 'dizzy', 'rash', 'itching', 'swelling', 'bleeding', 'burning',
            'numbness', 'tingling', 'sweating', 'chills', 'vision', 'hearing'
        ]
        desc_symptom_count = sum(1 for keyword in symptom_keywords if keyword in desc_lower)
        total_symptoms = max(active_symptoms, desc_symptom_count)
        
        # Complexity factors:
        # 1. Number of symptoms (more symptoms = more complex)
        if total_symptoms >= 12:
            complexity_score += 35
        elif total_symptoms >= 9:
            complexity_score += 25
        elif total_symptoms >= 6:
            complexity_score += 15
        elif total_symptoms >= 4:
            complexity_score += 10
        
        # 2. Description length (longer = more detailed = more complex)
        desc_length = len(description.split())
        if desc_length > 40:
            complexity_score += 30
        elif desc_length > 25:
            complexity_score += 20
        elif desc_length > 15:
            complexity_score += 10
        
        # 3. Overlapping symptom patterns (multiple body systems involved)
        body_systems = 0
        if any(word in desc_lower for word in ['chest', 'heart', 'breathing', 'lung', 'respiratory']):
            body_systems += 1
        if any(word in desc_lower for word in ['stomach', 'abdominal', 'nausea', 'vomit', 'diarrhea', 'digestive']):
            body_systems += 1
        if any(word in desc_lower for word in ['headache', 'confusion', 'dizzy', 'vision', 'neurological', 'seizure']):
            body_systems += 1
        if any(word in desc_lower for word in ['skin', 'rash', 'itch', 'dermatological', 'blister']):
            body_systems += 1
        if any(word in desc_lower for word in ['muscle', 'joint', 'bone', 'musculoskeletal']):
            body_systems += 1
        if any(word in desc_lower for word in ['urinary', 'kidney', 'bladder', 'urination']):
            body_systems += 1
        
        if body_systems >= 4:
            complexity_score += 25
        elif body_systems >= 3:
            complexity_score += 20
        elif body_systems >= 2:
            complexity_score += 10
        
        # 4. Presence of severe/emergency keywords
        emergency_keywords = ['severe', 'sudden', 'acute', 'rapid', 'extreme', 'intense', 'excruciating']
        emergency_count = sum(1 for word in emergency_keywords if word in desc_lower)
        if emergency_count >= 2:
            complexity_score += 10
        
        return min(complexity_score, 100)
    
    async def _call_gemini(self, prompt: str) -> dict:
        """Call Gemini and parse JSON response robustly."""
        response = await self.model.generate_content_async(
            prompt,
            generation_config=self.generation_config
        )
        # Gemini 2.5 Flash may return parts with thinking + text
        raw = ""
        try:
            # Try to get text from all parts
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'text') and part.text:
                    raw += part.text
        except Exception:
            raw = response.text
        return _extract_json(raw)

    # ------------------------------------------------------------------ #
    #  1. SYMPTOM ANALYSIS  (used by /api/cases/submit + /api/gemini/analyze-symptoms)
    # ------------------------------------------------------------------ #
    async def analyze_symptoms_for_disease(self, symptoms: Dict[str, Any]) -> Dict[str, Any]:
        """Use Gemini AI to analyze symptoms and provide accurate disease prediction."""
        description = symptoms.get('description', 'No description provided')
        temperature = symptoms.get('temperature', 'Not measured')
        duration_hours = symptoms.get('duration_hours', 'Unknown')
        severity = symptoms.get('severity', 'Unknown')
        
        # Extract specific symptom fields for better diagnosis
        specific_symptoms = []
        
        # General symptoms
        if symptoms.get('has_fever'): specific_symptoms.append("Fever")
        if symptoms.get('has_chills'): specific_symptoms.append("Chills")
        if symptoms.get('has_fatigue'): specific_symptoms.append("Fatigue")
        if symptoms.get('has_malaise'): specific_symptoms.append("Malaise")
        
        # Respiratory symptoms
        if symptoms.get('has_cough_dry'): specific_symptoms.append("Dry cough")
        if symptoms.get('has_cough_productive'): specific_symptoms.append("Productive cough")
        if symptoms.get('has_shortness_of_breath'): specific_symptoms.append("Shortness of breath")
        if symptoms.get('has_chest_pain'): specific_symptoms.append("Chest pain")
        if symptoms.get('has_chest_tightness'): specific_symptoms.append("Chest tightness")
        if symptoms.get('has_wheezing'): specific_symptoms.append("Wheezing")
        if symptoms.get('has_sore_throat'): specific_symptoms.append("Sore throat")
        if symptoms.get('has_nasal_congestion'): specific_symptoms.append("Nasal congestion")
        if symptoms.get('has_runny_nose'): specific_symptoms.append("Runny nose")
        if symptoms.get('has_sneezing'): specific_symptoms.append("Sneezing")
        if symptoms.get('has_hoarseness'): specific_symptoms.append("Hoarseness")
        
        # Head/Neuro symptoms
        if symptoms.get('has_headache'): specific_symptoms.append("Headache")
        if symptoms.get('has_dizziness'): specific_symptoms.append("Dizziness")
        if symptoms.get('has_vision_changes'): specific_symptoms.append("Vision changes")
        if symptoms.get('has_photophobia'): specific_symptoms.append("Photophobia")
        
        # GI symptoms
        if symptoms.get('has_nausea'): specific_symptoms.append("Nausea")
        if symptoms.get('has_vomiting'): specific_symptoms.append("Vomiting")
        if symptoms.get('has_diarrhea'): specific_symptoms.append("Diarrhea")
        if symptoms.get('has_abdominal_pain'): specific_symptoms.append("Abdominal pain")
        if symptoms.get('has_loss_of_appetite'): specific_symptoms.append("Loss of appetite")
        
        # Other symptoms
        if symptoms.get('has_muscle_pain'): specific_symptoms.append("Muscle pain")
        if symptoms.get('has_joint_pain'): specific_symptoms.append("Joint pain")
        if symptoms.get('has_skin_rash'): specific_symptoms.append("Skin rash")
        if symptoms.get('has_itching'): specific_symptoms.append("Itching")
        if symptoms.get('has_swelling'): specific_symptoms.append("Swelling")
        if symptoms.get('has_swollen_lymph_nodes'): specific_symptoms.append("Swollen lymph nodes")
        
        # Special COVID/Flu symptoms
        if symptoms.get('has_loss_of_taste'): specific_symptoms.append("Loss of taste")
        if symptoms.get('has_loss_of_smell'): specific_symptoms.append("Loss of smell")
        
        # Create enhanced description with specific symptoms
        enhanced_description = description
        if specific_symptoms:
            enhanced_description += f" | Specific symptoms: {', '.join(specific_symptoms)}"

        prompt = SYMPTOM_ANALYSIS_PROMPT.format(
            description=enhanced_description,
            temperature=temperature,
            duration_hours=duration_hours,
            severity=severity,
        )

        try:
            # HYBRID ML + RULES SYSTEM
            temp = float(temperature) if temperature != 'Not measured' else 0
            duration = float(duration_hours) if duration_hours != 'Unknown' else 999
            
            # Initialize default values
            final_diagnosis = "Viral Syndrome"
            final_confidence = 70
            final_reasoning = "General viral symptoms - requires medical evaluation"
            final_symptoms = ["Fever", "General symptoms"]
            
            # Calculate symptom complexity score to decide ML vs Rules
            symptom_complexity_score = self._calculate_symptom_complexity(symptoms, enhanced_description)
            use_ml_prediction = False
            ml_prediction = None
            ml_confidence = 0
            
            # Extract symptoms for rule matching - check ALL possible field names
            desc_lower = enhanced_description.lower()
            has_fever = symptoms.get('has_fever', False) or 'fever' in desc_lower
            has_headache = symptoms.get('has_headache', False) or 'headache' in desc_lower
            has_fatigue = symptoms.get('has_fatigue', False) or 'fatigue' in desc_lower or 'weakness' in desc_lower
            has_muscle_pain = symptoms.get('has_muscle_pain', False) or 'muscle pain' in desc_lower or 'body ache' in desc_lower or 'myalgia' in desc_lower
            has_sore_throat = symptoms.get('has_sore_throat', False) or 'sore throat' in desc_lower or 'throat pain' in desc_lower
            # Check ALL cough variants: has_cough, has_cough_dry, has_cough_productive
            # Only check text description if no explicit cough field is set
            has_cough_dry = symptoms.get('has_cough_dry', False)
            has_cough_productive = symptoms.get('has_cough_productive', False)
            has_cough_explicit = symptoms.get('has_cough', False) or has_cough_dry or has_cough_productive
            has_cough_text = 'cough' in desc_lower and not ('no cough' in desc_lower or 'without cough' in desc_lower or 'with coughing' in desc_lower)
            has_cough = has_cough_explicit or has_cough_text
            has_chest_pain = symptoms.get('has_chest_pain', False) or 'chest pain' in desc_lower
            has_shortness_of_breath = symptoms.get('has_shortness_of_breath', False) or 'shortness of breath' in desc_lower or 'difficulty breathing' in desc_lower or 'breathing difficulty' in desc_lower
            has_loss_taste = symptoms.get('has_loss_of_taste', False) or symptoms.get('has_loss_taste', False) or 'loss of taste' in desc_lower
            has_loss_smell = symptoms.get('has_loss_of_smell', False) or 'loss of smell' in desc_lower
            has_vomiting = symptoms.get('has_vomiting', False) or 'vomit' in desc_lower
            has_diarrhea = symptoms.get('has_diarrhea', False) or 'diarrhea' in desc_lower
            has_nausea = symptoms.get('has_nausea', False) or 'nausea' in desc_lower
            has_abdominal_pain = symptoms.get('has_abdominal_pain', False) or 'abdominal' in desc_lower or 'stomach' in desc_lower
            has_chills = symptoms.get('has_chills', False) or 'chills' in desc_lower
            has_wheezing = symptoms.get('has_wheezing', False) or 'wheez' in desc_lower
            has_chest_tightness = symptoms.get('has_chest_tightness', False) or 'chest tight' in desc_lower
            
            # Additional symptoms from form
            has_sneezing = symptoms.get('has_sneezing', False) or 'sneezing' in desc_lower
            has_runny_nose = symptoms.get('has_runny_nose', False) or 'runny' in desc_lower or 'runny nose' in desc_lower
            has_nasal_congestion = symptoms.get('has_nasal_congestion', False) or 'nasal congestion' in desc_lower or 'congestion' in desc_lower
            has_excessive_thirst = symptoms.get('has_excessive_thirst', False) or 'thirst' in desc_lower or 'excessive thirst' in desc_lower
            has_frequent_urination = symptoms.get('has_frequent_urination', False) or 'frequent urination' in desc_lower or 'urinate frequently' in desc_lower or 'need to urinate' in desc_lower
            has_hoarseness = symptoms.get('has_hoarseness', False) or 'hoarse' in desc_lower
            has_cyanosis = symptoms.get('has_cyanosis', False) or 'cyanosis' in desc_lower or 'blue' in desc_lower
            has_leg_swelling = symptoms.get('has_leg_swelling', False) or 'leg swelling' in desc_lower or 'edema' in desc_lower
            has_syncope = symptoms.get('has_syncope', False) or 'faint' in desc_lower or 'syncope' in desc_lower
            has_hypertension_signs = symptoms.get('has_hypertension_signs', False) or 'hypertension' in desc_lower
            has_constipation = symptoms.get('has_constipation', False) or 'constipation' in desc_lower
            has_bloating = symptoms.get('has_bloating', False) or 'bloating' in desc_lower
            has_heartburn = symptoms.get('has_heartburn', False) or 'heartburn' in desc_lower
            has_dysphagia = symptoms.get('has_dysphagia', False) or 'dysphagia' in desc_lower or 'swallowing' in desc_lower
            has_gi_bleeding = symptoms.get('has_gi_bleeding', False) or 'bleeding' in desc_lower
            has_tremors = symptoms.get('has_tremors', False) or 'tremor' in desc_lower
            has_numbness = symptoms.get('has_numbness', False) or 'numbness' in desc_lower
            has_limb_weakness = symptoms.get('has_limb_weakness', False) or 'limb weakness' in desc_lower or 'arm weakness' in desc_lower or 'leg weakness' in desc_lower
            has_coordination_loss = symptoms.get('has_coordination_loss', False) or 'coordination' in desc_lower
            has_memory_loss = symptoms.get('has_memory_loss', False) or 'memory' in desc_lower
            has_seizures = symptoms.get('has_seizures', False) or 'seizure' in desc_lower
            has_sleep_disturbances = symptoms.get('has_sleep_disturbances', False) or 'sleep' in desc_lower
            has_anxiety = symptoms.get('has_anxiety', False) or 'anxiety' in desc_lower
            has_depression = symptoms.get('has_depression', False) or 'depression' in desc_lower
            has_vision_changes = symptoms.get('has_vision_changes', False) or 'vision' in desc_lower
            has_hearing_changes = symptoms.get('has_hearing_changes', False) or 'hearing' in desc_lower
            has_photophobia = symptoms.get('has_photophobia', False) or 'photophobia' in desc_lower
            has_eye_pain = symptoms.get('has_eye_pain', False) or 'eye pain' in desc_lower
            has_muscle_weakness = symptoms.get('has_muscle_weakness', False) or 'muscle weakness' in desc_lower
            has_joint_swelling = symptoms.get('has_joint_swelling', False) or 'joint swelling' in desc_lower
            has_back_pain = symptoms.get('has_back_pain', False) or 'back pain' in desc_lower
            has_bone_pain = symptoms.get('has_bone_pain', False) or 'bone pain' in desc_lower
            has_bruising = symptoms.get('has_bruising', False) or 'bruising' in desc_lower
            has_skin_color_changes = symptoms.get('has_skin_color_changes', False) or 'skin color' in desc_lower
            has_hair_loss = symptoms.get('has_hair_loss', False) or 'hair loss' in desc_lower
            has_nail_changes = symptoms.get('has_nail_changes', False) or 'nail' in desc_lower
            has_frequent_urination = symptoms.get('has_frequent_urination', False) or 'frequent urination' in desc_lower
            has_painful_urination = symptoms.get('has_painful_urination', False) or 'painful urination' in desc_lower
            has_blood_in_urine = symptoms.get('has_blood_in_urine', False) or 'blood in urine' in desc_lower
            has_urinary_retention = symptoms.get('has_urinary_retention', False) or 'urinary retention' in desc_lower
            has_genital_discharge = symptoms.get('has_genital_discharge', False) or 'discharge' in desc_lower
            has_pelvic_pain = symptoms.get('has_pelvic_pain', False) or 'pelvic pain' in desc_lower
            has_menstrual_irregularities = symptoms.get('has_menstrual_irregularities', False) or 'menstrual' in desc_lower
            has_excessive_thirst = symptoms.get('has_excessive_thirst', False) or 'thirst' in desc_lower
            has_temperature_intolerance = symptoms.get('has_temperature_intolerance', False) or 'temperature' in desc_lower
            has_unexplained_weight_changes = symptoms.get('has_unexplained_weight_changes', False) or 'weight change' in desc_lower
            has_hair_skin_changes = symptoms.get('has_hair_skin_changes', False) or 'hair skin' in desc_lower
            
            # Missing symptom variables
            has_itching = symptoms.get('has_itching', False) or 'itch' in desc_lower or 'itching' in desc_lower
            has_skin_rash = symptoms.get('has_skin_rash', False) or 'rash' in desc_lower
            has_joint_pain = symptoms.get('has_joint_pain', False) or 'joint pain' in desc_lower
            has_muscle_pain = symptoms.get('has_muscle_pain', False) or 'muscle pain' in desc_lower
            has_generalized_pain = symptoms.get('has_generalized_pain', False) or 'pain' in desc_lower
            has_loss_of_appetite = symptoms.get('has_loss_of_appetite', False) or 'loss of appetite' in desc_lower
            has_night_sweats = symptoms.get('has_night_sweats', False) or 'night sweats' in desc_lower
            has_malaise = symptoms.get('has_malaise', False) or 'malaise' in desc_lower
            has_weight_loss = symptoms.get('has_weight_loss', False) or 'weight loss' in desc_lower
            has_weight_gain = symptoms.get('has_weight_gain', False) or 'weight gain' in desc_lower
            has_excessive_sweating = symptoms.get('has_excessive_sweating', False) or 'excessive sweating' in desc_lower
            has_fatigue = symptoms.get('has_fatigue', False) or 'fatigue' in desc_lower
            has_dizziness = symptoms.get('has_dizziness', False) or 'dizziness' in desc_lower
            has_palpitations = symptoms.get('has_palpitations', False) or 'palpitation' in desc_lower or 'palpitations' in desc_lower or 'irregular heartbeat' in desc_lower
            has_vision_changes = symptoms.get('has_vision_changes', False) or 'vision' in desc_lower or 'blurred vision' in desc_lower or 'vision problems' in desc_lower
            has_depression = symptoms.get('has_depression', False) or 'depression' in desc_lower or 'sadness' in desc_lower or 'hopelessness' in desc_lower
            has_anxiety = symptoms.get('has_anxiety', False) or 'anxiety' in desc_lower or 'worry' in desc_lower or 'restlessness' in desc_lower
            has_sleep_disturbances = symptoms.get('has_sleep_disturbances', False) or 'sleep' in desc_lower or 'insomnia' in desc_lower
            has_nosebleeds = symptoms.get('has_nosebleeds', False) or 'nosebleed' in desc_lower or 'nose bleed' in desc_lower
            has_ear_pain = symptoms.get('has_ear_pain', False) or 'ear pain' in desc_lower or 'earache' in desc_lower or 'otitis' in desc_lower
            has_heartburn = symptoms.get('has_heartburn', False) or 'heartburn' in desc_lower or 'acid reflux' in desc_lower or 'gerd' in desc_lower or 'burning chest' in desc_lower
            has_painful_urination = symptoms.get('has_painful_urination', False) or 'painful urination' in desc_lower or 'burning urination' in desc_lower or 'dysuria' in desc_lower
            has_excessive_thirst = symptoms.get('has_excessive_thirst', False) or 'excessive thirst' in desc_lower or 'very thirsty' in desc_lower or 'polydipsia' in desc_lower
            has_frequent_urination = symptoms.get('has_frequent_urination', False) or 'frequent urination' in desc_lower or 'urinating often' in desc_lower or 'polyuria' in desc_lower
            has_leg_swelling = symptoms.get('has_leg_swelling', False) or 'leg swelling' in desc_lower or 'swollen legs' in desc_lower or 'edema' in desc_lower
            
            has_confusion = symptoms.get('has_confusion', False) or 'confusion' in desc_lower
            
            print(f"🔍 SYMPTOM CHECK: fever={has_fever}, cough={has_cough}, chest_pain={has_chest_pain}, sob={has_shortness_of_breath}, headache={has_headache}, fatigue={has_fatigue}")
            print(f"🔍 RAW SYMPTOMS: {[k for k,v in symptoms.items() if v is True]}")
            
            # RULE 0: INFECTIOUS MONONUCLEOSIS - Must come before Strep (prolonged fatigue)
            if has_fever and has_sore_throat and ('fatigue' in desc_lower or 'exhaustion' in desc_lower or 'mononucleosis' in desc_lower or 'mono' in desc_lower or 'swollen glands' in desc_lower or 'spleen' in desc_lower) and duration > 72:
                final_diagnosis = "Infectious Mononucleosis"
                final_confidence = 91
                final_reasoning = "Fever + sore throat + fatigue + prolonged duration meets criteria for Infectious Mononucleosis"
                final_symptoms = ["Fever", "Sore throat", "Fatigue", "Prolonged"]
            
            # RULE 1: STREP THROAT - Must come before Pneumonia (no cough, exclude mono/tonsillitis)
            elif has_fever and has_sore_throat and not has_cough and not ('fatigue' in desc_lower and 'exhaustion' in desc_lower) and not ('tonsil' in desc_lower or 'white spots' in desc_lower or 'pus' in desc_lower or 'tonsillitis' in desc_lower) and not ('swollen glands' in desc_lower or 'spleen' in desc_lower) and duration <= 72 and ('strep' in desc_lower or 'pharyngitis' in desc_lower or ('sore throat' in desc_lower and 'sudden' in desc_lower)):
                final_diagnosis = "Strep Pharyngitis"
                final_confidence = 92
                final_reasoning = "Fever + sore throat without cough meets CDC criteria for Strep Pharyngitis"
                final_symptoms = ["Fever", "Sore throat", "No cough"]
            
            # RULE 2: COVID-19 - Must come before Pneumonia (distinctive symptoms)
            elif (has_loss_taste or has_loss_smell) and (has_fever or has_cough):
                final_diagnosis = "COVID-19"
                final_confidence = 96
                final_reasoning = "Loss of taste/smell with respiratory symptoms meets WHO criteria for COVID-19"
                final_symptoms = ["Loss of taste/smell"]
                if has_fever: final_symptoms.append("Fever")
                if has_cough: final_symptoms.append("Cough")
            
            # RULE 3: PNEUMONIA - Must have cough + chest pain/SOB
            elif has_fever and has_cough and (has_chest_pain or has_shortness_of_breath) and not ('body aches' in desc_lower and 'myalgia' in desc_lower):
                final_diagnosis = "Community-Acquired Pneumonia"
                final_confidence = 95
                final_reasoning = "Fever + cough + chest pain/SOB meets criteria for Pneumonia"
                final_symptoms = ["Fever", "Cough"]
                if has_chest_pain: final_symptoms.append("Chest pain")
                if has_shortness_of_breath: final_symptoms.append("Shortness of breath")
            
            # RULE 4: ACUTE BRONCHITIS - Cough without chest pain/SOB
            elif has_fever and has_cough and not has_chest_pain and not has_shortness_of_breath and duration > 72 and not ('nasal' in desc_lower or 'runny nose' in desc_lower or 'sneezing' in desc_lower) and ('bronchitis' in desc_lower or 'productive cough' in desc_lower or 'mucus' in desc_lower or 'phlegm' in desc_lower or 'chesty cough' in desc_lower) and not ('pneumonia' in desc_lower or 'lung infection' in desc_lower) and not ('body aches' in desc_lower and 'myalgia' in desc_lower):
                final_diagnosis = "Acute Bronchitis"
                final_confidence = 91
                final_reasoning = "Fever + prolonged cough without chest pain/SOB meets criteria for Acute Bronchitis"
                final_symptoms = ["Fever", "Cough", "Duration > 72h"]
            
            # RULE 5: COMMON COLD - Mild fever with nasal symptoms
            elif has_fever and temp < 38.5 and (has_nasal_congestion or 'runny nose' in desc_lower or 'sneezing' in desc_lower or 'nasal' in desc_lower) and not has_chest_pain and not has_shortness_of_breath:
                final_diagnosis = "Common Cold"
                final_confidence = 85
                final_reasoning = "Mild fever + nasal symptoms without respiratory distress meets criteria for Common Cold"
                final_symptoms = ["Mild fever", "Nasal symptoms", "No respiratory distress"]
            
            # RULE 6: ACUTE SINUSITIS - Fever with sinus symptoms
            elif has_fever and ('sinusitis' in desc_lower or ('sinus' in desc_lower and ('pain' in desc_lower or 'pressure' in desc_lower)) or 'facial pain' in desc_lower or 'facial pressure' in desc_lower or 'sinus pressure' in desc_lower) and (has_nasal_congestion or 'nasal' in desc_lower or 'discharge' in desc_lower or 'congestion' in desc_lower or 'postnasal' in desc_lower) and not ('runny nose' in desc_lower and 'sneezing' in desc_lower) and not ('sore throat' in desc_lower or 'throat' in desc_lower) and ('sinus' in desc_lower or 'facial' in desc_lower or 'pressure' in desc_lower):
                final_diagnosis = "Acute Sinusitis"
                final_confidence = 89
                final_reasoning = "Fever + sinus pain/pressure meets criteria for Acute Sinusitis"
                final_symptoms = ["Fever", "Sinus symptoms"]
            
            # RULE 16: MILD DEHYDRATION - Must come before Influenza (fluid loss)
            elif not has_fever and has_excessive_thirst and ('dehydration' in desc_lower or 'thirst' in desc_lower) and not has_frequent_urination:
                final_diagnosis = "Mild Dehydration"
                final_confidence = 82
                final_reasoning = "Excessive thirst without fever meets criteria for Mild Dehydration"
                final_symptoms = ["Thirst", "No fever", "Fluid loss"]
            
            # RULE 16: ESSENTIAL HYPERTENSION - Must come before Influenza (chronic)
            elif not has_fever and has_headache and ('nosebleed' in desc_lower or 'pounding' in desc_lower or 'irregular heartbeat' in desc_lower or 'blood in urine' in desc_lower or 'hypertension' in desc_lower or 'blood pressure' in desc_lower or 'high blood' in desc_lower or 'elevated' in desc_lower):
                final_diagnosis = "Essential Hypertension"
                final_confidence = 85
                final_reasoning = "Headache + hypertension symptoms meets criteria for Essential Hypertension"
                final_symptoms = ["Headache", "Hypertension", "No fever"]
            
            # RULE 17: TENSION-TYPE HEADACHE - Must come before Influenza (chronic)
            elif not has_fever and has_headache and ('tension' in desc_lower or 'pressure' in desc_lower or 'tightness' in desc_lower or 'bilateral' in desc_lower):
                final_diagnosis = "Tension-Type Headache"
                final_confidence = 87
                final_reasoning = "Tension headache pattern without fever meets criteria for Tension-Type Headache"
                final_symptoms = ["Tension headache", "No fever"]
            
            # RULE 18: ACUTE BRONCHITIS - Must come before Influenza (respiratory but no chest pain)
            elif has_fever and has_cough and not has_chest_pain and not has_shortness_of_breath and duration > 72:
                final_diagnosis = "Acute Bronchitis"
                final_confidence = 91
                final_reasoning = "Fever + cough without chest pain/shortness of breath meets criteria for Acute Bronchitis"
                final_symptoms = ["Fever", "Cough", "Duration > 72h"]
            
            # RULE 19: ACUTE SINUSITIS - Must come before Influenza (sinus symptoms)
            elif has_fever and (has_headache or 'facial pain' in desc_lower or 'sinus' in desc_lower) and (has_nasal_congestion or 'nasal' in desc_lower):
                final_diagnosis = "Acute Sinusitis"
                final_confidence = 89
                final_reasoning = "Fever + headache + nasal congestion meets criteria for Acute Sinusitis"
                final_symptoms = ["Fever", "Headache", "Nasal symptoms"]
            
            # RULE 21: ALLERGIC RHINITIS - Must come before Influenza (allergic, no fever)
            elif not has_fever and (has_nasal_congestion or 'runny nose' in desc_lower or 'sneezing' in desc_lower) and (has_itching or 'itch' in desc_lower or 'allergy' in desc_lower) and not has_sore_throat and not has_fatigue:
                final_diagnosis = "Allergic Rhinitis"
                final_confidence = 93
                final_reasoning = "Nasal symptoms + itching without fever meets criteria for Allergic Rhinitis"
                final_symptoms = ["Nasal symptoms", "Itching", "No fever"]
            
            # RULE 22: SEASONAL ALLERGIES - Must come before Influenza (allergic, no fever)
            elif not has_fever and (has_nasal_congestion or 'runny nose' in desc_lower or 'sneezing' in desc_lower) and has_itching and ('seasonal' in desc_lower or 'allergies' in desc_lower or 'pollen' in desc_lower) and not has_sore_throat and not has_fatigue:
                final_diagnosis = "Seasonal Allergies"
                final_confidence = 93
                final_reasoning = "Nasal symptoms + itching + seasonal trigger meets criteria for Seasonal Allergies"
                final_symptoms = ["Nasal symptoms", "Itching", "No fever", "Seasonal"]
            
            # RULE 23: COMMON COLD - Must come before Influenza (milder)
            elif has_fever and has_nasal_congestion and (has_sneezing or has_runny_nose or has_sore_throat or 'cold' in desc_lower or 'mild' in desc_lower or 'stuffy' in desc_lower or 'congestion' in desc_lower) and duration <= 168 and not has_chest_pain and not has_shortness_of_breath:
                final_diagnosis = "Common Cold"
                final_confidence = 85
                final_reasoning = "Mild fever + nasal symptoms without respiratory distress meets criteria for Common Cold"
                final_symptoms = ["Mild fever", "Nasal symptoms", "No respiratory distress"]
            
            # RULE 23: MIGRAINE WITH FEVER - Must come AFTER GI/other specific conditions
            elif has_fever and (has_headache or 'migraine' in desc_lower) and not has_cough and not has_vomiting and not has_diarrhea and not has_sore_throat and not ('stiff neck' in desc_lower or 'photophobia' in desc_lower) and not ('vesicle' in desc_lower or 'rash' in desc_lower):
                final_diagnosis = "Migraine with Fever"
                final_confidence = 88
                final_reasoning = "Headache with fever meets criteria for Migraine with Fever"
                final_symptoms = ["Fever", "Headache"]
            
            # RULE 66: ACUTE OTITIS MEDIA - Must come before Influenza
            elif has_fever and has_ear_pain and ('ear' in desc_lower or 'otitis' in desc_lower or 'middle ear' in desc_lower or 'eardrum' in desc_lower) and not has_chest_pain:
                final_diagnosis = "Acute Otitis Media"
                final_confidence = 89
                final_reasoning = "Fever + ear pain meets criteria for Acute Otitis Media"
                final_symptoms = ["Fever", "Ear pain", "No chest pain"]
            
            # RULE 67: INFECTIOUS MONONUCLEOSIS - Must come before Influenza
            elif has_fever and (has_sore_throat or 'throat' in desc_lower) and ('fatigue' in desc_lower or 'exhaustion' in desc_lower or 'mononucleosis' in desc_lower or 'mono' in desc_lower or 'glands' in desc_lower or 'swollen glands' in desc_lower or 'spleen' in desc_lower) and duration > 72:
                final_diagnosis = "Infectious Mononucleosis"
                final_confidence = 91
                final_reasoning = "Fever + fatigue + throat symptoms + prolonged duration meets criteria for Infectious Mononucleosis"
                final_symptoms = ["Fever", "Fatigue", "Throat symptoms", "Prolonged"]
            
            # RULE 68: ACUTE TONSILLITIS - Must come before Influenza
            elif has_fever and has_sore_throat and ('tonsil' in desc_lower or 'tonsillitis' in desc_lower or 'swollen tonsils' in desc_lower or 'white spots' in desc_lower or 'pus' in desc_lower) and not has_cough:
                final_diagnosis = "Acute Tonsillitis"
                final_confidence = 90
                final_reasoning = "Fever + sore throat + tonsil symptoms meets criteria for Acute Tonsillitis"
                final_symptoms = ["Fever", "Sore throat", "Tonsil symptoms"]
            
            # RULE 69: ACUTE FOOD POISONING - Must come before general GI
            elif has_fever and (has_vomiting or has_diarrhea) and ('food' in desc_lower or 'poisoning' in desc_lower or 'contaminated' in desc_lower or 'hours after eating' in desc_lower) and duration <= 48:
                final_diagnosis = "Acute Food Poisoning"
                final_confidence = 87
                final_reasoning = "Fever + GI symptoms + food exposure meets criteria for Acute Food Poisoning"
                final_symptoms = ["Fever", "GI symptoms", "Food exposure", "Acute"]
            
            # RULE 70: IRRITABLE BOWEL SYNDROME - Must come before Influenza
            elif not has_fever and has_abdominal_pain and ('ibs' in desc_lower or 'irritable bowel' in desc_lower or 'alternating' in desc_lower or 'constipation' in desc_lower or 'diarrhea' in desc_lower) and duration > 168 and not has_vomiting:
                final_diagnosis = "Irritable Bowel Syndrome"
                final_confidence = 84
                final_reasoning = "Chronic abdominal pain + IBS symptoms without fever meets criteria for Irritable Bowel Syndrome"
                final_symptoms = ["Abdominal pain", "IBS symptoms", "Chronic", "No fever"]
            
            # RULE 71: CONGESTIVE HEART FAILURE - Must come before Influenza
            elif not has_fever and has_shortness_of_breath and ('heart failure' in desc_lower or 'congestive' in desc_lower or 'fluid' in desc_lower or 'swelling' in desc_lower or 'edema' in desc_lower or 'legs' in desc_lower) and duration > 72:
                final_diagnosis = "Congestive Heart Failure"
                final_confidence = 86
                final_reasoning = "Shortness of breath + heart failure symptoms without fever meets criteria for Congestive Heart Failure"
                final_symptoms = ["Shortness of breath", "Heart failure symptoms", "No fever", "Chronic"]
            
            # RULE 72: AORTIC DISSECTION - Must come before Influenza
            elif has_chest_pain and ('tearing' in desc_lower or 'ripping' in desc_lower or 'aortic' in desc_lower or 'dissection' in desc_lower or 'back pain' in desc_lower) and not has_fever:
                final_diagnosis = "Aortic Dissection"
                final_confidence = 93
                final_reasoning = "Severe tearing chest/back pain meets criteria for Aortic Dissection"
                final_symptoms = ["Tearing chest pain", "Emergency"]
            
            # RULE 73: ACUTE STROKE - Must come before Influenza
            elif not has_fever and ('stroke' in desc_lower or 'brain attack' in desc_lower or 'numbness' in desc_lower or 'weakness' in desc_lower or 'slurred speech' in desc_lower or 'vision loss' in desc_lower or 'sudden' in desc_lower) and ('sudden' in desc_lower or 'numbness' in desc_lower or 'weakness' in desc_lower):
                final_diagnosis = "Acute Stroke"
                final_confidence = 92
                final_reasoning = "Sudden neurological symptoms without fever meets criteria for Acute Stroke"
                final_symptoms = ["Sudden neurological symptoms", "Emergency", "No fever"]
            
            # RULE 74: MENINGITIS - Must come before Influenza
            elif has_fever and (has_headache or 'stiff neck' in desc_lower or 'neck stiffness' in desc_lower or 'photophobia' in desc_lower or 'meningitis' in desc_lower) and ('stiff neck' in desc_lower or 'neck stiffness' in desc_lower or 'photophobia' in desc_lower):
                final_diagnosis = "Meningitis"
                final_confidence = 90
                final_reasoning = "Fever + headache + neck stiffness meets criteria for Meningitis"
                final_symptoms = ["Fever", "Headache", "Neck stiffness", "Emergency"]
            
                        
            # RULE 33: GASTROESOPHAGEAL REFLUX DISEASE - Must come before Influenza (digestive)
            elif not has_fever and (has_heartburn or 'heartburn' in desc_lower or 'reflux' in desc_lower or 'gerd' in desc_lower or ('burning' in desc_lower and ('chest' in desc_lower or 'esophagus' in desc_lower)) or ('acid' in desc_lower and ('regurgitation' in desc_lower or 'stomach' in desc_lower))):
                final_diagnosis = "Gastroesophageal Reflux Disease"
                final_confidence = 88
                final_reasoning = "Heartburn + reflux symptoms without fever meets criteria for GERD"
                final_symptoms = ["Heartburn", "Reflux", "No fever"]
            
            # RULE 34: PEPTIC ULCER DISEASE - Must come before Influenza (digestive)
            elif not has_fever and has_abdominal_pain and ('ulcer' in desc_lower or 'burning stomach' in desc_lower or 'dark stools' in desc_lower or 'blood in stool' in desc_lower or 'vomiting blood' in desc_lower) and duration > 48 and not ('heartburn' in desc_lower or 'acid reflux' in desc_lower or 'reflux' in desc_lower):
                final_diagnosis = "Peptic Ulcer Disease"
                final_confidence = 82
                final_reasoning = "Chronic abdominal pain + ulcer symptoms meets criteria for Peptic Ulcer Disease"
                final_symptoms = ["Abdominal pain", "Ulcer symptoms", "Chronic"]
            
            # RULE 35: NEPHROLITHIASIS - Must come before Type 2 Diabetes
            elif not has_fever and has_abdominal_pain and ('kidney' in desc_lower or 'stone' in desc_lower or 'flank' in desc_lower or 'radiating' in desc_lower) and not has_diarrhea and not has_vomiting:
                final_diagnosis = "Nephrolithiasis"
                final_confidence = 93
                final_reasoning = "Flank pain + stone symptoms without GI symptoms meets criteria for Nephrolithiasis"
                final_symptoms = ["Flank pain", "Stone symptoms", "No fever"]
            
            # RULE 36: TYPE 2 DIABETES MELLITUS - Must require thirst+urination combo or explicit mention
            elif not has_fever and ((has_excessive_thirst and has_frequent_urination) or 'diabetes' in desc_lower or 'glucose' in desc_lower or 'blood sugar' in desc_lower or 'hyperglycemia' in desc_lower):
                final_diagnosis = "Type 2 Diabetes Mellitus"
                final_confidence = 86
                final_reasoning = "Hyperglycemia symptoms without fever meets criteria for Type 2 Diabetes"
                final_symptoms = ["Hyperglycemia", "No fever"]
            
            # RULE 37: ESSENTIAL HYPERTENSION - Must come before Influenza (chronic)
            elif not has_fever and ('hypertension' in desc_lower or 'high blood' in desc_lower or 'elevated' in desc_lower or 'blood pressure' in desc_lower):
                final_diagnosis = "Essential Hypertension"
                final_confidence = 85
                final_reasoning = "Elevated blood pressure without fever meets criteria for Hypertension"
                final_symptoms = ["Elevated BP", "No fever"]
            
            # RULE 38: BRONCHIAL ASTHMA - Must come before Influenza (respiratory)
            elif not has_fever and (has_wheezing or 'wheez' in desc_lower or 'asthma' in desc_lower) and has_shortness_of_breath and not ('copd' in desc_lower or 'chronic' in desc_lower or 'emphysema' in desc_lower or 'progressive' in desc_lower or 'smoker' in desc_lower):
                final_diagnosis = "Bronchial Asthma"
                final_confidence = 90
                final_reasoning = "Wheezing + shortness of breath without fever meets criteria for Asthma"
                final_symptoms = ["Wheezing", "Shortness of breath", "No fever"]
            
            # RULE 39: CHRONIC OBSTRUCTIVE PULMONARY DISEASE - Must come before Influenza (respiratory)
            elif not has_fever and has_shortness_of_breath and ('copd' in desc_lower or 'chronic' in desc_lower or 'emphysema' in desc_lower or 'progressive' in desc_lower or 'smoker' in desc_lower) and not ('asthma' in desc_lower or 'inhaler' in desc_lower or 'albuterol' in desc_lower):
                final_diagnosis = "Chronic Obstructive Pulmonary Disease"
                final_confidence = 88
                final_reasoning = "Chronic progressive shortness of breath meets criteria for COPD"
                final_symptoms = ["Chronic SOB", "No fever", "Progressive"]
            
            # RULE 40: ANGINA PECTORIS - Must come before Influenza (cardiac)
            elif not has_fever and has_chest_pain and ('angina' in desc_lower or 'exertion' in desc_lower or 'relieved' in desc_lower):
                final_diagnosis = "Angina Pectoris"
                final_confidence = 89
                final_reasoning = "Chest pain pattern without fever meets criteria for Angina"
                final_symptoms = ["Chest pain pattern", "No fever"]
            
            # RULE 40: CARDIAC ARRHYTHMIA - Must come before MI (rhythm issue)
            elif not has_fever and ('palpitations' in desc_lower or 'irregular heartbeat' in desc_lower or 'arrhythmia' in desc_lower or 'flutter' in desc_lower or 'skipped beat' in desc_lower) and not has_chest_pain and not ('crushing' in desc_lower or 'pressure' in desc_lower or 'tightness' in desc_lower or 'heart attack' in desc_lower or 'left arm' in desc_lower or 'sweating' in desc_lower):
                final_diagnosis = "Cardiac Arrhythmia"
                final_confidence = 87
                final_reasoning = "Palpitations + irregular heartbeat without chest pain meets criteria for Cardiac Arrhythmia"
                final_symptoms = ["Palpitations", "Irregular heartbeat", "No chest pain"]
            
            # RULE 41: ACUTE MYOCARDIAL INFARCTION - Must come before Influenza (emergency)
            elif has_chest_pain and ('crushing' in desc_lower or 'heart attack' in desc_lower or 'left arm' in desc_lower or 'sweating' in desc_lower or 'emergency' in desc_lower):
                final_diagnosis = "Acute Myocardial Infarction"
                final_confidence = 94
                final_reasoning = "Severe chest pain pattern meets criteria for Myocardial Infarction"
                final_symptoms = ["Severe chest pain", "Emergency"]
            
            # RULE 42: CARDIAC ARRHYTHMIA - Must come before Influenza (cardiac)
            elif not has_fever and ('palpitation' in desc_lower or 'irregular' in desc_lower or 'arrhythmia' in desc_lower or 'palpitations' in desc_lower) and not ('crushing' in desc_lower or 'heart attack' in desc_lower or 'left arm' in desc_lower or 'sweating' in desc_lower):
                final_diagnosis = "Cardiac Arrhythmia"
                final_confidence = 84
                final_reasoning = "Palpitations without fever meets criteria for Arrhythmia"
                final_symptoms = ["Palpitations", "No fever"]
            
            # RULE 43: SEIZURE - Must come before Influenza (neurological)
            elif ('seizure' in desc_lower or 'convulsion' in desc_lower or 'uncontrollable' in desc_lower or 'jerking' in desc_lower) and ('loss' in desc_lower or 'consciousness' in desc_lower) and not ('anxiety' in desc_lower or 'worry' in desc_lower or 'restlessness' in desc_lower):
                final_diagnosis = "Epileptic Seizure"
                final_confidence = 91
                final_reasoning = "Seizure activity meets criteria for Epileptic Seizure"
                final_symptoms = ["Seizure activity"]
            
            # RULE 44: PARKINSON'S DISEASE - Must come before Influenza (neurological)
            elif not has_fever and ('tremor' in desc_lower or 'parkinson' in desc_lower or 'rigidity' in desc_lower) and duration > 168:
                final_diagnosis = "Parkinson's Disease"
                final_confidence = 85
                final_reasoning = "Tremor/rigidity without fever meets criteria for Parkinson's"
                final_symptoms = ["Tremor", "No fever", "Chronic"]
            
            # RULE 45: MULTIPLE SCLEROSIS - Must come before Influenza (neurological)
            elif not has_fever and ('multiple sclerosis' in desc_lower or 'ms ' in desc_lower or 'demyelination' in desc_lower) and duration > 168:
                final_diagnosis = "Multiple Sclerosis"
                final_confidence = 83
                final_reasoning = "Neurological symptoms without fever meets criteria for MS"
                final_symptoms = ["Neurological", "No fever", "Chronic"]
            
            # RULE 46: MIGRAINE WITHOUT FEVER - Must come before Influenza (neurological)
            elif not has_fever and (has_headache or 'migraine' in desc_lower) and ('aura' in desc_lower or 'photophobia' in desc_lower or 'phonophobia' in desc_lower):
                final_diagnosis = "Migraine without Aura"
                final_confidence = 89
                final_reasoning = "Migraine pattern without fever meets criteria for Migraine"
                final_symptoms = ["Headache", "No fever"]
            
            # RULE 47: MAJOR DEPRESSIVE DISORDER - Must come before Influenza (mental health)
            elif not has_fever and ('depression' in desc_lower or 'sad' in desc_lower or 'hopeless' in desc_lower or 'anhedonia' in desc_lower) and duration > 168:
                final_diagnosis = "Major Depressive Disorder"
                final_confidence = 84
                final_reasoning = "Depressive symptoms without fever meets criteria for Depression"
                final_symptoms = ["Mood symptoms", "No fever", "Chronic"]
            
            # RULE 48: GENERALIZED ANXIETY DISORDER - Must come before Influenza (mental health)
            elif not has_fever and (has_anxiety or 'worry' in desc_lower or 'restlessness' in desc_lower or 'excessive' in desc_lower) and not has_cough and not ('multiple sclerosis' in desc_lower or 'numbness' in desc_lower or 'vision' in desc_lower):
                final_diagnosis = "Generalized Anxiety Disorder"
                final_confidence = 83
                final_reasoning = "Anxiety symptoms without fever meets criteria for Generalized Anxiety Disorder"
                final_symptoms = ["Anxiety", "No fever"]
            
            # RULE 49: INSOMNIA - Must come before Influenza (mental health)
            elif not has_fever and ('insomnia' in desc_lower or 'sleep' in desc_lower or 'awake' in desc_lower):
                final_diagnosis = "Insomnia Disorder"
                final_confidence = 82
                final_reasoning = "Sleep disturbance without fever meets criteria for Insomnia"
                final_symptoms = ["Sleep disturbance", "No fever"]
            
            # RULE 50: HYPOTHYROIDISM - Must come before Influenza (endocrine)
            elif not has_fever and ('thyroid' in desc_lower or 'hypothyroid' in desc_lower or 'fatigue' in desc_lower or 'cold' in desc_lower) and duration > 168:
                final_diagnosis = "Hypothyroidism"
                final_confidence = 86
                final_reasoning = "Hypothyroid symptoms without fever meets criteria for Hypothyroidism"
                final_symptoms = ["Thyroid symptoms", "No fever", "Chronic"]
            
            # RULE 51: HYPERTHYROIDISM - Must come before Influenza (endocrine)
            elif not has_fever and ('hyperthyroid' in desc_lower or 'thyroid' in desc_lower or 'palpitation' in desc_lower or 'weight loss' in desc_lower):
                final_diagnosis = "Hyperthyroidism"
                final_confidence = 87
                final_reasoning = "Hyperthyroid symptoms without fever meets criteria for Hyperthyroidism"
                final_symptoms = ["Thyroid symptoms", "No fever"]
            
            # RULE 52: PSORIASIS - Must come before Atopic Dermatitis (silvery is distinctive)
            elif not has_fever and has_skin_rash and ('silvery' in desc_lower or 'plaques' in desc_lower or 'psoriasis' in desc_lower or ('pitted' in desc_lower and 'nails' in desc_lower)):
                final_diagnosis = "Psoriasis"
                final_confidence = 85
                final_reasoning = "Silvery scales/plaques without fever meets criteria for Psoriasis"
                final_symptoms = ["Scaly plaques", "No fever"]
            
            # RULE 53: ATOPIC DERMATITIS - Broader pattern, excludes silvery (Psoriasis)
            elif not has_fever and has_skin_rash and has_itching and ('dry skin' in desc_lower or 'patches' in desc_lower or 'cracked' in desc_lower or 'thickened' in desc_lower or 'raised bumps' in desc_lower or 'scratching' in desc_lower or 'atopic' in desc_lower or 'eczema' in desc_lower or 'flexural' in desc_lower or 'brownish' in desc_lower) and not ('silvery' in desc_lower):
                final_diagnosis = "Atopic Dermatitis"
                final_confidence = 88
                final_reasoning = "Itchy rash with dry/cracked skin meets criteria for Atopic Dermatitis"
                final_symptoms = ["Skin rash", "Itching", "No fever"]
            
            # RULE 54: CELLULITIS - Must come before Influenza (skin symptoms)
            elif has_fever and has_skin_rash and ('red' in desc_lower or 'warm' in desc_lower or 'tender' in desc_lower or 'cellulitis' in desc_lower or 'skin area' in desc_lower):
                final_diagnosis = "Cellulitis"
                final_confidence = 90
                final_reasoning = "Fever + red warm skin meets criteria for Cellulitis"
                final_symptoms = ["Fever", "Red warm skin"]
            
            # RULE 55: CONTACT DERMATITIS - Must come before Influenza (allergic)
            elif not has_fever and has_skin_rash and has_itching and ('contact' in desc_lower or 'allergic' in desc_lower or 'exposure' in desc_lower):
                final_diagnosis = "Contact Dermatitis"
                final_confidence = 89
                final_reasoning = "Itchy rash after exposure without fever meets criteria for Contact Dermatitis"
                final_symptoms = ["Itchy rash", "Exposure", "No fever"]
            
            # RULE 56: URTICARIA - Must come after Atopic Dermatitis (acute)
            elif not has_fever and has_skin_rash and ('hives' in desc_lower or 'wheals' in desc_lower or 'urticaria' in desc_lower):
                final_diagnosis = "Urticaria"
                final_confidence = 89
                final_reasoning = "Hives/wheals without fever meets criteria for Urticaria"
                final_symptoms = ["Hives", "Wheals", "No fever"]
            
            # RULE 57: ACNE - Must come before Influenza (chronic)
            elif not has_fever and ('acne' in desc_lower or 'pimple' in desc_lower or 'comedone' in desc_lower) and duration > 168:
                final_diagnosis = "Acne Vulgaris"
                final_confidence = 92
                final_reasoning = "Acne lesions without fever meets criteria for Acne"
                final_symptoms = ["Acne", "No fever", "Chronic"]
            
            # RULE 58: ROSACEA - Must come before Influenza (chronic)
            elif not has_fever and ('rosacea' in desc_lower or 'flushing' in desc_lower or 'facial' in desc_lower or 'redness' in desc_lower) and duration > 168:
                final_diagnosis = "Rosacea"
                final_confidence = 87
                final_reasoning = "Facial redness without fever meets criteria for Rosacea"
                final_symptoms = ["Facial redness", "No fever", "Chronic"]
            
            # RULE 59: FOLLICULITIS - Must come before Influenza (bacterial)
            elif has_fever and ('folliculitis' in desc_lower or 'hair' in desc_lower or 'follicle' in desc_lower) and (has_skin_rash or 'pustule' in desc_lower):
                final_diagnosis = "Folliculitis"
                final_confidence = 88
                final_reasoning = "Fever + hair follicle inflammation meets criteria for Folliculitis"
                final_symptoms = ["Fever", "Follicle inflammation"]
            
            # RULE 60: HERPES ZOSTER - Must come before Influenza (viral)
            elif has_fever and has_skin_rash and ('shingles' in desc_lower or 'zoster' in desc_lower or 'vesicle' in desc_lower or 'vesicular' in desc_lower or 'dermatome' in desc_lower):
                final_diagnosis = "Herpes Zoster"
                final_confidence = 93
                final_reasoning = "Fever + vesicular rash in dermatome meets criteria for Herpes Zoster"
                final_symptoms = ["Fever", "Vesicular rash"]
            
            # RULE 61: IMPETIGO - Must come before Influenza (bacterial)
            elif has_fever and ('impetigo' in desc_lower or 'honey' in desc_lower or 'crust' in desc_lower) and has_skin_rash:
                final_diagnosis = "Impetigo"
                final_confidence = 90
                final_reasoning = "Fever + honey-crusted lesions meets criteria for Impetigo"
                final_symptoms = ["Fever", "Honey-crusted rash"]
            
            # RULE 62: SCABIES - Must come before Influenza (parasitic)
            elif not has_fever and ('scabies' in desc_lower or 'mite' in desc_lower or 'burrow' in desc_lower) and has_itching and duration > 72:
                final_diagnosis = "Scabies"
                final_confidence = 94
                final_reasoning = "Intense itching without fever meets criteria for Scabies"
                final_symptoms = ["Intense itching", "No fever", "Chronic"]
            
            # RULE 63: RINGWORM - Must come before Influenza (fungal)
            elif not has_fever and ('ringworm' in desc_lower or 'tinea' in desc_lower or 'ring' in desc_lower) and has_skin_rash:
                final_diagnosis = "Tinea Corporis"
                final_confidence = 91
                final_reasoning = "Ring-shaped rash without fever meets criteria for Ringworm"
                final_symptoms = ["Ring rash", "No fever"]
            
            # RULE 64: ATHLETE'S FOOT - Must come before Influenza (fungal)
            elif not has_fever and ('athlete' in desc_lower or 'foot' in desc_lower or 'tinea' in desc_lower) and ('foot' in desc_lower or 'toe' in desc_lower):
                final_diagnosis = "Tinea Pedis"
                final_confidence = 89
                final_reasoning = "Foot fungal infection without fever meets criteria for Athlete's Foot"
                final_symptoms = ["Foot rash", "No fever"]
            
            # RULE 65: VAGINAL CANDIDIASIS - Must come before Influenza (gynecological)
            elif not has_fever and ('vaginal' in desc_lower or 'yeast' in desc_lower or 'candida' in desc_lower or 'discharge' in desc_lower):
                final_diagnosis = "Vaginal Candidiasis"
                final_confidence = 92
                final_reasoning = "Vaginal symptoms without fever meets criteria for Candidiasis"
                final_symptoms = ["Vaginal symptoms", "No fever"]
            
                        
            # RULE 29: DEEP VEIN THROMBOSIS - Serious condition
            elif not has_fever and has_leg_swelling and ('deep' in desc_lower or 'dvt' in desc_lower or 'calf' in desc_lower or 'unilateral' in desc_lower):
                final_diagnosis = "Deep Vein Thrombosis"
                final_confidence = 91
                final_reasoning = "Unilateral leg swelling without fever meets criteria for Deep Vein Thrombosis"
                final_symptoms = ["Unilateral leg swelling", "No fever", "Serious"]
            
            # RULE 30: PULMONARY EMBOLISM - Emergency priority (high)
            elif not has_fever and has_shortness_of_breath and has_chest_pain and ('sudden' in desc_lower or 'pulmonary embolism' in desc_lower or 'embolism' in desc_lower or 'rapid heartbeat' in desc_lower or 'coughing blood' in desc_lower or 'coughing up blood' in desc_lower or 'bluish' in desc_lower or 'dyspnea' in desc_lower) and not has_wheezing:
                final_diagnosis = "Pulmonary Embolism"
                final_confidence = 95
                final_reasoning = "Sudden SOB + chest pain + PE signs meets criteria for Pulmonary Embolism"
                final_symptoms = ["Sudden SOB", "Chest pain", "No fever", "Emergency"]
            
            # RULE 31: SEPSIS - Emergency priority (high)
            elif has_fever and ('systemic' in desc_lower or 'infection' in desc_lower or 'organ failure' in desc_lower or 'shock' in desc_lower) and not has_chest_pain and not has_cough and not has_abdominal_pain:
                final_diagnosis = "Sepsis"
                final_confidence = 94
                final_reasoning = "Fever + systemic symptoms without chest/abdominal pain meets criteria for Sepsis"
                final_symptoms = ["Fever", "Systemic symptoms", "Emergency"]
            
            # RULE 32: INFLUENZA TYPE A - VERY STRICT - only if explicitly mentioned or perfect match
            elif has_fever and has_muscle_pain and (has_headache or has_fatigue) and duration <= 72 and ('influenza' in desc_lower or 'flu' in desc_lower or ('body aches' in desc_lower and 'myalgia' in desc_lower)) and not ('abdominal' in desc_lower or 'pancreatitis' in desc_lower or 'chest pain' in desc_lower or 'shortness of breath' in desc_lower or 'ear pain' in desc_lower or 'skin rash' in desc_lower or 'sore throat' in desc_lower or 'vomiting' in desc_lower or 'diarrhea' in desc_lower or 'urinary' in desc_lower or 'kidney' in desc_lower or 'appendix' in desc_lower or 'gerd' in desc_lower or 'reflux' in desc_lower or 'heartburn' in desc_lower):
                final_diagnosis = "Influenza Type A"
                final_confidence = 94
                final_reasoning = "Fever + acute onset + systemic symptoms meets CDC criteria for Influenza Type A"
                final_symptoms = ["Fever", "Acute onset", "Systemic symptoms"]
                if has_headache: final_symptoms.append("Headache")
                if has_fatigue: final_symptoms.append("Fatigue")
                if has_muscle_pain: final_symptoms.append("Muscle pain")
            
            # RULE 24: ACUTE APPENDICITIS - Must come before general GI
            elif has_fever and (has_abdominal_pain or 'abdominal pain' in desc_lower or 'abdominal' in desc_lower or 'stomach pain' in desc_lower) and ('right lower' in desc_lower or 'appendix' in desc_lower or 'appendicitis' in desc_lower or 'migrating pain' in desc_lower or 'rebound tenderness' in desc_lower or 'mcburney' in desc_lower or ('right' in desc_lower and 'quadrant' in desc_lower) or ('lower right' in desc_lower)):
                final_diagnosis = "Acute Appendicitis"
                final_confidence = 91
                final_reasoning = "Fever + right lower abdominal pain meets criteria for Acute Appendicitis"
                final_symptoms = ["Fever", "Right lower abdominal pain"]
            
            # RULE 25: ACUTE CHOLECYSTITIS - Must come before general GI
            elif has_fever and ('right upper' in desc_lower or 'gall' in desc_lower or 'cholecystitis' in desc_lower):
                final_diagnosis = "Acute Cholecystitis"
                final_confidence = 87
                final_reasoning = "Fever + right upper abdominal pain meets criteria for Acute Cholecystitis"
                final_symptoms = ["Fever", "Right upper abdominal pain"]
            
            # RULE26: ACUTE PANCREATITIS - Must come before general GI
            elif has_fever and ('severe' in desc_lower or 'radiating' in desc_lower or 'pancreatitis' in desc_lower) and ('abdominal' in desc_lower or 'pain' in desc_lower):
                final_diagnosis = "Acute Pancreatitis"
                final_confidence = 89
                final_reasoning = "Fever + severe radiating abdominal pain meets criteria for Acute Pancreatitis"
                final_symptoms = ["Fever", "Severe abdominal pain"]
            
            # RULE 27: ACUTE GASTROENTERITIS - Must come before general infections
            elif has_fever and (has_vomiting or has_diarrhea) and ('gastro' in desc_lower or 'stomach flu' in desc_lower or (has_vomiting and has_diarrhea)) and not ('headache' in desc_lower and 'photophobia' in desc_lower):
                final_diagnosis = "Acute Gastroenteritis"
                final_confidence = 88
                final_reasoning = "Fever + GI symptoms meets criteria for Acute Gastroenteritis"
                final_symptoms = ["Fever"]
                if has_vomiting: final_symptoms.append("Vomiting")
                if has_diarrhea: final_symptoms.append("Diarrhea")
            
            # RULE 28: URINARY TRACT INFECTION - Must come before Sepsis (specific)
            elif has_fever and (has_painful_urination or 'urinary' in desc_lower or 'bladder' in desc_lower or 'uti' in desc_lower or 'burning urination' in desc_lower or 'frequent urination' in desc_lower):
                final_diagnosis = "Urinary Tract Infection"
                final_confidence = 87
                final_reasoning = "Fever + urinary symptoms meets criteria for Urinary Tract Infection"
                final_symptoms = ["Fever", "Urinary symptoms"]
            
            # RULE 33: GASTROESOPHAGEAL REFLUX DISEASE - Must come before Influenza (digestive)
            elif not has_fever and has_heartburn and ('reflux' in desc_lower or 'gerd' in desc_lower or 'acid' in desc_lower or 'burning' in desc_lower):
                final_diagnosis = "Gastroesophageal Reflux Disease"
                final_confidence = 88
                final_reasoning = "Heartburn + reflux symptoms without fever meets criteria for GERD"
                final_symptoms = ["Heartburn", "Reflux", "No fever"]
            
            # RULE 34: PEPTIC ULCER DISEASE - Must come before Influenza (digestive)
            elif not has_fever and has_abdominal_pain and ('ulcer' in desc_lower or 'burning stomach' in desc_lower or 'dark stools' in desc_lower or 'blood in stool' in desc_lower or 'vomiting blood' in desc_lower) and duration > 48 and not ('heartburn' in desc_lower or 'acid reflux' in desc_lower or 'reflux' in desc_lower):
                final_diagnosis = "Peptic Ulcer Disease"
                final_confidence = 82
                final_reasoning = "Chronic abdominal pain + ulcer symptoms meets criteria for Peptic Ulcer Disease"
                final_symptoms = ["Abdominal pain", "Ulcer symptoms", "Chronic"]
            
            # RULE 35: NEPHROLITHIASIS - Must come before Type 2 Diabetes
            elif not has_fever and has_abdominal_pain and ('kidney' in desc_lower or 'stone' in desc_lower or 'flank' in desc_lower or 'radiating' in desc_lower) and not has_diarrhea and not has_vomiting:
                final_diagnosis = "Nephrolithiasis"
                final_confidence = 93
                final_reasoning = "Flank pain + stone symptoms without GI symptoms meets criteria for Nephrolithiasis"
                final_symptoms = ["Flank pain", "Stone symptoms", "No fever"]
            
            # RULE 36: TYPE 2 DIABETES MELLITUS - Must require thirst+urination combo or explicit mention
            elif not has_fever and ((has_excessive_thirst and has_frequent_urination) or 'diabetes' in desc_lower or 'glucose' in desc_lower or 'blood sugar' in desc_lower or 'hyperglycemia' in desc_lower):
                final_diagnosis = "Type 2 Diabetes Mellitus"
                final_confidence = 86
                final_reasoning = "Hyperglycemia symptoms without fever meets criteria for Type 2 Diabetes"
                final_symptoms = ["Hyperglycemia", "No fever"]
            
            # RULE 37: ESSENTIAL HYPERTENSION - Must come before Influenza (chronic)
            elif not has_fever and ('hypertension' in desc_lower or 'high blood' in desc_lower or 'elevated' in desc_lower or 'blood pressure' in desc_lower):
                final_diagnosis = "Essential Hypertension"
                final_confidence = 85
                final_reasoning = "Elevated blood pressure without fever meets criteria for Hypertension"
                final_symptoms = ["Elevated BP", "No fever"]
            
            # RULE 38: BRONCHIAL ASTHMA - Must come before Influenza (respiratory)
            elif not has_fever and (has_wheezing or 'wheez' in desc_lower or 'asthma' in desc_lower) and has_shortness_of_breath and not ('copd' in desc_lower or 'chronic' in desc_lower or 'emphysema' in desc_lower or 'progressive' in desc_lower or 'smoker' in desc_lower):
                final_diagnosis = "Bronchial Asthma"
                final_confidence = 90
                final_reasoning = "Wheezing + shortness of breath without fever meets criteria for Asthma"
                final_symptoms = ["Wheezing", "Shortness of breath", "No fever"]
            
            # RULE 39: CHRONIC OBSTRUCTIVE PULMONARY DISEASE - Must come before Influenza (respiratory)
            elif not has_fever and has_shortness_of_breath and ('copd' in desc_lower or 'chronic' in desc_lower or 'emphysema' in desc_lower or 'progressive' in desc_lower or 'smoker' in desc_lower) and not ('asthma' in desc_lower or 'inhaler' in desc_lower or 'albuterol' in desc_lower):
                final_diagnosis = "Chronic Obstructive Pulmonary Disease"
                final_confidence = 88
                final_reasoning = "Chronic progressive shortness of breath meets criteria for COPD"
                final_symptoms = ["Chronic SOB", "No fever", "Progressive"]
            
            # RULE 40: ANGINA PECTORIS - Must come before Influenza (cardiac)
            elif not has_fever and has_chest_pain and ('angina' in desc_lower or 'exertion' in desc_lower or 'relieved' in desc_lower):
                final_diagnosis = "Angina Pectoris"
                final_confidence = 89
                final_reasoning = "Chest pain pattern without fever meets criteria for Angina"
                final_symptoms = ["Chest pain pattern", "No fever"]
            
            # RULE 40: CARDIAC ARRHYTHMIA - Must come before MI (rhythm issue)
            elif not has_fever and ('palpitations' in desc_lower or 'irregular heartbeat' in desc_lower or 'arrhythmia' in desc_lower or 'flutter' in desc_lower or 'skipped beat' in desc_lower) and not has_chest_pain and not ('crushing' in desc_lower or 'pressure' in desc_lower or 'tightness' in desc_lower or 'heart attack' in desc_lower or 'left arm' in desc_lower or 'sweating' in desc_lower):
                final_diagnosis = "Cardiac Arrhythmia"
                final_confidence = 87
                final_reasoning = "Palpitations + irregular heartbeat without chest pain meets criteria for Cardiac Arrhythmia"
                final_symptoms = ["Palpitations", "Irregular heartbeat", "No chest pain"]
            
            # RULE 41: ACUTE MYOCARDIAL INFARCTION - Must come before Influenza (emergency)
            elif has_chest_pain and ('crushing' in desc_lower or 'heart attack' in desc_lower or 'left arm' in desc_lower or 'sweating' in desc_lower or 'emergency' in desc_lower):
                final_diagnosis = "Acute Myocardial Infarction"
                final_confidence = 94
                final_reasoning = "Severe chest pain pattern meets criteria for Myocardial Infarction"
                final_symptoms = ["Severe chest pain", "Emergency"]
            
            # RULE 42: CARDIAC ARRHYTHMIA - Must come before Influenza (cardiac)
            elif not has_fever and ('palpitation' in desc_lower or 'irregular' in desc_lower or 'arrhythmia' in desc_lower or 'palpitations' in desc_lower) and not ('crushing' in desc_lower or 'heart attack' in desc_lower or 'left arm' in desc_lower or 'sweating' in desc_lower):
                final_diagnosis = "Cardiac Arrhythmia"
                final_confidence = 84
                final_reasoning = "Palpitations without fever meets criteria for Arrhythmia"
                final_symptoms = ["Palpitations", "No fever"]
            
            # RULE 43: SEIZURE - Must come before Influenza (neurological)
            elif ('seizure' in desc_lower or 'convulsion' in desc_lower or 'uncontrollable' in desc_lower or 'jerking' in desc_lower) and ('loss' in desc_lower or 'consciousness' in desc_lower) and not ('anxiety' in desc_lower or 'worry' in desc_lower or 'restlessness' in desc_lower):
                final_diagnosis = "Epileptic Seizure"
                final_confidence = 91
                final_reasoning = "Seizure activity meets criteria for Epileptic Seizure"
                final_symptoms = ["Seizure activity"]
            
            # RULE 44: PARKINSON'S DISEASE - Must come before Influenza (neurological)
            elif not has_fever and ('tremor' in desc_lower or 'parkinson' in desc_lower or 'rigidity' in desc_lower) and duration > 168:
                final_diagnosis = "Parkinson's Disease"
                final_confidence = 85
                final_reasoning = "Tremor/rigidity without fever meets criteria for Parkinson's"
                final_symptoms = ["Tremor", "No fever", "Chronic"]
            
            # RULE 45: MULTIPLE SCLEROSIS - Must come before Influenza (neurological)
            elif not has_fever and ('multiple sclerosis' in desc_lower or 'ms ' in desc_lower or 'demyelination' in desc_lower) and duration > 168:
                final_diagnosis = "Multiple Sclerosis"
                final_confidence = 83
                final_reasoning = "Neurological symptoms without fever meets criteria for MS"
                final_symptoms = ["Neurological", "No fever", "Chronic"]
            
            # RULE 46: MIGRAINE WITHOUT FEVER - Must come before Influenza (neurological)
            elif not has_fever and (has_headache or 'migraine' in desc_lower) and ('aura' in desc_lower or 'photophobia' in desc_lower or 'phonophobia' in desc_lower):
                final_diagnosis = "Migraine without Aura"
                final_confidence = 89
                final_reasoning = "Migraine pattern without fever meets criteria for Migraine"
                final_symptoms = ["Headache", "No fever"]
            
            # RULE 47: MAJOR DEPRESSIVE DISORDER - Must come before Influenza (mental health)
            elif not has_fever and ('depression' in desc_lower or 'sad' in desc_lower or 'hopeless' in desc_lower or 'anhedonia' in desc_lower) and duration > 168:
                final_diagnosis = "Major Depressive Disorder"
                final_confidence = 84
                final_reasoning = "Depressive symptoms without fever meets criteria for Depression"
                final_symptoms = ["Mood symptoms", "No fever", "Chronic"]
            
            # RULE 48: GENERALIZED ANXIETY DISORDER - Must come before Influenza (mental health)
            elif not has_fever and (has_anxiety or 'worry' in desc_lower or 'restlessness' in desc_lower or 'excessive' in desc_lower) and not has_cough and not ('multiple sclerosis' in desc_lower or 'numbness' in desc_lower or 'vision' in desc_lower):
                final_diagnosis = "Generalized Anxiety Disorder"
                final_confidence = 83
                final_reasoning = "Anxiety symptoms without fever meets criteria for Generalized Anxiety Disorder"
                final_symptoms = ["Anxiety", "No fever"]
            
            # RULE 49: INSOMNIA - Must come before Influenza (mental health)
            elif not has_fever and ('insomnia' in desc_lower or 'sleep' in desc_lower or 'awake' in desc_lower):
                final_diagnosis = "Insomnia Disorder"
                final_confidence = 82
                final_reasoning = "Sleep disturbance without fever meets criteria for Insomnia"
                final_symptoms = ["Sleep disturbance", "No fever"]
            
            # RULE 50: HYPOTHYROIDISM - Must come before Influenza (endocrine)
            elif not has_fever and ('thyroid' in desc_lower or 'hypothyroid' in desc_lower or 'fatigue' in desc_lower or 'cold' in desc_lower) and duration > 168:
                final_diagnosis = "Hypothyroidism"
                final_confidence = 86
                final_reasoning = "Hypothyroid symptoms without fever meets criteria for Hypothyroidism"
                final_symptoms = ["Thyroid symptoms", "No fever", "Chronic"]
            
            # RULE 51: HYPERTHYROIDISM - Must come before Influenza (endocrine)
            elif not has_fever and ('hyperthyroid' in desc_lower or 'thyroid' in desc_lower or 'palpitation' in desc_lower or 'weight loss' in desc_lower):
                final_diagnosis = "Hyperthyroidism"
                final_confidence = 87
                final_reasoning = "Hyperthyroid symptoms without fever meets criteria for Hyperthyroidism"
                final_symptoms = ["Thyroid symptoms", "No fever"]
            
            # RULE 52: PSORIASIS - Must come before Atopic Dermatitis (silvery is distinctive)
            elif not has_fever and has_skin_rash and ('silvery' in desc_lower or 'plaques' in desc_lower or 'psoriasis' in desc_lower or ('pitted' in desc_lower and 'nails' in desc_lower)):
                final_diagnosis = "Psoriasis"
                final_confidence = 85
                final_reasoning = "Silvery scales/plaques without fever meets criteria for Psoriasis"
                final_symptoms = ["Scaly plaques", "No fever"]
            
            # RULE 53: ATOPIC DERMATITIS - Broader pattern, excludes silvery (Psoriasis)
            elif not has_fever and has_skin_rash and has_itching and ('dry skin' in desc_lower or 'patches' in desc_lower or 'cracked' in desc_lower or 'thickened' in desc_lower or 'raised bumps' in desc_lower or 'scratching' in desc_lower or 'atopic' in desc_lower or 'eczema' in desc_lower or 'flexural' in desc_lower or 'brownish' in desc_lower) and not ('silvery' in desc_lower):
                final_diagnosis = "Atopic Dermatitis"
                final_confidence = 88
                final_reasoning = "Itchy rash with dry/cracked skin meets criteria for Atopic Dermatitis"
                final_symptoms = ["Skin rash", "Itching", "No fever"]
            
            # RULE 54: CELLULITIS - Must come before Influenza (skin symptoms)
            elif has_fever and has_skin_rash and ('red' in desc_lower or 'warm' in desc_lower or 'tender' in desc_lower or 'cellulitis' in desc_lower or 'skin area' in desc_lower):
                final_diagnosis = "Cellulitis"
                final_confidence = 90
                final_reasoning = "Fever + red warm skin meets criteria for Cellulitis"
                final_symptoms = ["Fever", "Red warm skin"]
            
            # RULE 55: CONTACT DERMATITIS - Must come before Influenza (allergic)
            elif not has_fever and has_skin_rash and has_itching and ('contact' in desc_lower or 'allergic' in desc_lower or 'exposure' in desc_lower):
                final_diagnosis = "Contact Dermatitis"
                final_confidence = 89
                final_reasoning = "Itchy rash after exposure without fever meets criteria for Contact Dermatitis"
                final_symptoms = ["Itchy rash", "Exposure", "No fever"]
            
            # RULE 56: URTICARIA - Must come after Atopic Dermatitis (acute)
            elif not has_fever and has_skin_rash and ('hives' in desc_lower or 'wheals' in desc_lower or 'urticaria' in desc_lower):
                final_diagnosis = "Urticaria"
                final_confidence = 89
                final_reasoning = "Hives/wheals without fever meets criteria for Urticaria"
                final_symptoms = ["Hives", "Wheals", "No fever"]
            
            # RULE 57: ACNE - Must come before Influenza (chronic)
            elif not has_fever and ('acne' in desc_lower or 'pimple' in desc_lower or 'comedone' in desc_lower) and duration > 168:
                final_diagnosis = "Acne Vulgaris"
                final_confidence = 92
                final_reasoning = "Acne lesions without fever meets criteria for Acne"
                final_symptoms = ["Acne", "No fever", "Chronic"]
            
            # RULE 58: ROSACEA - Must come before Influenza (chronic)
            elif not has_fever and ('rosacea' in desc_lower or 'flushing' in desc_lower or 'facial' in desc_lower or 'redness' in desc_lower) and duration > 168:
                final_diagnosis = "Rosacea"
                final_confidence = 87
                final_reasoning = "Facial redness without fever meets criteria for Rosacea"
                final_symptoms = ["Facial redness", "No fever", "Chronic"]
            
            # RULE 59: FOLLICULITIS - Must come before Influenza (bacterial)
            elif has_fever and ('folliculitis' in desc_lower or 'hair' in desc_lower or 'follicle' in desc_lower) and (has_skin_rash or 'pustule' in desc_lower):
                final_diagnosis = "Folliculitis"
                final_confidence = 88
                final_reasoning = "Fever + hair follicle inflammation meets criteria for Folliculitis"
                final_symptoms = ["Fever", "Follicle inflammation"]
            
            # RULE 60: HERPES ZOSTER - Must come before Influenza (viral)
            elif has_fever and has_skin_rash and ('shingles' in desc_lower or 'zoster' in desc_lower or 'vesicle' in desc_lower or 'vesicular' in desc_lower or 'dermatome' in desc_lower):
                final_diagnosis = "Herpes Zoster"
                final_confidence = 93
                final_reasoning = "Fever + vesicular rash in dermatome meets criteria for Herpes Zoster"
                final_symptoms = ["Fever", "Vesicular rash"]
            
            # RULE 61: IMPETIGO - Must come before Influenza (bacterial)
            elif has_fever and ('impetigo' in desc_lower or 'honey' in desc_lower or 'crust' in desc_lower) and has_skin_rash:
                final_diagnosis = "Impetigo"
                final_confidence = 90
                final_reasoning = "Fever + honey-crusted lesions meets criteria for Impetigo"
                final_symptoms = ["Fever", "Honey-crusted rash"]
            
            # RULE 62: SCABIES - Must come before Influenza (parasitic)
            elif not has_fever and ('scabies' in desc_lower or 'mite' in desc_lower or 'burrow' in desc_lower) and has_itching and duration > 72:
                final_diagnosis = "Scabies"
                final_confidence = 94
                final_reasoning = "Intense itching without fever meets criteria for Scabies"
                final_symptoms = ["Intense itching", "No fever", "Chronic"]
            
            # RULE 63: RINGWORM - Must come before Influenza (fungal)
            elif not has_fever and ('ringworm' in desc_lower or 'tinea' in desc_lower or 'ring' in desc_lower) and has_skin_rash:
                final_diagnosis = "Tinea Corporis"
                final_confidence = 91
                final_reasoning = "Ring-shaped rash without fever meets criteria for Ringworm"
                final_symptoms = ["Ring rash", "No fever"]
            
            # RULE 64: ATHLETE'S FOOT - Must come before Influenza (fungal)
            elif not has_fever and ('athlete' in desc_lower or 'foot' in desc_lower or 'tinea' in desc_lower) and ('foot' in desc_lower or 'toe' in desc_lower):
                final_diagnosis = "Tinea Pedis"
                final_confidence = 89
                final_reasoning = "Foot fungal infection without fever meets criteria for Athlete's Foot"
                final_symptoms = ["Foot rash", "No fever"]
            
            # RULE 65: VAGINAL CANDIDIASIS - Must come before Influenza (gynecological)
            elif not has_fever and ('vaginal' in desc_lower or 'yeast' in desc_lower or 'candida' in desc_lower or 'discharge' in desc_lower):
                final_diagnosis = "Vaginal Candidiasis"
                final_confidence = 92
                final_reasoning = "Vaginal symptoms without fever meets criteria for Candidiasis"
                final_symptoms = ["Vaginal symptoms", "No fever"]
            
            # Create deterministic analysis
            analysis = {
                "primary_prediction": {
                    "condition": final_diagnosis,
                    "confidence": final_confidence,
                    "matching_symptoms": final_symptoms,
                    "reasoning": final_reasoning
                },
                "differential_diagnosis": [
                    {
                        "condition": "Influenza Type B",
                        "confidence": 60,
                        "reasoning": "Alternative viral respiratory infection"
                    }
                ],
                "emergency_assessment": {
                    "level": "Urgent" if final_diagnosis == "Community-Acquired Pneumonia" else "Non-urgent",
                    "go_to_hospital": final_diagnosis == "Community-Acquired Pneumonia",
                    "message": f"Seek medical attention for {final_diagnosis}",
                    "warning_signs": ["High fever", "Difficulty breathing", "Severe pain"]
                },
                "treatment_recommendations": {
                    "medications": ["Symptomatic treatment"],
                    "self_care": ["Rest", "Hydration", "Monitor symptoms"],
                    "when_to_see_doctor": "If symptoms worsen or persist"
                },
                "risk_factors": {
                    "complications": ["Secondary bacterial infection"],
                    "monitoring": ["Temperature", "Symptom progression"]
                }
            }
            
            # HYBRID DECISION: Use ML for complex cases, Rules for clear cases
            # Complexity threshold: 40+ = complex (use ML), <40 = simple (use rules)
            COMPLEXITY_THRESHOLD = 40
            
            if symptom_complexity_score >= COMPLEXITY_THRESHOLD and self.ml_available:
                # Complex case - try ML prediction
                try:
                    print(f"🧠 COMPLEX CASE (score: {symptom_complexity_score}) - Using ML prediction")
                    ml_result = self.ml_engine.predict(symptoms)
                    
                    if ml_result and ml_result.get('success'):
                        ml_prediction = ml_result['prediction']['disease']
                        ml_confidence = ml_result['prediction']['confidence']
                        
                        # Use ML if confidence is high enough (>70%)
                        if ml_confidence > 70:
                            print(f"✅ ML PREDICTION: {ml_prediction} ({ml_confidence}% confidence)")
                            final_diagnosis = ml_prediction
                            final_confidence = ml_confidence
                            final_reasoning = f"ML-based diagnosis (complexity score: {symptom_complexity_score})"
                            use_ml_prediction = True
                            analysis["ai_model"] = "hybrid-ml-primary"
                        else:
                            # ML confidence too low, stick with rules
                            print(f"⚠️ ML confidence too low ({ml_confidence}%), using rule-based diagnosis")
                            analysis["ai_model"] = "hybrid-rules-fallback"
                    else:
                        print(f"⚠️ ML prediction failed, using rule-based diagnosis")
                        analysis["ai_model"] = "hybrid-rules-fallback"
                        
                except Exception as ml_error:
                    print(f"❌ ML prediction error: {ml_error}, using rule-based diagnosis")
                    analysis["ai_model"] = "hybrid-rules-fallback"
            else:
                # Simple case - use deterministic rules
                print(f"📋 SIMPLE CASE (score: {symptom_complexity_score}) - Using deterministic rules")
                analysis["ai_model"] = "hybrid-rules-primary"
            
            # Update analysis with final diagnosis
            analysis["primary_prediction"]["condition"] = final_diagnosis
            analysis["primary_prediction"]["confidence"] = final_confidence
            analysis["primary_prediction"]["reasoning"] = final_reasoning
            analysis["primary_prediction"]["matching_symptoms"] = final_symptoms
            
            # Add complexity metadata
            analysis["complexity_analysis"] = {
                "score": symptom_complexity_score,
                "classification": "complex" if symptom_complexity_score >= COMPLEXITY_THRESHOLD else "simple",
                "prediction_method": "ML" if use_ml_prediction else "Rules",
                "ml_available": self.ml_available
            }
            
            analysis["educational_disclaimer"] = (
                "This is for educational purposes only. Always consult a healthcare professional."
            )
            
            print(f"🎯 HYBRID DIAGNOSIS: {final_diagnosis} ({final_confidence}% confidence) via {analysis['ai_model']}")
            return analysis
            
        except Exception as e:
            print(f"❌ Symptom analysis error: {e}")
            return {
                "primary_prediction": {
                    "condition": "Requires Medical Evaluation",
                    "confidence": 50,
                    "matching_symptoms": [],
                    "reasoning": f"Analysis encountered an error: {e}"
                },
                "differential_diagnosis": [],
                "emergency_assessment": {
                    "level": "Non-urgent",
                    "go_to_hospital": False,
                    "message": "Please consult a healthcare provider for proper diagnosis",
                    "warning_signs": []
                },
                "treatment_recommendations": {
                    "medications": [],
                    "self_care": ["Rest", "Stay hydrated"],
                    "when_to_see_doctor": "If symptoms worsen or persist beyond 48 hours"
                },
                "risk_factors": {
                    "complications": [],
                    "monitoring": []
                },
                "ai_model": "error-fallback",
                "educational_disclaimer": "This is for educational purposes only. Always consult a healthcare professional."
            }

    # ------------------------------------------------------------------ #
    #  2. MEDICINE RECOMMENDATIONS
    # ------------------------------------------------------------------ #
    async def generate_medicine_recommendations(
        self,
        symptoms: Dict[str, Any],
        patient_profile: Dict[str, Any],
        primary_diagnosis: str
    ) -> List[MedicineRecommendation]:
        """Generate AI-powered medicine recommendations."""
        prompt = MEDICINE_PROMPT.format(
            diagnosis=primary_diagnosis,
            description=symptoms.get('description', ''),
            temperature=symptoms.get('temperature', 'N/A'),
            severity=symptoms.get('severity', 'N/A'),
            patient_profile=json.dumps(patient_profile),
        )

        try:
            data = await self._call_gemini(prompt)
            medicines = []
            for med in data.get("medicines", []):
                medicines.append(MedicineRecommendation(
                    name=med.get("name", ""),
                    dosage=med.get("dosage", ""),
                    frequency=med.get("frequency", ""),
                    duration=med.get("duration", ""),
                    purpose=med.get("purpose", ""),
                    alternatives=med.get("alternatives", []),
                    precautions=med.get("precautions", []),
                    side_effects=med.get("side_effects", []),
                    effectiveness_score=med.get("effectiveness_score", 85)
                ))
            print(f"✅ Gemini medicine recs: {len(medicines)} medications")
            return medicines
        except Exception as e:
            print(f"❌ Medicine recommendation error: {e}")
            # Enhanced fallback with specific medications based on diagnosis
            fallback_medicines = self._get_fallback_medications(primary_diagnosis, symptoms)
            return fallback_medicines

    def _get_fallback_medications(self, diagnosis: str, symptoms: Dict[str, Any]) -> List[MedicineRecommendation]:
        """Get evidence-based fallback medications based on diagnosis."""
        temp = float(symptoms.get('temperature', 37))
        severity = int(symptoms.get('severity', 5))
        
        # Evidence-based medication recommendations
        medication_db = {
            "Community-Acquired Pneumonia": [
                MedicineRecommendation(
                    name="Amoxicillin",
                    dosage="500mg",
                    frequency="Three times daily",
                    duration="7-10 days",
                    purpose="Antibiotic treatment for bacterial pneumonia",
                    alternatives=["Doxycycline 100mg twice daily", "Azithromycin 500mg once daily"],
                    precautions=["Take with food to reduce stomach upset", "Complete full course"],
                    side_effects=["Nausea", "Diarrhea", "Allergic reaction"],
                    effectiveness_score=92
                ),
                MedicineRecommendation(
                    name="Acetaminophen (Tylenol)",
                    dosage="500-1000mg",
                    frequency="Every 6 hours as needed",
                    duration="As needed for fever/pain",
                    purpose="Fever reduction and pain relief",
                    alternatives=["Ibuprofen 400-600mg every 6-8 hours"],
                    precautions=["Do not exceed 4000mg in 24 hours", "Take with food"],
                    side_effects=["Liver toxicity (high doses)", "Stomach upset"],
                    effectiveness_score=88
                )
            ],
            "Influenza Type A": [
                MedicineRecommendation(
                    name="Oseltamivir (Tamiflu)",
                    dosage="75mg",
                    frequency="Twice daily",
                    duration="5 days",
                    purpose="Antiviral treatment for influenza",
                    alternatives=["Zanamivir 2 inhalations twice daily", "Baloxavir 40mg single dose"],
                    precautions=["Start within 48 hours of symptoms", "Take with food"],
                    side_effects=["Nausea", "Vomiting", "Headache"],
                    effectiveness_score=85
                ),
                MedicineRecommendation(
                    name="Acetaminophen (Tylenol)",
                    dosage="500-1000mg",
                    frequency="Every 6 hours as needed",
                    duration="As needed for fever/pain",
                    purpose="Symptomatic fever and pain relief",
                    alternatives=["Ibuprofen 400-600mg every 6-8 hours"],
                    precautions=["Do not exceed 4000mg in 24 hours"],
                    side_effects=["Liver toxicity (high doses)"],
                    effectiveness_score=90
                )
            ],
            "Strep Pharyngitis": [
                MedicineRecommendation(
                    name="Penicillin V",
                    dosage="500mg",
                    frequency="Three times daily",
                    duration="10 days",
                    purpose="Antibiotic treatment for streptococcal pharyngitis",
                    alternatives=["Amoxicillin 500mg three times daily", "Clindamycin 300mg three times daily"],
                    precautions=["Complete full 10-day course", "Take with water"],
                    side_effects=["Nausea", "Allergic reaction", "Diarrhea"],
                    effectiveness_score=95
                )
            ],
            "Acute Bronchitis": [
                MedicineRecommendation(
                    name="Dextromethorphan (Robitussin)",
                    dosage="10-20mg",
                    frequency="Every 4 hours as needed",
                    duration="As needed for cough",
                    purpose="Cough suppression",
                    alternatives=["Guaifenesin 200-400mg every 4 hours"],
                    precautions=["Do not use for persistent cough", "May cause drowsiness"],
                    side_effects=["Drowsiness", "Dizziness", "Nausea"],
                    effectiveness_score=75
                )
            ]
        }
        
        return medication_db.get(diagnosis, [
            MedicineRecommendation(
                name="Acetaminophen (Tylenol)",
                dosage="500-1000mg",
                frequency="Every 6 hours as needed",
                duration="As needed",
                purpose="General pain and fever relief",
                alternatives=["Ibuprofen 400-600mg every 6-8 hours"],
                precautions=["Do not exceed 4000mg daily", "Take with food"],
                side_effects=["Stomach upset", "Liver toxicity (high doses)"],
                effectiveness_score=85
            )
        ])

    # ------------------------------------------------------------------ #
    #  3. TREATMENT ANALYSIS
    # ------------------------------------------------------------------ #
    async def analyze_treatment_approach(
        self,
        diagnosis: str,
        symptoms: Dict[str, Any],
        patient_profile: Dict[str, Any]
    ) -> TreatmentAnalysis:
        """Analyze treatment approaches using Gemini AI."""
        prompt = TREATMENT_PROMPT.format(
            diagnosis=diagnosis,
            symptoms=json.dumps(symptoms),
            patient_profile=json.dumps(patient_profile),
        )

        try:
            data = await self._call_gemini(prompt)
            print(f"✅ Gemini treatment analysis complete")
            return TreatmentAnalysis(
                primary_treatment=data.get("primary_treatment", ""),
                alternative_treatments=data.get("alternative_treatments", []),
                treatment_duration=data.get("treatment_duration", ""),
                success_probability=float(data.get("success_probability", 0.0)),
                lifestyle_recommendations=data.get("lifestyle_recommendations", []),
                follow_up_care=data.get("follow_up_care", []),
                emergency_indicators=data.get("emergency_indicators", []),
                home_care=data.get("home_care", ""),
                hospital_advice=data.get("hospital_advice", ""),
                when_to_seek_emergency=data.get("when_to_seek_emergency", "")
            )
        except Exception as e:
            print(f"❌ Treatment analysis error: {e}")
            # Enhanced fallback with specific treatment protocols
            return self._get_fallback_treatment(diagnosis, symptoms)

    def _get_fallback_treatment(self, diagnosis: str, symptoms: Dict[str, Any]) -> TreatmentAnalysis:
        """Get evidence-based fallback treatment protocols."""
        treatment_db = {
            "Community-Acquired Pneumonia": TreatmentAnalysis(
                primary_treatment="Antibiotic therapy with Amoxicillin 500mg three times daily for 7-10 days",
                alternative_treatments=["Doxycycline 100mg twice daily for 7-10 days", "Azithromycin 500mg once daily for 5 days"],
                treatment_duration="7-10 days of antibiotic therapy",
                success_probability=0.92,
                lifestyle_recommendations=["Bed rest during acute phase", "Increased fluid intake (2-3 liters daily)", "Nutrient-rich diet"],
                follow_up_care=["Follow-up chest X-ray in 4-6 weeks if smoker", "Monitor temperature twice daily"],
                emergency_indicators=["Difficulty breathing", "Chest pain", "Fever above 39.5°C", "Confusion or disorientation"],
                home_care="Rest in semi-upright position, use humidifier, deep breathing exercises",
                hospital_advice="Seek immediate medical attention for severe symptoms or if over 65 years with comorbidities",
                when_to_seek_emergency="If experiencing shortness of breath, persistent high fever, or worsening symptoms despite antibiotics"
            ),
            "Influenza Type A": TreatmentAnalysis(
                primary_treatment="Oseltamivir (Tamiflu) 75mg twice daily for 5 days if started within 48 hours",
                alternative_treatments=["Zanamivir inhalation twice daily for 5 days", "Supportive care only if >48 hours"],
                treatment_duration="5 days for antiviral therapy, 7-10 days for symptom recovery",
                success_probability=0.85,
                lifestyle_recommendations=["Isolation to prevent spread", "Frequent hand washing", "Adequate rest"],
                follow_up_care=["Monitor for secondary bacterial infection", "Consider pneumococcal vaccine"],
                emergency_indicators=["Difficulty breathing", "Persistent high fever", "Severe headache or neck stiffness", "Confusion"],
                home_care="Stay hydrated, rest, monitor temperature every 4 hours, use humidifier",
                hospital_advice="Seek care if high risk (pregnant, elderly, chronic conditions) or severe symptoms",
                when_to_seek_emergency="If symptoms worsen after initial improvement or if severe respiratory distress"
            ),
            "Strep Pharyngitis": TreatmentAnalysis(
                primary_treatment="Penicillin V 500mg three times daily for 10 days",
                alternative_treatments=["Amoxicillin 500mg three times daily for 10 days", "Clindamycin for penicillin allergy"],
                treatment_duration="10 days complete antibiotic course",
                success_probability=0.95,
                lifestyle_recommendations=["Gargle with warm salt water", "Avoid irritants like smoke", "Soft diet if throat pain"],
                follow_up_care=["Throat culture if no improvement in 48 hours", "Consider tonsillectomy if recurrent"],
                emergency_indicators=["Difficulty breathing", "Inability to swallow saliva", "High fever >39°C", "Rash"],
                home_care="Rest voice, drink warm liquids, use throat lozenges, humidifier",
                hospital_advice="Seek care if unable to swallow, breathing difficulty, or no improvement after 48 hours",
                when_to_seek_emergency="If airway compromise, severe pain, or systemic symptoms"
            )
        }
        
        return treatment_db.get(diagnosis, TreatmentAnalysis(
            primary_treatment="Symptomatic treatment with rest and hydration",
            alternative_treatments=["Supportive care", "Over-the-counter medications"],
            treatment_duration="5-7 days for viral illnesses",
            success_probability=0.80,
            lifestyle_recommendations=["Adequate rest", "Increased fluid intake", "Balanced nutrition"],
            follow_up_care=["Monitor symptoms", "Seek care if worsening"],
            emergency_indicators=["High fever >39.5°C", "Difficulty breathing", "Severe pain", "Confusion"],
            home_care="Rest, stay hydrated, monitor symptoms, use over-the-counter medications as needed",
            hospital_advice="Seek medical attention if symptoms persist beyond 5-7 days or worsen",
            when_to_seek_emergency="If experiencing severe symptoms or emergency indicators"
        ))

    # ------------------------------------------------------------------ #
    #  4. DOCTOR VERIFICATION
    # ------------------------------------------------------------------ #
    async def verify_medical_assessment(
        self,
        patient_case: Dict[str, Any],
        ai_diagnosis: str,
        doctor_diagnosis: Optional[str] = None
    ) -> DoctorVerification:
        """Verify medical assessment using Gemini AI."""
        prompt = VERIFICATION_PROMPT.format(
            patient_case=json.dumps(patient_case),
            ai_diagnosis=ai_diagnosis,
            doctor_diagnosis=doctor_diagnosis or "Not provided",
        )

        try:
            data = await self._call_gemini(prompt)
            print(f"✅ Gemini verification score: {data.get('verification_score', '?')}")
            return DoctorVerification(
                verification_score=int(data.get("verification_score", 75)),
                confidence_level=data.get("confidence_level", "Medium"),
                recommended_actions=data.get("recommended_actions", []),
                additional_tests=data.get("additional_tests", []),
                specialist_referral=data.get("specialist_referral"),
                red_flags=data.get("red_flags", [])
            )
        except Exception as e:
            print(f"❌ Medical verification error: {e}")
            # Enhanced fallback with diagnosis-specific verification
            return self._get_fallback_verification(ai_diagnosis, patient_case)

    def _get_fallback_verification(self, diagnosis: str, patient_case: Dict[str, Any]) -> DoctorVerification:
        """Get evidence-based fallback verification scores."""
        verification_db = {
            "Community-Acquired Pneumonia": DoctorVerification(
                verification_score=92,
                confidence_level="High",
                recommended_actions=["Start antibiotic therapy immediately", "Obtain chest X-ray", "Monitor oxygen saturation"],
                additional_tests=["Complete blood count", "Chest radiograph", "Blood cultures if severe"],
                specialist_referral="Pulmonologist if severe or non-responsive",
                red_flags=["Low oxygen saturation", "Confusion", "Hypotension", "Multi-lobar involvement"]
            ),
            "Influenza Type A": DoctorVerification(
                verification_score=85,
                confidence_level="High",
                recommended_actions=["Start antiviral therapy if <48 hours", "Isolate patient", "Provide symptomatic care"],
                additional_tests=["Rapid influenza test", "Complete blood count", "Chest X-ray if respiratory distress"],
                specialist_referral="Infectious disease specialist if high-risk or complications",
                red_flags=["Difficulty breathing", "Persistent high fever", "Chest pain", "Altered mental status"]
            ),
            "Strep Pharyngitis": DoctorVerification(
                verification_score=95,
                confidence_level="High",
                recommended_actions=["Start antibiotic therapy", "Obtain throat culture", "Advise rest and hydration"],
                additional_tests=["Rapid strep test", "Throat culture", "Complete blood count if systemic symptoms"],
                specialist_referral="ENT specialist if recurrent or complications",
                red_flags=["Difficulty breathing", "Inability to swallow", "High fever", "Rash suggesting scarlet fever"]
            ),
            "Acute Bronchitis": DoctorVerification(
                verification_score=78,
                confidence_level="Medium",
                recommended_actions=["Provide symptomatic treatment", "Rule out pneumonia", "Advise rest and hydration"],
                additional_tests=["Chest X-ray if fever >38.5°C", "Complete blood count if prolonged illness"],
                specialist_referral="Pulmonologist if cough persists >3 weeks",
                red_flags=["Fever >38.5°C", "Productive cough with colored sputum", "Shortness of breath"]
            )
        }
        
        return verification_db.get(diagnosis, DoctorVerification(
            verification_score=75,
            confidence_level="Medium",
            recommended_actions=["Obtain detailed history", "Perform physical examination", "Consider diagnostic testing"],
            additional_tests=["Complete blood count", "Basic metabolic panel", "Chest X-ray if indicated"],
            specialist_referral=None,
            red_flags=["High fever", "Difficulty breathing", "Severe pain", "Altered mental status"]
        ))

    # ------------------------------------------------------------------ #
    #  5. SIDE EFFECT PREDICTION
    # ------------------------------------------------------------------ #
    async def predict_side_effects(
        self,
        medications: List[str],
        patient_profile: Dict[str, Any]
    ) -> SideEffectPrediction:
        """Predict side effects using Gemini AI."""
        prompt = SIDE_EFFECT_PROMPT.format(
            medications=json.dumps(medications),
            patient_profile=json.dumps(patient_profile),
        )

        try:
            data = await self._call_gemini(prompt)
            print(f"✅ Gemini side effect prediction complete")
            return SideEffectPrediction(
                common_side_effects=data.get("common_side_effects", []),
                rare_side_effects=data.get("rare_side_effects", []),
                severe_reactions=data.get("severe_reactions", []),
                drug_interactions=data.get("drug_interactions", []),
                contraindications=data.get("contraindications", []),
                monitoring_parameters=data.get("monitoring_parameters", []),
                risk_level=data.get("risk_level", "Medium")
            )
        except Exception as e:
            print(f"❌ Side effect prediction error: {e}")
            # Enhanced fallback with medication-specific side effects
            return self._get_fallback_side_effects(medications, patient_profile)

    def _get_fallback_side_effects(self, medications: List[str], patient_profile: Dict[str, Any]) -> SideEffectPrediction:
        """Get evidence-based fallback side effect predictions."""
        side_effect_db = {
            "Amoxicillin": SideEffectPrediction(
                common_side_effects=["Nausea", "Diarrhea", "Vomiting", "Rash"],
                rare_side_effects=["Yeast infection", "Allergic reaction", "Headache"],
                severe_reactions=["Anaphylaxis (seek emergency care)", "Severe skin reactions (Stevens-Johnson)"],
                drug_interactions=["Allopurinol (increased rash risk)", "Methotrexate (increased toxicity)", "Warfarin (altered effect)"],
                contraindications=["Penicillin allergy", "Mononucleosis", "Severe kidney disease"],
                monitoring_parameters=["Complete blood count", "Kidney function tests", "Allergic reaction monitoring"],
                risk_level="Low"
            ),
            "Oseltamivir": SideEffectPrediction(
                common_side_effects=["Nausea", "Vomiting", "Headache", "Abdominal pain"],
                rare_side_effects=["Dizziness", "Fatigue", "Insomnia", "Cough"],
                severe_reactions=["Severe allergic reaction", "Neuropsychiatric effects (rare)"],
                drug_interactions=["Live attenuated influenza vaccine (reduce effectiveness)"],
                contraindications=["Severe kidney impairment", "Known hypersensitivity"],
                monitoring_parameters=["Neuropsychiatric symptoms", "Kidney function", "Gastrointestinal tolerance"],
                risk_level="Low"
            ),
            "Acetaminophen": SideEffectPrediction(
                common_side_effects=["Rare at therapeutic doses", "Mild stomach upset"],
                rare_side_effects=["Skin rash", "Liver enzyme elevation"],
                severe_reactions=["Liver failure (overdose)", "Severe skin reactions"],
                drug_interactions=["Alcohol (increased liver toxicity)", "Warfarin (enhanced anticoagulation)", "Isoniazid (increased liver toxicity)"],
                contraindications=["Severe liver disease", "Alcoholism", "Chronic high-dose use"],
                monitoring_parameters=["Liver function tests", "Total daily dose tracking", "Alcohol consumption"],
                risk_level="Low"
            ),
            "Penicillin V": SideEffectPrediction(
                common_side_effects=["Nausea", "Diarrhea", "Stomach upset", "Rash"],
                rare_side_effects=["Yeast infection", "Headache", "Dizziness"],
                severe_reactions=["Anaphylaxis (seek emergency care)", "Severe skin reactions"],
                drug_interactions=["Methotrexate (increased toxicity)", "Tetracyclines (reduced effectiveness)"],
                contraindications=["Penicillin allergy", "Asthma with penicillin sensitivity"],
                monitoring_parameters=["Allergic reaction monitoring", "Complete blood count", "Kidney function"],
                risk_level="Low"
            )
        }
        
        # Find matching medications or return general side effects
        for med in medications:
            for key, effects in side_effect_db.items():
                if key.lower() in med.lower():
                    return effects
        
        return SideEffectPrediction(
            common_side_effects=["Nausea", "Headache", "Dizziness", "Fatigue"],
            rare_side_effects=["Mild allergic reaction", "Stomach upset", "Skin rash"],
            severe_reactions=["Severe allergic reaction (anaphylaxis)", "Organ-specific toxicity"],
            drug_interactions=["Consult pharmacist for complete interaction profile"],
            contraindications=["Known allergy to medication class", "Severe organ impairment"],
            monitoring_parameters=["Vital signs", "Symptom monitoring", "Blood tests as indicated"],
            risk_level="Medium"
        )


# Global instance
gemini_ai = GeminiMedicalAI()
