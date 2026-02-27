import requests

def test_diverse_cases():
    """Test diverse medical conditions beyond the main 10"""
    
    test_cases = [
        {
            'name': 'COVID-19',
            'symptoms': {
                'description': 'loss of taste and smell with dry cough and fever',
                'temperature': '38.5',
                'has_fever': True,
                'has_cough': True,
                'has_loss_taste': True,
                'has_loss_smell': True
            }
        },
        {
            'name': 'Strep Throat',
            'symptoms': {
                'description': 'severe sore throat with fever and swollen glands',
                'temperature': '39.0',
                'has_fever': True,
                'has_sore_throat': True
            }
        },
        {
            'name': 'Heart Attack',
            'symptoms': {
                'description': 'crushing chest pain radiating to left arm with sweating',
                'has_chest_pain': True,
                'severity': '10'
            }
        },
        {
            'name': 'Asthma',
            'symptoms': {
                'description': 'wheezing and shortness of breath with chest tightness',
                'has_wheezing': True,
                'has_shortness_of_breath': True,
                'has_chest_tightness': True
            }
        },
        {
            'name': 'Type 2 Diabetes',
            'symptoms': {
                'description': 'excessive thirst and frequent urination with fatigue',
                'has_excessive_thirst': True,
                'has_frequent_urination': True,
                'has_fatigue': True
            }
        }
    ]
    
    print('🏥 TESTING DIVERSE MEDICAL CONDITIONS')
    print('=' * 60)
    
    passed = 0
    failed = 0
    
    for test in test_cases:
        try:
            response = requests.post(
                'http://localhost:8000/api/gemini/analyze-symptoms',
                json={'symptoms': test['symptoms']},
                timeout=10
            )
            result = response.json()
            predicted = result['analysis']['primary_prediction']['condition']
            confidence = result['analysis']['primary_prediction']['confidence']
            
            status = '✅' if predicted == test['name'] else '❌'
            print(f'{status} {test["name"]}: {predicted} ({confidence}%)')
            
            if predicted == test['name']:
                passed += 1
            else:
                failed += 1
                
        except Exception as e:
            print(f'❌ {test["name"]}: ERROR - {str(e)}')
            failed += 1
    
    print('=' * 60)
    print(f'📊 DIVERSE TEST RESULTS: {passed}/{len(test_cases)} ({passed/len(test_cases)*100:.1f}%)')
    print(f'✅ Correct: {passed} | ❌ Incorrect: {failed}')
    
    return passed, failed

if __name__ == '__main__':
    test_diverse_cases()
