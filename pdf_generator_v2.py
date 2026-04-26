"""
PDF Generator V2 — HTML-to-PDF Conversion using Weasyprint

Renders beautiful, styled PDFs from HTML templates with proper pagination,
links, and professional formatting. Replaces basic fpdf2 approach.
"""

import logging
import os
from typing import Dict, List
from pdf_templates import PDFTemplates

logger = logging.getLogger(__name__)


def generate_pdf_report_v2(
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
    Generate professional PDF report using HTML templates + Weasyprint.
    
    Args:
        output_path: Where to save the PDF
        property_name: Property name
        vitality_data: Vitality score data
        recommendations: All recommendations
        analysis_text: "The Problem" narrative
        shopping_list: Shopping items
        top_three_fixes: Top 3 fixes
        report_type: "free" or "premium"
    
    Returns: True if successful
    """
    try:
        # Import weasyprint (required for this function)
        try:
            from weasyprint import HTML, CSS
            from io import BytesIO
        except ImportError:
            logger.error("⚠️  weasyprint not installed. Install with: pip install weasyprint")
            logger.info("Fallback: Would need fpdf2 or other PDF library")
            return False
        
        if shopping_list is None:
            shopping_list = []
        if top_three_fixes is None:
            top_three_fixes = []
        
        # Extract vitality data
        score = vitality_data.get('vitality_score', 0)
        grade = vitality_data.get('grade', 'F')
        grade_description = vitality_data.get('grade_description', '')
        comfort_score = vitality_data.get('comfort_score', 0)
        photo_score = vitality_data.get('photo_score', 0)
        design_score = vitality_data.get('design_score', 0)
        
        logger.info(f"📄 Generating {report_type.upper()} PDF: {property_name}")
        
        # Generate HTML from template
        if report_type == "premium":
            html_content = PDFTemplates.build_premium_report_html(
                property_name=property_name,
                vitality_score=score,
                grade=grade,
                grade_description=grade_description,
                analysis_text=analysis_text,
                top_three_fixes=top_three_fixes,
                recommendations=recommendations,
                shopping_list=shopping_list,
                comfort_score=comfort_score,
                photo_score=photo_score,
                design_score=design_score
            )
            logger.info(f"✅ Premium HTML template generated")
        else:
            html_content = PDFTemplates.build_free_report_html(
                property_name=property_name,
                vitality_score=score,
                grade=grade,
                grade_description=grade_description,
                analysis_text=analysis_text,
                top_three_fixes=top_three_fixes
            )
            logger.info(f"✅ Free HTML template generated")
        
        # Create directories if needed
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Convert HTML to PDF using Weasyprint
        try:
            html_obj = HTML(string=html_content)
            html_obj.write_pdf(output_path)
            logger.info(f"✅ PDF generated successfully: {output_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Weasyprint conversion failed: {e}")
            return False
    
    except Exception as e:
        logger.error(f"❌ PDF generation error: {e}")
        return False


def generate_html_report(
    property_name: str,
    vitality_data: Dict,
    recommendations: List[Dict],
    analysis_text: str = "",
    shopping_list: List[Dict] = None,
    top_three_fixes: List[Dict] = None,
    report_type: str = "free"
) -> str:
    """
    Generate HTML report without PDF conversion (for email viewing).
    
    Returns: HTML string
    """
    if shopping_list is None:
        shopping_list = []
    if top_three_fixes is None:
        top_three_fixes = []
    
    score = vitality_data.get('vitality_score', 0)
    grade = vitality_data.get('grade', 'F')
    grade_description = vitality_data.get('grade_description', '')
    comfort_score = vitality_data.get('comfort_score', 0)
    photo_score = vitality_data.get('photo_score', 0)
    design_score = vitality_data.get('design_score', 0)
    
    if report_type == "premium":
        html = PDFTemplates.build_premium_report_html(
            property_name=property_name,
            vitality_score=score,
            grade=grade,
            grade_description=grade_description,
            analysis_text=analysis_text,
            top_three_fixes=top_three_fixes,
            recommendations=recommendations,
            shopping_list=shopping_list,
            comfort_score=comfort_score,
            photo_score=photo_score,
            design_score=design_score
        )
    else:
        html = PDFTemplates.build_free_report_html(
            property_name=property_name,
            vitality_score=score,
            grade=grade,
            grade_description=grade_description,
            analysis_text=analysis_text,
            top_three_fixes=top_three_fixes
        )
    
    return html
