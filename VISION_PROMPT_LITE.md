# VISION_PROMPT_LITE: Zero-Shot Minimal-Token Analysis (Free Tier)

**Purpose**: Lightweight baseline Vitality Score for Free Tier (blurred previews)  
**Token Usage**: ~500-800 tokens (vs. 3000-5000 for premium prompts)  
**Approach**: Zero-shot (no examples), superficial scan only  
**Output**: Baseline score (0-30) + 3 major structural gaps  
**Quality**: Good enough for "should I upgrade?" decision, NOT suitable for paid reports  

---

## SYSTEM PROMPT: MINIMAL VISION ANALYSIS

```
You are a property design reviewer. Analyze the property photos for basic design quality.

Return ONLY a JSON object with no other text:
{
  "design_score": <integer 0-30>,
  "gap_1": "<single structural gap>",
  "gap_2": "<single structural gap>",
  "gap_3": "<single structural gap>",
  "brief_assessment": "<1 sentence summary>"
}

SCORING RULES (0-30 scale):
- 0-10: Very poor (bare, dark, disorganized)
- 10-20: Below average (some furniture, but missing key pieces)
- 20-30: Adequate (reasonably furnished, basic comfort items present)

IDENTIFY GAPS BY LOOKING FOR:
1. Missing bedside lamps (bedroom)
2. Missing sofa/seating (living room)
3. Missing entry hooks/shoe storage
4. Harsh overhead lighting only
5. Excessive clutter or poor organization

DO NOT:
- Make up items you don't see
- Use examples or few-shot analysis
- Provide detailed narratives
- Analyze individual rooms in detail

BE BRIEF:
- Score only (not 0-100, only 0-30)
- 3 gaps maximum (1 line each)
- 1-sentence summary
```

---

## EXAMPLE INPUT

```
[8 images of property interior]
```

## EXAMPLE OUTPUT

```json
{
  "design_score": 18,
  "gap_1": "Bedroom missing bedside lamps (only overhead light)",
  "gap_2": "Entry area has no hooks or storage for coats/shoes",
  "gap_3": "Living room furniture sparse and undersized for room",
  "brief_assessment": "Functional but needs key comfort items and entry organization."
}
```

---

## IMPLEMENTATION NOTES

### Why Zero-Shot?
- **Premium Prompts**: Few-shot (5-10 examples per pillar) = 2000+ tokens
- **Lite Prompt**: Zero-shot (no examples) = 300-500 tokens
- **Savings**: 80-90% token reduction per Free Tier request

### Why Limited Score Range (0-30)?
- **Premium**: 0-100 scale with detailed 5-pillar breakdowns
- **Lite**: 0-30 scale (simplified, superficial)
- **Clear distinction**: Free users see this is a preview, not full analysis

### Why Only 3 Gaps?
- **Premium**: 10-15 fixes with costs, priorities, room-by-room
- **Lite**: 3 major gaps (quick scan)
- **Incentive**: Users see "learn more" potential in Premium

### Error Handling
If unable to analyze:
```json
{
  "design_score": 0,
  "gap_1": "Unable to analyze property",
  "gap_2": "Please try uploading clearer photos",
  "gap_3": "Or upgrade to Premium for detailed feedback",
  "brief_assessment": "Analysis unavailable. Please retry or upgrade."
}
```

---

## TOKEN BUDGET COMPARISON

### Premium Analysis (VISION_PROMPTS_PILLARS_CORRECTED.md)

```
System prompt:        1,200 tokens (5 pillars × few-shot examples)
User prompt:          100 tokens (5-10 images)
Response:             800 tokens (detailed analysis)
Total per request:    2,100 tokens
```

### Lite Analysis (VISION_PROMPT_LITE.md)

```
System prompt:        200 tokens (minimal rules, no examples)
User prompt:          100 tokens (5-10 images)
Response:             150 tokens (JSON only)
Total per request:    450 tokens
```

### Cost Savings

```
Premium: $0.03/request × 2,100 tokens = ~$0.06 per request
Lite:    $0.03/request ÷ 4.7x savings = ~$0.013 per request
```

**Annual savings** (10,000 Free Tier requests):
- Premium cost: $600
- Lite cost: $130
- Savings: **$470/year** with 100x more scalability

---

## USAGE IN PRODUCTION

### When to Use LITE:
```python
if submission.report_type == "free":
    # Use lite prompt (minimal tokens, basic score)
    response = vision_service.analyze_lite(images)
    score = response["design_score"]  # 0-30
    gaps = [response["gap_1"], response["gap_2"], response["gap_3"]]
else:
    # Use premium prompts (detailed, full-featured)
    response = vision_service.analyze_pillars(images)
    score = response["total_score"]  # 0-100
```

### Frontend Rendering

**Free Tier (Lite)**:
```
Vitality Score: 18/30
(Preview - Upgrade to see full analysis)

Quick Issues:
• Bedroom missing bedside lamps
• Entry area needs hooks/storage
• Living room furniture undersized
```

**Premium (Full)**:
```
Vitality Score: 72/100

Bedroom Standards (14/20)
• Missing bedside lamps → -2 points
• Low thread-count bedding → -1 point
[Detailed breakdown with fixes...]
```

---

## ROLLOUT PLAN

### Phase 1: Testing (Local)
1. Generate sample Free Tier requests
2. Compare token usage (should be ~5x less)
3. Verify score accuracy (0-30 range)
4. Confirm JSON parsing

### Phase 2: Production
1. Deploy updated vision_service.py with two-lane routing
2. Monitor token spend for Free vs. Premium
3. Track user upgrade rate from Free to Premium
4. A/B test threshold for "upgrade prompts"

### Phase 3: Optimization
1. If Free Tier users upgrade frequently → Lite prompt too good (raise difficulty)
2. If Free Tier users never upgrade → Lite prompt too vague (improve clarity)
3. Fine-tune 3 gaps to maximize conversion

---

## NOTES FOR RACHEL

This approach:
- ✅ Reduces Free Tier compute cost by 80-90%
- ✅ Keeps Free users seeing enough to want Premium
- ✅ Maintains quality for Premium (no changes)
- ✅ Clear differentiation between tiers
- ✅ Easy to implement (one new prompt file)

The lite prompt is intentionally vague and limited. That's the feature, not a bug. Users who get a "18/30 preview" will upgrade to Premium to see the full "72/100 analysis" and understand why.
