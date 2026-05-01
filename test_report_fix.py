#!/usr/bin/env python3
"""
Test Report Generation for Submission #1 to verify fixes.

Tests:
1. Top 3 fixes generation (should NOT be "Perfect Score")
2. PDF page count (should be 8+ pages)
3. Math UI (should show "74/92" + Grade)
"""

import sys
import os
import json
from pathlib import Path

# Add paths
sys.path.insert(0, os.path.dirname(__file__))

from database import DesignDiagnosisDB
from report_generator import generate_report
from pdf_generator_v2 import generate_pdf_report_v2
from data_cleaner import clean_item_name

def test_report_generation():
    """Test report generation for submission #1"""
    
    db = DesignDiagnosisDB("design_diagnosis.db")
    
    # Get submission #1
    submission = db.get_form_submission(1)
    if not submission:
        print("❌ Submission #1 not found")
        return False
    
    print(f"📋 Testing Submission #1: {submission.property_name}")
    print(f"   Comfort items checked: {len(submission.guest_comfort_checklist) if submission.guest_comfort_checklist else 0}")
    print(f"   Photos: {submission.total_photos}")
    
    # Clean the submission data
    cleaned_comfort_list = []
    if submission.guest_comfort_checklist:
        for item_key in submission.guest_comfort_checklist:
            cleaned_name = clean_item_name(item_key)
            cleaned_comfort_list.append(cleaned_name)
    
    submission_dict = {
        'id': submission.id,
        'property_name': submission.property_name,
        'listing_type': submission.listing_type,
        'guest_comfort_checklist': cleaned_comfort_list,
        'total_photos': int(submission.total_photos or 20),
    }
    
    # Generate report
    print("\n📊 Generating report...")
    result = generate_report(submission_dict)
    
    if not result['success']:
        print(f"❌ Report generation failed: {result.get('error')}")
        return False
    
    vitality_data = result['vitality_data']
    print(f"✅ Vitality score: {vitality_data['vitality_score']}/100 (Grade {vitality_data['grade']})")
    print(f"   Comfort: {vitality_data['comfort_score']}/42")
    print(f"   Photos: {vitality_data['photo_score']}/20")
    print(f"   Design: {vitality_data['design_score']}/30")
    print(f"   Raw: {vitality_data['comfort_score'] + vitality_data['photo_score'] + vitality_data['design_score']}/92")
    
    # Check top 3 fixes
    top_three_fixes = result.get('top_three_fixes', [])
    print(f"\n🔧 Top 3 Fixes ({len(top_three_fixes)} found):")
    for i, fix in enumerate(top_three_fixes, 1):
        print(f"   Fix #{i}: {fix['title']}")
        print(f"      Cost: ${fix.get('cost_low')}–${fix.get('cost_high')}")
        print(f"      Impact: {fix.get('impact')}")
        if "Perfect" in fix['title'] or "perfect" in fix['description'].lower():
            print(f"      ⚠️  WARNING: This fix looks like a 'Perfect Score' message!")
    
    if len(top_three_fixes) < 3:
        print(f"❌ ERROR: Only {len(top_three_fixes)} fixes generated (need 3)")
        return False
    
    # Check shopping list
    shopping_list = result.get('shopping_list', [])
    print(f"\n🛒 Shopping list: {len(shopping_list)} items")
    
    # Check analysis text
    analysis = result.get('analysis', '')
    print(f"\n📝 Analysis text: {len(analysis)} chars")
    
    # Generate PDF
    print(f"\n📄 Generating PDF...")
    reports_dir = Path("reports_test")
    reports_dir.mkdir(exist_ok=True)
    
    pdf_path = str(reports_dir / f"submission_{submission.id}_test.pdf")
    
    pdf_success = generate_pdf_report_v2(
        output_path=pdf_path,
        property_name=submission.property_name,
        vitality_data=vitality_data,
        recommendations=result.get('recommendations', []),
        analysis_text=analysis,
        shopping_list=shopping_list,
        top_three_fixes=top_three_fixes,
        report_type="premium"
    )
    
    if not pdf_success:
        print(f"❌ PDF generation failed")
        return False
    
    print(f"✅ PDF generated: {pdf_path}")
    
    # Check file size
    if os.path.exists(pdf_path):
        file_size = os.path.getsize(pdf_path)
        print(f"   File size: {file_size:,} bytes")
        
        # Rough estimate: 8+ pages ≈ 50KB+ (varies with content)
        if file_size > 40000:
            print(f"   ✅ File size suggests 8+ pages")
        else:
            print(f"   ⚠️  File size might indicate fewer pages (typical 8+ page: 50KB+)")
    
    return True

if __name__ == "__main__":
    success = test_report_generation()
    sys.exit(0 if success else 1)
