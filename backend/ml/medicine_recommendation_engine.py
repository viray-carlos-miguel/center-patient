"""
Medicine Recommendation Engine
AI-powered system for recommending medicines based on symptoms and patient profile
"""

from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import json
from dataclasses import dataclass
from enum import Enum

class RiskLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"

class MedicineCategory(str, Enum):
    PRESCRIPTION = "prescription"
    OVER_THE_COUNTER = "over_the_counter"
    SUPPLEMENT = "supplement"

@dataclass
class PatientProfile:
    age: int
    weight: float
    medical_conditions: List[str]
    current_medications: List[str]
    allergies: List[str]
    pregnancy: bool
    breastfeeding: bool

@dataclass
class MedicineRecommendation:
    rank: int
    drug_name: str
    generic_name: str
    brand_names: List[str]
    category: MedicineCategory
    confidence: float
    risk_level: RiskLevel
    dosage: Dict[str, Any]
    treatment_analysis: Dict[str, Any]
    effectiveness: str
    availability: str
    price_range: str
    contraindications: List[str]
    side_effects: List[str]

@dataclass
class SafetyAnalysis:
    overall_risk: RiskLevel
    contraindications: List[Dict[str, Any]]
    interactions: List[Dict[str, Any]]
    side_effects: List[Dict[str, Any]]
    monitoring_required: List[str]
    warnings: List[str]

class MedicineRecommendationEngine:
    def __init__(self):
        self.drug_db = None
        self._load_drug_database()
    
    def _load_drug_database(self):
        """Load the drug database"""
        try:
            from data.drug_database import drug_db
            self.drug_db = drug_db
        except ImportError:
            print("Warning: Drug database not available")
            self.drug_db = None
    
    def recommend_medicines(self, symptoms: List[str], patient_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Generate medicine recommendations based on symptoms and patient profile"""
        try:
            if not self.drug_db:
                return self._fallback_recommendation(symptoms, patient_profile)
            
            # Convert patient profile dict to PatientProfile object
            profile = PatientProfile(
                age=patient_profile.get('age', 30),
                weight=patient_profile.get('weight', 70),
                medical_conditions=patient_profile.get('medical_conditions', []),
                current_medications=patient_profile.get('current_medications', []),
                allergies=patient_profile.get('allergies', []),
                pregnancy=patient_profile.get('pregnancy', False),
                breastfeeding=patient_profile.get('breastfeeding', False)
            )
            
            # Get candidate medicines based on symptoms
            candidates = self._get_candidate_medicines(symptoms)
            
            # Score and rank candidates based on patient factors
            scored_candidates = self._score_medicines(candidates, profile, symptoms)
            
            # Generate safety analysis
            safety_analysis = self._analyze_safety(scored_candidates, profile)
            
            # Generate treatment plans
            treatment_plans = self._generate_treatment_plans(scored_candidates, profile)
            
            # Check if prescription is required
            requires_prescription = any(med.category == MedicineCategory.PRESCRIPTION for med in scored_candidates[:3])
            
            return {
                "success": True,
                "recommendations": [self._medicine_to_dict(med) for med in scored_candidates[:5]],
                "safety_analysis": self._safety_to_dict(safety_analysis),
                "treatment_plans": treatment_plans,
                "requires_prescription": requires_prescription,
                "confidence": self._calculate_overall_confidence(scored_candidates[:3]),
                "risk_level": safety_analysis.overall_risk.value,
                "total_candidates": len(candidates),
                "filtered_candidates": len(scored_candidates)
            }
            
        except Exception as e:
            print(f"Error in medicine recommendation: {e}")
            return self._fallback_recommendation(symptoms, patient_profile)
    
    def _fallback_recommendation(self, symptoms: List[str], patient_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback recommendation when drug database is not available"""
        fallback_medicines = [
            {
                "rank": 1,
                "drug_name": "paracetamol",
                "generic_name": "Paracetamol",
                "brand_names": ["Tylenol", "Biogesic", "Calpol"],
                "category": "over_the_counter",
                "confidence": 0.75,
                "risk_level": "low",
                "dosage": {
                    "adult": "500-1000mg every 4-6 hours",
                    "child": "10-15mg/kg every 4-6 hours",
                    "max_daily": "4000mg"
                },
                "treatment_analysis": {
                    "effectiveness": "moderate",
                    "duration": "3-7 days",
                    "usage_instructions": ["Take with food", "Do not exceed recommended dose"],
                    "precautions": ["Avoid alcohol", "Monitor liver function"]
                },
                "effectiveness": "moderate",
                "availability": "widely_available",
                "price_range": "₱5-50"
            }
        ]
        
        return {
            "success": True,
            "recommendations": fallback_medicines,
            "safety_analysis": {
                "overall_risk": "low",
                "contraindications": [],
                "interactions": [],
                "side_effects": [],
                "monitoring_required": [],
                "warnings": ["Use as directed", "Consult doctor if symptoms persist"]
            },
            "treatment_plans": ["Rest and monitor symptoms", "Stay hydrated", "Take medication as needed"],
            "requires_prescription": False,
            "confidence": 0.65,
            "risk_level": "low",
            "total_candidates": 1,
            "filtered_candidates": 1
        }
    
    def _get_candidate_medicines(self, symptoms: List[str]) -> List[Dict[str, Any]]:
        """Get candidate medicines based on symptoms"""
        if not self.drug_db:
            return []
        
        candidates = []
        symptom_lower = [s.lower() for s in symptoms]
        
        # Search for medicines that match symptoms
        for drug_name, drug_info in self.drug_db.drugs.items():
            # Check if any symptom matches drug indications
            matching_indications = []
            for indication in drug_info.get('indications', []):
                if any(symptom in indication.lower() or indication.lower() in symptom for symptom in symptom_lower):
                    matching_indications.append(indication)
            
            if matching_indications:
                candidates.append({
                    'drug_name': drug_name,
                    'drug_info': drug_info,
                    'matching_indications': matching_indications,
                    'match_score': len(matching_indications)
                })
        
        # Sort by match score
        candidates.sort(key=lambda x: x['match_score'], reverse=True)
        return candidates
    
    def _score_medicines(self, candidates: List[Dict[str, Any]], profile: PatientProfile, symptoms: List[str]) -> List[MedicineRecommendation]:
        """Score and rank medicines based on patient factors"""
        scored_medicines = []
        
        for i, candidate in enumerate(candidates[:10]):  # Top 10 candidates
            drug_info = candidate['drug_info']
            
            # Base score from symptom matching
            base_score = candidate['match_score'] / len(symptoms)
            
            # Adjust score based on patient factors
            adjusted_score = self._adjust_score_for_patient(base_score, drug_info, profile)
            
            # Determine risk level
            risk_level = self._assess_risk_level(drug_info, profile)
            
            # Create recommendation
            recommendation = MedicineRecommendation(
                rank=i + 1,
                drug_name=candidate['drug_name'],
                generic_name=drug_info.get('generic_name', candidate['drug_name']),
                brand_names=drug_info.get('brand_names', []),
                category=self._determine_category(drug_info),
                confidence=adjusted_score,
                risk_level=risk_level,
                dosage=drug_info.get('dosage', {}),
                treatment_analysis=self._generate_treatment_analysis(drug_info, profile),
                effectiveness=self._assess_effectiveness(drug_info, profile),
                availability=drug_info.get('availability', 'available'),
                price_range=drug_info.get('price_range', '₱10-100'),
                contraindications=drug_info.get('contraindications', []),
                side_effects=drug_info.get('side_effects', [])
            )
            
            scored_medicines.append(recommendation)
        
        # Sort by adjusted score
        scored_medicines.sort(key=lambda x: x.confidence, reverse=True)
        return scored_medicines
    
    def _adjust_score_for_patient(self, base_score: float, drug_info: Dict[str, Any], profile: PatientProfile) -> float:
        """Adjust medicine score based on patient profile"""
        adjusted_score = base_score
        
        # Age adjustments
        if profile.age < 12 and drug_info.get('pediatric_safe', True):
            adjusted_score += 0.1
        elif profile.age < 12 and not drug_info.get('pediatric_safe', True):
            adjusted_score -= 0.3
        
        if profile.age > 65 and drug_info.get('geriatric_safe', True):
            adjusted_score += 0.05
        elif profile.age > 65 and not drug_info.get('geriatric_safe', True):
            adjusted_score -= 0.2
        
        # Pregnancy/Breastfeeding adjustments
        if profile.pregnancy and drug_info.get('pregnancy_safe', False):
            adjusted_score += 0.2
        elif profile.pregnancy and not drug_info.get('pregnancy_safe', True):
            adjusted_score -= 0.4
        
        if profile.breastfeeding and drug_info.get('breastfeeding_safe', False):
            adjusted_score += 0.1
        elif profile.breastfeeding and not drug_info.get('breastfeeding_safe', True):
            adjusted_score -= 0.3
        
        # Allergy adjustments
        for allergy in profile.allergies:
            if allergy.lower() in [drug.lower() for drug in drug_info.get('allergens', [])]:
                adjusted_score -= 0.5  # Severe penalty for allergens
        
        # Medical condition adjustments
        for condition in profile.medical_conditions:
            if condition.lower() in [contra.lower() for contra in drug_info.get('contraindications', [])]:
                adjusted_score -= 0.4  # Penalty for contraindications
        
        # Drug interaction adjustments
        for medication in profile.current_medications:
            if medication.lower() in [interact.lower() for interact in drug_info.get('interactions', [])]:
                adjusted_score -= 0.3  # Penalty for interactions
        
        # Ensure score is within valid range
        return max(0.0, min(1.0, adjusted_score))
    
    def _assess_risk_level(self, drug_info: Dict[str, Any], profile: PatientProfile) -> RiskLevel:
        """Assess the risk level of a medicine for the patient"""
        risk_score = 0
        
        # Check for high-risk factors
        if profile.age < 12 and not drug_info.get('pediatric_safe', True):
            risk_score += 3
        if profile.age > 65 and not drug_info.get('geriatric_safe', True):
            risk_score += 2
        if profile.pregnancy and not drug_info.get('pregnancy_safe', True):
            risk_score += 4
        if profile.breastfeeding and not drug_info.get('breastfeeding_safe', True):
            risk_score += 2
        
        # Check for contraindications
        for condition in profile.medical_conditions:
            if condition.lower() in [contra.lower() for contra in drug_info.get('contraindications', [])]:
                risk_score += 3
        
        # Check for interactions
        for medication in profile.current_medications:
            if medication.lower() in [interact.lower() for interact in drug_info.get('interactions', [])]:
                risk_score += 2
        
        # Check for allergies
        for allergy in profile.allergies:
            if allergy.lower() in [drug.lower() for drug in drug_info.get('allergens', [])]:
                risk_score += 5  # Highest risk for allergens
        
        # Determine risk level based on score
        if risk_score >= 5:
            return RiskLevel.HIGH
        elif risk_score >= 2:
            return RiskLevel.MODERATE
        else:
            return RiskLevel.LOW
    
    def _determine_category(self, drug_info: Dict[str, Any]) -> MedicineCategory:
        """Determine the category of the medicine"""
        category = drug_info.get('category', 'over_the_counter').lower()
        
        if 'prescription' in category or 'rx' in category:
            return MedicineCategory.PRESCRIPTION
        elif 'supplement' in category:
            return MedicineCategory.SUPPLEMENT
        else:
            return MedicineCategory.OVER_THE_COUNTER
    
    def _generate_treatment_analysis(self, drug_info: Dict[str, Any], profile: PatientProfile) -> Dict[str, Any]:
        """Generate treatment analysis for the medicine"""
        return {
            "effectiveness": drug_info.get('effectiveness', 'moderate'),
            "duration": drug_info.get('treatment_duration', '3-7 days'),
            "usage_instructions": drug_info.get('usage_instructions', ['Take as directed']),
            "precautions": drug_info.get('precautions', ['Follow dosage instructions'])
        }
    
    def _assess_effectiveness(self, drug_info: Dict[str, Any], profile: PatientProfile) -> str:
        """Assess the effectiveness of the medicine for the patient"""
        base_effectiveness = drug_info.get('effectiveness', 'moderate')
        
        # Adjust effectiveness based on patient factors
        if profile.age < 12 or profile.age > 65:
            # May be less effective in extreme ages
            if base_effectiveness == 'high':
                return 'moderate'
            elif base_effectiveness == 'moderate':
                return 'low'
        
        return base_effectiveness
    
    def _analyze_safety(self, medicines: List[MedicineRecommendation], profile: PatientProfile) -> SafetyAnalysis:
        """Analyze safety of recommended medicines"""
        if not medicines:
            return SafetyAnalysis(
                overall_risk=RiskLevel.LOW,
                contraindications=[],
                interactions=[],
                side_effects=[],
                monitoring_required=[],
                warnings=["No specific safety concerns"]
            )
        
        # Collect all safety information
        all_contraindications = []
        all_interactions = []
        all_side_effects = []
        all_monitoring = []
        all_warnings = []
        
        for medicine in medicines[:3]:  # Top 3 medicines
            drug_info = medicine.drug_info if hasattr(medicine, 'drug_info') else {}
            
            # Contraindications
            for contra in medicine.contraindications:
                condition_match = any(condition.lower() in contra.lower() for condition in profile.medical_conditions)
                if condition_match:
                    all_contraindications.append({
                        "medicine": medicine.drug_name,
                        "condition": contra,
                        "severity": "high"
                    })
            
            # Interactions
            for interaction in medicine.side_effects:  # Using side_effects as interactions placeholder
                med_match = any(med.lower() in interaction.lower() for med in profile.current_medications)
                if med_match:
                    all_interactions.append({
                        "medicine": medicine.drug_name,
                        "interacts_with": interaction,
                        "severity": "moderate"
                    })
            
            # Side effects
            for side_effect in medicine.side_effects[:5]:  # Top 5 side effects
                all_side_effects.append({
                    "medicine": medicine.drug_name,
                    "effect": side_effect,
                    "frequency": "common"
                })
        
        # Determine overall risk
        high_risk_count = sum(1 for med in medicines[:3] if med.risk_level == RiskLevel.HIGH)
        moderate_risk_count = sum(1 for med in medicines[:3] if med.risk_level == RiskLevel.MODERATE)
        
        if high_risk_count > 0:
            overall_risk = RiskLevel.HIGH
        elif moderate_risk_count > 1:
            overall_risk = RiskLevel.MODERATE
        else:
            overall_risk = RiskLevel.LOW
        
        return SafetyAnalysis(
            overall_risk=overall_risk,
            contraindications=all_contraindications,
            interactions=all_interactions,
            side_effects=all_side_effects,
            monitoring_required=all_monitoring,
            warnings=all_warnings
        )
    
    def _generate_treatment_plans(self, medicines: List[MedicineRecommendation], profile: PatientProfile) -> List[str]:
        """Generate treatment plans based on recommended medicines"""
        plans = []
        
        if not medicines:
            return ["Rest and monitor symptoms", "Stay hydrated", "Consult doctor if symptoms worsen"]
        
        top_medicine = medicines[0]
        
        # Basic treatment plan
        plans.append(f"Take {top_medicine.generic_name} as prescribed")
        plans.append("Monitor symptoms and response to treatment")
        
        if top_medicine.risk_level == RiskLevel.HIGH:
            plans.append("Seek medical attention immediately if side effects occur")
        
        if profile.age < 12:
            plans.append("Monitor for pediatric-specific side effects")
        
        if profile.pregnancy:
            plans.append("Consult obstetrician before continuing treatment")
        
        plans.append("Follow up with healthcare provider if symptoms persist beyond 3 days")
        
        return plans
    
    def _calculate_overall_confidence(self, medicines: List[MedicineRecommendation]) -> float:
        """Calculate overall confidence in recommendations"""
        if not medicines:
            return 0.0
        
        # Weight top recommendations more heavily
        weights = [0.5, 0.3, 0.2]  # Top 3 medicines
        total_confidence = 0.0
        
        for i, medicine in enumerate(medicines[:3]):
            weight = weights[i] if i < len(weights) else 0.1
            total_confidence += medicine.confidence * weight
        
        return total_confidence
    
    def _medicine_to_dict(self, medicine: MedicineRecommendation) -> Dict[str, Any]:
        """Convert MedicineRecommendation to dictionary"""
        return {
            "rank": medicine.rank,
            "drug_name": medicine.drug_name,
            "generic_name": medicine.generic_name,
            "brand_names": medicine.brand_names,
            "category": medicine.category.value,
            "confidence": medicine.confidence,
            "risk_level": medicine.risk_level.value,
            "dosage": medicine.dosage,
            "treatment_analysis": medicine.treatment_analysis,
            "effectiveness": medicine.effectiveness,
            "availability": medicine.availability,
            "price_range": medicine.price_range
        }
    
    def _safety_to_dict(self, safety: SafetyAnalysis) -> Dict[str, Any]:
        """Convert SafetyAnalysis to dictionary"""
        return {
            "overall_risk": safety.overall_risk.value,
            "contraindications": safety.contraindications,
            "interactions": safety.interactions,
            "side_effects": safety.side_effects,
            "monitoring_required": safety.monitoring_required,
            "warnings": safety.warnings
        }

# Global instance
medicine_engine = MedicineRecommendationEngine()
