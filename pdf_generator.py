"""
PDF Report Generator — Design Diagnosis

Generates professional PDF reports with vitality scores and recommendations.
"""

import logging
import os
import re
from typing import Dict, List

logger = logging.getLogger(__name__)


def sanitize_text_for_pdf(text: str) -> str:
    """
    Sanitize text for PDF generation (fpdf2 compatibility).
    
    Removes/replaces problematic Unicode characters:
    - Special dashes (–, —) → regular hyphen (-)
    - Emojis → removed
    - Other Unicode → ASCII fallback
    """
    if not text:
        return ""
    
    # Replace special dashes
    text = text.replace('–', '-')  # En dash
    text = text.replace('—', '-')  # Em dash
    text = text.replace('•', '-')  # Bullet
    text = text.replace('…', '...')  # Ellipsis
    
    # Remove emojis and other non-ASCII characters
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    
    return text.strip()

# Try to import fpdf2
try:
    from fpdf import FPDF
    PDF_AVAILABLE = True
except ImportError:
    logger.warning("⚠️  fpdf2 package not installed. PDF generation will use HTML fallback.")
    PDF_AVAILABLE = False


class DesignDiagnosisPDF(FPDF):
    """Custom PDF class for Design Diagnosis reports"""
    
    def __init__(self):
        super().__init__()
        self.WIDTH = 210
        self.HEIGHT = 297
    
    def header(self):
        """Add header to each page"""
        self.set_font("Helvetica", "B", 20)
        self.set_text_color(102, 126, 234)  # Purple
        # Note: fpdf2 doesn't support emojis, use plain text
        self.cell(0, 10, "Design Diagnosis Report", 0, 1, "C")
        self.ln(5)
    
    def footer(self):
        """Add footer to each page"""
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")
    
    def chapter_title(self, title: str):
        """Add a chapter title"""
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(102, 126, 234)
        self.cell(0, 10, title, 0, 1, "L")
        self.set_text_color(0, 0, 0)
        self.ln(3)
    
    def chapter_body(self, text: str):
        """Add chapter text"""
        self.set_font("Helvetica", "", 11)
        self.multi_cell(0, 5, text)
        self.ln()


def generate_pdf_report(
    output_path: str,
    property_name: str,
    vitality_data: Dict,
    recommendations: List[Dict]
) -> bool:
    """
    Generate a professional PDF report.
    
    Args:
        output_path: Where to save the PDF
        property_name: Property name
        vitality_data: Vitality score data
        recommendations: List of recommendations
    
    Returns: True if successful
    """
    if not PDF_AVAILABLE:
        logger.warning("⚠️  fpdf2 not available. PDF generation skipped.")
        return False
    
    try:
        pdf = DesignDiagnosisPDF()
        pdf.add_page()
        
        # Title section (no emojis for fpdf2 compatibility)
        pdf.set_font("Helvetica", "B", 24)
        pdf.set_text_color(102, 126, 234)
        pdf.cell(0, 15, "Design Diagnosis", 0, 1, "C")
        
        pdf.set_font("Helvetica", "", 16)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 10, sanitize_text_for_pdf(property_name), 0, 1, "C")
        pdf.ln(10)
        
        # Vitality Score Section
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 10, "Your Vitality Score", 0, 1)
        pdf.ln(2)
        
        # Score box
        score = vitality_data.get('vitality_score', 0)
        grade = vitality_data.get('grade', 'F')
        
        pdf.set_font("Helvetica", "B", 48)
        pdf.set_text_color(102, 126, 234)
        score_text = str(score)
        pdf.cell(100, 20, score_text, 0, 1, "C")
        
        pdf.set_font("Helvetica", "", 12)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 8, f"Grade: {grade} — {vitality_data.get('grade_label', '')}", 0, 1, "C")
        pdf.cell(0, 6, vitality_data.get('grade_description', ''), 0, 1, "C")
        pdf.ln(8)
        
        # Breakdown
        pdf.chapter_title("Score Breakdown")
        breakdown = vitality_data.get('breakdown', {})
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(100, 6, f"Guest Comfort: {breakdown.get('comfort', '0/42')}", 0, 1)
        pdf.cell(100, 6, f"Photos: {breakdown.get('photos', '0/20')}", 0, 1)
        pdf.cell(100, 6, f"Design Assessment: {breakdown.get('design', '0/30')}", 0, 1)
        pdf.ln(5)
        
        # Recommendations
        pdf.chapter_title("Top Recommendations")
        for i, rec in enumerate(recommendations[:5], 1):
            priority = rec.get('priority', '')
            title = sanitize_text_for_pdf(rec.get('title', ''))
            description = sanitize_text_for_pdf(rec.get('description', ''))
            
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(0, 6, f"{i}. [{priority}] {title}", 0, 1)
            
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 4, description)
            pdf.ln(2)
        
        # Footer
        pdf.ln(10)
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(150, 150, 150)
        pdf.multi_cell(0, 4, "Design Diagnosis helps Airbnb/VRBO hosts optimize their listings through design expertise. Learn more at designdiagnosisapp.com")
        
        # Save PDF
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        pdf.output(output_path)
        
        logger.info(f"✅ PDF report generated: {output_path}")
        return True
    
    except Exception as e:
        logger.error(f"❌ PDF generation error: {e}")
        return False


def generate_html_as_pdf_fallback(
    output_path: str,
    html_content: str
) -> bool:
    """
    Save HTML as .html file (fallback when fpdf2 unavailable).
    Can be printed to PDF from browser.
    """
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # If output is .pdf, change to .html
        if output_path.endswith('.pdf'):
            output_path = output_path.replace('.pdf', '.html')
        
        with open(output_path, 'w') as f:
            f.write(html_content)
        
        logger.info(f"✅ HTML report saved (can be printed to PDF): {output_path}")
        return True
    
    except Exception as e:
        logger.error(f"❌ HTML fallback error: {e}")
        return False
