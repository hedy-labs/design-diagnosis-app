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
    Convert Vision AI analysis to design_score for vitality calculation.
    
    Weighting (per Rachel):
    - Staging Integrity: 40% (most critical for guest perception)
    - Functionality: 30% (guest needs)
    - Color Harmony: 15% (professional look)
    - Lighting Quality: 10% (atmosphere)
    - Clutter Density: 5% (detail polish)
    
    Args:
        vision_results: {
            'lighting_quality': 0-20,
            'color_harmony': 0-20,
            'clutter_density': 0-20,
            'staging_integrity': 0-20,
            'functionality': 0-20,
            ...
        }
    
    Returns:
        {
            'design_score': 0-30,
            'lighting': 0-20,
            'colors': 0-20,
            'clutter': 0-20,
            'staging': 0-20,
            'functionality': 0-20
        }
    """
    
    # Extract scores (0-20 scale)
    staging = vision_results.get('staging_integrity', 10)
    functionality = vision_results.get('functionality', 10)
    colors = vision_results.get('color_harmony', 10)
    lighting = vision_results.get('lighting_quality', 10)
    clutter = vision_results.get('clutter_density', 10)
    
    # Validate ranges
    staging = max(0, min(20, staging))
    functionality = max(0, min(20, functionality))
    colors = max(0, min(20, colors))
    lighting = max(0, min(20, lighting))
    clutter = max(0, min(20, clutter))
    
    # Convert 0-20 scale to 0-100 percentage
    staging_pct = (staging / 20) * 100
    functionality_pct = (functionality / 20) * 100
    colors_pct = (colors / 20) * 100
    lighting_pct = (lighting / 20) * 100
    clutter_pct = (clutter / 20) * 100
    
    # Weighted average (0-100)
    design_pct = (
        staging_pct * 0.40 +
        functionality_pct * 0.30 +
        colors_pct * 0.15 +
        lighting_pct * 0.10 +
        clutter_pct * 0.05
    )
    
    # Convert 0-100 to 0-30 scale (design_score for vitality)
    design_score = int((design_pct / 100) * 30)
    design_score = max(0, min(30, design_score))  # Clamp to 0-30
    
    logger.info(f"📊 Vision → Design Score: {design_pct:.1f}% = {design_score}/30")
    logger.info(f"   Staging: {staging}/20 (40%) | Functionality: {functionality}/20 (30%) | Colors: {colors}/20 (15%) | Lighting: {lighting}/20 (10%) | Clutter: {clutter}/20 (5%)")
    
    return {
        'design_score': design_score,
        'lighting': lighting,
        'colors': colors,
        'clutter': clutter,
        'staging': staging,
        'functionality': functionality
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
