#!/usr/bin/env python3
"""
Quick working backend server with corrected YouTube API
"""

import json
import os
from pathlib import Path
from youtube_transcript_api import YouTubeTranscriptApi
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import re
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_video_id(url: str) -> str:
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

# Load basic vocabulary data
CEFR_WORDS = {}
def load_basic_vocab():
    global CEFR_WORDS
    script_dir = Path(__file__).parent
    vocab_dir = script_dir / "data" / "vocabulary"

    if vocab_dir.exists():
        for level in ['a1', 'a2', 'b1', 'b2', 'c1', 'c2']:
            vocab_file = vocab_dir / f"{level}_words.json"
            try:
                if vocab_file.exists():
                    with open(vocab_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        CEFR_WORDS[level] = set(word.lower() for word in data['words'])
                        print(f"Loaded {len(data['words'])} {level.upper()} words")
            except Exception as e:
                print(f"Error loading {vocab_file}: {e}")
                CEFR_WORDS[level] = set()

    total = sum(len(words) for words in CEFR_WORDS.values())
    print(f"Total vocabulary loaded: {total} words")

load_basic_vocab()

@app.get("/")
async def root():
    return {"message": "WORKING Language Learning API with CORRECTED YouTube API", "version": "FIXED"}

@app.post("/api/extract-content")
async def extract_content(video_data: dict):
    """Extract vocabulary and grammar with CORRECTED YouTube API"""
    try:
        video_url = video_data.get("videoUrl", "")
        user_level = video_data.get("userLevel", "A2")
        video_id = extract_video_id(video_url)

        if not video_id:
            return JSONResponse({"error": "Invalid YouTube URL", "source": "error"})

        print(f"🎬 Processing video: {video_id}")

        # CORRECTED YouTube Transcript API usage
        try:
            print("🔍 Attempting CORRECTED YouTube Transcript API...")
            api = YouTubeTranscriptApi()
            raw_transcript = api.fetch(video_id)

            # Convert to expected format
            transcript = []
            for entry in raw_transcript:
                transcript.append({
                    'text': entry.text,
                    'start': entry.start,
                    'duration': getattr(entry, 'duration', 0)
                })

            print(f"🎉 SUCCESS: Extracted {len(transcript)} entries")

            # Create transcript text
            transcript_text = " ".join([entry['text'] for entry in transcript])
            print(f"📝 Transcript length: {len(transcript_text)} characters")
            print(f"📝 Sample: {transcript_text[:200]}...")

            # Simple vocabulary extraction
            words = re.findall(r'\b[a-zA-Z]+\b', transcript_text.lower())
            common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'a', 'an'}

            interesting_words = []
            for word in set(words):
                if len(word) > 3 and word not in common_words:
                    interesting_words.append(word)

            # Create vocabulary
            vocabulary = []
            for i, word in enumerate(interesting_words[:8]):
                vocabulary.append({
                    "word": word,
                    "definition": f"extracted from video: {word}",
                    "level": "A2",
                    "timestamp": i * 30 + 15
                })

            # Create first 100 subtitles for debugging
            subtitle_debug = []
            for i, entry in enumerate(transcript[:100]):
                subtitle_debug.append({
                    "index": i,
                    "text": entry.get('text', ''),
                    "start": entry.get('start', 0),
                    "duration": entry.get('duration', 0)
                })

            return JSONResponse({
                "vocabulary": vocabulary,
                "grammar": [
                    {"concept": "Real Transcript", "explanation": "Extracted from actual video", "level": "A2", "timestamp": 30}
                ],
                "transcript_length": len(transcript_text),
                "source": "real_transcript_CORRECTED_API",
                "user_level": user_level,
                "transcript_entries": len(transcript),
                "subtitle_debug": subtitle_debug,
                "success": True
            })

        except Exception as e:
            print(f"❌ YouTube API failed: {e}")
            return JSONResponse({
                "vocabulary": [{"word": "failed", "definition": "API extraction failed", "level": "A1", "timestamp": 15}],
                "grammar": [{"concept": "Error", "explanation": str(e), "level": "A1", "timestamp": 30}],
                "source": "error_fallback",
                "error": str(e),
                "success": False
            })

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        return JSONResponse({"error": str(e), "source": "critical_error"})

if __name__ == "__main__":
    print("🚀 Starting CORRECTED backend server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)