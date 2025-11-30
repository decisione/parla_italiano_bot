# Russian Translation Implementation Plan

## Overview
This document outlines the implementation plan for adding a russian translation to the Parla Italiano Bot. It will allow users to get translations upon request.

## Requirements Summary

### Core Functionality
- New `/rus` command to show the translation
- Display one last italian sentence tried by this user, and it's translation

### Database Changes
- Add `sentence_rus` column to `italian_sentences` table

### Content Generation
- Update `sentence_replenishment()` with LLM prompt to generates also russian translation during replenishment
- Validate LLM generated content: words must be in Russian (check with the alphabet and punctuation marks).

## Implementation Phases

### Phase 1: Database Migration
**Objective**: Add database schema changes for russian translation functionality

**Tasks**:
1. Create migration `004_russian_translation.sql`:
   - Add `sentence_rus` column to `italian_sentences` table
   - Add constraints: the column is NOT NULL with empty string defaults

**Deliverables**:
- `migrations/004_russian_translation.sql`

### Phase 2: Content Generation Updates
**Objective**: Update sentence replenishment to generate russian translation data

**Tasks**:
1. Update LLM prompt and structured output for russian translation generation:
   - Use structured output to ensure data consistency
   - Validate each generated sentence

2. Update database functions:
   - Store russian translation for generated sentences

**Deliverables**:
- Updated LLM prompt and response model, updated `sentence_replenishment()` function

### Phase 3: Bot Command Implementation
**Objective**: Create the `/rus` command handler

**Tasks**:
1. Create `src/bot_commands/rus.py`:
   - Implement command handler function
   - Update command routing

**Deliverables**:
- `src/bot_commands/rus.py`
- Updated bot application configuration

## Technical Specifications

- Create new tests to cover new functionality
- Documentation: Update README and memory bank after implementation
