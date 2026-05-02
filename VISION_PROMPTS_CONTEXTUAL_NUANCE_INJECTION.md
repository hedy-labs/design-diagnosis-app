# CONTEXTUAL NUANCE INJECTION — Vision Prompts Update

**Authority:** Rachel's Blind Test #2 Feedback (STUDIO Property)  
**Date:** May 2, 2026  
**Status:** Production-ready contextual refinements  
**Previous Iteration:** Blind Test #1 (8 hard-coded rules against hallucinations)  
**Current Iteration:** Blind Test #2 (context-aware refinement layer)  

---

## GLOBAL UPDATE: MICRO-SPACE DETECTION & CONTEXT-AWARE SCORING

### NEW RULE: Footprint Assessment First

```
BEFORE APPLYING ANY PILLAR RULES:

Step 0: Detect Property Type & Footprint

MICRO-SPACES (Studio/Hotel Suite):
- Total rooms: ≤ 2 (bedroom + bathroom typical)
- Open-concept living/kitchen/dining common
- Square footage: <400 sq ft (typically)
- Constraints: Tight layouts, limited wall space, furniture placement rigid

APARTMENTS (1-2BR traditional):
- Total rooms: 2-4 (separate living, bedroom(s), kitchen, bathroom)
- Enclosed rooms standard
- Square footage: 400-800 sq ft
- Constraints: Moderate (more flexibility than studios)

HOUSES (3BR+):
- Total rooms: 5+ (separate spaces throughout)
- Full-size rooms standard
- Square footage: 800+ sq ft
- Constraints: Minimal (optimization possible)

DETECTION METHOD:
1. Count distinct enclosed rooms (living room, bedroom, bathroom, kitchen)
2. Assess wall space (tight angles? open-concept?)
3. Estimate total square footage from furniture scale
4. If enclosed rooms ≤ 2 AND open-concept evident → MICRO-SPACE thresholds

THRESHOLD ADJUSTMENTS BY PROPERTY TYPE:

MICRO-SPACE (Studio/Suite):
- Command Position: Accept wall-facing if no alternative (0 points, not -1)
- Artwork: 1-2 pieces appropriate (add 1 more if space allows, not 5-7)
- Investment budget: $300-500 maximum
- Per-room thresholds: Reduce by 50%
- Curtains: Roman blinds acceptable (equal to curtains)
- Area rugs: 1 appropriately-sized rug sufficient (not 1 per room)

APARTMENT (Traditional):
- Command Position: Back-to-wall ideal (+1), wall-facing penalty (-1)
- Artwork: 1+ per room (more generous)
- Investment budget: $800-1500
- Per-room thresholds: Full application

HOUSE (3BR+):
- Command Position: Back-to-wall essential (+1), wall-facing penalty (-1.5)
- Artwork: 1.5+ per room
- Investment budget: $1500+
- Per-room thresholds: Full application with premium standards
```

---

## UPDATE 1: The "Micro-Space" Exception (Command Position & Artwork Rules)

### RULE #2 REVISION: Command Position (Context-Aware)

**Blind Test #2 Failure:** Penalized desk facing wall in studio where no alternative existed.

```
REVISED RULE #2: Command Position (Context-Sensitive)

DETECTION:
Is this a micro-space (studio/suite ≤2 rooms)?
  IF YES → Apply micro-space rule
  IF NO → Apply apartment/house rule

MICRO-SPACE VERSION:
✓ ACCEPTABLE: Desk facing wall when space is constrained
  Studio context = often no alternative
  Layout is optimized given footprint
  Not a failure; unavoidable constraint
  SCORE: 0 points (neutral, not penalty)

✓ IDEAL (if space allows): Desk back-to-wall facing room
  Bonus if feasible without compromising other areas
  SCORE: +0.5 points (optimization)

APARTMENT/HOUSE VERSION:
✗ FAIL: Desk facing wall when alternatives exist
  Spacious room with poor choice = -1 point
  
✓ PASS: Desk back-to-wall facing room
  Professional, confident positioning = +1 point

ASSESSMENT LANGUAGE (Micro-Space):
"Desk is wall-facing. This is the optimal placement given studio constraints. 
While back-to-wall facing room would be ideal in a larger space, the current 
configuration works well for this micro-apartment layout."

NOT: "Desk facing wall = institutional failure (-1 point)"
```

### RULE #8 REVISION: Artwork Counting (Property-Type Scaled)

**Blind Test #2 Failure:** Applied apartment thresholds (1+ per room) to studio (1BR + bathroom).

```
REVISED RULE #8: Artwork Distribution (Property-Type Aware)

DETECTION:
Is this a micro-space (≤2 functional rooms)?
  IF YES → Apply micro-space thresholds
  IF NO → Apply standard thresholds

MICRO-SPACE THRESHOLDS (Studio/Suite):
1-2 pieces visible = Minimal (acceptable for small footprint)
3-4 pieces = Thoughtful (good for studio)
5+ pieces = Risk of clutter (too much for small space)

SCORING:
1 piece = 5/10 (minimal)
2 pieces = 7/10 (adequate for studio)
3 pieces = 8/10 (thoughtful distribution)
4+ pieces = 9/10 (excellent, if not cluttered)

RED FLAG THRESHOLD:
<1 piece per 4 rooms = RED FLAG (insufficient intentionality)
NOT: <1 piece per 2 rooms (apartment standard)

APARTMENT THRESHOLDS (2-3BR):
<1 per 2 rooms = RED FLAG
1 per room = Adequate
1.5+ per room = Thoughtful

ASSESSMENT LANGUAGE (Micro-Space):
"Studio contains 2 pieces of artwork. This is appropriate for the square footage. 
Consider adding 1 more thoughtfully-chosen piece to reach 'excellent' range (8+/10). 
Recommendation: Art for [specific wall], not additional pieces elsewhere."

NOT: "Only 2 pieces in 3+ rooms = RED FLAG (0.25 per room)"
```

---

## UPDATE 2: The "Negative Hallucination" Fix (Lighting & Textiles)

### RULE #3 REVISION: Lighting (Alternative Fixture Recognition)

**Blind Test #2 Failure:** Claimed "harsh overhead-only lighting" when desk lamp, wall sconces, and floor lamp were present.

```
REVISED RULE #3: Lighting Inventory (Comprehensive Fixture Search)

CRITICAL FIX:
Do NOT just look for recessed ceiling lights.
Expand search to ALL lighting fixture types:

TASK LIGHTING (not just table lamps):
✓ Table lamps (standard)
✓ Desk lamps (on furniture, not on tables)
✓ Wall sconces (mounted on walls, easily missed)
✓ Floor lamps (standing lights, often in corners)

AMBIENT LIGHTING (not just pendants):
✓ Pendant lights (from ceiling)
✓ Chandeliers
✓ Floor uplights
✓ Wall washers

ACCENT LIGHTING:
✓ Picture lights (above artwork)
✓ Spot lights
✓ Strip lighting

OVERHEAD:
✓ Recessed ceiling lights
✓ Surface-mounted ceiling fixtures

ASSESSMENT PROCESS:
1. List EVERY light source visible in photos (name each)
2. Categorize: Overhead / Task / Ambient / Accent
3. Count total types: If 4+ types present = good layering
4. Assess warmth: 2700K-3000K = warm (good)

COMMON MISSES:
- Wall sconces (small, mounted on wall, easy to overlook)
- Floor lamps in corners (dark areas of photos)
- Desk lamps (seen from distance, small in frame)

ASSESSMENT LANGUAGE:
Instead of: "Only overhead recessed lights, harsh and institutional"
Say: "Overhead recessed lights + desk lamp + wall sconces + floor lamp visible. 
Multiple light sources create good layering. Warm white bulbs noted."

SCORING:
- Only overhead: 5-6/10
- Overhead + 1 task light: 6-7/10
- Overhead + 2+ task lights: 7-8/10
- Overhead + task + ambient + warm bulbs: 8-9/10
```

### RULE #3 REVISION: Textiles (Alternative Window Treatment Recognition)

**Blind Test #2 Failure:** Claimed "NO CURTAINS" when Roman blinds were present but hard to see.

```
REVISED RULE #3: Textiles (Window Treatment Types)

CRITICAL FIX:
"Curtains" ≠ only heavy drapes.
Window treatments include:

CURTAINS/DRAPES (traditional):
✓ Heavy curtains (most obvious)
✓ Sheer curtains (light filtering)
✓ Thermal curtains (blackout)

BLINDS (often hard to see):
✓ Roman blinds/shades (fabric, motorized or manual)
✓ Venetian blinds (slats, wood or metal)
✓ Vertical blinds (sliding panels)
✓ Roller shades (pull-down fabric)
✓ Cellular shades (honeycomb, insulating)

SPECIALTY:
✓ Plantation shutters (louvered, wood)
✓ Japanese shades (cellular style)
✓ Sliding panels (modern alternative)

ASSESSMENT PROCESS:
1. Look at every window in every photo
2. Identify ANY type of covering (not just obvious curtains)
3. Note color/material (influences softness perception)
4. If covering is subtle/hard to see, STILL COUNT IT

COMMON MISSES:
- Roman blinds (fabric, blend with walls, small details)
- Roller shades (pull-down, subtle in photos)
- Cellular shades (appear as simple texture, easy to miss)

ASSESSMENT LANGUAGE:
Instead of: "NO CURTAINS IN ANY ROOM - Missing window treatments entirely"
Say: "Roman blinds present on windows (subtle/hard to see in photos). 
Adequate for light control and privacy. Heavier curtains could add more softness 
and layering, but current treatment is functional."

SCORING:
- No window treatment: 3-4/10 (gap)
- Subtle blinds (Roman, roller, cellular): 5-6/10 (adequate)
- Traditional curtains: 7-8/10 (good)
- Layered curtains + blinds: 8-9/10 (excellent)
```

---

## UPDATE 3: The Usability & Proportion Check (NEW Rule for Spatial Flow)

### NEW RULE: Functional Assessment Layer

**Blind Test #2 Failure:** Missed mirror trapped between bed & wall (can't use), artwork too large for wall, microwave precariously on mini-fridge.

```
NEW RULE: Usability & Proportion Check (Spatial Flow Detail Layer)

ASSESSMENT REQUIREMENT:
Do not just identify objects. Assess their interaction and functionality.

THREE CHECKS FOR EVERY FURNITURE/FIXTURE ITEM:

1. USABILITY CHECK: "Can a human actually use this?"
   - Mirror: Is there clearance in front to see yourself? (measure ~3 ft minimum)
   - Door: Does it open fully without hitting furniture?
   - Desk: Is there legroom and comfortable reach to keyboard?
   - Bed: Can both sides be accessed? Is there clearance for standing/dressing?
   - Chairs: Can you sit without hitting walls/furniture?

2. SAFETY CHECK: "Is this stable and safe?"
   - Appliances: On proper table/stand (not balancing on fridge)?
   - Furniture: Against walls or stable in open space?
   - Lamps: Stable base, not tipsy or precarious?
   - Shelving: Properly anchored (not wobbling)?

3. PROPORTION CHECK: "Is the scale correct for the space/wall?"
   - Artwork: Appropriate size for wall (not oversized, not postage-stamp tiny)?
   - Furniture: Scale appropriate to room (oversized couch in small bedroom?)?
   - Rugs: Properly sized to anchor furniture group (postage-stamp rug doesn't count)?
   - Accessories: Not overwhelming the space?

ASSESSMENT LANGUAGE:
"Full-length mirror is positioned between bed and wall, limiting clearance 
to see yourself. Recommend relocating to: [alternatives]. This is a usability 
issue, not a presence issue."

"Artwork above desk is proportionally oversized for the wall space. Creates 
visual imbalance in small room. Recommend: [smaller piece] or [repositioning]."

"Microwave is balancing on mini-fridge, creating safety risk. Recommend: 
Small table underneath ($80-150) to stabilize and organize kitchenette."

SCORING IMPACT:
- Usability failure (mirror trapped, can't access): -1 point (Pillar 1)
- Safety risk (appliance placement): -1 point (Pillar 1)
- Proportion mismatch (artwork too large): -0.5 point (Pillar 5)
- Missing item (should have cushions): -0.5 point (Pillar 5)

EXAMPLE (STUDIO):
Pillar 1 Assessment includes:
- Desk orientation ✓
- Walkway clearance ✓
- Furniture scale ✓
- **NEW: Usability checks** (mirror clearance, door swing, bed access)
- **NEW: Safety checks** (microwave stability, lamp stability)
```

---

## UPDATE 4: The Sizing Rule (Rug Appropriateness)

### RULE #4 REVISION: Area Rugs (Quality + Appropriateness)

**Blind Test #2 Failure:** Counted tiny rug under bed as "area rug" when it did nothing for the space.

```
REVISED RULE #4: Area Rugs (Size & Function Assessment)

CURRENT MISTAKE:
Presence alone is not enough. A postage-stamp rug under the bed 
does not count as proper layering.

REVISED ASSESSMENT:

1. EXISTENCE CHECK:
   Area rug visible? YES/NO

2. SIZE ASSESSMENT (if present):
   "Postage stamp" (too small): 2-3/10 (does nothing for space)
   Undersized (misses mark): 4-5/10 (minimal coverage)
   Appropriately-sized: 7-8/10 (anchors furniture group)
   Oversized/generous: 8-9/10 (fills room well)

3. PLACEMENT CHECK:
   Proper anchor? Under sofa (living) or under bed + surrounding (bedroom)?
   Visible and functional? Or hidden/ineffective?
   Strategic? Does it define space? Or is it an afterthought?

4. IMPACT ASSESSMENT:
   Does rug improve spatial coherence? Color? Texture? Coziness?
   If it's tiny, it likely doesn't.

ASSESSMENT LANGUAGE:
Instead of: "Area rug present: +0.5 points"
Say: "Small area rug partially under bed appears undersized and does not 
effectively anchor the space. Recommend: Appropriately-sized rug (6x9 or 8x10) 
positioned under sofa OR under bed with surrounding coverage. This would 
significantly improve spatial coherence and add colour/texture."

SCORING:
- No rug: -0.5 point
- Undersized/ineffective rug: -0.25 point (same issue, less severe)
- Appropriately-sized rug: +0.5 point
- Oversized/generous rug: +1 point

EXAMPLE (STUDIO):
"1 small rug partially under bed (underperforming). 
Expected: 1 appropriately-sized rug anchoring main seating area. 
Investment: $150-250. Impact: +0.5 to +1 point (Pillar 3)."
```

---

## UPDATE 5: Scaled Cost Estimation

### NEW RULE: Property-Type Cost Scaling

**Blind Test #2 Failure:** Estimated $850-$1,100 for studio; should be $300-$500.

```
REVISED RULE: Cost Estimation (Property-Type Scaled)

ERROR:
Applied apartment-scale budgets to micro-spaces.
Micro-space furniture, fixes, and improvements cost 50% less.

SCALING FACTOR BY PROPERTY TYPE:

MICRO-SPACE (Studio/Suite, ≤2 rooms, <400 sq ft):
Budget cap: $300-500 per phase
Rationale: Fewer items to fix, smaller furniture, minimal wall space
Examples:
- Curtains/blinds: $80-150 (fewer windows)
- Area rug: $100-200 (smaller space to cover)
- Artwork: $50-150 per piece (smaller walls accommodate smaller/cheaper art)
- Lamps: $40-80 each (smaller fixtures)
- Cushions: $30-60 each

APARTMENT (1-2BR, 400-800 sq ft):
Budget cap: $800-1500 per phase
Rationale: Multiple rooms, more wall space, more items needed

HOUSE (3BR+, 800+ sq ft):
Budget cap: $1500-2500+ per phase
Rationale: Large spaces, full-size furniture, premium finishes justified

COST ESTIMATION PROCESS:

1. Identify property type (micro-space vs. apartment vs. house)
2. List fixes needed (curtains, rugs, art, lamps, etc.)
3. Apply micro-space prices (50% reduction from apartment scale)
4. Bundle fixes into realistic phases:
   - Phase 1 (immediate impact): 50-60% of budget
   - Phase 2 (nice-to-have): 30-40% of budget
   - Phase 3+ (polish): 10-20% of budget

EXAMPLE ESTIMATION (STUDIO):
Phase 1 - $300-400:
  Appropriately-sized area rug: $150-200
  Decorative cushions (2-3): $80-120
  Small artwork piece: $50-100
  Total: $280-420 ✓

NOT: 
Phase 1 - $850-1100:
  Curtains all windows: $200-400
  Area rugs multiple rooms: $300-500
  Table lamps: $150-250
  Total: $650-1150 ✗ (over-specified for studio)

ASSESSMENT LANGUAGE:
"Investment path to Grade C: $300-500 (Phase 1) + $100-200 (Phase 2).
Studios have lower budget requirements than apartments due to smaller 
square footage and fewer items needed."
```

---

## COMPLETE MICRO-SPACE CONTEXT CHECKLIST

### Before Analyzing Any Property:

```
STEP 0: PROPERTY TYPE DETECTION (Pre-Pillar)

1. Count enclosed rooms (separate from open-concept)
   Result: ___ (target: ≤2 for micro, 2-4 for apartment, 5+ for house)

2. Assess open-concept areas
   Result: Living/kitchen/dining combined? YES/NO

3. Estimate total square footage (from furniture scale)
   Result: ___ sq ft (target: <400 for micro, 400-800 for apartment, 800+ for house)

4. Look for wall constraints (tight angles, built-ins)
   Result: Constrained? Moderate? Spacious?

5. FINAL CLASSIFICATION:
   ☐ Micro-Space (Studio/Suite) → Apply micro thresholds
   ☐ Apartment (1-2BR traditional) → Apply standard thresholds
   ☐ House (3BR+) → Apply premium thresholds

THRESHOLDS TO APPLY:

IF MICRO-SPACE:
✓ Command Position: Accept wall-facing (0 points)
✓ Artwork: 1-2 pieces appropriate (no RED FLAG)
✓ Budget: $300-500 max per phase
✓ Curtains: Roman blinds count equally
✓ Rugs: 1 appropriately-sized rug sufficient
✓ Usability checks: Mirror clearance, safety, proportions
✓ Negative hallucination fix: Look for subtle items (sconces, blinds)

IF APARTMENT:
✓ Command Position: Back-to-wall ideal (+1), wall-facing penalty (-1)
✓ Artwork: 1+ per room standard
✓ Budget: $800-1500 per phase
✓ Thresholds: Full application
✓ Usability checks: Full application

IF HOUSE:
✓ Command Position: Back-to-wall essential (+1), wall-facing penalty (-1.5)
✓ Artwork: 1.5+ per room
✓ Budget: $1500+ per phase
✓ Thresholds: Full application with premium standards
```

---

## IMPLEMENTATION STATUS

✅ Footprint detection (micro-space vs. apartment vs. house)  
✅ Command Position rule (context-aware, not rigid)  
✅ Artwork counting rule (property-type scaled)  
✅ Lighting fixture search (comprehensive, including sconces & floor lamps)  
✅ Window treatment recognition (Roman blinds = curtains)  
✅ Usability & Proportion check (NEW layer for spatial flow)  
✅ Rug appropriateness assessment (size + function)  
✅ Cost estimation scaling (micro-space: 50% of apartment budget)  
✅ Negative hallucination fix (look for subtle items before claiming absence)  

---

## BLIND TEST #2 RECALIBRATION (With Contextual Nuance)

**Original AI Score:** 62/100 (D) — Rigid, context-unaware  
**With Contextual Nuance:** 65-66/100 (C-/C) — Context-appropriate  
**Improvement:** +3-4 points  

**Key Corrections Applied:**
1. Detected micro-space (studio ≤2 rooms)
2. Accepted desk-facing-wall as constraint (0 points, not -1)
3. Accepted 2 artworks as appropriate for studio (not RED FLAG)
4. Found Roman blinds, desk lamp, wall sconces, floor lamp (not "harsh overhead-only")
5. Assessed rug size (too small, appropriately-sized recommended)
6. Identified usability issues (mirror placement, artwork scale, microwave safety)
7. Applied micro-space budget ($300-500, not $850-1100)

---

**STATUS: Contextual Nuance Injection Complete. System Ready for Blind Test #3.**
