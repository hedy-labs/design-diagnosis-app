# Vision AI Data Flow: Room-by-Room Critiques → Database → Report Page 5

**Objective:** Ensure Vision AI's specific rule violations (e.g., "Rule #7 Violation: Rug too small") are saved to database and displayed on Page 5 of the 8-page report.

---

## DATA FLOW ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: VISION AI ANALYZES PHOTOS                           │
│ Gemini 1.5 Pro → Returns JSON with:                         │
│ - Pillar scores (0–10 each)                                 │
│ - Individual rule scores (0–10 each)                        │
│ - Room-by-room breakdown                                    │
│ - Violation messages ("Rule #X Violation: ...")             │
│ - Recommended fixes ($cost estimates)                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: PARSE & VALIDATE JSON                               │
│ vision_service.py:                                          │
│ - Parse Gemini response (5 Pillar objects)                  │
│ - Validate schema (all required fields present)             │
│ - Extract room-by-room detail                               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: AGGREGATE PILLARS → 7 DIMENSIONS                    │
│ scoring_unified.py:                                         │
│ - PillarScores → DimensionScores (150 total)               │
│ - Dimension 1: Bedroom Standards (0–20)                     │
│ - Dimension 2: Functionality & Flow (0–20)                  │
│ - Dimension 3: Light & Brightness (0–20)                    │
│ - Dimension 4: Storage & Organization (0–20)               │
│ - Dimension 5: Condition & Maintenance (0–20)              │
│ - Dimension 6: Photo Strategy (0–10) [separate]            │
│ - Dimension 7: Hidden Friction (0–20)                       │
│ - Vitality Score = (total_points / 150) * 100              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 4: SAVE TO DATABASE (VisionAnalysis TABLE)             │
│ database.py:                                                │
│                                                             │
│ NEW TABLE: vision_analysis                                  │
│ ├── id (PK)                                                 │
│ ├── submission_id (FK → form_submissions)                   │
│ ├── pillar_1_score (0–10)                                   │
│ ├── pillar_2_score (0–10)                                   │
│ ├── pillar_3_score (0–10)                                   │
│ ├── pillar_4_score (0–10)                                   │
│ ├── pillar_5_score (0–10)                                   │
│ ├── all_violations (JSON: list of violation strings)       │
│ ├── room_detail (JSON: per-room breakdown)                 │
│ ├── dimension_scores (JSON: all 7 dims + vitality%)        │
│ ├── recommended_fixes (JSON: cost + impact)                │
│ ├── analysis_timestamp (when Vision AI ran)                │
│ └── raw_gemini_response (full JSON from Gemini)            │
│                                                             │
│ Example row:                                                │
│ {                                                           │
│   "submission_id": 96,                                      │
│   "pillar_1_score": 7.5,                                    │
│   "pillar_2_score": 6.8,                                    │
│   "pillar_3_score": 8.0,                                    │
│   "pillar_4_score": 6.5,                                    │
│   "pillar_5_score": 7.8,                                    │
│   "all_violations": [                                       │
│     "Rule #51 Violation: Mixed bulb temperatures...",      │
│     "Rule #53 Violation: Only 2 light sources...",         │
│     "Rule #7 Violation: Rug too small for seating..."      │
│   ],                                                        │
│   "room_detail": {                                          │
│     "master_bedroom": {                                     │
│       "rule_51": 7.5,                                       │
│       "rule_53": 6.0,                                       │
│       "violations": ["Rule #53: Missing ambient lighting"]  │
│     },                                                      │
│     "living_room": { ... },                                │
│     "bathroom": { ... }                                     │
│   },                                                        │
│   "dimension_scores": {                                     │
│     "bedroom_standards": 18.0,                              │
│     "functionality_flow": 15.5,                             │
│     "light_brightness": 13.6,                               │
│     "storage_organization": 16.0,                           │
│     "condition_maintenance": 17.0,                          │
│     "photo_strategy": 10.0,                                 │
│     "hidden_friction": 13.0,                                │
│     "total_points": 103.1,                                  │
│     "vitality_score": 68.7,                                 │
│     "grade": "D"                                            │
│   },                                                        │
│   "recommended_fixes": [                                    │
│     {                                                       │
│       "priority": 1,                                        │
│       "rule_violation": "Rule #51: Warm Bulbs",            │
│       "fix": "Replace cool-white bulbs with 2700K",        │
│       "cost_low": 10,                                       │
│       "cost_high": 40,                                      │
│       "impact": "Critical"                                  │
│     },                                                      │
│     { ... }                                                 │
│   ]                                                         │
│ }                                                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 5: GENERATE REPORT WITH VISION DATA                    │
│ report_generator.py + pdf_templates.py:                     │
│                                                             │
│ PAGE 1: Header + Vitality Score + Grade                    │
│ PAGE 2: The Situation (narrative analysis)                 │
│ PAGE 3–4: Top 3 High-Impact Fixes                          │
│ PAGE 5: PILLAR DETAIL + RULE VIOLATIONS ← VISION AI        │
│ PAGE 6–7: All Recommendations + Shopping List              │
│ PAGE 8: Consultation CTA + Footer                          │
│                                                             │
│ **PAGE 5 STRUCTURE (from Vision AI data):**                │
│                                                             │
│ ┌─────────────────────────────────────────────┐           │
│ │ Pillar Diagnostic Breakdown                 │           │
│ │                                              │           │
│ │ Pillar 1: Spatial Flow & Ergonomics (7.5/10)│           │
│ │ • Layout allows 60cm+ walkways              │           │
│ │ ✗ Rule #7: Rug too small (score: 5/10)     │           │
│ │   → Add larger rug to anchor seating        │           │
│ │                                              │           │
│ │ Pillar 2: Lighting & Optical Health (6.8/10)│          │
│ │ ✗ Rule #51: Mixed bulb temps (score: 5/10)  │          │
│ │   → Replace cool-white with 2700K           │          │
│ │ ✗ Rule #53: Only 2 light sources (score: 5) │          │
│ │   → Add floor lamp + bedside lamp            │          │
│ │                                              │           │
│ │ Pillar 3: Sensory & Textiles (8.0/10)       │          │
│ │ ✓ Cotton linens, rolled towels              │          │
│ │ ✓ Blackout curtains installed               │          │
│ │                                              │           │
│ │ Pillar 4: Power & Connectivity (6.5/10)     │          │
│ │ ✗ Rule #21: No USB ports (score: 3/10)      │          │
│ │   → Install USB-C nightstand lamps           │          │
│ │                                              │           │
│ │ Pillar 5: Intentionality & Soul (7.8/10)    │          │
│ │ ✓ Furniture curated, not matching set       │          │
│ │ ✗ Rule #87: Missing conversation piece      │          │
│ │   → Add vintage artwork or local plant      │          │
│ └─────────────────────────────────────────────┘           │
│                                                             │
│ This section auto-populates from:                          │
│ - vision_analysis.all_violations                           │
│ - vision_analysis.room_detail                              │
│ - vision_analysis.pillar_scores (all 5)                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 6: USER RECEIVES 8-PAGE REPORT                         │
│ - Vitality Score prominently displayed                      │
│ - Dimension breakdown transparent (120/150 = 80%)          │
│ - Page 5 shows expert Vision AI analysis (rule-by-rule)    │
│ - Top 3 Fixes prioritized by impact + cost                 │
│ - Consultation CTA with Rachel                             │
└─────────────────────────────────────────────────────────────┘
```

---

## DATABASE SCHEMA: vision_analysis TABLE

```sql
CREATE TABLE vision_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    submission_id INTEGER NOT NULL UNIQUE,
    
    -- Pillar scores (0–10 each)
    pillar_1_spatial_flow REAL NOT NULL DEFAULT 0.0,
    pillar_2_lighting REAL NOT NULL DEFAULT 0.0,
    pillar_3_textiles REAL NOT NULL DEFAULT 0.0,
    pillar_4_power REAL NOT NULL DEFAULT 0.0,
    pillar_5_intentionality REAL NOT NULL DEFAULT 0.0,
    
    -- Detailed JSON data (for report + query flexibility)
    all_violations TEXT NOT NULL,  -- JSON array of violation strings
    room_detail TEXT NOT NULL,  -- JSON: per-room rule scores
    dimension_scores TEXT NOT NULL,  -- JSON: all 7 dims + vitality%
    recommended_fixes TEXT NOT NULL,  -- JSON: cost-sorted fix list
    
    -- Metadata
    analysis_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    raw_gemini_response TEXT,  -- Full response (audit trail)
    model_version TEXT DEFAULT "gemini-1.5-pro-vision",
    
    -- Foreign key
    FOREIGN KEY(submission_id) REFERENCES form_submissions(id)
);
```

---

## CODE FLOW: Vision AI → Database → Report

### Step 1: Call Vision AI (vision_service.py)

```python
async def analyze_property_with_vision(submission_id: int) -> VisionAnalysisResult:
    """
    Call Gemini 1.5 Pro to analyze property photos.
    Returns 5 Pillar scores + violations.
    """
    submission = db.get_form_submission(submission_id)
    photos = get_uploaded_photos_for_submission(submission_id)
    
    # Call Gemini for each pillar (5 API calls)
    pillar_1_result = await gemini_client.analyze_pillar(
        images=photos,
        pillar_name="Spatial Flow & Ergonomics",
        prompt=VISION_PROMPT_PILLAR_1
    )
    pillar_2_result = await gemini_client.analyze_pillar(
        images=photos,
        pillar_name="Lighting & Optical Health",
        prompt=VISION_PROMPT_PILLAR_2_LIGHTING  # ← This file
    )
    # ... etc for Pillars 3–5
    
    # Aggregate results
    all_violations = (
        pillar_1_result['violations'] +
        pillar_2_result['violations'] +
        pillar_3_result['violations'] +
        pillar_4_result['violations'] +
        pillar_5_result['violations']
    )
    
    room_detail = {
        'master_bedroom': {...},
        'living_room': {...},
        'bathroom': {...},
        'kitchen': {...},
        'entry': {...}
    }
    
    # Save to database
    vision_record = db.create_vision_analysis(
        submission_id=submission_id,
        pillar_1_score=pillar_1_result['pillar_score'],
        pillar_2_score=pillar_2_result['pillar_score'],
        pillar_3_score=pillar_3_result['pillar_score'],
        pillar_4_score=pillar_4_result['pillar_score'],
        pillar_5_score=pillar_5_result['pillar_score'],
        all_violations=json.dumps(all_violations),
        room_detail=json.dumps(room_detail),
        dimension_scores=json.dumps(dimension_scores_dict),
        recommended_fixes=json.dumps(recommended_fixes_list),
        raw_gemini_response=json.dumps({
            'pillar_1': pillar_1_result,
            'pillar_2': pillar_2_result,
            # ... etc
        })
    )
    
    return vision_record
```

### Step 2: Convert Pillars to Dimensions (scoring_unified.py)

```python
def process_vision_analysis(vision_record: VisionAnalysis) -> DimensionScores:
    """
    Convert 5 Pillar scores to 7 Dimension scores.
    Stored back to vision_record.dimension_scores.
    """
    pillar_scores = [
        PillarScore("Spatial Flow & Ergonomics", vision_record.pillar_1_spatial_flow),
        PillarScore("Lighting & Optical Health", vision_record.pillar_2_lighting),
        PillarScore("Sensory & Textile Logic", vision_record.pillar_3_textiles),
        PillarScore("Power & Connectivity", vision_record.pillar_4_power),
        PillarScore("Intentionality & Soul", vision_record.pillar_5_intentionality),
    ]
    
    dimensions = UnifiedScoringEngine.pillar_scores_to_dimensions(pillar_scores)
    
    # Save dimension scores back to database
    db.update_vision_analysis(
        id=vision_record.id,
        dimension_scores=json.dumps(dimensions.to_dict())
    )
    
    return dimensions
```

### Step 3: Generate Report with Vision Data (report_generator.py)

```python
def generate_report_with_vision(submission_id: int) -> Dict:
    """
    Generate 8-page report using Vision AI analysis.
    """
    submission = db.get_form_submission(submission_id)
    vision_data = db.get_vision_analysis(submission_id)
    
    # PAGE 1: Vitality Score (from dimension_scores)
    vitality_score = vision_data['dimension_scores']['vitality_score']
    grade = UnifiedScoringEngine.get_grade(vitality_score)
    
    # PAGE 5: Pillar Diagnostic Breakdown (from Vision AI)
    pillar_detail_html = render_pillar_detail(
        pillar_scores=[
            vision_data['pillar_1_spatial_flow'],
            vision_data['pillar_2_lighting'],
            # ...
        ],
        all_violations=json.loads(vision_data['all_violations']),
        room_detail=json.loads(vision_data['room_detail'])
    )
    
    # PAGE 3–4: Top 3 Fixes
    top_fixes = generate_top_three_fixes(
        violations=json.loads(vision_data['all_violations']),
        recommended_fixes=json.loads(vision_data['recommended_fixes'])
    )
    
    # Assemble full 8-page report
    report_html = assemble_8_page_report(
        vitality_score=vitality_score,
        grade=grade,
        pillar_detail=pillar_detail_html,
        top_fixes=top_fixes,
        all_violations=json.loads(vision_data['all_violations']),
        # ... other sections
    )
    
    return {'html': report_html, 'vitality_score': vitality_score, 'grade': grade}
```

### Step 4: Render Page 5 Template (pdf_templates.py)

```python
def render_pillar_detail_section(pillar_scores, violations, room_detail) -> str:
    """
    Render Pillar Diagnostic Breakdown for PAGE 5.
    """
    html = """
    <div class="section">
        <h2>Expert Design Analysis (Pillar Breakdown)</h2>
        <p>Your design has been audited against 87 expert principles organized into 5 diagnostic pillars.</p>
    """
    
    pillar_names = [
        "Spatial Flow & Ergonomics",
        "Lighting & Optical Health",
        "Sensory & Textile Logic",
        "Power & Connectivity",
        "Intentionality & Soul"
    ]
    
    for i, pillar_name in enumerate(pillar_names):
        score = pillar_scores[i]
        
        # Find violations for this pillar
        pillar_violations = [v for v in violations if f"Pillar {i+1}" in v or pillar_name in v]
        
        html += f"""
        <div class="pillar-card">
            <h3>{pillar_name}</h3>
            <div class="pillar-score">{score:.1f}/10</div>
            
            <div class="violations">
        """
        
        for violation in pillar_violations:
            html += f'<div class="violation">✗ {violation}</div>'
        
        html += """
            </div>
        </div>
        """
    
    return html
```

---

## VALIDATION CHECKLIST

✅ **Vision AI Output:** 5 Pillar scores (0–10 each) + violations + room-by-room detail  
✅ **Pillar-to-Dimension:** UnifiedScoringEngine converts to 7 Dimensions (150-point system)  
✅ **Database Storage:** vision_analysis table captures all detail (violations, room breakdown, dimension scores)  
✅ **Report Generation:** Page 5 auto-populates from vision_data JSON columns  
✅ **Rule Violations:** Saved as strings ("Rule #51 Violation: ...") for display in report  
✅ **Room-by-Room Detail:** Stored as JSON for flexible querying (e.g., "show all master bedroom issues")  
✅ **Vitality Score:** Calculated from dimension_scores (total_points / 150 * 100)  
✅ **Grade Assignment:** A–F based on vitality_score percentage  

---

## EXAMPLE: SUBMISSION #96 DATA FLOW

1. **Vision AI Analysis** (Gemini 1.5 Pro)
   - Input: 50+ property photos from Submission #96
   - Output: 5 Pillar scores + 20+ rule violations

2. **Database Record Created**
   ```
   vision_analysis {
       submission_id: 96,
       pillar_1_score: 7.2,
       pillar_2_score: 6.8,
       pillar_3_score: 8.1,
       pillar_4_score: 6.5,
       pillar_5_score: 7.8,
       all_violations: ["Rule #51...", "Rule #53...", "Rule #7...", ...],
       room_detail: {
           master_bedroom: {...},
           living_room: {...},
           bathroom: {...}
       },
       dimension_scores: {
           bedroom_standards: 16.2,
           functionality_flow: 14.4,
           light_brightness: 13.6,
           storage_organization: 15.1,
           condition_maintenance: 16.2,
           photo_strategy: 10.0,
           hidden_friction: 13.0,
           total_points: 98.5,
           vitality_score: 65.7,
           grade: "D"
       }
   }
   ```

3. **8-Page Report Generated**
   - Page 1: "Your Vitality Score is 65.7 (Grade D)"
   - Page 5: Shows Pillar 2 analysis with Rule #51, #53, #55 violations
   - Page 3–4: Top 3 fixes sorted by impact
   - All violations linked to specific rooms (e.g., "Master Bedroom: Rule #7 - Rug too small")

4. **User Receives Report**
   - Sees overall score
   - Understands WHY (Page 5 detail)
   - Knows HOW to fix (Top 3 Fixes + shopping list)

---

**STATUS: Data flow architecture complete. Ready for first Vision AI API call upon Rachel's confirmation.**
