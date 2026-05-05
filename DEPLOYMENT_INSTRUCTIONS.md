# Rachel Rules v1.0 Deployment Instructions

**Status:** Brain Transplant complete and ready for production deployment

## Quick Deployment (DigitalOcean Droplet)

### Step 1: Pull Latest Code
```bash
cd /root/design-diagnosis-app
git pull
```

### Step 2: Restart Application
```bash
systemctl restart design-diagnosis
```

### Step 3: Verify Deployment
Check that the app restarted cleanly:
```bash
systemctl status design-diagnosis
```

### Step 4: Test with Sample Property
Use the web form at your droplet URL to upload the 5 test photos and verify:
- ✅ JSON output contains `hero_fix` section
- ✅ JSON output contains `staging_and_click` section
- ✅ JSON output contains `aesthetic_refresh` section
- ✅ JSON output contains `photography_accountability` section
- ✅ JSON output contains `professional_imagery_roi` with 40%, 24%, 26%, 85% metrics

## What Changed

**File:** `vision_analyzer_v2.py` (Line ~184)  
**Variable:** `master_prompt`  
**Change:** Replaced old "elite designer" prompt with Rachel Rules v1.0 framework

## What to Expect

### Input
5 property photos (any STR/Airbnb listing)

### Output (JSON)
```json
{
  "hero_fix": {
    "title": "Single most impactful change",
    "cost_range": "$X-Y",
    "revenue_impact": "+$XXX/month",
    "roi_timeline": "X weeks to break even",
    "why_matters": "Host-speak explanation"
  },
  "staging_and_click": {
    "description": "Platform scroll-stop enhancements",
    "items": ["Item 1", "Item 2", "Item 3"],
    "estimated_budget": "$X-Y",
    "booking_impact": "X% increase"
  },
  "aesthetic_refresh": {
    "focus_areas": ["Area 1", "Area 2"],
    "actions": ["Action 1", "Action 2"],
    "budget": "$X-Y",
    "perceived_value_increase": "How guests perceive it"
  },
  "photography_accountability": "Notes on photo quality issues",
  "tier_specific_pivot": "Standard or Luxury advice",
  "professional_imagery_roi": {
    "average_revenue_increase": "40%",
    "booking_increase": "24%",
    "nightly_rate_increase": "26%",
    "payoff_timeline": "85% of hosts pay off in one night"
  }
}
```

## Rollback (If Needed)

If you want to revert to the previous prompt:
```bash
cd /root/design-diagnosis-app
git revert b08b5dd
systemctl restart design-diagnosis
```

Or reset to a specific commit:
```bash
git reset --hard <commit-hash>
systemctl restart design-diagnosis
```

## GitHub Commits

- **b08b5dd:** feat: Brain Transplant - Rachel Rules v1.0 System Prompt Injection
- **203a491:** docs: Brain Transplant Completion Report

Both are on the `main` branch and ready to pull.

## Notes

- The prompt is embedded directly in `vision_analyzer_v2.py` (no external config files)
- JSON output schema is guaranteed by the prompt instructions
- The framework prioritizes ROI and host-speak over designer aesthetics
- Rate limiting (429 Shield) and cloud storage (R2) are already deployed

## Questions?

Review `BRAIN_TRANSPLANT_COMPLETION.md` for full verification details.
