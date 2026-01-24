-- ============================================
-- TABLE: daily_summaries
-- PURPOSE: Store end-of-day nutrition totals and adherence scores
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
    adherence_score DECIMAL(5,2),  -- percentage of plan followed (0-100)
    meals_logged INT DEFAULT 0,  -- how many meals logged
    notes TEXT,
    synced_to_sheets BOOLEAN DEFAULT false,
    synced_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(phone_number, date)
);

-- Create composite index for efficient queries
CREATE INDEX IF NOT EXISTS idx_daily_summaries_phone_date ON daily_summaries(phone_number, date);

-- Create index for sync status queries
CREATE INDEX IF NOT EXISTS idx_daily_summaries_sync ON daily_summaries(synced_to_sheets, date);

-- Add helpful comments
COMMENT ON TABLE daily_summaries IS 'Daily nutrition summaries with adherence tracking';
COMMENT ON COLUMN daily_summaries.adherence_score IS 'Percentage score (0-100) measuring how well user followed their meal plan';
COMMENT ON COLUMN daily_summaries.synced_to_sheets IS 'True if data has been synced to Google Sheets';
