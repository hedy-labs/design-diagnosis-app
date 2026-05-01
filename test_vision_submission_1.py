#!/usr/bin/env python3
"""
Test Vision AI on Submission #1 (Test Villa)

Runs end-to-end Pillar 2 analysis to verify:
1. System prompt adoption of "Vibe → Expert Why → Fix" format
2. Gemini integration works correctly
3. JSON parsing is correct
4. Data flow is operational

Usage:
    python3 test_vision_submission_1.py
"""

import json
import sys
import os
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from database import DesignDiagnosisDB
from vision_service import VisionService

def get_test_images():
    """Find test images in the project"""
    # Look for test images in common locations
    test_image_dirs = [
        Path('./test_images'),
        Path('./static/test_images'),
        Path('./test_data/images'),
        Path('./sample_images'),
    ]
    
    images = []
    for image_dir in test_image_dirs:
        if image_dir.exists():
            images.extend(sorted(image_dir.glob('*.jpg')))
            images.extend(sorted(image_dir.glob('*.png')))
            images.extend(sorted(image_dir.glob('*.jpeg')))
    
    if images:
        logger.info(f"✅ Found {len(images)} test images")
        return [str(img) for img in images[:10]]  # Max 10 for Gemini
    else:
        logger.warning("⚠️  No test images found in standard directories")
        return None


def run_vision_test():
    """Execute Vision AI test on Submission #1"""
    
    print("\n" + "="*80)
    print("VISION AI TEST: Submission #1 (Test Villa) — Pillar 2: Lighting")
    print("="*80 + "\n")
    
    # Step 1: Initialize database
    print("[1/5] Initializing database...")
    db = DesignDiagnosisDB("design_diagnosis.db")
    
    submission = db.get_form_submission(1)
    if not submission:
        print("❌ Submission #1 not found in database")
        return False
    
    print(f"✅ Found Submission #1: {submission.property_name}")
    print(f"   Property name: {submission.property_name}")
    print(f"   Airbnb URL: {submission.airbnb_url}")
    print(f"   Guest capacity: {submission.guest_capacity}")
    
    # Step 2: Find test images
    print("\n[2/5] Looking for test images...")
    images = get_test_images()
    
    if not images:
        print("\n⚠️  NO TEST IMAGES FOUND")
        print("\nTo run this test, you need test property photos.")
        print("Place images in one of these directories:")
        print("  - ./test_images/")
        print("  - ./static/test_images/")
        print("  - ./test_data/images/")
        print("\nSupported formats: .jpg, .png, .jpeg")
        print("\nAlternatively, provide Airbnb URL and I can scrape photos.")
        return False
    
    print(f"✅ Found {len(images)} test images")
    for idx, img in enumerate(images, 1):
        print(f"   {idx}. {Path(img).name}")
    
    # Step 3: Check Gemini API availability
    print("\n[3/5] Checking Gemini API...")
    service = VisionService()
    
    if not service.ready:
        print("❌ Gemini API not available")
        print("   Set GEMINI_API_KEY environment variable:")
        print("   export GEMINI_API_KEY='your-api-key-here'")
        return False
    
    print("✅ Gemini 1.5 Pro Vision ready")
    
    # Step 4: Run Vision AI analysis
    print("\n[4/5] Running Pillar 2 (Lighting) analysis...")
    print("   Sending images to Gemini...")
    
    analysis = service.analyze_pillar_2_lighting(images)
    
    if not analysis:
        print("❌ Analysis failed")
        return False
    
    print(f"✅ Analysis complete: pillar_score={analysis.pillar_score:.1f}/10")
    
    # Step 5: Display results
    print("\n[5/5] Results\n")
    
    print("="*80)
    print("PILLAR 2: LIGHTING & OPTICAL HEALTH")
    print("="*80)
    print(f"\nScore: {analysis.pillar_score:.1f}/10")
    print(f"\n{analysis.pillar_narrative}\n")
    
    # Show findings with Human Voice format
    if analysis.findings:
        print("DETAILED FINDINGS (Human Voice Format):")
        print("-" * 80)
        
        for i, finding in enumerate(analysis.findings, 1):
            print(f"\n[Finding {i}] {finding.room.title()}")
            print(f"Issue: {finding.issue_type.replace('_', ' ').title()}")
            print(f"Score: {finding.score:.1f}/10")
            
            print(f"\nThe Vibe:")
            print(f"  \"{finding.the_vibe}\"")
            
            print(f"\nThe Expert Why:")
            print(f"  \"{finding.expert_why}\"")
            
            print(f"\nThe Fix:")
            print(f"  \"{finding.the_fix}\"")
            
            if finding.cost_low and finding.cost_high:
                print(f"  Cost: ${finding.cost_low}–${finding.cost_high}")
            
            print()
    
    # Show room summaries
    if analysis.room_summaries:
        print("\n" + "="*80)
        print("ROOM-BY-ROOM SUMMARY")
        print("="*80)
        
        for room_name, summary in analysis.room_summaries.items():
            print(f"\n{room_name.title()}:")
            print(f"  Feel: {summary.get('overall_feel', 'N/A')}")
            
            if summary.get('wins'):
                print(f"  Wins:")
                for win in summary['wins']:
                    print(f"    ✓ {win}")
            
            if summary.get('gaps'):
                print(f"  Gaps to fix:")
                for gap in summary['gaps']:
                    print(f"    ✗ {gap}")
    
    # Show priority fixes
    if analysis.priority_fixes:
        print("\n" + "="*80)
        print("PRIORITY FIXES (Cost-Sorted)")
        print("="*80)
        
        for fix in analysis.priority_fixes:
            print(f"\n#{fix['priority']}: {fix['fix_name']}")
            print(f"  Impact: {fix['impact']}")
            print(f"  Cost: ${fix['cost_low']}–${fix['cost_high']}")
    
    # Show raw JSON
    print("\n" + "="*80)
    print("RAW JSON RESPONSE (for verification)")
    print("="*80 + "\n")
    
    json_output = {
        'pillar_name': analysis.pillar_name,
        'pillar_score': analysis.pillar_score,
        'findings': [
            {
                'room': f.room,
                'issue_type': f.issue_type,
                'the_vibe': f.the_vibe,
                'expert_why': f.expert_why,
                'the_fix': f.the_fix,
                'score': f.score,
                'cost_low': f.cost_low,
                'cost_high': f.cost_high,
            }
            for f in analysis.findings
        ],
        'room_summaries': analysis.room_summaries,
        'pillar_narrative': analysis.pillar_narrative,
        'priority_fixes': analysis.priority_fixes,
    }
    
    print(json.dumps(json_output, indent=2))
    
    print("\n" + "="*80)
    print("✅ VISION TEST COMPLETE")
    print("="*80 + "\n")
    
    return True


if __name__ == "__main__":
    try:
        success = run_vision_test()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
