# SMTP Email Module Testing Guide

## **Module Overview**

The Email module (`app/core/email.py`) provides SMTP email functionality for sending automated alerts and notifications to administrators and users.

### **Purpose**
- Send ingestion failure alerts when data processing fails
- Send missing file alerts when expected data is not received
- Send validation error alerts when data quality issues are detected
- Support async/non-blocking email sending

### **Key Components**
- **EmailService class**: Main email sender using `aiosmtplib`
- **Configuration**: SMTP settings from environment variables
- **Templates**: HTML email templates for different alert types

---

## **Configuration Requirements**

### **1. Environment Variables (.env file)**

```env
# SMTP Configuration
SMTP_HOST=smtp.gmail.com              # For Gmail
SMTP_PORT=587                         # TLS port
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password       # Gmail App Password (not regular password)
SMTP_FROM_EMAIL=noreply@yourdomain.com
SMTP_FROM_NAME=Performance Dashboard Alert
```

### **2. Gmail App Password Setup** (if using Gmail)

1. Go to Google Account Settings → Security
2. Enable 2-Factor Authentication
3. Go to "App passwords" section
4. Generate new app password for "Mail"
5. Copy the 16-character password (no spaces)
6. Use this in `SMTP_PASSWORD` environment variable

### **3. Alternative SMTP Providers**

**SendGrid:**
```env
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=your-sendgrid-api-key
```

**AWS SES:**
```env
SMTP_HOST=email-smtp.us-east-1.amazonaws.com
SMTP_PORT=587
SMTP_USERNAME=your-ses-username
SMTP_PASSWORD=your-ses-password
```

**Mailgun:**
```env
SMTP_HOST=smtp.mailgun.org
SMTP_PORT=587
SMTP_USERNAME=postmaster@yourdomain.com
SMTP_PASSWORD=your-mailgun-password
```

---

## **Testing Methods**

### **Method 1: Direct Function Testing (Python Script)**

Create a test script: `test_email.py`

```python
import asyncio
from app.core.email import email_service
from datetime import date

async def test_basic_email():
    """Test basic email sending."""
    print("Testing basic email...")
    
    result = await email_service.send_email(
        to=["your-test-email@gmail.com"],
        subject="Test Email from Dashboard",
        body="This is a test email. If you receive this, SMTP is working!",
        html=False
    )
    
    print(f"Email sent: {result}")

async def test_ingestion_failure_alert():
    """Test ingestion failure alert."""
    print("Testing ingestion failure alert...")
    
    result = await email_service.send_ingestion_failure_alert(
        client_name="Test Client",
        source="surfside",
        run_date=date.today(),
        error_message="Database connection timeout after 30 seconds",
        admin_emails=["your-admin-email@gmail.com"]
    )
    
    print(f"Alert sent: {result}")

async def test_validation_error_alert():
    """Test validation error alert."""
    print("Testing validation error alert...")
    
    errors = [
        "Row 5: Missing required column 'Campaign'",
        "Row 12: Invalid date format '2025-13-45'",
        "Row 18: Impressions must be positive integer"
    ]
    
    result = await email_service.send_validation_error_alert(
        client_name="Test Client",
        source="facebook",
        run_date=date.today(),
        errors=errors,
        admin_emails=["your-admin-email@gmail.com"]
    )
    
    print(f"Validation alert sent: {result}")

async def test_missing_file_alert():
    """Test missing file alert."""
    print("Testing missing file alert...")
    
    result = await email_service.send_missing_file_alert(
        client_name="Test Client",
        source="vibe",
        expected_date=date.today(),
        admin_emails=["your-admin-email@gmail.com"]
    )
    
    print(f"Missing file alert sent: {result}")

async def run_all_tests():
    """Run all email tests."""
    print("=" * 60)
    print("SMTP EMAIL MODULE TESTS")
    print("=" * 60)
    
    await test_basic_email()
    print()
    
    await test_ingestion_failure_alert()
    print()
    
    await test_validation_error_alert()
    print()
    
    await test_missing_file_alert()
    print()
    
    print("=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(run_all_tests())
```

**Run the test:**
```powershell
cd c:\Users\shame\Desktop\mega\server
python test_email.py
```

---

### **Method 2: Testing via API Endpoints (Manual Trigger)**

Since email alerts are triggered by events, you can test them by triggering those events:

#### **Test 1: Trigger Ingestion Failure**

1. Upload a corrupted Surfside file:
   ```csv
   Invalid,Headers,Here
   Bad,Data,Values
   ```

2. The ETL pipeline will fail and send an email alert to admins

#### **Test 2: Trigger Validation Error**

1. Upload a Facebook CSV missing required columns
2. Parser will detect validation errors
3. Email alert sent with specific error details

---

### **Method 3: Using Postman to Trigger ETL Jobs**

Create an admin endpoint to manually trigger email tests:

**Add to `app/core/router.py` (create if doesn't exist):**

```python
from fastapi import APIRouter, Depends
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.core.email import email_service
from datetime import date

router = APIRouter(prefix="/system", tags=["System"])

@router.post("/test-email")
async def test_email(
    email: str,
    current_user: User = Depends(get_current_user)
):
    """Test email sending (admin only)."""
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Admin only")
    
    result = await email_service.send_email(
        to=[email],
        subject="Test Email from Dashboard",
        body="SMTP configuration is working correctly!",
        html=False
    )
    
    return {"sent": result, "to": email}
```

**Postman Test:**
- POST `http://localhost:8000/api/v1/system/test-email?email=your@email.com`
- Headers: `Authorization: Bearer <your_token>`

---

## **Verification Checklist**

### **Pre-Test Checks**
- [ ] SMTP credentials configured in `.env`
- [ ] Server running: `uvicorn app.main:app --reload`
- [ ] Valid test email address available
- [ ] Gmail App Password generated (if using Gmail)

### **Email Delivery Checks**
- [ ] Basic email received successfully
- [ ] HTML formatting preserved in alerts
- [ ] Subject line correct
- [ ] Sender name displays correctly
- [ ] Email not in spam folder
- [ ] All recipient addresses received email

### **Alert Content Checks**
- [ ] Ingestion failure alert includes: client name, source, date, error message
- [ ] Validation error alert includes: client name, source, error list
- [ ] Missing file alert includes: client name, source, expected date
- [ ] All placeholders replaced with actual values

---

## **Troubleshooting**

### **Error: "SMTPAuthenticationError"**
**Cause:** Invalid credentials or 2FA not enabled for Gmail
**Solution:**
- Enable 2-Factor Authentication in Google Account
- Generate App Password
- Use App Password in SMTP_PASSWORD (not regular password)

### **Error: "Connection refused"**
**Cause:** Wrong host or port
**Solution:**
- Verify SMTP_HOST and SMTP_PORT
- For Gmail: smtp.gmail.com:587
- Check firewall settings

### **Error: "Timeout"**
**Cause:** Network or firewall blocking SMTP
**Solution:**
- Test with telnet: `telnet smtp.gmail.com 587`
- Check corporate firewall settings
- Try port 465 (SSL) instead of 587 (TLS)

### **Emails Going to Spam**
**Solution:**
- Add sender to contact list
- Configure SPF/DKIM records for your domain
- Use authenticated SMTP provider (SendGrid, AWS SES)

### **Error: "Sender address rejected"**
**Cause:** FROM_EMAIL doesn't match authenticated account
**Solution:**
- Use same email as SMTP_USERNAME
- Or verify domain ownership with provider

---

## **Production Recommendations**

1. **Use Professional SMTP Service**
   - SendGrid (99.9% uptime SLA)
   - AWS SES (high deliverability)
   - Mailgun (developer-friendly)

2. **Email Monitoring**
   - Log all email attempts
   - Track delivery failures
   - Set up dead letter queue for retries

3. **Rate Limiting**
   - Implement exponential backoff for retries
   - Batch emails when possible
   - Respect provider rate limits

4. **Templates**
   - Use HTML templates with CSS
   - Include company branding
   - Add unsubscribe links (if marketing emails)

5. **Security**
   - Never log SMTP passwords
   - Use environment variables only
   - Rotate credentials regularly
   - Enable TLS/SSL encryption

---

## **Expected Test Results**

### **Successful Test Output:**
```
==========================================================
SMTP EMAIL MODULE TESTS
==========================================================
Testing basic email...
Email sent: True

Testing ingestion failure alert...
Alert sent: True

Testing validation error alert...
Validation alert sent: True

Testing missing file alert...
Missing file alert sent: True

==========================================================
ALL TESTS COMPLETED
==========================================================
```

### **Sample Email (HTML Alert):**
```html
Subject: Data Ingestion Failed: surfside - Test Client

<h2>Data Ingestion Failure Alert</h2>
<p><strong>Client:</strong> Test Client</p>
<p><strong>Source:</strong> surfside</p>
<p><strong>Date:</strong> 2025-12-15</p>
<p><strong>Error:</strong> Database connection timeout after 30 seconds</p>
<p>Please check the ingestion logs for more details.</p>
```

---

## **Integration Points**

Emails are automatically sent from:
1. **ETL Orchestrator** (`app/etl/orchestrator.py`)
   - On pipeline failures
   - On validation errors

2. **Daily Ingestion Jobs** (`app/jobs/daily_ingestion.py`)
   - When Surfside/Vibe ingestion fails
   - When expected files are missing

3. **Manual Triggers**
   - Test endpoints for admins
   - Debug/troubleshooting scenarios
