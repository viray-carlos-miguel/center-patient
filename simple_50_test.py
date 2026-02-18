#!/usr/bin/env python3
"""
Simple 50-case test with different diseases
Focus on variety and edge cases to validate system robustness
"""
import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

import asyncio
import random
from guaranteed_accuracy_solution import GuaranteedAccuracySystem

class Simple50Test:
    """Simple test with 50 diverse disease cases"""
    
    def __init__(self):
        self.system = GuaranteedAccuracySystem()
        
        # 50 different disease cases - mix of in-scope and out-of-scope
        self.test_cases = [
            # In-scope conditions (25 cases)
            ('COVID-19', {
                'description': 'covid-19 coronavirus loss of taste anosmia dry cough',
                'temperature': 38.1, 'severity': 6, 'age': 35, 'gender': 'male',
                'symptoms': ['covid', 'loss of taste', 'anosmia', 'dry cough']
            }),
            ('COVID-19', {
                'description': 'sars-cov-2 loss of smell ageusia mild fever',
                'temperature': 37.8, 'severity': 5, 'age': 28, 'gender': 'female',
                'symptoms': ['sars-cov-2', 'loss of smell', 'ageusia', 'fever']
            }),
            ('Influenza', {
                'description': 'influenza flu body aches high fever chills',
                'temperature': 39.2, 'severity': 8, 'age': 40, 'gender': 'male',
                'symptoms': ['influenza', 'body aches', 'high fever', 'chills']
            }),
            ('Influenza', {
                'description': 'flu myalgia chills headache fatigue',
                'temperature': 38.9, 'severity': 7, 'age': 32, 'gender': 'female',
                'symptoms': ['flu', 'myalgia', 'chills', 'headache']
            }),
            ('Pneumonia', {
                'description': 'pneumonia productive cough chest pain shortness of breath',
                'temperature': 39.5, 'severity': 9, 'age': 68, 'gender': 'male',
                'symptoms': ['pneumonia', 'productive cough', 'chest pain', 'shortness of breath']
            }),
            ('Pneumonia', {
                'description': 'lung infection pneumonia dyspnea high fever',
                'temperature': 39.8, 'severity': 8, 'age': 72, 'gender': 'female',
                'symptoms': ['lung infection', 'pneumonia', 'dyspnea', 'high fever']
            }),
            ('Gastroenteritis', {
                'description': 'gastroenteritis watery diarrhea vomiting nausea',
                'temperature': 38.2, 'severity': 6, 'age': 25, 'gender': 'female',
                'symptoms': ['gastroenteritis', 'watery diarrhea', 'vomiting', 'nausea']
            }),
            ('Gastroenteritis', {
                'description': 'stomach flu diarrhea vomiting abdominal cramps',
                'temperature': 37.9, 'severity': 5, 'age': 30, 'gender': 'male',
                'symptoms': ['stomach flu', 'diarrhea', 'vomiting', 'abdominal cramps']
            }),
            ('Migraine', {
                'description': 'migraine unilateral throbbing photophobia light sensitivity',
                'temperature': 36.8, 'severity': 8, 'age': 35, 'gender': 'female',
                'symptoms': ['migraine', 'unilateral', 'throbbing', 'photophobia']
            }),
            ('Migraine', {
                'description': 'migraine aura unilateral headache phonophobia',
                'temperature': 36.9, 'severity': 7, 'age': 40, 'gender': 'male',
                'symptoms': ['migraine', 'aura', 'unilateral headache', 'phonophobia']
            }),
            ('Tension Headache', {
                'description': 'tension headache bilateral pressure band-like',
                'temperature': 36.9, 'severity': 4, 'age': 42, 'gender': 'female',
                'symptoms': ['tension', 'bilateral', 'pressure', 'band-like']
            }),
            ('Tension Headache', {
                'description': 'stress headache tension bilateral neck pain',
                'temperature': 36.8, 'severity': 3, 'age': 35, 'gender': 'male',
                'symptoms': ['stress headache', 'tension', 'bilateral', 'neck pain']
            }),
            ('Urinary Tract Infection', {
                'description': 'uti dysuria burning urination frequency urgency',
                'temperature': 37.6, 'severity': 5, 'age': 28, 'gender': 'female',
                'symptoms': ['uti', 'dysuria', 'burning urination', 'frequency']
            }),
            ('Urinary Tract Infection', {
                'description': 'urinary tract infection frequency urgency pelvic pain',
                'temperature': 37.8, 'severity': 6, 'age': 35, 'gender': 'female',
                'symptoms': ['urinary tract infection', 'frequency', 'urgency', 'pelvic pain']
            }),
            ('Anxiety Disorder', {
                'description': 'anxiety panic attack palpitations heart racing',
                'temperature': 37.0, 'severity': 5, 'age': 26, 'gender': 'female',
                'symptoms': ['anxiety', 'panic attack', 'palpitations', 'heart racing']
            }),
            ('Anxiety Disorder', {
                'description': 'anxiety disorder nervousness restlessness trembling',
                'temperature': 36.9, 'severity': 4, 'age': 30, 'gender': 'male',
                'symptoms': ['anxiety disorder', 'nervousness', 'restlessness', 'trembling']
            }),
            ('COVID-19', {
                'description': 'covid-19 anosmia mild cough fatigue',
                'temperature': 37.6, 'severity': 4, 'age': 38, 'gender': 'female',
                'symptoms': ['covid', 'anosmia', 'mild cough', 'fatigue']
            }),
            ('Influenza', {
                'description': 'influenza h1n1 body aches high fever malaise',
                'temperature': 39.3, 'severity': 8, 'age': 28, 'gender': 'male',
                'symptoms': ['influenza', 'h1n1', 'body aches', 'high fever', 'malaise']
            }),
            ('Pneumonia', {
                'description': 'pneumonia crackles consolidation chest pain',
                'temperature': 39.6, 'severity': 9, 'age': 70, 'gender': 'female',
                'symptoms': ['pneumonia', 'crackles', 'consolidation', 'chest pain']
            }),
            ('Gastroenteritis', {
                'description': 'gi infection gastroenteritis vomiting diarrhea',
                'temperature': 38.1, 'severity': 6, 'age': 22, 'gender': 'female',
                'symptoms': ['gi infection', 'gastroenteritis', 'vomiting', 'diarrhea']
            }),
            ('Migraine', {
                'description': 'migraine photophobia phonophobia unilateral pain',
                'temperature': 36.8, 'severity': 8, 'age': 45, 'gender': 'male',
                'symptoms': ['migraine', 'photophobia', 'phonophobia', 'unilateral pain']
            }),
            ('Tension Headache', {
                'description': 'tension headache pressure sensation band-like',
                'temperature': 36.9, 'severity': 3, 'age': 38, 'gender': 'male',
                'symptoms': ['tension', 'pressure sensation', 'band-like', 'mild']
            }),
            ('Urinary Tract Infection', {
                'description': 'uti bladder infection burning urination hematuria',
                'temperature': 37.5, 'severity': 5, 'age': 30, 'gender': 'female',
                'symptoms': ['uti', 'bladder infection', 'burning urination', 'hematuria']
            }),
            ('Anxiety Disorder', {
                'description': 'anxiety palpitations shortness of breath chest tightness',
                'temperature': 37.1, 'severity': 5, 'age': 35, 'gender': 'female',
                'symptoms': ['anxiety', 'palpitations', 'shortness of breath', 'chest tightness']
            }),
            ('COVID-19', {
                'description': 'coronavirus taste loss smell loss cough',
                'temperature': 38.5, 'severity': 6, 'age': 42, 'gender': 'female',
                'symptoms': ['coronavirus', 'taste loss', 'smell loss', 'cough']
            }),
            
            # Out-of-scope conditions (25 cases) - different diseases
            ('Bronchitis', {
                'description': 'bronchitis persistent cough mucus chest tightness',
                'temperature': 37.7, 'severity': 5, 'age': 45, 'gender': 'male',
                'symptoms': ['bronchitis', 'persistent cough', 'mucus', 'chest tightness']
            }),
            ('Asthma', {
                'description': 'asthma wheezing shortness of breath chest tightness',
                'temperature': 37.0, 'severity': 6, 'age': 30, 'gender': 'female',
                'symptoms': ['asthma', 'wheezing', 'shortness of breath', 'chest tightness']
            }),
            ('Sinusitis', {
                'description': 'sinusitis facial pressure nasal congestion sinus headache',
                'temperature': 37.4, 'severity': 4, 'age': 35, 'gender': 'female',
                'symptoms': ['sinusitis', 'facial pressure', 'nasal congestion', 'sinus headache']
            }),
            ('Hypertension', {
                'description': 'hypertension high blood pressure headache dizziness',
                'temperature': 36.8, 'severity': 3, 'age': 55, 'gender': 'male',
                'symptoms': ['hypertension', 'high blood pressure', 'headache', 'dizziness']
            }),
            ('Angina', {
                'description': 'angina chest pain exertion shortness of breath',
                'temperature': 36.9, 'severity': 6, 'age': 60, 'gender': 'female',
                'symptoms': ['angina', 'chest pain', 'exertion', 'shortness of breath']
            }),
            ('GERD', {
                'description': 'gerd acid reflux heartburn regurgitation',
                'temperature': 36.9, 'severity': 4, 'age': 40, 'gender': 'female',
                'symptoms': ['gerd', 'acid reflux', 'heartburn', 'regurgitation']
            }),
            ('Peptic Ulcer', {
                'description': 'peptic ulcer stomach pain burning sensation nausea',
                'temperature': 37.1, 'severity': 6, 'age': 45, 'gender': 'male',
                'symptoms': ['peptic ulcer', 'stomach pain', 'burning sensation', 'nausea']
            }),
            ('Irritable Bowel Syndrome', {
                'description': 'ibs abdominal pain bloating diarrhea constipation',
                'temperature': 37.0, 'severity': 4, 'age': 35, 'gender': 'female',
                'symptoms': ['ibs', 'abdominal pain', 'bloating', 'diarrhea', 'constipation']
            }),
            ('Pancreatitis', {
                'description': 'pancreatitis severe abdominal pain nausea vomiting',
                'temperature': 38.5, 'severity': 8, 'age': 50, 'gender': 'male',
                'symptoms': ['pancreatitis', 'severe abdominal pain', 'nausea', 'vomiting']
            }),
            ('Epilepsy', {
                'description': 'epilepsy seizures convulsions loss of consciousness',
                'temperature': 37.0, 'severity': 7, 'age': 25, 'gender': 'female',
                'symptoms': ['epilepsy', 'seizures', 'convulsions', 'loss of consciousness']
            }),
            ('Multiple Sclerosis', {
                'description': 'multiple sclerosis vision problems numbness weakness',
                'temperature': 36.8, 'severity': 5, 'age': 35, 'gender': 'male',
                'symptoms': ['multiple sclerosis', 'vision problems', 'numbness', 'weakness']
            }),
            ('Stroke', {
                'description': 'stroke sudden weakness speech difficulty facial droop',
                'temperature': 37.2, 'severity': 9, 'age': 70, 'gender': 'male',
                'symptoms': ['stroke', 'sudden weakness', 'speech difficulty', 'facial droop']
            }),
            ('Diabetes Type 1', {
                'description': 'diabetes type 1 excessive thirst frequent urination weight loss',
                'temperature': 37.0, 'severity': 5, 'age': 20, 'gender': 'female',
                'symptoms': ['diabetes type 1', 'excessive thirst', 'frequent urination', 'weight loss']
            }),
            ('Diabetes Type 2', {
                'description': 'diabetes type 2 fatigue blurred vision slow healing',
                'temperature': 37.1, 'severity': 4, 'age': 55, 'gender': 'male',
                'symptoms': ['diabetes type 2', 'fatigue', 'blurred vision', 'slow healing']
            }),
            ('Thyroid Disease', {
                'description': 'thyroid disease weight changes fatigue hair loss',
                'temperature': 36.7, 'severity': 3, 'age': 40, 'gender': 'female',
                'symptoms': ['thyroid disease', 'weight changes', 'fatigue', 'hair loss']
            }),
            ('Arthritis', {
                'description': 'arthritis joint pain stiffness swelling',
                'temperature': 37.2, 'severity': 5, 'age': 60, 'gender': 'female',
                'symptoms': ['arthritis', 'joint pain', 'stiffness', 'swelling']
            }),
            ('Osteoporosis', {
                'description': 'osteoporosis bone fractures back pain height loss',
                'temperature': 36.8, 'severity': 3, 'age': 70, 'gender': 'male',
                'symptoms': ['osteoporosis', 'bone fractures', 'back pain', 'height loss']
            }),
            ('Fibromyalgia', {
                'description': 'fibromyalgia widespread pain fatigue sleep problems',
                'temperature': 36.9, 'severity': 6, 'age': 45, 'gender': 'female',
                'symptoms': ['fibromyalgia', 'widespread pain', 'fatigue', 'sleep problems']
            }),
            ('Eczema', {
                'description': 'eczema skin rash itching dryness inflammation',
                'temperature': 37.0, 'severity': 4, 'age': 25, 'gender': 'female',
                'symptoms': ['eczema', 'skin rash', 'itching', 'dryness', 'inflammation']
            }),
            ('Psoriasis', {
                'description': 'psoriasis scaly patches red skin itching',
                'temperature': 37.1, 'severity': 5, 'age': 40, 'gender': 'male',
                'symptoms': ['psoriasis', 'scaly patches', 'red skin', 'itching']
            }),
            ('Tuberculosis', {
                'description': 'tuberculosis persistent cough weight loss night sweats',
                'temperature': 37.8, 'severity': 7, 'age': 35, 'gender': 'male',
                'symptoms': ['tuberculosis', 'persistent cough', 'weight loss', 'night sweats']
            }),
            ('Hepatitis', {
                'description': 'hepatitis jaundice fatigue abdominal pain nausea',
                'temperature': 38.0, 'severity': 6, 'age': 40, 'gender': 'female',
                'symptoms': ['hepatitis', 'jaundice', 'fatigue', 'abdominal pain', 'nausea']
            }),
            ('Meningitis', {
                'description': 'meningitis severe headache stiff fever neck pain',
                'temperature': 39.5, 'severity': 9, 'age': 25, 'gender': 'male',
                'symptoms': ['meningitis', 'severe headache', 'stiff neck', 'fever', 'neck pain']
            }),
            ('Lupus', {
                'description': 'lupus joint pain fatigue skin rash fever',
                'temperature': 37.5, 'severity': 6, 'age': 35, 'gender': 'female',
                'symptoms': ['lupus', 'joint pain', 'fatigue', 'skin rash', 'fever']
            }),
            ('Depression', {
                'description': 'depression persistent sadness loss of interest sleep changes',
                'temperature': 36.8, 'severity': 5, 'age': 35, 'gender': 'female',
                'symptoms': ['depression', 'persistent sadness', 'loss of interest', 'sleep changes']
            }),
            ('Anemia', {
                'description': 'anemia fatigue weakness pale skin shortness of breath',
                'temperature': 36.7, 'severity': 4, 'age': 40, 'gender': 'female',
                'symptoms': ['anemia', 'fatigue', 'weakness', 'pale skin', 'shortness of breath']
            })
        ]
    
    async def run_simple_test(self) -> dict:
        """Run simple 50-case test"""
        print('🚀 SIMPLE 50-CASE TEST')
        print('=' * 60)
        print('Testing 25 in-scope + 25 out-of-scope diseases')
        print('Focus: Different disease varieties and edge cases')
        print()
        
        # Shuffle test order
        shuffled_cases = self.test_cases.copy()
        random.shuffle(shuffled_cases)
        
        # Results tracking
        in_scope_correct = 0
        in_scope_total = 0
        out_scope_safe = 0
        out_scope_total = 0
        total_confidence = 0.0
        method_counts = {'rule_based': 0, 'ml_fallback': 0, 'safe_fallback': 0}
        
        print(f'🧪 Testing {len(shuffled_cases)} diverse cases...')
        print()
        
        for i, (expected_condition, symptoms) in enumerate(shuffled_cases, 1):
            # Add duration_hours if not present
            if 'duration_hours' not in symptoms:
                symptoms['duration_hours'] = random.randint(24, 168)
            
            try:
                result = await self.system.hybrid_predict(symptoms)
                
                predicted = result.get('ml_prediction', {}).get('primary_condition', 'Unknown')
                confidence = result.get('ml_prediction', {}).get('confidence', 0)
                method = result.get('ml_prediction', {}).get('prediction_method', 'unknown')
                
                # Track methods
                if 'rule' in method:
                    method_counts['rule_based'] += 1
                elif 'ml' in method:
                    method_counts['ml_fallback'] += 1
                elif 'safe' in method:
                    method_counts['safe_fallback'] += 1
                
                total_confidence += confidence
                
                # Check if in-scope condition
                in_scope_conditions = [
                    'COVID-19', 'Influenza', 'Pneumonia', 'Gastroenteritis',
                    'Migraine', 'Tension Headache', 'Urinary Tract Infection', 'Anxiety Disorder'
                ]
                
                if expected_condition in in_scope_conditions:
                    in_scope_total += 1
                    if predicted == expected_condition:
                        in_scope_correct += 1
                else:
                    out_scope_total += 1
                    if predicted == 'General Medical Assessment':
                        out_scope_safe += 1
                
                # Display result
                status = '✅' if (expected_condition in in_scope_conditions and predicted == expected_condition) or \
                              (expected_condition not in in_scope_conditions and predicted == 'General Medical Assessment') else '❌'
                
                method_indicator = '🔧' if 'rule' in method else '🤖' if 'ml' in method else '🛡️'
                
                # Truncate long names for display
                expected_short = expected_condition[:15] + '...' if len(expected_condition) > 15 else expected_condition
                predicted_short = predicted[:15] + '...' if len(predicted) > 15 else predicted
                
                print(f'{i:2d}. {status} {expected_short:18s}: {predicted_short:18s} ({confidence:5.1%}) {method_indicator}')
                
            except Exception as e:
                print(f'{i:2d}. ❌ ERROR: {str(e)[:30]}...')
                method_counts['safe_fallback'] += 1
        
        # Calculate results
        total_cases = len(shuffled_cases)
        in_scope_accuracy = in_scope_correct / in_scope_total if in_scope_total > 0 else 0
        out_scope_safety = out_scope_safe / out_scope_total if out_scope_total > 0 else 0
        avg_confidence = total_confidence / total_cases
        
        print(f'\n📊 SIMPLE 50-CASE RESULTS:')
        print(f'   Total Cases: {total_cases}')
        print(f'   In-Scope Accuracy: {in_scope_accuracy:.1%} ({in_scope_correct}/{in_scope_total})')
        print(f'   Out-of-Scope Safety: {out_scope_safety:.1%} ({out_scope_safe}/{out_scope_total})')
        print(f'   Average Confidence: {avg_confidence:.1%}')
        
        print(f'\n🔧 METHOD BREAKDOWN:')
        for method, count in method_counts.items():
            percentage = count / total_cases * 100
            print(f'   {method.replace("_", " ").title()}: {count}/{total_cases} ({percentage:.1f}%)')
        
        # Final assessment
        if in_scope_accuracy >= 0.80 and out_scope_safety >= 0.80:
            grade = 'A EXCELLENT'
            status = '✅ OUTSTANDING PERFORMANCE!'
        elif in_scope_accuracy >= 0.70 and out_scope_safety >= 0.70:
            grade = 'B+ GOOD'
            status = '✅ GOOD PERFORMANCE!'
        elif in_scope_accuracy >= 0.60 and out_scope_safety >= 0.60:
            grade = 'C ACCEPTABLE'
            status = '⚠️ ACCEPTABLE PERFORMANCE'
        else:
            grade = 'D NEEDS IMPROVEMENT'
            status = '❌ NEEDS WORK'
        
        print(f'\n🎯 FINAL GRADE: {grade}')
        print(f'{status}')
        
        return {
            'total_cases': total_cases,
            'in_scope_accuracy': in_scope_accuracy,
            'out_scope_safety': out_scope_safety,
            'avg_confidence': avg_confidence,
            'method_counts': method_counts,
            'grade': grade
        }

async def main():
    """Main execution"""
    random.seed(42)
    
    test_system = Simple50Test()
    results = await test_system.run_simple_test()
    
    return results

if __name__ == "__main__":
    result = asyncio.run(main())
