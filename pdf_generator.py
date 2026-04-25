"""
PDF Report Generator — Design Diagnosis

Generates professional PDF reports with vitality scores and recommendations.
"""

import logging
import os
from typing import Dict, List

from sanitizer import sanitize_text_for_pdf, sanitize_float, sanitize_integer

logger = logging.getLogger(__name__)

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
    recommendations: List[Dict],
    analysis_text: str = "",
    shopping_list: List[Dict] = None,
    top_three_fixes: List[Dict] = None,
    report_type: str = "free"
) -> bool:
    """
    Generate a professional PDF report (8-9 pages for premium, 3 pages for free).
    
    Args:
        output_path: Where to save the PDF
        property_name: Property name
        vitality_data: Vitality score data
        recommendations: List of recommendations
        analysis_text: "The Problem" narrative
        shopping_list: List of items to buy (organized by tier/category)
        top_three_fixes: Top 3 highest-impact fixes
        report_type: "free" or "premium"
    
    Returns: True if successful
    """
    if not PDF_AVAILABLE:
        logger.warning("⚠️  fpdf2 not available. PDF generation skipped.")
        return False
    
    try:
        if shopping_list is None:
            shopping_list = []
        if top_three_fixes is None:
            top_three_fixes = []
        
        pdf = DesignDiagnosisPDF()
        pdf.add_page()
        
        # PAGE 1: Title + Score + The Problem Narrative
        pdf.set_font("Helvetica", "B", 24)
        pdf.set_text_color(102, 126, 234)
        pdf.cell(0, 15, "Design Diagnosis", 0, 1, "C")
        
        pdf.set_font("Helvetica", "", 14)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 10, sanitize_text_for_pdf(property_name), 0, 1, "C")
        pdf.ln(8)
        
        # Vitality Score Box
        pdf.set_font("Helvetica", "B", 48)
        pdf.set_text_color(102, 126, 234)
        score = vitality_data.get('vitality_score', 0)
        grade = vitality_data.get('grade', 'F')
        pdf.cell(0, 20, str(score), 0, 1, "C")
        
        pdf.set_font("Helvetica", "", 12)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 8, f"Grade: {grade} - {vitality_data.get('grade_label', '')}", 0, 1, "C")
        pdf.ln(8)
        
        # The Problem (Analysis Text)
        if analysis_text:
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 8, "The Situation", 0, 1)
            
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 4, sanitize_text_for_pdf(analysis_text))
            pdf.ln(5)
        
        # PAGE 2-3: Top Three Fixes
        if top_three_fixes:
            if pdf.will_page_break(15):
                pdf.add_page()
            
            pdf.set_font("Helvetica", "B", 14)
            pdf.set_text_color(102, 126, 234)
            pdf.cell(0, 10, "Top 3 High-Impact Fixes", 0, 1)
            pdf.set_text_color(0, 0, 0)
            pdf.ln(3)
            
            for i, fix in enumerate(top_three_fixes[:3], 1):
                if pdf.will_page_break(20):
                    pdf.add_page()
                
                # Fix number and title
                pdf.set_font("Helvetica", "B", 11)
                title = sanitize_text_for_pdf(fix.get('title', ''))
                pdf.cell(0, 8, f"Fix #{i}: {title}", 0, 1)
                
                # Cost estimate
                cost_low = fix.get('cost_low', 0)
                cost_high = fix.get('cost_high', 0)
                pdf.set_font("Helvetica", "", 10)
                pdf.cell(0, 6, f"Est. Cost: ${cost_low}-${cost_high}", 0, 1)
                
                # Description
                pdf.set_font("Helvetica", "", 9)
                description = sanitize_text_for_pdf(fix.get('description', ''))
                pdf.multi_cell(0, 4, description)
                
                # Impact
                impact = fix.get('impact', 'High')
                pdf.set_font("Helvetica", "I", 9)
                pdf.set_text_color(100, 100, 100)
                pdf.cell(0, 5, f"Impact: {impact} | ROI: {fix.get('roi', '')}", 0, 1)
                pdf.set_text_color(0, 0, 0)
                pdf.ln(3)
        
        # PAGE 4: Score Breakdown
        if pdf.will_page_break(15):
            pdf.add_page()
        
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(102, 126, 234)
        pdf.cell(0, 8, "Complete Score Breakdown", 0, 1)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(3)
        
        breakdown = vitality_data.get('breakdown', {})
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 6, f"Guest Comfort: {breakdown.get('comfort', '0/42')}", 0, 1)
        pdf.cell(0, 6, f"Photo Quality: {breakdown.get('photos', '0/20')}", 0, 1)
        pdf.cell(0, 6, f"Design Assessment: {breakdown.get('design', '0/30')}", 0, 1)
        pdf.ln(5)
        
        # All Recommendations
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 6, "All Recommendations", 0, 1)
        pdf.ln(2)
        
        for i, rec in enumerate(recommendations[:10], 1):
            if pdf.will_page_break(10):
                pdf.add_page()
            
            priority = rec.get('priority', '')
            title = sanitize_text_for_pdf(rec.get('title', ''))
            description = sanitize_text_for_pdf(rec.get('description', '')[:100])  # Truncate
            
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 5, f"{i}. [{priority}] {title}", 0, 1)
            
            pdf.set_font("Helvetica", "", 9)
            pdf.multi_cell(0, 3, description)
            pdf.ln(1)
        
        # PAGE 7-8: Shopping List
        if report_type == "premium" and shopping_list:
            if pdf.will_page_break(15):
                pdf.add_page()
            
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_text_color(102, 126, 234)
            pdf.cell(0, 8, "Shopping List (Amazon)", 0, 1)
            pdf.set_text_color(0, 0, 0)
            pdf.ln(3)
            
            current_tier = None
            current_category = None
            
            for item in shopping_list[:20]:  # Limit to 20 items
                if pdf.will_page_break(12):
                    pdf.add_page()
                
                tier = item.get('tier', '')
                category = item.get('category', '')
                
                # Tier header
                if tier != current_tier:
                    pdf.set_font("Helvetica", "B", 10)
                    pdf.set_text_color(102, 126, 234)
                    pdf.cell(0, 6, f"{tier} Tier", 0, 1)
                    current_tier = tier
                    pdf.set_text_color(0, 0, 0)
                
                # Category header
                if category != current_category:
                    pdf.set_font("Helvetica", "B", 9)
                    pdf.cell(0, 5, f"  {category}", 0, 1)
                    current_category = category
                
                # Item
                item_name = sanitize_text_for_pdf(item.get('item', ''))
                price_low = item.get('price_low', 0)
                price_high = item.get('price_high', 0)
                why = sanitize_text_for_pdf(item.get('why', '')[:50])
                
                pdf.set_font("Helvetica", "", 9)
                pdf.cell(0, 5, f"  • {item_name} (${price_low}-${price_high})", 0, 1)
                pdf.set_font("Helvetica", "I", 8)
                pdf.set_text_color(100, 100, 100)
                pdf.multi_cell(0, 3, f"    {why}")
                pdf.set_text_color(0, 0, 0)
                pdf.ln(1)
        
        # PAGE 9: Consultation CTA
        if pdf.will_page_break(15):
            pdf.add_page()
        
        pdf.ln(10)
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(102, 126, 234)
        pdf.cell(0, 10, "Ready to Transform Your Property?", 0, 1)
        
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(5)
        pdf.multi_cell(0, 4, "Book a consultation with Rachel to discuss your specific property, get personalized recommendations, and create a detailed action plan. During the call, we'll prioritize fixes, discuss budget options, and talk about maximizing your ROI.")
        
        pdf.ln(5)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 8, "Book a Consultation", 0, 1)
        
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 6, "Visit: calendly.com/roomsbyrachel", 0, 1)
        pdf.cell(0, 6, "Email: rachellabelles@gmail.com", 0, 1)
        pdf.cell(0, 6, "Instagram: @roomsbyrachel.ca", 0, 1)
        pdf.cell(0, 6, "TikTok: @rooms.by.rachel", 0, 1)
        
        pdf.ln(10)
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(150, 150, 150)
        pdf.multi_cell(0, 4, "Design Diagnosis - Expert Interior Design Analysis for Short-Term Rentals. Powered by Rooms by Rachel. Visit roomsbyrachel.ca")
        
        # Save PDF
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        pdf.output(output_path)
        
        logger.info(f"✅ {report_type.upper()} PDF report generated ({len(shopping_list)} items): {output_path}")
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
