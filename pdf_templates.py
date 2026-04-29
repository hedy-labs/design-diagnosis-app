"""
PDF Templates — Beautiful HTML templates for Design Diagnosis reports

Converts structured report data into professional HTML, then renders to PDF.
Uses weasyprint for beautiful, styled PDFs with proper pagination.
"""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class PDFTemplates:
    """HTML template generation for reports"""
    
    @staticmethod
    def build_premium_report_html(
        property_name: str,
        vitality_score: int,
        grade: str,
        grade_description: str,
        analysis_text: str,
        top_three_fixes: List[Dict],
        recommendations: List[Dict],
        shopping_list: List[Dict],
        comfort_score: int,
        photo_score: int,
        design_score: int
    ) -> str:
        """Build complete 8-9 page premium report HTML"""
        
        # Render top 3 fixes section
        fixes_html = ""
        for i, fix in enumerate(top_three_fixes[:3], 1):
            title = fix.get('title', 'Fix')
            description = fix.get('description', '')
            cost_low = fix.get('cost_low', 0)
            cost_high = fix.get('cost_high', 0)
            impact = fix.get('impact', 'High')
            roi = fix.get('roi', '')
            
            fixes_html += f"""
            <div class="fix-card">
                <div class="fix-number">Fix #{i}</div>
                <h3>{title}</h3>
                <p class="fix-description">{description}</p>
                <div class="fix-details">
                    <span class="cost">Est. Cost: ${cost_low}–${cost_high}</span>
                    <span class="impact">Impact: {impact}</span>
                    <span class="roi">ROI: {roi}</span>
                </div>
            </div>
            """
        
        # Render all recommendations
        all_recs_html = ""
        for i, rec in enumerate(recommendations[:10], 1):
            priority = rec.get('priority', '')
            title = rec.get('title', '')
            description = rec.get('description', '')
            
            all_recs_html += f"""
            <div class="recommendation">
                <span class="priority-badge priority-{priority.lower()}">{priority}</span>
                <h4>{title}</h4>
                <p>{description}</p>
            </div>
            """
        
        # Render shopping list organized by tier
        shopping_html = ""
        current_tier = None
        current_category = None
        
        for item in shopping_list[:20]:
            tier = item.get('tier', '')
            category = item.get('category', '')
            name = item.get('name', 'Item')
            price = item.get('price', 'N/A')
            link = item.get('link', '#')
            description = item.get('description', '')
            
            # Tier header
            if tier != current_tier:
                if current_tier:  # Close previous tier
                    shopping_html += "</div>"
                shopping_html += f"<div class='tier-section'><h4 class='tier-header'>{tier} Tier</h4>"
                current_tier = tier
                current_category = None
            
            # Category header
            if category != current_category:
                if current_category:  # Close previous category
                    shopping_html += "</div>"
                shopping_html += f"<div class='category-section'><h5 class='category-header'>{category}</h5>"
                current_category = category
            
            # Item
            shopping_html += f"""
            <div class="shopping-item">
                <a href="{link}" target="_blank" class="item-name">{name}</a>
                <span class="item-price">{price}</span>
                <p class="item-description">{description}</p>
            </div>
            """
        
        # Close final sections
        if current_category:
            shopping_html += "</div>"
        if current_tier:
            shopping_html += "</div>"
        
        # Assemble complete HTML
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Design Diagnosis Report</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                @page {{
                    size: A4;
                    margin: 0.75in;
                    @bottom-center {{
                        content: "Page " counter(page) " of " counter(pages);
                        font-size: 10px;
                        color: #999;
                    }}
                }}
                
                body {{
                    font-family: 'Montserrat', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    color: #1f2937;
                    line-height: 1.6;
                    background: white;
                }}
                
                /* BUG FIX 3: Ensure fonts render in PDF */
                h1, h2, h3, h4, h5, h6 {{
                    font-family: 'Playfair Display', Georgia, serif;
                }}
                
                /* Gold/champagne accent color for premium aesthetic */
                .accent-color {{
                    color: #C9A876;
                }}
                
                .container {{
                    max-width: 750px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                
                .header {{
                    background: white;
                    border-bottom: 2px solid #C9A876;
                    color: #2C3E50;
                    padding: 40px;
                    border-radius: 8px;
                    text-align: center;
                    margin-bottom: 30px;
                    page-break-after: avoid;
                }}
                
                .header h1 {{
                    font-size: 32px;
                    margin-bottom: 10px;
                }}
                
                .header p {{
                    font-size: 18px;
                    opacity: 0.95;
                }}
                
                .score-card {{
                    background: #f0f4ff;
                    border-left: 4px solid #667eea;
                    padding: 30px;
                    margin-bottom: 30px;
                    border-radius: 8px;
                    text-align: center;
                    page-break-after: avoid;
                }}
                
                .score-card .score {{
                    font-size: 72px;
                    font-weight: bold;
                    color: #667eea;
                    margin: 15px 0;
                }}
                
                .score-card .grade {{
                    font-size: 20px;
                    color: #764ba2;
                    font-weight: bold;
                }}
                
                .score-card .description {{
                    margin-top: 15px;
                    font-size: 14px;
                    color: #4b5563;
                }}
                
                .section {{
                    margin-bottom: 30px;
                    page-break-inside: avoid;
                }}
                
                .section h2 {{
                    font-size: 24px;
                    color: #667eea;
                    margin-bottom: 15px;
                    padding-bottom: 10px;
                    border-bottom: 2px solid #667eea;
                }}
                
                .section h3 {{
                    font-size: 18px;
                    color: #1f2937;
                    margin-top: 20px;
                    margin-bottom: 15px;
                }}
                
                .section p {{
                    margin-bottom: 15px;
                    color: #4b5563;
                    line-height: 1.8;
                }}
                
                .fix-card {{
                    background: #f9fafb;
                    border-left: 4px solid #10b981;
                    padding: 20px;
                    margin-bottom: 15px;
                    border-radius: 4px;
                    page-break-inside: avoid;
                }}
                
                .fix-number {{
                    font-size: 12px;
                    font-weight: bold;
                    color: #10b981;
                    text-transform: uppercase;
                }}
                
                .fix-card h3 {{
                    font-size: 16px;
                    margin: 10px 0;
                }}
                
                .fix-description {{
                    color: #4b5563;
                    margin-bottom: 10px;
                }}
                
                .fix-details {{
                    display: flex;
                    gap: 15px;
                    font-size: 12px;
                }}
                
                .fix-details span {{
                    color: #6b7280;
                }}
                
                .cost {{
                    font-weight: bold;
                    color: #1f2937;
                }}
                
                .recommendation {{
                    background: #f0f9ff;
                    border-left: 4px solid #3b82f6;
                    padding: 15px;
                    margin-bottom: 12px;
                    border-radius: 4px;
                }}
                
                .priority-badge {{
                    display: inline-block;
                    padding: 4px 8px;
                    border-radius: 3px;
                    color: white;
                    font-size: 11px;
                    font-weight: bold;
                    margin-bottom: 8px;
                }}
                
                .priority-critical {{
                    background: #ef4444;
                }}
                
                .priority-high {{
                    background: #f97316;
                }}
                
                .priority-important {{
                    background: #3b82f6;
                }}
                
                .priority-nice {{
                    background: #10b981;
                }}
                
                .recommendation h4 {{
                    font-size: 14px;
                    margin-bottom: 5px;
                    color: #1f2937;
                }}
                
                .recommendation p {{
                    font-size: 13px;
                    color: #4b5563;
                }}
                
                .breakdown {{
                    display: grid;
                    grid-template-columns: 1fr 1fr 1fr;
                    gap: 15px;
                    margin: 20px 0;
                }}
                
                .breakdown-item {{
                    background: #f3f4f6;
                    padding: 15px;
                    border-radius: 6px;
                    text-align: center;
                }}
                
                .breakdown-item .label {{
                    color: #6b7280;
                    font-size: 12px;
                    text-transform: uppercase;
                }}
                
                .breakdown-item .value {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #667eea;
                    margin: 8px 0;
                }}
                
                .tier-section {{
                    margin-bottom: 20px;
                    page-break-inside: avoid;
                }}
                
                .tier-header {{
                    font-size: 14px;
                    font-weight: bold;
                    color: #667eea;
                    padding: 10px 0;
                    border-top: 2px solid #667eea;
                    margin-top: 15px;
                }}
                
                .category-section {{
                    margin-left: 15px;
                }}
                
                .category-header {{
                    font-size: 12px;
                    color: #4b5563;
                    margin-top: 10px;
                    margin-bottom: 8px;
                    font-weight: 600;
                }}
                
                .shopping-item {{
                    margin-bottom: 12px;
                    padding: 8px 0;
                }}
                
                .item-name {{
                    font-weight: 600;
                    color: #667eea;
                    text-decoration: none;
                }}
                
                .item-price {{
                    float: right;
                    color: #1f2937;
                    font-weight: bold;
                }}
                
                .item-description {{
                    font-size: 12px;
                    color: #6b7280;
                    margin-top: 3px;
                }}
                
                .consultation-cta {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 40px;
                    border-radius: 8px;
                    text-align: center;
                    margin-top: 30px;
                    page-break-inside: avoid;
                }}
                
                .consultation-cta h2 {{
                    border: none;
                    color: white;
                    margin-bottom: 15px;
                }}
                
                .consultation-cta p {{
                    color: rgba(255, 255, 255, 0.95);
                    margin-bottom: 20px;
                }}
                
                .consultation-link {{
                    display: inline-block;
                    background: rgba(255, 255, 255, 0.2);
                    color: white;
                    padding: 12px 30px;
                    border-radius: 6px;
                    text-decoration: none;
                    font-weight: bold;
                    border: 2px solid white;
                }}
                
                .footer {{
                    border-top: 1px solid #e5e7eb;
                    padding-top: 20px;
                    margin-top: 30px;
                    text-align: center;
                    color: #999;
                    font-size: 11px;
                }}
                
                .footer p {{
                    margin: 5px 0;
                }}
                
                .footer a {{
                    color: #667eea;
                    text-decoration: none;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <!-- PAGE 1: Header + Score + Analysis -->
                <div class="header">
                    <h1>Design Diagnosis Report</h1>
                    <p>{property_name}</p>
                </div>
                
                <div class="score-card">
                    <div class="score">{vitality_score}</div>
                    <div class="grade">Grade {grade}</div>
                    <div class="description">{grade_description}</div>
                </div>
                
                <div class="section">
                    <h2>The Situation</h2>
                    <p>{analysis_text}</p>
                </div>
                
                <!-- PAGE 2-3: Top 3 Fixes -->
                <div class="section">
                    <h2>Top 3 High-Impact Fixes</h2>
                    {fixes_html}
                </div>
                
                <!-- PAGE 4: Score Breakdown + Recommendations -->
                <div class="section">
                    <h2>Complete Score Breakdown</h2>
                    <div class="breakdown">
                        <div class="breakdown-item">
                            <div class="label">Guest Comfort</div>
                            <div class="value">{comfort_score}</div>
                            <div class="label">/ 42 points</div>
                        </div>
                        <div class="breakdown-item">
                            <div class="label">Photo Quality</div>
                            <div class="value">{photo_score}</div>
                            <div class="label">/ 20 points</div>
                        </div>
                        <div class="breakdown-item">
                            <div class="label">Design Assessment</div>
                            <div class="value">{design_score}</div>
                            <div class="label">/ 30 points</div>
                        </div>
                    </div>
                </div>
                
                <!-- PAGE 5-6: All Recommendations -->
                <div class="section">
                    <h2>All Recommendations</h2>
                    {all_recs_html}
                </div>
                
                <!-- PAGE 7-8: Shopping List -->
                <div class="section">
                    <h2>Shopping List</h2>
                    {shopping_html}
                </div>
                
                <!-- PAGE 9: Consultation CTA -->
                <div class="consultation-cta">
                    <h2>Ready to Transform Your Property?</h2>
                    <p>Book a consultation with Rachel to discuss your specific situation, prioritize fixes, and create a detailed action plan.</p>
                    <a href="https://calendly.com/roomsbyrachel" class="consultation-link">Schedule a Consultation</a>
                </div>
                
                <div class="footer">
                    <p><strong>Rooms by Rachel</strong> — Design Diagnosis</p>
                    <p>Expert Interior Design Analysis for Short-Term Rentals</p>
                    <p><a href="https://roomsbyrachel.ca">roomsbyrachel.ca</a></p>
                    <p>© 2026 Rooms by Rachel. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    @staticmethod
    def build_free_report_html(
        property_name: str,
        vitality_score: int,
        grade: str,
        grade_description: str,
        analysis_text: str,
        top_three_fixes: List[Dict]
    ) -> str:
        """Build 3-page free report HTML (no shopping list)"""
        
        fixes_html = ""
        for i, fix in enumerate(top_three_fixes[:3], 1):
            title = fix.get('title', 'Fix')
            description = fix.get('description', '')
            cost_low = fix.get('cost_low', 0)
            cost_high = fix.get('cost_high', 0)
            
            fixes_html += f"""
            <div class="fix-card">
                <div class="fix-number">Fix #{i}</div>
                <h3>{title}</h3>
                <p class="fix-description">{description}</p>
                <div class="cost">Est. Cost: ${cost_low}–${cost_high}</div>
            </div>
            """
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Design Diagnosis Report</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                @page {{
                    size: A4;
                    margin: 0.75in;
                }}
                
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    color: #1f2937;
                    line-height: 1.6;
                }}
                
                .container {{
                    max-width: 750px;
                    margin: 0 auto;
                }}
                
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 40px;
                    border-radius: 8px;
                    text-align: center;
                    margin-bottom: 30px;
                }}
                
                .header h1 {{
                    font-size: 32px;
                    margin-bottom: 10px;
                }}
                
                .header p {{
                    font-size: 18px;
                }}
                
                .score-card {{
                    background: #f0f4ff;
                    border-left: 4px solid #667eea;
                    padding: 30px;
                    margin-bottom: 30px;
                    border-radius: 8px;
                    text-align: center;
                }}
                
                .score-card .score {{
                    font-size: 72px;
                    font-weight: bold;
                    color: #667eea;
                    margin: 15px 0;
                }}
                
                .score-card .grade {{
                    font-size: 20px;
                    color: #764ba2;
                    font-weight: bold;
                }}
                
                .section {{
                    margin-bottom: 30px;
                }}
                
                .section h2 {{
                    font-size: 24px;
                    color: #667eea;
                    margin-bottom: 15px;
                    padding-bottom: 10px;
                    border-bottom: 2px solid #667eea;
                }}
                
                .section p {{
                    margin-bottom: 15px;
                    color: #4b5563;
                    line-height: 1.8;
                }}
                
                .fix-card {{
                    background: #f9fafb;
                    border-left: 4px solid #10b981;
                    padding: 20px;
                    margin-bottom: 15px;
                    border-radius: 4px;
                }}
                
                .fix-number {{
                    font-size: 12px;
                    font-weight: bold;
                    color: #10b981;
                    text-transform: uppercase;
                }}
                
                .fix-card h3 {{
                    font-size: 16px;
                    margin: 10px 0;
                }}
                
                .fix-description {{
                    color: #4b5563;
                    margin-bottom: 10px;
                }}
                
                .cost {{
                    color: #1f2937;
                    font-weight: bold;
                    font-size: 12px;
                }}
                
                .cta {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 8px;
                    text-align: center;
                    margin-top: 30px;
                }}
                
                .cta h2 {{
                    border: none;
                    color: white;
                    margin-bottom: 15px;
                    font-size: 20px;
                }}
                
                .cta p {{
                    color: rgba(255, 255, 255, 0.95);
                    margin-bottom: 15px;
                    font-size: 14px;
                }}
                
                .cta-link {{
                    display: inline-block;
                    background: rgba(255, 255, 255, 0.2);
                    color: white;
                    padding: 10px 25px;
                    border-radius: 6px;
                    text-decoration: none;
                    font-weight: bold;
                    border: 2px solid white;
                }}
                
                .footer {{
                    border-top: 1px solid #e5e7eb;
                    padding-top: 20px;
                    margin-top: 30px;
                    text-align: center;
                    color: #999;
                    font-size: 11px;
                }}
                
                .footer p {{
                    margin: 5px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Design Diagnosis Report</h1>
                    <p>{property_name}</p>
                </div>
                
                <div class="score-card">
                    <div class="score">{vitality_score}</div>
                    <div class="grade">Grade {grade}</div>
                </div>
                
                <div class="section">
                    <h2>The Situation</h2>
                    <p>{analysis_text}</p>
                </div>
                
                <div class="section">
                    <h2>Top 3 Fixes</h2>
                    {fixes_html}
                </div>
                
                <div class="cta">
                    <h2>Want the Full Report?</h2>
                    <p>Upgrade to Premium for 8-9 pages of detailed analysis, complete shopping lists, and professional recommendations.</p>
                    <a href="https://roomsbyrachel.ca" class="cta-link">View Premium Options</a>
                </div>
                
                <div class="footer">
                    <p><strong>Rooms by Rachel</strong> — Design Diagnosis</p>
                    <p>© 2026 All rights reserved</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
