#!/usr/bin/env python3
"""
Generate missing word data for existing Italian sentences using OpenAI API with Instructor.
Reads temp/italian_sentences.csv and outputs temp/italian_sentences_updated.csv.
This script is for experiments only! Do not modify it if not explicitly instructed to do so!
"""

import os
import csv
import re
import asyncio
import time
from collections import deque
from typing import List

import pydantic
from openai import OpenAIError
from dotenv import load_dotenv
from openai import OpenAI


# Load environment variables
load_dotenv()

# Configuration
API_URL = "https://openrouter.ai/api/v1"
LLM_API_KEY = os.getenv("LLM_API_KEY")
MODEL_NAME = "qwen/qwen3-235b-a22b-2507"

INPUT_CSV_PATH = "italian_sentences.csv"
OUTPUT_CSV_PATH = "italian_sentences_updated.csv"

# Italian character set including accented vowels
ITALIAN_CHARACTERS = set('abcdefghiklmnopqrstuvzàèéìíîòóùú .,;:!?\'-')


class MissingWordResult(pydantic.BaseModel):
    word_to_replace: str
    word_suggestions: List[str]


def normalize_word(word: str) -> str:
    return word.strip().lower()


def extract_words(sentence: str) -> List[str]:
    return re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ']+", sentence.lower())


def strip_elision(word: str) -> str:
    parts = word.split("'", 1)
    return parts[1] if len(parts) == 2 else ""


def is_valid_italian_text(text: str) -> bool:
    for char in text.lower():
        if char not in ITALIAN_CHARACTERS:
            return False
    return True


def validate_missing_word_data(sentence: str, word_to_replace: str, suggestions: List[str]) -> bool:
    sentence_words = extract_words(sentence)
    target = normalize_word(word_to_replace)
    sentence_normalized = [normalize_word(w) for w in sentence_words]
    sentence_stripped = [strip_elision(w) for w in sentence_normalized]
    if not target or (target not in sentence_normalized and target not in sentence_stripped):
        return False
    target_matches = 0
    for original, stripped in zip(sentence_normalized, sentence_stripped):
        if original == target:
            target_matches += 1
        elif stripped and stripped == target:
            target_matches += 1
    if target_matches != 1:
        return False

    if not (2 <= len(suggestions) <= 5):
        return False

    normalized_suggestions = [normalize_word(s) for s in suggestions]
    if len(normalized_suggestions) != len(set(normalized_suggestions)):
        return False

    if target in normalized_suggestions:
        return False

    for suggestion in suggestions:
        if not suggestion.strip() or not is_valid_italian_text(suggestion):
            return False

    if any(
        suggestion in sentence_normalized or suggestion in sentence_stripped
        for suggestion in normalized_suggestions
    ):
        return False

    if not is_valid_italian_text(word_to_replace):
        return False

    return True


def generate_missing_word_data(client: OpenAI, sentence: str, recent_suggestions: List[str]) -> MissingWordResult:
    recent_text = ", ".join(recent_suggestions)
    system_prompt = f"""You are generating missing word exercise data for Italian sentences.
Given the Italian sentence, select a single target word to replace and propose 2 to 5 alternative words.

Rules:
- The target word must be in Italian.
- The target word must appear exactly once in the sentence.
- The target word must be a single word (no spaces).
- Provide 2 to 5 alternative words in Italian.
- Alternatives must be unique, not present in the original sentence, and not equal to the target word.
- An alternative word can be any part of speech: a noun, an adjective, a verb, and so on.
- **Important validation**: If any of the alternative words are inserted into a sentence instead of the target word, the sentence MUST become grammatically incorrect, absurd, or illogical.
- Avoid using any of these recent suggestions: {recent_text}
- Output only valid JSON with keys: word_to_replace (string) and word_suggestions (array of strings).
"""

#    print("\nSentence:", sentence)
#    print("recent_text:", recent_text)

    last_error = None
    for attempt in range(1, 8):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                tool_choice="auto",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Sentence: {sentence}"}
                ]
            )
            content = response.choices[0].message.content or ""
            content = re.sub(r"^```(?:json)?\s*", "", content.strip(), flags=re.IGNORECASE)
            content = re.sub(r"```$", "", content.strip())
            return MissingWordResult.model_validate_json(content)
        except OpenAIError as exc:
            status_code = getattr(exc, "status_code", None)
            if status_code == 429 and attempt < 8:
                backoff = 2 ** (attempt - 1)
                print(f"Rate limited (429). Retry {attempt} after {backoff}s")
                time.sleep(backoff)
                last_error = exc
                continue
            raise

    if last_error:
        raise last_error


async def main() -> None:
    print("=" * 60)
    print("Missing Word Data Generator")
    print("=" * 60)

    if not LLM_API_KEY:
        print("ERROR: LLM_API_KEY not found in environment variables!")
        print("Please set LLM_API_KEY in your .env file")
        return

    client = OpenAI(base_url=API_URL, api_key=LLM_API_KEY)

    if not os.path.exists(INPUT_CSV_PATH):
        print(f"ERROR: Input CSV not found at {INPUT_CSV_PATH}")
        return

    with open(INPUT_CSV_PATH, newline="", encoding="utf-8") as input_file:
        reader = csv.DictReader(input_file, delimiter=';')
        rows = list(reader)

    if not rows:
        print("No rows found in input CSV.")
        return

    semaphore = asyncio.Semaphore(4)
    recent_suggestions = deque(maxlen=200)
    recent_set = set()
    recent_lock = asyncio.Lock()

    async def process_row(index: int, row: dict) -> dict:
        sentence_id = row.get("id", "").strip()
        sentence = row.get("sentence", "").strip()

        if not sentence_id or not sentence:
            print(f"Skipping row {index}: missing id or sentence")
            return {
                "id": sentence_id,
                "sentence": sentence,
                "word_to_replace": "",
                "word_suggestions": ""
            }

        async with semaphore:
            try:
                print(f"Processing sentence {index}/{len(rows)} (id={sentence_id})")
                async with recent_lock:
                    recent_snapshot = list(recent_suggestions)
                result = await asyncio.to_thread(
                    generate_missing_word_data,
                    client,
                    sentence,
                    recent_snapshot
                )
                word_to_replace = result.word_to_replace.strip()
                suggestions = [s.strip() for s in result.word_suggestions]

                async with recent_lock:
                    for suggestion in suggestions:
                        normalized = normalize_word(suggestion)
                        if normalized in recent_set:
                            continue
                        recent_suggestions.append(suggestion)
                        recent_set.add(normalized)
                        while len(recent_set) > len(recent_suggestions):
                            removed = recent_suggestions[0]
                            recent_set.discard(normalize_word(removed))

                if validate_missing_word_data(sentence, word_to_replace, suggestions):
                    return {
                        "id": sentence_id,
                        "sentence": sentence,
                        "word_to_replace": word_to_replace,
                        "word_suggestions": ",".join(suggestions)
                    }
                print(f"Invalid data for id={sentence_id}: '{word_to_replace}' | {suggestions}")
                return {
                    "id": sentence_id,
                    "sentence": sentence,
                    "word_to_replace": "",
                    "word_suggestions": ""
                }
            except Exception as exc:
                print(f"Error processing id={sentence_id}: {exc}")
                return {
                    "id": sentence_id,
                    "sentence": sentence,
                    "word_to_replace": "",
                    "word_suggestions": ""
                }

    tasks = [process_row(index, row) for index, row in enumerate(rows, start=1)]
    output_rows = await asyncio.gather(*tasks)

    with open(OUTPUT_CSV_PATH, "w", newline="", encoding="utf-8") as output_file:
        fieldnames = ["id", "sentence", "word_to_replace", "word_suggestions"]
        writer = csv.DictWriter(output_file, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"\nSaved {len(output_rows)} rows to {OUTPUT_CSV_PATH}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
