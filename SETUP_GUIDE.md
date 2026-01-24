# 🚀 NutriGrove WhatsApp Nutrition Coach - Complete Setup Guide

Welcome! This guide will walk you through setting up your complete WhatsApp conversational AI nutrition coach system from scratch.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Database Setup (Supabase)](#1-database-setup-supabase)
3. [Anthropic Claude API](#2-anthropic-claude-api)
4. [Twilio WhatsApp Setup](#3-twilio-whatsapp-setup)
5. [Google Cloud Setup (Sheets & Calendar)](#4-google-cloud-setup)
6. [Install Dependencies](#5-install-dependencies)
7. [Environment Configuration](#6-environment-configuration)
8. [Deploy Your Server](#7-deploy-your-server)
9. [Testing](#8-testing)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before starting, make sure you have:

- ✅ Python 3.10 or higher installed
- ✅ A Supabase account (free tier works!)
- ✅ An Anthropic API account (you mentioned you have Claude Pro)
- ✅ A Twilio account (free trial available)
- ✅ A Google Cloud account (free tier works!)
- ✅ Git installed
- ✅ A code editor (VS Code recommended)

---

## 1. Database Setup (Supabase)

### Step 1.1: Create Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Click "Start your project"
3. Create a new organization (if you don't have one)
4. Click "New project"
5. Fill in:
   - **Project name**: `nutrigrove-whatsapp`
   - **Database Password**: Choose a strong password (save it!)
   - **Region**: Choose closest to you
6. Click "Create new project"
7. Wait ~2 minutes for setup to complete

### Step 1.2: Get Your Supabase Credentials

1. In your Supabase project dashboard, click "Settings" (gear icon in sidebar)
2. Click "API" in the left menu
3. Copy these values:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **Project API Key (anon public)**: `eyJhbGciOiJIUzI1...`
4. Save these - you'll add them to `.env` later

### Step 1.3: Create Database Tables

1. In Supabase dashboard, click "SQL Editor" in sidebar
2. Click "New query"
3. Open the file `database/migrations/000_run_all_migrations.sql` from this project
4. Copy the entire contents
5. Paste into the SQL Editor
6. Click "Run" (or press Ctrl+Enter)
7. You should see: "SUCCESS! All 6 tables created successfully"

**Tables created:**
- ✅ `user_profiles` - User info and nutrition targets
- ✅ `food_logs` - Daily food intake tracking
- ✅ `daily_summaries` - End of day totals
- ✅ `user_rules` - Custom user preferences
- ✅ `conversation_state` - AI conversation context
- ✅ `scheduled_reminders` - Smart reminder settings

### Step 1.4: Verify Tables

1. Click "Table Editor" in Supabase sidebar
2. You should see all 6 new tables listed
3. Click on each to verify structure

✅ **Database setup complete!**

---

## 2. Anthropic Claude API

You mentioned you have Claude Pro, so this should be easy!

### Step 2.1: Get API Key

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign in with your Anthropic account
3. Click "API Keys" in the left sidebar
4. Click "Create Key"
5. Give it a name: `nutrigrove-whatsapp-coach`
6. Copy the API key (starts with `sk-ant-...`)
7. **Save it immediately** - you can't see it again!

### Step 2.2: Add Credits (if needed)

1. Click "Billing" in console
2. Add at least $5-10 to start
3. Claude API pricing:
   - Sonnet 4: ~$3 per million input tokens
   - With our token optimization, expect ~$0.50-1.00 per day for one user

✅ **Claude API ready!**

---

## 3. Twilio WhatsApp Setup

### Step 3.1: Create Twilio Account

1. Go to [twilio.com/try-twilio](https://www.twilio.com/try-twilio)
2. Sign up for free trial (gives you $15 credit)
3. Verify your phone number

### Step 3.2: Activate WhatsApp Sandbox

1. After signing up, you'll be in Twilio Console
2. In left sidebar, click "Messaging" → "Try it out" → "Send a WhatsApp message"
3. You'll see instructions like:
   ```
   Join your sandbox by sending:
   join <your-code-here>
   to: +1 415 523 8886
   ```
4. Open WhatsApp on your phone
5. Send that join message to +1 415 523 8886
6. You'll get a confirmation message

### Step 3.3: Get Twilio Credentials

1. Go to [console.twilio.com](https://console.twilio.com)
2. On the main dashboard, you'll see:
   - **Account SID**: `ACxxxxxxxxxxxxxxxx`
   - **Auth Token**: Click "Show" to reveal
3. Copy both values

### Step 3.4: Configure Webhook (IMPORTANT - Do this AFTER deploying your server)

**Note**: You'll do this in Step 7 after deploying. For now, just understand what's needed.

We'll configure Twilio to send incoming WhatsApp messages to your server's `/whatsapp-webhook` endpoint.

✅ **Twilio account ready!** (webhook configuration pending deployment)

---

## 4. Google Cloud Setup

We'll set up Google Sheets and Calendar integration.

### Step 4.1: Create Google Cloud Project

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Click "Select a project" → "New Project"
3. Project name: `nutrigrove-whatsapp`
4. Click "Create"
5. Wait for project to be created, then select it

### Step 4.2: Enable APIs

1. In Google Cloud Console, go to "APIs & Services" → "Library"
2. Search for "Google Sheets API"
3. Click it, then click "Enable"
4. Go back to Library
5. Search for "Google Calendar API"
6. Click it, then click "Enable"

### Step 4.3: Create Service Account

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "Service Account"
3. Fill in:
   - **Service account name**: `nutrigrove-bot`
   - **Service account ID**: (auto-filled)
4. Click "Create and Continue"
5. For role, select "Editor" (or "Owner" for full access)
6. Click "Continue" → "Done"

### Step 4.4: Create Service Account Key

1. In Credentials page, click on your new service account email
2. Click "Keys" tab
3. Click "Add Key" → "Create new key"
4. Select "JSON"
5. Click "Create"
6. A JSON file will download - **SAVE THIS FILE!**
7. Rename it to `google-service-account.json`
8. Move it to your project root: `NutriGrove Backend/google-service-account.json`

### Step 4.5: Create Google Sheet for Food Diary

1. Go to [sheets.google.com](https://sheets.google.com)
2. Click "Blank" to create new spreadsheet
3. Name it "NutriGrove Food Diary"
4. Click "Share" button
5. Add your service account email (from step 4.3, looks like `nutrigrove-bot@xxx.iam.gserviceaccount.com`)
6. Give it "Editor" access
7. Click "Send"
8. Copy the Sheet ID from URL:
   ```
   https://docs.google.com/spreadsheets/d/SHEET_ID_HERE/edit
                                            ^^^^^^^^^^^
   ```
9. Save this Sheet ID

### Step 4.6: Setup Google Calendar (Optional)

1. Open Google Calendar
2. Create a new calendar called "Meal Plans"
3. Click settings → "Share with specific people"
4. Add your service account email with "Make changes to events" permission
5. Get Calendar ID:
   - Go to calendar settings
   - Scroll to "Integrate calendar"
   - Copy the "Calendar ID"

✅ **Google Cloud setup complete!**

---

## 5. Install Dependencies

### Step 5.1: Navigate to Project

```bash
cd "c:\My Projects\Coding Projects\NutriGrove\NutriGrove Backend"
```

### Step 5.2: Create Virtual Environment (Recommended)

```bash
python -m venv venv
```

Activate it:
- **Windows**: `venv\Scripts\activate`
- **Mac/Linux**: `source venv/bin/activate`

### Step 5.3: Install All Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- FastAPI (web framework)
- Anthropic (Claude AI)
- Twilio (WhatsApp)
- Google APIs (Sheets, Calendar)
- Supabase (database)
- APScheduler (scheduled jobs)
- And many more!

Wait ~2-3 minutes for installation to complete.

✅ **Dependencies installed!**

---

## 6. Environment Configuration

### Step 6.1: Create .env File

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Or manually create a new file named `.env` in project root

### Step 6.2: Fill In Your Credentials

Open `.env` in your editor and fill in ALL the values you collected:

```env
# SUPABASE (from Step 1.2)
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIs...

# ANTHROPIC (from Step 2.1)
ANTHROPIC_API_KEY=sk-ant-api03-xxx...

# TWILIO (from Step 3.3)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_WHATSAPP_NUMBER=+14155238886

# GOOGLE (from Steps 4.4 and 4.5)
GOOGLE_SERVICE_ACCOUNT_FILE=google-service-account.json
GOOGLE_SHEET_ID=your_sheet_id_from_step_4.5
GOOGLE_CALENDAR_ID=your_calendar_id_or_primary

# GEMINI (you already have this from your existing setup)
GEMINI_API_KEY=your_existing_gemini_key
```

### Step 6.3: Verify Service Account File

Make sure `google-service-account.json` is in your project root and the path in `.env` is correct.

✅ **Environment configured!**

---

## 7. Deploy Your Server

You have several deployment options. Here are the most common:

### Option A: Run Locally for Testing (EASIEST)

1. In your project directory, run:
   ```bash
   uvicorn backend.app.api:app --reload --host 0.0.0.0 --port 8000
   ```

2. You should see:
   ```
   INFO:     Uvicorn running on http://0.0.0.0:8000
   INFO:     Scheduler service started!
   ```

3. Test the API:
   - Open browser to `http://localhost:8000`
   - You should see: `{"message": "Hello, This is API system for NutriGrove WhatsApp Nutrition Coach"}`

4. **To make it accessible from internet (for Twilio webhook):**

   Install ngrok:
   ```bash
   # Windows (with Chocolatey)
   choco install ngrok

   # Or download from ngrok.com
   ```

   Run ngrok:
   ```bash
   ngrok http 8000
   ```

   You'll get a public URL like: `https://abcd-123-45-67-89.ngrok.io`

   **This is your webhook URL!**

### Option B: Deploy to Railway (RECOMMENDED for Production)

**Why Railway?** Free tier supports deployment, easy GitHub integration, and secure environment variable handling. Perfect for production!

#### Step B.1: Create Railway Account & Link GitHub

1. Go to [railway.app](https://railway.app)
2. Click "Start Project"
3. Select "Deploy from GitHub repo"
4. Authorize Railway to access GitHub
5. Select your NutriGrove repository

#### Step B.2: Add Environment Variables (SECURE CREDENTIALS HANDLING)

⚠️ **IMPORTANT**: Never commit `subtle-photon-*.json` to GitHub!

1. In Railway dashboard, click your project → "Variables" tab
2. Add each variable from your `.env` file
3. **For Google Cloud credentials** (the secure part):
   - You have TWO options:

   **Option B.2a: Use Environment Variable (RECOMMENDED - Most Secure)**
   - Variable name: `GOOGLE_SERVICE_ACCOUNT_JSON`
   - Variable value: Open `subtle-photon-485303-s9-040abb55a45d.json` and paste the **entire JSON content** (not the file path!)
   - The code will automatically use this for production

   **Option B.2b: Keep using file path**
   - Variable name: `GOOGLE_SERVICE_ACCOUNT_FILE`
   - Value: `google-service-account.json` (and manually upload the file)
   - ⚠️ Not recommended as it defeats the purpose

4. Add other variables:
   ```
   SUPABASE_URL=your-supabase-url
   SUPABASE_API_KEY=your-api-key
   ANTHROPIC_API_KEY=your-anthropic-key
   TWILIO_ACCOUNT_SID=your-sid
   TWILIO_AUTH_TOKEN=your-token
   TWILIO_WHATSAPP_PHONE=+1415523XXXX
   GOOGLE_SHEET_ID=your-sheet-id
   GOOGLE_CALENDAR_ID=your-calendar-id (optional)
   GOOGLE_SERVICE_ACCOUNT_JSON={"type": "service_account", ...} ← Paste the full JSON here!
   ```

5. Click "Save changes"

#### Step B.3: Deploy!

1. Railway will automatically detect your Python project
2. It will see `requirements.txt` and `run_server.py`
3. Click "Deploy" and wait ~3-5 minutes
4. You'll get a URL: `https://nutrigrove-production.up.railway.app`
5. Check "Deployments" tab to see logs and status

#### Step B.4: Verify Deployment

1. Visit `https://your-railway-url.com/` in browser
2. Should show: `{"message": "Hello, This is API system for NutriGrove WhatsApp Nutrition Coach"}`
3. Check Railway logs for any errors
4. This URL is now your **public webhook URL** for Twilio!

### Option C: Deploy to Heroku

(Similar process - can provide detailed steps if needed)

### Step 7.1: Configure Twilio Webhook

Now that your server is running on Railway:

1. Go to [Twilio Console](https://console.twilio.com)
2. Go to "Messaging" → "Settings" → "WhatsApp sandbox settings"
3. In "WHEN A MESSAGE COMES IN" field, enter:
   ```
   https://your-railway-url.com/whatsapp-webhook
   ```
   (Replace with your actual Railway URL from Step B.4)
4. Make sure HTTP POST is selected
5. Click "Save"

**Example**: If Railway gave you `https://nutrigrove-production.up.railway.app`, enter:
```
https://nutrigrove-production.up.railway.app/whatsapp-webhook
```

### Step 7.2: Test WhatsApp Integration

1. Open WhatsApp
2. Send a message to +1 415 523 8886:
   ```
   hi
   ```
3. You should get a response from your AI bot!

If it works, your bot will respond conversationally!

✅ **Server deployed and WhatsApp connected!**

---

## 8. Testing

### Test 1: User Profile Setup

Send via WhatsApp:
```
I'm 25 years old, male, 170 lbs, 180 cm tall. I want to build muscle. My goal is 2800 calories and 150g protein per day.
```

Bot should acknowledge and save your profile.

### Test 2: Food Logging

Send:
```
ate 3 eggs and toast for breakfast
```

Bot should:
- Log the foods
- Show nutrition totals
- Display progress vs target

### Test 3: Meal Suggestions

Send:
```
what should i eat for lunch?
```

Bot should:
- Search the menu
- Suggest 3-5 options with nutrition
- Ask which you prefer

### Test 4: Check Daily Progress

Send:
```
how am i doing today?
```

Bot should show:
- Calories logged vs target
- Protein logged vs target
- Meals logged
- Adherence score

### Test 5: Morning Meal Plan (Scheduled)

Wait until 7 AM or manually trigger:

```python
# In Python console
from backend.app.services.scheduler_service import SchedulerService
scheduler = SchedulerService()
await scheduler.send_morning_plans()
```

You should receive a WhatsApp message with your daily meal plan!

✅ **All tests passing!**

---

## Troubleshooting

### Issue: "Module not found" errors

**Solution**:
```bash
pip install -r requirements.txt --upgrade
```

### Issue: Twilio webhook not working

**Checklist**:
- ✅ Is your server running?
- ✅ Is ngrok running (if testing locally)?
- ✅ Did you configure the webhook URL in Twilio?
- ✅ Is the URL correct (https, not http)?
- ✅ Check Twilio logs: Console → Monitor → Logs → Errors

### Issue: Claude API errors

**Checklist**:
- ✅ Is your API key correct in `.env`?
- ✅ Do you have credits in your Anthropic account?
- ✅ Check: `echo $ANTHROPIC_API_KEY` (should show your key)

### Issue: Supabase connection errors

**Checklist**:
- ✅ Is your Supabase URL correct?
- ✅ Is your API key the **anon public** key (not service role)?
- ✅ Are all tables created?
- ✅ Check Supabase logs in dashboard

### Issue: Google Sheets not syncing

**Checklist**:
- ✅ Is service account email added to the Sheet with Editor access?
- ✅ Is `google-service-account.json` file in correct location?
- ✅ Is `GOOGLE_SHEET_ID` correct in `.env`?
- ✅ Check file permissions

### Issue: Scheduler not running

**Check**:
```python
# Add this to api.py startup to verify
print("Scheduler jobs:")
for job in scheduler.scheduler.get_jobs():
    print(f"  {job.name} - Next: {job.next_run_time}")
```

### Getting Help

If you're stuck:

1. Check the logs:
   ```bash
   # Your server logs show errors
   ```

2. Test individual services:
   ```python
   # Test menu service
   from backend.app.services.menu_service import MenuService
   menu = MenuService()
   result = await menu.search_menu_minimal(meal_type="lunch")
   print(result)
   ```

3. Create an issue on GitHub (if this is a GitHub project)

4. Check error messages carefully - they usually tell you what's wrong!

---

## 🎉 You're Done!

Your complete WhatsApp nutrition coach is now live!

### What happens now:

- **Every morning at 7 AM**: Users get a personalized meal plan
- **Throughout the day**: Users can chat to log food, ask questions, swap meals
- **Every evening at 9 PM**: All logs sync to Google Sheets
- **Every Sunday at 8 PM**: Users get a weekly nutrition summary

### Next Steps:

1. **Add your profile**: Send your info via WhatsApp
2. **Test all features**: Try logging food, asking for suggestions
3. **Invite friends**: They can also join the WhatsApp sandbox
4. **Monitor usage**: Check Anthropic/Twilio dashboards for usage
5. **Customize**: Modify prompts in `conversational_agent.py` to change bot personality

### Costs (Approximate):

- **Supabase**: Free (up to 500MB database)
- **Anthropic**: ~$0.50-1.00 per day per user
- **Twilio**: $0.005 per WhatsApp message (~$0.50/day for active user)
- **Google**: Free (Sheets/Calendar)
- **Total**: ~$1-2 per day for one active user

---

## 📚 Additional Resources

- [Anthropic Claude API Docs](https://docs.anthropic.com/)
- [Twilio WhatsApp API Docs](https://www.twilio.com/docs/whatsapp)
- [Supabase Docs](https://supabase.com/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com/)

---

**Built with ❤️ for UMass Dartmouth students by Vraj Patel**
