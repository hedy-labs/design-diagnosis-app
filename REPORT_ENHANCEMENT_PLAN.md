# Report Enhancement Plan — PDF Restoration & Content Population

## Current State
- PDF generation is **DISABLED** (main.py line 720)
- Email templates exist but analysis_text is blank/empty
- Reports lack "The Problem" narrative and detailed "Three Fixes"
- Shopping lists not integrated into reports
- No consultation CTA in the PDF

## What Needs to Happen

### 1. Re-Enable PDF Generation in main.py
Currently disabled. Need to restore:
```python
pdf_success = generate_pdf_report(
    output_path=pdf_path,
    property_name=submission.property_name,
    vitality_data=score_data,
    recommendations=recommendations,
    analysis_text=result.get("analysis", ""),
    shopping_list=result.get("shopping_list", [])
)
```

### 2. Enhance report_generator.py
Add these methods to `ReportBuilder` class:

#### Method A: `_generate_analysis_text()`
Generates "The Problem" narrative:
- Explains why the property scored as it did
- Identifies root causes (missing comfort items, design gaps, etc.)
- Written in Rachel's voice (professional, actionable)
- Example: "Your property has strong bones but critical comfort gaps. Guests will notice the missing bedside tables immediately—this is a 10-second first impression killer."

#### Method B: `_generate_top_three_fixes()`
Extracts the **3 highest-impact, most-urgent** recommendations:
- Prioritizes by ROI (guest satisfaction + cost)
- Includes estimated cost range (from shopping lists)
- Includes estimated impact on booking rates
- Example:
  1. **Add bedside tables + lamps** ($150–300) → Guests feel "home-ready"
  2. **Install entry hooks + shoe rack** ($50–100) → Reduces first-contact friction
  3. **Add bathroom caddy + plunger** ($30–80) → Essential comfort signal

#### Method C: `_generate_shopping_list()`
Creates a structured shopping list organized by:
- **Budget Tier**: Value / Signature / Luxury
- **Categories**: Bedroom, Bathroom, Entry, Living Room, Kitchen
- **For each item**:
  - Product name
  - Amazon/Wayfair/IKEA link
  - Price (with affiliate tag)
  - Why it matters (e.g., "Bedside lamps: Guest comfort signal")
- **Phased approach**: "Month 1 Critical Fixes" → "Month 2 Polish"

#### Method D: Enhanced `build_html_report()`
Add sections:
1. **The Problem** (analysis_text)
2. **Three High-Impact Fixes** (top three with costs)
3. **Complete Score Breakdown** (all recommendations)
4. **Shopping List** (by budget tier)
5. **Book a Consultation** (with Rachel's Calendly link)

### 3. Restore pdf_generator.py
Add parameters to `generate_pdf_report()`:
- `analysis_text`: "The Problem" narrative (2-3 paragraphs)
- `shopping_list`: Array of items with prices and links
- `consultation_link`: Rachel's Calendly or booking URL

Build 8-9 page PDF with:
- Page 1: Score card + grade + "The Problem"
- Pages 2-3: Three High-Impact Fixes with costs
- Pages 4-6: Complete breakdown + all recommendations
- Pages 7-8: Shopping list (organized by budget tier)
- Page 9: "Book a Consultation with Rachel" CTA + contact info

### 4. Update email_service.py
Ensure emails include:
- PDF attachment (for premium reports)
- Proper MIME type handling
- "Your expert report is being generated and will arrive in your inbox in 2-3 minutes" message on success page

### 5. Update success page (payment-success.html)
Add waiting message:
```html
<p>✨ Your expert report is being generated...</p>
<p>📧 We'll send it to your inbox in 2-3 minutes.</p>
<p>Check your spam folder if you don't see it!</p>
```

---

## Rachel's Input Needed

1. **Calendly/Booking Link**: What's your booking URL?
   - Example: `https://calendly.com/rachel-interior-design`
   - This goes in the "Book a Consultation" CTA in the PDF

2. **Affiliate Links**: Do you have active affiliate accounts for:
   - Amazon Associates
   - Wayfair
   - IKEA
   - West Elm
   - Target

3. **Shopping List Budget Tiers**: Confirm the price ranges you want:
   - Value: $20–80/item
   - Signature: $80–200/item
   - Luxury: $200–600/item

---

## Implementation Order

1. **Phase A** (Today): Restore PDF generation, re-enable pdf_generator calls in main.py
2. **Phase B** (Tomorrow): Enhance report_generator with analysis_text + three_fixes + shopping_list
3. **Phase C** (Next day): Update email templates with PDF attachment handling
4. **Phase D** (Testing): End-to-end test with real property (free + premium flows)

---

## Files to Modify

| File | Changes | Complexity |
|------|---------|-----------|
| `main.py` | Uncomment PDF generation, restore pdf_path logic | Low |
| `report_generator.py` | Add analysis_text, shopping_list, three_fixes generation | High |
| `pdf_generator.py` | Accept new params, build 8-9 page PDF | High |
| `email_service.py` | PDF attachment handling, proper MIME types | Medium |
| `payment-success.html` | Add "generating report..." message | Low |

---

## Timeline

- **2 hours**: Phase A (PDF restoration)
- **3-4 hours**: Phase B (analysis + fixes + shopping list)
- **2 hours**: Phase C (PDF + email integration)
- **1 hour**: Phase D (testing)

**Total: ~8-10 hours of development**

---

## Success Criteria

✅ Premium report is 8-9 pages (PDF attachment, not email body)  
✅ Free report is 3 pages (score + three fixes + shopping list intro)  
✅ "The Problem" narrative is populated (not blank)  
✅ "Three High-Impact Fixes" are specific to the property  
✅ Shopping lists have prices and links  
✅ "Book a Consultation" CTA is active  
✅ PDFs render without emoji issues  
✅ Emails arrive in inbox (not spam) with attachments  
✅ Success page shows "generating report..." message  
✅ Free flow: email only (no PDF, just upsell to premium)  
✅ Premium flow: PDF attachment + full email + consultation CTA

