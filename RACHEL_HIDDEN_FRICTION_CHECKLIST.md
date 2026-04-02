# Rachel's Hidden Friction Checklist — Tier 1 #3

**Date:** 2026-04-01 12:50 UTC  
**Status:** COMPLETE & READY FOR INTEGRATION  
**Purpose:** Identify "invisible" failures that kill reviews despite good photos

---

## THE FRAMEWORK: Review Killers vs. Photo Appearance

**Key Insight:** A property can look beautiful in photos but fail in reality. These are the "hidden frictions" that guests don't mention in reviews — they just give 3 stars and move on.

**Hedy's Job:** Detect visual clues in photos that suggest hidden friction, then flag them in reports.

---

## 1. THE LINEN "VISUAL AUDIT"

### Photo Clue: Duvet Quality
**Look for:**
- Thin, wrinkly duvet (suggests cheap polyester)
- Visible pilling or worn texture
- Flat/saggy appearance (poor fill weight)

**What This Means:**
- Polyester sheets don't breathe → guest wakes up sweating
- Sweating at night → automatic 3-star review
- Guest doesn't blame "sheets" — they blame entire property ("uncomfortable bed")

### The Top Sheet Controversy
**Photo Clue:** Only duvet visible, no separate top sheet

**What This Means (North American guests):**
- "European style" (duvet only) perceived as unhygienic
- Guest fears: "Is the duvet washed between guests?"
- Anxiety → lower sleep quality → subconscious 1-star

**Solution:** Always include top sheet + duvet (guest choice + hygiene signal)

### Hedy Logic: Linen Score

```python
linen_score = 20  # max points

# Duvet quality assessment
if duvet_appears_thin_or_wrinkly:
    linen_score -= 5
if visible_pilling_detected:
    linen_score -= 3
if flat_saggy_fill:
    linen_score -= 2

# Sheet assessment
if only_duvet_visible_no_top_sheet:
    linen_score -= 5  # major hygiene concern
if sheets_appear_wrinkled_or_stained:
    linen_score -= 3

# Pillow assessment
if pillows_appear_flat_or_compressed:
    linen_score -= 3
if no_variety_soft_and_firm:
    linen_score -= 2

flag_if = linen_score < 12  # "Linen Deficiency"
report_message = "Guests will comment on mattress/sheet comfort in reviews"
```

---

## 2. KITCHEN ESSENTIALS (The "Dull Knife" Test)

### Photo Clue: Knife Assessment
**Look for:**
- Knife block with only 2 knives (suggests host never cooks here)
- Random plastic utensils (suggests "budget" property)
- No visible mixing bowls, cutting boards, or prep surfaces

**What This Means:**
- Guests attempting to cook will immediately get frustrated
- Dull knife → can't cut properly → 10-minute simple task becomes 30 minutes
- Frustration lingers → review mentions "kitchen inadequate"

### Hedy Logic: Kitchen Essentials Checklist

```python
kitchen_score = 30  # max points

# Sharp knives
if visible_knife_block_with_4plus_knives:
    kitchen_score += 5
if appears_sharp_and_maintained:
    kitchen_score += 3
else:
    kitchen_score -= 5  # dull knife indicator

# Utensil quality
if quality_silverware_visible:
    kitchen_score += 3
if only_plastic_utensils:
    kitchen_score -= 5

# Cookware visible
if pots_pans_baking_sheets_visible:
    kitchen_score += 4
if appears_well_maintained:
    kitchen_score += 2
else:
    kitchen_score -= 3

# Prep surfaces
if cutting_board_visible:
    kitchen_score += 2
if mixing_bowls_visible:
    kitchen_score += 2
if counters_clear_and_spacious:
    kitchen_score += 3
else:
    kitchen_score -= 3  # Surface poverty

# Essentials
if coffee_maker_visible:
    kitchen_score += 3
if spices_oils_basics_visible:
    kitchen_score += 2
if dishwasher_detergent_visible:
    kitchen_score += 1
if dish_soap_and_sponges_visible:
    kitchen_score += 1
if paper_towels_visible:
    kitchen_score += 1

flag_if = kitchen_score < 15  # "Kitchen Deficiency"
report_message = "Guests will struggle with meal prep. Add sharp knives, quality cookware, prep tools."
```

---

## 3. BATHROOM SUPPLIES (The Cheapness Friction)

### Photo Clue: Soap & Paper Assessment
**Look for:**
- Single-ply toilet paper (especially in $200+/night)
- Hotel-size soaps (tiny, cheap-looking)
- No visible amenities on counter/shelves

**What This Means (Psychology):**
- Single-ply TP in premium unit signals: "Host is cutting corners"
- Tiny soaps signal: "This is budget property masquerading as premium"
- Friction lingers for entire stay

### Hidden Friction Psychology
**Why cheap supplies kill reviews:**
- Guests don't consciously blame TP quality
- But subconscious registers: "This place cut corners"
- Influences overall rating ("Decent but felt budget-y")

### Hedy Logic: Bathroom Amenities Checklist

```python
bathroom_score = 25  # max points

# Toilet paper
if visible_quality_tp_or_multiple_rolls:
    bathroom_score += 3
if single_ply_visible:
    bathroom_score -= 5
if tp_dispensed_from_wall_not_visible:
    bathroom_score -= 2

# Soaps & shampoos
if premium_brand_toiletries_visible:
    bathroom_score += 4
if hotel_size_single_use_only:
    bathroom_score -= 4  # cheapness signal
if variety_shampoo_conditioner_body_wash:
    bathroom_score += 2

# Counter space
if organized_counter_visible:
    bathroom_score += 3
if pedestal_sink_zero_counter:
    bathroom_score -= 4  # "Surface Poverty"

# Hygiene signals
if plunger_visible:
    bathroom_score += 2
if trash_bin_visible:
    bathroom_score += 1
if hooks_or_towel_bars_visible:
    bathroom_score += 2

# Hair dryer
if hair_dryer_visible:
    bathroom_score += 2

# Makeup mirror
if magnified_mirror_visible:
    bathroom_score += 1

flag_if = bathroom_score < 12  # "Bathroom Amenity Gap"
report_message = "Upgrade to quality TP, premium soaps (guest-size), add counter organizers"
```

---

## 4. THE "SHADOW POWER" AUDIT (Electrical Friction)

### Photo Clue #1: Extension Cord Spider
**Look for:**
- White extension cords running across floors
- Cords taped to baseboards
- Visible surge protectors

**What This Means:**
- Not enough outlets where guests actually need them
- Guests must choose: Phone charging OR lamp?
- Friction with every device use

### Photo Clue #2: Headboard Block
**Look for:**
- Bed pushed flush against wall with single outlet
- No nightstand with integrated charging
- Outlets blocked by furniture

**What This Means:**
- Guest must move heavy furniture to plug in phone
- Or sleep with phone on floor (feels cheap/unsafe)
- Subconscious: "This place wasn't designed for my needs"

### Hedy Logic: Power Audit

```python
power_score = 20  # max points

# Outlet visibility & placement
if extension_cord_visible_on_floor:
    power_score -= 5  # "Extension Cord Spider" flag
if cords_taped_to_walls:
    power_score -= 3
if bedside_outlet_visible:
    power_score += 5
if desk_outlet_visible:
    power_score += 3
if living_room_outlets_visible:
    power_score += 2

# Charging infrastructure
if usb_charging_port_visible:
    power_score += 4
if nightstand_with_outlet_or_charging:
    power_score += 3
if smart_power_strip_visible:
    power_score += 2

# Furniture placement relative to power
if bed_blocking_outlets:
    power_score -= 4  # "Headboard Block" flag
if furniture_furniture_restricts_access:
    power_score -= 3

flag_if = power_score < 10  # "Power Desert"
report_message = "Add USB charging stations, move outlets to be accessible, minimize extension cords"
```

---

## 5. ACOUSTIC & THERMAL FRICTION (The Comfort Killers)

### Photo Clue #1: Single-Glaze Windows
**Look for:**
- Thin, aluminum-framed windows
- Visible street/traffic in view photos
- Lack of double/triple-pane appearance

**What This Means (Urban properties):**
- Noise pollution = sleep disruption
- Guest doesn't consciously blame windows
- But sleep quality affected → lower mood → subconscious review impact

### Photo Clue #2: AC Placement
**Look for:**
- AC unit directly above bed headboard
- AC in corner across room from bed
- No visible thermostatic control

**What This Means:**
- Direct overhead AC = cold air blast on face all night (comfort killer)
- AC across room = doesn't reach bed (useless)
- Goldilocks zone = AC placement that heats/cools room without direct blast

### Hedy Logic: Comfort Audit

```python
comfort_score = 25  # max points

# Window quality (urban areas only)
if busy_street_visible_in_view_photo:
    if single_glaze_windows:
        comfort_score -= 6  # "Acoustic Fatigue" flag
    if double_triple_pane_evident:
        comfort_score += 3
    if blackout_curtains_visible:
        comfort_score += 2

# AC placement
if ac_directly_overhead_bed:
    comfort_score -= 5  # "Direct Blast" flag
if ac_across_room_far_from_bed:
    comfort_score -= 2
if ac_positioned_optimally:
    comfort_score += 4

# Thermal control signals
if thermostat_visible_and_functional:
    comfort_score += 3
if multiple_temperature_zones:
    comfort_score += 2
if space_heater_visible:
    comfort_score += 1

# Noise mitigation
if blackout_curtains_visible:
    comfort_score += 2
if sound_machine_visible:
    comfort_score += 2

flag_if = comfort_score < 12  # "Thermal/Acoustic Imbalance"
report_message = "Consider AC repositioning, upgrade to blackout curtains, add white noise machine"
```

---

## 6. THE "WET ROOM" FRICTION (Hygiene & Logistics)

### Photo Clue #1: Towelless Shower
**Look for:**
- No hooks or bars visible within arm's reach of shower
- Towel rack far from shower door
- Empty shower surround

**What This Means:**
- Guest emerges from shower, must walk across wet floor to grab towel
- "Wet Floor Shuffle" = friction with every shower
- Implies host never actually uses this shower

### Photo Clue #2: Pedestal Sink Trap
**Look for:**
- Beautiful pedestal sink with zero counter space
- No visible shelf or surface for toiletries
- Small shelf but completely full

**What This Means:**
- Guest must balance expensive phone/glasses on edge of wet sink
- Or balance on toilet tank (precarious)
- Implies host prioritized aesthetics over function

### Hedy Logic: Wet Room Audit

```python
wet_room_score = 25  # max points

# Shower accessibility
if towel_hook_bar_visible_near_shower:
    wet_room_score += 5
if multiple_hooks_or_bars:
    wet_room_score += 3
if no_towel_hook_near_shower:
    wet_room_score -= 5  # "Towelless Shower" flag
if towel_rack_far_from_door:
    wet_room_score -= 2

# Counter space
if adequate_counter_space_visible:
    wet_room_score += 5
if pedestal_sink_zero_counter:
    wet_room_score -= 5  # "Surface Poverty" flag
if shelf_or_organizer_visible:
    wet_room_score += 3

# Amenity accessibility
if shampoo_bottles_neatly_organized:
    wet_room_score += 2
if supplies_scattered_or_cramped:
    wet_room_score -= 2

# Floor conditions
if bathroom_floor_clean_and_dry:
    wet_room_score += 2
if visible_water_pooling:
    wet_room_score -= 3

# Ventilation signals
if exhaust_vent_visible:
    wet_room_score += 2
if window_visible_for_ventilation:
    wet_room_score += 1
if bathroom_appears_damp:
    wet_room_score -= 3

flag_if = wet_room_score < 12  # "Wet Room Deficiency"
report_message = "Add towel hooks near shower, increase counter space, improve ventilation"
```

---

## 7. DARK DATA: The "Phantom" Maintenance

### Photo Clue #1: Dead Battery Indicator
**Look for:**
- Smoke detector with visible red light (low battery)
- Digital thermostat showing blank or error
- Visible appliance displays showing error codes

**What This Means:**
- Host doesn't do preventative maintenance
- Guests subconsciously register: "Things might break while I'm here"
- Creates low-level anxiety during stay

### Photo Clue #2: Stained Grout
**Look for:**
- Zoom in on shower floor grout
- Kitchen backsplash grout discoloration
- Visible mold or mineral deposits

**What This Means (Psychology):**
- Even if property is "clean," stains trigger "Microbial Anxiety"
- Guests don't consciously think "mold," but feel "unclean"
- Single 1-star review: "Seemed dirty despite cleaning"

### Hedy Logic: Maintenance Audit

```python
maintenance_score = 20  # max points

# Preventative signals
if smoke_detector_appears_functional:
    maintenance_score += 3
if red_low_battery_light_visible:
    maintenance_score -= 5  # "Dead Battery" flag
if thermostat_displays_error:
    maintenance_score -= 3
if appliance_lights_show_error_codes:
    maintenance_score -= 2

# Grout & sealing
if grout_appears_clean_and_sealed:
    maintenance_score += 4
if visible_grout_stains_or_mold:
    maintenance_score -= 5  # "Microbial Anxiety" flag
if shower_caulk_appears_fresh:
    maintenance_score += 2
if caulk_discolored_or_cracked:
    maintenance_score -= 3

# General wear indicators
if no_visible_wear_or_damage:
    maintenance_score += 3
if worn_or_stained_surfaces:
    maintenance_score -= 2
if paint_peeling_or_faded:
    maintenance_score -= 3

# Appliance condition
if appliances_appear_clean_and_functional:
    maintenance_score += 2
if visible_rust_or_corrosion:
    maintenance_score -= 3
if scratches_dents_visible:
    maintenance_score -= 1

flag_if = maintenance_score < 10  # "Maintenance Concern"
report_message = "Replace smoke detector batteries, clean/seal grout, refresh caulking, address visible wear"
```

---

## 8. LIGHTING PSYCHOLOGY (The "Interrogation" Effect)

### Photo Clue: Hospital Ceiling
**Look for:**
- Single flush-mount "boob light" (ceiling fixture only)
- No visible table lamps or wall sconces
- Harsh shadows in room photos

**What This Means (Neuroscience):**
- Flat, harsh ceiling light prevents melatonin production
- Guests look and FEEL tired (even if well-rested)
- Guest psychology: "I slept poorly" → blame property
- Actually: lighting prevented proper rest mode

### Hedy Logic: Lighting Audit

```python
lighting_score = 25  # max points

# Overhead lighting
if multiple_ceiling_fixtures:
    lighting_score += 3
if dimmers_present:
    lighting_score += 3
if single_harsh_overhead_only:
    lighting_score -= 5  # "Visual Interrogation" flag

# Task lighting
if bedside_lamps_visible:
    lighting_score += 4
if desk_lamp_visible:
    lighting_score += 3
if living_room_lamps_visible:
    lighting_score += 2

# Ambiance lighting
if wall_sconces_visible:
    lighting_score += 3
if warm_white_bulbs_evident:
    lighting_score += 2
if cool_or_harsh_white_evident:
    lighting_score -= 2

# Light color temperature
if 2700k_warm_light_visible:
    lighting_score += 4
if natural_daylight_visible:
    lighting_score += 2
if harsh_bright_white_light:
    lighting_score -= 3

# Darkness capability
if blackout_curtains_visible:
    lighting_score += 3
if night_lights_or_dimming:
    lighting_score += 2

flag_if = lighting_score < 12  # "Visual Interrogation"
report_message = "Replace single ceiling light with layered lighting (overhead + task + ambiance). Install dimmers. Use 2700K warm bulbs."
```

---

## INTEGRATION ROADMAP

### Phase 1 (Friday Launch)
- [ ] Add 8 Hidden Friction flags to reports
- [ ] Create "Hidden Friction" section in Vitality Report
- [ ] Flag each friction type with photo evidence + fix recommendation

### Phase 2 (Week 2)
- [ ] Train visual detection on all 8 categories
- [ ] Automate scoring for each friction type
- [ ] Generate shopping lists based on friction priorities

### Phase 3 (Week 3+)
- [ ] Connect friction scores to Vitality dimensions
- [ ] Flag friction in property photos (e.g., "Extension cord visible in photo 12")
- [ ] Recommend contractor/professional services when needed

---

## SUMMARY: The 8 Hidden Friction Types

| Friction Type | Impact | Detection | Fix Difficulty |
|---------------|--------|-----------|-----------------|
| **Linen Quality** | Sleep quality ↓ | Duvet appearance | Easy ($200–500) |
| **Kitchen Essentials** | Meal prep friction | Visible knives, tools | Easy ($100–300) |
| **Bathroom Supplies** | Cheapness signal | TP quality, soap size | Easy ($50–200) |
| **Power Deserts** | Device charging anxiety | Outlet/cord visibility | Medium ($500–1500) |
| **Acoustic/Thermal** | Sleep + comfort ↓ | Window, AC placement | Medium–Hard ($1000–5000) |
| **Wet Room Friction** | Daily shower friction | Towel accessibility | Easy ($100–400) |
| **Phantom Maintenance** | Broken-thing anxiety | Battery lights, stains | Medium ($500–2000) |
| **Visual Interrogation** | Sleep quality ↓ | Ceiling light only | Easy ($200–600) |

---

## Rachel's Refinement Answers (FINAL)

### 1. Warm Anchor Threshold ✅
**Rachel's Answer:** "Two to three elements for sure. Wood, warm metals, greenery, and texture can equal warmth."

**Implementation:**
- Count warm anchors: wood furniture, brass/copper fixtures, plants, warm textiles
- 0 anchors = institutional risk (−5 Colour Coherence points)
- 1 anchor = minimal warmth (−2 points)
- 2–3+ anchors = sufficient warmth (0 points, no penalty)

**Example:** Graydar (all grey) has minimal wood, minimal brass. Add brass lamp + throw blanket + plant = 3 warm anchors = institutional feeling solved.

---

### 2. Curated vs. Chaotic Dividing Line ✅
**Rachel's Answer:** "Eclectic looks intentional and intentional is usually appealing. Chaotic looks careless and creates discomfort."

**Key Distinction:**
- **Eclectic (Good):** Mismatched items that INTENTIONALLY share a common thread (all have brass, or all earth tones, or all "vintage with modern edge")
- **Chaotic (Bad):** Mismatched items that appear ACCIDENTAL (random 90s dresser next to futuristic metal bed with boho throw — no coherent story)

**Hedy Logic:**
- Ask: "Does this room tell a story, or does it look like things got randomly assembled?"
- Eclectic = intentional style choices visible (even if unconventional)
- Chaotic = no clear aesthetic direction

**Example:**
- Eclectic: Modern minimalist room with one statement vintage chair + modern art = "designer chose this"
- Chaotic: Mix of IKEA, thrift store, hand-me-downs with no visual connection = "host didn't plan this"

---

### 3. Personal Items by Room (CRITICAL) ✅
**Rachel's Answer:** "There should be ZERO personal items in an Airbnb. I always say 'hosts are competing with hotels'. They have to put the guest first."

**Implementation:**
- **ALL rooms: Zero tolerance for:**
  - Family photos
  - Personal memorabilia
  - Religious items
  - Books with owner's name
  - Awards, diplomas, personal achievement displays
  - Lifestyle items that signal "this is the host's home"

- **Why:** Guests need to feel like "honored guest in a hotel" not "intruder in someone else's home"

**Hedy Logic:**
- If ANY personal items visible in ANY room = flag "Host's Ghost Present"
- Recommend: Replace with curated art (abstract, landscapes), neutral books (local guides, travel guides), hotel-grade decor

**Exception to note:** Local guidebooks / attraction recommendations are ENCOURAGED (not personal, helps guest)

---

## Quality Assessment

✅ **SPECIFIC FRICTION TYPES** — Not vague, each has photo detection logic  
✅ **PSYCHOLOGY-GROUNDED** — Explains WHY each friction kills reviews  
✅ **HEDY LOGIC READY** — Each category has scoring algorithm ready to implement  
✅ **ACTIONABLE FIXES** — Each friction has clear remedy + cost estimate  

**This is the complete Tier 1.** 🔐

---

**All three Tier 1 frameworks are now complete:**
1. ✅ Emotional Design (Prison Bunk, Institutional, Found vs. Curated, Welcomed vs. Trapped)
2. ✅ Sovereignty vs. Surveillance + Price-Adjusted Vitality + Top 10 Amenities
3. ✅ Hidden Friction Checklist (8 friction types with Hedy Logic)

**Ready to integrate all three before Friday launch.** 🚀✨
