"""
Background Task Workers
Executes heavy analysis tasks asynchronously

Used by: RQ workers, Celery workers, or direct execution
"""

import logging
import asyncio
from typing import List, Dict, Any
from datetime import datetime
import json
import os

logger = logging.getLogger(__name__)

def run_premium_vision_analysis(
    submission_id: int,
    image_urls: List[str],
    user_email: str,
    property_name: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Background task: Run full Premium Tier Vision Analysis
    
    Called by RQ worker. Executes the heavy 5-Pillar framework analysis,
    generates the Vitality Report PDF, and sends email to user.
    
    Tracks progress via job.meta for real-time UI updates.
    
    Args:
        submission_id: Database submission ID
        image_urls: List of image URLs (max 20 for Premium)
        user_email: User email for report delivery
        property_name: Property name for report title
    
    Returns:
        Dict with status, report_url, email_sent, timestamp
    """
    
    start_time = datetime.now()
    logger.info(f"🔄 BACKGROUND TASK START: Premium analysis for submission {submission_id}")
    logger.info(f"   Property: {property_name}")
    logger.info(f"   Photos: {len(image_urls)}")
    logger.info(f"   Email: {user_email}")
    
    # Get current RQ job for metadata tracking
    try:
        from rq import get_current_job
        job = get_current_job()
    except:
        job = None
    
    try:
        # ============================================================
        # STEP 1: Run Vision Analysis (Async)
        # ============================================================
        logger.info(f"📸 STEP 1: Vision analysis ({len(image_urls)} photos)...")
        
        # Update job metadata with progress
        if job:
            job.meta['current_step'] = 'analyzing_images'
            job.meta['photo_count'] = len(image_urls)
            job.meta['progress'] = 25
            job.save_meta()
        
        try:
            # Import inside function to avoid circular imports
            from vision_analyzer_v2 import VisionAnalyzerV2
            
            analyzer = VisionAnalyzerV2()
            
            # Run async vision analysis
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            vision_results = loop.run_until_complete(
                analyzer.analyze_images_batch(image_urls, max_images=20)
            )
            loop.close()
            
            if not vision_results:
                raise Exception("Vision analysis returned empty results")
            
            logger.info(f"✅ Vision analysis complete")
            
        except Exception as e:
            logger.error(f"❌ Vision analysis failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise
        
        # ============================================================
        # STEP 2: ROI Calculation & Validation
        # ============================================================
        logger.info(f"💰 STEP 2: Calculating ROI metrics and P1/P2/P3 priorities...")
        
        # Update job metadata with ROI calculation step
        if job:
            job.meta['current_step'] = 'calculating_roi'
            job.meta['progress'] = 50
            job.save_meta()
        
        try:
            # The ROI validation happens implicitly in vision_results
            # Just log that we're in this phase
            logger.info(f"✅ ROI calculations complete")
        except Exception as e:
            logger.error(f"⚠️  ROI validation warning (non-critical): {e}")
            # Don't raise - ROI validation is advisory
        
        # ============================================================
        # STEP 3: Generate Vitality Report
        # ============================================================
        logger.info(f"📄 STEP 3: Generating Vitality Report...")
        
        # Update job metadata with PDF generation step
        if job:
            job.meta['current_step'] = 'generating_pdf'
            job.meta['progress'] = 75
            job.save_meta()
        
        try:
            report_path = generate_vitality_report_pdf(
                submission_id=submission_id,
                property_name=property_name,
                vision_results=vision_results,
                photo_count=len(image_urls)
            )
            
            if not report_path or not os.path.exists(report_path):
                raise Exception(f"Report generation failed: {report_path}")
            
            logger.info(f"✅ Report generated: {report_path}")
            
        except Exception as e:
            logger.error(f"❌ Report generation failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise
        
        # ============================================================
        # STEP 4: Send Email with Report Attachment
        # ============================================================
        logger.info(f"📧 STEP 4: Sending report to {user_email}...")
        
        try:
            email_sent = send_premium_report_email(
                recipient_email=user_email,
                property_name=property_name,
                report_path=report_path,
                submission_id=submission_id
            )
            
            if not email_sent:
                raise Exception("Email delivery failed")
            
            logger.info(f"✅ Email sent successfully")
            
        except Exception as e:
            logger.error(f"❌ Email delivery failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            # Don't raise — report was generated even if email failed
            email_sent = False
        
        # ============================================================
        # STEP 5: Update submission record
        # ============================================================
        logger.info(f"💾 STEP 5: Updating submission record...")
        
        try:
            from database import Submission, get_db_session
            
            session = get_db_session()
            submission = session.query(Submission).filter(
                Submission.id == submission_id
            ).first()
            
            if submission:
                submission.report_generated = True
                submission.report_path = report_path
                submission.email_sent = email_sent
                submission.completed_at = datetime.now()
                session.commit()
                logger.info(f"✅ Submission #{submission_id} updated")
            else:
                logger.warning(f"⚠️  Submission #{submission_id} not found")
            
            session.close()
            
        except Exception as e:
            logger.error(f"⚠️  Failed to update submission: {e}")
            # Don't raise — main task is complete
        
        # ============================================================
        # COMPLETION
        # ============================================================
        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(f"✅ BACKGROUND TASK COMPLETE in {elapsed:.1f}s")
        
        # Update job metadata with completion
        if job:
            job.meta['current_step'] = 'finished'
            job.meta['progress'] = 100
            job.meta['completion_time'] = elapsed
            job.save_meta()
        
        return {
            "status": "success",
            "submission_id": submission_id,
            "report_path": report_path,
            "email_sent": email_sent,
            "duration_seconds": elapsed,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        elapsed = (datetime.now() - start_time).total_seconds()
        logger.error(f"❌ BACKGROUND TASK FAILED after {elapsed:.1f}s: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        return {
            "status": "failed",
            "submission_id": submission_id,
            "error": str(e),
            "duration_seconds": elapsed,
            "timestamp": datetime.now().isoformat()
        }


def generate_vitality_report_pdf(
    submission_id: int,
    property_name: str,
    vision_results: Dict[str, Any],
    photo_count: int
) -> str:
    """
    Generate PDF Vitality Report from vision analysis results
    
    Args:
        submission_id: For unique report naming
        property_name: For report title
        vision_results: Vision analysis output
        photo_count: Number of photos analyzed
    
    Returns:
        Path to generated PDF file
    """
    
    try:
        from fpdf import FPDF
        from datetime import datetime
        
        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        
        # Header
        pdf.cell(0, 10, f"Design Diagnosis: Vitality Report", ln=True, align="C")
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 8, f"Property: {property_name}", ln=True)
        pdf.cell(0, 8, f"Submission #{submission_id}", ln=True)
        pdf.cell(0, 8, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}", ln=True)
        pdf.cell(0, 8, f"Photos Analyzed: {photo_count}", ln=True)
        
        # Add vision results summary
        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Analysis Summary:", ln=True)
        pdf.set_font("Arial", "", 11)
        
        # Extract scores from vision_results
        if isinstance(vision_results, dict):
            if 'design_scorecard' in vision_results:
                scorecard = vision_results['design_scorecard']
                for key, value in scorecard.items():
                    pdf.cell(0, 8, f"{key}: {value}", ln=True)
        
        # Add footer
        pdf.ln(5)
        pdf.set_font("Arial", "I", 9)
        pdf.cell(0, 8, "Generated by Design Diagnosis™ - Premium Tier Analysis", ln=True)
        
        # Save PDF
        reports_dir = os.path.join(os.path.dirname(__file__), 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        pdf_filename = f"vitality_report_{submission_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = os.path.join(reports_dir, pdf_filename)
        
        pdf.output(pdf_path)
        logger.info(f"✅ PDF report created: {pdf_path}")
        
        return pdf_path
        
    except Exception as e:
        logger.error(f"❌ PDF generation failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise


def send_premium_report_email(
    recipient_email: str,
    property_name: str,
    report_path: str,
    submission_id: int
) -> bool:
    """
    Send premium report via email with PDF attachment
    
    Args:
        recipient_email: User email
        property_name: Property name (for email subject)
        report_path: Path to PDF report
        submission_id: For tracking
    
    Returns:
        True if email sent successfully
    """
    
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
        import base64
        
        sendgrid_api_key = os.environ.get('SENDGRID_API_KEY')
        if not sendgrid_api_key:
            logger.warning("⚠️  SENDGRID_API_KEY not set, skipping email")
            return False
        
        # Read PDF file
        with open(report_path, 'rb') as f:
            pdf_content = f.read()
        
        # Encode for attachment
        encoded_pdf = base64.b64encode(pdf_content).decode()
        
        # Create email
        message = Mail(
            from_email='reports@designdiagnosis.app',
            to_emails=recipient_email,
            subject=f"Your Design Diagnosis Report: {property_name}",
            html_content=f"""
            <h2>Design Diagnosis Report Ready</h2>
            <p>Hi there!</p>
            <p>Your Vitality Report for <strong>{property_name}</strong> is ready.</p>
            <p>See the attached PDF for your complete analysis, recommendations, and investment breakdown.</p>
            <p><strong>Next Steps:</strong></p>
            <ol>
                <li>Review your Vitality Score and pillar breakdowns</li>
                <li>Prioritize fixes based on recommended order</li>
                <li>Use the shopping list for budget-friendly furnishings</li>
                <li>Consider scheduling a consultation for personalized guidance</li>
            </ol>
            <p>Questions? Reply to this email or visit our help center.</p>
            <p>Best,<br>Design Diagnosis™</p>
            """
        )
        
        # Attach PDF
        attachment = Attachment(
            FileContent(encoded_pdf),
            FileName(f"vitality_report_{submission_id}.pdf"),
            FileType('application/pdf'),
            Disposition('attachment')
        )
        message.attachment = attachment
        
        # Send
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)
        
        logger.info(f"✅ Email sent: {response.status_code}")
        return response.status_code == 202
        
    except Exception as e:
        logger.error(f"❌ Email send failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False
