#!/usr/bin/env python3
"""
Test email service directly
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.append('e:/coffeejelly/center-patient/backend')

from email_service import email_service

async def test_email():
    """Test email sending"""
    try:
        print("🧪 Testing email service...")
        print(f"📧 Sender: {email_service.sender_email}")
        print(f"🔑 Password configured: {'Yes' if email_service.sender_password else 'No'}")
        
        # Test email content
        subject = "🧪 Test Email from Medical Center Pro"
        html_content = """
        <h1>Test Email</h1>
        <p>This is a test email from Medical Center Pro.</p>
        <p>If you receive this, the email service is working!</p>
        """
        text_content = "Test email from Medical Center Pro"
        
        # Send test email
        success = await email_service.send_email(
            to_email="carlosviray2004@gmail.com",
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
        
        if success:
            print("✅ Test email sent successfully!")
            print("📧 Check your Gmail inbox for the test email")
        else:
            print("❌ Failed to send test email")
            
    except Exception as e:
        print(f"❌ Error testing email: {e}")

if __name__ == "__main__":
    print("📧 Testing Email Service")
    asyncio.run(test_email())
