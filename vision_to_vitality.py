"""
Vision to Vitality — Map Claude Vision analysis to vitality scoring framework

Converts Vision AI design assessment (5 dimensions × 0-20 scale)
into design_score (0-30 scale) per Rachel's weighting.
"""

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


def map_vision_to_design_score(vision_results: Dict) -> Dict:
    """
    Convert PHASE 3 Vision AI analysis to design dimensions (0-20 scale each).
    
    PHASE 3: Claude returns design_scorecard with 0-6 scale per dimension.
    This function converts 0-6 → 0-20 scale for use in 150-point system.
    
    FORMULA: (Claude Score / 6) × 20 = Dimension Score (0-20)
    Example: Claude 5/6 = (5/6) × 20 = 16.67/20
    Perfect Claude score (30/30) = 100/150 points (before Photo and Friction added)
    
    Args:
        vision_results: {
            'design_scorecard': {
                'lighting_quality': 0-6,
                'color_harmony': 0-6,
                'clutter_density': 0-6,
                'staging_integrity': 0-6,
                'functionality': 0-6,
                'total_design_score': 0-30
            },
            'honest_marketing_status': 'High Trust|Medium Trust|Low Trust',
            'top_3_fixes': [...],
            'room_by_room_diagnosis': [...]
        }
    
    Returns:
        {
            'lighting': 0-20,          (Dimension 3)
            'colors': 0-20,            (Name for color_harmony)
            'clutter': 0-20,           (Name for clutter_density)
            'staging': 0-20,           (Dimension for staging_integrity)
            'functionality': 0-20,     (Dimension for functionality)
            'design_score': 0-100,     (Sum for reference, maps to Dimension 1: Bedroom Standards)
            'honest_marketing_status': str,
            'top_3_fixes': list
        }
    """
    
    # Extract design_scorecard (PHASE 3)
    scorecard = vision_results.get('design_scorecard', {})
    
    # Extract 0-6 scores from Claude
    lighting_6 = scorecard.get('lighting_quality', 3)
    colors_6 = scorecard.get('color_harmony', 3)
    clutter_6 = scorecard.get('clutter_density', 3)
    staging_6 = scorecard.get('staging_integrity', 3)
    functionality_6 = scorecard.get('functionality', 3)
    
    # Validate ranges (0-6)
    lighting_6 = max(0, min(6, lighting_6))
    colors_6 = max(0, min(6, colors_6))
    clutter_6 = max(0, min(6, clutter_6))
    staging_6 = max(0, min(6, staging_6))
    functionality_6 = max(0, min(6, functionality_6))
    
    # PHASE 4 MATH CALIBRATION: Convert 0-6 → 0-20 scale
    # Formula: (Score / 6) × 20
    lighting_20 = int((lighting_6 / 6) * 20)
    colors_20 = int((colors_6 / 6) * 20)
    clutter_20 = int((clutter_6 / 6) * 20)
    staging_20 = int((staging_6 / 6) * 20)
    functionality_20 = int((functionality_6 / 6) * 20)
    
    # Perfect Claude score (30/30) verification
    # 6 + 6 + 6 + 6 + 6 = 30 (Claude) → 20 + 20 + 20 + 20 + 20 = 100 (before Photo + Friction)
    perfect_score = lighting_20 + colors_20 + clutter_20 + staging_20 + functionality_20
    
    logger.info(f"📊 PHASE 4: Vision (0-6) → Dimensions (0-20)")
    logger.info(f"   Lighting: {lighting_6}/6 → {lighting_20}/20")
    logger.info(f"   Colors: {colors_6}/6 → {colors_20}/20")
    logger.info(f"   Clutter: {clutter_6}/6 → {clutter_20}/20")
    logger.info(f"   Staging: {staging_6}/6 → {staging_20}/20")
    logger.info(f"   Functionality: {functionality_6}/6 → {functionality_20}/20")
    logger.info(f"   Sum (before Photo+Friction): {perfect_score}/100")
    logger.info(f"   (Perfect Claude 30/30 = 100/150 in 150-point system)")
    
    return {
        'lighting': lighting_20,
        'colors': colors_20,
        'clutter': clutter_20,
        'staging': staging_20,
        'functionality': functionality_20,
        'design_score': perfect_score,  # Sum of 5 dimensions (0-100, before Photo+Friction)
        'honest_marketing_status': vision_results.get('honest_marketing_status', 'Medium Trust'),
        'top_3_fixes': vision_results.get('top_3_fixes', []),
        'room_by_room_diagnosis': vision_results.get('room_by_room_diagnosis', [])
    }


def enhance_recommendations_with_vision(vision_results: Dict, vision_details: Dict) -> List[Dict]:
    """
    Generate design-specific fix recommendations based on Vision AI scores.
    
    Args:
        vision_results: Overall aggregated vision scores
        vision_details: Mapping result with individual dimension scores
    
    Returns:
        List of additional design-focused recommendations
    """
    
    fixes = []
    
    staging = vision_details.get('staging', 10)
    functionality = vision_details.get('functionality', 10)
    colors = vision_details.get('colors', 10)
    lighting = vision_details.get('lighting', 10)
    clutter = vision_details.get('clutter', 10)
    
    # Low lighting recommendations
    if lighting < 8:
        fixes.append({
            'priority': 'High',
            'title': 'Improve Lighting Quality',
            'description': 'Add table lamps with warm bulbs, maximize natural light, avoid harsh shadows',
            'cost_low': 80,
            'cost_high': 400,
            'impact': 'High',
            'roi': '10-15%'
        })
    
    # Poor color harmony
    if colors < 8:
        fixes.append({
            'priority': 'High',
            'title': 'Harmonize Color Palette',
            'description': 'Use cohesive accent colors, neutral walls, remove clashing decor',
            'cost_low': 150,
            'cost_high': 600,
            'impact': 'High',
            'roi': '12-18%'
        })
    
    # Low functionality
    if functionality < 8:
        fixes.append({
            'priority': 'High',
            'title': 'Enhance Functionality',
            'description': 'Add workspace with chair, accessible storage, side tables for guest needs',
            'cost_low': 200,
            'cost_high': 800,
            'impact': 'High',
            'roi': '15-20%'
        })
    
    # Low staging integrity
    if staging < 8:
        fixes.append({
            'priority': 'Critical',
            'title': 'Professional Staging',
            'description': 'Add quality decor, art, throw pillows, fresh flowers, quality textiles',
            'cost_low': 300,
            'cost_high': 1500,
            'impact': 'High',
            'roi': '20-30%'
        })
    
    # High clutter
    if clutter < 8:
        fixes.append({
            'priority': 'Important',
            'title': 'Declutter & Organize',
            'description': 'Remove personal items, organize visible storage, create clean surfaces',
            'cost_low': 0,
            'cost_high': 100,
            'impact': 'Medium',
            'roi': '10-15%'
        })
    
    return fixes


def get_design_narrative(vision_results: Dict, vision_details: Dict) -> str:
    """
    Generate narrative describing the property's design quality.
    
    Integrates Vision AI insights into the "The Problem" analysis.
    """
    
    staging = vision_details.get('staging', 10)
    functionality = vision_details.get('functionality', 10)
    colors = vision_details.get('colors', 10)
    lighting = vision_details.get('lighting', 10)
    clutter = vision_details.get('clutter', 10)
    
    narratives = []
    
    # Staging assessment
    if staging >= 15:
        narratives.append("Your property is professionally staged with attention to detail.")
    elif staging >= 12:
        narratives.append("Your property has good staging foundation but needs refinement.")
    elif staging >= 8:
        narratives.append("Your property shows basic staging but lacks professional polish.")
    else:
        narratives.append("Your property needs significant staging improvements to attract guests.")
    
    # Lighting assessment
    if lighting >= 15:
        narratives.append("Lighting is excellent throughout, creating a warm and inviting atmosphere.")
    elif lighting >= 12:
        narratives.append("Lighting is adequate but could be warmer and more strategically placed.")
    else:
        narratives.append("Lighting needs improvement—add lamps and maximize natural light sources.")
    
    # Functionality assessment
    if functionality >= 15:
        narratives.append("All essential guest amenities are visible and accessible.")
    elif functionality >= 12:
        narratives.append("Most guest needs are met, though some functional gaps exist.")
    else:
        narratives.append("The space lacks clear functional areas for guest work and relaxation.")
    
    # Color harmony
    if colors >= 15:
        narratives.append("Color palette is cohesive and professional throughout.")
    elif colors >= 12:
        narratives.append("Colors are mostly harmonious but could be more intentional.")
    else:
        narratives.append("Color coordination needs work—conflicting tones reduce sophistication.")
    
    return " ".join(narratives)
