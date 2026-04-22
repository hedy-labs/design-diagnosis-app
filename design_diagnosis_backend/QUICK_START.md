# Quick Start — Phase 2 Testing

Get the backend running in **5 minutes**.

## 1. Install

```bash
cd design_diagnosis_backend
pip install -r requirements.txt
```

## 2. Run Backend

```bash
python main.py
```

You should see:
```
🚀 Design Diagnosis Backend (Phase 2) starting...
   Email Service: ⚠️  Mock Mode
   Stripe: ⚠️  Mock Mode
   Report Output: ./design-diagnosis-app/reports
   Base URL: http://localhost:8000
```

Backend is running on `http://localhost:8000`

## 3. Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "ok",
  "phase": "2",
  "services": {
    "email": "mock",
    "stripe": "mock"
  }
}
```

## 4. Test Complete Flow (Free Report)

### Step 1: Submit Form
```bash
curl -X POST http://localhost:8000/api/submit-form \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "property_name": "Beautiful Beach House",
    "listing_type": "House",
    "bedrooms": 3,
    "bathrooms": 2,
    "guest_capacity": 6,
    "total_photos": "15-20",
    "guest_comfort_checklist": ["wifi", "linens", "coffee"],
    "report_type": "free"
  }'
```

**Response:** Look for `"submission_id"` and `"status": "verification_pending"`

Example:
```json
{
  "success": true,
  "submission_id": 1,
  "email": "test@example.com",
  "report_type": "free",
  "status": "verification_pending",
  "message": "Verification email sent to test@example.com"
}
```

### Step 2: Get Verification Token
Check the backend console output—it will print the verification link:
```
📧 [MOCK] Email to test@example.com: Verify Your Email — Design Diagnosis Report
```

Copy the token from the backend console (or parse the URL). Example token format: `f47ac10b-58cc-4372-a567-0e02b2c3d479`

### Step 3: Verify Email
```bash
curl "http://localhost:8000/api/verify-email?token=<YOUR_TOKEN>"
```

**Response:**
```json
{
  "success": true,
  "status": "generating",
  "message": "Your free report is being generated and will be sent shortly",
  "next_step": "Check your email in 2-3 minutes"
}
```

### Step 4: Check Report
Once generated, check the file system:
```bash
ls -la design-diagnosis-app/reports/
```

You should see: `Beautiful_Beach_House_1_free.pdf` ✓

---

## 5. Test Premium Flow (with Payment)

### Step 1: Submit Premium Form
```bash
curl -X POST http://localhost:8000/api/submit-form \
  -H "Content-Type: application/json" \
  -d '{
    "email": "premium@example.com",
    "property_name": "Luxury Ocean Villa",
    "listing_type": "House",
    "bedrooms": 4,
    "bathrooms": 3,
    "guest_capacity": 8,
    "total_photos": "21-30",
    "guest_comfort_checklist": ["wifi", "linens", "coffee", "ac", "tv", "parking"],
    "report_type": "premium"
  }'
```

Note the `submission_id` (e.g., `2`)

### Step 2: Verify Email
Get the token from console output, then:
```bash
curl "http://localhost:8000/api/verify-email?token=<TOKEN>"
```

**Response:**
```json
{
  "success": true,
  "status": "payment_required",
  "submission_id": 2,
  "message": "Email verified! Proceeding to payment"
}
```

### Step 3: Create Payment Intent
```bash
curl -X POST http://localhost:8000/api/create-payment \
  -H "Content-Type: application/json" \
  -d '{
    "submission_id": 2,
    "property_name": "Luxury Ocean Villa"
  }'
```

**Response:**
```json
{
  "success": true,
  "payment_id": 1,
  "payment_intent_id": "pi_mock_test_12345",
  "amount": 3900,
  "amount_usd": "$39.00",
  "test_card": "4242 4242 4242 4242"
}
```

### Step 4: Simulate Stripe Webhook
```bash
curl -X POST http://localhost:8000/api/payment-webhook \
  -H "Content-Type: application/json" \
  -H "Stripe-Signature: test" \
  -d '{
    "type": "payment_intent.succeeded",
    "data": {
      "object": {
        "id": "pi_mock_test_12345",
        "status": "succeeded",
        "metadata": {
          "submission_id": 2
        }
      }
    }
  }'
```

**Response:**
```json
{
  "received": true
}
```

### Step 5: Check Premium Report
```bash
ls -la design-diagnosis-app/reports/
```

You should see: `Luxury_Ocean_Villa_2_premium.pdf` ✓

---

## 6. Use the Web Form (HTML)

Open in browser:
```
http://localhost:8000/form.html
```

Or directly from file:
```bash
# macOS
open design-diagnosis-app/form.html

# Linux
xdg-open design-diagnosis-app/form.html

# Windows
start design-diagnosis-app/form.html
```

The form is fully functional:
- ✓ 3-step workflow
- ✓ Property details
- ✓ Guest comfort checklist
- ✓ Email collection
- ✓ Free vs Premium toggle
- ✓ Form validation

---

## 7. Database Inspection

### View all submissions
```bash
sqlite3 design_diagnosis.db "SELECT * FROM form_submissions;"
```

### View verifications
```bash
sqlite3 design_diagnosis.db "SELECT * FROM email_verifications;"
```

### View payments
```bash
sqlite3 design_diagnosis.db "SELECT * FROM payments;"
```

### View report deliveries
```bash
sqlite3 design_diagnosis.db "SELECT * FROM report_deliveries;"
```

---

## 8. Enable Real Email (Optional)

To send actual emails via SendGrid:

1. **Get API key:** https://app.sendgrid.com/settings/api_keys
2. **Export:**
   ```bash
   export SENDGRID_API_KEY=SG.your_key_here
   ```
3. **Restart backend:**
   ```bash
   python main.py
   ```

You should see:
```
Email Service: ✅ SendGrid
```

---

## 9. Enable Real Stripe (Optional)

To test with actual Stripe sandbox:

1. **Get keys:** https://dashboard.stripe.com/test/apikeys
2. **Export:**
   ```bash
   export STRIPE_API_KEY=sk_test_your_key
   export STRIPE_WEBHOOK_SECRET=whsec_your_secret
   ```
3. **Restart backend:**
   ```bash
   python main.py
   ```

You should see:
```
Stripe: ✅ Test Mode
```

Now you can test with real Stripe (in sandbox):
- Create payment intents with real responses
- Test with card `4242 4242 4242 4242`
- Verify webhook signatures

---

## Troubleshooting

### Port Already in Use
```bash
# Kill process on port 8000
lsof -i :8000
kill -9 <PID>
```

### Python Dependency Error
```bash
pip install -r requirements.txt --upgrade
```

### Database Issues
```bash
# Reset database
rm design_diagnosis.db
python main.py  # Will recreate
```

### Form Not Loading
- Check backend is running (`python main.py`)
- Clear browser cache (Cmd+Shift+Delete)
- Try `http://localhost:8000/form.html` in private window

---

## Success Indicators

✅ You're good to go when you see:

1. Backend starts without errors
2. Health check returns status: "ok"
3. Form submission creates database entry
4. Email verification works
5. Free report PDF generated
6. Premium payment intent created
7. Webhook triggers report generation

---

## Next: Full Documentation

For detailed API reference, database schema, email templates, and more:

👉 **Read:** `PHASE2_README.md`

---

_Quick Start — Phase 2 Backend_
