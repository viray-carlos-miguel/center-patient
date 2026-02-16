# backend/email_service.py - Email Service for Medical Center Pro
import aiosmtplib
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class EmailService:
    def __init__(self):
        # Gmail SMTP configuration
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = os.getenv("GMAIL_EMAIL", "medical.center.pro.demo@gmail.com")
        self.sender_password = os.getenv("GMAIL_APP_PASSWORD", "your-app-password-here")
        
        print(f"📧 Email service initialized with: {self.sender_email}")
        print(f"🔑 Password configured: {'Yes' if self.sender_password != 'your-app-password-here' else 'No'}")
        
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """Send email using Gmail SMTP"""
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"Medical Center Pro <{self.sender_email}>"
            message["To"] = to_email
            
            # Add text content (fallback)
            if text_content:
                text_part = MIMEText(text_content, "plain")
                message.attach(text_part)
            
            # Add HTML content
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            # Send email
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._send_sync(message)
            )
            
            print(f"✅ Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email to {to_email}: {e}")
            return False
    
    def _send_sync(self, message):
        """Synchronous email sending for thread pool"""
        import smtplib
        
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                text = message.as_string()
                server.sendmail(self.sender_email, message["To"], text)
                print(f"✅ Email sent via SMTP to {message['To']}")
        except Exception as e:
            print(f"❌ SMTP Error: {e}")
            raise e
    
    def get_doctor_approval_template(self, doctor_name: str, doctor_email: str) -> tuple[str, str, str]:
        """Generate doctor approval email template"""
        subject = "Your Medical Center Pro Account Has Been Approved! 🎉"
        
        text_content = f"""Dear Dr. {doctor_name},

Your doctor account registration has been approved by our admin team.

Login Details:
Email: {doctor_email}
Password: [Your registration password]

You can now access the doctor dashboard and start reviewing patient cases.

To get started:
1. Visit: http://localhost:3000/auth/login
2. Enter your email and password
3. Access your professional dashboard

Best regards,
Medical Center Pro Team
{datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Medical Center Pro - Account Approved</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
        .button {{ display: inline-block; background: #4CAF50; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ text-align: center; color: #666; margin-top: 20px; font-size: 12px; }}
        .details {{ background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 Account Approved!</h1>
            <h2>Medical Center Pro</h2>
        </div>
        
        <div class="content">
            <p>Dear <strong>Dr. {doctor_name}</strong>,</p>
            
            <p>Congratulations! Your doctor account registration has been approved by our admin team. You now have full access to the Medical Center Pro platform.</p>
            
            <div class="details">
                <h3>📋 Account Details:</h3>
                <p><strong>Email:</strong> {doctor_email}<br>
                <strong>Password:</strong> [Your registration password]</p>
            </div>
            
            <h3>🚀 Next Steps:</h3>
            <ol>
                <li>Visit the login page</li>
                <li>Enter your email and password</li>
                <li>Access your professional dashboard</li>
                <li>Start reviewing patient cases</li>
            </ol>
            
            <div style="text-align: center;">
                <a href="http://localhost:3000/auth/login" class="button">Login to Your Account</a>
            </div>
            
            <p><strong>What you can do as a verified doctor:</strong></p>
            <ul>
                <li>✅ Review patient cases with AI assessments</li>
                <li>✅ Provide educational diagnoses</li>
                <li>✅ Create treatment recommendations</li>
                <li>✅ Manage patient records</li>
            </ul>
            
            <p>If you have any questions, please don't hesitate to contact our support team.</p>
            
            <p>Best regards,<br>
            <strong>The Medical Center Pro Team</strong></p>
        </div>
        
        <div class="footer">
            <p>This is an automated message. Please do not reply to this email.</p>
            <p>Medical Center Pro - Advanced Medical Diagnosis Platform</p>
            <p>{datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </div>
    </div>
</body>
</html>
"""
        
        return subject, text_content, html_content
    
    def get_patient_welcome_template(self, patient_name: str, patient_email: str) -> tuple[str, str, str]:
        """Generate patient welcome email template"""
        subject = "Welcome to Medical Center Pro! 🏥"
        
        text_content = f"""Dear {patient_name},

Welcome to Medical Center Pro! Your patient account has been created successfully.

Login Details:
Email: {patient_email}
Password: [Your registration password]

You can now submit symptoms and track your medical cases.

To get started:
1. Visit: http://localhost:3000/auth/login
2. Enter your email and password
3. Submit your symptoms for AI analysis

Best regards,
Medical Center Pro Team
{datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Medical Center Pro - Welcome</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
        .button {{ display: inline-block; background: #4CAF50; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ text-align: center; color: #666; margin-top: 20px; font-size: 12px; }}
        .details {{ background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏥 Welcome!</h1>
            <h2>Medical Center Pro</h2>
        </div>
        
        <div class="content">
            <p>Dear <strong>{patient_name}</strong>,</p>
            
            <p>Welcome to Medical Center Pro! Your patient account has been created successfully. You now have access to our advanced medical diagnosis platform.</p>
            
            <div class="details">
                <h3>📋 Account Details:</h3>
                <p><strong>Email:</strong> {patient_email}<br>
                <strong>Password:</strong> [Your registration password]</p>
            </div>
            
            <h3>🚀 Next Steps:</h3>
            <ol>
                <li>Visit the login page</li>
                <li>Enter your email and password</li>
                <li>Access your patient dashboard</li>
                <li>Submit symptoms for AI analysis</li>
            </ol>
            
            <div style="text-align: center;">
                <a href="http://localhost:3000/auth/login" class="button">Login to Your Account</a>
            </div>
            
            <p><strong>What you can do as a patient:</strong></p>
            <ul>
                <li>✅ Submit symptoms for AI analysis</li>
                <li>✅ Track your medical cases</li>
                <li>✅ Receive educational assessments</li>
                <li>✅ Monitor your health progress</li>
            </ul>
            
            <p>Our AI-powered system will help you understand your symptoms and provide educational insights about your health.</p>
            
            <p>If you have any questions, please don't hesitate to contact our support team.</p>
            
            <p>Best regards,<br>
            <strong>The Medical Center Pro Team</strong></p>
        </div>
        
        <div class="footer">
            <p>This is an automated message. Please do not reply to this email.</p>
            <p>Medical Center Pro - Advanced Medical Diagnosis Platform</p>
            <p>{datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </div>
    </div>
</body>
</html>
"""
        
        return subject, text_content, html_content

# Global email service instance
email_service = EmailService()
