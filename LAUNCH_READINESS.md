# Design Diagnosis Launch Readiness Checklist

**Target Launch:** Friday 2026-04-05  
**Current Date:** Wednesday 2026-04-01  
**Days to Launch:** 4 days

---

## CRITICAL BLOCKING ISSUES

### 🔴 CRITICAL: Affiliate Links Broken
- **Status:** Not working in app
- **Root Cause:** Rachel's affiliate accounts not yet active
- **Owner:** Rachel
- **Deadline:** Wednesday EOD (today) or Thursday morning
- **Action Items:**
  - [ ] Activate Amazon Associates account
  - [ ] Activate Wayfair account
  - [ ] Activate IKEA account
  - [ ] Share affiliate IDs with Hedy
  - [ ] Hedy: Inject working links into reports
- **Impact:** HIGH — Can't launch without working affiliate links
- **Fallback:** Launch with "Shop on Amazon" button (no affiliate tracking) if accounts not ready

---

## HIGH PRIORITY: Report Validation

### 📊 Report Review Status
- [x] Brown Town (Rachel reviewed, feedback logged)
- [ ] Delta Blue (pending)
- [ ] Lower Luxury (pending)
- [ ] Golden Grove (pending)
- [ ] Free Will (pending)
- [ ] Graydar (pending)
- [ ] Hobby Lobby (pending)
- [ ] Rent Free (pending)

**Owner:** Rachel  
**Deadline:** Tonight/Thursday morning  
**Action Items:**
- [ ] Score accuracy validation
- [ ] Dimension breakdown review
- [ ] Top 3 fixes feedback
- [ ] Shopping list check
- [ ] Revenue projection accuracy

**Impact:** HIGH — Feedback drives dimension weighting + scoring recalibration

---

## HIGH PRIORITY: Dimension Weighting

### Implement Weighted Dimensions
**From Brown Town feedback:**
- Functional Anchors: 30 points (25%)
- Clutter & Space Flow: 24 points (20%)
- Staging Integrity: 24 points (20%)
- Lighting Quality: 22 points (18%)
- Colour Coherence: 20 points (17%)

**Owner:** Hedy  
**Deadline:** Thursday EOD  
**Status:** Ready to implement (just needs Rachel's OK after all reports reviewed)  
**Impact:** HIGH — Changes all 8 property scores

---

## MEDIUM PRIORITY: Scoring Recalibrations

### Colour Dimension Recalibration
- Current: Too harsh on bland colours
- New: Distinguish between "clashing" vs. "repetitive"
- Owner: Hedy
- Deadline: Thursday
- Status: Ready to implement

### Lighting Dimension Recalibration
- Current: Too harsh on overhead-only lighting
- New: Overhead + some lamps = acceptable (14/20, not 9/20)
- Owner: Hedy
- Deadline: Thursday
- Status: Ready to implement

---

## MEDIUM PRIORITY: Photo Strategy Integration

### Photo Audit Features (6th Dimension)
- [ ] Flag listings with 50+ photos
- [ ] Detect inconsistent photos (advanced: Week 2)
- [ ] Score photo quality (professional vs. DIY)
- [ ] Recommend "Hire photographer" in Tier 1
- Owner: Hedy
- Deadline: Thursday (basic), Week 2 (advanced)
- Status: Framework complete, implementation ready
- Impact: MEDIUM — Nice-to-have for launch, critical for value prop

---

## MEDIUM PRIORITY: Shopping List Improvements

### Add Budget Alternatives
- [ ] For each fix, show 3 price tiers (Budget, Mid, Luxury)
- Example: Sofa replacement
  - Budget: Slipcovers ($100–200)
  - Mid: IKEA sofa ($400–600)
  - Luxury: Custom sofa ($800–1,200)
- Owner: Hedy
- Deadline: Thursday
- Status: Framework designed, implementation pending
- Impact: MEDIUM — Helps hosts match budget to solutions

---

## LOW PRIORITY: Photographer Referral Network

### Recruit Photographers (Week 2)
- [ ] Create photographer outreach template
- [ ] Search Upwork/Fiverr
- [ ] Contact 20+ photographers
- [ ] Build photographer database
- Owner: Hedy + Rachel
- Deadline: Week 2 (April 7–9)
- Status: Framework complete, recruitment starts after launch
- Impact: LOW for launch, HIGH for Year 1 revenue

---

## CONTENT & MARKETING

### TikTok Readiness
- [x] 87 Design Principles documented (content ideas)
- [x] Photo Strategy rules documented (4 video ideas)
- [x] 8 property case studies ready
- [ ] Rachel: Film 10+ videos (Thursday)
- [ ] Rachel: Post first 2 videos (Friday 6 AM + 6 PM UTC)
- Owner: Rachel
- Deadline: Friday
- Status: On track
- Impact: CRITICAL — This is the growth engine

### Website/Landing Page
- [ ] Update bios (TikTok, Instagram, Facebook)
- [ ] Create /design-diagnosis landing page
- [ ] Add affiliate disclaimers (legal)
- Owner: Rachel
- Deadline: Friday
- Status: In progress
- Impact: MEDIUM — Needed for link clicks

---

## DEPLOYMENT

### Server & Infrastructure
- [x] DigitalOcean droplet verified (14GB free space)
- [ ] Deploy Design Diagnosis backend (vitality_score.py)
- [ ] Set up Typeform for photo uploads
- [ ] Test end-to-end workflow (photo → report → email)
- Owner: Hedy
- Deadline: Friday morning
- Status: Ready to deploy
- Impact: CRITICAL — Can't launch without working backend

### Email System
- [ ] Verify email sender configured
- [ ] Test report email delivery
- [ ] Ensure affiliate links survive email transit
- Owner: Hedy
- Deadline: Thursday
- Status: Pending (depends on affiliate accounts)
- Impact: HIGH

---

## LEGAL & COMPLIANCE

### Affiliate Disclosures
- [ ] Add FTC disclaimer on reports ("We earn commissions...")
- [ ] Add terms of service
- [ ] Verify Airbnb usage rights for listing analysis
- Owner: Rachel (with legal review if needed)
- Deadline: Friday
- Status: Design Principles mention this, needs implementation
- Impact: MEDIUM — Important for compliance

---

## PHASE 1 (MVP) vs. PHASE 2 (Nice-to-Have)

### PHASE 1: Friday Launch (Minimum Viable Product)
✅ **Must have:**
- Working affiliate links (Amazon, Wayfair, IKEA)
- Vitality Score calculation + 8 property reports
- Email delivery system
- TikTok videos posted
- Typeform photo upload working

✅ **Working but not perfect:**
- Dimension weighting (current equal weights, refine after launch)
- Shopping lists (basic, improve with feedback)
- Photo strategy flagging (manual recommendation for now)

❌ **Not ready for launch:**
- Photographer referral network (Week 2)
- Advanced photo consistency detection (Week 2)
- StageMate teaser (Week 4)

### PHASE 2: Week 2 Launch (Polish & Scale)
- [ ] Implement weighted dimensions
- [ ] Advanced photo quality detection
- [ ] Photographer referral network live
- [ ] Budget alternative tiers in shopping lists
- [ ] Improved affiliate tracking

---

## RACHEL'S ACTION ITEMS (Due Friday)

**TODAY (Wednesday):**
- [ ] Activate affiliate accounts (Amazon, Wayfair, IKEA)
- [ ] Continue property report reviews (Brown Town feedback complete, 7 more to go)

**THURSDAY:**
- [ ] Complete all 8 property report reviews
- [ ] Film 10+ TikTok videos (batch production)
- [ ] Share final feedback on scoring
- [ ] Approve dimension weighting adjustments

**FRIDAY (Launch Day):**
- [ ] Share affiliate account IDs with Hedy
- [ ] Post first 2 TikTok videos (6 AM + 6 PM UTC)
- [ ] Monitor first submissions
- [ ] Activate Typeform
- [ ] Go live!

---

## HEDY'S ACTION ITEMS (Due Friday)

**TODAY (Wednesday):**
- [ ] Log Brown Town feedback
- [ ] Create photographer referral strategy doc
- [ ] Prepare dimension weighting implementation

**THURSDAY:**
- [ ] Receive Rachel's remaining 7 property reviews
- [ ] Implement weighted dimensions
- [ ] Implement colour/lighting recalibrations
- [ ] Inject working affiliate links (once Rachel provides IDs)
- [ ] Deploy backend to DigitalOcean
- [ ] Test end-to-end workflow
- [ ] Prepare launch checklist

**FRIDAY (Launch Day):**
- [ ] Final deployment
- [ ] Monitor system (performance, errors)
- [ ] Support Rachel with first submissions
- [ ] Track initial metrics (reports generated, affiliate clicks)

---

## LAUNCH DAY CHECKLIST (Friday 2026-04-05)

### 6:00 AM UTC
- [ ] Verify all systems operational
- [ ] Test report generation
- [ ] Rachel posts first TikTok video
- [ ] Activate Typeform live

### 9:00 AM UTC
- [ ] Monitor first submissions
- [ ] Check email delivery
- [ ] Verify affiliate links working

### 6:00 PM UTC
- [ ] Rachel posts second TikTok video
- [ ] Check metrics (reports, affiliate clicks)
- [ ] Monitor reviews

### 11:59 PM UTC
- [ ] End of day summary
- [ ] Note any critical issues
- [ ] Plan Friday → Saturday support

---

## SUCCESS METRICS (First Week)

### Conservative Target
- 10–20 Design Diagnosis reports submitted
- 5–10 affiliate clicks
- 100–200 TikTok followers gained
- 0 critical errors

### Moderate Target
- 30–50 reports submitted
- 15–25 affiliate clicks
- 500–1,000 followers gained
- 1–2 minor issues (fixed same day)

### Aggressive Target
- 100+ reports submitted
- 50+ affiliate clicks
- 2,000+ followers gained
- One viral video (>100K views)

---

## Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Affiliate accounts not active | HIGH | CRITICAL | Fallback: Generic "Shop on Amazon" button |
| Email system broken | MEDIUM | CRITICAL | Test Thursday morning |
| Typeform integration fails | LOW | HIGH | Manual email submission fallback |
| Scoring feedback incomplete | MEDIUM | MEDIUM | Launch with current weights, refine Week 2 |
| TikTok videos don't post | LOW | MEDIUM | Manual schedule Tuesday if needed |
| Server crashes under load | LOW | HIGH | DigitalOcean autoscaling configured |

---

## Go/No-Go Decision (Friday 6:00 AM)

**GO if:**
✅ Affiliate links working  
✅ Backend deployed + tested  
✅ Email system operational  
✅ Typeform live  
✅ First TikTok posted  

**NO-GO if:**
❌ Affiliate links broken (unfixable)  
❌ Backend crashes on test  
❌ Email system broken  

**PARTIAL LAUNCH if:**
⚠️ 1–2 issues minor (proceed with monitoring)  

---

**Status: ON TRACK. All critical items have clear ownership + deadlines. Ready for Friday launch.** 🚀
