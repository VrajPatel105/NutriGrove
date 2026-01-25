# NutriGrove WhatsApp Nutrition Coach - Deployment Checklist

## Pre-Deployment Checklist

### ✅ Code Quality
- [x] All debug logging removed from production code
- [x] Error handling in place for all API calls
- [x] Conversation history properly serialized/deserialized
- [x] Emoji stripping working for TwiML responses
- [x] Message splitting for WhatsApp 1600 char limit

### ✅ Configuration
- [x] `.env` file configured with all required keys
- [x] `.gitignore` properly excludes sensitive files (.env, *.json)
- [x] Health profile configured in `backend/app/config/user_health_profile.py`
- [x] All API keys valid and working

### ✅ Features Working
- [x] WhatsApp message receiving
- [x] WhatsApp message sending (TwiML responses)
- [x] Claude API integration (model: claude-sonnet-4-5-20250929)
- [x] Function calling (menu search, food logging, etc.)
- [x] Conversation history persistence
- [x] Glucose management protocol enforcement
- [x] Pizza protocol (training day detection)
- [x] Meal sequencing reminders

### ✅ Database
- [x] Supabase connection working
- [x] Tables created: `conversation_state`, `user_profiles`, `food_logs`, etc.
- [x] Database credentials in `.env`

### ✅ External Services
- [x] Twilio WhatsApp sandbox configured
- [x] Webhook URL set in Twilio
- [x] Anthropic API key valid
- [x] Google Sheets API (optional) configured

## Deployment Steps

### 1. Railway Deployment

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize project
railway init

# Add environment variables to Railway dashboard
# Copy all variables from .env file

# Deploy
railway up
```

### 2. Update Twilio Webhook URL

After deployment, update your Twilio WhatsApp webhook URL:
1. Go to Twilio Console → Messaging → Settings → WhatsApp Sandbox
2. Update "WHEN A MESSAGE COMES IN" URL to:
   ```
   https://your-railway-app.up.railway.app/whatsapp-webhook
   ```
3. Method: POST
4. Save

### 3. Test Deployment

Send test messages to WhatsApp:
1. "Hey" - Should get greeting
2. "What should I eat for lunch?" - Should get meal suggestions
3. "Should I have pizza today?" - Should check training day
4. "Give me my lunch plan" - Should generate full meal plan

### 4. Monitor Logs

```bash
railway logs
```

Watch for:
- Successful startup messages
- No errors in conversation agent
- Proper API responses
- No "Done." responses (indicates empty Claude responses)

## Environment Variables Required

```
SUPABASE_URL=your-supabase-url
SUPABASE_ANON_KEY=your-supabase-key
ANTHROPIC_API_KEY=your-anthropic-key
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_WHATSAPP_NUMBER=+14155238886
GEMINI_API_KEY=your-gemini-key (optional)
GOOGLE_SERVICE_ACCOUNT_FILE=/path/to/json (optional)
GOOGLE_SHEET_ID=your-sheet-id (optional)
TIMEZONE=America/New_York
```

## Post-Deployment

### Verify Features
- [ ] Message receiving works
- [ ] Message sending works (not HTTP retrieval failure)
- [ ] Conversation history persists across messages
- [ ] Glucose management reminders appear
- [ ] Pizza protocol enforced correctly
- [ ] Meal suggestions are glucose-conscious

### Monitor for Issues
- [ ] Check Twilio error logs
- [ ] Monitor Railway logs for errors
- [ ] Test with multiple conversation flows
- [ ] Verify no conversation corruption

### Performance
- [ ] Response time < 5 seconds
- [ ] No timeout errors
- [ ] Claude API calls successful
- [ ] Database queries fast

## Troubleshooting

### Issue: "HTTP retrieval failure" on Twilio
**Cause**: Emojis in TwiML response or encoding issues
**Fix**: Emoji stripping is implemented in `whatsapp_handler.py`

### Issue: "Done." responses
**Cause**: Claude returning empty content after function calls
**Fix**: Increased `max_tokens` to 4096, added better error message

### Issue: Conversation history corruption
**Cause**: Improper serialization of tool_use/tool_result blocks
**Fix**: Always save full content structure, not just text

### Issue: Tool_use_id mismatch errors
**Cause**: Inconsistent message history format
**Fix**: Clear conversation history: `python clear_conversation.py`

## Maintenance

### Weekly
- Check Twilio message logs
- Monitor API usage (Anthropic, Twilio)
- Review conversation logs for errors

### Monthly
- Check Supabase database size
- Review and archive old conversation history
- Update menu items if dining hall menu changes

### As Needed
- Update health profile when blood work results arrive (April 2026)
- Adjust calorie/protein targets based on progress
- Add new dietary rules or restrictions

## Support

For issues or questions:
- Check Railway logs: `railway logs`
- Check Twilio logs: https://console.twilio.com/
- Review conversation state in Supabase
- Clear corrupted history: `python clear_conversation.py`

## Success Criteria

✅ System is ready for deployment when:
1. All checklist items above are complete
2. Test messages work end-to-end
3. No "Done." or error responses
4. Glucose management rules enforced
5. Conversation history persists correctly
6. No HTTP retrieval failures on Twilio
