"""AI Insights API (ChatGPT)

Provides comprehensive AI insights (medicine, treatment, verification, side effects)
using OpenAI ChatGPT.

Response schema matches what the frontend AIInsights component expects today.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
import os
import json

from openai import OpenAI

router = APIRouter(prefix="/api/ai-insights", tags=["ai-insights"])


class ComprehensiveAnalysisRequest(BaseModel):
    symptoms: Dict[str, Any]
    patient_profile: Dict[str, Any]
    diagnosis: Optional[str] = None
    medications: Optional[List[str]] = None
    doctor_diagnosis: Optional[str] = None


def _client() -> OpenAI:
    api_key = os.getenv("CHATGPT_API_KEY")
    if not api_key:
        raise RuntimeError("CHATGPT_API_KEY not set")
    return OpenAI(api_key=api_key)


@router.post("/comprehensive-analysis")
async def comprehensive_analysis(req: ComprehensiveAnalysisRequest):
    """Generate comprehensive AI insights using ChatGPT."""
    model = os.getenv("CHATGPT_MODEL", "gpt-4o")

    # Strictly use provided inputs (no DB lookups / no extra patient data)
    payload = {
        "symptoms": req.symptoms,
        "patient_profile": req.patient_profile,
        "diagnosis": req.diagnosis,
        "medications": req.medications,
        "doctor_diagnosis": req.doctor_diagnosis,
    }

    system = (
        "You are a clinical support assistant. Return evidence-informed, cautious suggestions. "
        "Do not invent patient data. Use ONLY the provided JSON input. "
        "Return ONLY valid JSON matching the required schema."
    )

    user = (
        "Generate AI Insights in the following JSON schema. If something is unknown, "
        "use safe general guidance and empty arrays.\n\n"
        "Required JSON schema:\n"
        "{\n"
        "  \"medicine_recommendations\": [\n"
        "    {\n"
        "      \"name\": \"string\",\n"
        "      \"dosage\": \"string\",\n"
        "      \"frequency\": \"string\",\n"
        "      \"duration\": \"string\",\n"
        "      \"purpose\": \"string\",\n"
        "      \"alternatives\": [\"string\"],\n"
        "      \"precautions\": [\"string\"],\n"
        "      \"effectiveness_score\": 0.0,\n"
        "      \"side_effects\": [\"string\"]\n"
        "    }\n"
        "  ],\n"
        "  \"treatment_analysis\": {\n"
        "    \"primary_treatment\": \"string\",\n"
        "    \"alternative_treatments\": [\"string\"],\n"
        "    \"treatment_duration\": \"string\",\n"
        "    \"success_probability\": 0.0,\n"
        "    \"lifestyle_recommendations\": [\"string\"],\n"
        "    \"follow_up_care\": [\"string\"],\n"
        "    \"emergency_indicators\": [\"string\"],\n"
        "    \"home_care\": \"string\",\n"
        "    \"hospital_advice\": \"string\",\n"
        "    \"when_to_seek_emergency\": \"string\"\n"
        "  },\n"
        "  \"verification\": {\n"
        "    \"verification_score\": 0.0,\n"
        "    \"confidence_level\": \"Low|Medium|High\",\n"
        "    \"recommended_actions\": [\"string\"],\n"
        "    \"additional_tests\": [\"string\"],\n"
        "    \"specialist_referral\": \"string|null\",\n"
        "    \"red_flags\": [\"string\"]\n"
        "  },\n"
        "  \"side_effects\": {\n"
        "    \"common_side_effects\": [\"string\"],\n"
        "    \"rare_side_effects\": [\"string\"],\n"
        "    \"severe_reactions\": [\"string\"],\n"
        "    \"drug_interactions\": [\"string\"],\n"
        "    \"contraindications\": [\"string\"],\n"
        "    \"monitoring_parameters\": [\"string\"],\n"
        "    \"risk_level\": \"low|medium|high\"\n"
        "  },\n"
        "  \"disclaimer\": \"string\"\n"
        "}\n\n"
        f"Input JSON:\n{json.dumps(payload, ensure_ascii=False)}"
    )

    try:
        client = _client()
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.3,
            max_tokens=1200,
            response_format={"type": "json_object"},
        )

        content = resp.choices[0].message.content
        data = json.loads(content)

        return {
            "success": True,
            "comprehensive_analysis": {
                "medicine_recommendations": data.get("medicine_recommendations", []),
                "treatment_analysis": data.get("treatment_analysis"),
                "verification": data.get("verification"),
                "side_effects": data.get("side_effects"),
            },
            "disclaimer": data.get(
                "disclaimer",
                "AI-generated insights for educational/clinical support only. Consult qualified healthcare professionals.",
            ),
            "model": model,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Insights failed: {str(e)}")
