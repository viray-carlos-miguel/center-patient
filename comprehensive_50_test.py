#!/usr/bin/env python3
"""
Comprehensive 50 Test Cases
Tests 50 different symptom patterns and disease variations
"""
import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

import asyncio
import random
from guaranteed_accuracy_solution import GuaranteedAccuracySystem

class Comprehensive50Test:
    """Comprehensive test with 50 diverse symptom patterns"""
    
    def __init__(self):
        self.system = GuaranteedAccuracySystem()
        
        # 50 comprehensive test cases covering variations
        self.test_cases = [
            # COVID-19 variations (7 cases)
            ('COVID-19', {
                'description': 'covid-19 sars-cov-2 coronavirus loss of taste anosmia',
                'temperature': 38.1, 'severity': 6, 'age': 45, 'gender': 'male',
                'symptoms': ['covid', 'loss of taste', 'anosmia', 'dry cough']
            }),
            ('COVID-19', {
                'description': 'covid-19 loss of smell ageusia mild fever fatigue',
                'temperature': 37.8, 'severity': 5, 'age': 32, 'gender': 'female',
                'symptoms': ['covid', 'loss of smell', 'ageusia', 'fatigue']
            }),
            ('COVID-19', {
                'description': 'coronavirus sars-cov-2 taste loss smell loss cough',
                'temperature': 38.5, 'severity': 7, 'age': 28, 'gender': 'male',
                'symptoms': ['coronavirus', 'taste loss', 'smell loss', 'dry cough']
            }),
            ('COVID-19', {
                'description': 'covid-19 anosmia ageusia shortness of breath',
                'temperature': 38.3, 'severity': 6, 'age': 55, 'gender': 'female',
                'symptoms': ['covid', 'anosmia', 'ageusia', 'shortness of breath']
            }),
            ('COVID-19', {
                'description': 'sars-cov-2 covid loss of taste loss of smell fever',
                'temperature': 38.7, 'severity': 6, 'age': 38, 'gender': 'male',
                'symptoms': ['sars-cov-2', 'loss of taste', 'loss of smell', 'fever']
            }),
            ('COVID-19', {
                'description': 'covid-19 coronavirus dry cough loss of taste',
                'temperature': 38.0, 'severity': 5, 'age': 42, 'gender': 'female',
                'symptoms': ['covid-19', 'dry cough', 'loss of taste', 'fatigue']
            }),
            ('COVID-19', {
                'description': 'covid-19 loss of smell anosmia mild symptoms',
                'temperature': 37.6, 'severity': 4, 'age': 35, 'gender': 'male',
                'symptoms': ['covid', 'loss of smell', 'anosmia', 'mild cough']
            }),
            
            # Influenza variations (6 cases)
            ('Influenza', {
                'description': 'influenza flu h1n1 body aches myalgia high fever',
                'temperature': 39.2, 'severity': 8, 'age': 25, 'gender': 'female',
                'symptoms': ['influenza', 'body aches', 'myalgia', 'high fever']
            }),
            ('Influenza', {
                'description': 'flu influenza chills muscle pain headache',
                'temperature': 38.9, 'severity': 7, 'age': 40, 'gender': 'male',
                'symptoms': ['flu', 'chills', 'muscle pain', 'headache']
            }),
            ('Influenza', {
                'description': 'influenza h1n1 body aches high fever chills',
                'temperature': 39.5, 'severity': 8, 'age': 30, 'gender': 'female',
                'symptoms': ['influenza', 'h1n1', 'body aches', 'high fever', 'chills']
            }),
            ('Influenza', {
                'description': 'flu myalgia body aches severe headache',
                'temperature': 39.0, 'severity': 7, 'age': 45, 'gender': 'male',
                'symptoms': ['flu', 'myalgia', 'body aches', 'severe headache']
            }),
            ('Influenza', {
                'description': 'influenza flu chills fatigue muscle pain',
                'temperature': 38.8, 'severity': 6, 'age': 35, 'gender': 'female',
                'symptoms': ['influenza', 'chills', 'fatigue', 'muscle pain']
            }),
            ('Influenza', {
                'description': 'h1n1 influenza body aches high fever malaise',
                'temperature': 39.3, 'severity': 8, 'age': 28, 'gender': 'male',
                'symptoms': ['h1n1', 'body aches', 'high fever', 'malaise']
            }),
            
            # Pneumonia variations (6 cases)
            ('Pneumonia', {
                'description': 'pneumonia lung infection productive cough chest pain',
                'temperature': 39.8, 'severity': 9, 'age': 68, 'gender': 'male',
                'symptoms': ['pneumonia', 'productive cough', 'chest pain', 'high fever']
            }),
            ('Pneumonia', {
                'description': 'pneumonia crackles consolidation dyspnea shortness of breath',
                'temperature': 39.5, 'severity': 8, 'age': 72, 'gender': 'female',
                'symptoms': ['pneumonia', 'crackles', 'dyspnea', 'shortness of breath']
            }),
            ('Pneumonia', {
                'description': 'lung infection pneumonia productive cough fever',
                'temperature': 39.2, 'severity': 8, 'age': 65, 'gender': 'male',
                'symptoms': ['lung infection', 'pneumonia', 'productive cough', 'fever']
            }),
            ('Pneumonia', {
                'description': 'pneumonia chest pain consolidation crackles',
                'temperature': 39.6, 'severity': 9, 'age': 70, 'gender': 'female',
                'symptoms': ['pneumonia', 'chest pain', 'consolidation', 'crackles']
            }),
            ('Pneumonia', {
                'description': 'pneumonia dyspnea productive cough severe',
                'temperature': 39.4, 'severity': 8, 'age': 58, 'gender': 'male',
                'symptoms': ['pneumonia', 'dyspnea', 'productive cough', 'severe']
            }),
            ('Pneumonia', {
                'description': 'lung infection pneumonia shortness of breath',
                'temperature': 39.1, 'severity': 7, 'age': 62, 'gender': 'female',
                'symptoms': ['lung infection', 'pneumonia', 'shortness of breath', 'fatigue']
            }),
            
            # Gastroenteritis variations (6 cases)
            ('Gastroenteritis', {
                'description': 'gastroenteritis stomach flu watery diarrhea vomiting',
                'temperature': 38.2, 'severity': 6, 'age': 25, 'gender': 'female',
                'symptoms': ['gastroenteritis', 'watery diarrhea', 'vomiting', 'nausea']
            }),
            ('Gastroenteritis', {
                'description': 'gastroenteritis diarrhea vomiting stomach cramps',
                'temperature': 37.9, 'severity': 5, 'age': 30, 'gender': 'male',
                'symptoms': ['gastroenteritis', 'diarrhea', 'vomiting', 'stomach cramps']
            }),
            ('Gastroenteritis', {
                'description': 'stomach flu gi infection vomiting nausea',
                'temperature': 38.0, 'severity': 5, 'age': 22, 'gender': 'female',
                'symptoms': ['stomach flu', 'gi infection', 'vomiting', 'nausea']
            }),
            ('Gastroenteritis', {
                'description': 'gastroenteritis watery diarrhea abdominal pain',
                'temperature': 37.8, 'severity': 5, 'age': 35, 'gender': 'male',
                'symptoms': ['gastroenteritis', 'watery diarrhea', 'abdominal pain', 'dehydration']
            }),
            ('Gastroenteritis', {
                'description': 'gi infection gastroenteritis vomiting diarrhea',
                'temperature': 38.1, 'severity': 6, 'age': 28, 'gender': 'female',
                'symptoms': ['gi infection', 'gastroenteritis', 'vomiting', 'diarrhea']
            }),
            ('Gastroenteritis', {
                'description': 'stomach flu nausea vomiting stomach cramps',
                'temperature': 37.7, 'severity': 4, 'age': 32, 'gender': 'male',
                'symptoms': ['stomach flu', 'nausea', 'vomiting', 'stomach cramps']
            }),
            
            # Migraine variations (6 cases)
            ('Migraine', {
                'description': 'migraine unilateral throbbing photophobia light sensitivity',
                'temperature': 36.8, 'severity': 8, 'age': 35, 'gender': 'female',
                'symptoms': ['migraine', 'unilateral', 'throbbing', 'photophobia']
            }),
            ('Migraine', {
                'description': 'migraine aura unilateral headache phonophobia sound sensitivity',
                'temperature': 36.9, 'severity': 7, 'age': 40, 'gender': 'male',
                'symptoms': ['migraine', 'aura', 'unilateral headache', 'phonophobia']
            }),
            ('Migraine', {
                'description': 'migraine unilateral throbbing light sensitivity nausea',
                'temperature': 36.7, 'severity': 7, 'age': 30, 'gender': 'female',
                'symptoms': ['migraine', 'unilateral', 'throbbing', 'light sensitivity']
            }),
            ('Migraine', {
                'description': 'migraine photophobia phonophobia unilateral pain',
                'temperature': 36.8, 'severity': 8, 'age': 45, 'gender': 'male',
                'symptoms': ['migraine', 'photophobia', 'phonophobia', 'unilateral pain']
            }),
            ('Migraine', {
                'description': 'migraine aura throbbing headache light sensitivity',
                'temperature': 36.9, 'severity': 6, 'age': 25, 'gender': 'female',
                'symptoms': ['migraine', 'aura', 'throbbing headache', 'light sensitivity']
            }),
            ('Migraine', {
                'description': 'migraine unilateral phonophobia sound sensitivity',
                'temperature': 36.8, 'severity': 7, 'age': 38, 'gender': 'male',
                'symptoms': ['migraine', 'unilateral', 'phonophobia', 'sound sensitivity']
            }),
            
            # Tension Headache variations (6 cases)
            ('Tension Headache', {
                'description': 'tension headache bilateral pressure band-like',
                'temperature': 36.9, 'severity': 4, 'age': 42, 'gender': 'female',
                'symptoms': ['tension', 'bilateral', 'pressure', 'band-like']
            }),
            ('Tension Headache', {
                'description': 'tension headache bilateral pressure neck pain',
                'temperature': 36.8, 'severity': 3, 'age': 35, 'gender': 'male',
                'symptoms': ['tension', 'bilateral', 'pressure', 'neck pain']
            }),
            ('Tension Headache', {
                'description': 'stress headache tension bilateral scalp tenderness',
                'temperature': 37.0, 'severity': 4, 'age': 40, 'gender': 'female',
                'symptoms': ['stress headache', 'tension', 'bilateral', 'scalp tenderness']
            }),
            ('Tension Headache', {
                'description': 'tension headache pressure sensation band-like',
                'temperature': 36.9, 'severity': 3, 'age': 38, 'gender': 'male',
                'symptoms': ['tension', 'pressure sensation', 'band-like', 'mild']
            }),
            ('Tension Headache', {
                'description': 'tension bilateral headache neck pain stress',
                'temperature': 36.8, 'severity': 4, 'age': 45, 'gender': 'female',
                'symptoms': ['tension', 'bilateral headache', 'neck pain', 'stress']
            }),
            ('Tension Headache', {
                'description': 'tension headache pressure bilateral mild',
                'temperature': 36.9, 'severity': 2, 'age': 32, 'gender': 'male',
                'symptoms': ['tension', 'pressure', 'bilateral', 'mild pain']
            }),
            
            # Urinary Tract Infection variations (6 cases)
            ('Urinary Tract Infection', {
                'description': 'uti urinary tract infection dysuria burning urination',
                'temperature': 37.6, 'severity': 5, 'age': 28, 'gender': 'female',
                'symptoms': ['uti', 'dysuria', 'burning urination', 'frequency']
            }),
            ('Urinary Tract Infection', {
                'description': 'urinary tract infection frequency urgency suprapubic pain',
                'temperature': 37.8, 'severity': 6, 'age': 35, 'gender': 'female',
                'symptoms': ['urinary tract infection', 'frequency', 'urgency', 'suprapubic pain']
            }),
            ('Urinary Tract Infection', {
                'description': 'uti bladder infection burning urination hematuria',
                'temperature': 37.5, 'severity': 5, 'age': 30, 'gender': 'female',
                'symptoms': ['uti', 'bladder infection', 'burning urination', 'hematuria']
            }),
            ('Urinary Tract Infection', {
                'description': 'uti dysuria frequency urgency pelvic pain',
                'temperature': 37.7, 'severity': 5, 'age': 40, 'gender': 'female',
                'symptoms': ['uti', 'dysuria', 'frequency', 'urgency', 'pelvic pain']
            }),
            ('Urinary Tract Infection', {
                'description': 'urinary tract infection cloudy urine burning',
                'temperature': 37.4, 'severity': 4, 'age': 25, 'gender': 'female',
                'symptoms': ['urinary tract infection', 'cloudy urine', 'burning', 'urgency']
            }),
            ('Urinary Tract Infection', {
                'description': 'uti painful urination frequency urgency',
                'temperature': 37.6, 'severity': 5, 'age': 33, 'gender': 'female',
                'symptoms': ['uti', 'painful urination', 'frequency', 'urgency']
            }),
            
            # Anxiety Disorder variations (7 cases)
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
            ('Anxiety Disorder', {
                'description': 'anxiety palpitations shortness of breath chest tightness',
                'temperature': 37.1, 'severity': 5, 'age': 35, 'gender': 'female',
                'symptoms': ['anxiety', 'palpitations', 'shortness of breath', 'chest tightness']
            }),
            ('Anxiety Disorder', {
                'description': 'panic attack anxiety heart racing sweating dizziness',
                'temperature': 37.0, 'severity': 6, 'age': 28, 'gender': 'male',
                'symptoms': ['panic attack', 'anxiety', 'heart racing', 'sweating', 'dizziness']
            }),
            ('Anxiety Disorder', {
                'description': 'anxiety disorder nervousness restlessness worry',
                'temperature': 36.8, 'severity': 4, 'age': 32, 'gender': 'female',
                'symptoms': ['anxiety disorder', 'nervousness', 'restlessness', 'worry']
            }),
            ('Anxiety Disorder', {
                'description': 'anxiety palpitations trembling shortness of breath',
                'temperature': 37.0, 'severity': 5, 'age': 40, 'gender': 'male',
                'symptoms': ['anxiety', 'palpitations', 'trembling', 'shortness of breath']
            }),
            ('Anxiety Disorder', {
                'description': 'anxiety panic attack heart racing nervousness',
                'temperature': 36.9, 'severity': 5, 'age': 24, 'gender': 'female',
                'symptoms': ['anxiety', 'panic attack', 'heart racing', 'nervousness']
            })
        ]
    
    async def run_comprehensive_test(self) -> dict:
        """Run comprehensive test with 50 cases"""
        print('🚀 COMPREHENSIVE 50 TEST CASES')
        print('=' * 70)
        print('Testing 50 diverse symptom patterns and disease variations')
        print('Target: Maintain 75-90% accuracy across all variations')
        print()
        
        # Shuffle test order for realistic testing
        shuffled_cases = self.test_cases.copy()
        random.shuffle(shuffled_cases)
        
        # Results tracking
        results_by_condition = {condition: {'correct': 0, 'total': 0, 'confidences': []} 
                               for condition, _ in self.test_cases}
        
        overall_correct = 0
        overall_confidence = 0.0
        confidence_75_90 = 0
        confidence_80_90 = 0
        method_counts = {'rule_based': 0, 'ml_fallback': 0, 'fallback': 0}
        
        print(f'🧪 Testing {len(shuffled_cases)} diverse cases...')
        print()
        
        for i, (expected_condition, symptoms) in enumerate(shuffled_cases, 1):
            # Add duration_hours if not present
            if 'duration_hours' not in symptoms:
                symptoms['duration_hours'] = random.randint(24, 168)
            
            result = await self.system.hybrid_predict(symptoms)
            
            predicted = result.get('ml_prediction', {}).get('primary_condition', 'Unknown')
            confidence = result.get('ml_prediction', {}).get('confidence', 0)
            method = result.get('ml_prediction', {}).get('prediction_method', 'unknown')
            
            is_correct = predicted == expected_condition
            
            # Track results
            results_by_condition[expected_condition]['total'] += 1
            results_by_condition[expected_condition]['confidences'].append(confidence)
            
            if is_correct:
                results_by_condition[expected_condition]['correct'] += 1
                overall_correct += 1
            
            overall_confidence += confidence
            if 75 <= confidence * 100 <= 90:
                confidence_75_90 += 1
            if 80 <= confidence * 100 <= 90:
                confidence_80_90 += 1
            
            # Track methods
            if 'rule' in method:
                method_counts['rule_based'] += 1
            elif 'ml' in method:
                method_counts['ml_fallback'] += 1
            else:
                method_counts['fallback'] += 1
            
            # Display result
            status = '✅' if is_correct else '❌'
            method_indicator = '🔧' if 'rule' in method else '🤖' if 'ml' in method else '🔄'
            
            print(f'{i:2d}. {status} {expected_condition[:15]:15s}: {predicted[:15]:15s} ({confidence:5.1%}) {method_indicator} {"🔥" if not is_correct else ""}')
            
            # Show details for incorrect predictions
            if not is_correct:
                print(f'     Expected: {expected_condition}')
                print(f'     Method: {method}')
                print(f'     Description: {symptoms["description"][:50]}...')
        
        # Calculate comprehensive results
        total_cases = len(shuffled_cases)
        overall_accuracy = overall_correct / total_cases
        avg_confidence = overall_confidence / total_cases
        
        print(f'\n📊 COMPREHENSIVE RESULTS:')
        print(f'   Total Cases: {total_cases}')
        print(f'   Overall Accuracy: {overall_accuracy:.1%} ({overall_correct}/{total_cases})')
        print(f'   Average Confidence: {avg_confidence:.1%}')
        print(f'   75-90% Confidence: {confidence_75_90}/{total_cases} ({confidence_75_90/total_cases:.1%})')
        print(f'   80-90% Confidence: {confidence_80_90}/{total_cases} ({confidence_80_90/total_cases:.1%})')
        
        print(f'\n🔧 METHOD BREAKDOWN:')
        for method, count in method_counts.items():
            percentage = count / total_cases * 100
            print(f'   {method.replace("_", " ").title()}: {count}/{total_cases} ({percentage:.1f}%)')
        
        print(f'\n🏥 RESULTS BY CONDITION:')
        for condition, stats in results_by_condition.items():
            if stats['total'] > 0:
                accuracy = stats['correct'] / stats['total']
                avg_conf = np.mean(stats['confidences'])
                print(f'   {condition[:20]:20s}: {accuracy:.1%} ({stats["correct"]}/{stats["total"]}) - Avg Conf: {avg_conf:.1%}')
        
        # Final assessment
        if overall_accuracy >= 0.90:
            grade = 'A+ EXCELLENT'
            status = '🎯 OUTSTANDING SUCCESS!'
        elif overall_accuracy >= 0.80:
            grade = 'A EXCELLENT'
            status = '✅ EXCELLENT SUCCESS!'
        elif overall_accuracy >= 0.75:
            grade = 'B+ GOOD'
            status = '✅ SUCCESS!'
        elif overall_accuracy >= 0.60:
            grade = 'C ACCEPTABLE'
            status = '⚠️ MEETS MINIMUM'
        else:
            grade = 'D NEEDS IMPROVEMENT'
            status = '❌ NEEDS WORK'
        
        print(f'\n🎯 COMPREHENSIVE GRADE: {grade}')
        print(f'{status}')
        
        return {
            'total_cases': total_cases,
            'overall_accuracy': overall_accuracy,
            'avg_confidence': avg_confidence,
            'confidence_75_90': confidence_75_90,
            'confidence_80_90': confidence_80_90,
            'method_counts': method_counts,
            'results_by_condition': results_by_condition,
            'grade': grade
        }

async def main():
    """Main execution"""
    random.seed(42)  # For reproducible results
    
    test_system = Comprehensive50Test()
    results = await test_system.run_comprehensive_test()
    
    return results

if __name__ == "__main__":
    result = asyncio.run(main())
