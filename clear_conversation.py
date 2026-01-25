"""Quick script to clear corrupted conversation history"""
from supabase import create_client
import os
import sys
import io
from dotenv import load_dotenv

# Fix Windows encoding issues
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_ANON_KEY"))
supabase.table('conversation_state').delete().eq('phone_number', '+17746270286').execute()
print("Cleared conversation history for +17746270286")
