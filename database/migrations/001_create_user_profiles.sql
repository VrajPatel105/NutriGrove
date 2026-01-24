-- ============================================
-- TABLE: user_profiles
-- PURPOSE: Store user information, goals, and nutrition targets
-- ============================================

CREATE TABLE IF NOT EXISTS user_profiles (
    id SERIAL PRIMARY KEY,
    phone_number TEXT UNIQUE NOT NULL,
    age INT,
    gender TEXT,
    weight INT,  -- in lbs
    height INT,  -- in cm
    activity_level TEXT,  -- active/moderate/sedentary
    goal TEXT,  -- build_muscle/lose_weight/maintain/marathon_training
    diet TEXT,  -- keto/paleo/vegan/none
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

-- Create index for faster phone number lookups
CREATE INDEX IF NOT EXISTS idx_user_profiles_phone ON user_profiles(phone_number);

-- Create trigger to auto-update updated_at timestamp
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

-- Add helpful comments
COMMENT ON TABLE user_profiles IS 'Stores user profile information, goals, and nutrition targets for WhatsApp nutrition coach';
COMMENT ON COLUMN user_profiles.phone_number IS 'User WhatsApp phone number (unique identifier)';
COMMENT ON COLUMN user_profiles.calories_target IS 'Daily calorie target calculated from user goals';
COMMENT ON COLUMN user_profiles.protein_target IS 'Daily protein target in grams';
