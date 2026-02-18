#!/usr/bin/env python3
"""
Debug TF-IDF to verify it's capturing distinctive keywords
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from ml_system.prediction_engine import MedicalPredictionEngine
import numpy as np

def main():
    print("🔍 DEBUGGING TF-IDF KEYWORD CAPTURE")
    print("=" * 50)
    
    engine = MedicalPredictionEngine()
    
    # Test the distinctive keywords for each condition
    test_cases = [
        ('COVID-19', 'covid-19 coronavirus anosmia ageusia loss of taste loss of smell'),
        ('Influenza', 'influenza flu bodyaches myalgia muscle pain'),
        ('Pneumonia', 'pneumonia lunginfection crackles consolidation dyspnea'),
        ('Gastroenteritis', 'gastroenteritis stomachflu vomiting diarrhea nausea'),
        ('Migraine', 'migraine unilateral throbbing photophobia phonophobia'),
        ('Tension Headache', 'tensionheadache bilateral pressure bandlike scalp'),
        ('Urinary Tract Infection', 'uti urinarytract dysuria frequency urgency hematuria'),
        ('Anxiety Disorder', 'anxiety panicattack palpitations nervousness restlessness')
    ]
    
    print("TF-IDF Vocabulary Analysis:")
    print(f"Vocabulary size: {len(engine.data_processor.tfidf_vectorizer.vocabulary_)}")
    print(f"Vocabulary words: {sorted(engine.data_processor.tfidf_vectorizer.vocabulary_.keys())}")
    
    print("\nTF-IDF Vector Analysis:")
    for condition, text in test_cases:
        # Get TF-IDF vector
        tfidf_vector = engine.data_processor.tfidf_vectorizer.transform([text]).toarray()[0]
        
        # Find non-zero features
        non_zero_indices = np.where(tfidf_vector > 0)[0]
        non_zero_values = tfidf_vector[non_zero_indices]
        
        # Map back to vocabulary
        vocab = engine.data_processor.tfidf_vectorizer.vocabulary_
        vocab_reverse = {v: k for k, v in vocab.items()}
        
        words_with_scores = [(vocab_reverse[i], score) for i, score in zip(non_zero_indices, non_zero_values)]
        words_with_scores.sort(key=lambda x: x[1], reverse=True)
        
        print(f"\n{condition}:")
        print(f"  Input: '{text}'")
        print(f"  TF-IDF features: {len(non_zero_indices)} non-zero out of {len(tfidf_vector)}")
        print(f"  Top words: {words_with_scores[:5]}")
        
        # Test prediction
        symptoms = {
            'description': text,
            'severity': 'moderate',
            'temperature': 38.0,
            'duration_hours': 72,
            'age': 35,
            'gender': 'male'
        }
        
        import asyncio
        result = asyncio.run(engine.predict_disease(symptoms))
        predicted = result.get('ml_prediction', {}).get('primary_condition', 'Unknown')
        confidence = result.get('ml_prediction', {}).get('consensus', 0)
        
        print(f"  Prediction: {predicted} ({confidence:.1%})")

if __name__ == "__main__":
    main()
