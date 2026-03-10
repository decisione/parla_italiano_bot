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
from typing import List

import pydantic
from dotenv import load_dotenv
from openai import OpenAI


# Load environment variables
load_dotenv()

# Configuration
API_URL = "https://openrouter.ai/api/v1"
LLM_API_KEY = os.getenv("LLM_API_KEY")
MODEL_NAME = "z-ai/glm-4.5-air:free"

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


def is_valid_italian_text(text: str) -> bool:
    for char in text.lower():
        if char not in ITALIAN_CHARACTERS:
            return False
    return True


def validate_missing_word_data(sentence: str, word_to_replace: str, suggestions: List[str]) -> bool:
    sentence_words = extract_words(sentence)
    target = normalize_word(word_to_replace)
    if not target or target not in sentence_words:
        return False
    if sentence_words.count(target) != 1:
        return False

    if not (2 <= len(suggestions) <= 4):
        return False

    normalized_suggestions = [normalize_word(s) for s in suggestions]
    if len(normalized_suggestions) != len(set(normalized_suggestions)):
        return False

    if target in normalized_suggestions:
        return False

    for suggestion in suggestions:
        if not suggestion.strip() or not is_valid_italian_text(suggestion):
            return False

    if any(suggestion in sentence_words for suggestion in normalized_suggestions):
        return False

    if not is_valid_italian_text(word_to_replace):
        return False

    return True


async def generate_missing_word_data(client: OpenAI, sentence: str) -> MissingWordResult:
    system_prompt = """You are generating missing word exercise data for Italian sentences.
Given the Italian sentence, select a single target word to replace and propose 2 to 4 alternative words.

Rules:
- The target word must appear exactly once in the sentence.
- The target word must be a single word (no spaces).
- Provide 2 to 4 alternative words in Italian.
- Alternatives must be unique, not present in the original sentence, and not equal to the target word.
- When any of alternative words put into sentence instead of target word, the sentence must become gramatically incorrect or absurd
- Output only valid JSON with keys: word_to_replace (string) and word_suggestions (array of strings).

Examples:
- For sentence 'Buongiorno a tutti' the target word might be 'Buongiorno', bad alternatives would be 'Buonasera, Ciao, Salve', good alternatives would be 'Locomotiva, Passeggiata, Morso'
- For sentence 'Mi piace la pizza' the target word might be 'pizza', bad alternatives would be 'pasta, lasagna, mela, pera', good alternatives would be 'tavolo, volare, Parigi, ieri'
"""

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

    output_rows = []
    for index, row in enumerate(rows[:3], start=1):
        sentence_id = row.get("id", "").strip()
        sentence = row.get("sentence", "").strip()

        if not sentence_id or not sentence:
            print(f"Skipping row {index}: missing id or sentence")
            output_rows.append({
                "id": sentence_id,
                "word_to_replace": "",
                "word_suggestions": ""
            })
            continue

        print(f"Processing sentence {index}/{len(rows)} (id={sentence_id})")

        try:
            result = await generate_missing_word_data(client, sentence)
            word_to_replace = result.word_to_replace.strip()
            suggestions = [s.strip() for s in result.word_suggestions]

            if validate_missing_word_data(sentence, word_to_replace, suggestions):
                output_rows.append({
                    "id": sentence_id,
                    "sentence": sentence,
                    "word_to_replace": word_to_replace,
                    "word_suggestions": ",".join(suggestions)
                })
            else:
                print(f"Invalid data for id={sentence_id}: '{word_to_replace}' | {suggestions}")
                output_rows.append({
                    "id": sentence_id,
                    "sentence": sentence,
                    "word_to_replace": "",
                    "word_suggestions": ""
                })
        except Exception as exc:
            print(f"Error processing id={sentence_id}: {exc}")
            output_rows.append({
                "id": sentence_id,
                "sentence": sentence,
                "word_to_replace": "",
                "word_suggestions": ""
            })

    with open(OUTPUT_CSV_PATH, "w", newline="", encoding="utf-8") as output_file:
        fieldnames = ["id", "sentence", "word_to_replace", "word_suggestions"]
        writer = csv.DictWriter(output_file, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"\nSaved {len(output_rows)} rows to {OUTPUT_CSV_PATH}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
