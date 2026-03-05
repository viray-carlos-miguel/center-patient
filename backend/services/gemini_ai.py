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

# Import ML Urgency Classifier (replaces old prediction_engine + rule-based logic)
try:
    import sys
    ml_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'ml')
    if ml_path not in sys.path:
        sys.path.insert(0, ml_path)
    from ml.urgency_classifier import UrgencyClassifier
    URGENCY_CLASSIFIER = UrgencyClassifier()
    ML_AVAILABLE = URGENCY_CLASSIFIER.is_loaded
    if ML_AVAILABLE:
        print("✅ UrgencyClassifier loaded into Gemini AI service")
    else:
        print("⚠️ UrgencyClassifier not trained yet")
except Exception as e:
    print(f"⚠️ UrgencyClassifier not available: {e}")
    URGENCY_CLASSIFIER = None
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
        self.urgency_classifier = URGENCY_CLASSIFIER
        self.ml_available = ML_AVAILABLE
    
    def _extract_symptom_names(self, symptoms: Dict) -> list:
        """Extract human-readable symptom names from frontend symptom dict."""
        names = []
        for key, value in symptoms.items():
            if not value:
                continue
            if key.startswith("has_"):
                clean = key.replace("has_", "").replace("_", " ").title()
                names.append(clean)
        return names
    
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
    #  v2: ML UrgencyClassifier for urgency + Gemini AI for disease prediction
    #  No rule-based if/elif logic — all decisions are ML/AI-driven
    # ------------------------------------------------------------------ #
    async def analyze_symptoms_for_disease(self, symptoms: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze symptoms using ML urgency classifier + Gemini AI for disease prediction.
        All rule-based logic has been removed in favor of ML + AI."""
        description = symptoms.get('description', 'No description provided')
        temperature = symptoms.get('temperature', 'Not measured')
        duration_hours = symptoms.get('duration_hours', 'Unknown')
        severity = symptoms.get('severity', 'Unknown')
        
        # Extract symptom names from frontend flags
        specific_symptoms = self._extract_symptom_names(symptoms)
        
        # Create enhanced description with specific symptoms
        enhanced_description = description
        if specific_symptoms:
            enhanced_description += f" | Specific symptoms: {', '.join(specific_symptoms)}"

        try:
            # ── Step 1: ML Urgency Classification (no rule-based logic) ──
            urgency = "medium"
            urgency_confidence = 0.0
            urgency_method = "none"
            urgency_probabilities = {}

            if self.urgency_classifier and self.ml_available:
                urgency_result = self.urgency_classifier.predict_from_frontend(symptoms)
                urgency = urgency_result.get("urgency", "medium")
                urgency_confidence = urgency_result.get("confidence", 0.0)
                urgency_method = urgency_result.get("method", "unknown")
                urgency_probabilities = urgency_result.get("probabilities", {})
                print(f"🎯 ML Urgency: {urgency} ({urgency_confidence:.0%}) via {urgency_method}")

            # Map urgency to emergency assessment
            URGENCY_MAP = {
                "critical": {"level": "Emergency", "go_to_hospital": True},
                "high": {"level": "Urgent", "go_to_hospital": True},
                "medium": {"level": "Moderate", "go_to_hospital": False},
                "low": {"level": "Non-urgent", "go_to_hospital": False},
            }
            emergency_info = URGENCY_MAP.get(urgency, URGENCY_MAP["medium"])

            # ── Step 2: Gemini AI Disease Prediction (replaces all rule-based logic) ──
            symptom_list = ", ".join(specific_symptoms) if specific_symptoms else description

            disease_prompt = f"""You are a medical diagnosis AI. Analyze these symptoms and provide a diagnosis.

Patient symptoms: {symptom_list}
Description: {description}
Temperature: {temperature}
Duration: {duration_hours} hours
Severity: {severity}/10
ML-assessed urgency: {urgency}

Based STRICTLY on the symptoms above, respond in this exact JSON format:
{{
  "primary_condition": "Most likely disease/condition",
  "confidence": 85,
  "reasoning": "Brief medical reasoning",
  "matching_symptoms": ["symptom1", "symptom2"],
  "differential_diagnosis": [
    {{"condition": "Alternative 1", "confidence": 60, "reasoning": "..."}},
    {{"condition": "Alternative 2", "confidence": 40, "reasoning": "..."}}
  ],
  "recommended_tests": ["Test 1", "Test 2"],
  "treatment_recommendations": {{
    "medications": ["Med 1"],
    "self_care": ["Rest", "Hydration"],
    "when_to_see_doctor": "If symptoms worsen"
  }}
}}

IMPORTANT: Do NOT assume symptoms not listed. Be accurate and evidence-based."""

            gemini_data = await self._call_gemini(disease_prompt)

            # Extract Gemini predictions
            primary_condition = gemini_data.get("primary_condition", "Requires Medical Evaluation")
            confidence = gemini_data.get("confidence", 70)
            reasoning = gemini_data.get("reasoning", "AI-based analysis")
            matching_symptoms = gemini_data.get("matching_symptoms", specific_symptoms or [])
            differential = gemini_data.get("differential_diagnosis", [])
            recommended_tests = gemini_data.get("recommended_tests", ["Physical Examination"])
            treatment = gemini_data.get("treatment_recommendations", {
                "medications": ["Symptomatic treatment"],
                "self_care": ["Rest", "Hydration", "Monitor symptoms"],
                "when_to_see_doctor": "If symptoms worsen or persist"
            })

            # ── Step 3: Build analysis result ──
            analysis = {
                "primary_prediction": {
                    "condition": primary_condition,
                    "confidence": confidence,
                    "matching_symptoms": matching_symptoms,
                    "reasoning": reasoning
                },
                "differential_diagnosis": differential,
                "emergency_assessment": {
                    "level": emergency_info["level"],
                    "go_to_hospital": emergency_info["go_to_hospital"],
                    "message": f"{'Seek immediate medical attention' if emergency_info['go_to_hospital'] else 'Monitor symptoms'} for {primary_condition}",
                    "warning_signs": ["High fever", "Difficulty breathing", "Severe pain"]
                },
                "treatment_recommendations": treatment,
                "risk_factors": {
                    "complications": ["Secondary infection"] if urgency in ("high", "critical") else [],
                    "monitoring": ["Temperature", "Symptom progression"]
                },
                "urgency_assessment": {
                    "urgency": urgency,
                    "urgency_confidence": round(urgency_confidence * 100, 1),
                    "urgency_method": urgency_method,
                    "urgency_probabilities": urgency_probabilities,
                },
                "ai_model": f"ml-urgency+gemini-disease",
                "educational_disclaimer": "This is for educational purposes only. Always consult a healthcare professional."
            }

            print(f"🎯 AI DIAGNOSIS: {primary_condition} ({confidence}% confidence), Urgency: {urgency}")
            return analysis

        except Exception as e:
            print(f"❌ Symptom analysis error: {e}")
            import traceback
            traceback.print_exc()
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
