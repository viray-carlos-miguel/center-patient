#!/usr/bin/env python3
"""
Simple Gmail SMTP test
"""

import smtplib
import os
from dotenv import load_dotenv

load_dotenv('e:/coffeejelly/center-patient/backend/.env')

def test_gmail_smtp():
    """Test Gmail SMTP connection"""
    try:
        print("🧪 Testing Gmail SMTP connection...")
        
        email = os.getenv("GMAIL_EMAIL")
        password = os.getenv("GMAIL_APP_PASSWORD")
        
        print(f"📧 Email: {email}")
        print(f"🔑 Password: {'*' * len(password) if password else 'Not configured'}")
        
        # Test SMTP connection
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        
        print("🔐 Trying to login...")
        server.login(email, password)
        print("✅ Gmail SMTP login successful!")
        
        server.quit()
        return True
        
    except Exception as e:
        print(f"❌ Gmail SMTP error: {e}")
        return False

if __name__ == "__main__":
    print("📧 Gmail SMTP Test")
    test_gmail_smtp()
