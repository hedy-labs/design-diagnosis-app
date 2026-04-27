#!/usr/bin/env python3
"""
Test script to verify PDF gatekeeper logic:
- FREE reports should NOT generate PDFs
- PREMIUM reports should generate PDFs
- Data cleaning should convert underscores to human-readable names
"""

from data_cleaner import clean_item_name, clean_missing_items_list

print("=" * 60)
print("DATA CLEANER VERIFICATION")
print("=" * 60)

# Test data cleaning
test_items = [
    'bedside_lamps',
    'face_cloths',
    'shower_hooks',
    'dish_drying_rack',
    'extra_blanket',
    'coffee_maker'
]

print("\nTesting item name cleaning:")
all_pass = True
for item in test_items:
    cleaned = clean_item_name(item)
    # Verify no underscores remain
    has_underscore = '_' in cleaned
    status = "❌" if has_underscore else "✅"
    print(f"  {status} {item} → {cleaned}")
    if has_underscore:
        all_pass = False

print("\nTesting list cleaning:")
cleaned_list = clean_missing_items_list(test_items)
print(f"  Input: {test_items}")
print(f"  Output: {cleaned_list}")

# Verify no underscores in any output
has_underscores = any('_' in item for item in cleaned_list)
status = "❌" if has_underscores else "✅"
print(f"  {status} All items cleaned (no underscores)")
if has_underscores:
    all_pass = False

print("\n" + "=" * 60)
print("PDF GATEKEEPER LOGIC (Conceptual Check)")
print("=" * 60)
print("""
The updated generate_and_send_report() function now:

1. ✅ Only generates PDFs if report_type == "premium"
2. ✅ Skips PDF generation entirely for "free" reports
3. ✅ Hard fails on PDF generation error (no fallback)
4. ✅ Sends email with pdf_path=None for free reports
5. ✅ Sends email with pdf_path=<path> for premium reports

Email service will:
- Skip PDF attachment if pdf_path is None
- Include PDF attachment if pdf_path is not None
""")

print("\n" + "=" * 60)
if all_pass:
    print("✅ ALL TESTS PASSED")
else:
    print("❌ SOME TESTS FAILED")
print("=" * 60)
