import requests

def test_fixes():
    """Test the recent fixes"""
    
    test_cases = [
        {'name': 'Influenza Type A', 'symptoms': {'description': 'high fever, severe body aches, headache, fatigue, dry cough, sore throat, runny nose', 'temperature': '39.0', 'duration_hours': '48', 'severity': '7', 'has_fever': True, 'has_headache': True, 'has_fatigue': True, 'has_muscle_pain': True, 'has_cough': True}},
        {'name': 'Acute Bronchitis', 'symptoms': {'description': 'persistent cough, mild fever, chest discomfort, fatigue, clear or white sputum', 'temperature': '37.8', 'duration_hours': '120', 'severity': '5', 'has_fever': True, 'has_cough': True, 'has_chest_pain': True, 'has_fatigue': True}},
        {'name': 'Strep Pharyngitis', 'symptoms': {'description': 'severe sore throat, fever, swollen tonsils, difficulty swallowing, swollen lymph nodes', 'temperature': '39.0', 'duration_hours': '48', 'severity': '7', 'has_fever': True, 'has_sore_throat': True}},
        {'name': 'Seasonal Allergies', 'symptoms': {'description': 'sneezing, runny nose, itchy eyes, nasal congestion, post-nasal drip, fatigue', 'temperature': '37.0', 'duration_hours': '240', 'severity': '3', 'has_fever': False, 'has_nasal_congestion': True, 'has_itching': True, 'has_sneezing': True}}
    ]
    
    print('🔧 TESTING RECENT FIXES')
    print('=' * 50)
    
    for test in test_cases:
        try:
            response = requests.post('http://localhost:8000/api/gemini/analyze-symptoms', json={'symptoms': test['symptoms']}, timeout=10)
            result = response.json()
            predicted = result['analysis']['primary_prediction']['condition']
            confidence = result['analysis']['primary_prediction']['confidence']
            status = '✅' if predicted == test['name'] else '❌'
            print(f'{status} {test["name"]}: {predicted} ({confidence}%)')
        except Exception as e:
            print(f'❌ {test["name"]}: ERROR - {str(e)}')

if __name__ == '__main__':
    test_fixes()
