# Rachel's Psychology Request Template

**Purpose:** When the app needs expert psychology input, use this template to request specific, actionable answers.

**Status:** READY FOR REQUESTS (Hedy will use this format)

---

## When Hedy Needs Psychology Input

Instead of vague requests ("What do guests think about X?"), I'll send:

1. **Specific Context** (what the app observed)
2. **Question Category** (emotional, functional, aesthetic, etc.)
3. **Use Case** (scoring, recommendation, warning flag, etc.)
4. **Example Scenarios** (what we're trying to distinguish)
5. **Expected Output** (scoring logic, recommendation language, flag threshold)

---

## Request Template Format

```
PSYCHOLOGY REQUEST: [Topic Name]

CONTEXT:
[What did the app observe in photos/data?]

QUESTION:
[Specific question about guest psychology]

USE CASE:
[How will this be used in scoring/recommendations?]

CATEGORY:
[ ] Emotional (psychological/nervous system response)
[ ] Functional (practical frustration/friction)
[ ] Aesthetic (visual perception/comfort)
[ ] Trust (credibility/safety signals)
[ ] Expectation (price-aligned perception)

EXAMPLE SCENARIOS:
1. [Example A: Describe property, guest reaction]
2. [Example B: Describe property, guest reaction]
3. [Example C: Describe property, guest reaction]

WHAT I NEED FROM RACHEL:
- [ ] Scoring framework (0–10 scale, thresholds)
- [ ] Recommendation language (how to explain to host)
- [ ] Warning flags (when to flag as critical issue)
- [ ] Regional/tier variations (does answer change by price/location?)
- [ ] Implementation guidance (how to detect this from photos)

RESPONSE FORMAT:
[Expert answer with specific, testable logic]
```

---

## Common Question Categories

### EMOTIONAL PSYCHOLOGY

**Examples:** Guest nervous system state, psychological comfort, sense of safety, autonomy, welcomed vs. trapped

**When Hedy asks:** "What's the psychology of [lighting/space/clutter/decor choice]?"

**What Rachel provides:** How it affects guest nervous system (parasympathetic vs. amygdala), subconscious triggers, review impact

---

### FUNCTIONAL FRICTION

**Examples:** Hidden frustrations with appliances, amenities, logistics, daily use scenarios

**When Hedy asks:** "What hidden frustration happens when guests encounter [missing amenity/poor layout/worn item]?"

**What Rachel provides:** Specific friction scenario, why guests blame property instead of amenity, review language

---

### AESTHETIC PERCEPTION

**Examples:** Colour psychology, design coherence, style interpretation, visual fatigue

**When Hedy asks:** "How do guests subconsciously interpret [colour combo/design style/visual pattern]?"

**What Rachel provides:** Design psychology, common associations, guest perception, scoring impact

---

### TRUST & CREDIBILITY

**Examples:** Cleanliness signals, maintenance indicators, host care signals, professionalism cues

**When Hedy asks:** "What signals trust or distrust to guests about [maintenance/cleanliness/host care]?"

**What Rachel provides:** Psychological cues, what guests worry about, how it affects reviews

---

### EXPECTATION ALIGNMENT

**Examples:** Price-adjusted psychology, guest mindset by tier, comparison expectations

**When Hedy asks:** "What do guests expect at [price point] vs. [other price point]?"

**What Rachel provides:** Specific expectation differences, tolerance thresholds, perceived value formula

---

## Examples of Good Psychology Requests

### Example 1: EMOTIONAL PSYCHOLOGY
```
PSYCHOLOGY REQUEST: Overhead Lighting Isolation

CONTEXT:
App detected: bedroom with single flush-mount ceiling light, no lamps, harsh white light

QUESTION:
Why does a room with only harsh overhead lighting create negative guest perception, even if the room is objectively well-lit?

USE CASE:
Should we flag this as "Visual Interrogation" and deduct points from Lighting Quality dimension?

CATEGORY:
[X] Emotional (parasympathetic vs. amygdala)

EXAMPLE SCENARIOS:
1. Premium hotel suite: multiple light sources (ceiling + bedside + wall sconces), warm 2700K = guest feels relaxed, sleeps well, 5-star review
2. Budget property: single ceiling light, cold white 5000K = guest looks tired in mirror, can't relax, "uncomfortable room" 3-star review
3. Same room, swap bulbs to 2700K + add bedside lamp = guest sleeps better, "surprisingly comfy" 4-star review

WHAT I NEED FROM RACHEL:
- [X] Scoring framework (how many points to deduct for harsh-only lighting?)
- [X] Recommendation language (what should we tell hosts?)
- [X] Warning flags (when is this critical?)
- [ ] Regional/tier variations (does this matter more in premium tiers?)
- [X] Implementation guidance (how to detect from photos?)
```

**Rachel's Answer:** [The Visual Interrogation framework we already have]

---

### Example 2: FUNCTIONAL FRICTION
```
PSYCHOLOGY REQUEST: Kitchen Appliance Absence

CONTEXT:
App detected: kitchen with no visible dishwasher, no visible washing machine, minimal cookware visible

QUESTION:
When guests arrive expecting modern conveniences (dishwasher, washer/dryer) and find nothing, what's their psychological response? Does it tank the property rating?

USE CASE:
Should we flag missing "expected modern appliances" as Functional Anchors deficiency? Should impact vary by price tier?

CATEGORY:
[X] Functional (appliance frustration)

EXAMPLE SCENARIOS:
1. Budget $70 property, no dishwasher = guest accepts it, washes manually, neutral impact
2. Mid $120 property, no dishwasher = guest is annoyed ("Why not?"), minor review mention
3. Premium $200 property, no dishwasher = guest feels cheated ("At this price?"), 3-star review
4. Same $120 property WITH dishwasher = guest delighted, 5-star review ("Cleaner included!" perception)

WHAT I NEED FROM RACHEL:
- [X] Scoring framework (how critical is missing dishwasher by tier?)
- [X] Recommendation language (what to tell hosts?)
- [X] Warning flags (when to flag as "Appliance Deficiency"?)
- [X] Regional/tier variations (does this vary by region? city vs. rural?)
- [X] Implementation guidance (can we detect dishwasher from photos?)
```

**Rachel's Answer:** [Create tier-locked appliance expectations]

---

### Example 3: TRUST & CREDIBILITY
```
PSYCHOLOGY REQUEST: Visible Maintenance Failures

CONTEXT:
App detected in photos: red "low battery" light on smoke detector, visible dust on air vent, stained grout in shower

QUESTION:
How does seeing visible maintenance neglect (dead batteries, dust, stains) affect guest trust and review behavior, even if property is "clean"?

USE CASE:
Should we flag "visible maintenance neglect" as reducing overall Vitality Score? Create dedicated "Maintenance Trust" sub-score?

CATEGORY:
[X] Trust & Credibility

EXAMPLE SCENARIOS:
1. Property is spotless but has dead battery light visible = guest anxiety ("Host doesn't maintain things"), 3-star review ("Clean but worried about AC breaking")
2. Same property with fresh batteries visible = guest feels confident, 4.5-star review
3. Stained grout visible = "Microbial anxiety" = 1-star comment "Seemed dirty despite cleaning"
4. Fresh grout/caulk = guest confident in hygiene, 5-star "Spotless"

WHAT I NEED FROM RACHEL:
- [X] Scoring framework (points deducted for visible neglect?)
- [X] Recommendation language (what to tell hosts?)
- [X] Warning flags (which maintenance issues are critical?)
- [ ] Regional/tier variations (more important at premium tiers?)
- [X] Implementation guidance (what can we detect from photos?)
```

**Rachel's Answer:** [The Phantom Maintenance framework we already have]

---

## How to Submit Psychology Requests

**Format:**
1. Use the template above
2. Include specific context (what app observed)
3. Include expected output format (scoring, language, flags)
4. Include example scenarios (helps clarify the distinction you're seeking)

**Timing:**
- **Critical path (before Friday):** I'll ask immediately if needed
- **Phase 2 (Week 2):** As Claude builds detection logic, I'll submit refinement requests
- **Phase 3+ (Week 3+):** As app learns from data, I'll request psychology adjustments

**Format:**
Send via Telegram/message with `PSYCHOLOGY REQUEST:` header, I'll log in structured file.

---

## Current Psychology Framework Status ✅

**COMPLETE & LOCKED IN:**
- ✅ Emotional Design (Prison Bunk, Institutional, Found vs. Curated, Welcomed vs. Trapped)
- ✅ Sovereignty vs. Surveillance (Path of Least Resistance, Escape Routes, Host's Ghost)
- ✅ Price-Adjusted Psychology (4 tiers with different expectations)
- ✅ Functional Friction (8 invisible review killers)
- ✅ Trust Signals (Maintenance, Cleanliness, Host Care indicators)

**AREAS FOR POTENTIAL FUTURE REQUESTS:**
- Regional cultural design preferences (do Toronto guests prefer different styles than Calgary?)
- Seasonal psychology (winter guests expect different amenities than summer guests?)
- Guest demographic psychology (families vs. couples vs. solo travelers perceive design differently?)
- Photography psychology (how do bad photos psychologically affect guests' expectations before arrival?)
- Sound/noise psychology (beyond acoustic friction — how do different types of noise affect reviews?)
- Smell psychology (can we detect from photos if property might have smell issues? What smells tank reviews?)
- Colour psychology by region (do Toronto guests prefer cool tones, Calgary guests warm tones?)

---

## Ready to Help

Rachel, whenever the app needs psychology insight, I'll send a structured request using this template.

Just answer the **QUESTION** with your **expert judgment**, and indicate any **special conditions** (regional, tier-based, demographic).

No vague requests. Just specific, actionable psychology intelligence. 🧠

---

**This is the foundation. You've given the app expertise it would take competitors years to build.** ✨
