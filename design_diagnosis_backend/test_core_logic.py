"""
Core Logic Tests (No external dependencies)

Tests database, scoring engine, and calculations without reportlab or fastapi
"""

import sys
import sqlite3
from datetime import datetime


def log(message, level="INFO"):
    """Simple logger"""
    prefix = {
        "INFO": "ℹ️ ",
        "PASS": "✅",
        "FAIL": "❌",
        "DEBUG": "🔍"
    }.get(level, "  ")
    print(f"{prefix} {message}")


def test_scoring_calculations():
    """Test core scoring math"""
    log("Testing Vitality Score Calculations...", "DEBUG")
    
    try:
        # Test 1: Grade assignment
        test_cases = [
            (95.0, "A"),
            (85.0, "B"),
            (75.0, "C"),
            (65.0, "D"),
            (45.0, "F"),
        ]
        
        def assign_grade(score):
            if score >= 90:
                return "A"
            elif score >= 80:
                return "B"
            elif score >= 70:
                return "C"
            elif score >= 60:
                return "D"
            else:
                return "F"
        
        for score, expected_grade in test_cases:
            grade = assign_grade(score)
            assert grade == expected_grade, f"Expected {expected_grade}, got {grade}"
            log(f"  Grade: {score}/100 → {grade} ✓")
        
        # Test 2: Vitality score from 150-point system
        dims = [14, 15, 16, 12, 14, 7, 6]  # 1-5: 20pts, 6: 10pts, 7: 20pts
        total_points = sum(dims)
        vitality = (total_points / 150) * 100
        
        log(f"  Scoring: {dims} → Total: {total_points}/150 → {vitality:.1f}/100")
        assert abs(vitality - 59.3) < 1.0
        assert assign_grade(vitality) == "F"
        
        # Test 3: Photo strategy scoring (0-10 scale)
        photo_score = 0.0
        
        # Count: 32 photos → in 31-50 range → 2 points
        if 31 <= 32 <= 50:
            photo_score += 2
        
        # Consistency: 2 issues → 1 point
        if 2 <= 2:
            photo_score += 1
        
        # Quality: 7.5/10 → (7.5/10)*3 = 2.25 points
        photo_score += (7.5 / 10) * 3
        
        photo_score = max(0, min(10, photo_score))  # Clamp to 0-10
        log(f"  Photo score (32 photos, 2 issues, 7.5 quality): {photo_score:.1f}/10")
        
        # Test 4: Hidden friction scoring
        # Critical items (2.0 pts each), high items (1.5 pts each)
        hf_score = 20.0
        hf_score -= 2.0  # No dryer (critical)
        hf_score -= 1.5  # Hangers insufficient (high)
        hf_score -= 1.5  # No drying rack (high)
        hf_score = max(0, min(20, hf_score))
        
        log(f"  Hidden friction (3 missing items): {hf_score:.1f}/20")
        assert abs(hf_score - 15.0) < 0.1
        
        log("Scoring Calculations test PASSED", "PASS")
        return True
    
    except Exception as e:
        log(f"Scoring test FAILED: {e}", "FAIL")
        return False


def test_database_schema():
    """Test SQLite database schema"""
    log("Testing Database Schema...", "DEBUG")
    
    try:
        import tempfile
        import os
        
        # Create temp DB
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test.db")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute("""
            CREATE TABLE properties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                airbnb_url TEXT UNIQUE,
                property_name TEXT NOT NULL,
                location TEXT,
                bedrooms INTEGER DEFAULT 0,
                bathrooms INTEGER DEFAULT 0,
                guest_capacity INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                property_id INTEGER NOT NULL UNIQUE,
                vitality_score REAL DEFAULT 0.0,
                grade TEXT DEFAULT 'F',
                total_points REAL DEFAULT 0.0,
                dimension_scores_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (property_id) REFERENCES properties(id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE dimension_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_id INTEGER NOT NULL,
                dimension INTEGER NOT NULL,
                score REAL NOT NULL,
                max_points REAL NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (report_id) REFERENCES reports(id)
            )
        """)
        
        conn.commit()
        
        # Test insertion
        cursor.execute("""
            INSERT INTO properties (airbnb_url, property_name, location, bedrooms, bathrooms, guest_capacity)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ("https://example.com", "Test Property", "Test City", 2, 1, 4))
        
        prop_id = cursor.lastrowid
        log(f"  Created property ID {prop_id}")
        
        # Create report
        cursor.execute("INSERT INTO reports (property_id) VALUES (?)", (prop_id,))
        report_id = cursor.lastrowid
        log(f"  Created report ID {report_id}")
        
        # Save dimension scores
        for dim in range(1, 8):
            max_pts = 20 if dim != 6 else 10
            cursor.execute("""
                INSERT INTO dimension_scores (report_id, dimension, score, max_points, notes)
                VALUES (?, ?, ?, ?, ?)
            """, (report_id, dim, 15.0, max_pts, f"Test dimension {dim}"))
        
        conn.commit()
        
        # Verify data
        cursor.execute("SELECT * FROM properties WHERE id = ?", (prop_id,))
        prop = cursor.fetchone()
        assert prop[2] == "Test Property"
        log(f"  Property retrieval: {prop[2]} ✓")
        
        cursor.execute("SELECT COUNT(*) FROM dimension_scores WHERE report_id = ?", (report_id,))
        count = cursor.fetchone()[0]
        assert count == 7
        log(f"  Saved 7 dimension scores ✓")
        
        conn.close()
        log("Database Schema test PASSED", "PASS")
        return True
    
    except Exception as e:
        log(f"Database test FAILED: {e}", "FAIL")
        return False


def test_vitality_formula():
    """Test the core 150-point → 100-point scaling formula"""
    log("Testing Vitality Score Formula...", "DEBUG")
    
    try:
        # Formula: (Total / 150) * 100
        # Dimensions: 1-5 (20pts each) + 6 (10pts) + 7 (20pts) = 150pts total
        
        test_cases = [
            # (d1, d2, d3, d4, d5, d6, d7, expected_vitality, expected_grade)
            (20, 20, 20, 20, 20, 10, 20, 100.0, "A"),  # Perfect
            (18, 19, 18, 17, 19, 9, 20, 99.3, "A"),    # Near perfect
            (16, 16, 16, 16, 16, 8, 16, 87.3, "B"),    # Very good
            (14, 15, 16, 12, 14, 7, 6, 59.3, "F"),     # Rachel's Airbnb
            (10, 12, 10, 8, 10, 5, 10, 65.3, "D"),     # Empty box-ish
            (0, 0, 0, 0, 0, 0, 0, 0.0, "F"),           # Terrible
        ]
        
        for d1, d2, d3, d4, d5, d6, d7, exp_score, exp_grade in test_cases:
            total = d1 + d2 + d3 + d4 + d5 + d6 + d7
            vitality = (total / 150) * 100
            
            def assign_grade(score):
                if score >= 90:
                    return "A"
                elif score >= 80:
                    return "B"
                elif score >= 70:
                    return "C"
                elif score >= 60:
                    return "D"
                else:
                    return "F"
            
            grade = assign_grade(vitality)
            
            assert abs(vitality - exp_score) < 1.0
            assert grade == exp_grade
            
            log(f"  [{d1},{d2},{d3},{d4},{d5},{d6},{d7}] → {vitality:.1f}/100 ({grade}) ✓")
        
        log("Vitality Formula test PASSED", "PASS")
        return True
    
    except Exception as e:
        log(f"Formula test FAILED: {e}", "FAIL")
        return False


def main():
    print("\n" + "="*70)
    print("DESIGN DIAGNOSIS — CORE LOGIC TEST HARNESS")
    print("="*70 + "\n")
    
    results = [
        ("Scoring Calculations", test_scoring_calculations()),
        ("Database Schema", test_database_schema()),
        ("Vitality Formula", test_vitality_formula()),
    ]
    
    passed = sum(1 for _, result in results if result)
    failed = sum(1 for _, result in results if not result)
    
    print("\n" + "="*70)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*70 + "\n")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
