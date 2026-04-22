# Deployment Checklist — Phase 2 Backend

Complete this checklist before launching to production.

## Pre-Launch (Development → Staging)

### Code & Dependencies
- [ ] All Phase 2 files created
  - [ ] `main.py` (FastAPI endpoints)
  - [ ] `database.py` (SQLite schema)
  - [ ] `email_service.py` (SendGrid)
  - [ ] `stripe_service.py` (Stripe)
  - [ ] `form.html` (Frontend)
- [ ] `requirements.txt` updated with all dependencies
- [ ] No hardcoded secrets in code
- [ ] Git `.gitignore` includes `*.db`, `.env`

### Local Testing
- [ ] Backend starts without errors (`python main.py`)
- [ ] Health check passes (`GET /health`)
- [ ] All endpoints respond correctly
- [ ] Database schema created successfully
- [ ] PDF generation works locally
- [ ] Test suite passes (`python test_phase2.py`)

### Environment Variables
- [ ] `.env` file created (not in git)
- [ ] Contains:
  - [ ] `SENDGRID_API_KEY` (optional, can be mock)
  - [ ] `STRIPE_API_KEY` (sk_test_...)
  - [ ] `STRIPE_WEBHOOK_SECRET` (whsec_...)
  - [ ] `BASE_URL` (http://localhost:8000 for dev)
  - [ ] `DB_PATH` (optional)

### Database
- [ ] SQLite schema verified
- [ ] All 7 tables created:
  - [ ] `form_submissions`
  - [ ] `email_verifications`
  - [ ] `payments`
  - [ ] `report_deliveries`
  - [ ] `properties`
  - [ ] `reports`
  - [ ] `dimension_scores`
  - [ ] `hidden_friction_items`
- [ ] No migration issues

---

## Staging Deployment

### Infrastructure
- [ ] Server/VPS provisioned (Linux recommended)
- [ ] Python 3.9+ installed
- [ ] Port 8000 (or chosen port) is open
- [ ] SSL certificate installed (HTTPS)
- [ ] Firewall allows inbound traffic

### Database
- [ ] SQLite location writable by app user
- [ ] Or: PostgreSQL installed and accessible
- [ ] Regular backup strategy in place
- [ ] Database user has correct permissions

### Email Service (SendGrid)
- [ ] SendGrid account created and verified
- [ ] API key generated and tested
- [ ] Sender email verified in SendGrid
- [ ] From address matches sender
- [ ] Email templates reviewed

### Payment (Stripe)
- [ ] Stripe test account created
- [ ] API keys (sk_test_) added to `.env`
- [ ] Webhook endpoint registered:
  - [ ] URL: `https://yourdomain.com/api/payment-webhook`
  - [ ] Events: `payment_intent.succeeded`, `payment_intent.payment_failed`
  - [ ] Webhook secret saved to `.env`
- [ ] Test payment flow works end-to-end

### File Storage
- [ ] Report directory exists: `./design-diagnosis-app/reports/`
- [ ] Directory writable by app user
- [ ] Disk space monitored (set alerts for low space)
- [ ] Optional: Backup reports to S3/cloud storage

### Frontend
- [ ] `form.html` accessible at `https://yourdomain.com/form.html`
- [ ] Assets load correctly
- [ ] Form validation works
- [ ] Responsive design tested on mobile

---

## Pre-Launch Checks (Staging → Production)

### Functional Testing
- [ ] Complete free report flow tested
  - [ ] Form → Email verification → PDF delivery
- [ ] Complete premium flow tested
  - [ ] Form → Payment → PDF delivery
- [ ] Email verification emails arrive
- [ ] Report emails have correct PDF attachment
- [ ] All links in emails are correct
- [ ] Database records created correctly
- [ ] Error handling works (invalid inputs, timeouts, etc.)

### Performance & Load
- [ ] Backend responds within 2s for form submission
- [ ] PDF generation doesn't timeout
- [ ] Email delivery under 5 minutes
- [ ] Webhook processing under 1 second
- [ ] Test with 10+ concurrent form submissions
- [ ] Monitor memory/CPU usage

### Security
- [ ] HTTPS enabled (SSL certificate valid)
- [ ] API keys not exposed in logs
- [ ] Webhook signature verified
- [ ] CORS properly configured (not `*` in production)
- [ ] Rate limiting on form endpoint
- [ ] Input validation on all endpoints
- [ ] Sensitive data not logged (emails, tokens)

### Monitoring & Logging
- [ ] Error logging configured
- [ ] Application logs being written
- [ ] Log rotation configured
- [ ] Uptime monitoring set up (e.g., UptimeRobot)
- [ ] Alert system configured for critical errors
- [ ] Database growth monitored

---

## Launch Day

### 1 Hour Before
- [ ] All team members notified
- [ ] Backups taken (database, code)
- [ ] Monitoring dashboards open
- [ ] Incident response plan reviewed

### During Launch
- [ ] Health check passes
- [ ] Test form submission
- [ ] Test email delivery
- [ ] Monitor error logs
- [ ] Monitor performance metrics

### Post-Launch (First 24 Hours)
- [ ] Monitor for errors every 15 minutes
- [ ] Verify all emails being delivered
- [ ] Check database for unexpected records
- [ ] Gather user feedback
- [ ] Be ready to rollback if critical issues

---

## Post-Launch (Ongoing)

### Daily (First Week)
- [ ] Check error logs
- [ ] Verify reports being generated
- [ ] Monitor Stripe webhook events
- [ ] Check SendGrid delivery status
- [ ] Monitor application performance

### Weekly
- [ ] Review database size growth
- [ ] Audit form submissions for anomalies
- [ ] Check payment success rate (target: >99%)
- [ ] Test backup/restore procedure
- [ ] Review user feedback/support tickets

### Monthly
- [ ] Generate performance report
- [ ] Analyze user data (conversion rates, etc.)
- [ ] Plan for optimizations
- [ ] Update security patches
- [ ] Review costs (Stripe, SendGrid)

---

## Stripe Live Mode (After 2 Weeks Successful Testing)

### Approval from Rachel
- [ ] Rachel approves switching to live
- [ ] Business metrics reviewed (beta testing results)
- [ ] Support processes in place

### Setup Live Keys
- [ ] Create Stripe live account
- [ ] Generate `sk_live_...` and `wh_live_...` keys
- [ ] Update `.env` with live keys
- [ ] Update webhook URL to production domain
- [ ] Test webhook with live events (optional test charge)

### Go-Live Checklist
- [ ] Email notification to customers
- [ ] Pricing displayed correctly ($39.00)
- [ ] Payment success message clear
- [ ] Invoice/receipts configured in Stripe
- [ ] Refund process documented
- [ ] Tax handling configured (if needed)

---

## Affiliate Links Setup (Ongoing)

### Amazon Affiliate Links
- [ ] Rachel's affiliate ID obtained
- [ ] URLs inserted in `pdf_report.py`
- [ ] Links tested for clicks and tracking
- [ ] Affiliate dashboard monitored for revenue

### Other Affiliates (Placeholder)
- [ ] Wayfair account setup
- [ ] IKEA account setup
- [ ] Other retail partnerships
- [ ] Links activated when available
- [ ] Update PDF templates with live URLs

---

## Documentation Updates

- [ ] `PHASE2_README.md` matches deployed version
- [ ] API documentation current
- [ ] Email template samples documented
- [ ] Troubleshooting guide updated
- [ ] Runbook created for operations team
- [ ] Incident response plan documented

---

## Rollback Plan

If critical issues occur:

1. **Immediate (< 5 min)**
   - [ ] Stop accepting new form submissions
   - [ ] Notify users (maintenance message)
   - [ ] Alert team

2. **Rollback (5-15 min)**
   - [ ] Revert to previous stable code commit
   - [ ] Restore database from backup
   - [ ] Verify health check passes

3. **Post-Rollback**
   - [ ] Root cause analysis
   - [ ] Fix implemented
   - [ ] Staging testing (full flow)
   - [ ] Relaunch with confidence

---

## Performance Baselines

Target metrics for healthy production:

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Form submission (P95) | < 2s | > 5s |
| PDF generation (P95) | < 10s | > 30s |
| Email delivery | < 5 min | > 15 min |
| Webhook processing | < 1s | > 5s |
| Payment success rate | > 99% | < 95% |
| API uptime | > 99.9% | < 99% |
| Error rate | < 0.1% | > 1% |

---

## Support & Escalation

### Tier 1 (Monitoring)
- Automated alerts for:
  - Error rate spike
  - Payment failures
  - Email delivery issues
  - Uptime loss

### Tier 2 (On-Call)
- Developer on-call schedule
- Escalation path defined
- Incident severity levels (Critical/High/Medium/Low)

### Tier 3 (Escalation)
- Rachel notified for critical issues
- Business impact assessment
- Communication to affected users

---

## Sign-Off

- [ ] Backend lead: ______________________ Date: _____
- [ ] QA/Testing: ______________________ Date: _____
- [ ] Operations: ______________________ Date: _____
- [ ] Rachel (Product Owner): ______________________ Date: _____

---

## Launch Notes

Use this section to document:
- Deployment date/time: ___________
- Team members present: ___________
- Any issues encountered: ___________
- Resolution steps taken: ___________
- Post-launch notes: ___________

---

_Deployment Checklist — Design Diagnosis Phase 2_
_Last Updated: 2026-04-20_
