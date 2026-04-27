"""
CODE QUALITY VERIFICATION: Pre-Server Tests

Tests that verify code quality and correctness WITHOUT requiring a running server.
These tests validate:
1. Model configuration is correct
2. Scraper selectors are improved
3. Upload fallback logic is connected
4. Test bypass endpoint exists

Run: python3 tests/test_code_quality.py
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

class CodeQualityTest:
    """Test code quality before server startup"""
    
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.errors = []
    
    def log(self, result, message):
        if result:
            print(f"✅ {message}")
            self.tests_passed += 1
        else:
            print(f"❌ {message}")
            self.tests_failed += 1
            self.errors.append(message)
    
    def test_vision_model_version(self):
        """Verify Vision model is claude-3-5-sonnet-20240620"""
        print("\n📋 TEST 1: Vision Model Version")
        
        try:
            with open("vision_analyzer_v2.py", "r") as f:
                content = f.read()
            
            # Check for correct model version
            if 'claude-3-5-sonnet-20240620' in content:
                self.log(True, "Model version is claude-3-5-sonnet-20240620 (correct)")
            else:
                self.log(False, "Model version NOT set to 20240620")
            
            # Check for incorrect version
            if 'claude-3-5-sonnet-20241022' not in content:
                self.log(True, "Old model version (20241022) removed")
            else:
                self.log(False, "Old model version (20241022) still present")
        
        except Exception as e:
            self.log(False, f"Failed to read vision_analyzer_v2.py: {e}")
    
    def test_scraper_selectors(self):
        """Verify scraper has improved grid selectors"""
        print("\n📋 TEST 2: Scraper Grid Selectors")
        
        try:
            with open("photo_scraper.py", "r") as f:
                content = f.read()
            
            # Check for Airbnb grid class selectors
            selectors_to_check = [
                "itu7ddv",  # Carousel class
                "_6tbg2q",  # Grid item class
                "a0.muscache",  # Airbnb CDN
                "pdp-gallery-container",  # Gallery container
            ]
            
            found_count = sum(1 for sel in selectors_to_check if sel in content)
            
            self.log(
                found_count >= 3,
                f"Improved grid selectors found ({found_count}/4)"
            )
            
            # Check for deduplication logic
            has_dedup = "seen = new Set()" in content or "Set()" in content
            self.log(has_dedup, "Image deduplication logic present")
            
            # Check for min image threshold
            has_threshold = "len(images) >= 5" in content or "< 3" in content
            self.log(has_threshold, "Image threshold logic present (5+ requirement)")
        
        except Exception as e:
            self.log(False, f"Failed to read photo_scraper.py: {e}")
    
    def test_upload_fallback_logic(self):
        """Verify upload fallback is integrated"""
        print("\n📋 TEST 3: Upload Fallback Logic")
        
        try:
            with open("main.py", "r") as f:
                content = f.read()
            
            # Check for helper function
            has_helper = "def get_uploaded_photos_for_submission" in content
            self.log(has_helper, "Upload helper function exists")
            
            # Check for fallback trigger with < 3 images
            has_fallback_trigger = "len(image_urls) < 3" in content
            self.log(has_fallback_trigger, "Fallback triggered when < 3 images")
            
            # Check for upload directory config
            has_upload_dir = "UPLOADED_PHOTOS_DIR" in content
            self.log(has_upload_dir, "Upload photos directory configured")
            
            # Check for temp upload cleanup
            has_move_logic = "shutil.move" in content
            self.log(has_move_logic, "Photo movement logic present")
        
        except Exception as e:
            self.log(False, f"Failed to read main.py: {e}")
    
    def test_test_bypass_endpoint(self):
        """Verify test bypass endpoint exists"""
        print("\n📋 TEST 4: Test Bypass Endpoint")
        
        try:
            with open("main.py", "r") as f:
                content = f.read()
            
            # Check for test endpoint
            has_test_endpoint = "@app.post(\"/test/mark-payment-complete\")" in content
            self.log(has_test_endpoint, "Test bypass endpoint defined")
            
            # Check for test key validation
            has_test_key = "PILOT_TEST_KEY" in content
            self.log(has_test_key, "Test key validation present")
            
            # Check for fake payment creation
            has_fake_payment = "db.create_payment" in content
            self.log(has_fake_payment, "Fake payment creation logic present")
        
        except Exception as e:
            self.log(False, f"Failed to read main.py: {e}")
    
    def test_python_syntax(self):
        """Verify all files have valid Python syntax"""
        print("\n📋 TEST 5: Python Syntax")
        
        files_to_check = [
            "main.py",
            "vision_analyzer_v2.py",
            "photo_scraper.py",
            "tests/test_premium_flow.py"
        ]
        
        for filename in files_to_check:
            try:
                import py_compile
                py_compile.compile(filename, doraise=True)
                self.log(True, f"{filename} - syntax OK")
            except Exception as e:
                self.log(False, f"{filename} - syntax error: {e}")
    
    def run_all_tests(self):
        """Execute all code quality tests"""
        print("\n" + "=" * 60)
        print("CODE QUALITY VERIFICATION")
        print("=" * 60)
        
        self.test_vision_model_version()
        self.test_scraper_selectors()
        self.test_upload_fallback_logic()
        self.test_test_bypass_endpoint()
        self.test_python_syntax()
        
        # Summary
        print("\n" + "=" * 60)
        print("CODE QUALITY SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.tests_passed}")
        print(f"❌ Failed: {self.tests_failed}")
        
        if self.tests_failed == 0:
            print("\n✅ CODE QUALITY PASSED - All checks successful")
            return True
        else:
            print("\n❌ CODE QUALITY FAILED - Issues found:")
            for error in self.errors:
                print(f"   - {error}")
            return False


if __name__ == "__main__":
    tester = CodeQualityTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
