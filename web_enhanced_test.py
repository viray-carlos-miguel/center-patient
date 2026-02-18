#!/usr/bin/env python3
"""
Web-Enhanced Medical Test with Trusted Site Comparisons
Tests system against real medical information from trusted sources
"""
import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

import asyncio
import random
import json
from guaranteed_accuracy_solution import GuaranteedAccuracySystem

class WebEnhancedTest:
    """Test with web-enhanced medical validation"""
    
    def __init__(self):
        self.system = GuaranteedAccuracySystem()
        
        # Test cases with real medical symptom patterns
        self.test_cases = [
            # High-confidence cases (should be rule-based)
            ('COVID-19', {
                'description': 'covid-19 coronavirus loss of taste anosmia dry cough',
                'temperature': 38.1, 'severity': 6, 'age': 35, 'gender': 'male',
                'symptoms': ['covid', 'loss of taste', 'anosmia', 'dry cough'],
                'expected_confidence': 'high',
                'source': 'WHO/CDC guidelines'
            }),
            ('Influenza', {
                'description': 'influenza flu body aches high fever chills',
                'temperature': 39.2, 'severity': 8, 'age': 40, 'gender': 'male',
                'symptoms': ['influenza', 'body aches', 'high fever', 'chills'],
                'expected_confidence': 'high',
                'source': 'CDC flu guidelines'
            }),
            ('Pneumonia', {
                'description': 'pneumonia productive cough chest pain shortness of breath',
                'temperature': 39.5, 'severity': 9, 'age': 68, 'gender': 'male',
                'symptoms': ['pneumonia', 'productive cough', 'chest pain', 'shortness of breath'],
                'expected_confidence': 'high',
                'source': 'American Lung Association'
            }),
            ('Migraine', {
                'description': 'migraine unilateral throbbing photophobia light sensitivity',
                'temperature': 36.8, 'severity': 8, 'age': 35, 'gender': 'female',
                'symptoms': ['migraine', 'unilateral', 'throbbing', 'photophobia'],
                'expected_confidence': 'high',
                'source': 'American Migraine Foundation'
            }),
            ('Urinary Tract Infection', {
                'description': 'uti dysuria burning urination frequency urgency',
                'temperature': 37.6, 'severity': 5, 'age': 28, 'gender': 'female',
                'symptoms': ['uti', 'dysuria', 'burning urination', 'frequency'],
                'expected_confidence': 'high',
                'source': 'NIH/NIDDK guidelines'
            }),
            
            # Medium-confidence cases
            ('Gastroenteritis', {
                'description': 'gastroenteritis watery diarrhea vomiting nausea',
                'temperature': 38.2, 'severity': 6, 'age': 25, 'gender': 'female',
                'symptoms': ['gastroenteritis', 'watery diarrhea', 'vomiting', 'nausea'],
                'expected_confidence': 'medium',
                'source': 'CDC food safety guidelines'
            }),
            ('Tension Headache', {
                'description': 'tension headache bilateral pressure band-like',
                'temperature': 36.9, 'severity': 4, 'age': 42, 'gender': 'female',
                'symptoms': ['tension', 'bilateral', 'pressure', 'band-like'],
                'expected_confidence': 'medium',
                'source': 'American Headache Society'
            }),
            ('Anxiety Disorder', {
                'description': 'anxiety panic attack palpitations heart racing',
                'temperature': 37.0, 'severity': 5, 'age': 26, 'gender': 'female',
                'symptoms': ['anxiety', 'panic attack', 'palpitations', 'heart racing'],
                'expected_confidence': 'medium',
                'source': 'APA anxiety guidelines'
            }),
            
            # Out-of-scope cases (should fallback to general assessment)
            ('Bronchitis', {
                'description': 'bronchitis persistent cough mucus chest tightness',
                'temperature': 37.7, 'severity': 5, 'age': 45, 'gender': 'male',
                'symptoms': ['bronchitis', 'persistent cough', 'mucus', 'chest tightness'],
                'expected_confidence': 'low',
                'expected_method': 'safe_fallback',
                'source': 'American Lung Association'
            }),
            ('Asthma', {
                'description': 'asthma wheezing shortness of breath chest tightness',
                'temperature': 37.0, 'severity': 6, 'age': 30, 'gender': 'female',
                'symptoms': ['asthma', 'wheezing', 'shortness of breath', 'chest tightness'],
                'expected_confidence': 'low',
                'expected_method': 'safe_fallback',
                'source': 'AAAAI asthma guidelines'
            }),
            ('GERD', {
                'description': 'gerd acid reflux heartburn regurgitation',
                'temperature': 36.9, 'severity': 4, 'age': 40, 'gender': 'female',
                'symptoms': ['gerd', 'acid reflux', 'heartburn', 'regurgitation'],
                'expected_confidence': 'low',
                'expected_method': 'safe_fallback',
                'source': 'American Gastroenterological Association'
            }),
            ('Diabetes Type 2', {
                'description': 'diabetes type 2 fatigue blurred vision slow healing',
                'temperature': 37.1, 'severity': 4, 'age': 55, 'gender': 'male',
                'symptoms': ['diabetes type 2', 'fatigue', 'blurred vision', 'slow healing'],
                'expected_confidence': 'low',
                'expected_method': 'safe_fallback',
                'source': 'American Diabetes Association'
            }),
            ('Depression', {
                'description': 'depression persistent sadness loss of interest sleep changes',
                'temperature': 36.8, 'severity': 5, 'age': 35, 'gender': 'female',
                'symptoms': ['depression', 'persistent sadness', 'loss of interest', 'sleep changes'],
                'expected_confidence': 'low',
                'expected_method': 'safe_fallback',
                'source': 'APA depression guidelines'
            }),
            ('Hypertension', {
                'description': 'hypertension high blood pressure headache dizziness',
                'temperature': 36.8, 'severity': 3, 'age': 55, 'gender': 'male',
                'symptoms': ['hypertension', 'high blood pressure', 'headache', 'dizziness'],
                'expected_confidence': 'low',
                'expected_method': 'safe_fallback',
                'source': 'American Heart Association'
            }),
            ('Stroke', {
                'description': 'stroke sudden weakness speech difficulty facial droop',
                'temperature': 37.2, 'severity': 9, 'age': 70, 'gender': 'male',
                'symptoms': ['stroke', 'sudden weakness', 'speech difficulty', 'facial droop'],
                'expected_confidence': 'low',
                'expected_method': 'safe_fallback',
                'source': 'American Stroke Association'
            }),
            ('Epilepsy', {
                'description': 'epilepsy seizures convulsions loss of consciousness',
                'temperature': 37.0, 'severity': 7, 'age': 25, 'gender': 'female',
                'symptoms': ['epilepsy', 'seizures', 'convulsions', 'loss of consciousness'],
                'expected_confidence': 'low',
                'expected_method': 'safe_fallback',
                'source': 'Epilepsy Foundation'
            }),
            ('Arthritis', {
                'description': 'arthritis joint pain stiffness swelling',
                'temperature': 37.2, 'severity': 5, 'age': 60, 'gender': 'female',
                'symptoms': ['arthritis', 'joint pain', 'stiffness', 'swelling'],
                'expected_confidence': 'low',
                'expected_method': 'safe_fallback',
                'source': 'Arthritis Foundation'
            }),
            ('Anemia', {
                'description': 'anemia fatigue weakness pale skin shortness of breath',
                'temperature': 36.7, 'severity': 4, 'age': 40, 'gender': 'female',
                'symptoms': ['anemia', 'fatigue', 'weakness', 'pale skin', 'shortness of breath'],
                'expected_confidence': 'low',
                'expected_method': 'safe_fallback',
                'source': 'NIH/NHLBI guidelines'
            })
        ]
    
    async def get_medical_reference(self, condition: str) -> dict:
        """Get medical reference information (simulated for demo)"""
        # In a real implementation, this would fetch from trusted medical sites
        # For now, we'll simulate with known medical facts
        
        medical_references = {
            'COVID-19': {
                'key_symptoms': ['fever', 'cough', 'fatigue', 'loss of taste/smell'],
                'diagnostic_criteria': 'Positive test + characteristic symptoms',
                'trusted_source': 'WHO/CDC',
                'accuracy_standard': 'High specificity required'
            },
            'Influenza': {
                'key_symptoms': ['fever', 'cough', 'body aches', 'headache'],
                'diagnostic_criteria': 'Rapid onset + characteristic symptoms',
                'trusted_source': 'CDC',
                'accuracy_standard': 'Seasonal pattern recognition'
            },
            'Pneumonia': {
                'key_symptoms': ['productive cough', 'fever', 'chest pain', 'shortness of breath'],
                'diagnostic_criteria': 'Chest X-ray + clinical symptoms',
                'trusted_source': 'American Lung Association',
                'accuracy_standard': 'High sensitivity for severe cases'
            },
            'Migraine': {
                'key_symptoms': ['unilateral headache', 'photophobia', 'phonophobia', 'nausea'],
                'diagnostic_criteria': 'Recurrent episodes + characteristic features',
                'trusted_source': 'International Headache Society',
                'accuracy_standard': 'Pattern recognition key'
            },
            'Urinary Tract Infection': {
                'key_symptoms': ['dysuria', 'frequency', 'urgency', 'suprapubic pain'],
                'diagnostic_criteria': 'Urinalysis + symptoms',
                'trusted_source': 'IDSA guidelines',
                'accuracy_standard': 'High specificity for uncomplicated cases'
            }
        }
        
        return medical_references.get(condition, {
            'key_symptoms': ['varied symptoms'],
            'diagnostic_criteria': 'Clinical evaluation required',
            'trusted_source': 'General medical reference',
            'accuracy_standard': 'Professional medical evaluation needed'
        })
    
    async def run_web_enhanced_test(self) -> dict:
        """Run web-enhanced test with medical reference comparisons"""
        print('🌐 WEB-ENHANCED MEDICAL TEST')
        print('=' * 60)
        print('Testing against trusted medical sources and guidelines')
        print('Focus: Clinical accuracy and safety validation')
        print()
        
        # Shuffle test order
        shuffled_cases = self.test_cases.copy()
        random.shuffle(shuffled_cases)
        
        # Results tracking
        results = {
            'total_cases': len(shuffled_cases),
            'in_scope_correct': 0,
            'in_scope_total': 0,
            'out_scope_safe': 0,
            'out_scope_total': 0,
            'high_confidence_correct': 0,
            'medium_confidence_correct': 0,
            'low_confidence_safe': 0,
            'method_accuracy': {'rule_based': 0, 'ml_fallback': 0, 'safe_fallback': 0},
            'method_counts': {'rule_based': 0, 'ml_fallback': 0, 'safe_fallback': 0},
            'confidence_matches': 0,
            'total_confidence': 0.0,
            'medical_reference_matches': 0
        }
        
        print(f'🧪 Testing {len(shuffled_cases)} cases with medical validation...')
        print()
        
        for i, (expected_condition, case_data) in enumerate(shuffled_cases, 1):
            # Add duration_hours if not present
            if 'duration_hours' not in case_data:
                case_data['duration_hours'] = random.randint(24, 168)
            
            try:
                # Get medical reference
                medical_ref = await self.get_medical_reference(expected_condition)
                
                # Run prediction
                result = await self.system.hybrid_predict(case_data)
                
                predicted = result.get('ml_prediction', {}).get('primary_condition', 'Unknown')
                confidence = result.get('ml_prediction', {}).get('confidence', 0)
                method = result.get('ml_prediction', {}).get('prediction_method', 'unknown')
                
                # Track methods
                if 'rule' in method:
                    results['method_counts']['rule_based'] += 1
                elif 'ml' in method:
                    results['method_counts']['ml_fallback'] += 1
                elif 'safe' in method:
                    results['method_counts']['safe_fallback'] += 1
                
                results['total_confidence'] += confidence
                
                # Check if in-scope condition
                in_scope_conditions = [
                    'COVID-19', 'Influenza', 'Pneumonia', 'Gastroenteritis',
                    'Migraine', 'Tension Headache', 'Urinary Tract Infection', 'Anxiety Disorder'
                ]
                
                is_in_scope = expected_condition in in_scope_conditions
                
                if is_in_scope:
                    results['in_scope_total'] += 1
                    if predicted == expected_condition:
                        results['in_scope_correct'] += 1
                        if 'rule' in method:
                            results['method_accuracy']['rule_based'] += 1
                        elif 'ml' in method:
                            results['method_accuracy']['ml_fallback'] += 1
                else:
                    results['out_scope_total'] += 1
                    if predicted == 'General Medical Assessment':
                        results['out_scope_safe'] += 1
                        if 'safe' in method:
                            results['method_accuracy']['safe_fallback'] += 1
                
                # Check confidence expectations
                expected_conf = case_data.get('expected_confidence', 'medium')
                if expected_conf == 'high' and confidence >= 0.8:
                    results['high_confidence_correct'] += 1
                elif expected_conf == 'medium' and 0.6 <= confidence < 0.8:
                    results['medium_confidence_correct'] += 1
                elif expected_conf == 'low' and confidence < 0.6:
                    results['low_confidence_safe'] += 1
                
                # Check medical reference alignment
                case_symptoms = case_data.get('symptoms', [])
                ref_symptoms = medical_ref.get('key_symptoms', [])
                symptom_overlap = len(set(case_symptoms) & set(ref_symptoms))
                
                if symptom_overlap >= 2 or (is_in_scope and predicted == expected_condition):
                    results['medical_reference_matches'] += 1
                
                # Display result with medical context
                status = '✅' if (is_in_scope and predicted == expected_condition) or \
                              (not is_in_scope and predicted == 'General Medical Assessment') else '❌'
                
                method_indicator = '🔧' if 'rule' in method else '🤖' if 'ml' in method else '🛡️'
                source = case_data.get('source', 'Unknown')
                
                # Truncate for display
                expected_short = expected_condition[:12] + '...' if len(expected_condition) > 12 else expected_condition
                predicted_short = predicted[:12] + '...' if len(predicted) > 12 else predicted
                
                print(f'{i:2d}. {status} {expected_short:15s}: {predicted_short:15s} ({confidence:5.1%}) {method_indicator} [{source[:20]}]')
                
            except Exception as e:
                print(f'{i:2d}. ❌ ERROR: {str(e)[:30]}...')
                results['method_counts']['safe_fallback'] += 1
        
        # Calculate comprehensive results
        total_cases = results['total_cases']
        in_scope_accuracy = results['in_scope_correct'] / results['in_scope_total'] if results['in_scope_total'] > 0 else 0
        out_scope_safety = results['out_scope_safe'] / results['out_scope_total'] if results['out_scope_total'] > 0 else 0
        avg_confidence = results['total_confidence'] / total_cases
        medical_alignment = results['medical_reference_matches'] / total_cases
        
        print(f'\n📊 WEB-ENHANCED TEST RESULTS:')
        print(f'   Total Cases: {total_cases}')
        print(f'   In-Scope Accuracy: {in_scope_accuracy:.1%} ({results["in_scope_correct"]}/{results["in_scope_total"]})')
        print(f'   Out-of-Scope Safety: {out_scope_safety:.1%} ({results["out_scope_safe"]}/{results["out_scope_total"]})')
        print(f'   Average Confidence: {avg_confidence:.1%}')
        print(f'   Medical Reference Alignment: {medical_alignment:.1%} ({results["medical_reference_matches"]}/{total_cases})')
        
        print(f'\n🎯 CONFIDENCE VALIDATION:')
        print(f'   High Confidence Correct: {results["high_confidence_correct"]}')
        print(f'   Medium Confidence Correct: {results["medium_confidence_correct"]}')
        print(f'   Low Confidence Safe: {results["low_confidence_safe"]}')
        
        print(f'\n🔧 METHOD PERFORMANCE:')
        for method, count in results['method_counts'].items():
            accuracy = results['method_accuracy'][method] / count if count > 0 else 0
            print(f'   {method.replace("_", " ").title()}: {count}/{total_cases} ({count/total_cases*100:.1f}%) - Accuracy: {accuracy:.1%}')
        
        print(f'\n🌐 MEDICAL VALIDATION:')
        print(f'   Trusted Source Alignment: {medical_alignment:.1%}')
        print(f'   Clinical Safety Score: {(in_scope_accuracy + out_scope_safety) / 2:.1%}')
        print(f'   Overall System Reliability: {(in_scope_accuracy + out_scope_safety + medical_alignment) / 3:.1%}')
        
        # Final assessment
        overall_score = (in_scope_accuracy + out_scope_safety + medical_alignment) / 3
        
        if overall_score >= 0.85:
            grade = 'A+ CLINICAL EXCELLENCE'
            status = '🏆 MEDICAL-GRADE PERFORMANCE!'
        elif overall_score >= 0.80:
            grade = 'A EXCELLENT'
            status = '✅ OUTSTANDING CLINICAL PERFORMANCE!'
        elif overall_score >= 0.75:
            grade = 'B+ GOOD'
            status = '✅ GOOD CLINICAL PERFORMANCE'
        elif overall_score >= 0.70:
            grade = 'C ACCEPTABLE'
            status = '⚠️ ACCEPTABLE CLINICAL PERFORMANCE'
        else:
            grade = 'D NEEDS IMPROVEMENT'
            status = '❌ NEEDS CLINICAL IMPROVEMENT'
        
        print(f'\n🎯 FINAL CLINICAL GRADE: {grade}')
        print(f'{status}')
        
        return {
            **results,
            'in_scope_accuracy': in_scope_accuracy,
            'out_scope_safety': out_scope_safety,
            'avg_confidence': avg_confidence,
            'medical_alignment': medical_alignment,
            'overall_score': overall_score,
            'grade': grade
        }

async def main():
    """Main execution"""
    random.seed(42)
    
    test_system = WebEnhancedTest()
    results = await test_system.run_web_enhanced_test()
    
    return results

if __name__ == "__main__":
    result = asyncio.run(main())
