#!/usr/bin/env python3
"""
Test script for doctor registration
"""

import requests
import json

def test_doctor_registration():
    """Test doctor registration directly"""
    url = "http://localhost:8000/api/auth/register"
    
    # Test data
    doctor_data = {
        "first_name": "Test",
        "last_name": "Doctor",
        "email": "test.doctor@medical.com",
        "password": "Doctor@123",
        "confirm_password": "Doctor@123",
        "medical_license": "MED123456",
        "specialization": "Neurology",
        "agree_to_terms": True,
        "acknowledge_educational": True
    }
    
    try:
        print("🔍 Testing doctor registration...")
        response = requests.post(url, json=doctor_data, headers={'Content-Type': 'application/json'})
        
        print(f"✅ Status Code: {response.status_code}")
        print(f"✅ Response: {response.json()}")
        
        if response.status_code == 200:
            print("🎉 Doctor registration successful!")
            return True
        else:
            print(f"❌ Error: {response.json()}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Doctor Registration")
    success = test_doctor_registration()
    if success:
        print("🎉 Doctor registration test passed!")
    else:
        print("❌ Doctor registration test failed!")
