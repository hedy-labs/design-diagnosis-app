#!/usr/bin/env python3
"""
Quick test to verify pdf_generator_v2 generates correct HTML templates
"""

import sys
from pdf_generator_v2 import generate_html_report

# Test data
test_vitality_data = {
    'vitality_score': 75,
    'grade': 'C',
    'grade_description': 'Fair — Some important items missing.',
    'comfort_score': 28,
    'photo_score': 15,
    'design_score': 18
}

test_recommendations = [
    {'priority': 'Critical', 'title': 'Bedside Tables', 'description': 'Add bedside tables for guest comfort.'},
    {'priority': 'High', 'title': 'Entry Hooks', 'description': 'Install coat hooks at entry.'},
    {'priority': 'Important', 'title': 'Shower Caddy', 'description': 'Add shower caddy for toiletries.'},
]

test_top_three_fixes = [
    {'title': 'Bedside Tables + Lamps', 'description': 'Critical comfort signal', 'cost_low': 60, 'cost_high': 150, 'impact': 'High', 'roi': '15-25%'},
    {'title': 'Entry Hooks + Shoe Rack', 'description': 'First impression friction killer', 'cost_low': 50, 'cost_high': 140, 'impact': 'High', 'roi': '15-25%'},
    {'title': 'Shower Caddy + Stool', 'description': 'Shower utility essential', 'cost_low': 20, 'cost_high': 50, 'impact': 'Medium', 'roi': '10-15%'},
]

test_shopping_list = [
    {'category': 'Bedroom', 'tier': 'Value', 'name': 'Bedside Tables', 'price': '$60-$120', 'link': 'https://amazon.com/s?k=nightstands', 'description': 'Minimalist white'},
    {'category': 'Entry', 'tier': 'Value', 'name': 'Coat Hooks', 'price': '$20-$60', 'link': 'https://amazon.com/s?k=wall+hooks', 'description': 'Modern matte black'},
    {'category': 'Bathroom', 'tier': 'Value', 'name': 'Shower Caddy', 'price': '$20-$50', 'link': 'https://amazon.com/s?k=shower+caddy', 'description': 'Teak wood'},
]

def test_premium_html():
    print("Testing PREMIUM HTML generation...")
    html = generate_html_report(
        property_name="Test Property",
        vitality_data=test_vitality_data,
        recommendations=test_recommendations,
        analysis_text="This property has good bones but critical comfort gaps.",
        shopping_list=test_shopping_list,
        top_three_fixes=test_top_three_fixes,
        report_type="premium"
    )
    
    # Verify key sections exist
    checks = [
        ('Header with property name', 'Test Property' in html),
        ('Vitality score', '75' in html),
        ('Grade', 'Grade C' in html),
        ('Analysis text', 'good bones' in html),
        ('Top 3 fixes', 'Bedside Tables' in html),
        ('Shopping list', 'Coat Hooks' in html),
        ('Calendly link', 'calendly.com/roomsbyrachel' in html),
        ('Professional CSS styling', '@page' in html),
        ('Grid layout', 'grid-template-columns' in html),
        ('Weasyprint-compatible HTML', '<html>' in html),
    ]
    
    all_pass = True
    for check_name, result in checks:
        status = "✅" if result else "❌"
        print(f"  {status} {check_name}")
        if not result:
            all_pass = False
    
    return all_pass

def test_free_html():
    print("\nTesting FREE HTML generation...")
    html = generate_html_report(
        property_name="Test Property",
        vitality_data=test_vitality_data,
        recommendations=test_recommendations,
        analysis_text="This property has good bones but critical comfort gaps.",
        shopping_list=[],  # Empty for free
        top_three_fixes=test_top_three_fixes,
        report_type="free"
    )
    
    # Verify key sections exist
    checks = [
        ('Header with property name', 'Test Property' in html),
        ('Vitality score', '75' in html),
        ('Top 3 fixes', 'Bedside Tables' in html),
        ('Upsell CTA', 'Premium' in html),
        ('No shopping list', 'Coat Hooks' not in html),  # Should NOT have shopping
        ('Professional styling', '@page' in html),
    ]
    
    all_pass = True
    for check_name, result in checks:
        status = "✅" if result else "❌"
        print(f"  {status} {check_name}")
        if not result:
            all_pass = False
    
    return all_pass

if __name__ == '__main__':
    print("=" * 60)
    print("PDF GENERATOR V2 HTML TEMPLATE VERIFICATION")
    print("=" * 60)
    
    premium_pass = test_premium_html()
    free_pass = test_free_html()
    
    print("\n" + "=" * 60)
    if premium_pass and free_pass:
        print("✅ ALL TESTS PASSED - HTML templates correct")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED - Check template generation")
        sys.exit(1)
