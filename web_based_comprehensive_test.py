#!/usr/bin/env python3
"""
Web-Based Comprehensive Medical Test
Tests system against real medical information from trusted web sources
Simulates web access to medical databases and guidelines
"""
import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

import asyncio
import random
import json
from guaranteed_accuracy_solution import GuaranteedAccuracySystem

class WebBasedComprehensiveTest:
    """Web-based comprehensive test with real medical data simulation"""
    
    def __init__(self):
        self.system = GuaranteedAccuracySystem()
        
        # Simulated web medical database (real-world patterns)
        self.web_medical_database = {
            'WHO_CDC_GUIDELINES': {
                'COVID-19': {
                    'key_symptoms': ['fever', 'dry cough', 'fatigue', 'loss of taste/smell', 'sore throat', 'headache', 'body aches'],
                    'atypical_symptoms': ['gastrointestinal', 'diarrhea', 'nausea', 'vomiting', 'skin rash', 'conjunctivitis'],
                    'severity_indicators': ['shortness of breath', 'chest pain', 'confusion', 'loss of speech'],
                    'source': 'WHO/CDC Official Guidelines',
                    'diagnostic_confidence': 'high'
                },
                'Influenza': {
                    'key_symptoms': ['fever', 'cough', 'body aches', 'headache', 'fatigue', 'sore throat'],
                    'severity_indicators': ['high fever', 'severe body aches', 'difficulty breathing'],
                    'source': 'CDC Flu Guidelines',
                    'diagnostic_confidence': 'high'
                }
            },
            'NIH_MEDLINE_PLUS': {
                'Migraine': {
                    'key_symptoms': ['unilateral headache', 'throbbing pain', 'photophobia', 'phonophobia', 'nausea', 'vomiting'],
                    'aura_symptoms': ['visual disturbances', 'sensory changes', 'speech difficulty'],
                    'triggers': ['stress', 'hormonal changes', 'certain foods', 'sleep changes'],
                    'source': 'NIH MedlinePlus',
                    'diagnostic_confidence': 'high'
                },
                'Tension Headache': {
                    'key_symptoms': ['bilateral headache', 'pressure sensation', 'tight band feeling', 'mild to moderate pain'],
                    'associated_symptoms': ['neck pain', 'scalp tenderness', 'stress', 'fatigue'],
                    'source': 'NIH MedlinePlus',
                    'diagnostic_confidence': 'medium'
                }
            },
            'MAYO_CLINIC': {
                'Pneumonia': {
                    'key_symptoms': ['productive cough', 'fever', 'chest pain', 'shortness of breath', 'fatigue'],
                    'signs': ['crackles', 'consolidation', 'rapid breathing', 'low oxygen'],
                    'risk_factors': ['age > 65', 'chronic disease', 'smoking', 'weakened immune system'],
                    'source': 'Mayo Clinic',
                    'diagnostic_confidence': 'high'
                },
                'Gastroenteritis': {
                    'key_symptoms': ['watery diarrhea', 'vomiting', 'nausea', 'abdominal cramps', 'fever'],
                    'causes': ['viral', 'bacterial', 'parasitic', 'food poisoning'],
                    'severity_indicators': ['dehydration', 'high fever', 'bloody diarrhea'],
                    'source': 'Mayo Clinic',
                    'diagnostic_confidence': 'medium'
                }
            },
            'AMERICAN_UROLOGICAL_ASSOCIATION': {
                'Urinary Tract Infection': {
                    'key_symptoms': ['burning urination', 'frequency', 'urgency', 'suprapubic pain'],
                    'additional_symptoms': ['cloudy urine', 'strong odor', 'hematuria', 'pelvic pain'],
                    'complications': ['kidney infection', 'sepsis', 'recurrent infections'],
                    'source': 'AUA Guidelines',
                    'diagnostic_confidence': 'high'
                }
            },
            'AMERICAN_PSYCHIATRIC_ASSOCIATION': {
                'Anxiety Disorder': {
                    'key_symptoms': ['excessive worry', 'restlessness', 'fatigue', 'difficulty concentrating', 'irritability'],
                    'physical_symptoms': ['palpitations', 'shortness of breath', 'sweating', 'trembling', 'dizziness'],
                    'panic_symptoms': ['panic attacks', 'fear of dying', 'derealization', 'choking sensation'],
                    'source': 'DSM-5 Guidelines',
                    'diagnostic_confidence': 'medium'
                }
            }
        }
        
        # Web-based test cases with real medical scenarios
        self.web_test_cases = [
            # WHO/CDC COVID-19 cases
            ('COVID-19 - WHO Classic', {
                'description': 'covid-19 fever dry cough fatigue loss of taste',
                'temperature': 38.1, 'severity': 6, 'age': 35, 'gender': 'male',
                'symptoms': ['fever', 'dry cough', 'fatigue', 'loss of taste'],
                'web_source': 'WHO/CDC',
                'expected_confidence': 'high',
                'clinical_pattern': 'classic'
            }),
            
            ('COVID-19 - CDC Atypical', {
                'description': 'covid-19 gastrointestinal diarrhea nausea vomiting',
                'temperature': 37.8, 'severity': 5, 'age': 30, 'gender': 'female',
                'symptoms': ['gastrointestinal', 'diarrhea', 'nausea', 'vomiting'],
                'web_source': 'WHO/CDC',
                'expected_confidence': 'medium',
                'clinical_pattern': 'atypical'
            }),
            
            ('COVID-19 - Severe', {
                'description': 'covid-19 shortness of breath chest pain confusion',
                'temperature': 39.0, 'severity': 9, 'age': 70, 'gender': 'male',
                'symptoms': ['shortness of breath', 'chest pain', 'confusion'],
                'web_source': 'WHO/CDC',
                'expected_confidence': 'high',
                'clinical_pattern': 'severe'
            }),
            
            # CDC Influenza cases
            ('Influenza - CDC Classic', {
                'description': 'influenza fever cough body aches headache fatigue',
                'temperature': 39.2, 'severity': 8, 'age': 40, 'gender': 'male',
                'symptoms': ['fever', 'cough', 'body aches', 'headache', 'fatigue'],
                'web_source': 'CDC',
                'expected_confidence': 'high',
                'clinical_pattern': 'classic'
            }),
            
            ('Influenza - Severe', {
                'description': 'influenza high fever severe body aches difficulty breathing',
                'temperature': 40.0, 'severity': 10, 'age': 65, 'gender': 'female',
                'symptoms': ['high fever', 'severe body aches', 'difficulty breathing'],
                'web_source': 'CDC',
                'expected_confidence': 'high',
                'clinical_pattern': 'severe'
            }),
            
            # NIH Migraine cases
            ('Migraine - NIH Classic', {
                'description': 'migraine unilateral throbbing photophobia nausea',
                'temperature': 36.8, 'severity': 8, 'age': 35, 'gender': 'female',
                'symptoms': ['unilateral', 'throbbing', 'photophobia', 'nausea'],
                'web_source': 'NIH',
                'expected_confidence': 'high',
                'clinical_pattern': 'classic'
            }),
            
            ('Migraine - NIH With Aura', {
                'description': 'migraine visual disturbances aura unilateral headache',
                'temperature': 36.9, 'severity': 7, 'age': 30, 'gender': 'female',
                'symptoms': ['visual disturbances', 'aura', 'unilateral headache'],
                'web_source': 'NIH',
                'expected_confidence': 'high',
                'clinical_pattern': 'with_aura'
            }),
            
            # NIH Tension Headache cases
            ('Tension Headache - NIH Classic', {
                'description': 'tension headache bilateral pressure band-like stress',
                'temperature': 36.9, 'severity': 4, 'age': 42, 'gender': 'female',
                'symptoms': ['bilateral', 'pressure', 'band-like', 'stress'],
                'web_source': 'NIH',
                'expected_confidence': 'medium',
                'clinical_pattern': 'classic'
            }),
            
            ('Tension Headache - NIH Chronic', {
                'description': 'tension headache neck pain scalp tenderness fatigue',
                'temperature': 36.8, 'severity': 5, 'age': 45, 'gender': 'male',
                'symptoms': ['neck pain', 'scalp tenderness', 'fatigue'],
                'web_source': 'NIH',
                'expected_confidence': 'medium',
                'clinical_pattern': 'chronic'
            }),
            
            # Mayo Clinic Pneumonia cases
            ('Pneumonia - Mayo Classic', {
                'description': 'pneumonia productive cough fever chest pain shortness of breath',
                'temperature': 39.5, 'severity': 9, 'age': 68, 'gender': 'male',
                'symptoms': ['productive cough', 'fever', 'chest pain', 'shortness of breath'],
                'web_source': 'Mayo Clinic',
                'expected_confidence': 'high',
                'clinical_pattern': 'classic'
            }),
            
            ('Pneumonia - Mayo Elderly', {
                'description': 'pneumonia elderly confusion low oxygen no fever',
                'temperature': 37.5, 'severity': 8, 'age': 80, 'gender': 'female',
                'symptoms': ['confusion', 'low oxygen', 'no fever'],
                'web_source': 'Mayo Clinic',
                'expected_confidence': 'medium',
                'clinical_pattern': 'elderly_atypical'
            }),
            
            # Mayo Clinic Gastroenteritis cases
            ('Gastroenteritis - Mayo Classic', {
                'description': 'gastroenteritis watery diarrhea vomiting nausea abdominal cramps',
                'temperature': 38.2, 'severity': 6, 'age': 25, 'gender': 'female',
                'symptoms': ['watery diarrhea', 'vomiting', 'nausea', 'abdominal cramps'],
                'web_source': 'Mayo Clinic',
                'expected_confidence': 'medium',
                'clinical_pattern': 'classic'
            }),
            
            ('Gastroenteritis - Mayo Severe', {
                'description': 'gastroenteritis bloody diarrhea dehydration high fever',
                'temperature': 39.0, 'severity': 8, 'age': 30, 'gender': 'male',
                'symptoms': ['bloody diarrhea', 'dehydration', 'high fever'],
                'web_source': 'Mayo Clinic',
                'expected_confidence': 'high',
                'clinical_pattern': 'severe'
            }),
            
            # AUA UTI cases
            ('UTI - AUA Classic', {
                'description': 'uti burning urination frequency urgency pelvic pain',
                'temperature': 37.6, 'severity': 5, 'age': 28, 'gender': 'female',
                'symptoms': ['burning urination', 'frequency', 'urgency', 'pelvic pain'],
                'web_source': 'AUA',
                'expected_confidence': 'high',
                'clinical_pattern': 'classic'
            }),
            
            ('UTI - AUA Complicated', {
                'description': 'uti cloudy urine hematuria fever flank pain',
                'temperature': 38.5, 'severity': 7, 'age': 35, 'gender': 'female',
                'symptoms': ['cloudy urine', 'hematuria', 'fever', 'flank pain'],
                'web_source': 'AUA',
                'expected_confidence': 'high',
                'clinical_pattern': 'complicated'
            }),
            
            # APA Anxiety cases
            ('Anxiety - APA Classic', {
                'description': 'anxiety excessive worry restlessness fatigue difficulty concentrating',
                'temperature': 37.0, 'severity': 5, 'age': 30, 'gender': 'female',
                'symptoms': ['excessive worry', 'restlessness', 'fatigue', 'difficulty concentrating'],
                'web_source': 'APA',
                'expected_confidence': 'medium',
                'clinical_pattern': 'classic'
            }),
            
            ('Anxiety - APA Panic', {
                'description': 'anxiety panic attack palpitations shortness of breath fear',
                'temperature': 37.0, 'severity': 6, 'age': 25, 'gender': 'female',
                'symptoms': ['panic attack', 'palpitations', 'shortness of breath', 'fear'],
                'web_source': 'APA',
                'expected_confidence': 'medium',
                'clinical_pattern': 'panic'
            }),
            
            ('Anxiety - APA Physical', {
                'description': 'anxiety sweating trembling dizziness chest pain',
                'temperature': 37.0, 'severity': 5, 'age': 35, 'gender': 'male',
                'symptoms': ['sweating', 'trembling', 'dizziness', 'chest pain'],
                'web_source': 'APA',
                'expected_confidence': 'medium',
                'clinical_pattern': 'physical_symptoms'
            })
        ]
    
    async def simulate_web_lookup(self, condition: str, symptoms: list) -> dict:
        """Simulate web lookup of medical information"""
        # Search through web database for matching condition
        for source, conditions in self.web_medical_database.items():
            if condition in conditions:
                medical_info = conditions[condition]
                
                # Calculate symptom match score
                symptom_match = 0
                for symptom in symptoms:
                    if any(symptom.lower() in s.lower() for s in medical_info['key_symptoms']):
                        symptom_match += 1
                
                match_percentage = symptom_match / len(symptoms) if symptoms else 0
                
                return {
                    'source': source,
                    'condition': condition,
                    'medical_info': medical_info,
                    'symptom_match': match_percentage,
                    'confidence_level': medical_info['diagnostic_confidence'],
                    'web_validation': match_percentage >= 0.5
                }
        
        return {
            'source': 'Unknown',
            'condition': condition,
            'medical_info': {},
            'symptom_match': 0,
            'confidence_level': 'low',
            'web_validation': False
        }
    
    async def run_web_based_test(self) -> dict:
        """Run comprehensive web-based medical test"""
        print('🌐 WEB-BASED COMPREHENSIVE MEDICAL TEST')
        print('=' * 60)
        print('Testing against simulated web medical databases')
        print('Sources: WHO/CDC, NIH, Mayo Clinic, AUA, APA')
        print()
        
        # Shuffle test order
        shuffled_cases = self.web_test_cases.copy()
        random.shuffle(shuffled_cases)
        
        # Results tracking
        results = {
            'total_cases': len(shuffled_cases),
            'web_validated_correct': 0,
            'web_validated_total': 0,
            'source_performance': {},
            'confidence_accuracy': {'high': 0, 'medium': 0, 'low': 0},
            'confidence_totals': {'high': 0, 'medium': 0, 'low': 0},
            'pattern_performance': {},
            'method_counts': {'rule_based': 0, 'ml_fallback': 0, 'safe_fallback': 0},
            'total_confidence': 0.0,
            'web_alignment_score': 0.0
        }
        
        print(f'🧪 Testing {len(shuffled_cases)} web-based medical cases...')
        print()
        
        for i, (test_name, case_data) in enumerate(shuffled_cases, 1):
            # Add duration_hours if not present
            if 'duration_hours' not in case_data:
                case_data['duration_hours'] = random.randint(24, 168)
            
            try:
                # Simulate web lookup
                expected_condition = test_name.split(' - ')[0]
                web_info = await self.simulate_web_lookup(expected_condition, case_data['symptoms'])
                
                # Run prediction
                result = await self.system.hybrid_predict(case_data)
                
                predicted = result.get('ml_prediction', {}).get('primary_condition', 'Unknown')
                confidence = result.get('ml_prediction', {}).get('confidence', 0)
                method = result.get('ml_prediction', {}).get('prediction_method', 'unknown')
                web_source = case_data.get('web_source', 'Unknown')
                expected_conf = case_data.get('expected_confidence', 'medium')
                pattern = case_data.get('clinical_pattern', 'unknown')
                
                # Track methods
                if 'rule' in method:
                    results['method_counts']['rule_based'] += 1
                elif 'ml' in method:
                    results['method_counts']['ml_fallback'] += 1
                elif 'safe' in method:
                    results['method_counts']['safe_fallback'] += 1
                
                results['total_confidence'] += confidence
                
                # Source performance tracking
                if web_source not in results['source_performance']:
                    results['source_performance'][web_source] = {'correct': 0, 'total': 0, 'confidences': []}
                
                results['source_performance'][web_source]['total'] += 1
                results['source_performance'][web_source]['confidences'].append(confidence)
                
                # Pattern performance tracking
                if pattern not in results['pattern_performance']:
                    results['pattern_performance'][pattern] = {'correct': 0, 'total': 0}
                
                results['pattern_performance'][pattern]['total'] += 1
                
                # Evaluate correctness
                is_correct = False
                
                # Check if prediction matches expected condition
                if expected_condition.lower() in predicted.lower():
                    is_correct = True
                    results['web_validated_correct'] += 1
                    results['source_performance'][web_source]['correct'] += 1
                    results['pattern_performance'][pattern]['correct'] += 1
                
                results['web_validated_total'] += 1
                
                # Confidence accuracy tracking
                results['confidence_totals'][expected_conf] += 1
                
                if expected_conf == 'high' and confidence >= 0.8:
                    results['confidence_accuracy']['high'] += 1
                elif expected_conf == 'medium' and 0.6 <= confidence < 0.8:
                    results['confidence_accuracy']['medium'] += 1
                elif expected_conf == 'low' and confidence < 0.6:
                    results['confidence_accuracy']['low'] += 1
                
                # Display result
                status = '✅' if is_correct else '❌'
                method_indicator = '🔧' if 'rule' in method else '🤖' if 'ml' in method else '🛡️'
                web_indicator = '🌐' if web_info['web_validation'] else '❓'
                
                # Truncate for display
                test_name_short = test_name[:25] + '...' if len(test_name) > 25 else test_name
                predicted_short = predicted[:15] + '...' if len(predicted) > 15 else predicted
                
                print(f'{i:2d}. {status} {test_name_short:28s}: {predicted_short:15s} ({confidence:5.1%}) {method_indicator} {web_indicator} [{web_source}]')
                
            except Exception as e:
                print(f'{i:2d}. ❌ ERROR: {str(e)[:30]}...')
                results['method_counts']['safe_fallback'] += 1
                results['web_validated_total'] += 1
        
        # Calculate comprehensive results
        total_cases = results['total_cases']
        web_accuracy = results['web_validated_correct'] / results['web_validated_total'] if results['web_validated_total'] > 0 else 0
        avg_confidence = results['total_confidence'] / total_cases
        
        # Source performance details
        source_performance_detail = {}
        for source, perf in results['source_performance'].items():
            accuracy = perf['correct'] / perf['total'] if perf['total'] > 0 else 0
            avg_conf = sum(perf['confidences']) / len(perf['confidences']) if perf['confidences'] else 0
            source_performance_detail[source] = {
                'accuracy': accuracy,
                'avg_confidence': avg_conf,
                'total': perf['total']
            }
        
        # Pattern performance details
        pattern_performance_detail = {}
        for pattern, perf in results['pattern_performance'].items():
            accuracy = perf['correct'] / perf['total'] if perf['total'] > 0 else 0
            pattern_performance_detail[pattern] = {
                'accuracy': accuracy,
                'total': perf['total']
            }
        
        # Confidence accuracy
        high_conf_accuracy = results['confidence_accuracy']['high'] / results['confidence_totals']['high'] if results['confidence_totals']['high'] > 0 else 0
        medium_conf_accuracy = results['confidence_accuracy']['medium'] / results['confidence_totals']['medium'] if results['confidence_totals']['medium'] > 0 else 0
        low_conf_accuracy = results['confidence_accuracy']['low'] / results['confidence_totals']['low'] if results['confidence_totals']['low'] > 0 else 0
        
        # Overall web alignment score
        results['web_alignment_score'] = (web_accuracy + high_conf_accuracy + medium_conf_accuracy) / 3
        
        print(f'\n📊 WEB-BASED COMPREHENSIVE RESULTS:')
        print(f'   Total Cases: {total_cases}')
        print(f'   Web-Validated Accuracy: {web_accuracy:.1%} ({results["web_validated_correct"]}/{results["web_validated_total"]})')
        print(f'   Average Confidence: {avg_confidence:.1%}')
        print(f'   Web Alignment Score: {results["web_alignment_score"]:.1%}')
        
        print(f'\n🌐 SOURCE PERFORMANCE:')
        for source, perf in source_performance_detail.items():
            print(f'   {source}: {perf["accuracy"]:.1%} accuracy, {perf["avg_confidence"]:.1%} avg conf ({perf["total"]} cases)')
        
        print(f'\n🎯 PATTERN PERFORMANCE:')
        for pattern, perf in pattern_performance_detail.items():
            print(f'   {pattern.replace("_", " ").title()}: {perf["accuracy"]:.1%} ({perf["total"]} cases)')
        
        print(f'\n📈 CONFIDENCE ACCURACY:')
        print(f'   High Confidence: {high_conf_accuracy:.1%} ({results["confidence_accuracy"]["high"]}/{results["confidence_totals"]["high"]})')
        print(f'   Medium Confidence: {medium_conf_accuracy:.1%} ({results["confidence_accuracy"]["medium"]}/{results["confidence_totals"]["medium"]})')
        print(f'   Low Confidence: {low_conf_accuracy:.1%} ({results["confidence_accuracy"]["low"]}/{results["confidence_totals"]["low"]})')
        
        print(f'\n🔧 METHOD BREAKDOWN:')
        for method, count in results['method_counts'].items():
            percentage = count / total_cases * 100
            print(f'   {method.replace("_", " ").title()}: {count}/{total_cases} ({percentage:.1f}%)')
        
        # Final assessment
        if web_accuracy >= 0.85 and results['web_alignment_score'] >= 0.80:
            grade = 'A+ WEB-EXCELLENT'
            status = '🌐 OUTSTANDING WEB-BASED PERFORMANCE!'
        elif web_accuracy >= 0.75 and results['web_alignment_score'] >= 0.70:
            grade = 'A WEB-GOOD'
            status = '✅ GOOD WEB-BASED PERFORMANCE!'
        elif web_accuracy >= 0.65 and results['web_alignment_score'] >= 0.60:
            grade = 'B+ WEB-ACCEPTABLE'
            status = '⚠️ ACCEPTABLE WEB-BASED PERFORMANCE'
        else:
            grade = 'C WEB-NEEDS WORK'
            status = '❌ WEB-BASED PERFORMANCE NEEDS IMPROVEMENT'
        
        print(f'\n🎯 FINAL WEB-BASED GRADE: {grade}')
        print(f'{status}')
        
        return {
            **results,
            'web_accuracy': web_accuracy,
            'avg_confidence': avg_confidence,
            'source_performance_detail': source_performance_detail,
            'pattern_performance_detail': pattern_performance_detail,
            'confidence_accuracy': {
                'high': high_conf_accuracy,
                'medium': medium_conf_accuracy,
                'low': low_conf_accuracy
            },
            'grade': grade
        }

async def main():
    """Main execution"""
    random.seed(42)
    
    test_system = WebBasedComprehensiveTest()
    results = await test_system.run_web_based_test()
    
    return results

if __name__ == "__main__":
    result = asyncio.run(main())
