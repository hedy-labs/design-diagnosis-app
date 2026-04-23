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
        # Use a more trusted sender email (Rachel's domain if available)
        self.from_email = os.getenv("SENDGRID_FROM_EMAIL", "support@roomsbyrachel.com")
        
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
            subject = "Your Design Diagnosis Report is Ready!"
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; color: #333; line-height: 1.6; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px 20px; border-radius: 8px; text-align: center; }}
                    .header h1 {{ margin: 0; font-size: 28px; }}
                    .header p {{ margin: 10px 0 0 0; opacity: 0.9; }}
                    .content {{ padding: 30px; background: #f9f9f9; border-radius: 8px; margin: 20px 0; }}
                    .cta-button {{ 
                        display: inline-block; 
                        background: #667eea; 
                        color: white; 
                        padding: 14px 28px; 
                        text-decoration: none; 
                        border-radius: 6px; 
                        margin: 20px 0;
                        font-weight: bold;
                        cursor: pointer;
                    }}
                    .cta-button:hover {{ background: #764ba2; }}
                    .footer {{ color: #999; font-size: 12px; text-align: center; margin-top: 30px; }}
                    .divider {{ border-top: 1px solid #ddd; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>✨ Design Diagnosis</h1>
                        <p>Your Property Report is Ready</p>
                    </div>
                    <div class="content">
                        <p>Hi there,</p>
                        <p>Thank you for submitting your property for a Design Diagnosis analysis:</p>
                        <p style="font-weight: bold; color: #667eea;">{property_name}</p>
                        <p>To verify your email and access your personalized report with vitality score and design recommendations, click the button below:</p>
                        <center>
                            <a href="{verification_link}" class="cta-button">Verify Email & View Report</a>
                        </center>
                        <p style="color: #666; font-size: 13px; text-align: center;">Or copy and paste this link:<br><code style="background: #fff; padding: 8px; display: inline-block; border-radius: 4px; margin-top: 10px;">{verification_link}</code></p>
                        <div class="divider"></div>
                        <p style="color: #999; font-size: 12px;">
                            This verification link expires in 24 hours for security purposes.
                        </p>
                    </div>
                    <div class="footer">
                        <p>Design Diagnosis • Powered by Rooms by Rachel</p>
                        <p>Questions? Reply to this email or visit <strong>designdiagnosisapp.com</strong></p>
                        <p style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #ddd;">
                            © 2026 Rooms by Rachel. All rights reserved.
                        </p>
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
            # Ensure pdf_path is absolute and in the reports directory
            if not os.path.isabs(pdf_path):
                reports_dir = os.getenv("REPORT_OUTPUT_DIR", "./reports")
                pdf_path = os.path.join(reports_dir, os.path.basename(pdf_path))
            
            logger.info(f"📎 Looking for attachment at: {pdf_path}")
            
            subject = f"Your Design Diagnosis Report — {property_name} ({grade})"
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; color: #333; line-height: 1.6; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px 20px; border-radius: 8px; text-align: center; }}
                    .header h1 {{ margin: 0; font-size: 28px; }}
                    .score-card {{ background: #f0f4ff; border-left: 4px solid #667eea; padding: 20px; margin: 20px 0; border-radius: 6px; text-align: center; }}
                    .score {{ font-size: 56px; font-weight: bold; color: #667eea; margin: 10px 0; }}
                    .grade {{ font-size: 20px; color: #764ba2; font-weight: bold; }}
                    .content {{ padding: 30px; background: #f9f9f9; border-radius: 8px; margin: 20px 0; }}
                    .content ul {{ margin: 15px 0; padding-left: 20px; }}
                    .content li {{ margin: 8px 0; }}
                    .next-steps {{ background: #e8f5e9; border-left: 4px solid #4caf50; padding: 15px; margin: 20px 0; border-radius: 4px; }}
                    .footer {{ color: #999; font-size: 12px; text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>✨ Your Design Diagnosis Report is Ready!</h1>
                        <p>{property_name}</p>
                    </div>
                    <div class="score-card">
                        <div class="score">{vitality_score}</div>
                        <div>Vitality Score (out of 100)</div>
                        <div class="grade">Grade: {grade}</div>
                    </div>
                    <div class="content">
                        <h2 style="color: #667eea; margin-top: 0;">What's in Your Report</h2>
                        <ul>
                            <li><strong>Vitality Score Breakdown</strong> — Guest Comfort, Photos, Design Assessment</li>
                            <li><strong>Key Recommendations</strong> — Prioritized fixes for maximum impact</li>
                            <li><strong>Design Insights</strong> — Professional analysis grounded in interior design expertise</li>
                        </ul>
                        <div class="next-steps">
                            <strong>📋 Next Steps:</strong><br>
                            1. Review your attached PDF report<br>
                            2. Prioritize fixes based on impact & budget<br>
                            3. Want personalized guidance? Reply to schedule a consultation
                        </div>
                    </div>
                    <div class="footer">
                        <p>Design Diagnosis • Powered by Rachel's Interior Design Expertise</p>
                        <p>Questions? Reply to this email or visit <strong>designdiagnosisapp.com</strong></p>
                        <p style="margin-top: 15px;">© 2026 Rooms by Rachel. All rights reserved.</p>
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
