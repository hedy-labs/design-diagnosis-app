# CLOUD CREDENTIALS SHOPPING LIST

**For Rachel:** Step-by-step guide to obtain cloud storage credentials

---

## CHOOSE YOUR PROVIDER

### Option A: Cloudflare R2 (RECOMMENDED FOR DESIGN DIAGNOSIS)
- ✅ **Cheaper:** $0.015/GB vs AWS $0.023/GB
- ✅ **Easier setup:** 5 minutes to first bucket
- ✅ **Free egress:** Included (AWS charges $0.09/GB)
- ✅ **Perfect for:** Small-to-medium scale (your use case)
- ✅ **All major features:** Pre-signed URLs, public URLs, versioning

### Option B: AWS S3
- ✅ **Enterprise:** If your company already uses AWS
- ✅ **Scalable:** Unlimited storage, proven at massive scale
- ❌ **More complex:** IAM setup, regions, versioning options
- ❌ **Expensive:** Storage + egress charges add up
- ❌ **Overkill:** For Design Diagnosis at this stage

**RECOMMENDATION:** Use Cloudflare R2 unless you have a strong reason otherwise.

---

## CLOUDFLARE R2 SETUP (5 MINUTES)

### Step 1: Create Cloudflare Account (if needed)
1. Go to https://dash.cloudflare.com/sign-up
2. Sign up with email → verify
3. Skip domain setup (optional for now)

### Step 2: Navigate to R2
1. Go to https://dash.cloudflare.com
2. Left sidebar → **"R2"** (under "Storage")
3. Click **"Create bucket"**

### Step 3: Create Bucket
1. Bucket name: `design-diagnosis`
2. Region: Choose closest to you (e.g., **WNAM** for North America, **WEUR** for Europe)
3. Click **"Create bucket"**
4. Wait 10 seconds...

### Step 4: Generate API Token
1. Left sidebar → **"R2"** → **"Settings"**
2. Scroll to **"API tokens"** section
3. Click **"Create API token"**
4. Fill in:
   - Token name: `design-diagnosis-app`
   - Permission: **"Edit"** (full access to bucket)
   - Bucket: **"design-diagnosis"** (the one you just created)
   - TTL: Leave default (no expiry)
5. Click **"Create API token"**

### Step 5: Copy Credentials
You'll see a screen with:
- **Access Key ID** ← Copy this
- **Secret Access Key** ← Copy this
- **Endpoint URL** ← Copy this (format: `https://xxxxx.r2.cloudflarestorage.com`)

**⚠️ IMPORTANT:** This is the ONLY time you see the secret key. Copy it now and paste into .env immediately.

### Step 6: Get Public URL
1. Go to your bucket: **"R2"** → **"design-diagnosis"**
2. Click **"Settings"**
3. Look for **"Public URL"** section
4. Copy the domain (format: `https://xxxxx.r2.cloudflarestorage.com`)

### Step 7: Fill .env Variables
In your `.env` file, add:
```
CLOUD_STORAGE_PROVIDER=r2
CLOUD_STORAGE_ACCESS_KEY=<your Access Key ID>
CLOUD_STORAGE_SECRET_KEY=<your Secret Access Key>
CLOUD_STORAGE_BUCKET_NAME=design-diagnosis
CLOUD_STORAGE_ENDPOINT_URL=<your Endpoint URL>
CLOUD_STORAGE_PUBLIC_URL_BASE=<your Public URL>
```

### Step 8: Test
1. Restart the app
2. Check logs for: `"✅ Cloud storage health check passed: design-diagnosis"`
3. If you see that, you're done! ✅

---

## AWS S3 SETUP (15 MINUTES)

### Step 1: Create AWS Account (if needed)
1. Go to https://aws.amazon.com
2. Click **"Create AWS Account"**
3. Enter email, password, account name
4. Verify email
5. Add payment method (you'll be charged for storage + egress)

### Step 2: Create IAM User
1. Go to https://console.aws.amazon.com
2. Search for **"IAM"** in top search bar
3. Left sidebar → **"Users"**
4. Click **"Create user"**
5. Username: `design-diagnosis-app`
6. Skip "Add user to group" (we'll add permissions next)
7. Click **"Create user"**

### Step 3: Create Access Key
1. Click the user you just created: `design-diagnosis-app`
2. **"Security credentials"** tab
3. Scroll to **"Access keys"**
4. Click **"Create access key"**
5. Choose: **"Application running outside AWS"**
6. Click **"Create access key"**

You'll see:
- **Access Key ID** ← Copy this
- **Secret Access Key** ← Copy this

**⚠️ IMPORTANT:** Copy the secret key NOW (you can't see it again).

### Step 4: Attach Policy
1. Go to user → **"Add permissions"** → **"Attach policies directly"**
2. Search for: `AmazonS3FullAccess`
3. Check the checkbox
4. Click **"Add permissions"**

### Step 5: Create S3 Bucket
1. Search for **"S3"** in top search bar
2. Click **"Create bucket"**
3. Bucket name: `design-diagnosis` (must be globally unique)
   - If taken, try: `design-diagnosis-yourname-2024`
4. Region: Choose closest to you
5. **Important:** Scroll down, **uncheck** "Block all public access"
   - (We'll use pre-signed URLs, so it's fine)
6. Click **"Create bucket"**

### Step 6: Get Bucket Details
1. Your S3 bucket → **"Properties"**
2. **"Region"** ← Note this (e.g., `us-east-1`)
3. **"Permissions"**
4. Copy the bucket ARN (format: `arn:aws:s3:::design-diagnosis`)

### Step 7: Fill .env Variables
In your `.env` file, add:
```
CLOUD_STORAGE_PROVIDER=s3
CLOUD_STORAGE_ACCESS_KEY=<your Access Key ID>
CLOUD_STORAGE_SECRET_KEY=<your Secret Access Key>
CLOUD_STORAGE_BUCKET_NAME=design-diagnosis
CLOUD_STORAGE_REGION=<your region, e.g., us-east-1>
CLOUD_STORAGE_PUBLIC_URL_BASE=https://design-diagnosis.s3.amazonaws.com
```

### Step 8: Test
1. Restart the app
2. Check logs for: `"✅ AWS S3 client initialized: <region>"`
3. If you see that, you're done! ✅

---

## CREDENTIAL REFERENCE TABLE

| Variable | Cloudflare R2 | AWS S3 |
|---|---|---|
| **CLOUD_STORAGE_PROVIDER** | `r2` | `s3` |
| **CLOUD_STORAGE_ACCESS_KEY** | From API token | IAM Access Key ID |
| **CLOUD_STORAGE_SECRET_KEY** | From API token | IAM Secret Access Key |
| **CLOUD_STORAGE_BUCKET_NAME** | `design-diagnosis` | `design-diagnosis` (or unique name) |
| **CLOUD_STORAGE_ENDPOINT_URL** | `https://xxxxx.r2.cloudflarestorage.com` | _(not used)_ |
| **CLOUD_STORAGE_REGION** | _(not used)_ | `us-east-1` (example) |
| **CLOUD_STORAGE_PUBLIC_URL_BASE** | Bucket's public URL | `https://bucket.s3.amazonaws.com` |

---

## TESTING YOUR SETUP

After adding credentials to `.env`:

### Test 1: Check Logs
```bash
# Restart app and check logs
tail -f app.log | grep -i "cloud"

# Expected output:
# ✅ Cloudflare R2 client initialized: https://xxxxx.r2.cloudflarestorage.com
# OR
# ✅ AWS S3 client initialized: us-east-1
```

### Test 2: Check Health Endpoint
```bash
curl http://localhost:8000/health

# Look for:
# "cloud_storage": "✅ OK"
```

### Test 3: Upload a Photo
1. Go to http://localhost:8000/form.html
2. Fill in property details
3. Upload a photo
4. Check your cloud bucket in the dashboard
5. Photo should appear: `design-diagnosis/uploads/submission_X/...`

---

## TROUBLESHOOTING

### "Cloud storage not configured"
- ❌ Credentials missing from .env
- ✅ Solution: Copy all variables from Section 1 or 2 above

### "Failed to initialize cloud storage client"
- ❌ Credentials are invalid/wrong
- ✅ Solution: Double-check Access Key + Secret Key match exactly
- ✅ Solution: If R2, verify Endpoint URL format

### "AccessDenied" in logs
- ❌ Bucket doesn't exist or API token doesn't have permission
- ✅ Solution: Create bucket, re-generate API token with "Edit" permission

### "Cloud storage health check failed"
- ❌ Network issue or bucket permissions
- ✅ Solution: Restart app, check .env variables again
- ✅ Solution: Verify bucket exists in cloud dashboard

### "Upload fails silently, falls back to server"
- ⚠️ This is expected fallback behavior
- ✅ Check browser console (F12) for fetch errors
- ✅ Check server logs for API endpoint errors
- ✅ Verify pre-signed URL endpoint is working

---

## COST ESTIMATION

### Cloudflare R2
```
Users uploading:  50/month
Avg photos:       10 per submission
Avg size:         5 MB per photo
Storage:          50 × 10 × 5 = 2,500 MB = 2.5 GB
Cost:             2.5 GB × $0.015 = $0.0375/month
API calls:        50 × 10 = 500 calls = negligible
TOTAL:            <$1/month
```

### AWS S3
```
Same scenario:    2.5 GB storage
Storage cost:     2.5 × $0.023 = $0.0575
Egress cost:      2.5 × $0.09 = $0.225 (if you fetch from US)
API requests:     500 × $0.0004 = $0.20
TOTAL:            ~$0.50/month
(Plus CloudFront if you want CDN: +$0.085/GB)
```

**R2 is 5-10x cheaper for this use case.**

---

## NEXT: UPDATE .env AND RESTART

Once you have your credentials:

1. Open `.env` file
2. Add the section from Section 1 or 2 above
3. Save and close
4. Restart the app
5. Check logs for ✅ success message
6. Test uploading a photo
7. Done! ✅

---

## SUPPORT

If you get stuck:
1. Re-read the credential procurement step in your chosen provider
2. Verify credentials in cloud dashboard
3. Check app logs for specific error message
4. Fallback mode will keep app working (server storage) while you troubleshoot

Your app will **NEVER crash** due to missing cloud credentials — it gracefully falls back to server storage.
