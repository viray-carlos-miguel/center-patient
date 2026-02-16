# Gmail Email Setup for Medical Center Pro

## 📧 Configure Gmail SMTP for Email Notifications

### 🔑 Step 1: Enable 2-Factor Authentication
1. Go to your Gmail account
2. Click on your profile → "Manage your Google Account"
3. Go to "Security" tab
4. Enable "2-Step Verification"

### 🔑 Step 2: Generate App Password
1. Go to Google Account → Security
2. Scroll down to "Signing in to Google"
3. Click on "App passwords"
4. Select "Mail" for the app
5. Select "Other (Custom name)" for the device
6. Name it: "Medical Center Pro"
7. Click "Generate"
8. Copy the 16-character password (this is your `GMAIL_APP_PASSWORD`)

### 🔑 Step 3: Create Gmail Account (Optional)
If you don't have a Gmail account for testing:
1. Create a new Gmail account: `medical.center.pro.demo@gmail.com`
2. Follow steps 1-2 above to generate app password

### 🔧 Step 4: Configure Environment Variables
Create or update `backend/.env` file:

```env
# Email Configuration (Gmail SMTP)
GMAIL_EMAIL=medical.center.pro.demo@gmail.com
GMAIL_APP_PASSWORD=your-16-character-app-password-here
```

### 🧪 Step 5: Test Email Functionality
1. Restart the backend server
2. Register a new patient account
3. Check your Gmail inbox for welcome email
4. Register a new doctor account
5. Login as admin and verify the doctor
6. Check doctor's Gmail for approval email

### 📧 Email Templates

#### Patient Welcome Email:
- Subject: "Welcome to Medical Center Pro! 🏥"
- Sent immediately after patient registration
- Contains login instructions and features

#### Doctor Approval Email:
- Subject: "Your Medical Center Pro Account Has Been Approved! 🎉"
- Sent when admin verifies doctor account
- Contains login instructions and dashboard features

### 🔍 Troubleshooting

#### Common Issues:
1. **"Authentication failed"**: Check app password (not regular password)
2. **"SMTP server not responding"**: Check Gmail SMTP settings
3. **"Email not received"**: Check spam folder in Gmail

#### Debug Commands:
```bash
# Check backend logs for email status
python backend/main.py

# Look for these messages:
✅ Welcome email sent to: patient@email.com
✅ Approval email sent to: doctor@email.com
❌ Failed to send email to: email@email.com
```

### 🎯 Testing Email Flow

#### Complete Test:
1. **Patient Registration** → Welcome email immediately
2. **Doctor Registration** → Pending verification (no email yet)
3. **Admin Verification** → Approval email sent
4. **Doctor Login** → Full access granted

#### Email Addresses to Test:
- Patient: `test.patient@gmail.com`
- Doctor: `test.doctor@gmail.com`
- Admin: `admin@medical.com`

### 📱 Mobile Email Access
Emails can be checked on:
- Gmail mobile app
- Gmail web interface
- Any email client (with IMAP/POP3)

### 🔒 Security Notes
- App passwords are specific to your Google account
- Store app passwords securely in environment variables
- Never commit app passwords to version control
- Use a dedicated Gmail account for development

### 🚀 Ready to Test!
Once configured, the email system will send real emails that you can check in your Gmail app or any email client!
