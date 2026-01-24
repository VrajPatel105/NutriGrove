-- ============================================
-- MASTER MIGRATION SCRIPT
-- PURPOSE: Run all migrations in order
-- INSTRUCTIONS: Copy and paste this entire file into Supabase SQL Editor
-- ============================================

-- Run this script in Supabase SQL Editor to create all tables at once

-- ============================================
-- 1. USER PROFILES TABLE
-- ============================================

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

CREATE INDEX IF NOT EXISTS idx_user_profiles_phone ON user_profiles(phone_number);

-- ============================================
-- 2. FOOD LOGS TABLE
-- ============================================

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

CREATE INDEX IF NOT EXISTS idx_food_logs_phone_date ON food_logs(phone_number, date);
CREATE INDEX IF NOT EXISTS idx_food_logs_date ON food_logs(date);
CREATE INDEX IF NOT EXISTS idx_food_logs_meal_type ON food_logs(meal_type);

-- ============================================
-- 3. DAILY SUMMARIES TABLE
-- ============================================

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

CREATE INDEX IF NOT EXISTS idx_daily_summaries_phone_date ON daily_summaries(phone_number, date);
CREATE INDEX IF NOT EXISTS idx_daily_summaries_sync ON daily_summaries(synced_to_sheets, date);

-- ============================================
-- 4. USER RULES TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS user_rules (
    id SERIAL PRIMARY KEY,
    phone_number TEXT NOT NULL,
    rule_type TEXT NOT NULL,
    rule_value TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_rules_phone ON user_rules(phone_number);
CREATE INDEX IF NOT EXISTS idx_user_rules_active ON user_rules(phone_number, is_active);

-- ============================================
-- 5. CONVERSATION STATE TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS conversation_state (
    id SERIAL PRIMARY KEY,
    phone_number TEXT UNIQUE NOT NULL,
    current_phase TEXT,
    context_data JSONB,
    last_interaction TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_conversation_state_phone ON conversation_state(phone_number);
CREATE INDEX IF NOT EXISTS idx_conversation_state_context ON conversation_state USING GIN (context_data);

-- ============================================
-- 6. SCHEDULED REMINDERS TABLE
-- ============================================

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

CREATE INDEX IF NOT EXISTS idx_scheduled_reminders_phone ON scheduled_reminders(phone_number);
CREATE INDEX IF NOT EXISTS idx_scheduled_reminders_active ON scheduled_reminders(is_active, scheduled_time);

-- ============================================
-- TRIGGERS AND FUNCTIONS
-- ============================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_user_profiles_updated_at
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conversation_state_updated_at
    BEFORE UPDATE ON conversation_state
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- SUCCESS MESSAGE
-- ============================================

DO $$
BEGIN
    RAISE NOTICE 'SUCCESS! All 6 tables created successfully:';
    RAISE NOTICE '  ✓ user_profiles';
    RAISE NOTICE '  ✓ food_logs';
    RAISE NOTICE '  ✓ daily_summaries';
    RAISE NOTICE '  ✓ user_rules';
    RAISE NOTICE '  ✓ conversation_state';
    RAISE NOTICE '  ✓ scheduled_reminders';
    RAISE NOTICE '';
    RAISE NOTICE 'All indexes and triggers created successfully!';
    RAISE NOTICE 'Your WhatsApp nutrition coach database is ready to use!';
END $$;
