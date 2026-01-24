# ⚡ Quick Start Guide - NutriGrove WhatsApp Coach

Get up and running in 10 minutes!

## Step 1: Install Dependencies (2 min)

```bash
pip install -r requirements.txt
```

## Step 2: Setup Environment (3 min)

```bash
# Copy example file
cp .env.example .env
```

Edit `.env` and add:
```env
# Minimum required
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_key
ANTHROPIC_API_KEY=your_claude_key
GEMINI_API_KEY=your_gemini_key
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_WHATSAPP_NUMBER=+14155238886
```

## Step 3: Create Database Tables (2 min)

1. Open Supabase dashboard
2. Go to SQL Editor
3. Copy contents of `database/migrations/000_run_all_migrations.sql`
4. Paste and run

## Step 4: Start Server (1 min)

```bash
python run_server.py
```

Or:
```bash
uvicorn backend.app.api:app --reload
```

## Step 5: Setup Twilio Webhook (2 min)

### For local testing:

1. Install ngrok:
   ```bash
   ngrok http 8000
   ```

2. Copy the https URL (e.g., `https://abc123.ngrok.io`)

3. Go to Twilio Console → WhatsApp Sandbox Settings

4. Set webhook URL:
   ```
   https://abc123.ngrok.io/whatsapp-webhook
   ```

5. Save!

## Step 6: Test! 🎉

Send a WhatsApp message to your Twilio sandbox number:

```
Hi!
```

You should get a response from your AI bot!

---

## Next Steps

Try these commands:

```
# Set up your profile
I'm 25 years old, male, 170 lbs, 180cm tall. Goal is 2800 calories and 150g protein.

# Log food
ate 3 eggs and toast

# Get suggestions
what should I eat for lunch?

# Check progress
how am I doing?
```

---

## Troubleshooting

**Bot not responding?**
- Check server logs for errors
- Verify webhook URL in Twilio
- Make sure ngrok is running (if local)

**Database errors?**
- Verify tables created in Supabase
- Check SUPABASE_URL and key in .env

**AI errors?**
- Verify ANTHROPIC_API_KEY in .env
- Check you have credits in Anthropic account

---

## Full Documentation

For complete setup instructions: [SETUP_GUIDE.md](SETUP_GUIDE.md)

For detailed features: [WHATSAPP_README.md](WHATSAPP_README.md)
