# Missing Word Exercise Implementation Plan

## Overview
This document outlines the implementation plan for adding a new "missing word" exercise to the Parla Italiano Bot. The exercise will allow users to practice Italian by selecting the correct missing word from multiple choices.

## Requirements Summary

### Core Functionality
- New `/parola_mancante` command to start the exercise
- Display Italian sentences with one word replaced by "______"
- Present multiple choice options (2-4 words) with only one correct answer
- Track user performance in a new `missing_word_results` table
- Continue with new sentences indefinitely until user stops
- Use same encouraging/error phrases as sentence ordering exercise

### Database Changes
- Add `word_to_replace` and `word_suggestions` columns to `italian_sentences` table
- Create new `missing_word_results` table for tracking results
- Store suggestions as comma-separated string (easier to develop and maintain)
- Generate missing word data during `sentence_replenishment()` process

### Content Generation
- LLM generates sentences with missing word data during replenishment
- When less than 10 unsolved sentences remain for EITHER exercise, generate 25 new sentences
- Include word_to_replace and word_suggestions for each generated sentence
- Validate LLM generated content for number of words (2-4 options), generated words must be in Italian, must not have duplicates, must not be present in the original sentence

### User Experience
- Use inline keyboard buttons for answer selection (like sentence ordering)
- Randomize suggestion order each time for variety
- Allow multiple attempts with same wrong answer
- Show correct answer and move to next sentence after selection
- No visual feedback beyond proceeding to next sentence
- Users can exit by using other commands (/start, /stats, etc.)
- Use sentences that haven't been solved yet, even if used in sentence ordering
- Fallback to previously used sentences if no unsolved ones available

### Statistics Integration
- Add missing word statistics to existing `/stats` command
- Show global and individual success rates for missing word exercise
- Include today's statistics for missing word exercise

## Implementation Phases

### Phase 1: Database Migrations
**Objective**: Add database schema changes for missing word functionality

**Tasks**:
1. Create migration `004_missing_word.sql`:
   - Add `word_to_replace` column to `italian_sentences` table
   - Add `word_suggestions` column to `italian_sentences` table (comma-separated string)
   - Add constraints: both columns are NOT NULL with empty string defaults
   - Add necessary indexes in `italian_sentences` table
   - Create `missing_word_results` table with columns:
     - `id` (SERIAL PRIMARY KEY)
     - `user_id` (BIGINT NOT NULL REFERENCES users)
     - `italian_sentence_id` (INT NOT NULL REFERENCES italian_sentences)
     - `is_success` (BOOLEAN NOT NULL)
     - `timestamp` (TIMESTAMPTZ NOT NULL DEFAULT NOW())
   - Create indexes for performance (user_id, sentence_id, composite index)

2. Create a script `temp/generate_missing_words.py` to update existing sentences in `italian_sentences` table by means of LLM similar to `temp/generate_italian_sentences.py`.

**Deliverables**:
- `migrations/004_missing_word_columns.sql`
- `temp/generate_missing_words.py`

### Phase 2: Content Generation Updates
**Objective**: Update sentence replenishment to generate missing word data

**Tasks**:
1. Create `src/database/replenishment.py` module:
   - Move `sentence_replenishment()` function from `sentences.py`
   - Update replenishment logic to check both exercise types
   - Generate missing word data for new sentences during replenishment

2. Update LLM prompt and structured output for missing word generation:
   - Generate 25 Italian sentences (3-10 words, various topics)
   - For each sentence, specify:
     - `word_to_replace`: The target word to remove
     - `word_suggestions`: 2-5 comma-separated alternatives (correct + wrong answers)
   - Ensure suggestions are 2 to 4 words, must be in Italian, must not have duplicates, must not be present in the original sentence except for the word_to_replace
   - Use structured output to ensure data consistency

3. Update database functions:
   - Add function to store missing word data with new sentences
   - Update sentence selection logic to prefer unsolved sentences for missing word exercise
   - Add fallback logic for when no unsolved sentences are available

**Deliverables**:
- `src/database/replenishment.py`
- Updated LLM prompt and response model
- Updated database storage functions

### Phase 3: Bot Command Implementation
**Objective**: Create the `/parola_mancante` command handler

**Tasks**:
1. Create `src/bot_commands/missing_word.py`:
   - Implement command handler function
   - Create missing word exercise class
   - Handle user state management for the exercise
   - Integrate with database functions for sentence retrieval and result storage

2. Update bot application:
   - Register the new command in the main application
   - Add dependency injection for missing word exercise
   - Update command routing

3. Implement exercise flow:
   - Start exercise with welcome message
   - Retrieve appropriate sentence (unsolved, with missing word data)
   - Display sentence with blank and multiple choice options
   - Handle user selections via callback queries
   - Provide feedback and proceed to next sentence
   - Continue indefinitely until user stops

**Deliverables**:
- `src/bot_commands/missing_word.py`
- Updated bot application configuration
- Exercise flow implementation

### Phase 4: UI/UX and Exercise Mechanics
**Objective**: Implement complete user interface and exercise logic

**Tasks**:
1. Sentence display formatting:
   - Replace target word with "______" in sentence display
   - Create inline keyboard with randomized suggestion order
   - Ensure proper text encoding and display

2. Answer selection handling:
   - Process callback queries from inline keyboard
   - Validate user selection against correct answer
   - Store result in `missing_word_results` table
   - Display appropriate feedback message
   - Retrieve and display next sentence

3. User experience features:
   - Use existing encouraging/error phrases from database
   - Handle edge cases (no sentences available, etc.)
   - Ensure smooth transitions between sentences
   - Maintain consistent UI with existing sentence ordering exercise

4. Statistics integration:
   - Update `get_stats_data()` function to include missing word statistics
   - Add missing word success rates to `/stats` command output
   - Include today's missing word statistics

**Deliverables**:
- Complete missing word exercise UI
- Answer selection and feedback logic
- Updated statistics functionality

### Phase 5: /start command update
**Objective**: Make /start as the starting point, move sentence ordering exercise to a new `/ordine_delle_parole` command

**Tasks**:
1. Create the `/ordine_delle_parole` command handler
2. Move existing sentence ordering exercise logic to this handler
3. Change `/start` command handler to present a menu of `/ordine_delle_parole`, `/parola_mancante` or `/stats`

## Technical Specifications

### Database Schema

#### Updated italian_sentences table:
```sql
ALTER TABLE italian_sentences ADD COLUMN word_to_replace TEXT NOT NULL DEFAULT '';
ALTER TABLE italian_sentences ADD COLUMN word_suggestions TEXT NOT NULL DEFAULT '';
```

#### New missing_word_results table:
```sql
CREATE TABLE missing_word_results (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    italian_sentence_id INT NOT NULL REFERENCES italian_sentences(id) ON DELETE CASCADE,
    is_success BOOLEAN NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_missing_word_results_user_id ON missing_word_results(user_id);
CREATE INDEX idx_missing_word_results_sentence_id ON missing_word_results(italian_sentence_id);
CREATE INDEX idx_missing_word_results_user_sentence_time ON missing_word_results(user_id, italian_sentence_id, timestamp);
```

### LLM Response Model
```python
class MissingWordSentence(BaseModel):
    sentence: str
    word_to_replace: str
    word_suggestions: List[str]  # 2-4 items, first is correct

class MissingWordSentenceList(BaseModel):
    sentences: List[MissingWordSentence]
```

### Exercise State Management
- Use existing learning state pattern from sentence ordering
- Track current sentence, user selections, and exercise progress
- No need to track specific missing words or repeated answers
- Simple success/failure tracking per sentence

### Error Handling
- Graceful handling of database connection issues
- Fallback to previously used sentences when no unsolved available
- Robust LLM API error handling (429, timeouts, etc.)
- No special content validation needed (LLM ensures quality)

## Testing Strategy

### Unit Tests
- Database functions for missing word operations
- LLM response parsing and validation
- Sentence selection logic
- Result storage functionality

### Integration Tests
- Complete exercise flow from start to finish
- Statistics calculation and display
- Database migration scripts
- Error handling scenarios

### User Acceptance Testing
- Test with actual users for UI/UX feedback
- Verify LLM-generated content quality
- Validate exercise difficulty and engagement
- Confirm statistics accuracy

## Success Criteria

### Functional Requirements
- [ ] `/parola_mancante` command works correctly
- [ ] Sentences display with missing words properly
- [ ] Multiple choice options work as expected
- [ ] Results are tracked in database
- [ ] Statistics include missing word data
- [ ] Exercise continues indefinitely
- [ ] Users can exit using other commands

### Non-Functional Requirements
- [ ] Performance: sentences load quickly
- [ ] Reliability: handles errors gracefully
- [ ] Maintainability: code is well-structured and documented
- [ ] Scalability: can handle growing number of users and sentences

## Notes and Considerations

1. **Content Quality**: LLM will generate appropriate, universal content. Some validation needed on the bot side.

2. **User Experience**: Keep interface simple and consistent with existing sentence ordering exercise.

3. **Performance**: Use existing patterns for database queries and caching where appropriate.

4. **Maintainability**: Follow existing code structure and naming conventions.

5. **Testing**: Comprehensive testing at each phase before proceeding to next.

6. **Documentation**: Update README, technical documentation and memory bank as implementation progresses.

7. **Deployment**: Ensure migrations can be run in production environment safely.
