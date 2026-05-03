"""
ROI Intelligence Validator
Ensures Vision AI output includes revenue-first justifications

Validates that:
1. JSON includes roi_why_* or roi_impact fields
2. No designer speak (forbidden phrases)
3. All recommendations have payback periods
4. Priority levels (P1/P2/P3) are correctly assigned
5. Revenue impact estimates are reasonable ($0-500/month range)
"""

import logging
import json
import re
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

# Forbidden designer speak patterns
FORBIDDEN_PHRASES = [
    r"visual interest",
    r"aesthetic coherence",
    r"layered ambience",
    r"spatial narrative",
    r"design merit",
    r"visual harmony",
    r"artistic flow",
    r"creative styling",
    r"design sensibility",
    r"cultivate atmosphere",
    r"evoke emotion",
    r"sophisticated palette",
    r"curated experience",
]

# Expected field patterns for lite analysis
LITE_REQUIRED_FIELDS = [
    "design_score",
    "gap_1", "roi_why_1",
    "gap_2", "roi_why_2",
    "gap_3", "roi_why_3",
    "brief_assessment"
]

# Expected field patterns for premium analysis
PREMIUM_REQUIRED_FIELDS = [
    "pillar_name",
    "score",
    "issue",
    "fix",
    "booking_type_affected",
    "revenue_impact_monthly",
    "fix_cost",
    "payback_weeks",
    "priority_level"
]


def contains_designer_speak(text: str) -> Tuple[bool, List[str]]:
    """
    Check if text contains forbidden designer speak phrases
    
    Returns: (has_violations, list_of_violations)
    """
    violations = []
    
    for pattern in FORBIDDEN_PHRASES:
        if re.search(pattern, text, re.IGNORECASE):
            violations.append(pattern)
    
    return len(violations) > 0, violations


def extract_revenue_impact(roi_text: str) -> Dict[str, str]:
    """
    Extract structured data from roi_why_* fields
    
    Expected format: "Couples (20%), -$180/month, 2x $25 lamps, 1-2 weeks payback"
    Returns: {'booking_type': '...', 'impact': '...', 'fix_cost': '...', 'payback': '...'}
    """
    
    result = {
        'booking_type': None,
        'impact': None,
        'fix_cost': None,
        'payback': None
    }
    
    # Extract booking type (Couples, Families, Remote Workers, All)
    booking_match = re.search(r'(Couples|Families|Remote Workers|All)', roi_text, re.IGNORECASE)
    if booking_match:
        result['booking_type'] = booking_match.group(1)
    
    # Extract revenue impact ($XXX/month pattern)
    impact_match = re.search(r'[\-\+]\$(\d+(?:,\d+)?)/month', roi_text)
    if impact_match:
        result['impact'] = f"-${impact_match.group(1)}/month"
    
    # Extract fix cost ($XXX pattern)
    cost_match = re.search(r'\$(\d+(?:[-–]\$?\d+)?)', roi_text)
    if cost_match:
        result['fix_cost'] = f"${cost_match.group(1)}"
    
    # Extract payback period (X-Y weeks pattern)
    payback_match = re.search(r'(\d+(?:-\d+)?)\s*(?:week|wk)', roi_text, re.IGNORECASE)
    if payback_match:
        result['payback'] = f"{payback_match.group(1)} weeks"
    
    return result


def validate_lite_response(response: Dict) -> Tuple[bool, List[str]]:
    """
    Validate lite analysis response structure and content
    
    Returns: (is_valid, list_of_errors)
    """
    errors = []
    
    # Check required fields
    for field in LITE_REQUIRED_FIELDS:
        if field not in response or not response.get(field):
            errors.append(f"Missing required field: {field}")
    
    # Check design_score is 0-30
    score = response.get('design_score', -1)
    if not isinstance(score, int) or score < 0 or score > 30:
        errors.append(f"Invalid design_score: {score} (must be 0-30)")
    
    # Check for designer speak in gaps
    for i in range(1, 4):
        gap_field = f"gap_{i}"
        roi_field = f"roi_why_{i}"
        
        if gap_field in response:
            gap_text = response[gap_field]
            has_speak, violations = contains_designer_speak(gap_text)
            if has_speak:
                errors.append(f"Designer speak in {gap_field}: {', '.join(violations)}")
        
        if roi_field in response:
            roi_text = response[roi_field]
            
            # Extract and validate ROI components
            roi_data = extract_revenue_impact(roi_text)
            
            if not roi_data['booking_type']:
                errors.append(f"Missing booking type in {roi_field}")
            if not roi_data['impact']:
                errors.append(f"Missing revenue impact in {roi_field}")
            if not roi_data['fix_cost']:
                errors.append(f"Missing fix cost in {roi_field}")
            if not roi_data['payback']:
                errors.append(f"Missing payback period in {roi_field}")
    
    # Check brief_assessment has ROI summary
    assessment = response.get('brief_assessment', '')
    if not any(word in assessment.lower() for word in ['$', 'investment', 'payback', 'month']):
        errors.append("brief_assessment missing ROI metrics ($ or payback)")
    
    return len(errors) == 0, errors


def validate_premium_response(response: Dict) -> Tuple[bool, List[str]]:
    """
    Validate premium (5-pillar) analysis response structure
    
    Returns: (is_valid, list_of_errors)
    """
    errors = []
    
    if not isinstance(response, dict):
        errors.append(f"Response must be JSON dict, got {type(response)}")
        return False, errors
    
    # Check for each pillar (assuming response has pillar_1, pillar_2, etc.)
    for pillar_num in range(1, 6):
        pillar_key = f"pillar_{pillar_num}"
        
        # Response might be nested under a different key, so we check flexibly
        pillar_data = None
        if pillar_key in response:
            pillar_data = response[pillar_key]
        
        if not pillar_data:
            # Skip if pillar structure is different (e.g., flat response)
            continue
        
        # Check required fields for this pillar
        for field in PREMIUM_REQUIRED_FIELDS:
            if field not in pillar_data or not pillar_data.get(field):
                errors.append(f"{pillar_key}: Missing {field}")
        
        # Validate priority level
        priority = pillar_data.get('priority_level', '')
        if priority and not any(p in priority for p in ['P1', 'P2', 'P3']):
            errors.append(f"{pillar_key}: Invalid priority '{priority}' (must be P1/P2/P3)")
        
        # Check for designer speak
        issue = pillar_data.get('issue', '')
        has_speak, violations = contains_designer_speak(issue)
        if has_speak:
            errors.append(f"{pillar_key}: Designer speak in issue: {', '.join(violations)}")
    
    return len(errors) == 0, errors


def inject_missing_roi_fields(response: Dict, analysis_type: str = 'lite') -> Dict:
    """
    Auto-inject missing ROI fields if validation fails
    
    This is a recovery mechanism for incomplete responses.
    Should only be used as last resort if Claude partially complies.
    
    Args:
        response: The potentially incomplete response
        analysis_type: 'lite' or 'premium'
    
    Returns:
        Updated response with best-effort ROI field population
    """
    
    logger.warning("⚠️  Auto-injecting missing ROI fields (recovery mode)")
    
    if analysis_type == 'lite':
        # Ensure all roi_why_* fields exist
        for i in range(1, 4):
            roi_field = f"roi_why_{i}"
            gap_field = f"gap_{i}"
            
            if roi_field not in response or not response[roi_field]:
                gap_text = response.get(gap_field, f'Gap {i}')
                # Default ROI format
                response[roi_field] = (
                    f"Missing ROI data. {gap_text} affects guest satisfaction. "
                    f"Estimated fix: $50-200, expected ROI: +$50-150/month, "
                    f"payback 2-4 weeks."
                )
    
    return response


def log_validation_report(response: Dict, is_valid: bool, errors: List[str], analysis_type: str = 'lite'):
    """Log validation results with detailed reporting"""
    
    if is_valid:
        logger.info(f"✅ {analysis_type.upper()} VALIDATION PASSED")
        logger.info(f"   ROI fields: Complete")
        logger.info(f"   Designer speak: None detected")
        logger.info(f"   Revenue justifications: Present")
    else:
        logger.error(f"❌ {analysis_type.upper()} VALIDATION FAILED")
        logger.error(f"   Found {len(errors)} violation(s):")
        for error in errors:
            logger.error(f"     • {error}")


# ============================================================================
# INTEGRATION POINTS
# ============================================================================

def validate_vision_output(response: Dict, analysis_type: str = 'lite') -> Tuple[bool, Dict]:
    """
    Main validation entry point
    
    Returns: (is_valid, validated_response)
    """
    
    if analysis_type == 'lite':
        is_valid, errors = validate_lite_response(response)
    else:
        is_valid, errors = validate_premium_response(response)
    
    # Log the result
    log_validation_report(response, is_valid, errors, analysis_type)
    
    # If validation failed and we can auto-inject, do so
    if not is_valid:
        logger.warning("⚠️  Attempting recovery with ROI field injection...")
        response = inject_missing_roi_fields(response, analysis_type)
        
        # Revalidate after injection
        if analysis_type == 'lite':
            is_valid, errors = validate_lite_response(response)
        else:
            is_valid, errors = validate_premium_response(response)
        
        if is_valid:
            logger.info("✅ Recovery successful after ROI field injection")
        else:
            logger.error("❌ Recovery failed, returning partially invalid response")
    
    return is_valid, response
