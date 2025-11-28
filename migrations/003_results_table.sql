-- Migration 003: Create italian_sentences_results table for tracking user performance

CREATE TABLE IF NOT EXISTS italian_sentences_results (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    italian_sentence_id INT NOT NULL REFERENCES italian_sentences(id) ON DELETE CASCADE,
    is_success BOOLEAN NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_results_user_id ON italian_sentences_results(user_id);
CREATE INDEX IF NOT EXISTS idx_results_sentence_id ON italian_sentences_results(italian_sentence_id);
CREATE INDEX IF NOT EXISTS idx_results_user_sentence_time ON italian_sentences_results(user_id, italian_sentence_id, timestamp);
