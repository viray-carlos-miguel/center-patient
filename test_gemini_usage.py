#!/usr/bin/env python3
"""
Test script to verify Gemini API usage and generate trackable requests
"""

import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
import time

load_dotenv('backend/.env')

def test_gemini_api():
    """Test Gemini API with multiple requests to generate usage data"""
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found")
        return
    
    print(f"✅ Using API key: {api_key[:20]}...")
    
    # Configure Gemini
    genai.configure(api_key=api_key)
    
    # List available models first
    print("🔍 Checking available models...")
    models = genai.list_models()
    for model in models:
        print(f"  - {model.name}")
    
    # Use the correct model name
    model = genai.GenerativeModel('models/gemini-2.0-flash')
    
    # Test requests that should be trackable
    test_prompts = [
        "Analyze symptoms: headache, fever, cough for medical diagnosis",
        "Patient has fatigue and nausea, provide medical assessment",
        "Evaluate chest pain and shortness of breath symptoms",
        "Medical analysis of dizziness and blurred vision",
        "Assess abdominal pain and digestive symptoms"
    ]
    
    print(f"🚀 Making {len(test_prompts)} API requests...")
    
    for i, prompt in enumerate(test_prompts, 1):
        try:
            print(f"\n📝 Request {i}: {prompt[:50]}...")
            
            response = model.generate_content(f"""
            You are a medical AI assistant. {prompt}
            
            Provide a brief JSON response:
            {{
                "analysis": "Brief medical analysis",
                "urgency": "low/medium/high",
                "confidence": 0.85
            }}
            """)
            
            print(f"✅ Response {i}: {response.text[:100]}...")
            time.sleep(1)  # Small delay between requests
            
        except Exception as e:
            print(f"❌ Error in request {i}: {e}")
    
    print(f"\n🎯 Test complete! Check Google AI Studio for usage data.")
    print("📍 Go to: https://aistudio.google.com/app/apikey")
    print(f"🔑 Look for API key: {api_key[:20]}...")

if __name__ == "__main__":
    test_gemini_api()
