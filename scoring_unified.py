"""
Unified Scoring System — 150-Point Framework

ARCHITECTURE:
- 87 Rules (Rachel's expert knowledge)
- 5 Pillars (Diagnostic framework)
- 7 Dimensions (Scoring categories, 150 points total)
- Vitality Score (0–100: final percentage)

FORMULA:
vitality_score = (total_points / 150) * 100

Where total_points = sum of all 7 dimensions:
1. Bedroom Standards (20 pts)
2. Functionality & Flow (20 pts)
3. Light & Brightness (20 pts)
4. Storage & Organization (20 pts)
5. Condition & Maintenance (20 pts)
6. Photo Strategy (10 pts)
7. Hidden Friction (20 pts)
= 150 total points
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class DimensionScores:
    """All 7 dimension scores"""
    bedroom_standards: float = 0.0  # 0–20
    functionality_flow: float = 0.0  # 0–20
    light_brightness: float = 0.0  # 0–20
    storage_organization: float = 0.0  # 0–20
    condition_maintenance: float = 0.0  # 0–20
    photo_strategy: float = 0.0  # 0–10
    hidden_friction: float = 0.0  # 0–20
    
    def total_points(self) -> float:
        """Sum all dimensions (should be 0–150)"""
        return (self.bedroom_standards + self.functionality_flow + 
                self.light_brightness + self.storage_organization + 
                self.condition_maintenance + self.photo_strategy + 
                self.hidden_friction)
    
    def to_vitality_score(self) -> float:
        """Convert 150-point sum to 0–100 Vitality Score"""
        total = self.total_points()
        vitality = (total / 150) * 100
        return round(vitality, 1)
    
    def to_dict(self) -> Dict:
        """Return dimensions as dict for reporting"""
        return {
            'bedroom_standards': self.bedroom_standards,
            'functionality_flow': self.functionality_flow,
            'light_brightness': self.light_brightness,
            'storage_organization': self.storage_organization,
            'condition_maintenance': self.condition_maintenance,
            'photo_strategy': self.photo_strategy,
            'hidden_friction': self.hidden_friction,
            'total_points': self.total_points(),
            'vitality_score': self.to_vitality_score()
        }


@dataclass
class PillarScore:
    """Individual pillar diagnostic score"""
    pillar_name: str  # "Lighting & Optical Health"
    rules_checked: List[int]  # [51, 53, 55, etc.]
    individual_scores: Dict[int, float]  # {51: 8.5, 53: 7.0, ...}
    pillar_score: float  # Average of all rules (0–10)
    issues_found: List[str]  # ["Rule #51 Violation: ...", ...]
    
    def average_score(self) -> float:
        """Average rule score (0–10)"""
        if not self.individual_scores:
            return 0.0
        return sum(self.individual_scores.values()) / len(self.individual_scores)


class UnifiedScoringEngine:
    """
    150-Point Unified Scoring System
    
    Flow:
    1. Vision AI analyzes photos → returns PillarScore for each pillar
    2. PillarScores aggregate to DimensionScores (0–150 total)
    3. DimensionScores convert to Vitality Score (0–100)
    4. Database stores all detail: rule issues, pillar breakdowns, dimension scores
    5. Report displays: Vitality + Pillar detail + Rule issues
    """
    
    # Dimension caps (max points)
    DIMENSION_CAPS = {
        'bedroom_standards': 20,
        'functionality_flow': 20,
        'light_brightness': 20,
        'storage_organization': 20,
        'condition_maintenance': 20,
        'photo_strategy': 10,
        'hidden_friction': 20,
    }
    
    # Pillar-to-Dimension mapping
    PILLAR_DIMENSION_MAP = {
        'Spatial Flow & Ergonomics': [
            ('functionality_flow', 0.7),   # 70% weight
            ('storage_organization', 0.3),  # 30% weight
        ],
        'Lighting & Optical Health': [
            ('light_brightness', 1.0),  # 100% weight
        ],
        'Sensory & Textile Logic': [
            ('bedroom_standards', 0.5),
            ('condition_maintenance', 0.5),
        ],
        'Power & Connectivity': [
            ('hidden_friction', 1.0),  # Modern guest expectations
        ],
        'Intentionality & Soul': [
            ('storage_organization', 0.4),
            ('condition_maintenance', 0.3),
            ('bedroom_standards', 0.3),
        ],
    }
    
    @staticmethod
    def pillar_scores_to_dimensions(pillar_scores: List[PillarScore]) -> DimensionScores:
        """
        Convert 5 Pillar scores to 7 Dimension scores.
        
        Args:
            pillar_scores: List of PillarScore objects from Vision AI
        
        Returns:
            DimensionScores (all 7 dimensions filled)
        """
        dimensions = DimensionScores()
        
        # Create a map of pillar name → pillar score for lookup
        pillar_map = {ps.pillar_name: ps.pillar_score for ps in pillar_scores}
        
        logger.info(f"🔄 Converting 5 Pillar scores to 7 Dimensions")
        logger.info(f"   Pillar scores: {pillar_map}")
        
        # Map each pillar to its dimensions
        for pillar_name, dimension_weights in UnifiedScoringEngine.PILLAR_DIMENSION_MAP.items():
            pillar_score = pillar_map.get(pillar_name, 0.0)
            
            for dimension_name, weight in dimension_weights:
                # Pillar score is 0–10, dimension is 0–20
                # Scale: pillar_score * 2 * weight
                dimension_value = pillar_score * 2 * weight
                
                # Add to appropriate dimension
                if dimension_name == 'bedroom_standards':
                    dimensions.bedroom_standards += dimension_value
                elif dimension_name == 'functionality_flow':
                    dimensions.functionality_flow += dimension_value
                elif dimension_name == 'light_brightness':
                    dimensions.light_brightness += dimension_value
                elif dimension_name == 'storage_organization':
                    dimensions.storage_organization += dimension_value
                elif dimension_name == 'condition_maintenance':
                    dimensions.condition_maintenance += dimension_value
                elif dimension_name == 'hidden_friction':
                    dimensions.hidden_friction += dimension_value
                
                logger.info(f"   {pillar_name} → {dimension_name}: +{dimension_value:.1f} (weight: {weight})")
        
        # Photo strategy is separate (separate rule set, handled outside Vision AI)
        # For now, default to 10/10 (will be filled by dedicated photo analyzer)
        dimensions.photo_strategy = 10.0
        
        # Cap all dimensions at max
        dimensions.bedroom_standards = min(dimensions.bedroom_standards, 20)
        dimensions.functionality_flow = min(dimensions.functionality_flow, 20)
        dimensions.light_brightness = min(dimensions.light_brightness, 20)
        dimensions.storage_organization = min(dimensions.storage_organization, 20)
        dimensions.condition_maintenance = min(dimensions.condition_maintenance, 20)
        dimensions.photo_strategy = min(dimensions.photo_strategy, 10)
        dimensions.hidden_friction = min(dimensions.hidden_friction, 20)
        
        logger.info(f"✅ Dimensions computed:")
        logger.info(f"   Bedroom Standards: {dimensions.bedroom_standards:.1f}/20")
        logger.info(f"   Functionality & Flow: {dimensions.functionality_flow:.1f}/20")
        logger.info(f"   Light & Brightness: {dimensions.light_brightness:.1f}/20")
        logger.info(f"   Storage & Organization: {dimensions.storage_organization:.1f}/20")
        logger.info(f"   Condition & Maintenance: {dimensions.condition_maintenance:.1f}/20")
        logger.info(f"   Photo Strategy: {dimensions.photo_strategy:.1f}/10")
        logger.info(f"   Hidden Friction: {dimensions.hidden_friction:.1f}/20")
        logger.info(f"   TOTAL: {dimensions.total_points():.1f}/150")
        logger.info(f"   Vitality Score: {dimensions.to_vitality_score():.0f}/100")
        
        return dimensions
    
    @staticmethod
    def get_grade(vitality_score: float) -> str:
        """Get letter grade (A–F) for vitality score"""
        if vitality_score >= 90:
            return 'A'
        elif vitality_score >= 80:
            return 'B'
        elif vitality_score >= 70:
            return 'C'
        elif vitality_score >= 60:
            return 'D'
        else:
            return 'F'


# Example usage:
if __name__ == "__main__":
    # Simulate Vision AI returning 5 pillar scores
    pillar_scores = [
        PillarScore('Spatial Flow & Ergonomics', [1, 7, 47, 48], {1: 8.0, 7: 6.5, 47: 7.5, 48: 8.0}, 7.5, []),
        PillarScore('Lighting & Optical Health', [51, 53, 55], {51: 7.0, 53: 6.0, 55: 8.0}, 7.0, ['Rule #51: Mixed bulb temps']),
        PillarScore('Sensory & Textile Logic', [22, 56, 70], {22: 9.0, 56: 8.0, 70: 7.0}, 8.0, []),
        PillarScore('Power & Connectivity', [21, 33], {21: 6.0, 33: 7.0}, 6.5, ['Rule #21: No USB ports']),
        PillarScore('Intentionality & Soul', [50, 76, 87], {50: 7.0, 76: 8.0, 87: 9.0}, 8.0, ['Rule #50: Furniture mismatched']),
    ]
    
    # Convert to dimensions
    dims = UnifiedScoringEngine.pillar_scores_to_dimensions(pillar_scores)
    
    # Get vitality score
    vitality = dims.to_vitality_score()
    grade = UnifiedScoringEngine.get_grade(vitality)
    
    print(f"\n{'='*60}")
    print(f"VITALITY SCORE: {vitality:.0f}/100 (Grade {grade})")
    print(f"{'='*60}")
    print(dims.to_dict())
