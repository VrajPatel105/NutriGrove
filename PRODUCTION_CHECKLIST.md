# ✅ Production Deployment Checklist

## Phase 1: Local Verification ✓

### Code Readiness
- [ ] All code committed to Git (locally)
  ```bash
  git status
  # Should show "nothing to commit, working tree clean"
  ```

- [ ] Google credentials file is in `.gitignore`
  ```bash
  git check-ignore subtle-photon-485303-s9-*.json
  # Should respond with path (means it's ignored)
  ```

- [ ] Test local server
  ```bash
  uvicorn backend.app.api:app --reload
  # Should show "INFO: Uvicorn running on http://0.0.0.0:8000"
  ```

### Environment Setup
- [ ] `.env` file exists with all variables
  - [ ] `SUPABASE_URL` ✓
  - [ ] `SUPABASE_API_KEY` ✓
  - [ ] `ANTHROPIC_API_KEY` ✓
  - [ ] `TWILIO_ACCOUNT_SID` ✓
  - [ ] `TWILIO_AUTH_TOKEN` ✓
  - [ ] `TWILIO_WHATSAPP_PHONE` ✓
  - [ ] `GOOGLE_SHEET_ID` ✓
  - [ ] `GOOGLE_CALENDAR_ID` ✓ (optional)
  - [ ] `GOOGLE_SERVICE_ACCOUNT_FILE` ✓

- [ ] Google JSON file exists locally
  - [ ] `subtle-photon-485303-s9-040abb55a45d.json` is present
  - [ ] It has valid JSON content
  - [ ] It's in the root directory

---

## Phase 2: GitHub Push ✓

### Commit Changes
- [ ] Review changes
  ```bash
  git status
  git diff
  ```

- [ ] Commit all updates
  ```bash
  git add .
  git commit -m "Add Railway production deployment with secure credentials handling"
  ```

- [ ] Verify JSON file is NOT in the commit
  ```bash
  git show --stat
  # Should NOT list subtle-photon-*.json
  ```

- [ ] Push to GitHub
  ```bash
  git push origin main
  ```

- [ ] Verify on GitHub website
  - [ ] Go to your repo
  - [ ] Check: No `subtle-photon-*.json` file
  - [ ] Check: No `.env` file
  - [ ] Check: Code files are present ✓

---

## Phase 3: Railway Setup

### Create Railway Project
- [ ] Go to https://railway.app
- [ ] Sign in with GitHub
- [ ] Click "Start New Project"
- [ ] Select "Deploy from GitHub repo"
- [ ] Authorize Railway to access GitHub
- [ ] Select your NutriGrove repository
- [ ] Select `main` branch
- [ ] Click "Deploy"

### Monitor Initial Deployment
- [ ] Check Deployments tab
- [ ] Wait for build to complete (3-5 minutes)
- [ ] Check for any build errors
  - If errors: Check logs and fix locally, then git push
  - If success: Continue

### Get Your Railway URL
- [ ] Railway Dashboard → Your Project → Settings
- [ ] Find "Domains" section
- [ ] Copy your public URL
  ```
  Example: https://nutrigrove-production-up-railway.app
  ```
- [ ] Save this URL - you'll need it for Twilio

---

## Phase 4: Configure Environment Variables in Railway

### Add Variables
- [ ] Railway Dashboard → Your Project → Variables tab

- [ ] Add each variable from your `.env`:

  **Database:**
  - [ ] `SUPABASE_URL` = (copy from .env)
  - [ ] `SUPABASE_API_KEY` = (copy from .env)

  **AI:**
  - [ ] `ANTHROPIC_API_KEY` = (copy from .env)

  **WhatsApp:**
  - [ ] `TWILIO_ACCOUNT_SID` = (copy from .env)
  - [ ] `TWILIO_AUTH_TOKEN` = (copy from .env)
  - [ ] `TWILIO_WHATSAPP_PHONE` = (copy from .env)

  **Google:**
  - [ ] `GOOGLE_SHEET_ID` = (copy from .env)
  - [ ] `GOOGLE_CALENDAR_ID` = (copy from .env, if set)

### Add Google Credentials (⭐ CRITICAL STEP)

- [ ] Open `subtle-photon-485303-s9-040abb55a45d.json` in your text editor

- [ ] Select all content (Ctrl+A)

- [ ] Copy to clipboard (Ctrl+C)

- [ ] In Railway Variables tab:
  - [ ] Variable name: `GOOGLE_SERVICE_ACCOUNT_JSON`
  - [ ] Variable value: Paste the JSON (Ctrl+V)
  - [ ] Click Save

- [ ] Verify it was saved (Railway will show encrypted)

- [ ] Railway auto-redeploys with new variables
  - [ ] Watch Deployments tab for "Build" status
  - [ ] Should complete in 2-3 minutes

---

## Phase 5: Verify Deployment

### Check Server is Running
- [ ] Open browser to your Railway URL:
  ```
  https://your-railway-url/
  ```

- [ ] Expected response:
  ```json
  {"message": "Hello, This is API system for NutriGrove WhatsApp Nutrition Coach"}
  ```

- [ ] If error: Check Railway logs → Deployments → View logs

### Check Logs for Issues
- [ ] Railway → Deployments → Click latest deployment → Logs tab

- [ ] Look for these success messages:
  - [ ] "INFO: Uvicorn running on..." ✓
  - [ ] "INFO: Scheduler service started!" ✓

- [ ] No error messages about credentials ✓

---

## Phase 6: Configure Twilio Webhook

### Set Webhook URL
- [ ] Go to https://console.twilio.com

- [ ] Navigate to: Messaging → Settings → WhatsApp Sandbox Settings

- [ ] In "WHEN A MESSAGE COMES IN" field:
  - [ ] Enter: `https://your-railway-url/whatsapp-webhook`
  - [ ] Example: `https://nutrigrove-production-up-railway.app/whatsapp-webhook`
  - [ ] Make sure it's HTTPS (not HTTP)
  - [ ] Make sure `/whatsapp-webhook` is correct

- [ ] HTTP Method: Ensure "HTTP POST" is selected

- [ ] Click "Save"

- [ ] Verify: Message should show "Webhook updated successfully"

---

## Phase 7: Test WhatsApp Integration

### Send Test Message
- [ ] Open WhatsApp on your phone

- [ ] Send a message to: `+1 415 523 8886`

- [ ] Message content:
  ```
  hi
  ```

- [ ] Wait for response (should be 1-3 seconds)

- [ ] Expected: Bot responds with a greeting

- [ ] If no response:
  - [ ] Check Twilio error logs
  - [ ] Check Railway logs
  - [ ] Verify webhook URL is correct
  - [ ] Verify server is still running

### More Tests
- [ ] Send: "hello" → Bot responds
- [ ] Send: "I'm 25 years old, male..." → Bot acknowledges profile
- [ ] Send: "ate 3 eggs" → Bot logs food
- [ ] Send: "what should I eat?" → Bot suggests meals

---

## Phase 8: Monitor & Maintain

### Daily Monitoring
- [ ] Check Railway logs for errors
- [ ] Check Anthropic API usage/costs
- [ ] Check Twilio message counts
- [ ] Monitor Supabase database size

### Weekly Tasks
- [ ] Review any error messages
- [ ] Check estimated costs
- [ ] Monitor user activity

### Code Updates
- [ ] Make changes locally
- [ ] Test with `uvicorn`
- [ ] Commit: `git add . && git commit -m "..."`
- [ ] Push: `git push origin main`
- [ ] Railway auto-redeploys! ✓

### Credential Updates
- [ ] If credentials expire/change:
  - [ ] Update `.env` locally
  - [ ] Test locally: `uvicorn ...`
  - [ ] If new JSON file from Google:
    - [ ] Copy new JSON content
    - [ ] Paste in Railway → GOOGLE_SERVICE_ACCOUNT_JSON
    - [ ] Click Save → Auto-redeploy
  - [ ] Test with WhatsApp message

---

## ✅ Final Success Checklist

You're done when you can check ALL of these:

- [ ] Code is on GitHub (no secrets)
- [ ] `subtle-photon-*.json` is NOT on GitHub
- [ ] Railway has all environment variables
- [ ] Railway has Google credentials in GOOGLE_SERVICE_ACCOUNT_JSON
- [ ] Railway server is running (URL responds)
- [ ] Twilio webhook is configured
- [ ] WhatsApp bot responds to messages
- [ ] Logs show no credential errors
- [ ] Cost estimates are within budget

---

## 🎉 Deployment Complete!

Once all checks are done, your production system is live and secure!

### What You Have:
- ✅ Production server on Railway
- ✅ Secure credentials (not in GitHub)
- ✅ WhatsApp integration working
- ✅ Automatic deployments on Git push
- ✅ Scheduled tasks running

### Security:
- ✅ Google credentials only in Railway vault (encrypted)
- ✅ Code is public on GitHub (safe)
- ✅ Local files stay private
- ✅ Can safely collaborate

### Next:
- Test all features thoroughly
- Invite real users
- Monitor costs
- Scale as needed

---

## Troubleshooting Guide

### Issue: Server not responding
```
Check:
1. Is Railway deployment "Running"? (green status)
2. Is Deployments tab showing latest code?
3. Are logs showing errors?
4. Is URL correct?
```

### Issue: WhatsApp bot not responding
```
Check:
1. Did you save the Twilio webhook URL?
2. Is it the right URL (with /whatsapp-webhook)?
3. Are there Twilio logs showing errors?
4. Did you join the sandbox? (send "join" message first)
```

### Issue: Google services not working
```
Check:
1. Is GOOGLE_SERVICE_ACCOUNT_JSON set in Railway?
2. Is it the complete JSON (not truncated)?
3. Check Railway logs for "Google" errors
4. Did you update the variable? (auto-redeploy needed)
```

### Issue: Variables not updating
```
Solution:
1. Set variable in Railway UI
2. Click Save (should show "✓ Saved")
3. Check Deployments tab for auto-redeploy
4. Wait 2-3 minutes for deployment
5. Refresh Railway page
```

---

**Good luck with your production deployment! 🚀**
