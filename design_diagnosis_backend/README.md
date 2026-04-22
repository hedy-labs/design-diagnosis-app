# Design Diagnosis Backend

Vitality Score calculation engine for Airbnb properties (0–100 scale across 7 dimensions).

**Status:** ✅ Infrastructure ready (Phase 1 complete)  
**Launch:** Wed 2026-04-23  
**Brand:** Rooms by Rachel

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start API Server

```bash
python main.py
```

Server runs on `http://0.0.0.0:8000`

API docs: `http://localhost:8000/docs` (Swagger UI)

### 3. Test the API

```bash
# Health check
curl http://localhost:8000/health

# Analyze property
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d @test_payload.json

# Get report
curl http://localhost:8000/api/report/1
```

---

## Architecture

### Four Core Modules

| Module | File | Purpose |
|--------|------|---------|
| Database | `database.py` | SQLite CRUD for properties, reports, scores |
| Scoring | `scoring.py` | Vitality score calculation (0–150 → 0–100) |
| API | `main.py` | FastAPI endpoints for analysis & reporting |
| PDF | `pdf_report.py` | Rooms by Rachel branded PDF generation |

### Vitality Score Formula

```
Total Points = D1 + D2 + D3 + D4 + D5 + D6 + D7
(max 150 points)

Vitality Score = (Total / 150) × 100

Grade:
├── A: 90–100
├── B: 80–89
├── C: 70–79
├── D: 60–69
└── F: 0–59
```

### The 7 Dimensions

| # | Dimension | Points | Description |
|---|-----------|--------|-------------|
| 1 | Bedroom Standards | 20 | Beds, lamps, nightstands, textiles |
| 2 | Functionality & Flow | 20 | Layout, zones, appliance placement |
| 3 | Light & Brightness | 20 | Windows, fixtures, natural light |
| 4 | Storage & Organization | 20 | Closets, shelves, hangers, drawers |
| 5 | Condition & Maintenance | 20 | Cleanliness, repair, wear |
| 6 | Photo Strategy | 10 | Count, consistency, quality |
| 7 | Hidden Friction | 20 | 42-item guest expectation checklist |

---

## API Endpoints

### POST `/api/analyze`

Analyze property and calculate Vitality Score.

**Request:**
```json
{
  "property": {
    "airbnb_url": "https://www.airbnb.ca/rooms/...",
    "airbnb_id": "1234567890",
    "property_name": "Beautiful Apartment",
    "location": "Kuala Lumpur, Malaysia",
    "bedrooms": 2,
    "bathrooms": 1,
    "guest_capacity": 4
  },
  "bedroom_standards_score": 18.0,
  "functionality_flow_score": 17.0,
  "light_brightness_score": 18.0,
  "storage_organization_score": 16.0,
  "condition_maintenance_score": 19.0,
  "photo_count": 25,
  "photo_quality_score": 8.5,
  "photo_consistency_issues": 0
}
```

**Response:**
```json
{
  "report_id": 1,
  "property_id": 1,
  "property_name": "Beautiful Apartment",
  "vitality_score": 85.3,
  "grade": "B",
  "total_points": 128.0,
  "dimensions": [
    {
      "dimension": 1,
      "score": 18.0,
      "max_points": 20,
      "label": "Bedroom Standards"
    },
    ...
  ],
  "created_at": "2026-04-17T10:00:00",
  "recommendations": [...]
}
```

---

### POST `/api/hidden-friction`

Submit Hidden Friction checklist and recalculate score.

**Request:**
```json
{
  "report_id": 1,
  "missing_items": [
    {
      "name": "hangers",
      "severity": "high",
      "category": "BEDROOM",
      "notes": "Only 4 hangers in master bedroom"
    },
    {
      "name": "dryer",
      "severity": "critical",
      "category": "LAUNDRY"
    }
  ]
}
```

**Response:**
```json
{
  "status": "success",
  "report_id": 1,
  "hidden_friction_score": 16.0,
  "vitality_score": 82.5,
  "grade": "B",
  "total_points": 123.5,
  "missing_items_count": 2
}
```

---

### GET `/api/report/{report_id}`

Retrieve complete report.

**Response:**
```json
{
  "report_id": 1,
  "property_id": 1,
  "property_name": "Beautiful Apartment",
  "vitality_score": 82.5,
  "grade": "B",
  "total_points": 123.5,
  "dimensions": [
    {...}
  ],
  "created_at": "2026-04-17T10:00:00"
}
```

---

## Hidden Friction Checklist (42 Items)

### Severity Levels

- **Critical** (−2.0): Power bar, plunger, dryer, mattress protectors
- **High** (−1.5): Lamps, nightstands, hangers, pillows
- **Medium** (−1.0): Desk lamp, dishcloths, hamper
- **Low** (−0.5): Coasters, felt pads, placemats

### Categories

**BEDROOM (10 items per bedroom)**
- Power bar (per room)
- Hangers (10+)
- Pillows (2)
- Desk lamp (if desk)
- Bedside lamps (2)
- Nightstands (2)
- Laundry hamper
- Wall mirror
- Mattress protector
- Pillow protectors

**BATHROOM (9 items per bathroom)**
- Towels (3 bath, 3 hand, 3 face)
- Plunger (per room)
- Bath mat (2+)
- Hooks
- Shower curtain/door
- Toilet brush
- Cleaning supplies
- Soap dispenser
- Squeegee (if shower)

**KITCHEN & LAUNDRY (16 items shared)**
- Cookware (pots, pans)
- Glassware
- Plates, bowls, utensils
- Cutting board, knives
- Storage containers
- Dish drying rack
- Dishcloths
- Dryer OR drying rack (if washer)
- Laundry pods/detergent
- Can opener, bottle opener
- Trash can, recycling
- Compost (optional)
- Appliance manuals
- WiFi info
- Emergency contacts
- Cleaning supplies

**LIVING & ENTRY (6 items shared)**
- Shoe rack
- Console table
- Wall mirror
- Reading lamp
- Coasters
- Placemats

**MAINTENANCE (1 item)**
- Felt pads (furniture protection)

---

## Testing

### Unit Tests (No external dependencies)

```bash
python test_core_logic.py
```

Tests:
- ✅ Scoring calculations
- ✅ Database schema
- ✅ Vitality formula (150-point system)

### Full Test Suite (Requires dependencies)

```bash
python test_harness.py
```

Tests:
- ✅ Database CRUD
- ✅ Scoring engine
- ✅ Photo strategy scoring
- ✅ Hidden friction scoring
- ✅ End-to-end workflow
- ✅ PDF generation

### Sample Test Case: Rachel's Airbnb

**Property:** Trion @ KL, Kuala Lumpur  
**Expected Score:** ~59/100 (F grade)  
**Why:** Missing hangers, dryer, drying rack, limited storage

---

## PDF Report Generation

### Generate PDF Report

```python
from pdf_report import VitalityReportPDF

pdf = VitalityReportPDF("my_report.pdf")
pdf.generate(
    property_name="Trion @ KL",
    location="Kuala Lumpur, Malaysia",
    vitality_score=59.3,
    grade="F",
    total_points=89.0,
    dimension_scores={1: 14, 2: 15, 3: 16, 4: 12, 5: 14, 6: 7, 7: 6},
    missing_items=["hangers", "dryer", "drying_rack"],
    cost_estimate=1200.0,
    roi_projection=18.5
)
```

### Report Sections

1. **Header** — Brand + property name + vitality score box
2. **Dimensions** — Breakdown of 7 dimensions with scores
3. **Key Findings** — Missing items from checklist
4. **Investment** — Estimated cost + ROI projection
5. **Recommendations** — Action items based on grade

---

## Database Schema

### Properties Table

```sql
CREATE TABLE properties (
    id INTEGER PRIMARY KEY,
    airbnb_url TEXT UNIQUE,
    airbnb_id TEXT UNIQUE,
    property_name TEXT,
    location TEXT,
    bedrooms INTEGER,
    bathrooms INTEGER,
    guest_capacity INTEGER,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### Reports Table

```sql
CREATE TABLE reports (
    id INTEGER PRIMARY KEY,
    property_id INTEGER UNIQUE,
    vitality_score REAL,
    grade TEXT,
    total_points REAL,
    dimension_scores_json TEXT,
    photo_count INTEGER,
    photo_score REAL,
    photo_notes TEXT,
    hidden_friction_score REAL,
    hidden_friction_missing_json TEXT,
    hidden_friction_cost_estimate REAL,
    report_pdf_path TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

---

## Deployment

### Development

```bash
python main.py
```

Server: `http://localhost:8000`

### Production (AWS/Heroku)

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

### Docker

```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

```bash
docker build -t design-diagnosis .
docker run -p 8000:8000 design-diagnosis
```

---

## Next Steps

### Week 1 (Fri 2026-04-17)
- [x] Database schema
- [x] API skeleton
- [x] Scoring engine framework
- [x] PDF template structure
- [x] Test harness setup

### Week 2 (Sat–Tue 2026-04-18-22)
- [ ] Dimension 1–5 analyzers (photo + text analysis)
- [ ] Dimension 6 photo strategy (upload/extract/consistency)
- [ ] Dimension 7 hidden friction (form + auto-scoring)
- [ ] End-to-end testing (EMPTY BOX, Rachel's Airbnb)
- [ ] Stripe sandbox integration
- [ ] PDF finalization

### Week 3 (Wed 2026-04-23)
- [ ] Final QA
- [ ] Go-live

---

## Questions?

Ask Hedy for:
- Framework clarifications
- Airbnb API scraping approach
- Stripe sandbox setup
- PDF branding specs
- Any gaps in documentation

---

**Build by:** Claude  
**Date:** 2026-04-17  
**Launch:** 2026-04-23  
**Brand:** Rooms by Rachel
