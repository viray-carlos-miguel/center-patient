"""
Gemini 2.5 Flash AI Service for Advanced Medical Features
Enhanced with accurate disease prediction and comprehensive analysis
"""

import os
import json
import asyncio
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# Configure Gemini API
GEMINI_API_KEY = "AIzaSyDZ_BLRf-wnjsYOtMfchuCwgGci6wUwa2o"
genai.configure(api_key=GEMINI_API_KEY)


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


SYMPTOM_ANALYSIS_PROMPT = """You are a medical AI expert. Analyze the following symptoms and return ONLY a JSON object (no markdown, no explanation outside JSON).

PATIENT SYMPTOMS:
- Description: {description}
- Temperature: {temperature} Celsius
- Duration: {duration_hours} hours
- Severity: {severity} out of 10

Return ONLY this JSON structure with accurate medical analysis:
{{
  "primary_prediction": {{
    "condition": "<most likely disease/condition name>",
    "confidence": <number 0-100>,
    "matching_symptoms": ["<symptom1>", "<symptom2>"],
    "reasoning": "<brief medical reasoning>"
  }},
  "differential_diagnosis": [
    {{
      "condition": "<alternative condition>",
      "confidence": <number 0-100>,
      "reasoning": "<why less likely>"
    }}
  ],
  "emergency_assessment": {{
    "level": "<Critical|Urgent|Non-urgent>",
    "go_to_hospital": <true|false>,
    "message": "<specific medical advice>",
    "warning_signs": ["<sign1>", "<sign2>"]
  }},
  "treatment_recommendations": {{
    "medications": ["<medication with dosage>"],
    "self_care": ["<recommendation>"],
    "when_to_see_doctor": "<criteria>"
  }},
  "risk_factors": {{
    "complications": ["<complication>"],
    "monitoring": ["<what to watch>"]
  }}
}}

Be medically accurate. Consider the COMBINATION of symptoms together, not individually. For example fever + headache + fatigue for 2 days at 38.5C is likely Influenza or viral infection, NOT just "Unknown"."""

MEDICINE_PROMPT = """You are a medical expert. Provide accurate medicine recommendations for this case. Return ONLY a JSON object.

DIAGNOSIS: {diagnosis}
SYMPTOMS: {description}
TEMPERATURE: {temperature} Celsius
SEVERITY: {severity} out of 10
PATIENT: {patient_profile}

Return ONLY this JSON:
{{
  "medicines": [
    {{
      "name": "<brand name>",
      "generic_name": "<generic name>",
      "dosage": "<exact dosage>",
      "frequency": "<how often>",
      "duration": "<how long>",
      "purpose": "<why prescribed>",
      "effectiveness_score": <number 0-100>,
      "alternatives": ["<alt1>"],
      "precautions": ["<precaution1>"],
      "side_effects": ["<effect1>"]
    }}
  ]
}}

Provide 3-5 specific, evidence-based medications appropriate for the diagnosis."""

TREATMENT_PROMPT = """You are a medical expert. Analyze treatment approaches. Return ONLY a JSON object.

DIAGNOSIS: {diagnosis}
SYMPTOMS: {symptoms}
PATIENT: {patient_profile}

Return ONLY this JSON:
{{
  "primary_treatment": "<main treatment approach>",
  "alternative_treatments": ["<alt1>", "<alt2>"],
  "treatment_duration": "<expected duration>",
  "success_probability": <number 0.0 to 1.0>,
  "lifestyle_recommendations": ["<rec1>", "<rec2>"],
  "follow_up_care": ["<care1>"],
  "emergency_indicators": ["<indicator1>"]
}}

Be specific and evidence-based."""

VERIFICATION_PROMPT = """You are a senior medical expert verifying a diagnosis. Return ONLY a JSON object.

PATIENT CASE: {patient_case}
AI DIAGNOSIS: {ai_diagnosis}
DOCTOR DIAGNOSIS: {doctor_diagnosis}

Return ONLY this JSON:
{{
  "verification_score": <number 0-100>,
  "confidence_level": "<High|Medium|Low>",
  "recommended_actions": ["<action1>"],
  "additional_tests": ["<test1>"],
  "specialist_referral": "<specialist or null>",
  "red_flags": ["<flag1>"]
}}

Provide honest, accurate medical verification."""

SIDE_EFFECT_PROMPT = """You are a pharmacology expert. Predict side effects. Return ONLY a JSON object.

MEDICATIONS: {medications}
PATIENT: {patient_profile}

Return ONLY this JSON:
{{
  "common_side_effects": ["<effect1>"],
  "rare_side_effects": ["<effect1>"],
  "severe_reactions": ["<reaction1>"],
  "drug_interactions": ["<interaction1>"],
  "contraindications": ["<contraindication1>"],
  "monitoring_parameters": ["<parameter1>"],
  "risk_level": "<Low|Medium|High>"
}}

Be thorough and evidence-based."""


class GeminiMedicalAI:
    def __init__(self):
        """Initialize Gemini 2.5 Flash model with safety configurations"""
        self.model = genai.GenerativeModel(
            'gemini-2.5-flash',
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )
        self.generation_config = {
            "temperature": 0.3,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 4096,
        }

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

        prompt = SYMPTOM_ANALYSIS_PROMPT.format(
            description=description,
            temperature=temperature,
            duration_hours=duration_hours,
            severity=severity,
        )

        try:
            analysis = await self._call_gemini(prompt)
            analysis["ai_model"] = "gemini-2.5-flash"
            analysis["educational_disclaimer"] = (
                "This is for educational purposes only. Always consult a healthcare professional."
            )
            print(f"✅ Gemini diagnosis: {analysis.get('primary_prediction', {}).get('condition', '?')}")
            return analysis
        except Exception as e:
            print(f"❌ Gemini symptom analysis error: {e}")
            return {
                "primary_prediction": {
                    "condition": "Requires Medical Evaluation",
                    "confidence": 50,
                    "matching_symptoms": [],
                    "reasoning": f"AI analysis encountered an error: {e}"
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
                    "monitoring": ["Symptom progression", "Temperature changes"]
                },
                "ai_model": "gemini-2.5-flash",
                "error": str(e),
                "educational_disclaimer": "This is for educational purposes only."
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
                    effectiveness_score=float(med.get("effectiveness_score", 0)),
                    side_effects=med.get("side_effects", [])
                ))
            print(f"✅ Gemini medicine recs: {len(medicines)} medications")
            return medicines
        except Exception as e:
            print(f"❌ Medicine recommendation error: {e}")
            return []

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
                emergency_indicators=data.get("emergency_indicators", [])
            )
        except Exception as e:
            print(f"❌ Treatment analysis error: {e}")
            return TreatmentAnalysis(
                primary_treatment="Standard medical care recommended",
                alternative_treatments=[],
                treatment_duration="Varies based on condition",
                success_probability=0.7,
                lifestyle_recommendations=["Rest", "Adequate hydration", "Balanced nutrition"],
                follow_up_care=["Schedule follow-up within 1 week"],
                emergency_indicators=["Worsening symptoms", "High fever above 39.5C"]
            )

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
                verification_score=float(data.get("verification_score", 0)),
                confidence_level=data.get("confidence_level", "Medium"),
                recommended_actions=data.get("recommended_actions", []),
                additional_tests=data.get("additional_tests", []),
                specialist_referral=data.get("specialist_referral"),
                red_flags=data.get("red_flags", [])
            )
        except Exception as e:
            print(f"❌ Medical verification error: {e}")
            return DoctorVerification(
                verification_score=70.0,
                confidence_level="Medium",
                recommended_actions=["Consult with attending physician"],
                additional_tests=["Complete blood count", "Basic metabolic panel"],
                specialist_referral=None,
                red_flags=[]
            )

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
            return SideEffectPrediction(
                common_side_effects=["Nausea", "Headache", "Dizziness"],
                rare_side_effects=["Allergic reaction"],
                severe_reactions=["Anaphylaxis (seek emergency care)"],
                drug_interactions=["Consult pharmacist for full interaction check"],
                contraindications=["Known allergy to medication"],
                monitoring_parameters=["Vital signs", "Symptom changes"],
                risk_level="Low"
            )


# Global instance
gemini_ai = GeminiMedicalAI()
