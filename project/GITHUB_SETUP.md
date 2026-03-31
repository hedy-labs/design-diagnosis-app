# GitHub Setup Guide (For Beginners)

**What is GitHub?**
Think of it as a "backup drive + collaboration tool" for your code. It saves your files in the cloud, tracks all changes (who changed what, when), and lets multiple people work on the same project without overwriting each other.

**Why you need it:**
- Backup (if your laptop dies, your code is safe)
- History (you can see every change ever made)
- Collaboration (your developer can work on the code while you work on content)
- Sharing (easy to show people your progress)

---

## Step 1: Create a GitHub Account

1. Go to **https://github.com**
2. Click **"Sign up"** (top right)
3. Enter your email (use one you check regularly)
4. Create a password (strong password, save it)
5. Choose username: `roomsbyrachel` or `vitality-score` (no spaces)
6. Choose "Free" plan (sufficient for now)
7. Verify email

---

## Step 2: Create Your First Repository

1. Log in to GitHub
2. Click **"+"** icon (top right) → **"New repository"**
3. Fill in:
   - **Repository name:** `vitality-score-app` (or similar)
   - **Description:** "AI tool to score and improve Airbnb listings"
   - **Public** (so others can see it, good for credibility)
   - ✅ Check "Add a README file"
   - ✅ Check "Add .gitignore" → Choose "Python"
   - ✅ Check "Choose a license" → MIT License (beginner-friendly)
4. Click **"Create repository"**

Done! You now have a GitHub repo.

---

## Step 3: Upload Your Project Files

**Option A: Web Upload (Easiest for Beginners)**

1. Open your new repository (you're in it)
2. Click green button **"< > Code"** → **"Upload files"**
3. Drag and drop these files:
   - EXECUTIVE_SUMMARY.md
   - LAUNCH_PLAN_WEEK_1.md
   - BRAND_AUDIT_AND_STRATEGY.md
   - AMPANG_VITALITY_REPORT.md
   - EXPERIENCE_LOGIC.md
   - SHOPPING_LISTS.md
   - vitality_score.py
   - api_manager.py
   - vitality_integration.py
4. Click **"Commit changes"** (with default message)

Done! All files are now on GitHub.

**Option B: Desktop Git (More Powerful, Steeper Learning Curve)**

Skip this for now. Come back to it after you've done Option A and want to learn more.

---

## Step 4: Understanding the Basics

**What just happened:**
- Your files are now in the cloud ☁️
- You can access them from any computer
- Your developer can see your code
- GitHub tracks every change

**Key terms (don't memorize, just know):**
- **Repository (Repo):** Your project folder on GitHub
- **Commit:** Saving a version of your files with a message ("Updated bios")
- **Branch:** A copy of your code where you can test changes without breaking the main version
- **Push:** Uploading changes to GitHub
- **Pull:** Downloading changes from GitHub

---

## Step 5: How Your Developer Will Use This

Your developer (or AI assistant) can:
1. See all the code (transparency)
2. Make changes in a safe way (branches, so they don't break anything)
3. Leave comments on specific lines of code (collaboration)
4. See the full history (who changed what, when, why)

**For your workflow:**
- You keep the **main** branch clean (this is your "production" version)
- Developer works on **feature branches** (e.g., `backend-integration`, `frontend-ui`)
- When feature is done, they request to "merge" it back to main
- You review + approve

---

## Step 6: Quick Commands (If You Go CLI Route Later)

```bash
# Clone a repo to your computer
git clone https://github.com/yourusername/vitality-score-app.git

# Make changes, then save them
git add .
git commit -m "Updated README"
git push

# Pull latest changes from GitHub
git pull
```

But honestly? Don't worry about this yet. Use the web interface for now.

---

## Step 7: Sharing Your Repo

Once files are uploaded, share the link:

```
https://github.com/yourusername/vitality-score-app
```

Your developer, investors, or partners can see:
- All your code
- Full history of changes
- Issues/bugs you've logged
- Roadmap/planning

---

## GitHub Best Practices (For Later)

1. **Commit messages should be clear:** "Fixed rate limit bug" (not "asdf")
2. **Keep secrets out:** Never commit API keys, passwords, or affiliate IDs
3. **Use branches:** Main branch stays clean, features go on separate branches
4. **README is important:** It's the first thing people see (like a welcome sign)

---

## TL;DR for Right Now

1. Go to github.com
2. Sign up (free account)
3. Create repo called `vitality-score-app`
4. Upload your project files via web interface
5. Share the link with your developer

**That's it.** You're done. Everything else is optional details.

---

## Next Steps

After you upload files to GitHub:
1. Send the repo link to your developer
2. They'll review the code
3. They might ask you to create a `.env` file (for secrets/config)
4. You two can collaborate on the same code without stepping on each other

---

**Questions?** Ask Hedy. But for now: GitHub = "cloud backup + collaboration tool." That's all you need to know.
