"""
Database Setup Script
Programmatically create all tables for WhatsApp Nutrition Coach

This is a backup option if you prefer running Python instead of SQL scripts
"""

import os
from dotenv import load_dotenv
from supabase import create_client

def setup_database():
    """Create all tables in Supabase"""
    load_dotenv()

    supabase = create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_ANON_KEY")
    )

    print("Setting up database tables...")

    # Note: Supabase doesn't allow direct DDL via Python client
    # This script provides SQL commands that you need to run in Supabase SQL Editor

    sql_commands = """
    -- Run this in Supabase SQL Editor

    -- 1. User Profiles
    CREATE TABLE IF NOT EXISTS user_profiles (
        id SERIAL PRIMARY KEY,
        phone_number TEXT UNIQUE NOT NULL,
        age INT,
        gender TEXT,
        weight INT,
        height INT,
        activity_level TEXT,
        goal TEXT,
        diet TEXT,
        dietary_restrictions TEXT,
        calories_target INT,
        protein_target INT,
        carbs_target INT,
        fat_target INT,
        allergens TEXT[],
        dislikes TEXT[],
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
    );

    -- 2. Food Logs
    CREATE TABLE IF NOT EXISTS food_logs (
        id SERIAL PRIMARY KEY,
        phone_number TEXT NOT NULL,
        date DATE NOT NULL,
        meal_type TEXT,
        food_name TEXT NOT NULL,
        portion TEXT,
        calories INT,
        protein_g DECIMAL(8,2),
        carbs_g DECIMAL(8,2),
        fat_g DECIMAL(8,2),
        fiber_g DECIMAL(8,2),
        sodium_mg DECIMAL(8,2),
        sugar_g DECIMAL(8,2),
        was_planned BOOLEAN DEFAULT false,
        is_external BOOLEAN DEFAULT false,
        logged_at TIMESTAMP DEFAULT NOW(),
        notes TEXT
    );

    -- 3. Daily Summaries
    CREATE TABLE IF NOT EXISTS daily_summaries (
        id SERIAL PRIMARY KEY,
        phone_number TEXT NOT NULL,
        date DATE NOT NULL,
        planned_calories INT,
        actual_calories INT,
        planned_protein INT,
        actual_protein DECIMAL(8,2),
        actual_carbs DECIMAL(8,2),
        actual_fat DECIMAL(8,2),
        actual_fiber DECIMAL(8,2),
        adherence_score DECIMAL(5,2),
        meals_logged INT DEFAULT 0,
        notes TEXT,
        synced_to_sheets BOOLEAN DEFAULT false,
        synced_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT NOW(),
        UNIQUE(phone_number, date)
    );

    -- 4. User Rules
    CREATE TABLE IF NOT EXISTS user_rules (
        id SERIAL PRIMARY KEY,
        phone_number TEXT NOT NULL,
        rule_type TEXT NOT NULL,
        rule_value TEXT,
        is_active BOOLEAN DEFAULT true,
        created_at TIMESTAMP DEFAULT NOW()
    );

    -- 5. Conversation State
    CREATE TABLE IF NOT EXISTS conversation_state (
        id SERIAL PRIMARY KEY,
        phone_number TEXT UNIQUE NOT NULL,
        current_phase TEXT,
        context_data JSONB,
        last_interaction TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
    );

    -- 6. Scheduled Reminders
    CREATE TABLE IF NOT EXISTS scheduled_reminders (
        id SERIAL PRIMARY KEY,
        phone_number TEXT NOT NULL,
        reminder_type TEXT NOT NULL,
        scheduled_time TIME,
        day_of_week INT,
        is_active BOOLEAN DEFAULT true,
        last_sent TIMESTAMP,
        created_at TIMESTAMP DEFAULT NOW()
    );

    -- Create Indexes
    CREATE INDEX IF NOT EXISTS idx_user_profiles_phone ON user_profiles(phone_number);
    CREATE INDEX IF NOT EXISTS idx_food_logs_phone_date ON food_logs(phone_number, date);
    CREATE INDEX IF NOT EXISTS idx_daily_summaries_phone_date ON daily_summaries(phone_number, date);
    CREATE INDEX IF NOT EXISTS idx_conversation_state_phone ON conversation_state(phone_number);
    """

    print("\n" + "="*60)
    print("COPY THE SQL COMMANDS BELOW INTO SUPABASE SQL EDITOR")
    print("="*60)
    print(sql_commands)
    print("="*60)
    print("\nAfter running the SQL, all tables will be created!")

if __name__ == "__main__":
    setup_database()
