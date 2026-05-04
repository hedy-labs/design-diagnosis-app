# BRAIN TRANSPLANT: RACHEL RULES v1.0 COMPLETION REPORT

**Status:** ✅ **SUCCESSFULLY INSTALLED**  
**Commit:** `b08b5dd` - feat: Brain Transplant - Rachel Rules v1.0 System Prompt Injection  
**Date:** 2026-05-04 13:12 UTC  
**File Updated:** vision_analyzer_v2.py (master_prompt variable)

---

## WHAT WAS REPLACED

**Location:** `/design-diagnosis-app/vision_analyzer_v2.py` (Line ~184)  
**Variable:** `master_prompt`  
**Function:** Vision analysis system prompt for Claude Vision API

**Old Prompt (Removed):**
- Generic "elite interior designer" persona
- Basic JSON schema with design_scorecard
- No host-speak, no ROI focus
- No photography accountability
- No tier-specific logic

**New Prompt (Installed):**
- Authoritative STR Design Strategist persona
- Host-speak language (punchy, revenue-focused)
- Rachel Rules quality guardrails
- Photography accountability for technical failures
- Price-tier logic (Standard vs Luxury)
- Mandatory ROI metrics (40% revenue, 24% bookings, 26% nightly rate increase)

---

## THE RACHEL RULES FRAMEWORK

### 1. Persona & Tone
- **Role:** Authoritative Short-Term Rental (STR) Design Strategist and ROI Specialist
- **Tone:** Professional, supportive, direct
- **Language:** "Host-Speak" (punchy, revenue-focused)
- **Objective:** Identify low-cost, high-impact design changes that justify rate increases

### 2. Quality Guardrails (The "Rachel Rules")
✅ **Generalize Finishes:** Recommend "statement pendant," "modern pulls" (not "matte black," "brushed gold")  
✅ **Experience Over Utility:** Sell "Pinterest moments," "relaxing escapes," "morning coffee experiences"  
✅ **No Brand Names:** Use "coffee maker" (not "Nespresso")  
✅ **Avoid Staging Drift:** Only suggest items that stay (textiles, furniture—not staging props)  
✅ **Photography Accountability:** Flag dark, grainy, poorly-angled photos and quantify their revenue cost  

### 3. Reporting Structure (Three-Part Hierarchy)
1. **THE "HERO" FIX:** Single most impactful change to room atmosphere
2. **STAGING & "THE CLICK":** Enhancements to stop scroll on booking platforms
3. **AESTHETIC REFRESH:** Lighting, texture, freshness updates (painting, power-washing)

### 4. Price-Tier Logic
- **Standard Tier ($100–$300):** Visual decompression, cable management, lighting, freshness
- **Luxury Tier ($500+):** Prestige and curation, Blue Hour photography, layered textiles

### 5. Mandatory Success Metrics (The Closer)
Always conclude with professional imagery ROI:
- **40%** average increase in revenue
- **24%** increase in total bookings
- **26%** increase in nightly rates
- **85%** of hosts pay off the shoot in just one night

---

## NEW JSON OUTPUT SCHEMA

The system prompt now returns this structured format:

```json
{
  "hero_fix": {
    "title": "The single most impactful change",
    "cost_range": "$X-Y",
    "revenue_impact": "Quantified monthly impact",
    "roi_timeline": "Weeks/months to break even",
    "why_matters": "Host-speak explanation"
  },
  "staging_and_click": {
    "description": "Platform scroll-stop enhancements",
    "items": ["Item 1", "Item 2", "Item 3"],
    "estimated_budget": "$X-Y",
    "booking_impact": "Percentage or nightly rate increase"
  },
  "aesthetic_refresh": {
    "focus_areas": ["Area 1", "Area 2"],
    "actions": ["Action 1", "Action 2"],
    "budget": "$X-Y",
    "perceived_value_increase": "How guests perceive the space"
  },
  "photography_accountability": "Note dark/grainy/poorly-angled photos and cost impact",
  "tier_specific_pivot": "Standard or Luxury advice based on budget",
  "professional_imagery_roi": {
    "average_revenue_increase": "40%",
    "booking_increase": "24%",
    "nightly_rate_increase": "26%",
    "payoff_timeline": "85% of hosts pay off in one night"
  }
}
```

---

## EXAMPLES OF THE DIFFERENCE

### Before (Old Prompt)
```
"The bedroom lacks visual interest and coherence. Consider adding artwork 
to create a focal point, and incorporate textiles to establish a softer 
aesthetic that elevates the overall spatial narrative."
```
❌ Designer-speak, no ROI, no urgency, host sees it as optional

### After (Rachel Rules)
```
HERO FIX: Add 2 bedside lamps and a matching throw blanket
- Cost: $50
- Impact: Couples seeking 'cozy' experiences = +15% bookings = +$180/month revenue
- ROI: $50 investment breaks even in 1 week, pays for itself 3.6x in month 1
- Why it matters: 'Couples Retreat' filter + 'Good for Romance' review anchor
```
✅ Host-speak, clear ROI, quantified impact, host acts immediately

---

## DEPLOYMENT STATUS

**File:** vision_analyzer_v2.py  
**Change Type:** System prompt injection (master_prompt variable)  
**Syntax:** ✅ Validated  
**Tests:** Ready for activation  
**Production:** Ready when Rachel approves

**What This Means:**
- Every property analysis will use the new Rachel Rules framework
- All recommendations will include cost, ROI, and payback timeline
- Photography failures will be explicitly called out with revenue impact
- Tier-specific advice (Standard vs Luxury) will be automatically applied
- Professional imagery ROI metrics will be presented as mandatory closer

---

## GITHUB COMMIT DETAILS

**Commit Hash:** b08b5dd  
**Branch:** main  
**Files Changed:** 1 (vision_analyzer_v2.py)  
**Lines Added:** 57  
**Lines Removed:** 34  
**Net Change:** +23 lines (expanded prompt)

**Commit Message:**
```
feat: Brain Transplant - Rachel Rules v1.0 System Prompt Injection

Updated master_prompt in vision_analyzer_v2.py with Rachel's authoritative
STR Design Strategist framework.
```

---

## VERIFICATION CHECKLIST

- [x] Located master_prompt variable in vision_analyzer_v2.py
- [x] Replaced with Rachel's exact prompt text
- [x] Syntax validated (no Python errors)
- [x] JSON schema matches Rachel's specification
- [x] All 5 Rachel Rules included
- [x] All 5 mandatory success metrics included
- [x] Hero Fix / Staging & Click / Aesthetic Refresh structure present
- [x] Photography accountability field included
- [x] Price-tier logic (Standard vs Luxury) included
- [x] Committed to GitHub (b08b5dd)
- [x] Production-ready for activation

---

## NEXT STEPS (AWAITING RACHEL'S GO-AHEAD)

1. **Rachel reviews:** Confirm the prompt is correct and ready
2. **Deploy:** git pull on DigitalOcean droplet
3. **Restart:** systemctl restart design-diagnosis
4. **Test:** Run analysis on sample property
5. **Verify:** Check JSON output matches schema
6. **Monitor:** Track analysis quality in production

---

## NOTES FOR RACHEL

This brain transplant installs the **Rachel Rules v1.0 framework** directly into the Vision AI's core analysis logic. Every property analyzed will now:

1. Identify the single most impactful "Hero Fix"
2. Recommend platform-optimized "Staging & Click" enhancements
3. Suggest "Aesthetic Refresh" updates
4. Call out photography technical failures and their revenue cost
5. Apply tier-specific logic (budget-appropriate advice)
6. Always close with professional imagery ROI metrics

**Result:** Hosts get revenue-focused, actionable, quantified recommendations—not designer-speak.

---

🟢 **BRAIN TRANSPLANT COMPLETE. AWAITING GO-AHEAD.**