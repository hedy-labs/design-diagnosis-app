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
                    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif; color: #333; line-height: 1.6; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 30px; border-radius: 8px; text-align: center; }}
                    .header h1 {{ margin: 0; font-size: 28px; font-weight: bold; }}
                    .header p {{ margin: 10px 0 0 0; opacity: 0.95; font-size: 16px; }}
                    .content {{ padding: 30px; background: #f9f9f9; border-radius: 8px; margin: 20px 0; }}
                    .content p {{ margin: 12px 0; color: #555; }}
                    .property-name {{ font-weight: bold; color: #667eea; font-size: 16px; margin: 15px 0; }}
                    .cta-button {{ 
                        display: inline-block; 
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white; 
                        padding: 16px 36px; 
                        text-decoration: none; 
                        border-radius: 6px; 
                        margin: 25px 0;
                        font-weight: bold;
                        font-size: 16px;
                        cursor: pointer;
                    }}
                    .cta-button:hover {{ opacity: 0.9; }}
                    .link-code {{ background: white; padding: 12px; border-radius: 4px; display: inline-block; margin-top: 10px; font-family: monospace; font-size: 12px; word-break: break-all; max-width: 100%; }}
                    .features {{ background: #f0f4ff; border-left: 4px solid #667eea; padding: 20px; margin: 20px 0; border-radius: 6px; }}
                    .features h3 {{ color: #667eea; margin-top: 0; font-size: 16px; }}
                    .features ul {{ margin: 10px 0; padding-left: 20px; }}
                    .features li {{ margin: 8px 0; color: #555; }}
                    .footer {{ color: #999; font-size: 13px; text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; }}
                    .footer p {{ margin: 8px 0; }}
                    .footer a {{ color: #667eea; text-decoration: none; }}
                    .footer a:hover {{ text-decoration: underline; }}
                    .social-links {{ margin-top: 15px; }}
                    .social-links a {{ display: inline-block; margin: 0 8px; color: #667eea; text-decoration: none; font-weight: 500; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>✨ Design Diagnosis</h1>
                        <p>Your Property Analysis Awaits</p>
                    </div>
                    
                    <div class="content">
                        <p>Hi there!</p>
                        <p>Thank you for submitting your property for a Design Diagnosis analysis. We're excited to share your results!</p>
                        
                        <div class="property-name">{property_name}</div>
                        
                        <p>Click the button below to verify your email and instantly access your personalized report:</p>
                        
                        <center>
                            <a href="{verification_link}" class="cta-button">Verify Email & Get Report</a>
                        </center>
                        
                        <p style="color: #666; font-size: 12px; text-align: center;">Or copy and paste this link:<br><code class="link-code">{verification_link}</code></p>
                        
                        <div class="features">
                            <h3>📊 What You'll Receive:</h3>
                            <ul>
                                <li><strong>Vitality Score</strong> (0-100) measuring your listing's design quality</li>
                                <li><strong>Grade (A-F)</strong> with professional assessment</li>
                                <li><strong>Priority Recommendations</strong> ranked by impact</li>
                                <li><strong>Expert Analysis</strong> grounded in interior design principles</li>
                            </ul>
                        </div>
                        
                        <p style="color: #999; font-size: 12px;">
                            ⏰ This verification link expires in 24 hours for security.
                        </p>
                    </div>
                    
                    <div class="footer">
                        <p><strong>Rooms by Rachel</strong></p>
                        <p>Design Diagnosis — Expert Analysis for Short-Term Rentals</p>
                        
                        <div class="social-links">
                            <a href="https://tiktok.com/@rooms.by.rachel">TikTok</a> • 
                            <a href="https://instagram.com/@rooms.by.rachel">Instagram</a> • 
                            <a href="https://roomsbyrachel.com">Website</a>
                        </div>
                        
                        <p style="margin-top: 15px;">Questions? <a href="mailto:support@designdiagnosisapp.com">Contact us</a></p>
                        <p>© 2026 Rooms by Rachel. All rights reserved.</p>
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
            # VALIDATE REPORT TYPE STRICTLY
            if not report_type or report_type not in ["free", "premium"]:
                logger.error(f"❌ CRITICAL: send_report_email() received invalid report_type='{report_type}' (expected 'free' or 'premium'). Defaulting to 'free'.")
                report_type = "free"
            
            logger.info(f"📧 SENDING {report_type.upper()} REPORT EMAIL")
            logger.info(f"   → Recipient: {email}")
            logger.info(f"   → Property: {property_name}")
            logger.info(f"   → Score: {vitality_score}/100 (Grade {grade})")
            
            # Ensure pdf_path is absolute and in the reports directory
            if not os.path.isabs(pdf_path):
                reports_dir = os.getenv("REPORT_OUTPUT_DIR", "./reports")
                pdf_path = os.path.join(reports_dir, os.path.basename(pdf_path))
            
            logger.info(f"📎 PDF attachment: {pdf_path}")
            
            subject = f"Your Design Diagnosis Report — {property_name} ({grade})"
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif; color: #333; line-height: 1.6; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 30px; border-radius: 8px; text-align: center; }}
                    .header h1 {{ margin: 0; font-size: 28px; font-weight: bold; }}
                    .header p {{ margin: 10px 0 0 0; opacity: 0.95; font-size: 16px; }}
                    .score-card {{ background: #f0f4ff; border-left: 4px solid #667eea; padding: 30px; margin: 20px 0; border-radius: 8px; text-align: center; }}
                    .score {{ font-size: 56px; font-weight: bold; color: #667eea; margin: 10px 0; }}
                    .grade {{ font-size: 18px; color: #764ba2; font-weight: bold; margin-top: 10px; }}
                    .content {{ padding: 30px; background: #f9f9f9; border-radius: 8px; margin: 20px 0; }}
                    .content h2 {{ color: #667eea; margin-top: 0; font-size: 20px; }}
                    .content ul {{ margin: 15px 0; padding-left: 20px; }}
                    .content li {{ margin: 10px 0; color: #555; }}
                    .cta-button {{
                        display: inline-block;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 14px 32px;
                        text-decoration: none;
                        border-radius: 6px;
                        font-weight: bold;
                        margin: 20px 0;
                        font-size: 16px;
                    }}
                    .next-steps {{ background: #e8f5e9; border-left: 4px solid #4caf50; padding: 20px; margin: 20px 0; border-radius: 6px; }}
                    .next-steps strong {{ color: #2e7d32; display: block; margin-bottom: 10px; }}
                    .next-steps ol {{ margin: 10px 0; padding-left: 20px; color: #555; }}
                    .next-steps li {{ margin: 8px 0; }}
                    .footer {{ color: #999; font-size: 13px; text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; }}
                    .footer p {{ margin: 8px 0; }}
                    .footer a {{ color: #667eea; text-decoration: none; }}
                    .footer a:hover {{ text-decoration: underline; }}
                    .social-links {{ margin-top: 15px; }}
                    .social-links a {{ display: inline-block; margin: 0 8px; color: #667eea; text-decoration: none; font-weight: 500; }}
                    .divider {{ border-top: 1px solid #e5e7eb; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>✨ Your Design Diagnosis Report</h1>
                        <p>Complete Analysis for: <strong>{property_name}</strong></p>
                    </div>
                    
                    <div class="score-card">
                        <div>Your Vitality Score</div>
                        <div class="score">{vitality_score}/100</div>
                        <div class="grade">Grade: {grade}</div>
                    </div>
                    
                    <div class="content">
                        <h2>📊 What's Inside Your Report</h2>
                        <ul>
                            <li><strong>Vitality Score Breakdown</strong> — Guest Comfort, Photo Quality, Design Assessment</li>
                            <li><strong>Priority Recommendations</strong> — Ranked by impact and implementation cost</li>
                            <li><strong>Expert Design Insights</strong> — Grounded in professional interior design principles</li>
                            <li><strong>Action Plan</strong> — Clear next steps to improve your listing</li>
                        </ul>
                        
                        <center>
                            <a href="https://designdiagnosisapp.com" class="cta-button">View Full Dashboard</a>
                        </center>
                        
                        <div class="next-steps">
                            <strong>🚀 Here's What to Do Next:</strong>
                            <ol>
                                <li>Download and review your attached PDF report</li>
                                <li>Prioritize fixes based on your budget and timeline</li>
                                <li>Start implementing high-impact recommendations</li>
                                <li>Track your progress and re-submit in 30 days</li>
                            </ol>
                            <p style="margin-top: 15px; color: #2e7d32;"><strong>Need help?</strong> Reply to this email to schedule a consultation with Rachel ($99 for 15 min).</p>
                        </div>
                    </div>
                    
                    <div class="footer">
                        <p><strong>Rooms by Rachel</strong></p>
                        <p>Design Diagnosis — Expert Analysis for Short-Term Rentals</p>
                        
                        <div class="social-links">
                            <a href="https://tiktok.com/@rooms.by.rachel">TikTok</a> • 
                            <a href="https://instagram.com/rooms.by.rachel">Instagram</a> • 
                            <a href="https://roomsbyrachel.com">Website</a>
                        </div>
                        
                        <div class="divider"></div>
                        
                        <p>Questions? <a href="mailto:support@designdiagnosisapp.com">Contact us</a></p>
                        <p>© 2026 Rooms by Rachel. All rights reserved.</p>
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
