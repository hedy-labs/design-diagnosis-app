"""
Design Diagnosis PDF Report Generator

Generates branded PDF reports using ReportLab.
Brand: Rooms by Rachel
Sections: Vitality Score + 7 Dimensions + Recommendations + ROI Projection
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from datetime import datetime
from typing import List, Dict, Optional
import os


class VitalityReportPDF:
    """Generate PDF report for Design Diagnosis Vitality Score"""
    
    # Rooms by Rachel branding colors
    BRAND_PRIMARY = colors.HexColor("#2C3E50")      # Dark blue-gray
    BRAND_SECONDARY = colors.HexColor("#E74C3C")    # Coral red
    BRAND_ACCENT = colors.HexColor("#F39C12")       # Gold
    NEUTRAL_LIGHT = colors.HexColor("#ECF0F1")      # Light gray
    
    # Grade colors
    GRADE_COLORS = {
        "A": colors.HexColor("#27AE60"),  # Green
        "B": colors.HexColor("#2ECC71"),  # Light green
        "C": colors.HexColor("#F39C12"),  # Orange
        "D": colors.HexColor("#E67E22"),  # Dark orange
        "F": colors.HexColor("#E74C3C"),  # Red
    }
    
    def __init__(self, output_path: str = "report.pdf"):
        self.output_path = output_path
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles for branding"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='BrandTitle',
            parent=self.styles['Heading1'],
            fontSize=28,
            textColor=self.BRAND_PRIMARY,
            spaceAfter=6,
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle
        self.styles.add(ParagraphStyle(
            name='BrandSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=self.BRAND_SECONDARY,
            spaceAfter=12
        ))
        
        # Section heading
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=self.BRAND_PRIMARY,
            spaceAfter=10,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Normal text
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=10,
            leading=14
        ))
    
    def generate(
        self,
        property_name: str,
        location: str,
        vitality_score: float,
        grade: str,
        total_points: float,
        dimension_scores: Dict[int, float],
        missing_items: Optional[List[str]] = None,
        cost_estimate: float = 0.0,
        roi_projection: float = 0.0
    ):
        """
        Generate complete PDF report.
        
        Parameters:
        - property_name: Property name
        - location: Property location
        - vitality_score: Final score (0–100)
        - grade: Letter grade (A–F)
        - total_points: Points out of 150
        - dimension_scores: Dict of dimension scores {1: 18, 2: 15, ...}
        - missing_items: List of missing items from hidden friction
        - cost_estimate: Estimated remediation cost
        - roi_projection: Projected ROI percentage
        """
        
        doc = SimpleDocTemplate(
            self.output_path,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        story = []
        
        # ====================================================================
        # SECTION 1: HEADER & VITALITY SCORE
        # ====================================================================
        
        # Brand header
        brand_text = Paragraph("ROOMS BY RACHEL", self.styles['BrandTitle'])
        story.append(brand_text)
        
        subtitle = Paragraph("Design Diagnosis: Vitality Score Report", self.styles['BrandSubtitle'])
        story.append(subtitle)
        story.append(Spacer(1, 0.2*inch))
        
        # Property info
        property_info = f"<b>{property_name}</b> • {location}"
        story.append(Paragraph(property_info, self.styles['CustomBody']))
        story.append(Spacer(1, 0.1*inch))
        
        # Vitality score box
        score_color = self.GRADE_COLORS.get(grade, colors.black)
        score_table_data = [
            [
                Paragraph(f"<font size=48 color={score_color.hexval()}><b>{vitality_score:.0f}</b></font>", self.styles['CustomBody']),
                Paragraph(f"<font size=36 color={score_color.hexval()}><b>{grade}</b></font>", self.styles['CustomBody']),
                Paragraph(
                    f"<font size=11><b>{total_points:.0f}/150 points</b></font><br/>"
                    f"<font size=10>Guest satisfaction: <b>{self._grade_interpretation(grade)}</b></font>",
                    self.styles['CustomBody']
                )
            ]
        ]
        
        score_table = Table(score_table_data, colWidths=[1.2*inch, 0.8*inch, 2*inch])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.NEUTRAL_LIGHT),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BORDER', (0, 0), (-1, -1), 2, self.BRAND_PRIMARY),
        ]))
        story.append(score_table)
        story.append(Spacer(1, 0.3*inch))
        
        # ====================================================================
        # SECTION 2: DIMENSION BREAKDOWN (7 DIMENSIONS)
        # ====================================================================
        
        story.append(Paragraph("Dimension Breakdown", self.styles['SectionHeading']))
        
        dimension_labels = {
            1: "Bedroom Standards",
            2: "Functionality & Flow",
            3: "Light & Brightness",
            4: "Storage & Organization",
            5: "Condition & Maintenance",
            6: "Photo Strategy",
            7: "Hidden Friction"
        }
        
        dimension_data = [["Dimension", "Score", "Status"]]
        for dim in range(1, 8):
            score = dimension_scores.get(dim, 0.0)
            max_pts = 20 if dim != 6 else 10
            max_pts = 20 if dim == 7 else max_pts
            
            pct = (score / max_pts) * 100
            status = self._status_from_score(pct)
            
            dimension_data.append([
                dimension_labels[dim],
                f"{score:.1f}/{max_pts}",
                status
            ])
        
        dim_table = Table(dimension_data, colWidths=[2.5*inch, 1.2*inch, 1.3*inch])
        dim_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.BRAND_PRIMARY),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.NEUTRAL_LIGHT]),
        ]))
        story.append(dim_table)
        story.append(Spacer(1, 0.2*inch))
        
        # ====================================================================
        # SECTION 3: KEY FINDINGS (HIDDEN FRICTION)
        # ====================================================================
        
        if missing_items:
            story.append(Paragraph("Key Findings: Missing Items", self.styles['SectionHeading']))
            
            missing_text = "<br/>".join([f"• {item}" for item in missing_items[:15]])  # Limit to 15
            if len(missing_items) > 15:
                missing_text += f"<br/>• ... and {len(missing_items) - 15} more items"
            
            story.append(Paragraph(missing_text, self.styles['CustomBody']))
            story.append(Spacer(1, 0.2*inch))
        
        # ====================================================================
        # SECTION 4: RECOMMENDATIONS & ROI
        # ====================================================================
        
        story.append(Paragraph("Investment & Recommendations", self.styles['SectionHeading']))
        
        if cost_estimate > 0:
            story.append(Paragraph(
                f"<b>Estimated Remediation Cost:</b> ${cost_estimate:,.0f}",
                self.styles['CustomBody']
            ))
        
        if roi_projection > 0:
            story.append(Paragraph(
                f"<b>Projected ROI (12 months):</b> {roi_projection:.0f}% booking increase",
                self.styles['CustomBody']
            ))
        
        story.append(Spacer(1, 0.1*inch))
        
        # Recommendations
        recommendations = self._generate_recommendations(grade, missing_items or [])
        rec_text = "<br/>".join([f"• {r}" for r in recommendations])
        story.append(Paragraph(rec_text, self.styles['CustomBody']))
        
        story.append(Spacer(1, 0.3*inch))
        
        # ====================================================================
        # FOOTER
        # ====================================================================
        
        footer_text = (
            f"Report generated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC<br/>"
            f"Rooms by Rachel • <i>Design Diagnosis Analysis</i>"
        )
        story.append(Paragraph(footer_text, self.styles['CustomBody']))
        
        # Build PDF
        doc.build(story)
        return self.output_path
    
    @staticmethod
    def _grade_interpretation(grade: str) -> str:
        """Get interpretation text for grade"""
        interpretations = {
            "A": "Excellent",
            "B": "Very Good",
            "C": "Good",
            "D": "Fair",
            "F": "Needs Work"
        }
        return interpretations.get(grade, "Unknown")
    
    @staticmethod
    def _status_from_score(pct: float) -> str:
        """Convert percentage to status text"""
        if pct >= 90:
            return "✓ Excellent"
        elif pct >= 75:
            return "✓ Good"
        elif pct >= 60:
            return "△ Fair"
        else:
            return "✗ Needs Work"
    
    @staticmethod
    def _generate_recommendations(grade: str, missing_items: List[str]) -> List[str]:
        """Generate recommendations based on grade and missing items"""
        recommendations = []
        
        if grade == "F":
            recommendations.append("Priority: Address critical missing items (power bars, plungers, hangers)")
            recommendations.append("Enhance bedroom comfort with proper lighting and textiles")
            recommendations.append("Improve storage organization significantly")
        
        elif grade == "D":
            recommendations.append("Focus on functional essentials (power supply, hangers, drying)")
            recommendations.append("Add comfort items (lamps, nightstands, textiles)")
            recommendations.append("Organize storage more effectively")
        
        elif grade == "C":
            recommendations.append("Optimize lighting in key areas")
            recommendations.append("Expand storage solutions")
            recommendations.append("Add decorative elements for warmth")
        
        elif grade == "B":
            recommendations.append("Consider premium touches (artwork, plants, premium linens)")
            recommendations.append("Optimize photo consistency and staging")
            recommendations.append("Fine-tune spaces for specific guest types")
        
        elif grade == "A":
            recommendations.append("Maintain current standards consistently")
            recommendations.append("Continue strategic photo updates")
            recommendations.append("Monitor guest feedback for emerging needs")
        
        # Add item-specific recommendations
        if "hangers" in str(missing_items).lower():
            recommendations.append("Add 10+ hangers per bedroom closet for guest convenience")
        
        if "dryer" in str(missing_items).lower() or "drying" in str(missing_items).lower():
            recommendations.append("Install dryer or provide quality drying rack")
        
        if "lamp" in str(missing_items).lower():
            recommendations.append("Add task lighting (bedside + desk lamps) for functionality")
        
        return recommendations[:5]  # Return top 5


# ============================================================================
# TEST HARNESS
# ============================================================================

if __name__ == "__main__":
    print("=== Design Diagnosis PDF Report Generator Test ===\n")
    
    # Test report generation
    pdf_gen = VitalityReportPDF("test_report.pdf")
    
    test_dimension_scores = {
        1: 14, 2: 15, 3: 16, 4: 12, 5: 14, 6: 7, 7: 6
    }
    
    test_missing = [
        "Insufficient hangers in bedrooms",
        "No clothes dryer or drying rack",
        "Limited storage space",
        "Minimal task lighting",
        "Few bedside amenities"
    ]
    
    output_file = pdf_gen.generate(
        property_name="Test Property",
        location="Kuala Lumpur, Malaysia",
        vitality_score=59.3,
        grade="F",
        total_points=89.0,
        dimension_scores=test_dimension_scores,
        missing_items=test_missing,
        cost_estimate=1200.0,
        roi_projection=18.5
    )
    
    print(f"✅ PDF report generated: {output_file}")
