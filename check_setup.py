"""
Setup Verification Script
Checks if all required environment variables and dependencies are configured
"""

import os
import sys
import io

# Fix Windows encoding issues
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from dotenv import load_dotenv

def check_environment():
    """Check if all required environment variables are set"""
    load_dotenv()

    print("="*60)
    print("🔍 NutriGrove WhatsApp Coach - Setup Verification")
    print("="*60)
    print()

    required_vars = {
        'SUPABASE_URL': 'Supabase database URL',
        'SUPABASE_ANON_KEY': 'Supabase API key',
        'ANTHROPIC_API_KEY': 'Claude AI API key',
        'GEMINI_API_KEY': 'Google Gemini API key',
    }

    optional_vars = {
        'TWILIO_ACCOUNT_SID': 'Twilio account SID (for WhatsApp)',
        'TWILIO_AUTH_TOKEN': 'Twilio auth token',
        'TWILIO_WHATSAPP_NUMBER': 'Twilio WhatsApp number',
        'GOOGLE_SERVICE_ACCOUNT_FILE': 'Google service account JSON',
        'GOOGLE_SHEET_ID': 'Google Sheets ID',
        'NUTRITIONIX_APP_ID': 'Nutritionix API ID (optional)',
        'NUTRITIONIX_API_KEY': 'Nutritionix API key (optional)',
    }

    all_good = True

    # Check required variables
    print("📋 Required Environment Variables:")
    print("-" * 60)
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            masked = value[:10] + "..." if len(value) > 10 else value
            print(f"✅ {var}: {masked}")
        else:
            print(f"❌ {var}: NOT SET - {description}")
            all_good = False

    print()
    print("📋 Optional Environment Variables:")
    print("-" * 60)
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            masked = value[:10] + "..." if len(value) > 10 else value
            print(f"✅ {var}: {masked}")
        else:
            print(f"⚠️  {var}: Not set - {description}")

    print()
    print("="*60)

    # Check dependencies
    print("\n📦 Checking Dependencies:")
    print("-" * 60)

    dependencies = [
        ('fastapi', 'FastAPI'),
        ('anthropic', 'Anthropic Claude SDK'),
        ('twilio', 'Twilio SDK'),
        ('supabase', 'Supabase client'),
        ('google.oauth2', 'Google Auth'),
        ('googleapiclient', 'Google API client'),
        ('apscheduler', 'APScheduler'),
    ]

    for module, name in dependencies:
        try:
            __import__(module)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name} - Run: pip install -r requirements.txt")
            all_good = False

    print()
    print("="*60)

    # Database check
    print("\n🗄️  Checking Database Connection:")
    print("-" * 60)

    try:
        from supabase import create_client
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")

        if supabase_url and supabase_key:
            supabase = create_client(supabase_url, supabase_key)

            # Try to query user_profiles table
            try:
                result = supabase.table('user_profiles').select('*').limit(1).execute()
                print(f"✅ Database connection successful!")
                print(f"✅ user_profiles table exists")
            except Exception as e:
                print(f"⚠️  Database connected but tables may not exist")
                print(f"   Error: {e}")
                print(f"   Run the SQL migrations in Supabase SQL Editor")
        else:
            print("❌ Supabase credentials not set")
            all_good = False
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        all_good = False

    print()
    print("="*60)

    # Claude API check
    print("\n🤖 Checking Claude API:")
    print("-" * 60)

    try:
        import anthropic
        api_key = os.getenv("ANTHROPIC_API_KEY")

        if api_key:
            try:
                client = anthropic.Anthropic(api_key=api_key)
                # Try a minimal API call
                print("✅ Claude API key configured")
                print("   (Not testing actual API call to save credits)")
            except Exception as e:
                print(f"⚠️  Claude API key set but may be invalid: {e}")
        else:
            print("❌ ANTHROPIC_API_KEY not set")
            all_good = False
    except Exception as e:
        print(f"❌ Claude check failed: {e}")

    print()
    print("="*60)

    # Final summary
    print("\n📊 Summary:")
    print("-" * 60)

    if all_good:
        print("✅ All required components are configured!")
        print("\nYou're ready to start the server:")
        print("   python run_server.py")
        print("\nOr:")
        print("   uvicorn backend.app.api:app --reload")
    else:
        print("❌ Some required components are missing")
        print("\nPlease fix the issues above and run this script again.")
        print("\nCommon fixes:")
        print("1. Copy .env.example to .env and fill in your API keys")
        print("2. Run: pip install -r requirements.txt")
        print("3. Run SQL migrations in Supabase SQL Editor")
        print("\nSee SETUP_GUIDE.md for detailed instructions")

    print()
    print("="*60)

    return all_good

if __name__ == "__main__":
    try:
        success = check_environment()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nCheck cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
