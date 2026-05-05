#!/usr/bin/env python3
"""
Premium Analysis Engine - Two-Lane Report Pipeline

Lane A: Free Hook (Vitality Score + Grade + Blurred Placeholders)
Lane B: Premium Engine (8-Page PDF with Five Pillars + Sovereignty Analysis)

This module implements the premium tier logic with proper lane separation.
"""

import json
from typing import Dict, Optional, Literal

# Lane Configuration
REPORT_TIER = Literal["free", "premium"]

# Five Pillars Framework
FIVE_PILLARS = {
    "spatial_flow": {
        "name": "Spatial Flow & Ergonomics",
        "metrics": [
            "60cm_walkway_rule",
            "landing_strip_entry",
            "bilateral_bed_access",
            "kitchen_triangle",
            "floating_furniture_detection"
        ]
    },
    "lighting": {
        "name": "Lighting & Optical Health",
        "metrics": [
            "overhead_only_penalty",
            "task_lighting_layers",
            "accent_lighting",
            "color_temperature",
            "glare_analysis"
        ]
    },
    "sensory_textile": {
        "name": "Sensory & Textile Logic",
        "metrics": [
            "material_quality",
            "tactile_experience",
            "fabric_wear_signals",
            "natural_materials",
            "warmth_perception"
        ]
    },
    "power_connectivity": {
        "name": "Power & Connectivity",
        "metrics": [
            "usb_port_count",
            "outlet_placement",
            "cable_management",
            "wifi_coverage",
            "charging_access"
        ]
    },
    "intentionality": {
        "name": "Intentionality & Soul",
        "metrics": [
            "curated_vs_assembled",
            "host_mindset_signals",
            "monochromatic_failure_flag",
            "clinical_penalty",
            "personal_touches"
        ]
    }
}

# Sovereignty vs Surveillance Framework
class SovereigntyAnalyzer:
    """Analyzes whether guest feels welcomed (sovereignty) or trapped (surveillance)"""
    
    @staticmethod
    def analyze(photo_analysis: Dict) -> Dict:
        """
        Assess sovereignty vs surveillance signals in the property
        
        SOVEREIGNTY SIGNALS (Welcomed):
        - Clear floor space visible in entry
        - Available/empty hooks
        - Clear surfaces
        - Warm lighting visible from entry
        - Path of least resistance clear
        
        SURVEILLANCE SIGNALS (Trapped):
        - Rule signs ("Do Not Touch," "Do Not Sit")
        - Fragile items on low tables
        - Busy patterns dominating
        - Family photos in guest spaces
        - Monochromatic clinical design
        """
        
        sovereignty_score = 0
        surveillance_score = 0
        signals = {
            "sovereignty": [],
            "surveillance": [],
            "assessment": None
        }
        
        # Placeholder for actual photo analysis
        # In production, this would parse Claude's photo descriptions
        
        return {
            "sovereignty_score": sovereignty_score,
            "surveillance_score": surveillance_score,
            "signals": signals,
            "guest_mindset": "welcomed" if sovereignty_score > surveillance_score else "trapped"
        }


class FloatingFurnitureDetector:
    """Detects floating furniture (not wall-anchored) and prevents inappropriate recommendations"""
    
    FLOATING_INDICATORS = [
        "sofa positioned away from wall",
        "bed in center of room",
        "floating island",
        "center-positioned furniture",
        "visible floor around all sides"
    ]
    
    @staticmethod
    def detect(room_description: str) -> Dict:
        """Detect floating furniture and flag wall-based recommendations as inappropriate"""
        
        floating_items = []
        inappropriate_wall_fixes = []
        
        # Placeholder for actual detection
        # In production, Claude would identify floating furniture
        
        return {
            "has_floating_furniture": bool(floating_items),
            "floating_items": floating_items,
            "flag_wall_gallery_wall": True,  # Never recommend gallery walls for floating furniture
            "recommended_approach": "Floor anchors, area rugs, floating shelves only"
        }


class MonochromaticAnalyzer:
    """Flags monochromatic failures as clinical design that kills booking desire"""
    
    MONOCHROMATIC_PATTERNS = [
        "all_black",
        "all_white",
        "all_gray",
        "black_white_gray_combination"
    ]
    
    COST_IMPACT = {
        "clinical_penalty": -5,  # Points deducted from vitality
        "booking_desire_reduction": "20-30%",
        "revenue_impact_per_night": "$15-25",
        "guest_perception": "sterile, institutional, unwelcoming"
    }
    
    @staticmethod
    def analyze(color_analysis: Dict) -> Dict:
        """Detect monochromatic failures and quantify cost"""
        
        return {
            "is_monochromatic": False,  # Placeholder
            "dominant_colors": [],
            "clinical_penalty_points": 0,
            "recommended_warmth_injection": None,
            "cost_impact": MonochromaticAnalyzer.COST_IMPACT
        }


class PremiumReportGenerator:
    """Generates comprehensive 8-page premium analysis"""
    
    def __init__(self, report_tier: REPORT_TIER = "free"):
        self.report_tier = report_tier
        self.enable_five_pillars = (report_tier == "premium")
        self.enable_sovereignty = (report_tier == "premium")
        self.enable_floating_furniture = (report_tier == "premium")
        self.enable_monochromatic = (report_tier == "premium")
    
    def generate_free_hook(self, vitality_data: Dict) -> Dict:
        """
        Lane A: Free Hook - Email Only
        
        Content:
        - Vitality Score (0-100)
        - Grade (A/B/C/D/F)
        - 3 Blurred/Redacted Placeholders (teaser for premium)
        - Hero Fix summary from Rachel Rules v1.0
        """
        
        return {
            "report_type": "free_hook",
            "vitality_score": vitality_data.get("vitality_score", 0),
            "grade": vitality_data.get("grade", "C"),
            "hero_fix_summary": vitality_data.get("hero_fix", {}).get("title", ""),
            "revenue_impact_teaser": vitality_data.get("hero_fix", {}).get("revenue_impact", ""),
            "upgrade_prompt": "📄 Unlock full 8-page Premium Report for detailed room-by-room analysis",
            "blurred_sections": [
                {"section": "Five Pillars Analysis", "status": "locked"},
                {"section": "Sovereignty Assessment", "status": "locked"},
                {"section": "Professional Photography ROI", "status": "locked"}
            ]
        }
    
    def generate_premium_report(self, vitality_data: Dict, photo_analysis: Dict) -> Dict:
        """
        Lane B: Premium Engine - 8-Page PDF
        
        Content:
        1. Executive Summary + Vitality Score
        2. Five Pillars Deep Diagnostic
        3. Sovereignty vs Surveillance Assessment
        4. Room-by-Room Analysis (Pillar breakdown per room)
        5. Floating Furniture Detection & Recommendations
        6. Monochromatic Failure Analysis (if applicable)
        7. Professional Photography ROI Analysis
        8. Tier-Locked Amenity Checklist
        """
        
        if self.report_tier != "premium":
            raise ValueError("Premium report requires report_tier='premium'")
        
        # Initialize analysis layers
        sovereignty = SovereigntyAnalyzer.analyze(photo_analysis)
        floating = FloatingFurnitureDetector.detect(str(photo_analysis))
        monochromatic = MonochromaticAnalyzer.analyze(vitality_data.get("color_data", {}))
        
        # Build full 8-page structure
        premium_report = {
            "report_type": "premium_8_page",
            "vitality_score": vitality_data.get("vitality_score", 0),
            "grade": vitality_data.get("grade", "C"),
            
            # Page 1: Executive Summary
            "executive_summary": {
                "overview": vitality_data.get("hero_fix", {}),
                "key_opportunities": vitality_data.get("staging_and_click", {}),
                "investment_required": vitality_data.get("total_investment", "$0")
            },
            
            # Pages 2-6: Five Pillars Deep Diagnostic
            "five_pillars": {
                "spatial_flow": {
                    "name": FIVE_PILLARS["spatial_flow"]["name"],
                    "analysis": vitality_data.get("spatial_flow", {}),
                    "floating_furniture_detection": floating
                },
                "lighting": {
                    "name": FIVE_PILLARS["lighting"]["name"],
                    "analysis": vitality_data.get("lighting", {}),
                    "premium_note": "Overhead-only lighting = institutional ambiance"
                },
                "sensory_textile": {
                    "name": FIVE_PILLARS["sensory_textile"]["name"],
                    "analysis": vitality_data.get("sensory", {}),
                    "monochromatic_check": monochromatic
                },
                "power_connectivity": {
                    "name": FIVE_PILLARS["power_connectivity"]["name"],
                    "analysis": vitality_data.get("power_connectivity", {})
                },
                "intentionality": {
                    "name": FIVE_PILLARS["intentionality"]["name"],
                    "analysis": vitality_data.get("intentionality", {}),
                    "curated_vs_assembled": vitality_data.get("staging_integrity", {})
                }
            },
            
            # Page 3: Sovereignty vs Surveillance
            "sovereignty_assessment": sovereignty,
            
            # Pages 4-5: Room-by-Room with Pillar Breakdown
            "room_by_room_pillars": vitality_data.get("room_by_room_diagnosis", []),
            
            # Page 6: Floating Furniture Rules
            "floating_furniture_rules": {
                "detected": floating.get("has_floating_furniture", False),
                "items": floating.get("floating_items", []),
                "critical_rule": "Never recommend wall-based fixes (gallery walls, shelving) for floating furniture",
                "recommended_approach": floating.get("recommended_approach", ""),
                "example_conflict": "❌ WRONG: Add gallery wall above floating sofa\n✅ RIGHT: Use floor anchors, area rug, or floating shelves"
            },
            
            # Page 7: Monochromatic Failure Analysis
            "monochromatic_analysis": {
                "is_clinical": monochromatic.get("is_monochromatic", False),
                "technical_cost": monochromatic.get("cost_impact", {}),
                "guest_perception": "Clinical, sterile, institutional — kills booking desire",
                "remedy": "Inject warmth: natural materials, soft textures, warm lighting"
            },
            
            # Page 8: Professional Photography + Tier-Locked Checklist
            "professional_photography_roi": vitality_data.get("professional_imagery_roi", {}),
            "tier_locked_amenities": vitality_data.get("tier_locked_amenities", {})
        }
        
        return premium_report


def analyze_property(
    image_urls: list,
    report_tier: REPORT_TIER = "free"
) -> Dict:
    """
    Main entry point for property analysis with lane routing
    
    Args:
        image_urls: List of property photo URLs
        report_tier: "free" for Lane A (Free Hook), "premium" for Lane B (Full 8-Page)
    
    Returns:
        Either free hook summary or full premium report, based on report_tier
    """
    
    generator = PremiumReportGenerator(report_tier=report_tier)
    
    # In production, this would:
    # 1. Call Claude Vision API with images
    # 2. Receive vitality_data from Rachel Rules v1.0 (Lane A logic)
    # 3. If premium: Expand with Five Pillars + Sovereignty
    # 4. Return appropriate report tier
    
    # Placeholder data structure
    vitality_data = {
        "vitality_score": 0,
        "grade": "C",
        "hero_fix": {},
        "staging_and_click": {},
        "spatial_flow": {},
        "lighting": {},
        "sensory": {},
        "power_connectivity": {},
        "intentionality": {},
        "room_by_room_diagnosis": [],
        "professional_imagery_roi": {},
        "tier_locked_amenities": {}
    }
    
    photo_analysis = {}
    
    # Route to appropriate lane
    if report_tier == "free":
        return generator.generate_free_hook(vitality_data)
    elif report_tier == "premium":
        return generator.generate_premium_report(vitality_data, photo_analysis)
    else:
        raise ValueError(f"Invalid report_tier: {report_tier}. Must be 'free' or 'premium'")


if __name__ == "__main__":
    # Example usage
    print("🔄 Premium Analysis Engine Initialized")
    print("✅ Lane A (Free Hook): Enabled")
    print("✅ Lane B (Premium 8-Page): Enabled")
    print("✅ Five Pillars: Triggers on report_tier='premium'")
    print("✅ Sovereignty Analysis: Triggers on report_tier='premium'")
    print("✅ Floating Furniture Detection: Triggers on report_tier='premium'")
    print("✅ Monochromatic Analyzer: Triggers on report_tier='premium'")
