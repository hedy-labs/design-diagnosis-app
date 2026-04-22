"""
Email Service — SendGrid Integration

Handles email verification and report delivery
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Try to import SendGrid
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Email, To, Content
    SENDGRID_AVAILABLE = True
except ImportError:
    logger.warning("⚠️  sendgrid package not installed. Email will use mock mode.")
    SENDGRID_AVAILABLE = False


class EmailService:
    """Email service with SendGrid or mock fallback"""
    
    def __init__(self):
        self.api_key = os.getenv("SENDGRID_API_KEY")
        self.from_email = os.getenv("SENDGRID_FROM_EMAIL", "noreply@designdiagnosisapp.com")
        
        if self.api_key and SENDGRID_AVAILABLE:
            try:
                self.client = SendGridAPIClient(self.api_key)
                self.mode = "LIVE"
                logger.info("✅ SendGrid initialized (LIVE mode)")
            except Exception as e:
                logger.error(f"❌ SendGrid initialization failed: {e}")
                self.client = None
                self.mode = "MOCK"
        else:
            self.client = None
            self.mode = "MOCK"
            if not self.api_key:
                logger.warning("⚠️  SENDGRID_API_KEY not set. Using mock email mode.")
            if not SENDGRID_AVAILABLE:
                logger.warning("⚠️  sendgrid package not installed. Using mock email mode.")
    
    def send_verification_email(self, email: str, property_name: str, verification_link: str):
        """Send email verification link"""
        try:
            subject = "Verify Your Email — Design Diagnosis Report"
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 5px; text-align: center; }}
                    .content {{ padding: 20px; background: #f9f9f9; border-radius: 5px; margin: 20px 0; }}
                    .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                    .footer {{ color: #999; font-size: 12px; text-align: center; margin-top: 20px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>✨ Design Diagnosis</h1>
                    </div>
                    <div class="content">
                        <p>Hi there!</p>
                        <p>Thank you for submitting your property for a Design Diagnosis report:</p>
                        <p><strong>{property_name}</strong></p>
                        <p>To verify your email and receive your report, click the link below:</p>
                        <a href="{verification_link}" class="button">Verify Email & Get Report</a>
                        <p style="color: #999; font-size: 12px;">Or copy this link: <br><code>{verification_link}</code></p>
                    </div>
                    <div class="footer">
                        <p>This link expires in 24 hours.</p>
                        <p>Questions? Contact us at support@designdiagnosisapp.com</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            if self.mode == "LIVE" and self.client:
                self._send_with_sendgrid(
                    to_email=email,
                    subject=subject,
                    html_content=html_content
                )
            else:
                self._send_mock(
                    to_email=email,
                    subject=subject,
                    message_type="Verification"
                )
        
        except Exception as e:
            logger.error(f"❌ Verification email error: {e}")
    
    def send_report_email(
        self,
        email: str,
        property_name: str,
        pdf_path: str,
        vitality_score: float,
        grade: str,
        report_type: str
    ):
        """Send report email with PDF attachment"""
        try:
            subject = f"Your Design Diagnosis Report — {property_name}"
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 5px; text-align: center; }}
                    .score {{ font-size: 48px; font-weight: bold; color: #667eea; text-align: center; margin: 20px 0; }}
                    .grade {{ font-size: 24px; text-align: center; }}
                    .content {{ padding: 20px; background: #f9f9f9; border-radius: 5px; margin: 20px 0; }}
                    .footer {{ color: #999; font-size: 12px; text-align: center; margin-top: 20px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>✨ Your Design Diagnosis Report is Ready!</h1>
                    </div>
                    <div class="content">
                        <h2>{property_name}</h2>
                        <div class="score">{vitality_score}/100</div>
                        <div class="grade">Grade: <strong>{grade}</strong></div>
                        <p>Your {report_type.upper()} report is attached. Review it to discover:</p>
                        <ul>
                            <li>Your property's vitality score</li>
                            <li>Key design gaps and opportunities</li>
                            <li>Budget-friendly fixes with ROI estimates</li>
                        </ul>
                        <p>Have questions? Reply to this email or visit designdiagnosisapp.com</p>
                    </div>
                    <div class="footer">
                        <p>Powered by Rachel's Interior Design Expertise</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            if self.mode == "LIVE" and self.client:
                self._send_with_sendgrid(
                    to_email=email,
                    subject=subject,
                    html_content=html_content,
                    attachment_path=pdf_path
                )
            else:
                self._send_mock(
                    to_email=email,
                    subject=subject,
                    message_type="Report"
                )
        
        except Exception as e:
            logger.error(f"❌ Report email error: {e}")
    
    def _send_with_sendgrid(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        attachment_path: Optional[str] = None
    ):
        """Send email via SendGrid"""
        try:
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=subject,
                html_content=html_content
            )
            
            # Add attachment if provided
            if attachment_path and os.path.exists(attachment_path):
                with open(attachment_path, 'rb') as f:
                    attachment_data = f.read()
                    message.attachment = message.Attachment(
                        file_content=attachment_data,
                        file_name=os.path.basename(attachment_path),
                        file_type="application/pdf"
                    )
            
            # Send
            response = self.client.send(message)
            logger.info(f"✅ Email sent to {to_email} (Status: {response.status_code})")
        
        except Exception as e:
            logger.error(f"❌ SendGrid send error: {e}")
    
    def _send_mock(self, to_email: str, subject: str, message_type: str):
        """Mock email (log only)"""
        logger.info(f"📧 [MOCK] {message_type} email to {to_email}")
        logger.info(f"📧 [MOCK] Subject: {subject}")
