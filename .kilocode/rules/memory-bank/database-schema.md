## Current Database Schema

1. **`italian_sentences`** table:
   - `id` (SERIAL PRIMARY KEY)
   - `sentence` (TEXT NOT NULL) - Italian sentence text

2. **`encouraging_phrases`** table:
   - `id` (SERIAL PRIMARY KEY)
   - `phrase` (TEXT NOT NULL)

3. **`error_phrases`** table:
   - `id` (SERIAL PRIMARY KEY)
   - `phrase` (TEXT NOT NULL)

4. **`users`** table:
   - `user_id` (BIGINT PRIMARY KEY)
   - Profile and access tracking fields

5. **`italian_sentences_results`** table:
   - `id` (SERIAL PRIMARY KEY)
   - `user_id` (BIGINT REFERENCES users)
   - `italian_sentence_id` (INT REFERENCES italian_sentences)
   - `is_success` (BOOLEAN)
   - `timestamp` (TIMESTAMPTZ)