"""
Design Diagnosis — 5-Layer Scoring System

Integrates Rachel's refinement feedback:
1. Utility Completeness — Can guest actually USE the property?
2. Quantity-Duration Matching — Does supply scale with stay length?
3. Asymmetry Detection — Are pairs equitable for N guests?
4. Safety Layer — Health/safety risks independent of aesthetics?
5. Host Personality — Thoughtfulness signals (coasters, felt pads, etc)?

Purpose: Transform "beautiful" scoring to "functional" scoring.
"""

from dataclasses import dataclass
from typing import Dict, Optional, List
from enum import Enum


class StayLength(str, Enum):
    SHORT = "short"    # 1–5 days
    MEDIUM = "medium"  # 6–14 days
    LONG = "long"      # 15+ days (monthly)


@dataclass
class PropertyData:
    """Input data for layer scoring"""
    # Metadata
    guest_count: int = 2
    stay_length_days: int = 7
    property_type: str = "apartment"
    
    # Kitchen inventory
    pans_count: int = 0
    pan_damaged: bool = False
    plates_count: int = 0
    bowls_count: int = 0
    mugs_count: int = 0
    knives_count: int = 0
    cutting_boards_count: int = 0
    has_oil: bool = False
    has_salt: bool = False
    has_sugar: bool = False
    has_paper_towels: bool = False
    has_drying_rack: bool = False
    has_microwave: bool = False
    has_water_filter: bool = False
    
    # Bedroom inventory (per bedroom, use list if multi-bedroom)
    hangers_count: int = 0
    bedside_lamps_count: int = 0
    end_tables_count: int = 0
    dresser_present: bool = False
    hamper_present: bool = False
    
    # Bathroom inventory
    bath_mats_count: int = 0
    has_hooks: bool = False
    has_storage: bool = False
    has_plunger: bool = False
    
    # Living/Dining
    has_coasters: bool = False
    has_placemats: bool = False
    has_felt_pads: bool = False
    
    # Safety
    structural_issues: List[str] = None
    slip_hazards: int = 0


# ============================================================================
# LAYER 1: UTILITY COMPLETENESS
# ============================================================================

class UtilityScorer:
    """Score functional completeness of property zones"""
    
    MAX_KITCHEN_UTILITY = 15.0
    MAX_BEDROOM_UTILITY = 15.0
    MAX_BATHROOM_UTILITY = 10.0
    
    @staticmethod
    def score_kitchen_utility(data: PropertyData) -> float:
        """Score kitchen functionality (0–15 points)"""
        score = 0.0
        
        # COOKWARE (critical)
        if data.pans_count >= 2 and not data.pan_damaged:
            score += 1.0
        else:
            score -= 2.0  # critical penalty
        
        # PREP TOOLS (critical)
        if data.knives_count >= 2 and data.cutting_boards_count >= 1:
            score += 1.0
        else:
            score -= 1.5
        
        # DISHWARE (scale by guests)
        min_dishware = data.guest_count + 1
        if data.plates_count >= min_dishware and data.bowls_count >= min_dishware:
            score += 1.0
        else:
            score -= 1.0
        
        # PANTRY STAPLES (critical)
        pantry_items = sum([data.has_oil, data.has_salt, data.has_sugar])
        if pantry_items >= 3:
            score += 1.5
        else:
            score -= 1.5  # critical penalty
        
        # CLEANING (critical)
        if data.has_paper_towels and data.has_drying_rack:
            score += 1.5
        else:
            score -= 1.0
        
        # APPLIANCES (flexibility)
        if data.has_microwave:
            score += 0.5
        if data.has_water_filter:
            score += 0.5
        
        # Clamp to valid range
        score = max(0.0, min(UtilityScorer.MAX_KITCHEN_UTILITY, score))
        return score
    
    @staticmethod
    def score_bedroom_utility(data: PropertyData) -> float:
        """Score bedroom functionality (0–15 points)"""
        score = 0.0
        
        # LIGHTING (critical for 2+ guests)
        if data.guest_count > 1:
            if data.bedside_lamps_count >= data.guest_count:
                score += 2.0
            else:
                score -= 2.0  # asymmetry penalty
        else:
            if data.bedside_lamps_count >= 1:
                score += 1.0
            else:
                score -= 1.0
        
        # END TABLES (critical for 2+ guests)
        if data.guest_count > 1:
            if data.end_tables_count >= data.guest_count:
                score += 2.0
            else:
                score -= 1.5  # asymmetry penalty
        else:
            if data.end_tables_count >= 1:
                score += 1.0
            else:
                score -= 1.0
        
        # HANGERS (scale by duration — see Layer 2)
        if data.hangers_count >= 10:
            score += 2.0
        elif data.hangers_count >= 5:
            score += 0.5
        else:
            score -= 1.0
        
        # STORAGE
        if data.dresser_present and data.hamper_present:
            score += 2.0
        elif data.dresser_present or data.hamper_present:
            score += 1.0
        else:
            score -= 1.0
        
        # Clamp to valid range
        score = max(0.0, min(UtilityScorer.MAX_BEDROOM_UTILITY, score))
        return score
    
    @staticmethod
    def score_bathroom_utility(data: PropertyData) -> float:
        """Score bathroom functionality (0–10 points)"""
        score = 0.0
        
        # SAFETY (slip hazards — critical)
        if data.bath_mats_count >= 2:
            score += 2.0
        elif data.bath_mats_count == 1:
            score += 1.0
        else:
            score -= 2.0  # critical safety penalty
        
        # HOOKS & STORAGE
        if data.has_hooks and data.has_storage:
            score += 2.0
        elif data.has_hooks or data.has_storage:
            score += 1.0
        else:
            score -= 1.0
        
        # ESSENTIALS
        if data.has_plunger:
            score += 1.0
        else:
            score -= 1.0
        
        # Clamp to valid range
        score = max(0.0, min(UtilityScorer.MAX_BATHROOM_UTILITY, score))
        return score


# ============================================================================
# LAYER 2: QUANTITY-TO-DURATION MATCHING
# ============================================================================

class DurationScorer:
    """Score quantity requirements against stay duration"""
    
    @staticmethod
    def get_stay_category(days: int) -> StayLength:
        """Categorize stay by duration"""
        if days <= 5:
            return StayLength.SHORT
        elif days <= 14:
            return StayLength.MEDIUM
        else:
            return StayLength.LONG
    
    @staticmethod
    def get_hanger_requirement(days: int) -> int:
        """Get minimum hangers needed based on stay duration"""
        category = DurationScorer.get_stay_category(days)
        if category == StayLength.SHORT:
            return 5
        elif category == StayLength.MEDIUM:
            return 10
        else:  # LONG
            return 15
    
    @staticmethod
    def score_hangers(hangers: int, stay_days: int) -> float:
        """Score hangers against stay duration (-2 to +1)"""
        requirement = DurationScorer.get_hanger_requirement(stay_days)
        
        if hangers >= requirement:
            return 1.0
        elif hangers >= requirement * 0.5:
            return 0.0
        else:
            return -2.0  # critical for long stays
    
    @staticmethod
    def score_dishware(count: int, guest_count: int, stay_days: int) -> float:
        """Score dishware quantity against stay duration"""
        category = DurationScorer.get_stay_category(stay_days)
        
        if category == StayLength.SHORT:
            needed = guest_count + 1
        elif category == StayLength.MEDIUM:
            needed = (guest_count * 2) + 1
        else:  # LONG
            needed = (guest_count * 3) + 2
        
        if count >= needed:
            return 0.5
        elif count >= needed * 0.5:
            return 0.0
        else:
            return -1.0
    
    @staticmethod
    def score_cookware(pan_count: int, stay_days: int) -> float:
        """Score cookware quantity against stay duration"""
        category = DurationScorer.get_stay_category(stay_days)
        
        if category == StayLength.SHORT:
            needed = 1
        elif category == StayLength.MEDIUM:
            needed = 2
        else:  # LONG
            needed = 3
        
        if pan_count >= needed:
            return 0.5
        elif pan_count >= needed * 0.5:
            return 0.0
        else:
            return -1.0


# ============================================================================
# LAYER 3: ASYMMETRY DETECTION
# ============================================================================

class AsymmetryDetector:
    """Detect and penalize inequitable designs for N guests"""
    
    @staticmethod
    def check_bedroom_asymmetry(data: PropertyData) -> float:
        """Flag mismatched pairs (1 lamp + N guests) (-4 to 0)"""
        penalties = 0.0
        
        if data.guest_count <= 1:
            return 0.0
        
        # Lamps (each guest should have reading light)
        if data.bedside_lamps_count < data.guest_count:
            penalties += 2.0
        
        # End tables (each guest should have surface)
        if data.end_tables_count < data.guest_count:
            penalties += 1.5
        
        # Power bars (for charging devices)
        # Assumes at least 1 per bedroom (not per guest)
        
        return -penalties
    
    @staticmethod
    def check_bathroom_asymmetry(data: PropertyData) -> float:
        """Flag mismatched storage/hooks for N guests (-2 to 0)"""
        penalties = 0.0
        
        if data.guest_count <= 1:
            return 0.0
        
        # Mats (shared, but minimum 2 for shared bathroom)
        if data.bath_mats_count < 2:
            penalties += 1.0
        
        # Hooks (ideally 1 per guest)
        if not data.has_hooks:
            penalties += 0.5
        
        return -penalties
    
    @staticmethod
    def check_living_asymmetry(data: PropertyData) -> float:
        """Flag inequitable living/dining setup (-2 to 0)"""
        # This would check if there's enough seating for all guests
        # In MVP, just return 0; can be extended later
        return 0.0


# ============================================================================
# LAYER 4: SAFETY LAYER
# ============================================================================

class SafetyScorer:
    """Flag health/safety risks independent of aesthetics"""
    
    @staticmethod
    def score_safety_hazards(data: PropertyData) -> float:
        """Calculate safety penalties (-4 to 0)"""
        penalties = 0.0
        
        # SLIP HAZARDS (critical)
        if data.slip_hazards > 0:
            penalties += min(2.0, data.slip_hazards * 1.0)
        
        # Structural issues
        if data.structural_issues:
            for issue in data.structural_issues:
                if issue == "damaged_cookware":  # PTFE fumes
                    penalties += 2.0
                elif issue == "mold_risk":
                    penalties += 2.0
                elif issue == "broken_glass":
                    penalties += 2.0
                else:
                    penalties += 1.0
        
        return -penalties


# ============================================================================
# LAYER 5: HOST PERSONALITY SIGNALS
# ============================================================================

class PersonalityScorer:
    """Score thoughtfulness and hospitality signals (0 to +4 bonus)"""
    
    @staticmethod
    def score_host_signals(data: PropertyData) -> float:
        """Calculate thoughtfulness bonus (0 to +4)"""
        bonus = 0.0
        
        # NOISE CONTROL (acoustic comfort)
        if data.has_felt_pads:
            bonus += 0.5
        
        # SURFACE PROTECTION (care for property)
        if data.has_coasters:
            bonus += 0.5
        if data.has_placemats:
            bonus += 0.5
        
        # Total bonus (capped at 3–4)
        bonus = min(3.0, bonus)
        
        return bonus


# ============================================================================
# INTEGRATED HIDDEN FRICTION SCORER
# ============================================================================

class IntegratedHiddenFrictionScorer:
    """Calculate Dimension 7 using all 5 layers"""
    
    @staticmethod
    def score_hidden_friction(data: PropertyData) -> float:
        """
        Calculate hidden friction score (0–20) from all 5 layers.
        
        Returns:
        - Base score (0–20) from utility + duration + asymmetry + safety
        - Bonus points (0–3) for host personality
        """
        
        # LAYER 1: Utility Completeness (0–8 points)
        kitchen_util = UtilityScorer.score_kitchen_utility(data)
        bedroom_util = UtilityScorer.score_bedroom_utility(data)
        bathroom_util = UtilityScorer.score_bathroom_utility(data)
        
        # Scale individual scores to combined total
        utility_score = (
            (kitchen_util / UtilityScorer.MAX_KITCHEN_UTILITY) * 5 +
            (bedroom_util / UtilityScorer.MAX_BEDROOM_UTILITY) * 2 +
            (bathroom_util / UtilityScorer.MAX_BATHROOM_UTILITY) * 1
        )
        
        # LAYER 2: Duration Matching (−3 to 0)
        duration_penalty = DurationScorer.score_hangers(data.hangers_count, data.stay_length_days)
        
        # LAYER 3: Asymmetry Detection (−4 to 0)
        asymmetry_penalty = (
            AsymmetryDetector.check_bedroom_asymmetry(data) +
            AsymmetryDetector.check_bathroom_asymmetry(data) +
            AsymmetryDetector.check_living_asymmetry(data)
        )
        
        # LAYER 4: Safety Hazards (−4 to 0)
        safety_penalty = SafetyScorer.score_safety_hazards(data)
        
        # LAYER 5: Host Personality Bonus (0 to +3)
        personality_bonus = PersonalityScorer.score_host_signals(data)
        
        # Calculate final score
        score = utility_score + duration_penalty + asymmetry_penalty + safety_penalty + personality_bonus
        
        # Clamp to 0–20
        score = max(0.0, min(20.0, score))
        
        return score


# ============================================================================
# TEST CASE: RACHEL'S TRION @ KL
# ============================================================================

if __name__ == "__main__":
    print("=== Design Diagnosis — 5-Layer Scoring Test ===\n")
    
    # Rachel's Trion @ KL property
    rachel_property = PropertyData(
        guest_count=2,
        stay_length_days=28,  # Monthly rental
        
        # Kitchen (broken)
        pans_count=1,
        pan_damaged=True,  # PTFE coating damaged
        plates_count=2,
        bowls_count=2,
        mugs_count=2,
        knives_count=1,
        cutting_boards_count=1,
        has_oil=False,
        has_salt=False,
        has_sugar=False,
        has_paper_towels=False,
        has_drying_rack=False,
        has_microwave=False,
        has_water_filter=False,
        
        # Bedroom (asymmetrical)
        hangers_count=3,  # 3 for 28-day = insufficient
        bedside_lamps_count=1,  # 1 lamp for 2 guests
        end_tables_count=1,  # 1 table for 2 guests
        dresser_present=False,
        hamper_present=False,
        
        # Bathroom (missing safety)
        bath_mats_count=0,  # slip hazard
        has_hooks=False,
        has_storage=False,
        has_plunger=True,
        
        # Living/Dining (no protection)
        has_coasters=False,
        has_placemats=False,
        has_felt_pads=False,
        
        # Safety
        structural_issues=["damaged_cookware"],
        slip_hazards=1,
    )
    
    # Score using integrated system
    hf_score = IntegratedHiddenFrictionScorer.score_hidden_friction(rachel_property)
    
    print(f"Rachel's Trion @ KL — 5-Layer Hidden Friction Scoring")
    print(f"Stay duration: 28 days (LONG stay)")
    print(f"Guest count: 2\n")
    
    # Layer breakdown
    print("LAYER 1: Utility Completeness")
    kitchen = UtilityScorer.score_kitchen_utility(rachel_property)
    bedroom = UtilityScorer.score_bedroom_utility(rachel_property)
    bathroom = UtilityScorer.score_bathroom_utility(rachel_property)
    print(f"  Kitchen: {kitchen:.1f}/15 (broken cookware, no staples)")
    print(f"  Bedroom: {bedroom:.1f}/15 (asymmetrical for 2 guests)")
    print(f"  Bathroom: {bathroom:.1f}/10 (no mats, no hooks)\n")
    
    print("LAYER 2: Duration Matching")
    hanger_score = DurationScorer.score_hangers(rachel_property.hangers_count, rachel_property.stay_length_days)
    print(f"  Hangers: {hanger_score:.1f} (3 for 28-day = critical fail)\n")
    
    print("LAYER 3: Asymmetry Detection")
    bedroom_asym = AsymmetryDetector.check_bedroom_asymmetry(rachel_property)
    bathroom_asym = AsymmetryDetector.check_bathroom_asymmetry(rachel_property)
    print(f"  Bedroom: {bedroom_asym:.1f} (1 lamp + 2 guests = no equity)")
    print(f"  Bathroom: {bathroom_asym:.1f} (no mats for shared space)\n")
    
    print("LAYER 4: Safety Hazards")
    safety = SafetyScorer.score_safety_hazards(rachel_property)
    print(f"  Safety: {safety:.1f} (damaged cookware + slip hazard)\n")
    
    print("LAYER 5: Host Personality")
    personality = PersonalityScorer.score_host_signals(rachel_property)
    print(f"  Personality: +{personality:.1f} (no coasters, no felt pads)\n")
    
    print(f"FINAL HIDDEN FRICTION SCORE: {hf_score:.1f}/20")
    print(f"Grade: {'F' if hf_score < 10 else 'D' if hf_score < 14 else 'C'}")
    print(f"\nInterpretation: Property is beautiful in photos but dysfunctional for living.")
