#!/usr/bin/env python3
"""
Fixed Web-Based Test - Addressing UTI Detection and Confidence Calibration
Tests improved system against web medical databases
"""
import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

import asyncio
import random
from guaranteed_accuracy_solution import GuaranteedAccuracySystem

class FixedWebTest:
    """Fixed web-based test with improved UTI detection and confidence calibration"""
    
    def __init__(self):
        self.system = GuaranteedAccuracySystem()
        
        # Focus on problematic areas from previous test
        self.improved_test_cases = [
            # Enhanced UTI cases (AUA guidelines)
            ('UTI - AUA Classic Enhanced', {
                'description': 'uti burning urination frequency urgency pelvic pain',
                'temperature': 37.6, 'severity': 5, 'age': 28, 'gender': 'female',
                'symptoms': ['burning urination', 'frequency', 'urgency', 'pelvic pain'],
                'web_source': 'AUA',
                'expected_confidence': 'high',
                'clinical_pattern': 'classic'
            }),
            
            ('UTI - AUA Complicated Enhanced', {
                'description': 'urinary tract infection cloudy urine hematuria fever flank pain',
                'temperature': 38.5, 'severity': 7, 'age': 35, 'gender': 'female',
                'symptoms': ['urinary tract infection', 'cloudy urine', 'hematuria', 'fever', 'flank pain'],
                'web_source': 'AUA',
                'expected_confidence': 'high',
                'clinical_pattern': 'complicated'
            }),
            
            ('UTI - AUA Dysuria Focus', {
                'description': 'uti dysuria burning sensation urination strong odor',
                'temperature': 37.8, 'severity': 6, 'age': 30, 'gender': 'female',
                'symptoms': ['uti', 'dysuria', 'burning sensation', 'strong odor'],
                'web_source': 'AUA',
                'expected_confidence': 'high',
                'clinical_pattern': 'dysuria'
            }),
            
            # Medium confidence calibration cases
            ('Gastroenteritis - Medium Calibration', {
                'description': 'gastroenteritis watery diarrhea vomiting mild abdominal cramps',
                'temperature': 37.8, 'severity': 5, 'age': 25, 'gender': 'female',
                'symptoms': ['watery diarrhea', 'vomiting', 'mild abdominal cramps'],
                'web_source': 'Mayo Clinic',
                'expected_confidence': 'medium',
                'clinical_pattern': 'moderate'
            }),
            
            ('Tension Headache - Medium Calibration', {
                'description': 'tension headache bilateral pressure mild stress',
                'temperature': 36.9, 'severity': 3, 'age': 35, 'gender': 'female',
                'symptoms': ['bilateral', 'pressure', 'mild', 'stress'],
                'web_source': 'NIH',
                'expected_confidence': 'medium',
                'clinical_pattern': 'mild'
            }),
            
            ('Anxiety - Medium Calibration', {
                'description': 'anxiety nervousness restlessness mild fatigue',
                'temperature': 37.0, 'severity': 4, 'age': 30, 'gender': 'female',
                'symptoms': ['nervousness', 'restlessness', 'mild fatigue'],
                'web_source': 'APA',
                'expected_confidence': 'medium',
                'clinical_pattern': 'mild'
            }),
            
            # High confidence cases (should remain high)
            ('COVID-19 - High Confidence', {
                'description': 'covid-19 loss of taste anosmia dry cough fever',
                'temperature': 38.1, 'severity': 6, 'age': 35, 'gender': 'male',
                'symptoms': ['loss of taste', 'anosmia', 'dry cough', 'fever'],
                'web_source': 'WHO/CDC',
                'expected_confidence': 'high',
                'clinical_pattern': 'classic'
            }),
            
            ('Influenza - High Confidence', {
                'description': 'influenza body aches high fever chills headache',
                'temperature': 39.2, 'severity': 8, 'age': 40, 'gender': 'male',
                'symptoms': ['body aches', 'high fever', 'chills', 'headache'],
                'web_source': 'CDC',
                'expected_confidence': 'high',
                'clinical_pattern': 'classic'
            }),
            
            ('Migraine - High Confidence', {
                'description': 'migraine unilateral throbbing photophobia nausea',
                'temperature': 36.8, 'severity': 8, 'age': 35, 'gender': 'female',
                'symptoms': ['unilateral', 'throbbing', 'photophobia', 'nausea'],
                'web_source': 'NIH',
                'expected_confidence': 'high',
                'clinical_pattern': 'classic'
            }),
            
            ('Pneumonia - High Confidence', {
                'description': 'pneumonia productive cough fever chest pain shortness of breath',
                'temperature': 39.5, 'severity': 9, 'age': 68, 'gender': 'male',
                'symptoms': ['productive cough', 'fever', 'chest pain', 'shortness of breath'],
                'web_source': 'Mayo Clinic',
                'expected_confidence': 'high',
                'clinical_pattern': 'classic'
            }),
            
            # Mixed confidence cases
            ('COVID-19 Atypical - Medium', {
                'description': 'covid-19 gastrointestinal diarrhea nausea no fever',
                'temperature': 37.5, 'severity': 5, 'age': 30, 'gender': 'female',
                'symptoms': ['gastrointestinal', 'diarrhea', 'nausea'],
                'web_source': 'WHO/CDC',
                'expected_confidence': 'medium',
                'clinical_pattern': 'atypical'
            }),
            
            ('Pneumonia Elderly - Medium', {
                'description': 'pneumonia elderly confusion mild fever shortness of breath',
                'temperature': 37.8, 'severity': 7, 'age': 80, 'gender': 'female',
                'symptoms': ['confusion', 'mild fever', 'shortness of breath'],
                'web_source': 'Mayo Clinic',
                'expected_confidence': 'medium',
                'clinical_pattern': 'elderly_atypical'
            })
        ]
    
    async def run_fixed_web_test(self) -> dict:
        """Run fixed web-based test with improvements"""
        print('🔧 FIXED WEB-BASED TEST')
        print('=' * 60)
        print('Testing improved UTI detection and confidence calibration')
        print('Focus: AUA guidelines alignment and medium confidence cases')
        print()
        
        # Shuffle test order
        shuffled_cases = self.improved_test_cases.copy()
        random.shuffle(shuffled_cases)
        
        # Results tracking
        results = {
            'total_cases': len(shuffled_cases),
            'uti_correct': 0,
            'uti_total': 0,
            'medium_conf_correct': 0,
            'medium_conf_total': 0,
            'high_conf_correct': 0,
            'high_conf_total': 0,
            'confidence_accuracy': {'high': 0, 'medium': 0, 'low': 0},
            'confidence_totals': {'high': 0, 'medium': 0, 'low': 0},
            'method_counts': {'rule_based': 0, 'ml_fallback': 0, 'safe_fallback': 0},
            'total_confidence': 0.0,
            'web_alignment_score': 0.0
        }
        
        print(f'🧪 Testing {len(shuffled_cases)} improved web cases...')
        print()
        
        for i, (test_name, case_data) in enumerate(shuffled_cases, 1):
            # Add duration_hours if not present
            if 'duration_hours' not in case_data:
                case_data['duration_hours'] = random.randint(24, 168)
            
            try:
                # Run prediction
                result = await self.system.hybrid_predict(case_data)
                
                predicted = result.get('ml_prediction', {}).get('primary_condition', 'Unknown')
                confidence = result.get('ml_prediction', {}).get('confidence', 0)
                method = result.get('ml_prediction', {}).get('prediction_method', 'unknown')
                expected_conf = case_data.get('expected_confidence', 'medium')
                web_source = case_data.get('web_source', 'Unknown')
                pattern = case_data.get('clinical_pattern', 'unknown')
                
                # Track methods
                if 'rule' in method:
                    results['method_counts']['rule_based'] += 1
                elif 'ml' in method:
                    results['method_counts']['ml_fallback'] += 1
                elif 'safe' in method:
                    results['method_counts']['safe_fallback'] += 1
                
                results['total_confidence'] += confidence
                
                # UTI specific tracking
                if 'UTI' in test_name:
                    results['uti_total'] += 1
                    if 'Urinary Tract' in predicted or 'UTI' in predicted:
                        results['uti_correct'] += 1
                
                # Confidence tracking
                results['confidence_totals'][expected_conf] += 1
                
                # Check confidence calibration
                conf_correct = False
                if expected_conf == 'high' and confidence >= 0.8:
                    conf_correct = True
                    results['confidence_accuracy']['high'] += 1
                    results['high_conf_correct'] += 1
                elif expected_conf == 'medium' and 0.6 <= confidence < 0.85:
                    conf_correct = True
                    results['confidence_accuracy']['medium'] += 1
                    results['medium_conf_correct'] += 1
                elif expected_conf == 'low' and confidence < 0.7:
                    conf_correct = True
                    results['confidence_accuracy']['low'] += 1
                
                if expected_conf == 'high':
                    results['high_conf_total'] += 1
                elif expected_conf == 'medium':
                    results['medium_conf_total'] += 1
                
                # Display result
                uti_status = '✅' if 'UTI' in test_name and ('Urinary Tract' in predicted or 'UTI' in predicted) else '❌' if 'UTI' in test_name else ''
                conf_status = '✅' if conf_correct else '❌'
                method_indicator = '🔧' if 'rule' in method else '🤖' if 'ml' in method else '🛡️'
                
                # Truncate for display
                test_name_short = test_name[:25] + '...' if len(test_name) > 25 else test_name
                predicted_short = predicted[:15] + '...' if len(predicted) > 15 else predicted
                
                print(f'{i:2d}. {uti_status}{conf_status} {test_name_short:28s}: {predicted_short:15s} ({confidence:5.1%}) {method_indicator} [{expected_conf}]')
                
            except Exception as e:
                print(f'{i:2d}. ❌ ERROR: {str(e)[:30]}...')
                results['method_counts']['safe_fallback'] += 1
        
        # Calculate comprehensive results
        total_cases = results['total_cases']
        uti_accuracy = results['uti_correct'] / results['uti_total'] if results['uti_total'] > 0 else 0
        avg_confidence = results['total_confidence'] / total_cases
        
        # Confidence accuracy
        high_conf_accuracy = results['confidence_accuracy']['high'] / results['confidence_totals']['high'] if results['confidence_totals']['high'] > 0 else 0
        medium_conf_accuracy = results['confidence_accuracy']['medium'] / results['confidence_totals']['medium'] if results['confidence_totals']['medium'] > 0 else 0
        low_conf_accuracy = results['confidence_accuracy']['low'] / results['confidence_totals']['low'] if results['confidence_totals']['low'] > 0 else 0
        
        # Overall web alignment score
        results['web_alignment_score'] = (uti_accuracy + high_conf_accuracy + medium_conf_accuracy) / 3
        
        print(f'\n📊 FIXED WEB TEST RESULTS:')
        print(f'   Total Cases: {total_cases}')
        print(f'   UTI Detection Accuracy: {uti_accuracy:.1%} ({results["uti_correct"]}/{results["uti_total"]})')
        print(f'   Average Confidence: {avg_confidence:.1%}')
        print(f'   Web Alignment Score: {results["web_alignment_score"]:.1%}')
        
        print(f'\n🎯 CONFIDENCE CALIBRATION:')
        print(f'   High Confidence: {high_conf_accuracy:.1%} ({results["confidence_accuracy"]["high"]}/{results["confidence_totals"]["high"]})')
        print(f'   Medium Confidence: {medium_conf_accuracy:.1%} ({results["confidence_accuracy"]["medium"]}/{results["confidence_totals"]["medium"]})')
        print(f'   Low Confidence: {low_conf_accuracy:.1%} ({results["confidence_accuracy"]["low"]}/{results["confidence_totals"]["low"]})')
        
        print(f'\n🔧 METHOD BREAKDOWN:')
        for method, count in results['method_counts'].items():
            percentage = count / total_cases * 100
            print(f'   {method.replace("_", " ").title()}: {count}/{total_cases} ({percentage:.1f}%)')
        
        # Final assessment
        if uti_accuracy >= 0.80 and medium_conf_accuracy >= 0.60 and results['web_alignment_score'] >= 0.70:
            grade = 'A+ FIXED-EXCELLENT'
            status = '🔧 OUTSTANDING IMPROVEMENTS!'
        elif uti_accuracy >= 0.60 and medium_conf_accuracy >= 0.40 and results['web_alignment_score'] >= 0.60:
            grade = 'A FIXED-GOOD'
            status = '✅ GOOD IMPROVEMENTS!'
        elif uti_accuracy >= 0.40 and medium_conf_accuracy >= 0.20 and results['web_alignment_score'] >= 0.50:
            grade = 'B+ FIXED-ACCEPTABLE'
            status = '⚠️ ACCEPTABLE IMPROVEMENTS'
        else:
            grade = 'C NEEDS MORE WORK'
            status = '❌ NEEDS FURTHER IMPROVEMENTS'
        
        print(f'\n🎯 FINAL FIXED TEST GRADE: {grade}')
        print(f'{status}')
        
        return {
            **results,
            'uti_accuracy': uti_accuracy,
            'avg_confidence': avg_confidence,
            'high_conf_accuracy': high_conf_accuracy,
            'medium_conf_accuracy': medium_conf_accuracy,
            'low_conf_accuracy': low_conf_accuracy,
            'grade': grade
        }

async def main():
    """Main execution"""
    random.seed(42)
    
    test_system = FixedWebTest()
    results = await test_system.run_fixed_web_test()
    
    return results

if __name__ == "__main__":
    result = asyncio.run(main())
