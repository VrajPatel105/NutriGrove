# 🍽️ NutriGrove WhatsApp Nutrition Coach

**A complete conversational AI nutrition coach system powered by Claude AI, integrated with WhatsApp for real-time meal planning, food logging, and nutrition tracking.**

---

## 🌟 Features

### Core Capabilities

✅ **Morning Meal Plans** (7 AM automated)
- Personalized daily meal plans from UMass Dartmouth dining hall menu
- Optimized for your calorie and protein targets
- Considers dietary restrictions, allergens, and preferences

✅ **Real-Time Conversational AI**
- Natural language food logging: "ate 3 eggs and toast"
- Intelligent meal swapping: "swap the salmon for chicken"
- Smart food suggestions: "what should I eat for lunch?"
- Context-aware responses using Claude AI with function calling

✅ **Smart Food Logging**
- Automatic nutrition lookup from dining hall menu
- External food estimation (Starbucks, snacks, etc.)
- Portion calculation and scaling
- Tracks planned vs actual intake

✅ **Daily Progress Tracking**
- Real-time calorie and protein progress
- Meal adherence scoring
- Remaining macros to hit targets
- Visual progress updates

✅ **Google Sheets Integration** (9 PM automated)
- Daily food logs synced to Google Sheets
- Automatic daily summaries
- Weekly trend analysis
- Exportable nutrition data

✅ **Weekly Check-Ins** (Sunday 8 PM automated)
- Comprehensive weekly nutrition analysis
- Top 5 most eaten foods
- Adherence trends
- Personalized suggestions

✅ **Smart Reminders**
- Meal logging reminders
- Under-target notifications
- Plan confirmation prompts
- Custom scheduled reminders

---

## 🏗️ Architecture

```
WhatsApp User
    ↕ (Twilio)
FastAPI Backend (/whatsapp-webhook)
    ↕
Claude AI Agent (Function Calling)
    ↕
Services:
    • MenuService (token-optimized search)
    • FoodLogger (nutrition tracking)
    • NutritionEstimator (external foods)
    • SheetsService (Google Sheets sync)
    • AnalyticsService (weekly insights)
    • SchedulerService (automated tasks)
    ↕
Supabase Database:
    • user_profiles
    • food_logs
    • daily_summaries
    • conversation_state
    • user_rules
    • scheduled_reminders
```

---

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.10+
- Anthropic API key (Claude)
- Twilio account (free trial works)
- Supabase account (free tier works)
- Google Cloud account (for Sheets)

### 2. Installation

```bash
# Clone repository
cd "NutriGrove Backend"

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your API keys
```

### 3. Database Setup

```bash
# Run SQL migration in Supabase SQL Editor
# Copy contents of: database/migrations/000_run_all_migrations.sql
```

### 4. Run Server

```bash
# Local development
uvicorn backend.app.api:app --reload --host 0.0.0.0 --port 8000

# Production (Railway/Heroku)
# Follow SETUP_GUIDE.md
```

### 5. Configure Twilio

1. Set webhook URL in Twilio console:
   ```
   https://your-server.com/whatsapp-webhook
   ```

2. Send WhatsApp message to your Twilio number
3. Bot responds! 🎉

---

## 📖 Full Documentation

- **[Complete Setup Guide](SETUP_GUIDE.md)** - Step-by-step setup for all services
- **[API Documentation](#api-documentation)** - FastAPI endpoints
- **[Testing Guide](#testing)** - How to run tests

---

## 💬 Usage Examples

### Set Up Profile

```
WhatsApp: Hi! I'm 25 years old, male, 170 lbs, 180cm tall. I want to build muscle. Goal is 2800 calories and 150g protein per day.

Bot: Great! I've set up your profile:
• Age: 25, Male
• Weight: 170 lbs, Height: 180 cm
• Goal: Build muscle
• Targets: 2800 cal, 150g protein

You'll get your first meal plan tomorrow at 7 AM! 🌅
```

### Morning Meal Plan (Automated 7 AM)

```
Bot: 🌅 Good morning! Here's your meal plan for today:

🍳 BREAKFAST
• Scrambled Eggs - 3 eggs
  210cal, 18g protein
• Whole Wheat Toast - 2 slices
  160cal, 8g protein
• Greek Yogurt - 1 cup
  150cal, 20g protein

🥗 LUNCH
• Chicken Alfredo - 2 cups
  900cal, 45g protein
• Side Salad - 1 plate
  100cal, 3g protein

🍽️ DINNER
• Grilled Salmon - 8oz
  400cal, 50g protein
• Brown Rice - 1.5 cups
  330cal, 7g protein
• Steamed Broccoli - 1 cup
  55cal, 4g protein

📊 DAILY TOTALS
• 2805cal / 2800cal target ✅
• 155g protein / 150g target ✅

Reply with any questions or to swap foods! 💬
```

### Food Logging

```
WhatsApp: ate 3 eggs and toast

Bot: ✅ Logged from your plan:
- 3 eggs - 210 cal, 18g protein
- 2 slices toast - 160 cal, 8g protein

Breakfast: 370 cal, 26g protein
Today's progress: 370/2800 cal, 26/150g protein
```

### External Food Logging

```
WhatsApp: ate some Ferrero Rocher

Bot: How many pieces did you eat?

WhatsApp: like 3

Bot: ✅ Logged:
➕ Ferrero Rocher - 3 pieces (219 cal, 3g protein)

Updated: 1739/2800 cal, 82/150g protein
```

### Meal Suggestions

```
WhatsApp: what should i eat for lunch?

Bot: Here are your best lunch options today:

1. 🍗 Chicken Alfredo (900 cal, 45g protein) - Pasta Station
2. 🐟 Grilled Salmon Bowl (650 cal, 40g protein) - Global Kitchen
3. 🥙 Turkey Club Wrap (720 cal, 38g protein) - Deli

Which sounds good?
```

### Food Swapping

```
WhatsApp: swap the salmon for steak

Bot: Got it! Replacing Grilled Salmon (400 cal, 50g protein) with:

🥩 Sirloin Steak - 8oz (450 cal, 52g protein)

Your new dinner total: 890 cal, 68g protein

Updated plan saved! ✅
```

### Daily Progress Check

```
WhatsApp: how am i doing?

Bot: 📊 Today's Progress:

Logged: 2450/2800 cal (88%)
Protein: 138/150g (92%)
Meals: 2/3 logged

Remaining:
• 350 cal
• 12g protein

You're doing great! Have your planned dinner and you'll hit your targets! 💪
```

### Weekly Summary (Automated Sunday 8 PM)

```
Bot: 📊 WEEKLY NUTRITION SUMMARY
Jan 17 - Jan 23, 2025

📈 AVERAGES (7 days)
• Calories: 2750 / 2800 target (-50 cal)
• Protein: 148g / 150g target (-2g)
• Carbs: 310g
• Fat: 85g

✅ ADHERENCE
• Plan adherence: 87%
• Planned meals: 18/21
• Off-campus meals: 3

🍽️ TOP 5 FOODS THIS WEEK
1. Chicken Alfredo (5x)
2. Scrambled Eggs (7x)
3. Greek Yogurt (6x)
4. Brown Rice (5x)
5. Grilled Salmon (4x)

📊 TRENDS
✅ Consistently hitting calorie targets
✅ Meeting protein goals consistently
✅ Excellent plan adherence!

💡 SUGGESTIONS
• Keep up the great work with meal planning! 💪
• You're crushing your nutrition goals! 🎯
```

---

## 🔧 Token Optimization

A key feature is our **smart token optimization** to minimize API costs:

### The Problem
- UMass dining hall menu: 500+ items
- Full nutrition data: 20+ fields per item
- Sending full menu to AI: **100,000+ tokens per request**
- Cost: **$0.30 per request** with Claude Sonnet

### Our Solution
```python
# ❌ BAD: Send full menu (100k tokens)
send_to_ai(all_500_items_with_full_nutrition)

# ✅ GOOD: Filter first, send minimal (500 tokens)
filtered = supabase.query()
    .eq('meal_type', 'lunch')
    .gte('protein_g', 40)
    .limit(10)

send_to_ai(filtered)  # Only 10 items, only essential fields
```

### Results
- **99.5% token reduction** (100k → 500 tokens)
- **Cost per request**: $0.30 → **$0.0015**
- **Response time**: 5s → **0.5s**
- **Same quality** meal suggestions!

---

## 🧪 Testing

Run comprehensive test suite:

```bash
# Run all tests
pytest tests/test_whatsapp_system.py -v

# Run specific test
pytest tests/test_whatsapp_system.py::TestFoodLogger -v

# Run with coverage
pytest tests/test_whatsapp_system.py --cov=backend/app/services
```

Test categories:
- ✅ Unit tests (utilities, parsers)
- ✅ Service tests (menu, logger, analytics)
- ✅ Integration tests (full workflows)
- ✅ Performance tests (token optimization)

---

## 📊 API Documentation

### FastAPI Endpoints

#### `GET /`
Health check

#### `POST /recommendations`
Generate meal plan (existing endpoint)

**Body:**
```json
{
  "age": 25,
  "gender": "male",
  "weight": 170,
  "height": 180,
  "activity_level": "active",
  "goal": "build_muscle",
  "calories": 2800,
  "protein": 150,
  ...
}
```

#### `POST /whatsapp-webhook`
Twilio WhatsApp webhook (handles incoming messages)

**Form Data:**
- `From`: Sender phone number
- `Body`: Message text
- `MessageSid`: Twilio message ID

**Returns:** TwiML response

---

## 🗂️ Project Structure

```
NutriGrove Backend/
├── backend/
│   └── app/
│       ├── api.py                 # FastAPI app & endpoints
│       ├── ai_food_recommendation.py  # Existing Gemini integration
│       ├── database.py            # Supabase client
│       ├── model/
│       │   └── schema.py          # Pydantic models
│       ├── services/              # NEW: All WhatsApp services
│       │   ├── conversational_agent.py    # Claude AI brain
│       │   ├── whatsapp_handler.py        # Twilio integration
│       │   ├── menu_service.py            # Token-optimized search
│       │   ├── food_logger.py             # Food tracking
│       │   ├── nutrition_estimator.py     # External foods
│       │   ├── sheets_service.py          # Google Sheets
│       │   ├── calendar_service.py        # Google Calendar
│       │   ├── reminder_service.py        # Smart reminders
│       │   ├── scheduler_service.py       # Cron jobs
│       │   └── analytics_service.py       # Weekly analysis
│       └── utils/                 # NEW: Utility modules
│           ├── date_parser.py     # Parse dates
│           ├── food_parser.py     # Parse food text
│           └── portion_calculator.py  # Scale portions
├── database/
│   ├── migrations/                # SQL scripts
│   │   ├── 000_run_all_migrations.sql   # Master script
│   │   ├── 001_create_user_profiles.sql
│   │   └── ...
│   └── setup_database.py          # Python setup script
├── tests/
│   └── test_whatsapp_system.py    # Comprehensive tests
├── .env.example                   # Environment template
├── SETUP_GUIDE.md                 # Complete setup guide
├── WHATSAPP_README.md             # This file
└── requirements.txt               # Dependencies
```

---

## 💰 Cost Breakdown

### Per Active User Per Day

| Service | Cost | Notes |
|---------|------|-------|
| **Anthropic Claude** | $0.50-1.00 | ~20-30 API calls/day with token optimization |
| **Twilio WhatsApp** | $0.30-0.50 | ~$0.005 per message, 60-100 messages/day |
| **Supabase** | $0.00 | Free tier (up to 500MB) |
| **Google Sheets/Calendar** | $0.00 | Free |
| **Total** | **$0.80-1.50** | Very affordable! |

### Ways to Reduce Costs

1. **Use Haiku model** for simple responses ($0.25/1M tokens vs $3/1M)
2. **Cache menu data** (already implemented)
3. **Batch API calls** (already optimized)
4. **Use Twilio free tier** during development

---

## 🤝 Contributing

This is a personal project, but suggestions welcome!

1. Test the system
2. Find bugs or improvements
3. Create an issue or PR
4. Improve documentation

---

## 📝 License

Built for educational purposes at UMass Dartmouth.

---

## 👨‍💻 Author

**Vraj Patel**
UMass Dartmouth Student
Nutrition enthusiast & developer

---

## 🙏 Acknowledgments

- **Anthropic** - Claude AI API
- **Twilio** - WhatsApp Business API
- **Supabase** - Database & backend
- **Google** - Sheets & Calendar APIs
- **UMass Dartmouth** - Dining hall menu data

---

## 📞 Support

Having issues? Check:

1. [Setup Guide](SETUP_GUIDE.md) - Complete setup instructions
2. [Troubleshooting](#troubleshooting-in-setup-guide)
3. Server logs for error messages
4. Test suite to verify setup

---

**Built with ❤️ for better nutrition tracking**
