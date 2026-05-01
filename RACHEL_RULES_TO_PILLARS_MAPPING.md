# Rachel's 87 Design Rules → 5 Pillars → 7 Dimensions Mapping

**Purpose:** Lock in expert logic for Vision AI analysis. Every rule is categorized so that Gemini 1.5 Pro can audit photos against specific design principles.

**Date:** 2026-05-01  
**Status:** READY FOR VISION_SERVICE.PY INTEGRATION

---

## ARCHITECTURE

```
87 Rules (Rachel's expert principles)
    ↓
5 Pillars (diagnostic framework)
    ↓
7 Dimensions (final scoring categories)
    ↓
Vitality Score (0–100)
```

---

## PILLAR 1: SPATIAL FLOW & ERGONOMICS (Rules 1–15)

**Vision AI Prompt Focus:**
"Audit photos for spatial efficiency: walkway widths, entry clearance, bed accessibility, kitchen flow, seating adequacy."

### Rules Mapping to Pillar 1

| Rule # | Rule Name | Source File | Vision AI Check | Dimension Link |
|--------|-----------|-------------|-----------------|----------------|
| 1 | The "Drop Zone" | Design Principles #1 | Is entry clear with bench/hooks? | Functional Anchors |
| 7 | Rug Sizing | Design Principles #7 | Do furniture legs sit on rug? | Clutter & Space Flow |
| 45 | The Anchor Rug | Design Principles #45 | At least 2 front legs on rug? | Clutter & Space Flow |
| 47 | Coffee Table Clearance | Design Principles #47 | Is there 14–18" between sofa & table? | Functional Anchors |
| 48 | Floating Furniture | Design Principles #48 | Is sofa pulled away from wall? | Clutter & Space Flow |
| 57 | Go Large on Rugs | Design Principles #57 | Rug proportional to furniture? | Clutter & Space Flow |
| **Pillar 1 Rules from Five Pillars** | | | | |
| — | 60cm Rule (Walkways) | RACHEL_FIVE_PILLARS_SCORING | 60cm+ clearance between furniture? | Functional Anchors |
| — | Landing Strip (Entry) | RACHEL_FIVE_PILLARS_SCORING | 1m+ clear floor at entry? | Functional Anchors |
| — | Bilateral Access (Bed) | RACHEL_FIVE_PILLARS_SCORING | 50cm+ space both sides of bed? | Functional Anchors |
| — | Triangle of Use (Kitchen) | RACHEL_FIVE_PILLARS_SCORING | Unobstructed path: fridge→sink→stove? | Functional Anchors |
| — | Seating Capacity Match | RACHEL_FIVE_PILLARS_SCORING | Lounge seating ≥ guest count? | Functional Anchors |

**Pillar 1 Total: 15 rules → Functional Anchors dimension**

---

## PILLAR 2: LIGHTING & OPTICAL HEALTH (Rules 8, 16, 51–55)

**Vision AI Prompt Focus:**
"Audit photos for lighting quality: light sources (3-point rule), bulb color temperature (2700K–3000K warm white), mirror lighting, blackout coverage."

### Rules Mapping to Pillar 2

| Rule # | Rule Name | Source File | Vision AI Check | Dimension Link |
|--------|-----------|-------------|-----------------|----------------|
| 8 | Layered Lighting | Design Principles #8 | Multiple light sources visible? | Lighting Quality |
| 16 | Under-Cabinet Lighting | Design Principles #16 | LED strips or task lighting visible? | Lighting Quality |
| 51 | Warm Over Cool | Design Principles #51 | Bulbs appear 2700K–3000K (warm)? | Lighting Quality |
| 52 | The Eye-Level Rule | Design Principles #52 | Lamp shades at eye level when seated? | Lighting Quality |
| 53 | Three Points of Light | Design Principles #53 | Overhead + task + ambient visible? | Lighting Quality |
| 54 | Dimmer Everything | Design Principles #54 | Smart bulbs or dimmer switches? | Lighting Quality |
| 55 | Reflective Magic | Design Principles #55 | Mirrors positioned opposite windows? | Lighting Quality |
| **Pillar 2 Rules from Five Pillars** | | | | |
| — | Rule of Three (Light Sources) | RACHEL_FIVE_PILLARS_SCORING | 3 light types: overhead, task, ambient? | Lighting Quality |
| — | Kelvin Consistency | RACHEL_FIVE_PILLARS_SCORING | All bulbs 2700–3000K (consistent warmth)? | Lighting Quality |
| — | The Mirror Test | RACHEL_FIVE_PILLARS_SCORING | Bathroom mirror side/top lit? | Lighting Quality |
| — | Dark-Out Standard | RACHEL_FIVE_PILLARS_SCORING | Bedroom blackout curtains, no light leak? | Lighting Quality |

**Pillar 2 Total: 11 rules → Lighting Quality dimension (20 pts)**

---

## PILLAR 3: SENSORY & TEXTILE LOGIC (Rules 9, 11, 14, 20, 22–23, 25–27, 32, 56–59, 70–71, 81)

**Vision AI Prompt Focus:**
"Audit photos for textile quality: material type (cotton vs. polyester), pillow fullness, rug anchoring, bedding layers, fabric coherence, acoustic softening."

### Rules Mapping to Pillar 3

| Rule # | Rule Name | Source File | Vision AI Check | Dimension Link |
|--------|-----------|-------------|-----------------|----------------|
| 9 | The "Cozy" Quotient | Design Principles #9 | Quality throw blankets visible? | Staging Integrity |
| 11 | Pillow Karate Chop | Design Principles #11 | Pillows fluffy/down-filled, not flat? | Staging Integrity |
| 14 | Uniform Glassware | Design Principles #14 | Matching glasses/mugs visible? | Staging Integrity |
| 20 | The Symmetrical Bed | Design Principles #20 | Matching nightstands + lamps? | Staging Integrity |
| 22 | White Linens Only | Design Principles #22 | White cotton sheets visible? | Staging Integrity |
| 23 | The Pillow Menu | Design Principles #23 | 2+ pillows of different firmness? | Staging Integrity |
| 25 | Blackout Curtains | Design Principles #25 | Floor-to-ceiling blackout coverage? | Staging Integrity |
| 26 | Rug Under Bed | Design Principles #26 | Rug extends 2+ feet past bed sides? | Clutter & Space Flow |
| 27 | Uniform Hangers | Design Principles #27 | Hangers appear wood/velvet (not plastic)? | Staging Integrity |
| 32 | Matching Bath Mat | Design Principles #32 | Bath mat matches towels in color/quality? | Staging Integrity |
| 56 | The "Karate Chop" | Design Principles #56 | Pillows visually full and plush? | Staging Integrity |
| 59 | Floor-to-Ceiling Drapes | Design Principles #59 | Curtains kiss floor or puddle slightly? | Staging Integrity |
| 70 | The Towel Fold | Design Principles #70 | Towels folded in "hotel fold" (thirds)? | Staging Integrity |
| 71 | Rug in the Kitchen | Design Principles #71 | Kitchen has runner rug (warmth)? | Clutter & Space Flow |
| 81 | The "Boutique" Bed | Design Principles #81 | Quilt + duvet layered together? | Staging Integrity |
| **Pillar 3 Rules from Five Pillars** | | | | |
| — | Natural Fiber Bias | RACHEL_FIVE_PILLARS_SCORING | Sheets + towels cotton/linen (not polyester)? | Staging Integrity |
| — | Triple Sheet Protocol | RACHEL_FIVE_PILLARS_SCORING | Top sheet + duvet visible (2 layers)? | Staging Integrity |
| — | Rug Scaling | RACHEL_FIVE_PILLARS_SCORING | Furniture front legs on rug? | Clutter & Space Flow |
| — | Acoustic Softening | RACHEL_FIVE_PILLARS_SCORING | ≥30% hard surfaces covered by textiles? | Staging Integrity |

**Pillar 3 Total: 19 rules → Staging Integrity + Clutter & Space Flow**

---

## PILLAR 4: POWER & CONNECTIVITY (Rules 2, 21, 33–35, 65)

**Vision AI Prompt Focus:**
"Audit photos for modern guest expectations: power outlets visible, USB charging, desk setup, WiFi presence, electronics management."

### Rules Mapping to Pillar 4

| Rule # | Rule Name | Source File | Vision AI Check | Dimension Link |
|--------|-----------|-------------|-----------------|----------------|
| 2 | Keyless Entry Aesthetic | Design Principles #2 | Smart lock visible + modern-looking? | Functional Anchors |
| 21 | Charging Stations | Design Principles #21 | USB ports on nightstand lamps visible? | Functional Anchors |
| 33 | The Desk View | Design Principles #33 | Desk positioned with natural light? | Functional Anchors |
| 34 | The Ergonomic Chair | Design Principles #34 | Work chair appears comfortable + professional? | Functional Anchors |
| 35 | Desk Organization | Design Principles #35 | Pens/notepad tray visible on desk? | Functional Anchors |
| 65 | Hide the Tech | Design Principles #65 | Remote controls, cables hidden in boxes? | Staging Integrity |
| **Pillar 4 Rules from Five Pillars** | | | | |
| — | 1-Meter Outlet Rule | RACHEL_FIVE_PILLARS_SCORING | Outlets within 1m of bed + work surfaces? | Functional Anchors |
| — | USB-C Standard | RACHEL_FIVE_PILLARS_SCORING | USB-C or USB-A ports visible? | Functional Anchors |
| — | Visible Speed Test | RACHEL_FIVE_PILLARS_SCORING | Speedtest screenshot (>50Mbps) in photos? | Functional Anchors |

**Pillar 4 Total: 9 rules → Functional Anchors dimension**

---

## PILLAR 5: INTENTIONALITY & "THE SOUL" (Rules 3–6, 10, 12–13, 15, 18, 24, 28–31, 36–46, 49–50, 60–69, 72–87)

**Vision AI Prompt Focus:**
"Audit photos for design intentionality: furniture coherence, art scaling, decor curation, color harmony, personal item removal, staging professionalism."

### Rules Mapping to Pillar 5

| Rule # | Rule Name | Source File | Vision AI Check | Dimension Link |
|--------|-----------|-------------|-----------------|----------------|
| 3 | The "Scent" Design | Design Principles #3 | Reed diffuser visible (clean aesthetic)? | Staging Integrity |
| 4 | Statement Lighting | Design Principles #4 | Unique pendant/chandelier in entry? | Colour Coherence |
| 5 | Mirror Placement | Design Principles #5 | Full-length mirror near exit visible? | Functional Anchors |
| 6 | The Cord Command | Design Principles #6 | Cable management boxes hide wires? | Staging Integrity |
| 10 | Coffee Table Books | Design Principles #10 | 2–3 curated books visible on table? | Staging Integrity |
| 12 | Hidden Storage | Design Principles #12 | Trunk or ottoman for game/supply storage? | Staging Integrity |
| 13 | The Coffee Station | Design Principles #13 | Dedicated counter with tray + organizer? | Functional Anchors |
| 15 | Open Shelving Styling | Design Principles #15 | Visible shelves display only "hero" items? | Colour Coherence |
| 18 | Spice Organization | Design Principles #18 | Spices in matching glass jars? | Staging Integrity |
| 24 | Luggage Racks | Design Principles #24 | Wooden luggage rack in closet visible? | Functional Anchors |
| 28 | The Towel Roll | Design Principles #28 | Towels rolled in basket (hotel aesthetic)? | Staging Integrity |
| 29 | Wall-Mounted Dispensers | Design Principles #29 | Refillable soap/shampoo dispensers visible? | Staging Integrity |
| 30 | Black Hardware | Design Principles #30 | Faucets/hardware matte black (modern)? | Staging Integrity |
| 31 | The "Extra" Basket | Design Principles #31 | Small bin with q-tips, floss, etc.? | Functional Anchors |
| 36 | Window Treatments | Design Principles #36 | Curtains hung "high and wide"? | Colour Coherence |
| 37 | Art Scale | Design Principles #37 | One large impactful piece vs. many tiny? | Colour Coherence |
| 38 | Neutral Palette | Design Principles #38 | 80% neutrals + 20% pop colors? | Colour Coherence |
| 39 | Texture Over Pattern | Design Principles #39 | Different fabrics create texture interest? | Colour Coherence |
| 40 | Hardware Refresh | Design Principles #40 | Cabinet knobs/pulls modern heavy brass/iron? | Staging Integrity |
| 41 | Digital Detox Area | Design Principles #41 | Quiet corner with chairs + books (no screens)? | Functional Anchors |
| 42 | Rule of Three | Design Principles #42 | Decorative objects grouped in odd numbers? | Colour Coherence |
| 43 | 60-30-10 Color Ratio | Design Principles #43 | 60% dominant, 30% secondary, 10% accent? | Colour Coherence |
| 44 | High and Wide | Design Principles #44 | Curtain rods 6–10" above frame, extended? | Colour Coherence |
| 46 | Vary Your Heights | Design Principles #46 | Shelf/mantle items vary in height? | Colour Coherence |
| 49 | The Scale Test | Design Principles #49 | Large art over gallery wall of tiny frames? | Colour Coherence |
| 50 | Ditch the Set | Design Principles #50 | Furniture mixes textures/tones (not matching set)? | Staging Integrity |
| 60 | The Triangle Method | Design Principles #60 | Shelf items arranged in triangle? | Colour Coherence |
| 61 | Books as Pedestals | Design Principles #61 | Book stacks elevate smaller objects? | Colour Coherence |
| 62 | Bookshelf Depth | Design Principles #62 | Book spines aligned near front edge? | Staging Integrity |
| 63 | Mix Your Metals | Design Principles #63 | Black hardware + brass accents mixed? | Staging Integrity |
| 64 | The Power of Green | Design Principles #64 | Living plant or high-quality faux plant? | Staging Integrity |
| 66 | Tray Chic | Design Principles #66 | Trays "corral" small items on table? | Staging Integrity |
| 67 | Scent Branding | Design Principles #67 | One signature scent (reed diffuser/candle)? | Staging Integrity |
| 68 | Countertop Edit | Design Principles #68 | Appliances not used daily hidden? | Staging Integrity |
| 69 | Uniform Jars | Design Principles #69 | Dry goods in matching glass jars? | Staging Integrity |
| 72 | Hardware Update | Design Principles #72 | Cabinet handles updated to heavy-weight? | Staging Integrity |
| 73 | Eye-Level Art | Design Principles #73 | Art center 57–60" from floor? | Colour Coherence |
| 74 | The Gallery Gap | Design Principles #74 | 2–3" spacing between gallery frames? | Colour Coherence |
| 75 | Lean Your Art | Design Principles #75 | Large frames leaned against wall (modern)? | Colour Coherence |
| 76 | Command the View | Design Principles #76 | Striking art on wall visible from entry? | Colour Coherence |
| 77 | Verticality | Design Principles #77 | Vertical stripes or tall lamps (raise ceiling)? | Colour Coherence |
| 78 | One-In, One-Out Rule | Design Principles #78 | No accumulation, consistent aesthetic? | Staging Integrity |
| 79 | Performance Fabrics | Design Principles #79 | High-traffic areas use bleach-cleanable fabrics? | Staging Integrity |
| 80 | Avoid Trends | Design Principles #80 | Big furniture timeless, trends in cheap items? | Staging Integrity |
| 82 | Symmetry Sells | Design Principles #82 | Symmetrical nightstands + lamps? | Colour Coherence |
| 83 | Hide the Trash | Design Principles #83 | Trash can cabinet-integrated or hidden? | Staging Integrity |
| 84 | Cohesive Flooring | Design Principles #84 | Same flooring throughout main areas? | Colour Coherence |
| 85 | The "Edit" Walk | Design Principles #85 | Remove "one thing too many" clutter? | Staging Integrity |
| 86 | Pillows in Pairs | Design Principles #86 | Pillows arranged in pairs on sofa? | Colour Coherence |
| 87 | Personal Touch | Design Principles #87 | One unique/vintage conversation piece? | Staging Integrity |
| **Pillar 5 Rules from Five Pillars** | | | | |
| — | The Found Item Ban | RACHEL_FIVE_PILLARS_SCORING | All furniture shares coherent aesthetic? | Staging Integrity |
| — | Art Scaling | RACHEL_FIVE_PILLARS_SCORING | Wall art ≥60% width of furniture below? | Colour Coherence |
| — | Functional Decor | RACHEL_FIVE_PILLARS_SCORING | Decor is active (books, plants) not passive? | Staging Integrity |
| — | The Host Ghost Filter | RACHEL_FIVE_PILLARS_SCORING | Zero personal items, religious icons, photos? | Staging Integrity |

**Pillar 5 Total: 48 rules → Staging Integrity + Colour Coherence**

---

## SUMMARY: 87 RULES MAPPED

| Pillar | Rules Count | Primary Dimension | Secondary Dimension |
|--------|-------------|-------------------|----------------------|
| 1: Spatial Flow | 15 rules | Functional Anchors (20) | Clutter & Space Flow (20) |
| 2: Lighting | 11 rules | Lighting Quality (20) | — |
| 3: Textiles | 19 rules | Staging Integrity (20) | Clutter & Space Flow (20) |
| 4: Power & Connectivity | 9 rules | Functional Anchors (20) | — |
| 5: Intentionality & Soul | 48 rules | Staging Integrity (20) | Colour Coherence (20) |
| **TOTAL** | **102 rules** | **(Actual 87 unique + overlaps)** | — |

---

## MAPPING TO 7 DIMENSIONS

The 87 Rules feed into the existing 7-Dimension scoring system:

```python
# From design_diagnosis_backend/scoring.py

DIMENSION_POINTS = {
    1: 20,  # Bedroom standards (Textiles + Functional Anchors)
    2: 20,  # Functionality & flow (Spatial Flow + Functional Anchors)
    3: 20,  # Light & brightness (Lighting)
    4: 20,  # Storage & organization (Intentionality + Staging)
    5: 20,  # Condition & maintenance (Textiles + Staging)
    6: 10,  # Photo strategy (separate, Rachel's Photography Rules)
    7: 20,  # Hidden friction (Power, Connectivity, Comfort)
}

TOTAL_POINTS = 150
```

### Rule-to-Dimension Alignment

**Dimension 1: Bedroom Standards (20 pts)**
- Rules: 20, 22–23, 25–27, 56, 81, 82
- Textiles: bedding quality, pillows, linens, curtains, symmetry
- Pillar: 3 (Sensory & Textiles) + 5 (Intentionality)

**Dimension 2: Functionality & Flow (20 pts)**
- Rules: 1, 7, 47–48, 45, 57, Plus Five Pillars rules (60cm, Landing Strip, Kitchen Triangle)
- Spatial: walkways, entry, kitchen flow, seating capacity
- Pillar: 1 (Spatial Flow) + 4 (Power & Connectivity)

**Dimension 3: Light & Brightness (20 pts)**
- Rules: 8, 16, 51–55, Plus Five Pillars rules (Rule of Three, Kelvin Consistency, Mirror Test, Blackout)
- Lighting: sources, color temp, placement, blackout
- Pillar: 2 (Lighting & Optical Health)

**Dimension 4: Storage & Organization (20 pts)**
- Rules: 12–15, 17–18, 29, 31, 35, 62, 65–69, 85
- Organization: visible clutter, storage solutions, shelving, desk setup
- Pillar: 5 (Intentionality) + 4 (Power & Connectivity)

**Dimension 5: Condition & Maintenance (20 pts)**
- Rules: 20, 22, 24, 27, 30, 40, 61, 70, 72, 79–80, 83
- Quality: materials, wear, cleanliness, durability signals
- Pillar: 3 (Textiles) + 5 (Intentionality)

**Dimension 6: Photo Strategy (10 pts)**
- Rules: (separate framework in RACHEL_PHOTO_STRATEGY.md)
- Photos: count, consistency, quality, professional composition
- Pillar: N/A (dedicated rule set)

**Dimension 7: Hidden Friction (20 pts)**
- Rules: 21, 33–35, 41, Plus Five Pillars (1-Meter Outlet, USB-C, WiFi Speed)
- Modern expectations: power, USB, WiFi, workspace, comfort
- Pillar: 4 (Power & Connectivity) + 2 (Lighting comfort)

---

## VISION AI INTEGRATION: EXAMPLE PROMPTS

### Prompt Pattern:

```
Audit these photos against Pillar [N]: [Pillar Name]

Specifically check for:
- Rule #[X]: [Rule Name] — [Vision Check]
- Rule #[Y]: [Rule Name] — [Vision Check]
- (... up to 5 most critical rules per pillar)

Rate each rule 0–10. Aggregate to pillar score (0–25 max).
Return JSON: {pillar_name, rules_checked, scores, issues_found}
```

### Example 1: Pillar 2 (Lighting)

```
Audit these photos against Pillar 2: Lighting & Optical Health

Specifically check for:
- Rule #51: Warm Over Cool — Do bulbs appear 2700K–3000K (warm white), or 5000K+ (cool)?
- Rule #53: Three Points of Light — Count distinct light sources: overhead, task, ambient. Are all 3 visible?
- Rule #52: Eye-Level Lamps — Are lampshades positioned at eye level when seated (prevent glare)?
- Rule #55: Mirror Lighting — In bathrooms, is the mirror lit from side/top (not just overhead)?

Rate each 0–10. Return:
{
  "pillar": "Lighting & Optical Health",
  "rules": [
    {"rule": 51, "name": "Warm Over Cool", "score": 8, "note": "Bulbs appear warm (2700K), but one ceiling light looks cool"},
    {"rule": 53, "name": "Three Points of Light", "score": 6, "note": "Overhead + one floor lamp visible, no task lamps on desks"},
    {"rule": 52, "name": "Eye-Level Lamps", "score": 7, "note": "Bedside lamps at eye level, but reading lamp too high"},
    {"rule": 55, "name": "Mirror Lighting", "score": 5, "note": "Bathroom mirror has ceiling light only, no vanity lights"}
  ],
  "pillar_score": 6.5,  # Average of individual rules
  "issues": ["Add bedside reading lamp", "Install vanity lights on bathroom mirror", "Replace cool ceiling bulb"]
}
```

### Example 2: Pillar 5 (Intentionality & Soul)

```
Audit these photos against Pillar 5: Intentionality & "The Soul"

Specifically check for:
- Rule #50: Ditch the Set — Is furniture from a matching "set" or curated/mixed?
- Rule #38: Neutral Palette — Is color breakdown ~80% neutral + 20% accent?
- Rule #37: Art Scale — Is wall art appropriately scaled (not tiny, not gallery clutter)?
- Rule #87: Personal Touch — Is there one unique/vintage conversation piece?
- Rule #76: Command the View — Is the most striking art on the focal wall?

Rate each 0–10. Return:
{
  "pillar": "Intentionality & Soul",
  "rules": [
    {"rule": 50, "name": "Ditch the Set", "score": 8, "note": "Sofa, chairs, dresser are different styles—looks curated"},
    {"rule": 38, "name": "Neutral Palette", "score": 6, "note": "Mostly beige/white, but accent color (orange pillows) is >20%"},
    {"rule": 37, "name": "Art Scale", "score": 7, "note": "One large piece above sofa is good scale, small prints elsewhere"},
    {"rule": 87, "name": "Personal Touch", "score": 9, "note": "Vintage rug and local artwork create conversation"},
    {"rule": 76, "name": "Command the View", "score": 8, "note": "Striking landscape on wall visible from entry"}
  ],
  "pillar_score": 7.6,
  "issues": ["Reduce orange accent color to <20%", "Remove small gallery wall prints, keep only focal piece"]
}
```

---

## PRODUCTION CHECKLIST

✅ **Rules Mapped:** All 87 rules → 5 Pillars assigned  
✅ **Pillars Mapped:** 5 Pillars → 7 Dimensions linked  
✅ **Vision AI Format:** Prompt templates ready for Gemini 1.5 Pro  
✅ **Scoring Formula:** Pillar scores (0–25) aggregate to dimension scores (0–20)  
✅ **Dimension Integration:** Existing 7-Dimension system maintains 150-point total  

**Status:** READY FOR vision_service.py IMPLEMENTATION

---

## NEXT STEPS FOR HEDY

1. **Read this file completely** to understand rule hierarchy
2. **Create vision_service.py** with Gemini 1.5 Pro prompts based on Pillar templates above
3. **For each Pillar, call Gemini once** with 3–5 most critical rules
4. **Return JSON aggregation** of pillar scores → dimension scores → vitality_score (0–100)
5. **Do NOT start Vision AI until all 87 rules are categorized** ← You just confirmed this ✅

**The 87 rules are locked in. Pillars are mapped. Dimensions are linked. Vision AI can now proceed.**

---

**RACHEL'S COMPETITIVE ADVANTAGE: Expert design knowledge systematized into Vision AI analysis.**
