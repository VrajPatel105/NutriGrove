-- ============================================
-- TABLE: scheduled_reminders
-- PURPOSE: Manage scheduled reminders for meal logging and nutrition tracking
-- ============================================

CREATE TABLE IF NOT EXISTS scheduled_reminders (
    id SERIAL PRIMARY KEY,
    phone_number TEXT NOT NULL,
    reminder_type TEXT NOT NULL,  -- meal_log/under_target/plan_confirmation/weekly_checkin
    scheduled_time TIME,  -- time of day to send reminder
    day_of_week INT,  -- 0=Sunday, 1=Monday, ..., 6=Saturday (NULL for daily)
    is_active BOOLEAN DEFAULT true,
    last_sent TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create index for phone number queries
CREATE INDEX IF NOT EXISTS idx_scheduled_reminders_phone ON scheduled_reminders(phone_number);

-- Create index for active reminders
CREATE INDEX IF NOT EXISTS idx_scheduled_reminders_active ON scheduled_reminders(is_active, scheduled_time);

-- Add helpful comments
COMMENT ON TABLE scheduled_reminders IS 'Scheduled reminders for meal logging and nutrition tracking';
COMMENT ON COLUMN scheduled_reminders.reminder_type IS 'Type of reminder (meal_log, under_target, plan_confirmation, etc.)';
COMMENT ON COLUMN scheduled_reminders.scheduled_time IS 'Time of day to send reminder (HH:MM:SS)';
COMMENT ON COLUMN scheduled_reminders.day_of_week IS 'Day of week (0-6, NULL for daily reminders)';
COMMENT ON COLUMN scheduled_reminders.last_sent IS 'Timestamp of last reminder sent';
