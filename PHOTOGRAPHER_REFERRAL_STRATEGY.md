# Photographer Referral Strategy for Design Diagnosis

**Author:** Rachel + Hedy  
**Date:** 2026-04-01  
**Purpose:** Secondary revenue stream (photographer commissions) + host support  
**Status:** Framework ready, implementation pending affiliate accounts

---

## The Opportunity

### Current State
- Design Diagnosis identifies when hosts need professional photography
- Recommendation: "Hire a professional photographer ($300–500)"
- Host: "OK, but who do I hire?"
- **We have no answer** → Lost opportunity

### New State
- Design Diagnosis identifies photo quality issues
- Recommendation: "Hire a professional photographer via our partner network"
- Host clicks → Referred photographer (gets lead)
- We get 10–20% commission on job
- Win-win-win: Host gets photographer, photographer gets lead, we get revenue

---

## Revenue Model

### Photographer Commission Structure

**Assumption:** Average photography job = $400
- Our commission: 10–20% = $40–80 per referral
- If 10 referrals/month (conservative) = $400–800/month
- If 20 referrals/month (modest) = $800–1,600/month
- If 50 referrals/month (aggressive) = $2,000–4,000/month

**Scaling:** With 1,000+ Design Diagnosis reports/month, photographer referrals = $2K–5K/month passive revenue

---

## Implementation Strategy

### Phase 1: Partner with Local Photographers (Week 1–2)

**Goal:** Find 5–10 professional photographers in key markets (Canada/USA)

**Requirements:**
- Professional portfolio (Instagram/website)
- Experience with Airbnb/vacation rental photography
- Willing to offer referral commission (10–20%)
- Quick turnaround (can shoot within 1 week of referral)

**Approach:**
1. Search Upwork/Fiverr for "Airbnb photography" + filter by reviews (4.9+)
2. Reach out: "We refer hosts in [market] who need photography. Interested in 10% commission per job?"
3. Collect:
   - Photographer name + portfolio link
   - Service area (city/region)
   - Typical cost ($250–600 range)
   - Turnaround time (2–7 days)
   - Email for referral handoff

**Expected outcome:** 5–10 photographers per major city (Vancouver, Calgary, Toronto, Seattle, LA, NYC, etc.)

### Phase 2: Build Referral Network (Week 2–3)

**Create:** Simple photographer database
```json
{
  "photographers": [
    {
      "name": "Sarah Chen Photography",
      "city": "Vancouver, BC",
      "website": "https://sarahchenphotography.com",
      "service_area": "Vancouver, Burnaby, Richmond, Surrey",
      "typical_cost": "$400–500",
      "turnaround": "5–7 days",
      "commission": "15%",
      "email": "sarah@example.com",
      "rating": 4.95,
      "portfolio_photos": 45,
      "airbnb_experience": true
    },
    ...
  ]
}
```

### Phase 3: Integrate into Design Diagnosis App (Week 3–4)

**When app detects poor photo quality:**

**Current recommendation:**
> "Hire a professional photographer ($300–500)"

**New recommendation:**
> "Professional photographers in your area:
> - Sarah Chen Photography (Vancouver) - 5–7 days, $400–500
> - [Link to partner]
> 
> Click to get referred (we earn a small commission, you get a vetted photographer)"

**Technical implementation:**
- Add photographer lookup by postal code/city
- Store referral link + photographer email
- Track referral → payment
- Dashboard shows "pending referrals" + "completed jobs" + "commission earned"

### Phase 4: Track Referrals & Payments (Week 4+)

**Payment flow:**
1. Host clicks "Get Referred"
2. System emails photographer: "You've been referred by Design Diagnosis. Here's the lead."
3. Photographer books the job
4. Upon completion, photographer confirms via email/dashboard
5. We invoice photographer 10–20% commission
6. Track in accounting (recurring revenue model)

---

## Positioning in Design Diagnosis

### In the Vitality Report

**When photo score is low (7/10 or less):**

#### Current Recommendation (Design Issues Only)
```
TOP RECOMMENDATION: Professional Photography
Cost: $300–500
ROI: 15–25% booking increase
Impact: +5 Vitality Score points
```

#### New Recommendation (Design + Referral Network)
```
TOP RECOMMENDATION: Professional Photography
Cost: $300–500
ROI: 15–25% booking increase
Impact: +5 Vitality Score points

NEXT STEP: Connect with a photographer in your area
[Button: "Get Referred to a Photographer"]

Why we recommend this:
- Bad photos kill bookings, no matter how good your design
- Professional photographers know how to show off your space
- Our partner photographers specialize in vacation rentals
```

### In TikTok Content

**Video angles:**
1. "Your photos are costing you money. Here's who to hire."
2. "We partner with professional photographers. Free referral service."
3. "Before/after: DIY photos vs. professional ($400 investment, 20% booking increase)"

---

## Affiliate Terms to Negotiate

### With Photographers

| Term | Details |
|------|---------|
| **Commission rate** | 10–20% per referral (we take from photographer, not host) |
| **Payment terms** | Monthly invoice or quarterly (photographer pays us) |
| **Exclusivity** | Non-exclusive (photographer can join other referral networks) |
| **Territory** | Geographic (photographer agrees to cover X city/region) |
| **Referral limit** | No limit (more referrals = more commission) |
| **Service level** | Photographer agrees to 5–7 day turnaround |
| **Quality** | Photographer provides 30+ professional photos per job |

### Contract Template (Simple)

**Photographer Referral Partner Agreement**

"Design Diagnosis refers hosts who need professional photography services. When a host is referred through our platform and books a job with you, we receive 15% of the job fee as a referral commission. Payment due within 30 days of job completion."

---

## Revenue Projections

### Conservative Scenario (Month 1–3)
- 5 photographers in network
- 2 referrals/month per photographer = 10 referrals total
- $400 average job × 15% commission = $60/referral
- **Monthly revenue: $600**
- **Quarterly: $1,800**

### Moderate Scenario (Month 4–6)
- 15 photographers across 3 major cities
- 3 referrals/month per photographer = 45 referrals total
- **Monthly revenue: $2,700**
- **Quarterly: $8,100**

### Aggressive Scenario (Month 7–12)
- 30 photographers across 10 major cities
- 4 referrals/month per photographer = 120 referrals total
- **Monthly revenue: $7,200**
- **Annual: $86,400**

**Key driver:** As Design Diagnosis scales to 1,000s of reports/month, photographer referral revenue grows passively.

---

## Why This Works

### For Hosts
✅ "I don't know who to hire" → Solved
✅ "How do I know they're good?" → Vetted photographers only
✅ "How much will it cost?" → Price range provided upfront
✅ Free referral service (we absorb cost via photographer commission)

### For Photographers
✅ Steady lead flow (high-quality, pre-qualified leads)
✅ No marketing cost (we send the referral)
✅ Likely higher booking rate (host already knows they need photos)
✅ No exclusivity (can join other networks too)

### For Design Diagnosis
✅ Secondary revenue stream ($600–7,200/month)
✅ Increases host satisfaction (we solve the "who to hire" problem)
✅ Improves reviews ("helped me find a great photographer")
✅ Scalable (no marginal cost per referral)
✅ Passive income (photographers handle the work)

---

## Implementation Checklist

### Week 1–2: Recruit Photographers
- [ ] Search Upwork/Fiverr for photographers
- [ ] Send outreach: "Referral partnership opportunity"
- [ ] Collect photographer info (name, portfolio, cost, turnaround)
- [ ] Goal: 5–10 photographers in 2–3 major cities

### Week 3: Build Database
- [ ] Create photographer directory (JSON/spreadsheet)
- [ ] Organize by city/region
- [ ] Verify portfolio + reviews

### Week 4: Integrate into App
- [ ] Add photographer lookup by postal code
- [ ] Create "Get Referred" button in reports
- [ ] Wire referral tracking (which host → which photographer)
- [ ] Create referral confirmation flow

### Week 5+: Track & Optimize
- [ ] Monitor referral conversion rate (clicks → bookings)
- [ ] Track commission revenue
- [ ] Collect feedback from photographers
- [ ] Scale to more cities/photographers

---

## Future: Expand to Other Services

**Once photographer referral system works, expand to:**
- Professional stagers ($500–1,000 jobs, 10–15% commission)
- Furniture rental companies ($200–500 jobs, 5–10% commission)
- House cleaners ($100–200 jobs, 10% commission)
- Handymen/contractors ($500–2,000 jobs, 5–10% commission)

**Each service = recurring referral revenue stream**

---

## Success Metrics

**Month 1–3:**
- [ ] 5+ photographers in network
- [ ] 10+ referrals sent
- [ ] 3–5 jobs booked (30–50% conversion)
- [ ] $600+ monthly revenue
- [ ] Host satisfaction: "Great photographer recommendation"

**Month 4–6:**
- [ ] 15+ photographers
- [ ] 45+ referrals sent
- [ ] 15–20 jobs booked (30–40% conversion)
- [ ] $2,500+ monthly revenue

**Month 7–12:**
- [ ] 30+ photographers nationwide
- [ ] 120+ referrals/month
- [ ] 40–50 jobs/month booked
- [ ] $6,000+ monthly revenue

---

## Next Steps

1. **Rachel:** Work on affiliate accounts (Amazon, Wayfair, IKEA) — due Friday
2. **Hedy:** Build photographer outreach template + Upwork search strategy
3. **Together (Week 2):** Launch photographer recruitment
4. **Hedy (Week 3–4):** Build photographer database + app integration

---

**This is a smart secondary revenue stream that solves a real host problem: "Who do I hire for professional photography?"**

**Low friction, high value, scalable. Let's do it.** 🚀
