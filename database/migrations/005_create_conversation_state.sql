-- ============================================
-- TABLE: conversation_state
-- PURPOSE: Track conversation context and state for each user
-- ============================================

CREATE TABLE IF NOT EXISTS conversation_state (
    id SERIAL PRIMARY KEY,
    phone_number TEXT UNIQUE NOT NULL,
    current_phase TEXT,  -- awaiting_confirmation/logging_mode/adjusting_plan/general_chat
    context_data JSONB,  -- store current plan, last messages, pending actions
    last_interaction TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create index for phone number lookups
CREATE INDEX IF NOT EXISTS idx_conversation_state_phone ON conversation_state(phone_number);

-- Create index for JSONB queries (for efficient context searches)
CREATE INDEX IF NOT EXISTS idx_conversation_state_context ON conversation_state USING GIN (context_data);

-- Create trigger to auto-update updated_at timestamp
CREATE TRIGGER update_conversation_state_updated_at
    BEFORE UPDATE ON conversation_state
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Add helpful comments
COMMENT ON TABLE conversation_state IS 'Maintains conversation context and state for WhatsApp AI agent';
COMMENT ON COLUMN conversation_state.current_phase IS 'Current conversation phase (awaiting_confirmation, logging_mode, etc.)';
COMMENT ON COLUMN conversation_state.context_data IS 'JSONB storing conversation history, current meal plan, pending actions';

-- Example context_data structure:
-- {
--   "current_plan": {...},
--   "conversation_history": [...],
--   "pending_action": "waiting_for_lunch_confirmation",
--   "last_reminder_sent": "2025-01-23T14:00:00Z"
-- }
