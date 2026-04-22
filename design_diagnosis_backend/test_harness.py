"""
Design Diagnosis Test Harness

Tests the complete scoring pipeline:
1. Database initialization
2. Scoring engine
3. API endpoints (mocked)
4. PDF generation
"""

import sys
import json
from datetime import datetime

from database import DesignDiagnosisDB, Property
from scoring import ScoringEngine, ScoringInput, PhotoStrategyScorer, HiddenFrictionScorer
from pdf_report import VitalityReportPDF


class TestHarness:
    """Test suite for Design Diagnosis backend"""
    
    def __init__(self):
        self.db = DesignDiagnosisDB("test_design_diagnosis.db")
        self.passed = 0
        self.failed = 0
    
    def log(self, message: str, level: str = "INFO"):
        """Log test message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = {
            "INFO": "ℹ️ ",
            "PASS": "✅",
            "FAIL": "❌",
            "DEBUG": "🔍"
        }.get(level, "  ")
        print(f"[{timestamp}] {prefix} {message}")
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("\n" + "="*70)
        print("DESIGN DIAGNOSIS BACKEND — TEST HARNESS")
        print("="*70 + "\n")
        
        self.test_database()
        self.test_scoring_engine()
        self.test_photo_scorer()
        self.test_hidden_friction()
        self.test_end_to_end()
        self.test_pdf_generation()
        
        print("\n" + "="*70)
        self.log(f"Test Results: {self.passed} passed, {self.failed} failed", "DEBUG")
        print("="*70 + "\n")
    
    def test_database(self):
        """Test database CRUD operations"""
        self.log("Testing Database CRUD...", "DEBUG")
        
        try:
            # Create property
            prop = Property(
                property_name="Test Property 1",
                location="Test City",
                bedrooms=2,
                bathrooms=1,
                guest_capacity=4
            )
            prop_id = self.db.create_property(prop)
            self.log(f"Created property ID {prop_id}")
            
            # Retrieve property
            retrieved = self.db.get_property(prop_id)
            assert retrieved.property_name == "Test Property 1"
            self.log("Property retrieval successful")
            
            # Create report
            report_id = self.db.create_report(prop_id)
            self.log(f"Created report ID {report_id}")
            
            # Save dimension scores
            self.db.save_dimension_score(report_id, 1, 18.5, 20.0, "Good bedroom standards")
            self.db.save_dimension_score(report_id, 7, 6.0, 20.0, "Missing items")
            
            # Retrieve dimension scores
            dim_scores = self.db.get_dimension_scores(report_id)
            assert len(dim_scores) == 2
            self.log(f"Saved and retrieved {len(dim_scores)} dimension scores")
            
            self.passed += 1
            self.log("Database CRUD test PASSED", "PASS")
        
        except Exception as e:
            self.failed += 1
            self.log(f"Database test FAILED: {e}", "FAIL")
    
    def test_scoring_engine(self):
        """Test scoring calculation"""
        self.log("Testing Scoring Engine...", "DEBUG")
        
        try:
            # Test grade assignment
            test_cases = [
                (95.0, "A"),
                (85.0, "B"),
                (75.0, "C"),
                (65.0, "D"),
                (45.0, "F"),
            ]
            
            for score, expected_grade in test_cases:
                grade = ScoringEngine.assign_grade(score)
                assert grade == expected_grade, f"Expected {expected_grade}, got {grade}"
                self.log(f"Grade assignment: {score}/100 → {grade} ✓")
            
            # Test vitality score calculation
            vitality, total, grade = ScoringEngine.calculate_vitality_score(
                18, 15, 16, 12, 14, 7, 6  # Should be ~59/100, F grade
            )
            
            assert abs(vitality - 59.3) < 1.0
            assert grade == "F"
            self.log(f"Vitality calculation: {vitality:.1f}/100, grade {grade} ✓")
            
            self.passed += 1
            self.log("Scoring Engine test PASSED", "PASS")
        
        except Exception as e:
            self.failed += 1
            self.log(f"Scoring test FAILED: {e}", "FAIL")
    
    def test_photo_scorer(self):
        """Test photo strategy scoring"""
        self.log("Testing Photo Strategy Scorer...", "DEBUG")
        
        try:
            # Test cases
            test_cases = [
                # (photo_count, consistency_issues, quality_score, expected_score)
                (25, 0, 8.0, 8.5),   # Good
                (50, 1, 6.0, 5.0),   # Acceptable
                (80, 3, 4.0, 2.0),   # Poor
                (15, 0, 9.0, 9.5),   # Excellent
            ]
            
            for count, consistency, quality, expected in test_cases:
                score = PhotoStrategyScorer.score_photos(count, consistency, quality)
                self.log(f"Photo score: {count} photos, {consistency} issues, quality {quality} → {score:.1f}")
                assert abs(score - expected) <= 1.5  # Allow small variance
            
            self.passed += 1
            self.log("Photo Strategy test PASSED", "PASS")
        
        except Exception as e:
            self.failed += 1
            self.log(f"Photo test FAILED: {e}", "FAIL")
    
    def test_hidden_friction(self):
        """Test hidden friction scoring"""
        self.log("Testing Hidden Friction Scorer...", "DEBUG")
        
        try:
            # Test case: Rachel's Airbnb (missing 3 critical items)
            missing = [
                ("hangers", "high"),
                ("dryer", "critical"),
                ("drying_rack", "critical"),
            ]
            
            score = HiddenFrictionScorer.calculate_score(missing)
            self.log(f"Hidden friction score: {len(missing)} items → {score:.1f}/20")
            
            # Expected: 20 - (1.5 + 2 + 2) = 14.5
            assert abs(score - 14.5) < 0.1
            
            self.passed += 1
            self.log("Hidden Friction test PASSED", "PASS")
        
        except Exception as e:
            self.failed += 1
            self.log(f"Hidden Friction test FAILED: {e}", "FAIL")
    
    def test_end_to_end(self):
        """End-to-end test: Rachel's Airbnb scenario"""
        self.log("Testing End-to-End Scenario (Rachel's Airbnb)...", "DEBUG")
        
        try:
            # Create property
            prop = Property(
                airbnb_url="https://www.airbnb.ca/rooms/1607891254358662604",
                airbnb_id="1607891254358662604",
                property_name="Trion @ KL",
                location="Kuala Lumpur, Malaysia",
                bedrooms=2,
                bathrooms=1,
                guest_capacity=4
            )
            prop_id = self.db.create_property(prop)
            
            # Create report
            report_id = self.db.create_report(prop_id)
            
            # Score all dimensions
            scoring_input = ScoringInput(
                property_id=prop_id,
                property_name=prop.property_name,
                bedrooms=2,
                bathrooms=1,
                guest_capacity=4,
                bedroom_standards_score=14.0,
                functionality_flow_score=15.0,
                light_brightness_score=16.0,
                storage_organization_score=12.0,
                condition_maintenance_score=14.0,
                photo_count=32,
                photo_consistency_issues=2,
                photo_quality_score=7.5,
                hidden_friction_items_missing=["hangers", "dryer", "drying_rack"],
                hidden_friction_score=6.0
            )
            
            result = ScoringEngine.score_from_input(scoring_input)
            
            # Save to database
            self.db.update_report_scores(
                report_id=report_id,
                vitality_score=result.vitality_score,
                grade=result.grade,
                total_points=result.total_points,
                dimension_scores=result.dimension_scores
            )
            
            # Verify results
            self.log(f"Vitality Score: {result.vitality_score:.1f}/100")
            self.log(f"Grade: {result.grade}")
            self.log(f"Total Points: {result.total_points:.1f}/150")
            
            # Check expected score ~59/100, F grade
            assert abs(result.vitality_score - 59.3) < 5.0  # Allow ±5 variance
            assert result.grade == "F"
            
            self.passed += 1
            self.log("End-to-End test PASSED", "PASS")
        
        except Exception as e:
            self.failed += 1
            self.log(f"End-to-End test FAILED: {e}", "FAIL")
    
    def test_pdf_generation(self):
        """Test PDF report generation"""
        self.log("Testing PDF Generation...", "DEBUG")
        
        try:
            pdf_gen = VitalityReportPDF("test_report.pdf")
            
            dimension_scores = {
                1: 14, 2: 15, 3: 16, 4: 12, 5: 14, 6: 7, 7: 6
            }
            
            missing_items = [
                "Insufficient hangers in bedrooms",
                "No clothes dryer or drying rack",
                "Limited storage space",
            ]
            
            output_file = pdf_gen.generate(
                property_name="Trion @ KL",
                location="Kuala Lumpur, Malaysia",
                vitality_score=59.3,
                grade="F",
                total_points=89.0,
                dimension_scores=dimension_scores,
                missing_items=missing_items,
                cost_estimate=1200.0,
                roi_projection=18.5
            )
            
            self.log(f"PDF generated: {output_file}")
            
            self.passed += 1
            self.log("PDF Generation test PASSED", "PASS")
        
        except Exception as e:
            self.failed += 1
            self.log(f"PDF test FAILED: {e}", "FAIL")


if __name__ == "__main__":
    harness = TestHarness()
    harness.run_all_tests()
    
    sys.exit(0 if harness.failed == 0 else 1)
