# Rachel's Vision AI Verification Checklist

**Date:** 2026-05-01 13:45 UTC  
**Purpose:** Confirm system architecture before first Gemini API call  
**Status:** AWAITING RACHEL SIGN-OFF

---

## VERIFICATION REQUIRED

### 1. PILLAR 2 PROMPT LOGIC ✓ DRAFT

**File:** `VISION_PROMPT_PILLAR_2_LIGHTING.md`

**Questions to verify:**

- [ ] **Rule #51 (Warm Over Cool):** Does the prompt correctly identify 2700K–3000K as target, with 5000K+ as failure?
  - **Prompt language:** "All visible bulbs are 2700K–3000K warm white (yellow-toned, NOT blue-white)"
  - **Violation:** "Bulbs appear cool white 5000K+ (sterile, blue-tinted)"
  - **Your feedback:** ___________________________

- [ ] **Rule #53 (Three Points of Light):** Does the prompt capture overhead + task + ambient requirement?
  - **Prompt language:** "Room has 3+ distinct light sources: (1) Overhead, (2) Task lamp, (3) Ambient/mood"
  - **Failure condition:** "Only ceiling light = Visual Interrogation"
  - **Your feedback:** ___________________________

- [ ] **Rule #55 (Reflective Magic):** Does the prompt check mirror positioning opposite windows?
  - **Prompt language:** "Mirrors positioned opposite or near windows to bounce natural light"
  - **Failure:** "Mirror present but facing wall or in bright area (wasting potential)"
  - **Your feedback:** ___________________________

- [ ] **Rule #52 (Eye-Level):** Does the prompt prevent glare from naked bulbs?
  - **Prompt language:** "Lampshades sit at guest eye level when seated (prevents glare from naked bulb)"
  - **Your feedback:** ___________________________

- [ ] **Bathroom Mirror Test:** Does the prompt specifically check for vanity lights (not just ceiling)?
  - **Prompt language:** "Mirror has side lighting (vanity lights) OR top lighting that illuminates face"
  - **Failure:** "Mirror lit only from ceiling (creates eye shadow = guest looks tired in mirror)"
  - **Your feedback:** ___________________________

- [ ] **Bedroom Blackout:** Does the prompt audit for light leaks?
  - **Prompt language:** "Thick, opaque blackout curtains/shades with NO visible light leaks at edges"
  - **Scoring:** "10 = full blackout, 7 = minor light leak, 3 = significant leak, 0 = no treatment"
  - **Your feedback:** ___________________________

---

### 2. 150-POINT SYSTEM DENOMINATOR ✓ DRAFT

**File:** `scoring_unified.py`

**Architecture Question:** Is 150 points the right denominator for final vitality percentage?

**Current System:**
```
Vitality Score = (total_points / 150) * 100

Where:
- Dimension 1 (Bedroom Standards): 0–20 pts
- Dimension 2 (Functionality & Flow): 0–20 pts
- Dimension 3 (Light & Brightness): 0–20 pts
- Dimension 4 (Storage & Organization): 0–20 pts
- Dimension 5 (Condition & Maintenance): 0–20 pts
- Dimension 6 (Photo Strategy): 0–10 pts
- Dimension 7 (Hidden Friction): 0–20 pts
= 150 total
```

**Alternative Considered:** 92-point system (Comfort 42 + Photos 20 + Design 30)
- ❌ **Problem:** Doesn't accommodate all 87 Rules and 5 Pillars
- ❌ **Problem:** Loses detail across 7 Dimensions

**Questions:**
- [ ] Should we use **150 points** as the authoritative denominator?
  - This gives room for all 87 Rules across 5 Pillars and 7 Dimensions
  - Vitality Score remains 0–100 (transparent percentage math)
  - **Your feedback:** ___________________________

- [ ] Or should we **keep 92 points** and use a different system?
  - **Pros:** Simpler, aligns with current report setup
  - **Cons:** Doesn't have room for all expert detail
  - **Your feedback:** ___________________________

---

### 3. DATABASE SCHEMA: vision_analysis TABLE ✓ DRAFT

**File:** `VISION_DATA_FLOW_ARCHITECTURE.md`

**Proposed Table Structure:**

```sql
CREATE TABLE vision_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    submission_id INTEGER NOT NULL UNIQUE,
    
    -- 5 Pillar scores (0–10 each from Vision AI)
    pillar_1_spatial_flow REAL,
    pillar_2_lighting REAL,
    pillar_3_textiles REAL,
    pillar_4_power REAL,
    pillar_5_intentionality REAL,
    
    -- JSON columns for flexible reporting
    all_violations TEXT,  -- ["Rule #51 Violation: ...", ...]
    room_detail TEXT,     -- {master_bedroom: {...}, living_room: {...}}
    dimension_scores TEXT, -- {bedroom_standards: 18.0, ..., vitality_score: 68.7}
    recommended_fixes TEXT,-- [{priority: 1, rule: "#51", cost: 10-40, ...}]
    
    -- Metadata
    analysis_timestamp DATETIME,
    raw_gemini_response TEXT,
    model_version TEXT,
    
    FOREIGN KEY(submission_id) REFERENCES form_submissions(id)
);
```

**Questions:**
- [ ] Does this table structure work for your reporting workflow?
  - **Concern:** JSON columns allow flexible querying (e.g., "show all bedroom issues")
  - **Concern:** all_violations is a simple list for Page 5 rendering
  - **Your feedback:** ___________________________

- [ ] Should room_detail track rule scores PER ROOM (e.g., master_bedroom.rule_51 = 7.5)?
  - **Current design:** Yes, per-room rule breakdown
  - **Purpose:** Allows Page 5 to say "Master Bedroom: Rule #51 (7.5/10) — Mixed bulb temps"
  - **Your feedback:** ___________________________

- [ ] Should we store raw_gemini_response for audit trail?
  - **Rationale:** If Gemini response format changes, we can re-parse historical data
  - **Storage cost:** ~10–15KB per submission
  - **Your feedback:** ___________________________

---

### 4. PAGE 5 REPORT STRUCTURE ✓ DRAFT

**File:** `VISION_DATA_FLOW_ARCHITECTURE.md` (Section: STEP 6)

**Proposed Page 5 Layout:**

```
┌─────────────────────────────────────────┐
│ Pillar Diagnostic Breakdown             │
│                                          │
│ Pillar 1: Spatial Flow & Ergonomics     │
│ Score: 7.5/10                           │
│ • Layout allows 60cm+ walkways ✓       │
│ ✗ Rule #7: Rug too small (5/10)         │
│   → Add larger rug to anchor seating   │
│                                          │
│ Pillar 2: Lighting & Optical Health     │
│ Score: 6.8/10                           │
│ ✗ Rule #51: Mixed bulb temps (5/10)     │
│   → Replace cool-white with 2700K      │
│ ✗ Rule #53: Only 2 light sources (5/10) │
│   → Add floor lamp + bedside lamp      │
│ ... (Pillars 3–5)                       │
└─────────────────────────────────────────┘
```

**Questions:**
- [ ] Should each Pillar show a score (0–10) or just violations?
  - **Proposed:** Show score + checkmarks for wins + violations for issues
  - **Alternative:** Only show violations (simpler, less cluttered)
  - **Your feedback:** ___________________________

- [ ] Should violations be prioritized by impact or by pillar order?
  - **Proposed:** Order by pillar (1–5), then by score (lowest first)
  - **Alternative:** Priority-sort all violations (Critical → Nice to Have)
  - **Your feedback:** ___________________________

- [ ] Should room-by-room detail (master_bedroom, living_room, etc.) appear on Page 5?
  - **Proposed:** Yes, sub-section: "Master Bedroom Findings" showing room-specific rule issues
  - **Alternative:** Mention rooms in violation text only (e.g., "Master Bedroom: Rule #51...")
  - **Your feedback:** ___________________________

---

### 5. RULE VIOLATION MESSAGE FORMAT ✓ DRAFT

**Proposed Format:**

```
"Rule #51 Violation: Bulbs are cool white (5000K). Guests perceive institutional coldness. 
Replace with warm white 2700–3000K."
```

**Questions:**
- [ ] Is this the right tone (direct, actionable, expert)?
  - **Alternative:** "Rule #51 — Lighting temperature. Cool white detected. Recommendation: Switch to 2700K warm white."
  - **Your feedback:** ___________________________

- [ ] Should violation messages include room location?
  - **Proposed:** "Rule #51 Violation (Master Bedroom): Bulbs are cool white..."
  - **Your feedback:** ___________________________

- [ ] Should we append cost estimates for fixes?
  - **Proposed:** Include in Top 3 Fixes section, not in violation text
  - **Your feedback:** ___________________________

---

### 6. INTEGRATION READINESS ✓ DRAFT

**Questions:**
- [ ] Are we ready to call Gemini 1.5 Pro with Pillar 2 prompt?
  - **Status:** Prompt drafted and documented
  - **Validation:** Rule-specific checks, JSON schema defined
  - **Your approval:** ___________________________

- [ ] Should we start with a TEST SUBMISSION before running on Report #96?
  - **Proposed:** Test on Submission #1 (existing test data) first
  - **Rationale:** Verify data flow (Vision AI → DB → Report) before production run
  - **Your approval:** ___________________________

- [ ] Once Pillar 2 works, should we draft Pillars 1, 3, 4, 5?
  - **Timeline:** 2–3 hours per pillar (follow same structure as Pillar 2)
  - **Your approval:** ___________________________

---

## APPROVAL SIGN-OFF

**Once all questions above are answered, provide final approval:**

```
✅ RACHEL APPROVAL: All logic verified. Proceed with Vision API integration.

Approved by: _________________________ (Rachel)
Date: ___________________
```

---

## NEXT STEPS (Upon Approval)

1. **Create vision_analysis table** in database
2. **Call Gemini 1.5 Pro** with Pillar 2 prompt on test submission
3. **Verify JSON response** matches expected schema
4. **Aggregate Pillar scores** to Dimension scores (scoring_unified.py)
5. **Save to database** via new vision_analysis table
6. **Generate Page 5** report section from vision_analysis data
7. **Test full 8-page report** with Vision AI data included
8. **Draft Pillars 1, 3, 4, 5** prompts (same structure)
9. **Run on Report #96** as production test case
10. **Deploy to production**

---

**File Status:** Ready for review  
**Estimated Vision AI Integration Time:** 3–4 hours (Pillar 2 + testing)  
**All 5 Pillars Ready:** By Friday evening, 2026-05-01 18:00 UTC

Awaiting Rachel's verification and approval. 🚀
