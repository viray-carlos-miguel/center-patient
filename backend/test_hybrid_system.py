"""
Test script for Hybrid ML+Rules System
"""
import requests
import json

def test_hybrid_system():
    print('🔬 TESTING HYBRID ML+RULES SYSTEM')
    print('=' * 80)
    
    # Test complex cases
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
        }
    ]
    
    passed = 0
    ml_used = 0
    
    for test in test_cases:
        name = test['name']
        symptoms = test['symptoms']
        
        try:
            response = requests.post(
                'http://localhost:8000/api/gemini/analyze-symptoms',
                json={'symptoms': symptoms},
                timeout=10
            )
            result = response.json()
            
            predicted = result['analysis']['primary_prediction']['condition']
            confidence = result['analysis']['primary_prediction']['confidence']
            ai_model = result['analysis'].get('ai_model', 'unknown')
            complexity = result['analysis'].get('complexity_analysis', {})
            
            status = '✅' if predicted == name else '❌'
            comp_score = complexity.get('score', 0) if complexity else 0
            method = complexity.get('prediction_method', 'unknown') if complexity else 'unknown'
            ml_avail = complexity.get('ml_available', False) if complexity else False
            
            print(f'{status} {name}')
            print(f'   Predicted: {predicted} ({confidence}%)')
            print(f'   Model: {ai_model}')
            print(f'   Complexity: {comp_score:.0f} - Method: {method}')
            print(f'   ML Available: {ml_avail}')
            print()
            
            if predicted == name:
                passed += 1
            
            if 'ml' in ai_model.lower() and 'primary' in ai_model.lower():
                ml_used += 1
                
        except Exception as e:
            print(f'❌ {name}: ERROR - {str(e)}')
    
    print('=' * 80)
    print(f'📊 RESULTS: {passed}/{len(test_cases)} correct')
    print(f'🧠 ML Used: {ml_used}/{len(test_cases)} cases')
    print('=' * 80)
    
    if ml_used > 0:
        print('\n✅ HYBRID SYSTEM IS ACTIVE - ML engine working!')
    else:
        print('\n⚠️ ML engine not active - restart backend to load ML engine')
        print('   Run: uvicorn main:app --reload')

if __name__ == '__main__':
    test_hybrid_system()
