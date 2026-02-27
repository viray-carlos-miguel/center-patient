"""
Comprehensive test for improved deterministic rules
"""
import requests
import json

def test_improved_rules():
    print('🔬 TESTING IMPROVED DETERMINISTIC RULES')
    print('📋 Testing complex symptoms with enhanced rule specificity')
    print('=' * 80)
    
    # Test cases that were previously failing
    test_cases = [
        {
            'name': 'Meningitis',
            'symptoms': {
                'description': 'severe headache with stiff neck, high fever, sensitivity to light, confusion, nausea and vomiting, difficulty concentrating, seizures, sleepiness, difficulty waking, skin rash',
                'temperature': '39.5',
                'duration_hours': '12',
                'severity': '9',
                'has_fever': True,
                'has_headache': True,
                'has_nausea': True,
                'has_vomiting': True,
                'has_confusion': True,
                'has_photophobia': True
            }
        },
        {
            'name': 'Pulmonary Embolism',
            'symptoms': {
                'description': 'sudden sharp chest pain when breathing deeply, rapid heartbeat, shortness of breath, coughing up blood, leg pain and swelling, lightheadedness, excessive sweating, bluish skin discoloration',
                'temperature': '37.0',
                'duration_hours': '3',
                'severity': '9',
                'has_fever': False,
                'has_chest_pain': True,
                'has_shortness_of_breath': True,
                'has_leg_swelling': True,
                'has_cough': True
            }
        },
        {
            'name': 'Sepsis',
            'symptoms': {
                'description': 'high fever with chills and shivering, rapid heart rate, rapid breathing, confusion and disorientation, extreme pain or discomfort, clammy or sweaty skin, shortness of breath',
                'temperature': '39.8',
                'duration_hours': '8',
                'severity': '10',
                'has_fever': True,
                'has_confusion': True,
                'has_shortness_of_breath': True,
                'has_chills': True
            }
        },
        {
            'name': 'Essential Hypertension',
            'symptoms': {
                'description': 'severe headaches, nosebleeds, fatigue or confusion, vision problems, chest pain, difficulty breathing, irregular heartbeat, blood in urine, pounding in chest neck or ears',
                'temperature': '37.0',
                'duration_hours': '8760',
                'severity': '4',
                'has_fever': False,
                'has_headache': True,
                'has_nosebleeds': True,
                'has_fatigue': True,
                'has_vision_changes': True,
                'has_chest_pain': True
            }
        },
        {
            'name': 'Nephrolithiasis',
            'symptoms': {
                'description': 'severe sharp pain in side and back below ribs, pain that radiates to lower abdomen and groin, pain that comes in waves and fluctuates in intensity, pain on urination, pink red or brown urine, cloudy or foul-smelling urine, nausea and vomiting, persistent need to urinate',
                'temperature': '37.0',
                'duration_hours': '12',
                'severity': '9',
                'has_fever': False,
                'has_abdominal_pain': True,
                'has_back_pain': True,
                'has_nausea': True,
                'has_vomiting': True,
                'has_painful_urination': True
            }
        },
        {
            'name': 'Common Cold',
            'symptoms': {
                'description': 'runny or stuffy nose, sore throat, cough, congestion, slight body aches or mild headache, sneezing, low-grade fever, generally feeling unwell',
                'temperature': '37.5',
                'duration_hours': '72',
                'severity': '3',
                'has_fever': True,
                'has_nasal_congestion': True,
                'has_runny_nose': True,
                'has_sore_throat': True,
                'has_cough_dry': True,
                'has_sneezing': True,
                'has_headache': True
            }
        },
        {
            'name': 'Atopic Dermatitis',
            'symptoms': {
                'description': 'dry skin, itching which may be severe especially at night, red to brownish-gray patches, small raised bumps, thickened cracked scaly skin, raw sensitive swollen skin from scratching',
                'temperature': '37.0',
                'duration_hours': '2160',
                'severity': '5',
                'has_fever': False,
                'has_skin_rash': True,
                'has_itching': True
            }
        },
        {
            'name': 'Psoriasis',
            'symptoms': {
                'description': 'red patches of skin covered with thick silvery scales, dry cracked skin that may bleed, itching burning or soreness, thickened pitted or ridged nails, swollen and stiff joints',
                'temperature': '37.0',
                'duration_hours': '4320',
                'severity': '5',
                'has_fever': False,
                'has_skin_rash': True,
                'has_itching': True
            }
        },
        {
            'name': 'Herpes Zoster',
            'symptoms': {
                'description': 'pain burning numbness or tingling, sensitivity to touch, red rash that begins a few days after pain, fluid-filled blisters that break open and crust over, itching, fever, headache, fatigue',
                'temperature': '38.0',
                'duration_hours': '72',
                'severity': '7',
                'has_fever': True,
                'has_skin_rash': True,
                'has_headache': True,
                'has_fatigue': True
            }
        },
        {
            'name': 'Acute Appendicitis',
            'symptoms': {
                'description': 'sudden pain near navel that shifts to lower right abdomen, pain that worsens with coughing walking or jarring movements, nausea and vomiting, loss of appetite, low-grade fever, constipation or diarrhea, abdominal bloating',
                'temperature': '38.0',
                'duration_hours': '24',
                'severity': '8',
                'has_fever': True,
                'has_abdominal_pain': True,
                'has_nausea': True,
                'has_vomiting': True,
                'has_loss_of_appetite': True
            }
        }
    ]
    
    passed = 0
    failed = 0
    results = []
    
    print(f'Testing {len(test_cases)} complex symptom cases...')
    print()
    
    for test in test_cases:
        name = test['name']
        symptoms = test['symptoms']
        
        try:
            response = requests.post(
                'http://localhost:8000/api/gemini/analyze-symptoms',
                json={'symptoms': symptoms},
                timeout=30
            )
            result = response.json()
            
            predicted = result['analysis']['primary_prediction']['condition']
            confidence = result['analysis']['primary_prediction']['confidence']
            ai_model = result['analysis'].get('ai_model', 'unknown')
            complexity = result['analysis'].get('complexity_analysis', {})
            
            status = '✅' if predicted == name else '❌'
            comp_score = complexity.get('score', 0) if complexity else 0
            method = complexity.get('prediction_method', 'unknown') if complexity else 'unknown'
            
            print(f'{status} {name}')
            print(f'   Predicted: {predicted} ({confidence}%)')
            print(f'   Model: {ai_model}')
            print(f'   Complexity: {comp_score:.0f} - Method: {method}')
            print()
            
            if predicted == name:
                passed += 1
            else:
                failed += 1
                
            results.append({
                'expected': name,
                'predicted': predicted,
                'correct': predicted == name,
                'confidence': confidence,
                'model': ai_model,
                'complexity': comp_score
            })
                
        except Exception as e:
            print(f'❌ {name}: ERROR - {str(e)}')
            failed += 1
            results.append({
                'expected': name,
                'predicted': 'ERROR',
                'correct': False,
                'confidence': 0,
                'model': 'error',
                'complexity': 0
            })
    
    print('=' * 80)
    print(f'📊 FINAL RESULTS: {passed}/{len(test_cases)} ({passed/len(test_cases)*100:.1f}%)')
    print(f'✅ Correct: {passed} | ❌ Incorrect: {failed}')
    print('=' * 80)
    
    # Analysis by complexity
    simple_cases = [r for r in results if r['complexity'] < 40]
    complex_cases = [r for r in results if r['complexity'] >= 40]
    
    if simple_cases:
        simple_correct = sum(1 for r in simple_cases if r['correct'])
        print(f'📋 Simple Cases (<40 complexity): {simple_correct}/{len(simple_cases)} ({simple_correct/len(simple_cases)*100:.1f}%)')
    
    if complex_cases:
        complex_correct = sum(1 for r in complex_cases if r['correct'])
        print(f'🧠 Complex Cases (≥40 complexity): {complex_correct}/{len(complex_cases)} ({complex_correct/len(complex_cases)*100:.1f}%)')
    
    print()
    if passed >= 7:
        print('🎉 EXCELLENT: Improved rules achieving high accuracy!')
    elif passed >= 5:
        print('✅ GOOD: Significant improvement with enhanced rules')
    elif passed >= 3:
        print('⚠️  MODERATE: Some improvement, more optimization needed')
    else:
        print('❌ POOR: Further rule refinement required')
    
    # Show failed cases
    failed_cases = [r for r in results if not r['correct'] and r['predicted'] != 'ERROR']
    if failed_cases:
        print('\n🔍 FAILED CASES ANALYSIS:')
        for case in failed_cases:
            print(f'   {case["expected"]} → {case["predicted"]} ({case["confidence"]}%)')

if __name__ == '__main__':
    test_improved_rules()
