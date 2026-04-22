# Design Diagnosis Scoring Refinement
## Rachel's "Beautiful ≠ Usable" Feedback Integration

**Status:** 🎯 CRITICAL REFINEMENT LOCKED  
**Source:** Rachel's Trion @ KL assessment (2026-04-17 09:59 UTC)  
**Impact:** Transforms app from photo-scorer to functional hospitality validator  

---

## THE CORE INSIGHT

**"On camera, it's a 10/10. In practice, the UX is a disaster."**

**Problem:** Current scoring asks "Does the property HAVE X?"  
**Solution:** New scoring asks "Can the guest FUNCTIONALLY USE X?"

### Example Transformation

❌ **OLD (Presence-based):**
```
"Kitchen has stove" → +1 point
"Bedroom has lamp" → +1 point
"Living room has furniture" → +1 point
```

✅ **NEW (Functionality-based):**
```
"Kitchen has stove, pans, knives, oil, salt, paper towels, drying rack" → +3 points
"Bedroom has 2 lamps + 2 end tables (for 2 guests)" → +3 points
"Living room has furniture + coasters + felt pads (for 2+ guests)" → +2 points
```

---

## 5 NEW SCORING LAYERS (Integrated into Dimension 7: Hidden Friction)

### **LAYER 1: UTILITY COMPLETENESS**

**Principle:** Each functional zone (kitchen, bedroom, bathroom) has a baseline utility requirement.

#### Kitchen Utility Checklist (was −10 points in Rachel's assessment)
```
Core Cookware:
  ✅ Pots (minimum: 2 of different sizes) → +1
  ✅ Pans (minimum: 1 functional, non-damaged) → +1
  ❌ MISSING functional cookware → −2 (critical)

Utensils:
  ✅ Knives (minimum: 1 functional) → +0.5
  ✅ Cutting board (minimum: 1) → +0.5
  ❌ MISSING prep tools → −1.5 (critical)

Dishware (scale by guest capacity):
  ✅ Plates: 1 per guest + 1 spare → +1
  ✅ Bowls: 1 per guest + 1 spare → +1
  ✅ Mugs: 1 per guest + 1 spare → +1
  ❌ Only 2 total (insufficient for 2 guests) → −1

Pantry Essentials:
  ✅ Oil → +0.5
  ✅ Salt → +0.5
  ✅ Sugar → +0.5
  ✅ Condiments → +0.5
  ❌ None present → −1.5 (critical)

Cleaning:
  ✅ Paper towels → +0.5
  ✅ Dish soap → +0.5
  ✅ Dish drying rack (if washer, or stand-alone) → +1
  ❌ MISSING all → −2 (critical)

Appliances (scale by stay length):
  ✅ Microwave → +1 (flexibility)
  ✅ Air fryer (bonus) → +1
  ✅ Water filter → +0.5 (quality signal)
  ❌ None → −1.5

**TOTAL KITCHEN UTILITY: 0–15 points possible**
```

#### Bedroom Utility Checklist (was −5.5 points in Rachel's assessment)
```
Lighting (for N guests):
  ✅ 1 bedside lamp per guest → +2
  ✅ 1 end table per guest → +2
  ✅ Overhead light → +1
  ❌ Asymmetrical (1 lamp + N guests where N>1) → −2

Sleeping Infrastructure:
  ✅ 1 pillow per guest → +1
  ✅ Quality bedding (not institutional white sheets) → +1
  ✅ Throws/blankets for warmth → +1
  ❌ Bare-bones (white sheet only) → −1

Closet/Hanging:
  ✅ 10+ hangers per bedroom → +2
  ✅ Hangers scale by stay length:
      - Short stay (1–5 days): 5+ hangers → +1
      - Medium stay (6–14 days): 10+ hangers → +2
      - Long stay (15+ days): 15+ hangers → +3
  ❌ 3 hangers (for 28-day stay) → −2 (critical)

Storage:
  ✅ Dresser or shelves → +1
  ✅ Laundry hamper → +1
  ❌ No storage → −1.5

**TOTAL BEDROOM UTILITY: 0–15 points possible**
```

#### Bathroom Utility Checklist (was −2 points in Rachel's assessment)
```
Safety:
  ✅ Non-slip bath mats (minimum: 2, one by tub, one by sink) → +2
  ✅ Proper lighting → +1
  ❌ No mats (slip hazard) → −2 (critical)

Comfort/Hygiene:
  ✅ Towel set (3 bath, 3 hand, 3 face per guest) → +1
  ✅ Hooks for organization → +1
  ✅ Toilet brush + plunger → +1
  ❌ Missing → −1 per item

Storage:
  ✅ Under-sink storage for TP backup → +1
  ✅ Shelves for toiletries → +1
  ❌ No storage (clutter) → −1

**TOTAL BATHROOM UTILITY: 0–10 points possible**
```

### **LAYER 2: QUANTITY-TO-DURATION MATCHING**

**Principle:** Scale utility requirements by stay length.

```
SHORT STAY (1–5 days):
├── Hangers: 5+ acceptable
├── Cookware: 1 pan, 1 knife acceptable
├── Dishware: 2 plates okay (daily wash)
└── Hangers deduction: −0.5 if <5

MEDIUM STAY (6–14 days):
├── Hangers: 10+ required
├── Cookware: 2 pans, 1 knife required
├── Dishware: 4 plates + bowls (multiple days between wash)
└── Hangers deduction: −1 if <10

LONG STAY (15+ days, monthly rental):
├── Hangers: 15+ required
├── Cookware: 2+ pans, 2 knives required
├── Dishware: 6+ plates, 6 bowls (full week between wash)
├── Storage: Multiple drawers/closet space critical
└── Hangers deduction: −2 if <15

SCORING LOGIC:
if stay_length < 6:
    hanger_requirement = 5
elif stay_length < 15:
    hanger_requirement = 10
else:
    hanger_requirement = 15

if hangers >= hanger_requirement:
    score += 1
elif hangers >= hanger_requirement * 0.5:
    score += 0
else:
    score += -1
```

### **LAYER 3: ASYMMETRY DETECTION**

**Principle:** Flag mismatched pairs (2 guests but 1 lamp = inequitable design).

```
ASYMMETRY RULES:

Bedroom (2-guest assumption):
  ❌ 1 bedside lamp + 2 pillows → −2 (one guest can't read)
  ❌ 1 end table + 2 pillows → −1.5 (asymmetrical sleeping)
  ❌ 1 power bar + 2 beds → −1 (unfair charging access)

Bathroom (shared):
  ❌ 1 hook + 2 towel sets → −1 (storage inequity)
  ❌ 1 bath mat + 2 guests → −1 (safety concern)

Living/Dining:
  ❌ 1 chair + 2 guests → flag for dinners/gatherings
  ❌ Couch but no second seating + 2 guests → −1

DETECTION LOGIC:
for guest in range(guest_count):
    if bedside_lamps < guest_count and guest_count > 1:
        score += -2
    
    if end_tables < guest_count and guest_count > 1:
        score += -1.5
    
    if bath_mats < guest_count and guest_count > 1:
        score += -1
```

### **LAYER 4: SAFETY LAYER**

**Principle:** Flag health/safety risks independent of aesthetics.

```
CRITICAL SAFETY ISSUES:

Slip Hazards:
  ❌ Wet bathroom floor without mats → −2
  ❌ Slippery kitchen tile without runner → −1
  ❌ Stair without handrail → −2

Structural/Hygiene:
  ❌ Damaged non-stick coating (PTFE fumes) → −2
  ❌ Moldy drying area (no ventilation) → −2
  ❌ Blocked emergency exits → −3

Sharp Edges:
  ❌ Exposed corner edges (furniture) → −1
  ❌ Broken glass or sharp fixtures → −2

SCORING:
Critical safety issue found → −2 to −3 points (automatic)
Medium issue → −1 point
Minor issue → −0.5 point
```

### **LAYER 5: HOST PERSONALITY SIGNALS**

**Principle:** Details that show "I think about my guests' comfort."

```
HOSPITALITY SIGNALS (each +0.5 points):

Noise Control:
  ✅ Felt pads under chair legs → +0.5
  ✅ Rugs in living areas → +0.5

Surface Protection:
  ✅ Coaster set (visible, accessible) → +0.5
  ✅ Placemats for dining → +0.5
  ✅ Table runners → +0.25

Comfort Details:
  ✅ Extra pillows (beyond minimum) → +0.5
  ✅ Throws on sofa → +0.5
  ✅ Night light in bathroom → +0.25
  ✅ Nighttime safety lighting → +0.5

Organization:
  ✅ Labeled storage → +0.25
  ✅ Hangers all matching (not chaotic) → +0.5
  ✅ Drawer dividers → +0.25

Cleanliness Signals:
  ✅ Fresh welcome amenities (tea, coffee, snacks) → +0.5
  ✅ Cleaning supplies visible (not hidden) → +0.25
  ✅ Air freshener/ventilation → +0.25

SCORING:
Each signal → +0.5 max (or proportional)
Can add up to +3–4 bonus points for "exceptional hospitality mindset"

MISSING SIGNALS (penalty for apathy):
❌ Zero coasters (water rings inevitable) → −1
❌ Zero felt pads (acoustic discomfort) → −0.5
❌ Zero hooks/storage (clutter) → −1
```

---

## REVISED HIDDEN FRICTION SCORING (Dimension 7)

**Old system:** 42-item checklist, severity-based deductions  
**New system:** 42-item checklist + 5 layers (utility, duration, asymmetry, safety, personality)

### Scoring Breakdown
```
BASE HIDDEN FRICTION (0–20 points):
├── Utility Completeness (0–40 points, scaled to 8)
│   ├── Kitchen: 0–15 → scale to 5
│   ├── Bedroom: 0–15 → scale to 2
│   └── Bathroom: 0–10 → scale to 1
│
├── Quantity-Duration Matching (0–3 points)
│   └── Hangers, cookware, dishware scale by stay length
│
├── Asymmetry Detection (0–4 points deduction)
│   └── Flag mismatched pairs, unfair layouts
│
├── Safety Layer (0–3 points deduction)
│   └── Slip hazards, structural issues, hygiene risks
│
└── Host Personality (0–3 points bonus)
    └── Coasters, felt pads, hooks, welcome signals

TOTAL HIDDEN FRICTION SCORE = Base − Deductions + Bonus
(clamped to 0–20)

EXAMPLE (Rachel's Trion @ KL):
├── Utility completeness: 2/8 (terrible kitchen, asymmetrical bedroom)
├── Duration matching: −2 (3 hangers for 28-day stay)
├── Asymmetry: −2 (1 lamp + 2 guests)
├── Safety: 0 (no critical issues, but missing mats)
└── Personality: −3 (no coasters, no felt pads, no hooks)

TOTAL: 2 − 2 − 2 − 0 − 3 = −5 (clamped to 0)
Final Hidden Friction Score: 0/20 (F grade)
```

---

## UPDATED TEST CASE: RACHEL'S TRION @ KL

### Old System (Presence-based)
```
D1 (Bedroom): 14/20
D2 (Flow): 15/20
D3 (Light): 16/20
D4 (Storage): 12/20
D5 (Condition): 14/20
D6 (Photo): 7/10
D7 (Friction): 6/20 (only basic items counted)

Total: 84/150 = 56/100 (F)
```

### New System (Functionality-based)
```
D1 (Bedroom): 12/20 (asymmetry penalty: 1 lamp, 1 table for 2 guests)
D2 (Flow): 10/20 (low utility: beautiful but unusable)
D3 (Light): 16/20 (bright but asymmetrical)
D4 (Storage): 8/20 (no practical storage, only visual)
D5 (Condition): 18/20 (immaculate)
D6 (Photo): 9/10 (beautiful but misleading)
D7 (Friction): 0/20 (utility failures, asymmetry, personality gaps)

Total: 73/150 = 48.7/100 (F)
```

**Impact:** Score drops from 56→48 because framework now catches the "beautiful but broken" issue.

---

## IMPLEMENTATION PRIORITY

### Phase 2A (This week: Sat–Sun)
- [ ] Implement Layer 1 (Utility Completeness) for Kitchen, Bedroom, Bathroom
- [ ] Update Hidden Friction scoring with utility points
- [ ] Validate against Rachel's assessment (0/20 expected)

### Phase 2B (Mon–Tue)
- [ ] Implement Layer 2 (Duration Matching) — hangers scale by stay length
- [ ] Implement Layer 3 (Asymmetry Detection) — flag mismatched pairs
- [ ] Implement Layer 4 (Safety Layer) — slip hazards, structural issues

### Phase 2C (Tue–Wed)
- [ ] Implement Layer 5 (Host Personality) — bonus points for thoughtfulness
- [ ] Integrate all layers into Dimension 7 scoring
- [ ] Re-test Rachel's Airbnb (expect 48–51/100)
- [ ] Final QA before Wednesday launch

---

## SCORING LOGIC PSEUDOCODE (Python Implementation)

```python
class UtilityScorer:
    """Score functional completeness of property zones"""
    
    def score_kitchen_utility(property_data, stay_length):
        """Score kitchen functionality (0–15 points)"""
        score = 0
        
        # Cookware
        if property_data.pans >= 2 and not property_data.pan_damaged:
            score += 1
        else:
            score -= 2  # critical
        
        if property_data.knives >= 2 and property_data.cutting_board:
            score += 1
        else:
            score -= 1.5
        
        # Dishware (scale by guests)
        dishware_needed = property_data.guest_count + 1
        if property_data.plates >= dishware_needed:
            score += 1
        else:
            score -= 1
        
        # Pantry
        if property_data.oil and property_data.salt and property_data.sugar:
            score += 1.5
        else:
            score -= 1.5  # critical
        
        # Cleaning
        if property_data.paper_towels and property_data.drying_rack:
            score += 1.5
        else:
            score -= 1
        
        return max(0, min(15, score))
    
    def score_bedroom_utility(property_data, guest_count, stay_length):
        """Score bedroom functionality (0–15 points)"""
        score = 0
        
        # Lighting for 2+ guests
        if guest_count > 1:
            if property_data.bedside_lamps >= guest_count:
                score += 2
            else:
                score -= 2  # asymmetry penalty
            
            if property_data.end_tables >= guest_count:
                score += 2
            else:
                score -= 1.5  # asymmetry penalty
        
        # Hangers scale by duration
        if stay_length < 6:
            hanger_requirement = 5
        elif stay_length < 15:
            hanger_requirement = 10
        else:
            hanger_requirement = 15
        
        if property_data.hangers >= hanger_requirement:
            score += 2
        elif property_data.hangers >= hanger_requirement * 0.5:
            score += 0
        else:
            score -= 2
        
        # Storage
        if property_data.dresser and property_data.hamper:
            score += 2
        else:
            score -= 1
        
        return max(0, min(15, score))

class AsymmetryDetector:
    """Detect and penalize inequitable designs"""
    
    def check_bedroom_asymmetry(property_data, guest_count):
        """Flag mismatched pairs (1 lamp + N guests)"""
        penalties = 0
        
        if guest_count > 1:
            if property_data.bedside_lamps < guest_count:
                penalties += 2
            
            if property_data.end_tables < guest_count:
                penalties += 1.5
            
            if property_data.power_bars < 1:
                penalties += 1
        
        return penalties

class HostPersonalityScorer:
    """Score thoughtfulness and hospitality signals"""
    
    def score_host_signals(property_data):
        """Calculate bonus points for hospitality details"""
        bonus = 0
        
        # Noise control
        if property_data.felt_pads_under_furniture:
            bonus += 0.5
        
        # Surface protection
        if property_data.coaster_set_visible:
            bonus += 0.5
        if property_data.placemats:
            bonus += 0.5
        
        # Comfort details
        if property_data.extra_pillows:
            bonus += 0.5
        if property_data.throws_on_furniture:
            bonus += 0.5
        
        return bonus
```

---

## VALIDATION CHECKLIST

- [ ] Old system (presence-based) scores Rachel's property: 56/100
- [ ] New system (functionality-based) scores Rachel's property: 48–51/100
- [ ] Utility layers correctly identify kitchen as unusable (−10 pts)
- [ ] Duration matching penalizes 3 hangers for 28-day stay (−2 pts)
- [ ] Asymmetry detection flags 1 lamp + 2 guests (−2 pts)
- [ ] Host personality layer rewards thoughtfulness (coasters, felt pads)
- [ ] All 5 layers integrate into Dimension 7 (Hidden Friction) scoring
- [ ] Test cases pass (EMPTY BOX, Rachel's Airbnb)

---

## THE GOAL

Transform Design Diagnosis from:  
**"That's a beautiful property in photos"**

To:  
**"That's a functional, thoughtful property where I can actually live for a month."**

---

**Status:** 🎯 LOCKED FOR PHASE 2 IMPLEMENTATION  
**Prepared by:** Claude (post-refinement)  
**Date:** 2026-04-17 10:35 UTC  
**Impact:** This makes the app genuinely useful, not just photo-scoring.
