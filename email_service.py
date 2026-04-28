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
    from sendgrid.helpers.mail import Mail, Email, To, Content, Attachment, FileContent, FileName, FileType, Disposition, From
    SENDGRID_AVAILABLE = True
except ImportError:
    logger.warning("⚠️  sendgrid package not installed. Email will use mock mode.")
    SENDGRID_AVAILABLE = False


class EmailService:
    """Email service with SendGrid or mock fallback"""
    
    def __init__(self):
        self.api_key = os.getenv("SENDGRID_API_KEY")
        # Use Rachel's trusted sender email
        self.from_email = os.getenv("SENDGRID_FROM_EMAIL", "rachellabelles@gmail.com")
        # Brand links
        self.website_url = "https://roomsbyrachel.ca"
        self.instagram_url = "https://www.instagram.com/roomsbyrachel.ca"
        self.tiktok_url = "https://www.tiktok.com/@rooms.by.rachel"
        self.support_email = "rachellabelles@gmail.com"
        
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
                            <a href="{self.tiktok_url}">TikTok</a> • 
                            <a href="{self.instagram_url}">Instagram</a> • 
                            <a href="{self.website_url}">Website</a>
                        </div>
                        
                        <p style="margin-top: 15px;">Questions? <a href="mailto:{self.support_email}">Contact Support</a></p>
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
        report_type: str,
        analysis_text: str = "",
        shopping_list: list = None,
        top_three_fixes: list = None
    ):
        """Send report email with PDF attachment and content"""
        try:
            # VALIDATE REPORT TYPE STRICTLY
            if not report_type or report_type not in ["free", "premium"]:
                logger.error(f"❌ CRITICAL: send_report_email() received invalid report_type='{report_type}' (expected 'free' or 'premium'). Defaulting to 'free'.")
                report_type = "free"
            
            logger.info(f"📧 SENDING {report_type.upper()} REPORT EMAIL")
            logger.info(f"   → Recipient: {email}")
            logger.info(f"   → Property: {property_name}")
            logger.info(f"   → Score: {vitality_score}/100 (Grade {grade})")
            
            # Ensure pdf_path is absolute and in the reports directory (if provided)
            if pdf_path and not os.path.isabs(pdf_path):
                reports_dir = os.getenv("REPORT_OUTPUT_DIR", "./reports")
                pdf_path = os.path.join(reports_dir, os.path.basename(pdf_path))
            
            if pdf_path:
                logger.info(f"📎 PDF attachment: {pdf_path}")
            else:
                logger.info(f"📧 No PDF attachment (email only)")
            
            # Build HTML email with dynamic content
            if shopping_list is None:
                shopping_list = []
            if top_three_fixes is None:
                top_three_fixes = []
            
            # Build shopping list HTML
            shopping_html = ""
            if shopping_list and report_type == "premium":
                shopping_html = "<div class='content'><h2>Shopping List</h2><ul>"
                for item in shopping_list[:10]:  # Limit to 10 in email
                    name = item.get('name', 'Item')
                    price = item.get('price', 'N/A')
                    link = item.get('link', '#')
                    desc = item.get('description', '')
                    shopping_html += f"<li><strong><a href='{link}'>{name}</a></strong> ({price})<br/><em>{desc}</em></li>"
                shopping_html += "</ul></div>"
            
            # Build analysis HTML
            analysis_html = ""
            if analysis_text:
                analysis_html = f"<div class='content'><h2>The Situation</h2><p>{analysis_text}</p></div>"
            
            # Build top 3 fixes HTML
            fixes_html = ""
            if top_three_fixes:
                fixes_html = "<div class='content'><h2>Top 3 High-Impact Fixes</h2><ul>"
                for i, fix in enumerate(top_three_fixes[:3], 1):
                    title = fix.get('title', 'Fix')
                    desc = fix.get('description', '')
                    cost = fix.get('cost_low', 0)
                    fixes_html += f"<li><strong>#{i}: {title}</strong><br/>{desc}<br/><em>Est. Cost: ${cost}+</em></li>"
                fixes_html += "</ul></div>"
            
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
                    .content a {{ color: #667eea; text-decoration: none; font-weight: 500; }}
                    .content a:hover {{ text-decoration: underline; }}
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
                        <h1>Your Design Diagnosis Report</h1>
                        <p>{property_name}</p>
                    </div>
                    
                    <div class="score-card">
                        <div>Vitality Score</div>
                        <div class="score">{vitality_score}/100</div>
                        <div class="grade">Grade {grade}</div>
                    </div>
                    
                    {analysis_html}
                    {fixes_html}
                    {shopping_html}
                    
                    <div class="content">
                        <strong>Next Steps:</strong>
                        <ol style="padding-left: 20px;">
                            <li>Review your attached PDF report (8-9 pages of detailed analysis)</li>
                            <li>Prioritize fixes based on your budget and timeline</li>
                            <li>Use the shopping list to source items</li>
                            <li>Track progress and re-submit in 30 days for a re-score</li>
                        </ol>
                        <p style="margin-top: 15px; text-align: center;">
                            <strong>Ready for expert guidance?</strong><br/>
                            <a href="https://calendly.com/roomsbyrachel" class="cta-button">Book a Consultation</a>
                        </p>
                    </div>
                    </div>
                    
                    <div class="footer">
                        <p><strong>Rooms by Rachel</strong></p>
                        <p>Design Diagnosis — Expert Analysis for Short-Term Rentals</p>
                        
                        <div class="social-links">
                            <a href="{self.tiktok_url}">TikTok</a> • 
                            <a href="{self.instagram_url}">Instagram</a> • 
                            <a href="{self.website_url}">Website</a>
                        </div>
                        
                        <div class="divider"></div>
                        
                        <p>Questions? <a href="mailto:{self.support_email}">Contact Support</a></p>
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
            # Use From() to include display name
            message = Mail(
                from_email=From(self.from_email, "Rooms by Rachel"),
                to_emails=to_email,
                subject=subject,
                html_content=html_content
            )
            
            # Add PDF attachment if provided
            if attachment_path and os.path.exists(attachment_path):
                import base64
                with open(attachment_path, 'rb') as f:
                    attachment_data = f.read()
                    # Base64 encode the PDF file
                    file_content_b64 = base64.b64encode(attachment_data).decode('utf-8')
                    
                    # Create attachment using proper SendGrid classes
                    attachment = Attachment(
                        file_content=FileContent(file_content_b64),
                        file_name=FileName(os.path.basename(attachment_path)),
                        file_type=FileType("application/pdf"),
                        disposition=Disposition("attachment")
                    )
                    message.attachment = attachment
                    logger.info(f"📎 PDF attachment added: {os.path.basename(attachment_path)}")
            
            # Send
            response = self.client.send(message)
            logger.info(f"✅ Email sent to {to_email} (Status: {response.status_code})")
        
        except Exception as e:
            logger.error(f"❌ SendGrid send error: {e}")
            raise
    
    def send_free_vitality_report(self, email: str, vitality_score: int, grade: str, top_fixes: list, property_name: str = "Your Property", submission_id: int = None, unchecked_items: list = None):
        """
        PHASE 4: Send Free Tier Vitality Report Email (REDACTED)
        
        Instant hook email with Vitality Score, Grade, REDACTED AI Fixes, and Upgrade CTA to Stripe.
        
        CRITICAL: AI Design Fixes are REDACTED to prevent revenue leakage.
        Instead: Show 2-3 static utility fixes from unchecked checklist items.
        
        Args:
            email: Recipient email
            vitality_score: Score 0-100
            grade: Letter grade (A-F)
            top_fixes: List of top 3 fixes (IGNORED - redacted for free tier)
            property_name: Property name for personalization
            submission_id: For Stripe checkout link
            unchecked_items: List of unchecked comfort items to show as "Essential Baseline Fixes"
        """
        try:
            subject = f"🎯 Your Design Diagnosis: {vitality_score}/100 ({grade}) — {property_name}"
            
            # Grade color coding
            grade_colors = {
                'A': '#388e3c',  # Green
                'B': '#7cb342',  # Light green
                'C': '#fbc02d',  # Yellow
                'D': '#f57c00',  # Orange
                'F': '#d32f2f'   # Red
            }
            grade_color = grade_colors.get(grade, '#757575')
            
            # Build HTML email
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0; text-align: center; }}
                    .header h1 {{ margin: 0 0 10px 0; font-size: 32px; }}
                    .score-card {{ background: white; border: 3px solid {grade_color}; border-radius: 10px; padding: 30px; text-align: center; margin: 20px 0; }}
                    .score-number {{ font-size: 48px; font-weight: bold; color: {grade_color}; }}
                    .score-label {{ font-size: 18px; color: #666; margin-top: 10px; }}
                    .grade-badge {{ display: inline-block; width: 80px; height: 80px; background: {grade_color}; color: white; border-radius: 50%; line-height: 80px; font-size: 32px; font-weight: bold; margin: 20px 0; }}
                    .fixes-section {{ margin: 30px 0; }}
                    .fixes-section h3 {{ color: #667eea; font-size: 20px; margin-bottom: 15px; }}
                    .fix-item {{ background: #f5f5f5; padding: 15px; border-left: 4px solid #667eea; margin-bottom: 12px; border-radius: 4px; }}
                    .fix-priority {{ font-weight: bold; color: #764ba2; font-size: 12px; text-transform: uppercase; }}
                    .fix-title {{ font-size: 16px; font-weight: bold; margin: 8px 0 5px 0; }}
                    .fix-rationale {{ font-size: 14px; color: #666; }}
                    .cta-button {{ display: inline-block; background: #667eea; color: white; padding: 15px 40px; border-radius: 6px; text-decoration: none; font-weight: bold; font-size: 16px; margin: 20px 0; }}
                    .cta-button:hover {{ background: #764ba2; }}
                    .footer {{ background: #f9f9f9; padding: 20px; text-align: center; font-size: 12px; color: #999; margin-top: 30px; border-radius: 0 0 10px 10px; }}
                    .footer a {{ color: #667eea; text-decoration: none; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🏠 Design Diagnosis</h1>
                        <p>Your Property's Visual Quality Score</p>
                    </div>
                    
                    <div class="score-card">
                        <div class="score-number">{vitality_score}</div>
                        <div class="score-label">Vitality Score (out of 100)</div>
                        <div class="grade-badge">{grade}</div>
                    </div>
                    
                    <div style="padding: 0 20px;">
                        <h2 style="color: #333; margin-top: 30px;">What This Score Means</h2>
                        <p style="font-size: 16px; color: #666;">
                            Your listing's design quality directly impacts booking rates, guest reviews, and nightly rates. 
                            This score reflects how guests will perceive your property from photos alone.
                        </p>
                        
                        <div class="fixes-section">
                            <h3>🔧 AI-Powered Design Fixes (Redacted)</h3>
                            <p style="color: #666; font-size: 14px; margin-bottom: 15px;">
                                Your custom design recommendations are locked behind the Premium report. 
                                Unlock your personalized fixes below:
                            </p>
                            {self._render_redacted_fixes_html()}
                        </div>
                        
                        <div class="fixes-section">
                            <h3>📋 Essential Baseline Fixes (Free Preview)</h3>
                            <p style="color: #666; font-size: 14px; margin-bottom: 15px;">
                                Start with these foundational guest experience improvements:
                            </p>
                            {self._render_utility_fixes_html(unchecked_items)}
                        </div>
                        
                        <div style="text-align: center; margin: 40px 0;">
                            <p style="font-size: 16px; font-weight: bold; color: #333; margin-bottom: 15px;">
                                Ready to unlock your custom design strategy?
                            </p>
                            <a href="{self._get_stripe_checkout_url(submission_id)}" class="cta-button" style="background: #d32f2f; font-size: 18px; padding: 18px 40px;">
                                🔓 Show me my 3 custom design fixes
                            </a>
                            <p style="font-size: 14px; color: #666; margin-top: 15px; font-weight: bold;">
                                Unlock the 8-page Spatial Diagnosis PDF ($39)
                            </p>
                            <p style="font-size: 12px; color: #999; margin-top: 5px;">
                                Includes room-by-room analysis, AI shopping lists, and budget-aware recommendations.
                            </p>
                        </div>
                        
                        <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                        
                        <div style="background: #f0f4ff; padding: 20px; border-radius: 6px; margin: 20px 0;">
                            <h3 style="color: #667eea; margin-top: 0;">💡 Why Premium?</h3>
                            <p style="margin: 0 0 10px 0;">✅ <strong>Room-by-Room Analysis</strong> — See which spaces need the most help</p>
                            <p style="margin: 0 0 10px 0;">✅ <strong>AI-Powered Shopping Lists</strong> — Links to exact products that fix each issue</p>
                            <p style="margin: 0 0 10px 0;">✅ <strong>Budget-Aware Recommendations</strong> — Value, Signature, and Luxury tiers</p>
                            <p style="margin: 0;">✅ <strong>Guest Experience Blueprint</strong> — Fix priority and ROI for each improvement</p>
                        </div>
                    </div>
                    
                    <div class="footer">
                        <p style="margin: 0 0 10px 0;">
                            <strong>Rooms by Rachel</strong> — Interior Design for Short-Term Rentals
                        </p>
                        <p style="margin: 0 0 15px 0;">
                            <a href="{self.instagram_url}">Instagram</a> · 
                            <a href="{self.tiktok_url}">TikTok</a> · 
                            <a href="{self.website_url}">Website</a>
                        </p>
                        <p style="margin: 0;">
                            Questions? Reply to this email or contact <a href="mailto:{self.support_email}">{self.support_email}</a>
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Send email
            print(f"[EMAIL] 📧 Sending FREE VITALITY REPORT to {email}")
            print(f"[EMAIL]    Score: {vitality_score}/100, Grade: {grade}")
            print(f"[EMAIL]    Top fixes: {len(top_fixes)} items")
            
            if self.mode == "LIVE":
                message = Mail(
                    from_email=self.from_email,
                    to_emails=email,
                    subject=subject,
                    html_content=html_content
                )
                response = self.client.send(message)
                logger.info(f"✅ Free vitality report sent to {email} (Status: {response.status_code})")
            else:
                logger.info(f"📧 [MOCK] Free vitality report to {email}")
                logger.info(f"📧 [MOCK] Subject: {subject}")
                logger.info(f"📧 [MOCK] Score: {vitality_score}/100, Grade: {grade}")
        
        except Exception as e:
            logger.error(f"❌ Free report email error: {e}")
            print(f"[EMAIL] ❌ Failed to send free report: {e}")
            raise
    
    def _render_fixes_html(self, top_fixes: list) -> str:
        """Render top 3 fixes as HTML (OLD - for reference)"""
        if not top_fixes:
            return "<p style='color: #999;'>No fixes available.</p>"
        
        html = ""
        for idx, fix in enumerate(top_fixes[:3], 1):
            priority = fix.get('priority', 1)
            title = fix.get('title', 'Fix')
            rationale = fix.get('experience_logic_rationale', '')
            
            html += f"""
            <div class="fix-item">
                <div class="fix-priority">#{priority} — {['Low', 'Medium', 'High', 'Critical'][min(priority - 1, 3)]}</div>
                <div class="fix-title">{title}</div>
                <div class="fix-rationale">{rationale}</div>
            </div>
            """
        
        return html
    
    def _render_redacted_fixes_html(self) -> str:
        """
        REVENUE PROTECTION: Render 3 redacted fix placeholders
        Prevents free users from seeing AI design fixes without paying
        """
        redacted_html = ""
        for idx in range(1, 4):
            redacted_html += f"""
            <div style="background: #f5f5f5; padding: 15px; border-left: 4px solid #d32f2f; margin-bottom: 12px; border-radius: 4px; opacity: 0.6;">
                <div style="font-weight: bold; color: #999; font-size: 12px; text-transform: uppercase;">Fix #{idx}</div>
                <div style="font-size: 16px; font-weight: bold; color: #999; margin: 8px 0;">
                    🔒 [REDACTED DESIGN FIX]
                </div>
                <div style="font-size: 14px; color: #999;">
                    This personalized recommendation is locked. Upgrade to Premium to unlock.
                </div>
            </div>
            """
        return redacted_html
    
    def _render_utility_fixes_html(self, unchecked_items: list = None) -> str:
        """
        Render 2-3 static utility fixes from unchecked checklist items
        These are basic baseline improvements, not the premium AI analysis
        """
        # Map unchecked items to guest experience language
        utility_fixes_library = {
            'powerBars': {
                'title': 'Add Power Bars',
                'rationale': 'Modern guests need accessible charging for phones and laptops. Missing power bars frustrate guests and risk negative reviews.'
            },
            'bedLamps': {
                'title': 'Install Bedside Lamps',
                'rationale': 'Bedside lamps are essential for guest comfort and safety. Without them, guests feel like the property lacks care and attention.'
            },
            'hangers': {
                'title': 'Add Hangers to Closet',
                'rationale': 'Hangers are a basic expectation. Their absence signals a low-budget property and creates inconvenience for guests.'
            },
            'plunger': {
                'title': 'Place Plunger in Bathroom',
                'rationale': 'A plunger is non-negotiable for guest peace of mind. Its absence can trigger 1-star reviews instantly.'
            },
            'glasses': {
                'title': 'Stock Guest Glasses',
                'rationale': 'Glasses for drinking are standard. Missing glassware makes guests feel neglected and unprofessional.'
            },
            'plates': {
                'title': 'Add Dinner Plates',
                'rationale': 'Plates are essential for dining. Without them, your kitchen feels incomplete and guest-unfriendly.'
            },
            'dryingRack': {
                'title': 'Add Drying Rack',
                'rationale': 'A drying rack shows you understand guest needs. Without it, wet laundry becomes a problem that ruins their experience.'
            },
            'paperTowels': {
                'title': 'Stock Paper Towels',
                'rationale': 'Paper towels are expected. Their absence frustrates guests and signals low maintenance standards.'
            },
            'coasters': {
                'title': 'Add Coasters',
                'rationale': 'Coasters protect your furniture and show hospitality. They are a small touch that elevates perceived quality.'
            },
            'shoeRack': {
                'title': 'Install Shoe Rack',
                'rationale': 'A shoe rack prevents clutter and shows organizational care. Without one, your entry feels chaotic.'
            },
            'mirror': {
                'title': 'Add Entry Mirror',
                'rationale': 'A mirror in the entry helps guests feel at home and check their appearance. It is a simple luxury detail.'
            },
            'bathMats': {
                'title': 'Stock Bath Mats',
                'rationale': 'Bath mats are a comfort essential. Without them, guests feel the property is bare and lacks hospitality.'
            },
        }
        
        if not unchecked_items or len(unchecked_items) == 0:
            # Default fallback if no unchecked items provided
            unchecked_items = ['plunger', 'bedLamps', 'hangers']
        
        # Take first 2-3 unchecked items
        selected_items = unchecked_items[:3]
        
        utility_html = ""
        for idx, item_key in enumerate(selected_items, 1):
            fix_info = utility_fixes_library.get(item_key, {
                'title': f'Missing Guest Amenity',
                'rationale': 'Guests expect this item. Adding it will improve their experience and your ratings.'
            })
            
            utility_html += f"""
            <div style="background: #f9f9f9; padding: 15px; border-left: 4px solid #388e3c; margin-bottom: 12px; border-radius: 4px;">
                <div style="font-weight: bold; color: #388e3c; font-size: 12px; text-transform: uppercase;">Baseline Fix #{idx}</div>
                <div style="font-size: 16px; font-weight: bold; color: #333; margin: 8px 0;">
                    ✅ {fix_info['title']}
                </div>
                <div style="font-size: 14px; color: #666;">
                    {fix_info['rationale']}
                </div>
            </div>
            """
        
        return utility_html
    
    def _get_stripe_checkout_url(self, submission_id: int = None) -> str:
        """
        Generate Stripe checkout URL for this submission
        Falls back to generic premium page if submission_id not provided
        """
        if submission_id:
            return f"{self.website_url}/checkout?submission_id={submission_id}"
        else:
            return f"{self.website_url}/premium"
    
    def _send_mock(self, to_email: str, subject: str, message_type: str):
        """Mock email (log only)"""
        logger.info(f"📧 [MOCK] {message_type} email to {to_email}")
        logger.info(f"📧 [MOCK] Subject: {subject}")
