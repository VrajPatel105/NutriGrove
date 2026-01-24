-- ============================================
-- TABLE: user_rules
-- PURPOSE: Store custom user preferences and rules
-- ============================================

CREATE TABLE IF NOT EXISTS user_rules (
    id SERIAL PRIMARY KEY,
    phone_number TEXT NOT NULL,
    rule_type TEXT NOT NULL,  -- skip_meal_weekends/extra_protein_run_days/etc
    rule_value TEXT,  -- JSON or text description
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create index for phone number queries
CREATE INDEX IF NOT EXISTS idx_user_rules_phone ON user_rules(phone_number);

-- Create index for active rules
CREATE INDEX IF NOT EXISTS idx_user_rules_active ON user_rules(phone_number, is_active);

-- Add helpful comments
COMMENT ON TABLE user_rules IS 'Custom user preferences and behavioral rules learned from conversations';
COMMENT ON COLUMN user_rules.rule_type IS 'Type of rule (e.g., skip_breakfast_weekends, extra_protein_run_days)';
COMMENT ON COLUMN user_rules.rule_value IS 'JSON or text describing the rule details';

-- Example rules:
-- rule_type: "skip_breakfast_weekends", rule_value: "User prefers to skip breakfast on Saturdays and Sundays"
-- rule_type: "extra_protein_run_days", rule_value: '{"days": ["Monday", "Wednesday", "Friday"], "extra_protein": 30}'
