#!/usr/bin/env python3
"""
Generate Italian Sentences using OpenAI API with Instructor for structured output.
This script generates some new Italian sentences, validates them, and prints the results.
This script is for experiments only! Do not modify it if not explicitly instructed to do so!
"""

import os
import re
import asyncio
from typing import List
import pydantic
from dotenv import load_dotenv
from openai import OpenAI
import instructor


# Load environment variables
load_dotenv()

# Configuration
API_URL = "https://openrouter.ai/api/v1"
API_KEY = os.getenv("API_KEY")
MODEL_NAME = "qwen/qwen3-235b-a22b:free"

# Italian character set including accented vowels
ITALIAN_CHARACTERS = set('abcdefghiklmnopqrstuvzàèéìíîòóùú .,;:!?\'-')

# Pydantic model for structured output
class SentenceList(pydantic.BaseModel):
    sentences: List[str]

def is_valid_italian_sentence(sentence: str) -> bool:
    """
    Validate that a sentence:
    1. Contains only Italian letters (including accented characters)
    2. Has between 3 and 10 words
    3. Does not contain duplicate words
    """
    # Check word count
    word_count = len(sentence.split())
    if word_count < 3 or word_count > 10:
        return False
    
    # Check for duplicate words
    words = sentence.lower().split()
    if len(words) != len(set(words)):
        return False
    
    # Check character set
    sentence_lower = sentence.lower()
    for char in sentence_lower:
        if char not in ITALIAN_CHARACTERS:
            return False
    
    return True

def clean_sentence(sentence: str) -> str:
    """Clean and normalize sentence"""
    # Remove extra whitespace and normalize
    return ' '.join(sentence.strip().split())

async def generate_sentences() -> List[str]:
    """Generate Italian sentences using OpenAI with structured output"""
    
    # Initialize OpenAI client with instructor patch
    client = instructor.patch(OpenAI(base_url=API_URL, api_key=API_KEY))
    
    # System prompt to guide the LLM
    system_prompt = """Generate Italian sentences for language learning. 
Each sentence should:
- Be in Italian (not translated from English)
- Contain 3 to 10 words
- Be grammatically correct
- Use various and different topics
- Make some of them fun! Make some jokes!
- Use standard Italian characters including accented vowels (à, è, é, ì, í, î, ò, ó, ù, ú)

Examples of appropriate sentences:
- "L'unico mobile presente nella stanza era il nonno."
- "Questa stanza è troppo costosa, dormirò per strada."
- "Perché non ti piace Marco, ha la barba?"

Please generate exactly 25 sentences in the format requested."""
    
    try:
        print("Connecting to OpenAI API...")
        print(f"Using model: {MODEL_NAME}")
        print("Generating Italian sentences...")
        
        # Call the LLM with structured output
        response: SentenceList = client.chat.completions.create(
            model=MODEL_NAME,
            response_model=SentenceList,
            messages=[
                {"role": "system", "content": system_prompt},
            ]
        )
        
        print(f"Generated {len(response.sentences)} sentences from API")
        
        # Validate and clean sentences
        valid_sentences = []
        invalid_sentences = []
        
        for i, sentence in enumerate(response.sentences, 1):
            cleaned = clean_sentence(sentence)
            
            if is_valid_italian_sentence(cleaned):
                valid_sentences.append(cleaned)
            else:
                invalid_sentences.append((i, cleaned))
        
        print(f"\nValid sentences: {len(valid_sentences)}")
        print(f"Invalid sentences: {len(invalid_sentences)}")
        
        if invalid_sentences:
            print("\nInvalid sentences details:")
            for i, sentence in invalid_sentences:
                print(f"  Sentence {i}: '{sentence}'")
        
        return valid_sentences
        
    except Exception as e:
        print(f"Error generating sentences: {e}")
        return []

async def main():
    """Main function to generate and display Italian sentences"""
    print("=" * 60)
    print("Italian Sentence Generator")
    print("=" * 60)
    
    # Check API key
    if not API_KEY:
        print("ERROR: API_KEY not found in environment variables!")
        print("Please set API_KEY in your .env file")
        return
    
    print(f"API Key loaded: {'Yes' if API_KEY else 'No'}")
    print()
    
    # Generate sentences
    sentences = await generate_sentences()
    
    # Display results
    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    
    if sentences:
        print(f"Successfully generated {len(sentences)} valid Italian sentences:")
        print()
        for i, sentence in enumerate(sentences, 1):
            print(f"{i}. {sentence}")
    else:
        print("No valid sentences were generated.")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(main())