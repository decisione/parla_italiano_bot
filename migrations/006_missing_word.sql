-- Add missing word exercise columns to italian_sentences
ALTER TABLE italian_sentences
    ADD COLUMN word_to_replace TEXT NOT NULL DEFAULT '';

ALTER TABLE italian_sentences
    ADD COLUMN word_suggestions TEXT NOT NULL DEFAULT '';

-- Create missing word results table
CREATE TABLE missing_word_results (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    italian_sentence_id INT NOT NULL REFERENCES italian_sentences(id) ON DELETE CASCADE,
    is_success BOOLEAN NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for missing word results
CREATE INDEX idx_missing_word_results_user_id ON missing_word_results(user_id);
CREATE INDEX idx_missing_word_results_sentence_id ON missing_word_results(italian_sentence_id);
CREATE INDEX idx_missing_word_results_user_sentence_time ON missing_word_results(user_id, italian_sentence_id, timestamp);
