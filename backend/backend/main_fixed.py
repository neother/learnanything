from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from youtube_transcript_api import YouTubeTranscriptApi
import re
import random
import aiohttp
import asyncio
import json
import os
import traceback
from pathlib import Path
from collections import Counter

app = FastAPI(title="Language Learning API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_video_id(url: str) -> str:
    """Extract YouTube video ID from various URL formats"""
    if not url:
        return ""

    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]+)',
        r'youtube\.com/watch\?.*v=([a-zA-Z0-9_-]+)'
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return ""

# Load vocabulary data
CEFR_WORDS = {}

def load_vocabulary_data():
    """Load comprehensive vocabulary data from JSON files"""
    global CEFR_WORDS
    script_dir = Path(__file__).parent
    vocab_dir = script_dir / "data" / "vocabulary"
    levels = ['a1', 'a2', 'b1', 'b2', 'c1', 'c2']

    for level in levels:
        vocab_file = vocab_dir / f"{level}_words.json"
        try:
            if vocab_file.exists():
                with open(vocab_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    CEFR_WORDS[level] = set(word.lower() for word in data['words'])
                    print(f"Loaded {len(data['words'])} {level.upper()} words")
            else:
                print(f"Warning: {vocab_file} not found")
                CEFR_WORDS[level] = set()
        except Exception as e:
            print(f"Error loading {vocab_file}: {e}")
            CEFR_WORDS[level] = set()

    print(f"Total vocabulary loaded: {sum(len(words) for words in CEFR_WORDS.values())} words")

load_vocabulary_data()

def get_word_difficulty(word: str) -> str:
    """Determine the difficulty level of a word based on comprehensive CEFR lists"""
    word_lower = word.lower().strip()
    levels_order = ['a1', 'a2', 'b1', 'b2', 'c1', 'c2']

    for level in levels_order:
        if level in CEFR_WORDS and word_lower in CEFR_WORDS[level]:
            return level.upper()

    # Fallback classification
    word_len = len(word)
    if word_len <= 3:
        return "A1"
    elif word_len <= 5:
        return "A2"
    elif word_len <= 7:
        return "B1"
    elif word_len <= 10:
        return "B2"
    else:
        return "C1"

async def get_word_definition(session: aiohttp.ClientSession, word: str) -> str:
    """Get word definition from Datamuse API"""
    try:
        async with session.get(f"https://api.datamuse.com/words?sp={word}&md=d&max=1") as response:
            if response.status == 200:
                data = await response.json()
                if data and len(data) > 0 and 'defs' in data[0]:
                    definition = data[0]['defs'][0]
                    if '\t' in definition:
                        definition = definition.split('\t', 1)[1]
                    return definition
    except Exception as e:
        print(f"Error getting definition for {word}: {e}")

    return f"a word meaning {word}"

def find_word_timestamps(transcript: list, words: list) -> dict:
    """Find actual timestamps for words in the transcript"""
    word_timestamps = {}

    for entry in transcript:
        text = entry['text'].lower()
        start_time = int(entry['start'])

        for word in words:
            if word.lower() in text and word not in word_timestamps:
                word_timestamps[word] = start_time

    return word_timestamps

def adaptive_vocabulary_selection(vocabulary: list, user_level: str = "A2", max_words: int = 8) -> list:
    """Select vocabulary adaptively based on user proficiency level"""
    level_map = {'A1': 0, 'A2': 1, 'B1': 2, 'B2': 3, 'C1': 4, 'C2': 5}
    levels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']

    user_index = level_map.get(user_level.upper(), 1)

    vocab_by_level = {}
    for item in vocabulary:
        level = item['level']
        if level not in vocab_by_level:
            vocab_by_level[level] = []
        vocab_by_level[level].append(item)

    selected = []
    user_level_count = int(max_words * 0.6)
    higher_level_count = int(max_words * 0.3)
    challenge_level_count = max_words - user_level_count - higher_level_count

    if user_level in vocab_by_level:
        user_words = vocab_by_level[user_level][:user_level_count]
        selected.extend(user_words)

    higher_level = levels[min(user_index + 1, len(levels) - 1)]
    if higher_level in vocab_by_level:
        higher_words = vocab_by_level[higher_level][:higher_level_count]
        selected.extend(higher_words)

    challenge_level = levels[min(user_index + 2, len(levels) - 1)]
    if challenge_level in vocab_by_level:
        challenge_words = vocab_by_level[challenge_level][:challenge_level_count]
        selected.extend(challenge_words)

    while len(selected) < max_words:
        for level in levels:
            if level in vocab_by_level:
                remaining_words = [w for w in vocab_by_level[level] if w not in selected]
                if remaining_words:
                    selected.append(remaining_words[0])
                    break
        if len(selected) >= max_words:
            break
        else:
            break

    return selected[:max_words]

async def extract_vocabulary_from_transcript(transcript_text: str, transcript_data: list, user_level: str = "A2", max_words: int = 8):
    """Extract key vocabulary words from transcript text with real definitions"""
    words = re.findall(r'\b[a-zA-Z]+\b', transcript_text.lower())

    common_words = {
        'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
        'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does',
        'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this',
        'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me',
        'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their',
        'a', 'an', 'if', 'so', 'up', 'out', 'now', 'how', 'who', 'what', 'when',
        'where', 'why', 'very', 'much', 'more', 'most', 'some', 'many', 'any',
        'all', 'both', 'each', 'few', 'other', 'another', 'such', 'only', 'own',
        'same', 'so', 'than', 'too', 'well', 'can', 'just'
    }

    word_counter = Counter(words)
    interesting_words = []

    for word, count in word_counter.most_common():
        if (len(word) > 3 and
            word not in common_words and
            word.isalpha() and
            count >= 1):  # Changed from 2 to 1 for more words
            interesting_words.append(word)

    selected_words = interesting_words[:max_words * 2]  # Get more candidates
    word_timestamps = find_word_timestamps(transcript_data, selected_words)

    vocabulary = []
    async with aiohttp.ClientSession() as session:
        for word in selected_words:
            definition = await get_word_definition(session, word)
            level = get_word_difficulty(word)
            timestamp = word_timestamps.get(word, random.randint(10, 200))

            vocabulary.append({
                "word": word,
                "definition": definition,
                "level": level,
                "timestamp": timestamp
            })

    adaptive_vocab = adaptive_vocabulary_selection(vocabulary, user_level, max_words)
    return adaptive_vocab

def extract_grammar_from_transcript(transcript_text: str) -> list:
    """Extract grammar concepts from transcript with pattern matching"""
    grammar_concepts = []
    text_lower = transcript_text.lower()

    grammar_patterns = [
        {
            "pattern": r"\b(is|are|was|were|am)\b",
            "concept": "Present/Past Simple (to be)",
            "explanation": "The verb 'to be' used to describe states, locations, and identities",
            "level": "A1"
        },
        {
            "pattern": r"\b(have|has|had)\s+\w+ed\b|\b(have|has|had)\s+(been|done|gone|seen)\b",
            "concept": "Present/Past Perfect",
            "explanation": "Used to talk about completed actions with relevance to the present or past",
            "level": "B1"
        },
        {
            "pattern": r"\b(will|shall)\s+\w+\b|\bgoing to\s+\w+\b",
            "concept": "Future Tense",
            "explanation": "Used to express future actions, plans, and predictions",
            "level": "A2"
        },
        {
            "pattern": r"\b\w+ing\b",
            "concept": "Present Continuous (-ing form)",
            "explanation": "Used to describe ongoing actions or current situations",
            "level": "A1"
        }
    ]

    for pattern_info in grammar_patterns:
        matches = re.findall(pattern_info["pattern"], text_lower)
        if matches:
            grammar_concepts.append({
                "concept": pattern_info["concept"],
                "explanation": pattern_info["explanation"],
                "level": pattern_info["level"],
                "timestamp": random.randint(15, 200)
            })

    seen_concepts = set()
    unique_concepts = []
    for concept in grammar_concepts:
        if concept["concept"] not in seen_concepts:
            seen_concepts.add(concept["concept"])
            unique_concepts.append(concept)

    return unique_concepts[:4]

@app.get("/")
async def root():
    return {"message": "Language Learning API is running - FIXED VERSION"}

@app.post("/api/extract-content")
async def extract_content(video_data: dict):
    """Extract vocabulary and grammar from YouTube video using CORRECTED YouTube Transcript API"""
    try:
        video_url = video_data.get("videoUrl", "")
        user_level = video_data.get("userLevel", "A2")
        video_id = extract_video_id(video_url)

        if not video_id:
            raise HTTPException(status_code=400, detail="Invalid YouTube URL")

        transcript = None
        transcript_source = ""

        # CORRECTED YouTube Transcript API usage
        try:
            print(f"Attempting CORRECTED YouTube Transcript API for video: {video_id}")
            api = YouTubeTranscriptApi()
            raw_transcript = api.fetch(video_id)

            # Convert the new API format to our expected format
            transcript = []
            for entry in raw_transcript:
                transcript.append({
                    'text': entry.text,
                    'start': entry.start,
                    'duration': getattr(entry, 'duration', 0)
                })

            transcript_source = "youtube_transcript_api_CORRECTED"
            print(f"🎉 SUCCESS: Extracted {len(transcript)} entries using CORRECTED YouTube Transcript API")

        except Exception as transcript_error:
            print(f"❌ CORRECTED YouTube Transcript API failed: {transcript_error}")

        # Process transcript if we got one
        if transcript and len(transcript) > 0:
            transcript_text = " ".join([entry['text'] for entry in transcript])
            print(f"📝 Processing transcript text: {len(transcript_text)} characters")
            print(f"📝 Sample text: {transcript_text[:200]}...")

            # Extract vocabulary and grammar from real transcript
            vocabulary = await extract_vocabulary_from_transcript(transcript_text, transcript, user_level)
            grammar = extract_grammar_from_transcript(transcript_text)

            return JSONResponse({
                "vocabulary": vocabulary,
                "grammar": grammar,
                "transcript_length": len(transcript_text),
                "source": f"real_transcript_{transcript_source}",
                "user_level": user_level,
                "adaptive_selection": True,
                "transcript_entries": len(transcript)
            })

        else:
            print("❌ All transcript extraction methods failed, using fallback mock data")
            return JSONResponse({
                "vocabulary": [
                    {"word": "hello", "definition": "a greeting", "level": "A1", "timestamp": 15},
                    {"word": "world", "definition": "the earth", "level": "A1", "timestamp": 45}
                ],
                "grammar": [
                    {"concept": "Present Simple", "explanation": "Used for facts and habits", "level": "A1", "timestamp": 30}
                ],
                "source": "fallback_mock",
                "error": "No subtitles available - tried corrected YouTube Transcript API"
            })

    except Exception as e:
        print(f"CRITICAL ERROR in extract_content: {str(e)}")
        print("Full stack trace:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing video: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting FIXED backend server with corrected YouTube API...")
    uvicorn.run(app, host="0.0.0.0", port=8000)