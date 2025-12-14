"""
Email notification service for alerts.
"""
import smtplib
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from datetime import date
from app.core.config import settings
from app.core.logging import logger


class EmailService:
    """SMTP email sender for notifications and alerts."""
    
    def __init__(self):
        self.host = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.username = settings.SMTP_USERNAME
        self.password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_FROM_EMAIL
        self.from_name = settings.SMTP_FROM_NAME
    
    async def send_email(
        self,
        to: List[str],
        subject: str,
        body: str,
        html: bool = False
    ) -> bool:
        """
        Send email via SMTP.
        
        Args:
            to: List of recipient email addresses
            subject: Email subject
            body: Email body (plain text or HTML)
            html: Whether body is HTML
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = f"{self.from_name} <{self.from_email}>"
            message['To'] = ', '.join(to)
            
            if html:
                message.attach(MIMEText(body, 'html'))
            else:
                message.attach(MIMEText(body, 'plain'))
            
            # Send email asynchronously
            await aiosmtplib.send(
                message,
                hostname=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                start_tls=True
            )
            
            logger.info(f"Email sent successfully to {', '.join(to)}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False
    
    async def send_ingestion_failure_alert(
        self,
        client_name: str,
        source: str,
        run_date: date,
        error_message: str,
        admin_emails: List[str]
    ) -> bool:
        """Send alert when data ingestion fails."""
        
        subject = f"Data Ingestion Failed: {source} - {client_name}"
        
        body = f"""
        <h2>Data Ingestion Failure Alert</h2>
        <p><strong>Client:</strong> {client_name}</p>
        <p><strong>Source:</strong> {source}</p>
        <p><strong>Date:</strong> {run_date}</p>
        <p><strong>Error:</strong> {error_message}</p>
        <p>Please check the ingestion logs for more details.</p>
        """
        
        return await self.send_email(admin_emails, subject, body, html=True)
    
    async def send_missing_file_alert(
        self,
        client_name: str,
        source: str,
        expected_date: date,
        admin_emails: List[str]
    ) -> bool:
        """Send alert when expected data file is missing."""
        
        subject = f"Missing Data File: {source} - {client_name}"
        
        body = f"""
        <h2>Missing Data File Alert</h2>
        <p><strong>Client:</strong> {client_name}</p>
        <p><strong>Source:</strong> {source}</p>
        <p><strong>Expected Date:</strong> {expected_date}</p>
        <p>The expected data file was not found. Please verify the data delivery.</p>
        """
        
        return await self.send_email(admin_emails, subject, body, html=True)
    
    async def send_validation_error_alert(
        self,
        client_name: str,
        source: str,
        run_date: date,
        errors: List[str],
        admin_emails: List[str]
    ) -> bool:
        """Send alert when data validation fails."""
        
        subject = f"Data Validation Errors: {source} - {client_name}"
        
        error_list = '<br>'.join([f"• {error}" for error in errors])
        
        body = f"""
        <h2>Data Validation Error Alert</h2>
        <p><strong>Client:</strong> {client_name}</p>
        <p><strong>Source:</strong> {source}</p>
        <p><strong>Date:</strong> {run_date}</p>
        <h3>Errors:</h3>
        <p>{error_list}</p>
        <p>Please review and correct the data issues.</p>
        """
        
        return await self.send_email(admin_emails, subject, body, html=True)


# Singleton instance
email_service = EmailService()
