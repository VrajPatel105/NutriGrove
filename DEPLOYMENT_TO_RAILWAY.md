# 🚀 Production Deployment Guide: Railway + GitHub

Complete step-by-step guide to deploy NutriGrove to Railway while keeping sensitive files private.

---

## 🔐 Security First: Handling Google Cloud Credentials

### The Problem
You have `subtle-photon-485303-s9-040abb55a45d.json` containing sensitive Google Cloud credentials.

**NEVER push this to GitHub!** Anyone with access can abuse your Google Cloud account.

### The Solution

#### Step 1: Ensure `.gitignore` is Updated ✅

Your `.gitignore` now includes:
```
# Google Cloud & Sensitive Files
*.json
!requirements*.json
!.github/workflows/*.json
subtle-photon-*.json
```

This prevents the file from being committed to GitHub.

**Verify it's not tracked:**
```bash
git status
```

You should NOT see `subtle-photon-485303-s9-040abb55a45d.json` in the list.

#### Step 2: How to Deploy WITHOUT Committing the File

Your code now supports **two ways** to provide Google credentials:

**A. From File (Local Development)**
```
GOOGLE_SERVICE_ACCOUNT_FILE=subtle-photon-485303-s9-040abb55a45d.json
```
File exists locally, Git ignores it.

**B. From Environment Variable (Railway Production)**
```
GOOGLE_SERVICE_ACCOUNT_JSON={"type": "service_account", "project_id": "subtle-photon-485303", ...}
```
Railway stores the entire JSON content securely in its encrypted Variables system.

---

## 📋 Railway Deployment Checklist

### Prerequisites
- [ ] GitHub account with NutriGrove repository
- [ ] Railway.app account (free)
- [ ] All credentials ready (Supabase, Anthropic, Twilio, Google)
- [ ] `subtle-photon-*.json` in `.gitignore` ✅ (already done!)

---

## 🚢 Step-by-Step Deployment

### Step 1: Prepare Your Repository

```bash
# In your NutriGrove Backend folder
git add .
git commit -m "Update Google services to support environment variable credentials"
git push origin main
```

### Step 2: Create Railway Project

1. Go to [railway.app](https://railway.app)
2. Click "Start a New Project"
3. Select "Deploy from GitHub repo"
4. Authorize Railway to access your GitHub
5. Select your NutriGrove repository
6. Choose main branch

### Step 3: Configure Environment Variables in Railway

Railway Dashboard → Your Project → "Variables" Tab

Copy and paste each from your local `.env`:

```
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_API_KEY=eyJhbGciOiJIUzI1...

ANTHROPIC_API_KEY=sk-ant-v0-xxxxx...

TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxx
TWILIO_WHATSAPP_PHONE=+1415523XXXX

GOOGLE_SHEET_ID=1a2b3c4d5e6f...
GOOGLE_CALENDAR_ID=xxxxx@group.calendar.google.com (optional)

# ⭐ IMPORTANT: Google Cloud Credentials (the secure part!)
GOOGLE_SERVICE_ACCOUNT_JSON=
```

### Step 4: Add Google Cloud Credentials Securely

⚠️ **This is the critical security step!**

1. Open `subtle-photon-485303-s9-040abb55a45d.json` on your computer
2. Copy the **entire JSON content** (everything from `{` to `}`)
3. In Railway Variables, find `GOOGLE_SERVICE_ACCOUNT_JSON`
4. Paste the entire JSON content there
5. Click "Save Variables"

**Result:**
- Your JSON file stays on your computer only ✅
- Railway stores it encrypted in its secure vault ✅
- Code automatically uses it when running on Railway ✅
- GitHub never sees it ✅

### Step 5: Deploy!

Railway automatically detects your Python project:
- Finds `requirements.txt` → installs dependencies
- Finds `run_server.py` → starts the server
- Deployment takes 3-5 minutes

**Monitor the deployment:**
- Railway Dashboard → Deployments tab
- Watch the build and deployment logs
- Should end with "✅ Deployment successful"

### Step 6: Get Your Railway URL

Railway Dashboard → Your Project → "Settings" tab

You'll see something like:
```
https://nutrigrove-production-up-railway.app
```

**This is your public server URL!**

---

## 🔗 Connect Twilio WebHook

Now you need to tell Twilio where your server is.

1. Go to [Twilio Console](https://console.twilio.com)
2. Click "Messaging" → "Try it out" → "WhatsApp Sandbox Settings"
3. Find "WHEN A MESSAGE COMES IN"
4. Enter your Railway URL:
   ```
   https://nutrigrove-production-up-railway.app/whatsapp-webhook
   ```
5. Make sure "HTTP POST" is selected
6. Click "Save"

**Now Twilio sends all incoming WhatsApp messages to your Railway server!**

---

## ✅ Verification

### Test 1: Server is Running
```
Visit: https://nutrigrove-production-up-railway.app/
Expected: {"message": "Hello, This is API system for NutriGrove WhatsApp Nutrition Coach"}
```

### Test 2: Check Logs
Railway → Deployments → Click deployment → View logs

Look for:
- ✅ "Scheduler service started!"
- ✅ "INFO: Uvicorn running on..."
- ❌ No Google credential errors

### Test 3: WhatsApp Message
1. Send via WhatsApp to +1 415 523 8886:
   ```
   hi
   ```
2. Your bot should respond!

---

## 🔄 Making Changes & Updates

### Update Code
```bash
git add .
git commit -m "Your changes"
git push origin main
```
→ Railway automatically redeploys! (Watch Deployments tab)

### Update Environment Variables
1. Railway → Your Project → Variables tab
2. Edit and save
3. Railways auto-redeploys with new variables

### Update Google Credentials (if needed)
1. Get new `subtle-photon-*.json` from Google Cloud
2. Railway → Variables → GOOGLE_SERVICE_ACCOUNT_JSON
3. Paste new JSON content
4. Save

Local `.json` file stays private. Only the JSON content goes to Railway. ✅

---

## 🆘 Troubleshooting

### Issue: "Google credentials error"
**Check:**
1. Is `GOOGLE_SERVICE_ACCOUNT_JSON` set in Railway Variables? (not empty?)
2. Is the JSON valid? (copy-pasted correctly?)
3. Check Railway logs for exact error message

**Fix:**
1. Copy the JSON file again carefully
2. Paste into Railway Variables
3. Save and redeploy

### Issue: Twilio not sending messages
**Check:**
1. Is the webhook URL correct in Twilio?
2. Is it `https://` not `http://`?
3. Is the `/whatsapp-webhook` endpoint exactly right?
4. Check Twilio error logs

### Issue: Supabase connection error
**Check:**
1. Is `SUPABASE_URL` correct? (should start with `https://`)
2. Is `SUPABASE_API_KEY` correct? (should be the anon public key)
3. Are the tables created in Supabase?

### Issue: "Module not found" errors
**Solution:**
1. Check `requirements.txt` is in root directory
2. Railway should auto-install all packages
3. Check Railway build logs

---

## 📊 Monitoring Your Production App

### Check Logs
Railway Dashboard → Deployments tab → Click deployment → Logs

Watch for:
- User messages received
- Processing messages
- API calls to Claude
- Database queries

### Monitor Usage/Costs
- **Supabase**: Dashboard shows database usage
- **Anthropic**: Console shows API usage (~$0.50-1/day per user)
- **Twilio**: Console shows message count
- **Railway**: Free tier includes 5GB bandwidth - more than enough!

---

## 🎉 You're Live!

Your WhatsApp bot is now running on Railway with:
- ✅ Secure credentials (not in Git!)
- ✅ Automatic deployments (push to GitHub = auto-deploy)
- ✅ Production-grade infrastructure
- ✅ Twilio integration ready
- ✅ All scheduled tasks working

### Next Steps:
1. Test all features via WhatsApp
2. Monitor logs for any issues
3. Invite real users
4. Scale confidently knowing credentials are secure!

---

## 📚 Quick Reference

```bash
# Local development (uses .env file)
uvicorn backend.app.api:app --reload

# Check .gitignore is preventing JSON upload
git status

# See what Railway is doing
# Go to: railway.app → Your Project → Deployments

# Update after code changes
git push origin main
# Railway auto-deploys within seconds!
```

---

**Questions?** Check the main [SETUP_GUIDE.md](SETUP_GUIDE.md)
