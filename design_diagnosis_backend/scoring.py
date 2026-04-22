"""
Design Diagnosis Scoring Engine

Calculates Vitality Score (0–100) across 7 dimensions:
- Dimensions 1–5: 20 points each (standard design criteria)
- Dimension 6: 10 points (photo strategy)
- Dimension 7: 20 points (hidden friction)
Total: 150 points → scaled to 0–100
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple
from enum import Enum


class Grade(str, Enum):
    A = "A"  # 90–100
    B = "B"  # 80–89
    C = "C"  # 70–79
    D = "D"  # 60–69
    F = "F"  # 0–59


@dataclass
class ScoringInput:
    """Input data for scoring all 7 dimensions"""
    # Property metadata
    property_id: int
    property_name: str = ""
    bedrooms: int = 0
    bathrooms: int = 0
    guest_capacity: int = 0
    
    # Dimension 1–5 scores (0–20 each, provided by analysis)
    bedroom_standards_score: float = 0.0
    functionality_flow_score: float = 0.0
    light_brightness_score: float = 0.0
    storage_organization_score: float = 0.0
    condition_maintenance_score: float = 0.0
    
    # Dimension 6: Photo strategy
    photo_count: int = 0
    photo_consistency_issues: int = 0
    photo_quality_score: float = 0.0  # 0–10
    
    # Dimension 7: Hidden friction checklist
    hidden_friction_items_missing: List[str] = None
    hidden_friction_score: float = 0.0  # pre-calculated from checklist


@dataclass
class ScoringResult:
    """Complete scoring result"""
    property_id: int
    
    # Individual dimension scores
    dimension_1_bedroom: float  # 0–20
    dimension_2_flow: float  # 0–20
    dimension_3_light: float  # 0–20
    dimension_4_storage: float  # 0–20
    dimension_5_condition: float  # 0–20
    dimension_6_photo: float  # 0–10
    dimension_7_friction: float  # 0–20
    
    # Composite
    total_points: float  # sum of all dimensions (0–150)
    vitality_score: float  # (total_points / 150) * 100
    grade: str  # A, B, C, D, F
    
    # Breakdown for reporting
    dimension_scores: Dict[int, float]  # {1: 18.5, 2: 15, ...}


class ScoringEngine:
    """Core scoring logic for Design Diagnosis"""
    
    # Point systems per dimension
    DIMENSION_POINTS = {
        1: 20,  # Bedroom standards
        2: 20,  # Functionality & flow
        3: 20,  # Light & brightness
        4: 20,  # Storage & organization
        5: 20,  # Condition & maintenance
        6: 10,  # Photo strategy
        7: 20,  # Hidden friction
    }
    
    TOTAL_POINTS = 150
    
    @staticmethod
    def assign_grade(vitality_score: float) -> str:
        """Assign letter grade based on vitality score (0–100)"""
        if vitality_score >= 90:
            return Grade.A.value
        elif vitality_score >= 80:
            return Grade.B.value
        elif vitality_score >= 70:
            return Grade.C.value
        elif vitality_score >= 60:
            return Grade.D.value
        else:
            return Grade.F.value
    
    @staticmethod
    def calculate_vitality_score(
        dim1: float, dim2: float, dim3: float, dim4: float, dim5: float,
        dim6: float, dim7: float
    ) -> Tuple[float, float, str]:
        """
        Calculate vitality score from 7 dimensions.
        
        Returns: (vitality_score, total_points, grade)
        """
        # Clamp all dimensions to valid ranges
        dim1 = max(0, min(20, dim1))
        dim2 = max(0, min(20, dim2))
        dim3 = max(0, min(20, dim3))
        dim4 = max(0, min(20, dim4))
        dim5 = max(0, min(20, dim5))
        dim6 = max(0, min(10, dim6))
        dim7 = max(0, min(20, dim7))
        
        # Sum all dimensions
        total_points = dim1 + dim2 + dim3 + dim4 + dim5 + dim6 + dim7
        
        # Scale to 0–100
        vitality_score = (total_points / ScoringEngine.TOTAL_POINTS) * 100
        
        # Assign grade
        grade = ScoringEngine.assign_grade(vitality_score)
        
        return vitality_score, total_points, grade
    
    @staticmethod
    def score_from_input(input_data: ScoringInput) -> ScoringResult:
        """
        Score property from input data.
        
        Assumes dimensions 1–5 and 7 are pre-calculated.
        Dimension 6 (photo) calculated here if needed.
        """
        # Use provided scores
        dim1 = input_data.bedroom_standards_score
        dim2 = input_data.functionality_flow_score
        dim3 = input_data.light_brightness_score
        dim4 = input_data.storage_organization_score
        dim5 = input_data.condition_maintenance_score
        dim6 = input_data.photo_quality_score  # 0–10
        dim7 = input_data.hidden_friction_score
        
        # Calculate vitality score
        vitality_score, total_points, grade = ScoringEngine.calculate_vitality_score(
            dim1, dim2, dim3, dim4, dim5, dim6, dim7
        )
        
        # Build result
        result = ScoringResult(
            property_id=input_data.property_id,
            dimension_1_bedroom=dim1,
            dimension_2_flow=dim2,
            dimension_3_light=dim3,
            dimension_4_storage=dim4,
            dimension_5_condition=dim5,
            dimension_6_photo=dim6,
            dimension_7_friction=dim7,
            total_points=total_points,
            vitality_score=vitality_score,
            grade=grade,
            dimension_scores={
                1: dim1, 2: dim2, 3: dim3, 4: dim4, 5: dim5, 6: dim6, 7: dim7
            }
        )
        
        return result


# ============================================================================
# DIMENSION 6: PHOTO STRATEGY SCORING
# ============================================================================

class PhotoStrategyScorer:
    """Scores Dimension 6: Photo Strategy (0–10 points)"""
    
    @staticmethod
    def score_photos(
        photo_count: int,
        consistency_issues: int,
        quality_score: float
    ) -> float:
        """
        Score photo strategy.
        
        Parameters:
        - photo_count: Total number of photos
        - consistency_issues: Number of detected inconsistencies (e.g., same room different furniture)
        - quality_score: Overall photo quality (0–10)
        
        Returns: Photo strategy score (0–10)
        """
        score = 0.0
        
        # PHOTO COUNT (0–3 points)
        if photo_count == 0:
            count_score = 0
        elif photo_count <= 30:
            count_score = 3  # Ideal range
        elif photo_count <= 50:
            count_score = 2  # Acceptable
        elif photo_count <= 70:
            count_score = 1  # Slightly excessive
        else:
            count_score = 0  # Too many photos (>70)
        
        # CONSISTENCY (0–4 points)
        if consistency_issues == 0:
            consistency_score = 4  # All photos consistent
        elif consistency_issues == 1:
            consistency_score = 2  # Minor variants
        elif consistency_issues <= 2:
            consistency_score = 1  # Some variants
        else:
            consistency_score = 0  # Major inconsistencies
        
        # QUALITY (0–3 points)
        # Assuming quality_score is 0–10, map to 0–3
        quality_score = max(0, min(10, quality_score))
        quality_points = (quality_score / 10) * 3
        
        # TOTAL (clamped to 0–10)
        score = count_score + consistency_score + quality_points
        score = max(0, min(10, score))
        
        return score


# ============================================================================
# DIMENSION 7: HIDDEN FRICTION SCORING
# ============================================================================

class HiddenFrictionScorer:
    """Scores Dimension 7: Hidden Friction (0–20 points)"""
    
    # Severity-based deductions
    SEVERITY_DEDUCTIONS = {
        "critical": 2.0,   # e.g., no plunger, no power bar
        "high": 1.5,       # e.g., no nightstands, no lamps
        "medium": 1.0,     # e.g., no desk lamp, no dishcloths
        "low": 0.5,        # e.g., no coasters, no felt pads
    }
    
    @staticmethod
    def calculate_score(
        missing_items: List[Tuple[str, str]]  # [(item_name, severity), ...]
    ) -> float:
        """
        Calculate hidden friction score.
        
        Parameters:
        - missing_items: List of (item_name, severity) tuples
        
        Returns: Hidden friction score (0–20)
        """
        deductions = 0.0
        
        for item_name, severity in missing_items:
            deduction = HiddenFrictionScorer.SEVERITY_DEDUCTIONS.get(severity, 1.0)
            deductions += deduction
        
        # Start with 20 points, subtract deductions
        score = 20.0 - deductions
        
        # Clamp to 0–20
        score = max(0, min(20, score))
        
        return score


# ============================================================================
# TEST HARNESS
# ============================================================================

if __name__ == "__main__":
    # Example: Test property with mixed scores
    print("=== Design Diagnosis Scoring Engine Test ===\n")
    
    # Test 1: High-quality property (should score ~85/100)
    test_input_1 = ScoringInput(
        property_id=1,
        property_name="Premium Listing",
        bedrooms=2,
        bathrooms=1,
        guest_capacity=4,
        bedroom_standards_score=18,
        functionality_flow_score=19,
        light_brightness_score=18,
        storage_organization_score=17,
        condition_maintenance_score=19,
        photo_count=25,
        photo_consistency_issues=0,
        photo_quality_score=9.0,
        hidden_friction_items_missing=[],
        hidden_friction_score=20.0
    )
    
    result_1 = ScoringEngine.score_from_input(test_input_1)
    print(f"Test 1: {test_input_1.property_name}")
    print(f"  Vitality Score: {result_1.vitality_score:.1f}/100")
    print(f"  Grade: {result_1.grade}")
    print(f"  Total Points: {result_1.total_points}/150")
    print(f"  Breakdown: D1={result_1.dimension_1_bedroom}, D2={result_1.dimension_2_flow}, "
          f"D3={result_1.dimension_3_light}, D4={result_1.dimension_4_storage}, "
          f"D5={result_1.dimension_5_condition}, D6={result_1.dimension_6_photo}, "
          f"D7={result_1.dimension_7_friction}\n")
    
    # Test 2: Rachel's expected Airbnb (~59/100, F grade)
    test_input_2 = ScoringInput(
        property_id=2,
        property_name="Rachel's Trion @ KL",
        bedrooms=2,
        bathrooms=1,
        guest_capacity=4,
        bedroom_standards_score=14,  # Missing hangers, some missing items
        functionality_flow_score=15,  # Decent layout
        light_brightness_score=16,   # Good natural light
        storage_organization_score=12,  # Limited storage
        condition_maintenance_score=14,  # Well-maintained but sparse
        photo_count=32,
        photo_consistency_issues=2,   # Some staging inconsistencies
        photo_quality_score=7.5,      # Good quality
        hidden_friction_items_missing=["hangers", "dryer", "drying_rack"],
        hidden_friction_score=6.0  # Many missing items
    )
    
    result_2 = ScoringEngine.score_from_input(test_input_2)
    print(f"Test 2: {test_input_2.property_name}")
    print(f"  Vitality Score: {result_2.vitality_score:.1f}/100")
    print(f"  Grade: {result_2.grade}")
    print(f"  Total Points: {result_2.total_points}/150")
    print(f"  Breakdown: D1={result_2.dimension_1_bedroom}, D2={result_2.dimension_2_flow}, "
          f"D3={result_2.dimension_3_light}, D4={result_2.dimension_4_storage}, "
          f"D5={result_2.dimension_5_condition}, D6={result_2.dimension_6_photo}, "
          f"D7={result_2.dimension_7_friction}\n")
    
    # Test 3: Low-quality property (empty box, should score ~65/100)
    test_input_3 = ScoringInput(
        property_id=3,
        property_name="Empty Box",
        bedrooms=1,
        bathrooms=1,
        guest_capacity=2,
        bedroom_standards_score=10,  # Bare essentials only
        functionality_flow_score=12,  # Basic layout
        light_brightness_score=10,   # Minimal lighting
        storage_organization_score=8,  # Very limited
        condition_maintenance_score=10,  # Clean but sparse
        photo_count=15,
        photo_consistency_issues=0,
        photo_quality_score=5.0,      # Basic quality
        hidden_friction_items_missing=["many items"],
        hidden_friction_score=10.0  # Some missing items
    )
    
    result_3 = ScoringEngine.score_from_input(test_input_3)
    print(f"Test 3: {test_input_3.property_name}")
    print(f"  Vitality Score: {result_3.vitality_score:.1f}/100")
    print(f"  Grade: {result_3.grade}")
    print(f"  Total Points: {result_3.total_points}/150")
    print(f"  Breakdown: D1={result_3.dimension_1_bedroom}, D2={result_3.dimension_2_flow}, "
          f"D3={result_3.dimension_3_light}, D4={result_3.dimension_4_storage}, "
          f"D5={result_3.dimension_5_condition}, D6={result_3.dimension_6_photo}, "
          f"D7={result_3.dimension_7_friction}\n")
    
    print("✅ Scoring engine test complete")
