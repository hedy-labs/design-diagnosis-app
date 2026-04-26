"""
Report Generator — Design Diagnosis

Generates vitality scores, recommendations, and PDF reports
based on Rachel's 92-point framework.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class VitalityScorer:
    """92-Point Vitality Scoring System"""
    
    # Guest Comfort Checklist Items (42 points total)
    TIER_1_ITEMS = {
        "bedside_lamps": 3,
        "bedside_tables": 3,
        "two_towels_per_guest": 3,
        "two_pillows_per_guest": 3,
        "plunger": 3,
        "soap_dispenser": 3,
        "mattress_protectors": 3,
    }
    
    TIER_2_ITEMS = {
        "hangers": 2,
        "power_bars": 2,
        "dish_drying_rack": 2,
        "pillow_protectors": 2,
    }
    
    TIER_3_ITEMS = {
        "shower_hooks": 1,
        "towel_hooks": 1,
        "face_cloths": 1,
        "extra_blanket": 1,
        "full_length_mirror": 1,
        "entry_hooks": 1,
        "shoe_rack": 1,
        "welcome_basket": 1,
        "bathroom_caddy": 1,
        "desk_chair": 1,
        "workspace": 1,
        "coffee_maker": 1,
        "can_opener": 1,
    }
    
    def __init__(self):
        self.total_points = 92
    
    def calculate_guest_comfort_score(self, checklist: List[str]) -> int:
        """
        Calculate guest comfort score from checklist items.
        
        checklist: List of item IDs that are present
        Returns: Points earned (0-42)
        """
        points = 0
        
        for item in checklist:
            if item in self.TIER_1_ITEMS:
                points += self.TIER_1_ITEMS[item]
            elif item in self.TIER_2_ITEMS:
                points += self.TIER_2_ITEMS[item]
            elif item in self.TIER_3_ITEMS:
                points += self.TIER_3_ITEMS[item]
        
        # Cap at 42
        return min(points, 42)
    
    def calculate_photo_score(self, total_photos) -> int:
        """
        Calculate photo score (0-20 points).
        
        Ideal: 10-40 photos (5 pts)
        Low: <10 or >40 photos (2 pts)
        Quality assessment: Up to 15 pts
        
        Handles string inputs like "51+" by extracting numeric part.
        """
        from sanitizer import sanitize_integer
        
        count_score = 0
        
        # Sanitize input: handles "51+", strings, integers
        total_photos = sanitize_integer(total_photos, default=20)
        
        # Photo count penalty/reward
        if 10 <= total_photos <= 40:
            count_score = 5  # Ideal range
        else:
            count_score = 2  # Too few or too many
        
        # Mock quality assessment (in real app, use Claude Vision)
        quality_score = 10  # Default: good quality assumption
        
        total = count_score + quality_score
        return min(total, 20)
    
    def calculate_design_score(self, design_factors: Dict[str, int]) -> int:
        """
        Calculate design assessment score (0-30 points).
        
        design_factors: {
            'lighting_quality': 0-6,
            'functionality': 0-6,
            'color_harmony': 0-6,
            'clutter_and_flow': 0-6,
            'staging_integrity': 0-6,
        }
        """
        # Default values if not provided
        defaults = {
            'lighting_quality': 4,
            'functionality': 4,
            'color_harmony': 4,
            'clutter_and_flow': 4,
            'staging_integrity': 4,
        }
        
        factors = {**defaults, **design_factors}
        
        total = sum([
            factors.get('lighting_quality', 4),
            factors.get('functionality', 4),
            factors.get('color_harmony', 4),
            factors.get('clutter_and_flow', 4),
            factors.get('staging_integrity', 4),
        ])
        
        return min(total, 30)
    
    def calculate_vitality_score(
        self,
        guest_comfort_checklist: List[str],
        total_photos: int,
        design_factors: Optional[Dict[str, int]] = None
    ) -> tuple:
        """
        Calculate overall Vitality Score (0-100).
        
        Returns: (score, grade, summary)
        """
        comfort_score = self.calculate_guest_comfort_score(guest_comfort_checklist)
        photo_score = self.calculate_photo_score(total_photos)
        design_score = self.calculate_design_score(design_factors or {})
        
        raw_score = comfort_score + photo_score + design_score
        vitality_score = round((raw_score / self.total_points) * 100)
        
        # Determine grade
        if vitality_score >= 90:
            grade = "A"
            grade_label = "Excellent"
            grade_description = "Move-in ready. Beautiful, functional, guest-ready."
        elif vitality_score >= 80:
            grade = "B"
            grade_label = "Good"
            grade_description = "Strong property with minor improvements needed."
        elif vitality_score >= 70:
            grade = "C"
            grade_label = "Fair"
            grade_description = "Some important items missing. Guests will notice gaps."
        elif vitality_score >= 60:
            grade = "D"
            grade_label = "Poor"
            grade_description = "Multiple gaps. Guests will struggle with basics."
        else:
            grade = "F"
            grade_label = "Critical"
            grade_description = "Major improvements needed urgently."
        
        return {
            'vitality_score': vitality_score,
            'grade': grade,
            'grade_label': grade_label,
            'grade_description': grade_description,
            'raw_score': raw_score,
            'comfort_score': comfort_score,
            'photo_score': photo_score,
            'design_score': design_score,
            'breakdown': {
                'comfort': f"{comfort_score}/42",
                'photos': f"{photo_score}/20",
                'design': f"{design_score}/30",
            }
        }


class ReportBuilder:
    """Build HTML/PDF reports with recommendations"""
    
    def __init__(self, submission_data: Dict, vitality_data: Dict):
        self.submission = submission_data
        self.vitality = vitality_data
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    def build_html_report(self) -> str:
        """Generate HTML report content"""
        
        property_name = self.submission.get('property_name', 'Property')
        vitality_score = self.vitality['vitality_score']
        grade = self.vitality['grade']
        grade_label = self.vitality['grade_label']
        
        # Generate recommendations based on gaps
        recommendations = self._generate_recommendations()
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #1f2937; line-height: 1.6; }}
                .container {{ max-width: 900px; margin: 0 auto; padding: 40px 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; border-radius: 8px; text-align: center; margin-bottom: 30px; }}
                .header h1 {{ font-size: 32px; margin-bottom: 10px; }}
                .header p {{ font-size: 16px; opacity: 0.9; }}
                .score-card {{ background: #f3f4f6; border-radius: 8px; padding: 30px; text-align: center; margin-bottom: 30px; }}
                .vitality-number {{ font-size: 72px; font-weight: bold; color: #667eea; }}
                .grade-badge {{ 
                    display: inline-block; 
                    background: {self._get_grade_color(grade)};
                    color: white; 
                    padding: 8px 16px; 
                    border-radius: 20px; 
                    font-weight: bold; 
                    margin-top: 10px;
                }}
                .section {{ margin-bottom: 30px; }}
                .section h2 {{ font-size: 24px; color: #1f2937; margin-bottom: 15px; border-bottom: 2px solid #667eea; padding-bottom: 10px; }}
                .section h3 {{ font-size: 18px; color: #4b5563; margin-top: 20px; margin-bottom: 10px; }}
                .breakdown {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-bottom: 20px; }}
                .breakdown-item {{ background: #f9fafb; padding: 15px; border-radius: 6px; text-align: center; }}
                .breakdown-item .label {{ color: #6b7280; font-size: 12px; text-transform: uppercase; }}
                .breakdown-item .value {{ font-size: 28px; font-weight: bold; color: #667eea; margin-top: 5px; }}
                .recommendation {{ background: #f0f9ff; border-left: 4px solid #3b82f6; padding: 15px; margin-bottom: 12px; border-radius: 4px; }}
                .recommendation .priority {{ display: inline-block; background: #3b82f6; color: white; padding: 4px 8px; border-radius: 3px; font-size: 11px; font-weight: bold; margin-right: 8px; }}
                .recommendation .title {{ font-weight: 600; margin-bottom: 5px; }}
                .recommendation .description {{ color: #4b5563; font-size: 14px; }}
                .footer {{ border-top: 1px solid #e5e7eb; padding-top: 20px; color: #6b7280; font-size: 12px; text-align: center; margin-top: 40px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✨ Design Diagnosis Report</h1>
                    <p>{property_name}</p>
                </div>
                
                <div class="score-card">
                    <div class="vitality-number">{vitality_score}</div>
                    <p>Vitality Score</p>
                    <div class="grade-badge">{grade}: {grade_label}</div>
                </div>
                
                <div class="section">
                    <h2>Your Score Breakdown</h2>
                    <div class="breakdown">
                        <div class="breakdown-item">
                            <div class="label">Guest Comfort</div>
                            <div class="value">{self.vitality['comfort_score']}</div>
                            <div class="label">/ 42 points</div>
                        </div>
                        <div class="breakdown-item">
                            <div class="label">Photos</div>
                            <div class="value">{self.vitality['photo_score']}</div>
                            <div class="label">/ 20 points</div>
                        </div>
                        <div class="breakdown-item">
                            <div class="label">Design</div>
                            <div class="value">{self.vitality['design_score']}</div>
                            <div class="label">/ 30 points</div>
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>What This Score Means</h2>
                    <p>{self.vitality['grade_description']}</p>
                </div>
                
                <div class="section">
                    <h2>Top Recommendations</h2>
                    {self._render_recommendations_html(recommendations)}
                </div>
                
                <div class="footer">
                    <p>Design Diagnosis Report • Generated {self.timestamp}</p>
                    <p>Powered by Rachel's Interior Design Expertise</p>
                    <p>© 2026 Rooms by Rachel. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _generate_recommendations(self) -> List[Dict]:
        """Generate recommendations based on missing comfort items"""
        
        recommendations = []
        comfort_checklist = self.submission.get('guest_comfort_checklist', [])
        missing_items = self._find_missing_items(comfort_checklist)
        
        # Tier 1 (Critical)
        tier1_missing = [item for item in missing_items if item in VitalityScorer.TIER_1_ITEMS]
        if tier1_missing:
            recommendations.append({
                'priority': 'Critical',
                'title': 'Essential Guest Comfort Items Missing',
                'description': f"Add: {', '.join(tier1_missing)}. These directly impact guest satisfaction.",
                'impact': 'High'
            })
        
        # Tier 2 (High Impact)
        tier2_missing = [item for item in missing_items if item in VitalityScorer.TIER_2_ITEMS]
        if tier2_missing:
            recommendations.append({
                'priority': 'High',
                'title': 'Important Conveniences Missing',
                'description': f"Add: {', '.join(tier2_missing)}. These improve guest experience.",
                'impact': 'Medium'
            })
        
        # Tier 3 (Nice to Have)
        tier3_missing = [item for item in missing_items if item in VitalityScorer.TIER_3_ITEMS]
        if tier3_missing:
            recommendations.append({
                'priority': 'Nice to Have',
                'title': 'Polish & Details',
                'description': f"Consider adding: {', '.join(tier3_missing)}. These elevate the property.",
                'impact': 'Low'
            })
        
        # Photo advice
        if self.vitality['photo_score'] < 15:
            recommendations.append({
                'priority': 'Important',
                'title': 'Photo Strategy',
                'description': 'Consider professional photography. Quality photos increase bookings by 15-25%.',
                'impact': 'High'
            })
        
        return recommendations[:5]  # Top 5 recommendations
    
    def _find_missing_items(self, checklist: List[str]) -> List[str]:
        """Find items not in the checklist"""
        all_items = set(VitalityScorer.TIER_1_ITEMS.keys()) | \
                   set(VitalityScorer.TIER_2_ITEMS.keys()) | \
                   set(VitalityScorer.TIER_3_ITEMS.keys())
        return list(all_items - set(checklist))
    
    def _render_recommendations_html(self, recommendations: List[Dict]) -> str:
        """Render recommendations as HTML"""
        html = ""
        for rec in recommendations:
            priority_color = {
                'Critical': '#ef4444',
                'High': '#f97316',
                'Important': '#3b82f6',
                'Nice to Have': '#10b981'
            }.get(rec['priority'], '#6b7280')
            
            html += f"""
            <div class="recommendation">
                <span class="priority" style="background: {priority_color};">{rec['priority']}</span>
                <div class="title">{rec['title']}</div>
                <div class="description">{rec['description']}</div>
            </div>
            """
        return html
    
    def _get_grade_color(self, grade: str) -> str:
        """Get color for grade badge"""
        colors = {
            'A': '#10b981',
            'B': '#3b82f6',
            'C': '#f59e0b',
            'D': '#ef4444',
            'F': '#7f1d1d'
        }
        return colors.get(grade, '#6b7280')
    
    def generate_analysis_text(self) -> str:
        """
        Generate 'The Problem' narrative explaining the score.
        
        Returns: 2-3 paragraph analysis in Rachel's voice
        """
        property_name = self.submission.get('property_name', 'Your property')
        score = self.vitality['vitality_score']
        grade = self.vitality['grade']
        comfort_score = self.vitality['comfort_score']
        photo_score = self.vitality['photo_score']
        design_score = self.vitality['design_score']
        checklist = self.submission.get('guest_comfort_checklist', [])
        
        # Identify key missing items
        all_items = set(VitalityScorer.TIER_1_ITEMS.keys()) | \
                   set(VitalityScorer.TIER_2_ITEMS.keys()) | \
                   set(VitalityScorer.TIER_3_ITEMS.keys())
        missing = list(all_items - set(checklist))[:3]  # Top 3 missing items
        
        missing_text = ", ".join(missing) if missing else "various comfort items"
        
        # Grade-specific narrative
        if score >= 90:
            intro = f"🎉 Excellent work! {property_name} is move-in ready and guest-focused. You've created a beautiful, functional space that guests will love."
            body = f"Your score of {score}/100 (Grade {grade}: {self.vitality['grade_label']}) reflects strong fundamentals across all dimensions. Minor polish opportunities remain, but your property is positioned for success."
            cta = "Focus on maintaining consistency and gathering guest reviews to build social proof."
        
        elif score >= 80:
            intro = f"👍 {property_name} has strong bones and good guest fundamentals. You're in the solid 'bookable' range with just a few intentional upgrades needed."
            body = f"Your score of {score}/100 (Grade {grade}: {self.vitality['grade_label']}) shows you've covered most essentials. The missing {missing_text} are straightforward fixes that will significantly improve guest perception without major investment."
            cta = "Add the three high-impact fixes below and re-submit in 30 days for a rescoring."
        
        elif score >= 70:
            intro = f"⚠️ {property_name} has potential but needs strategic improvements. Right now, guests will notice gaps that signal 'rushed listing.'"
            body = f"Your score of {score}/100 (Grade {grade}: {self.vitality['grade_label']}) reflects {missing_text} missing from guest-critical categories. These aren't cosmetic—they're the difference between a 4-star and 5-star experience. The good news: all are solvable with focused effort and modest budget."
            cta = "Implement the three fixes below within 2 weeks and you'll move into the 'Strong' tier."
        
        else:  # Score < 70
            intro = f"🚨 {property_name} needs urgent attention to be competitive. Multiple critical gaps are creating 'guest friction points' that will harm bookings and reviews."
            body = f"Your score of {score}/100 (Grade {grade}: {self.vitality['grade_label']}) shows significant work ahead, but this is fixable. The missing {missing_text} are foundational comfort signals. Once these are in place, design polish can follow."
            cta = "Prioritize the three critical fixes below over the next 30 days. Budget: $300–600."
        
        return f"{intro} {body} {cta}"
    
    def generate_top_three_fixes(self) -> List[Dict]:
        """
        Generate top 3 highest-impact, most-urgent fixes with costs.
        
        Returns: List of {title, description, cost_low, cost_high, impact}
        """
        recommendations = self._generate_recommendations()[:3]  # Top 3 by priority
        
        # Enrich with cost data
        cost_lookup = {
            'bedside_lamps': (60, 150),
            'bedside_tables': (80, 200),
            'entry_hooks': (20, 60),
            'shoe_rack': (30, 80),
            'plunger': (15, 40),
            'shower_hooks': (15, 40),
            'towel_hooks': (15, 40),
            'welcome_basket': (25, 75),
            'bathroom_caddy': (20, 50),
            'desk_chair': (100, 300),
            'sofa_side_tables': (100, 250),
            'power_bars': (25, 60),
        }
        
        fixes = []
        for i, rec in enumerate(recommendations, 1):
            # Extract item from description if possible
            title = rec['title']
            description = rec['description']
            
            # Estimate cost (default range)
            cost_low = 100
            cost_high = 300
            
            # Try to match known items for better cost estimates
            for item, (low, high) in cost_lookup.items():
                if item.replace('_', ' ') in description.lower():
                    cost_low, cost_high = low, high
                    break
            
            fixes.append({
                'priority': i,
                'title': title,
                'description': description,
                'cost_low': cost_low,
                'cost_high': cost_high,
                'impact': rec.get('impact', 'High'),
                'roi': '15-25% booking increase'  # Standard ROI for professional staging
            })
        
        return fixes
    
    def generate_shopping_list(self) -> List[Dict]:
        """
        Generate structured shopping list by budget tier and category.
        
        Returns: List of {category, tier, items: [{name, price, url, why}]}
        """
        # Identify missing items from checklist
        checklist = self.submission.get('guest_comfort_checklist', [])
        all_items = set(VitalityScorer.TIER_1_ITEMS.keys()) | \
                   set(VitalityScorer.TIER_2_ITEMS.keys()) | \
                   set(VitalityScorer.TIER_3_ITEMS.keys())
        missing = list(all_items - set(checklist))
        
        # Amazon affiliate base (to be populated with Rachel's ID)
        # For now, using placeholder URLs
        amazon_base = "https://amazon.com/s?k="
        affiliate_tag = "&tag=roomsbyrachel-20"  # Placeholder
        
        shopping_list = []
        
        # Tier 1: Critical (Value: $20-80)
        if 'bedside_tables' in missing or 'bedside_lamps' in missing:
            shopping_list.append({
                'category': 'Bedroom',
                'tier': 'Value',
                'name': 'Bedside Tables (Set of 2)',
                'price': '$60–$120',
                'link': f"{amazon_base}nightstands+white{affiliate_tag}",
                'description': 'Critical comfort signal. Guests expect a table next to the bed for phone, water, lamp.'
            })
            shopping_list.append({
                'category': 'Bedroom',
                'tier': 'Value',
                'name': 'Bedside Lamps (Set of 2)',
                'price': '$40–$100',
                'link': f"{amazon_base}bedside+lamps+modern{affiliate_tag}",
                'description': 'Functional + psychological comfort. Guests need independent light control.'
            })
        
        if 'plunger' in missing:
            shopping_list.append({
                'category': 'Bathroom',
                'tier': 'Value',
                'name': 'Plunger + Brush Holder',
                'price': '$15–$40',
                'link': f"{amazon_base}toilet+plunger+modern{affiliate_tag}",
                'description': 'Non-negotiable. Guests will be very uncomfortable without this.'
            })
        
        if 'entry_hooks' in missing or 'shoe_rack' in missing:
            shopping_list.append({
                'category': 'Entry',
                'tier': 'Value',
                'name': 'Entry Coat Hooks (3-4 piece)',
                'price': '$20–$60',
                'link': f"{amazon_base}wall+hooks+modern{affiliate_tag}",
                'description': 'First-impression friction killer. Guests need obvious place for jackets/bags.'
            })
            shopping_list.append({
                'category': 'Entry',
                'tier': 'Value',
                'name': 'Slim Shoe Rack',
                'price': '$30–$80',
                'link': f"{amazon_base}shoe+rack+entryway{affiliate_tag}",
                'description': 'Functional necessity. Shows you expect guests to stay, not visit.'
            })
        
        if 'sofa_side_tables' in missing:
            shopping_list.append({
                'category': 'Living Room',
                'tier': 'Signature',
                'name': 'Sofa Side Table (C-shape)',
                'price': '$80–$200',
                'link': f"{amazon_base}c+table+sofa+side{affiliate_tag}",
                'description': 'Functional anchor. Guests need place for drinks, remotes, phones while sitting.'
            })
        
        if 'bathroom_caddy' in missing:
            shopping_list.append({
                'category': 'Bathroom',
                'tier': 'Value',
                'name': 'Shower Caddy / Stool',
                'price': '$20–$50',
                'link': f"{amazon_base}shower+caddy+teak{affiliate_tag}",
                'description': 'Shower utility essential. Guests need shelf for toiletries.'
            })
        
        return shopping_list


def generate_report(submission_data: Dict) -> Dict:
    """
    Complete report generation workflow.
    
    Returns: {
        'html': '<html report>',
        'vitality_data': { score, grade, etc },
        'analysis': 'The Problem narrative',
        'shopping_list': [{category, tier, items}],
        'top_three_fixes': [{priority, title, cost_low, cost_high}],
        'success': True/False
    }
    """
    try:
        logger.info(f"📊 Generating report for submission {submission_data.get('id')}")
        
        # Calculate vitality score
        scorer = VitalityScorer()
        vitality_data = scorer.calculate_vitality_score(
            guest_comfort_checklist=submission_data.get('guest_comfort_checklist', []),
            total_photos=int(submission_data.get('total_photos', 20))
        )
        
        logger.info(f"✅ Vitality score calculated: {vitality_data['vitality_score']}/100 ({vitality_data['grade']})")
        
        # Build complete report
        builder = ReportBuilder(submission_data, vitality_data)
        html_report = builder.build_html_report()
        analysis_text = builder.generate_analysis_text()
        shopping_list = builder.generate_shopping_list()
        top_three_fixes = builder.generate_top_three_fixes()
        
        logger.info(f"✅ HTML report generated ({len(html_report)} bytes)")
        logger.info(f"✅ Analysis text generated ({len(analysis_text)} chars)")
        logger.info(f"✅ Shopping list generated ({len(shopping_list)} items)")
        logger.info(f"✅ Top 3 fixes identified")
        
        return {
            'html': html_report,
            'vitality_data': vitality_data,
            'analysis': analysis_text,
            'shopping_list': shopping_list,
            'top_three_fixes': top_three_fixes,
            'success': True
        }
    
    except Exception as e:
        logger.error(f"❌ Report generation error: {e}")
        return {
            'html': None,
            'vitality_data': None,
            'analysis': '',
            'shopping_list': [],
            'top_three_fixes': [],
            'success': False,
            'error': str(e)
        }
