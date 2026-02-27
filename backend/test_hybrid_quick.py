"""Quick test for Hybrid ML+Rules System"""
import requests

print('🔬 QUICK HYBRID SYSTEM TEST')
print('=' * 80)

# Single test case
test = {
    'description': 'severe headache with stiff neck, high fever, sensitivity to light, confusion, nausea and vomiting',
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

try:
    print('📤 Sending request...')
    response = requests.post(
        'http://localhost:8000/api/gemini/analyze-symptoms',
        json={'symptoms': test},
        timeout=30
    )
    result = response.json()
    
    predicted = result['analysis']['primary_prediction']['condition']
    confidence = result['analysis']['primary_prediction']['confidence']
    ai_model = result['analysis'].get('ai_model', 'unknown')
    complexity = result['analysis'].get('complexity_analysis', {})
    
    print('\n📊 RESULT:')
    print(f'   Expected: Meningitis')
    print(f'   Predicted: {predicted} ({confidence}%)')
    print(f'   Model: {ai_model}')
    
    if complexity:
        print(f'   Complexity Score: {complexity.get("score", 0):.0f}')
        print(f'   Classification: {complexity.get("classification", "unknown")}')
        print(f'   Method: {complexity.get("prediction_method", "unknown")}')
        print(f'   ML Available: {complexity.get("ml_available", False)}')
    
    print('\n' + '=' * 80)
    
    if complexity.get('ml_available'):
        print('✅ ML ENGINE IS ACTIVE IN HYBRID SYSTEM!')
        if 'ml' in ai_model.lower():
            print('✅ ML WAS USED FOR THIS PREDICTION!')
        else:
            print('📋 Rules were used (complexity may be below threshold)')
    else:
        print('⚠️ ML engine not loaded')
        
except Exception as e:
    print(f'\n❌ Error: {e}')
    import traceback
    traceback.print_exc()
