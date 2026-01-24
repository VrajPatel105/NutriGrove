-- ============================================
-- TABLE: food_logs
-- PURPOSE: Track all foods eaten by users throughout the day
-- ============================================

CREATE TABLE IF NOT EXISTS food_logs (
    id SERIAL PRIMARY KEY,
    phone_number TEXT NOT NULL,
    date DATE NOT NULL,
    meal_type TEXT,  -- breakfast/lunch/dinner/snack
    food_name TEXT NOT NULL,
    portion TEXT,  -- "3 eggs", "1 cup", "small bag"
    calories INT,
    protein_g DECIMAL(8,2),
    carbs_g DECIMAL(8,2),
    fat_g DECIMAL(8,2),
    fiber_g DECIMAL(8,2),
    sodium_mg DECIMAL(8,2),
    sugar_g DECIMAL(8,2),
    was_planned BOOLEAN DEFAULT false,  -- true if from morning plan
    is_external BOOLEAN DEFAULT false,  -- true if not from dining hall menu
    logged_at TIMESTAMP DEFAULT NOW(),
    notes TEXT
);

-- Create composite index for efficient queries by user and date
CREATE INDEX IF NOT EXISTS idx_food_logs_phone_date ON food_logs(phone_number, date);

-- Create index for date-based queries
CREATE INDEX IF NOT EXISTS idx_food_logs_date ON food_logs(date);

-- Create index for meal type queries
CREATE INDEX IF NOT EXISTS idx_food_logs_meal_type ON food_logs(meal_type);

-- Add helpful comments
COMMENT ON TABLE food_logs IS 'Daily food intake logs from WhatsApp conversations';
COMMENT ON COLUMN food_logs.was_planned IS 'True if food was from AI-generated morning meal plan';
COMMENT ON COLUMN food_logs.is_external IS 'True if food is not from dining hall menu (estimated nutrition)';
COMMENT ON COLUMN food_logs.portion IS 'Human-readable portion size (e.g., "3 eggs", "1 cup rice")';
