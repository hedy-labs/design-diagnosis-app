"""
Design Diagnosis Email Service

Handles:
- Email verification (sends link with token)
- PDF report delivery
- Transactional emails (payment confirmation, etc.)

Uses SendGrid for reliability.
"""

import os
from typing import Optional
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, ContentId
import base64


class EmailService:
    """SendGrid-based email service"""
    
    def __init__(self, api_key: Optional[str] = None, from_email: str = "hello@designdiagnosis.com"):
        self.api_key = api_key or os.getenv("SENDGRID_API_KEY", "SG.test_key")
        self.from_email = from_email
        self.client = SendGridAPIClient(self.api_key) if self.api_key.startswith("SG.") else None
    
    def send_verification_email(
        self, to_email: str, verification_link: str, property_name: str = "Your Property"
    ) -> bool:
        """Send email verification link"""
        
        subject = "Verify Your Email — Design Diagnosis Report"
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2C3E50;">Design Diagnosis Report</h2>
                    <p>Hi there,</p>
                    <p>You've requested your Design Diagnosis report for <strong>{property_name}</strong>.</p>
                    <p>To access your report, please verify your email by clicking the link below:</p>
                    
                    <div style="margin: 30px 0;">
                        <a href="{verification_link}" 
                           style="background-color: #E74C3C; color: white; padding: 12px 30px; 
                                  text-decoration: none; border-radius: 5px; display: inline-block;">
                            Verify Email & Get Report
                        </a>
                    </div>
                    
                    <p style="color: #666; font-size: 12px;">
                        Or copy and paste this link in your browser:<br>
                        <code>{verification_link}</code>
                    </p>
                    
                    <p style="color: #999; font-size: 12px; margin-top: 30px;">
                        This link expires in 24 hours.<br>
                        If you didn't request this, you can ignore this email.
                    </p>
                    
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                    <p style="color: #999; font-size: 11px;">Design Diagnosis by Rooms by Rachel</p>
                </div>
            </body>
        </html>
        """
        
        return self._send_email(to_email, subject, html_content)
    
    def send_report_email(
        self, to_email: str, property_name: str, report_type: str,
        pdf_path: str, pdf_filename: str = "Design_Diagnosis_Report.pdf"
    ) -> bool:
        """Send report PDF via email"""
        
        subject = f"Your Design Diagnosis Report — {property_name}"
        
        if report_type == "premium":
            description = "your complete Design Diagnosis report with shopping lists and ROI analysis"
        else:
            description = "your Design Diagnosis report with top 3 recommended fixes"
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2C3E50;">Design Diagnosis Report</h2>
                    <p>Hi there,</p>
                    <p>Great news! Your Design Diagnosis report is ready.</p>
                    
                    <div style="background-color: #ECF0F1; padding: 20px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="margin-top: 0;">📊 {property_name}</h3>
                        <p><strong>Report Type:</strong> {report_type.upper()}</p>
                        <p style="color: #666;">Your {description} is attached to this email.</p>
                    </div>
                    
                    <h3>What's in your report?</h3>
                    <ul>
                        <li><strong>Vitality Score</strong> (0-100) with grade A-F</li>
                        <li><strong>5-Pillar Analysis</strong> breakdown</li>
                        <li><strong>Guest Comfort Checklist</strong> results</li>
                        <li><strong>Top 3 Recommended Fixes</strong> with cost estimates</li>
                        <li><strong>Shopping Lists</strong> (Value, Signature, Luxury tiers)</li>
                        <li><strong>Implementation Roadmap</strong></li>
                    </ul>
                    
                    <p style="color: #666;">
                        <strong>Next Steps:</strong> Review your report and prioritize the recommendations 
                        that best fit your budget and timeline.
                    </p>
                    
                    <p style="color: #999; font-size: 12px; margin-top: 30px;">
                        Questions? Reply to this email or visit designdiagnosis.com
                    </p>
                    
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                    <p style="color: #999; font-size: 11px;">Design Diagnosis by Rooms by Rachel</p>
                </div>
            </body>
        </html>
        """
        
        return self._send_email_with_attachment(
            to_email, subject, html_content, pdf_path, pdf_filename
        )
    
    def send_payment_confirmation_email(
        self, to_email: str, property_name: str, amount: str = "$39.00"
    ) -> bool:
        """Send payment confirmation email"""
        
        subject = f"Payment Confirmed — Design Diagnosis Premium Report"
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2C3E50;">Payment Confirmed ✓</h2>
                    <p>Hi there,</p>
                    <p>Thank you! Your payment has been processed successfully.</p>
                    
                    <div style="background-color: #d4edda; border: 1px solid #c3e6cb; padding: 15px; 
                              border-radius: 5px; margin: 20px 0; color: #155724;">
                        <p style="margin: 0;"><strong>Amount:</strong> {amount}</p>
                        <p style="margin: 0;"><strong>Property:</strong> {property_name}</p>
                        <p style="margin: 0;"><strong>Report Type:</strong> PREMIUM</p>
                    </div>
                    
                    <p>Your complete Design Diagnosis report is being generated and will be sent to you within 2-3 minutes.</p>
                    
                    <p style="color: #999; font-size: 12px; margin-top: 30px;">
                        Questions? Reply to this email or visit designdiagnosis.com
                    </p>
                    
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                    <p style="color: #999; font-size: 11px;">Design Diagnosis by Rooms by Rachel</p>
                </div>
            </body>
        </html>
        """
        
        return self._send_email(to_email, subject, html_content)
    
    def _send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Internal: send email without attachment"""
        try:
            if not self.client:
                print(f"📧 [MOCK] Email to {to_email}: {subject}")
                return True
            
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=subject,
                html_content=html_content
            )
            
            response = self.client.send(message)
            return response.status_code in [200, 201, 202]
        except Exception as e:
            print(f"❌ Email send failed: {e}")
            return False
    
    def _send_email_with_attachment(
        self, to_email: str, subject: str, html_content: str,
        pdf_path: str, pdf_filename: str
    ) -> bool:
        """Internal: send email with PDF attachment"""
        try:
            if not self.client:
                print(f"📧 [MOCK] Email to {to_email}: {subject} (with PDF: {pdf_filename})")
                return True
            
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=subject,
                html_content=html_content
            )
            
            # Attach PDF
            with open(pdf_path, 'rb') as f:
                pdf_data = f.read()
            
            encoded = base64.b64encode(pdf_data).decode()
            attachment = Attachment(
                FileContent(encoded),
                FileName(pdf_filename),
                FileType("application/pdf"),
                ContentId("Report")
            )
            message.attachment = attachment
            
            response = self.client.send(message)
            return response.status_code in [200, 201, 202]
        except Exception as e:
            print(f"❌ Email send failed: {e}")
            return False
    
    def is_configured(self) -> bool:
        """Check if SendGrid is properly configured"""
        return self.client is not None and self.api_key.startswith("SG.")


# Test
if __name__ == "__main__":
    email_service = EmailService()
    print(f"✅ Email service initialized (SendGrid: {email_service.is_configured()})")
