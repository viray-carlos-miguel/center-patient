"""
Drug Database for Philippine Context
Comprehensive drug information for medicine recommendations
"""

from typing import Dict, List, Any, Optional
from datetime import datetime

class DrugDatabase:
    def __init__(self):
        self.drugs = self._initialize_drugs()
    
    def _initialize_drugs(self) -> Dict[str, Dict[str, Any]]:
        """Initialize drug database with Philippine context"""
        return {
            "paracetamol": {
                "generic_name": "Paracetamol",
                "brand_names": ["Tylenol", "Biogesic", "Calpol", "Tempra", "Febrinil"],
                "category": "over_the_counter",
                "indications": ["fever", "headache", "muscle pain", "mild to moderate pain"],
                "dosage": {
                    "adult": "500-1000mg every 4-6 hours",
                    "child": "10-15mg/kg every 4-6 hours",
                    "max_daily": "4000mg",
                    "type": "oral"
                },
                "side_effects": ["rare allergic reactions", "liver toxicity with overdose"],
                "contraindications": ["severe liver disease", "alcoholism"],
                "interactions": ["warfarin", "isoniazid", "alcohol"],
                "precautions": ["avoid alcohol", "monitor liver function"],
                "pregnancy_safe": True,
                "breastfeeding_safe": True,
                "pediatric_safe": True,
                "geriatric_safe": True,
                "effectiveness": "high",
                "treatment_duration": "3-7 days",
                "usage_instructions": ["Take with food", "Do not exceed recommended dose"],
                "availability": "widely_available",
                "price_range": "₱5-50",
                "allergens": ["paracetamol"]
            },
            
            "ibuprofen": {
                "generic_name": "Ibuprofen",
                "brand_names": ["Advil", "Motrin", "Alaxan", "Medifen", "Ibufen"],
                "category": "over_the_counter",
                "indications": ["fever", "inflammation", "moderate to severe pain", "menstrual cramps"],
                "dosage": {
                    "adult": "200-400mg every 4-6 hours",
                    "child": "5-10mg/kg every 6-8 hours",
                    "max_daily": "1200mg",
                    "type": "oral"
                },
                "side_effects": ["stomach upset", "gastric ulcers", "kidney problems", "increased bleeding risk"],
                "contraindications": ["peptic ulcer disease", "kidney disease", "bleeding disorders"],
                "interactions": ["aspirin", "warfarin", "ACE inhibitors", "diuretics"],
                "precautions": ["take with food", "avoid alcohol", "monitor kidney function"],
                "pregnancy_safe": False,
                "breastfeeding_safe": True,
                "pediatric_safe": True,
                "geriatric_safe": True,
                "effectiveness": "high",
                "treatment_duration": "3-7 days",
                "usage_instructions": ["Take with food", "Do not exceed recommended dose"],
                "availability": "widely_available",
                "price_range": "₱10-80",
                "allergens": ["ibuprofen", "NSAIDs"]
            },
            
            "amoxicillin": {
                "generic_name": "Amoxicillin",
                "brand_names": ["Amoxil", "Augmentin", "Moxiforce", "Cipmox", "Amoxycillin"],
                "category": "prescription",
                "indications": ["bacterial infections", "respiratory infections", "urinary tract infections"],
                "dosage": {
                    "adult": "250-500mg every 8 hours",
                    "child": "20-50mg/kg/day divided every 8 hours",
                    "max_daily": "3000mg",
                    "type": "oral"
                },
                "side_effects": ["diarrhea", "nausea", "allergic reactions", "yeast infections"],
                "contraindications": ["penicillin allergy", "mononucleosis"],
                "interactions": ["allopurinol", "methotrexate", "warfarin"],
                "precautions": ["complete full course", "monitor for allergic reactions"],
                "pregnancy_safe": True,
                "breastfeeding_safe": True,
                "pediatric_safe": True,
                "geriatric_safe": True,
                "effectiveness": "high",
                "treatment_duration": "7-14 days",
                "usage_instructions": ["Complete full course", "Take with or without food"],
                "availability": "prescription_required",
                "price_range": "₱50-200",
                "allergens": ["penicillin", "amoxicillin"]
            },
            
            "cetirizine": {
                "generic_name": "Cetirizine",
                "brand_names": ["Zyrtec", "Allertec", "Virlix", "Cetiriz", "Reactine"],
                "category": "over_the_counter",
                "indications": ["allergic rhinitis", "hives", "seasonal allergies", "itching"],
                "dosage": {
                    "adult": "10mg once daily",
                    "child": "5mg once daily (6+ years)",
                    "max_daily": "10mg",
                    "type": "oral"
                },
                "side_effects": ["drowsiness", "dry mouth", "headache", "fatigue"],
                "contraindications": ["severe kidney disease"],
                "interactions": ["alcohol", "sedatives", "other antihistamines"],
                "precautions": ["avoid driving", "avoid alcohol", "take at bedtime if drowsy"],
                "pregnancy_safe": True,
                "breastfeeding_safe": True,
                "pediatric_safe": True,
                "geriatric_safe": True,
                "effectiveness": "high",
                "treatment_duration": "as needed",
                "usage_instructions": ["Can be taken with or without food", "May cause drowsiness"],
                "availability": "widely_available",
                "price_range": "₱15-60",
                "allergens": ["cetirizine", "antihistamines"]
            },
            
            "losartan": {
                "generic_name": "Losartan",
                "brand_names": ["Cozaar", "Losar", "Xartan", "Lopressor", "Losacar"],
                "category": "prescription",
                "indications": ["high blood pressure", "heart failure", "diabetic kidney disease"],
                "dosage": {
                    "adult": "25-50mg once daily",
                    "child": "0.7mg/kg once daily (6+ years)",
                    "max_daily": "100mg",
                    "type": "oral"
                },
                "side_effects": ["dizziness", "hyperkalemia", "kidney problems", "angioedema"],
                "contraindications": ["pregnancy", "severe kidney disease", "bilateral renal artery stenosis"],
                "interactions": ["potassium supplements", "NSAIDs", "diuretics"],
                "precautions": ["monitor blood pressure", "monitor potassium levels"],
                "pregnancy_safe": False,
                "breastfeeding_safe": False,
                "pediatric_safe": True,
                "geriatric_safe": True,
                "effectiveness": "high",
                "treatment_duration": "long-term",
                "usage_instructions": ["Take consistently", "Do not stop abruptly"],
                "availability": "prescription_required",
                "price_range": "₱30-150",
                "allergens": ["losartan", "ARBs"]
            },
            
            "metformin": {
                "generic_name": "Metformin",
                "brand_names": ["Glucophage", "Formet", "Diabex", "Metforal", "Glycomet"],
                "category": "prescription",
                "indications": ["type 2 diabetes", "prediabetes", "PCOS"],
                "dosage": {
                    "adult": "500mg twice daily",
                    "child": "500mg once daily (10+ years)",
                    "max_daily": "2550mg",
                    "type": "oral"
                },
                "side_effects": ["gastrointestinal upset", "lactic acidosis", "vitamin B12 deficiency"],
                "contraindications": ["severe kidney disease", "liver disease", "heart failure"],
                "interactions": ["contrast dye", "alcohol", "diuretics"],
                "precautions": ["take with food", "monitor kidney function", "avoid alcohol"],
                "pregnancy_safe": True,
                "breastfeeding_safe": True,
                "pediatric_safe": True,
                "geriatric_safe": True,
                "effectiveness": "high",
                "treatment_duration": "long-term",
                "usage_instructions": ["Take with meals", "Consistent timing important"],
                "availability": "prescription_required",
                "price_range": "₱20-80",
                "allergens": ["metformin"]
            },
            
            "omeprazole": {
                "generic_name": "Omeprazole",
                "brand_names": ["Prilosec", "Losec", "Omez", "Omeprad", "Protocid"],
                "category": "over_the_counter",
                "indications": ["GERD", "stomach ulcers", "heartburn", "acid reflux"],
                "dosage": {
                    "adult": "20mg once daily",
                    "child": "10mg once daily (2+ years)",
                    "max_daily": "40mg",
                    "type": "oral"
                },
                "side_effects": ["headache", "diarrhea", "vitamin B12 deficiency", "bone fractures"],
                "contraindications": ["rare allergic reactions"],
                "interactions": ["clopidogrel", "ketoconazole", "iron supplements"],
                "precautions": ["long-term use risks", "monitor for side effects"],
                "pregnancy_safe": True,
                "breastfeeding_safe": True,
                "pediatric_safe": True,
                "geriatric_safe": True,
                "effectiveness": "high",
                "treatment_duration": "2-8 weeks",
                "usage_instructions": ["Take before meals", "Swallow whole, do not crush"],
                "availability": "widely_available",
                "price_range": "₱25-100",
                "allergens": ["omeprazole", "PPIs"]
            },
            
            "salbutamol": {
                "generic_name": "Salbutamol",
                "brand_names": ["Ventolin", "Aerolin", "Asmalin", "Salbuvent", "ProAir"],
                "category": "prescription",
                "indications": ["asthma", "COPD", "bronchospasm", "breathing difficulties"],
                "dosage": {
                    "adult": "2-4 puffs every 4-6 hours as needed",
                    "child": "1-2 puffs every 4-6 hours as needed",
                    "max_daily": "12 puffs",
                    "type": "inhaler"
                },
                "side_effects": ["tremors", "increased heart rate", "nervousness", "headache"],
                "contraindications": ["rare severe allergic reactions"],
                "interactions": ["beta blockers", "diuretics", "theophylline"],
                "precautions": ["use sparingly", "monitor heart rate", "clean inhaler regularly"],
                "pregnancy_safe": True,
                "breastfeeding_safe": True,
                "pediatric_safe": True,
                "geriatric_safe": True,
                "effectiveness": "high",
                "treatment_duration": "as needed",
                "usage_instructions": ["Shake well before use", "Rinse mouth after use"],
                "availability": "prescription_required",
                "price_range": "₱100-300",
                "allergens": ["salbutamol", "albuterol"]
            }
        }
    
    def get_drug_by_name(self, drug_name: str) -> Optional[Dict[str, Any]]:
        """Get drug information by name"""
        return self.drugs.get(drug_name.lower())
    
    def search_drugs_by_indication(self, indication: str) -> List[Dict[str, Any]]:
        """Search drugs by indication"""
        results = []
        indication_lower = indication.lower()
        
        for drug_name, drug_info in self.drugs.items():
            for ind in drug_info.get('indications', []):
                if indication_lower in ind.lower() or ind.lower() in indication_lower:
                    results.append(drug_info)
                    break
        
        return results
    
    def get_side_effects(self, drug_name: str) -> List[str]:
        """Get side effects for a drug"""
        drug = self.get_drug_by_name(drug_name)
        return drug.get('side_effects', []) if drug else []
    
    def get_drug_interactions(self, drug_name: str) -> List[str]:
        """Get drug interactions for a drug"""
        drug = self.get_drug_by_name(drug_name)
        return drug.get('interactions', []) if drug else []
    
    def get_contraindications(self, drug_name: str) -> List[str]:
        """Get contraindications for a drug"""
        drug = self.get_drug_by_name(drug_name)
        return drug.get('contraindications', []) if drug else []
    
    def is_safe_for_pregnancy(self, drug_name: str) -> bool:
        """Check if drug is safe for pregnancy"""
        drug = self.get_drug_by_name(drug_name)
        return drug.get('pregnancy_safe', False) if drug else False
    
    def is_safe_for_breastfeeding(self, drug_name: str) -> bool:
        """Check if drug is safe for breastfeeding"""
        drug = self.get_drug_by_name(drug_name)
        return drug.get('breastfeeding_safe', False) if drug else False
    
    def is_safe_for_pediatrics(self, drug_name: str) -> bool:
        """Check if drug is safe for children"""
        drug = self.get_drug_by_name(drug_name)
        return drug.get('pediatric_safe', False) if drug else False
    
    def is_safe_for_geriatrics(self, drug_name: str) -> bool:
        """Check if drug is safe for elderly"""
        drug = self.get_drug_by_name(drug_name)
        return drug.get('geriatric_safe', False) if drug else False

# Global instance
drug_db = DrugDatabase()
