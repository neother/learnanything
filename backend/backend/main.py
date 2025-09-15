from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from youtube_transcript_api import YouTubeTranscriptApi
try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    print("yt-dlp not available, will use YouTube Transcript API only")
    YT_DLP_AVAILABLE = False
import re
import random
import aiohttp
import asyncio
import ssl
import json
import os
import traceback
import tempfile
import subprocess
from pathlib import Path
from collections import Counter
import hashlib
import time
try:
    from googletrans import Translator
    translator = Translator()
    TRANSLATION_ENABLED = True
except ImportError:
    print("Google Translate not available, translation disabled")
    translator = None
    TRANSLATION_ENABLED = False

app = FastAPI(title="Language Learning API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=False,  # Disable credentials to allow wildcard origin
    allow_methods=["*"],
    allow_headers=["*"],
)

# Translator initialized above with error handling

# Translation cache file
TRANSLATION_CACHE_FILE = "translation_cache.json"

# Load translation cache
def load_translation_cache():
    """Load existing translations from cache file"""
    if os.path.exists(TRANSLATION_CACHE_FILE):
        try:
            with open(TRANSLATION_CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading translation cache: {e}")
            return {}
    return {}

# Save translation cache
def save_translation_cache(cache):
    """Save translations to cache file"""
    try:
        with open(TRANSLATION_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving translation cache: {e}")

# Global translation cache
translation_cache = load_translation_cache()

def get_chinese_translation(word):
    """Get Chinese translation for a word, using cache if available"""
    word_lower = word.lower().strip()

    # Hardcoded translations for common vocabulary words
    hardcoded_translations = {
        'campus': '校园',
        'people': '人们',
        'about': '关于',
        'from': '从',
        'said': '说',
        'time': '时间',
        'come': '来',
        'go': '去',
        'see': '看',
        'know': '知道',
        'get': '得到',
        'make': '制作',
        'think': '想',
        'take': '拿',
        'look': '看',
        'want': '想要',
        'give': '给',
        'find': '找到',
        'tell': '告诉',
        'work': '工作',
        'call': '打电话',
        'try': '试试',
        'ask': '问',
        'feel': '感觉',
        'leave': '离开',
        'put': '放',
        'mean': '意思',
        'keep': '保持',
        'let': '让',
        'begin': '开始'
    }

    # Use hardcoded translation if available
    if word_lower in hardcoded_translations:
        translation = hardcoded_translations[word_lower]
        try:
            print(f"Using hardcoded translation '{word}' -> '{translation}'")
        except UnicodeEncodeError:
            print(f"Using hardcoded translation '{word}' -> [Chinese characters]")
        return translation

    # Check cache first
    if word_lower in translation_cache:
        return translation_cache[word_lower]

    try:
        if not TRANSLATION_ENABLED or translator is None:
            # Return original word if translation is disabled
            return word

        # Get translation from Google Translate
        result = translator.translate(word_lower, dest='zh-cn')
        translation = result.text if result else word

        # Cache the result
        translation_cache[word_lower] = translation
        save_translation_cache(translation_cache)

        print(f"Translated '{word}' to '{translation}'")
        return translation

    except Exception as e:
        print(f"Translation error for '{word}': {e}")
        # Return the original word if translation fails
        return word

# Common proper nouns to skip for vocabulary learning
COMMON_PROPER_NOUNS = {
    # Common first names
    'john', 'james', 'mary', 'robert', 'patricia', 'jennifer', 'linda', 'elizabeth', 'barbara', 'susan',
    'jessica', 'sarah', 'karen', 'nancy', 'lisa', 'betty', 'helen', 'sandra', 'donna', 'carol',
    'michael', 'william', 'david', 'richard', 'charles', 'joseph', 'thomas', 'christopher', 'daniel', 'paul',
    'mark', 'donald', 'steven', 'kenneth', 'andrew', 'joshua', 'brian', 'george', 'edward', 'ronald',
    'timothy', 'jason', 'jeffrey', 'ryan', 'jacob', 'gary', 'nicholas', 'eric', 'jonathan', 'stephen',
    'larry', 'justin', 'scott', 'brandon', 'benjamin', 'samuel', 'gregory', 'frank', 'raymond', 'alexander',
    'patrick', 'jack', 'dennis', 'jerry', 'tyler', 'aaron', 'jose', 'henry', 'adam', 'douglas',
    'nathan', 'peter', 'zachary', 'kyle', 'noah', 'alan', 'ethan', 'jeremy', 'lionel', 'angel',
    'mason', 'evan', 'liam', 'oliver', 'lucas', 'charlie', 'kirk', 'emily', 'hannah', 'madison', 'ashley',
    'grace', 'britney', 'samantha', 'rachel', 'lauren', 'alexis', 'alyssa', 'kayla', 'megan', 'anna',

    # Common cities and countries
    'america', 'american', 'china', 'chinese', 'japan', 'japanese', 'korea', 'korean', 'england', 'english',
    'france', 'french', 'germany', 'german', 'italy', 'italian', 'spain', 'spanish', 'russia', 'russian',
    'canada', 'canadian', 'australia', 'australian', 'brazil', 'brazilian', 'mexico', 'mexican',
    'london', 'paris', 'tokyo', 'beijing', 'shanghai', 'york', 'angeles', 'chicago', 'houston', 'phoenix',
    'philadelphia', 'antonio', 'diego', 'dallas', 'jose', 'austin', 'jacksonville', 'francisco',
    'columbus', 'charlotte', 'fort', 'detroit', 'memphis', 'boston', 'seattle', 'denver', 'washington',
    'nashville', 'baltimore', 'louisville', 'milwaukee', 'portland', 'vegas', 'oklahoma', 'tucson',
    'atlanta', 'colorado', 'raleigh', 'omaha', 'miami', 'oakland', 'minneapolis', 'tulsa', 'cleveland',
    'wichita', 'arlington', 'utah', 'california', 'texas', 'florida', 'illinois', 'pennsylvania',
    'ohio', 'georgia', 'michigan', 'carolina', 'jersey', 'virginia', 'tennessee', 'indiana',
    'arizona', 'massachusetts', 'maryland', 'missouri', 'wisconsin', 'minnesota', 'colorado', 'alabama',
    'louisiana', 'kentucky', 'oregon', 'oklahoma', 'connecticut', 'arkansas', 'mississippi', 'kansas',
    'nevada', 'mexico', 'nebraska', 'virginia', 'hampshire', 'maine', 'hawaii', 'idaho', 'montana',
    'dakota', 'delaware', 'alaska', 'vermont', 'wyoming'
}

def is_proper_noun(word: str) -> bool:
    """Check if a word is likely a proper noun that should be skipped"""
    word_lower = word.lower().strip()

    # Check against common proper nouns list
    if word_lower in COMMON_PROPER_NOUNS:
        return True

    return False

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

# Subtitle caching system
CACHE_DIR = Path(__file__).parent / "cache" / "subtitles"
# Cache never expires - subtitles are always valid
CACHE_EXPIRY_HOURS = float('inf')  # Cache never expires

def ensure_cache_dir():
    """Create cache directory if it doesn't exist"""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

def get_cache_filename(video_id: str) -> Path:
    """Generate cache filename for a video ID"""
    return CACHE_DIR / f"{video_id}.json"

def get_cached_subtitles(video_id: str) -> dict:
    """Get cached subtitles if they exist - cache never expires"""
    ensure_cache_dir()
    cache_file = get_cache_filename(video_id)

    if cache_file.exists():
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)

            # Calculate cache age for informational purposes
            cache_time = cached_data.get('cached_at', 0)
            current_time = time.time()
            hours_since_cache = (current_time - cache_time) / 3600

            print(f"Using cached subtitles for {video_id} (cached {hours_since_cache:.1f}h ago)")
            return cached_data.get('subtitles', [])

        except Exception as e:
            print(f"Error reading cache for {video_id}: {e}")
            if cache_file.exists():
                cache_file.unlink()  # Delete corrupted cache

    return None

def cache_subtitles(video_id: str, raw_subtitles: list):
    """Cache PURE RAW subtitles exactly as received from YouTube API (no modifications)"""
    ensure_cache_dir()
    cache_file = get_cache_filename(video_id)

    try:
        cache_data = {
            'video_id': video_id,
            'cached_at': time.time(),
            'subtitles': raw_subtitles,  # Store PURE RAW subtitles exactly as received
            'type': 'raw_youtube_segments',
            'source': 'youtube_transcript_api'
        }

        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)

        print(f"Cached PURE RAW subtitles for {video_id} ({len(raw_subtitles)} original segments)")

    except Exception as e:
        print(f"Error caching subtitles for {video_id}: {e}")

def extract_subtitles_with_ytdlp(video_url: str) -> list:
    """Extract subtitles using yt-dlp with multiple fallback methods"""
    try:
        # Configure yt-dlp options for subtitle extraction
        ydl_opts = {
            'writesubtitles': False,
            'writeautomaticsub': True,
            'subtitleslangs': ['en', 'en-US', 'en-GB'],
            'skip_download': True,
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'format': 'best',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Get video info including available subtitles
            info = ydl.extract_info(video_url, download=False)

            # Try to get manual subtitles first
            subtitles_data = info.get('subtitles', {})
            auto_subtitles_data = info.get('automatic_captions', {})

            print(f"Available manual subtitles: {list(subtitles_data.keys())}")
            print(f"Available auto subtitles: {list(auto_subtitles_data.keys())}")

            # Priority order: manual English subtitles, then auto English subtitles
            subtitle_sources = []

            # Check for manual subtitles
            for lang in ['en', 'en-US', 'en-GB']:
                if lang in subtitles_data:
                    subtitle_sources.extend(subtitles_data[lang])
                    break

            # Fallback to automatic subtitles if no manual ones
            if not subtitle_sources:
                for lang in ['en', 'en-US', 'en-GB']:
                    if lang in auto_subtitles_data:
                        subtitle_sources.extend(auto_subtitles_data[lang])
                        break

            if not subtitle_sources:
                raise Exception("No English subtitles found (manual or automatic)")

            # Find the best subtitle format (prefer vtt, then srv3, then ttml)
            best_subtitle = None
            for subtitle in subtitle_sources:
                if subtitle.get('ext') == 'vtt':
                    best_subtitle = subtitle
                    break
                elif subtitle.get('ext') in ['srv3', 'ttml'] and not best_subtitle:
                    best_subtitle = subtitle

            if not best_subtitle:
                best_subtitle = subtitle_sources[0]  # Use first available

            print(f"Using subtitle format: {best_subtitle.get('ext')}")

            # Download subtitle content
            import urllib.request
            subtitle_url = best_subtitle['url']
            with urllib.request.urlopen(subtitle_url) as response:
                subtitle_content = response.read().decode('utf-8')

            # Parse subtitle content based on format
            transcript_entries = []

            if best_subtitle.get('ext') == 'vtt':
                transcript_entries = parse_vtt_subtitles(subtitle_content)
            elif best_subtitle.get('ext') == 'srv3':
                transcript_entries = parse_srv3_subtitles(subtitle_content)
            elif best_subtitle.get('ext') == 'ttml':
                transcript_entries = parse_ttml_subtitles(subtitle_content)
            else:
                # Try to parse as generic format
                transcript_entries = parse_generic_subtitles(subtitle_content)

            print(f"Parsed {len(transcript_entries)} subtitle entries")
            return transcript_entries

    except Exception as e:
        print(f"yt-dlp subtitle extraction failed: {e}")
        raise e

def parse_vtt_subtitles(content: str) -> list:
    """Parse WebVTT subtitle format"""
    entries = []
    lines = content.split('\n')

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Skip header and empty lines
        if not line or line.startswith('WEBVTT') or line.startswith('NOTE'):
            i += 1
            continue

        # Look for timestamp line
        if '-->' in line:
            # Parse timestamps
            time_parts = line.split(' --> ')
            if len(time_parts) == 2:
                start_time = parse_vtt_timestamp(time_parts[0])

                # Get subtitle text (next non-empty lines)
                i += 1
                text_lines = []
                while i < len(lines) and lines[i].strip():
                    text_lines.append(lines[i].strip())
                    i += 1

                if text_lines:
                    text = ' '.join(text_lines)
                    # Clean VTT formatting tags
                    text = re.sub(r'<[^>]+>', '', text)
                    entries.append({
                        'text': text,
                        'start': start_time
                    })

        i += 1

    return entries

def parse_vtt_timestamp(timestamp: str) -> float:
    """Convert VTT timestamp to seconds"""
    try:
        # Format: 00:00:30.500 or 30.500
        timestamp = timestamp.strip()

        if ':' in timestamp:
            parts = timestamp.split(':')
            if len(parts) == 3:
                hours, minutes, seconds = parts
                return float(hours) * 3600 + float(minutes) * 60 + float(seconds)
            elif len(parts) == 2:
                minutes, seconds = parts
                return float(minutes) * 60 + float(seconds)
        else:
            return float(timestamp)
    except:
        return 0.0

def parse_srv3_subtitles(content: str) -> list:
    """Parse YouTube's srv3 XML subtitle format"""
    entries = []
    import xml.etree.ElementTree as ET

    try:
        root = ET.fromstring(content)

        for text_elem in root.findall('.//text'):
            start_time = float(text_elem.get('start', 0))
            text = text_elem.text or ''

            # Clean HTML entities and tags
            text = re.sub(r'&[^;]+;', '', text)
            text = re.sub(r'<[^>]+>', '', text)
            text = text.strip()

            if text:
                entries.append({
                    'text': text,
                    'start': start_time
                })

    except Exception as e:
        print(f"Error parsing srv3: {e}")

    return entries

def parse_ttml_subtitles(content: str) -> list:
    """Parse TTML subtitle format"""
    entries = []
    import xml.etree.ElementTree as ET

    try:
        # Remove namespace prefixes for easier parsing
        content = re.sub(r'xmlns[^=]*="[^"]*"', '', content)
        content = re.sub(r'</?tt[^>]*>', '', content)

        root = ET.fromstring('<root>' + content + '</root>')

        for p_elem in root.findall('.//p'):
            begin = p_elem.get('begin', '0s')
            text = ''.join(p_elem.itertext()).strip()

            # Convert time format (e.g., "30.5s" to seconds)
            start_time = 0.0
            if begin.endswith('s'):
                start_time = float(begin[:-1])

            if text:
                entries.append({
                    'text': text,
                    'start': start_time
                })

    except Exception as e:
        print(f"Error parsing TTML: {e}")

    return entries

def parse_generic_subtitles(content: str) -> list:
    """Fallback parser for unknown subtitle formats"""
    entries = []
    lines = content.split('\n')

    # Look for any lines that might be subtitle text
    for line in lines:
        line = line.strip()
        if line and not re.match(r'^\d+$', line) and '-->' not in line:
            # Clean common subtitle artifacts
            line = re.sub(r'<[^>]+>', '', line)
            line = re.sub(r'&[^;]+;', '', line)
            if len(line) > 10:  # Only keep substantial text
                entries.append({
                    'text': line,
                    'start': 0.0  # No timing info available
                })

    return entries

# Comprehensive CEFR word lists loaded from JSON files
CEFR_WORDS = {}

def load_vocabulary_data():
    """Load comprehensive vocabulary data from JSON files"""
    global CEFR_WORDS

    # Get the directory where this script is located
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

# Load vocabulary data on startup
load_vocabulary_data()

def get_word_difficulty(word: str) -> str:
    """Determine the difficulty level of a word based on comprehensive CEFR lists"""
    word_lower = word.lower().strip()

    # Skip proper nouns (names, cities, countries) for vocabulary learning
    if word.strip() and is_proper_noun(word):
        return "SKIP"

    # Check against comprehensive CEFR word lists in order of difficulty
    levels_order = ['a1', 'a2', 'b1', 'b2', 'c1', 'c2']

    for level in levels_order:
        if level in CEFR_WORDS and word_lower in CEFR_WORDS[level]:
            return level.upper()

    # Advanced fallback classification for unlisted words
    word_len = len(word)

    # Very short common words likely A1
    if word_len <= 3:
        return "A1"
    # Short words likely A1-A2
    elif word_len <= 5:
        return "A2"
    # Medium words likely A2-B1
    elif word_len <= 7:
        return "B1"
    # Longer words likely B2-C1
    elif word_len <= 10:
        return "B2"
    # Very long words likely C1-C2
    else:
        return "C1"

# Enhanced Vocabulary Data Loading
enhanced_vocab_cache = {}

def load_enhanced_vocabulary(level: str) -> dict:
    """Load enhanced vocabulary data for a specific CEFR level"""
    global enhanced_vocab_cache

    if level in enhanced_vocab_cache:
        return enhanced_vocab_cache[level]

    try:
        enhanced_file = f"data/vocabulary_enhanced/{level.lower()}_enhanced.json"
        with open(enhanced_file, 'r', encoding='utf-8') as f:
            enhanced_data = json.load(f)
            enhanced_vocab_cache[level] = enhanced_data
            return enhanced_data
    except FileNotFoundError:
        print(f"Enhanced vocabulary file not found for level {level}")
        return {}
    except Exception as e:
        print(f"Error loading enhanced vocabulary for {level}: {e}")
        return {}

def get_enhanced_word_info(word: str, level: str) -> dict:
    """Get enhanced information for a word including definition, usage, examples"""

    # Load enhanced vocabulary for the word's level
    enhanced_vocab = load_enhanced_vocabulary(level)

    if enhanced_vocab and word.lower() in enhanced_vocab.get('words', {}):
        word_info = enhanced_vocab['words'][word.lower()]
        return {
            "definition": word_info.get('meaning_en', f"a word that means {word}"),
            "definition_zh": word_info.get('meaning_zh', ''),
            "usage": word_info.get('usage', ''),
            "examples": word_info.get('examples', []),
            "synonyms": word_info.get('synonyms', []),
            "collocations": word_info.get('collocations', []),
            "pos": word_info.get('pos', [])
        }

    # Fallback to simple definition if enhanced data not available
    return {
        "definition": get_simple_definition(word),
        "definition_zh": '',
        "usage": '',
        "examples": [],
        "synonyms": [],
        "collocations": [],
        "pos": []
    }

def get_simple_definition(word: str) -> str:
    """Get simple, kid-friendly definitions"""

    # Simple definitions for common words - perfect for kids
    simple_definitions = {
        "hello": "a way to greet someone",
        "world": "the earth we live on",
        "time": "when things happen",
        "people": "humans like you and me",
        "water": "what you drink to stay healthy",
        "house": "a place where people live",
        "school": "where you go to learn",
        "friend": "someone you like and play with",
        "happy": "feeling good and smiling",
        "love": "caring about someone very much",
        "food": "what you eat to grow strong",
        "family": "the people who care for you",
        "money": "what people use to buy things",
        "work": "what grown-ups do to earn money",
        "play": "having fun and games",
        "learn": "getting smarter about something",
        "help": "making things easier for someone",
        "good": "nice or well done",
        "big": "very large in size",
        "small": "tiny or little",
        "fast": "moving very quickly",
        "slow": "moving not quickly",
        "hot": "very warm temperature",
        "cold": "very cool temperature",
        "new": "just made or recent",
        "old": "been around for a long time",
        "easy": "not hard to do",
        "hard": "difficult to do",
        "nice": "pleasant and kind",
        "fun": "enjoyable and entertaining",
        "book": "pages with words to read",
        "car": "a vehicle that drives on roads",
        "dog": "a friendly animal that barks",
        "cat": "a soft animal that meows",
        "tree": "a tall plant with leaves",
        "sun": "the bright light in the sky",
        "moon": "the round light at night",
        "day": "when the sun is out",
        "night": "when it's dark outside",
        "morning": "the early part of the day",
        "evening": "the late part of the day",
        "week": "seven days together",
        "year": "twelve months together",
        "red": "the color of apples",
        "blue": "the color of the sky",
        "green": "the color of grass",
        "yellow": "the color of the sun",
        "black": "the darkest color",
        "white": "the lightest color",
        "talk": "using words to communicate",
        "walk": "moving forward on your feet",
        "run": "moving very fast on your feet",
        "jump": "pushing off the ground",
        "sit": "putting your bottom on something",
        "stand": "being up on your feet",
        "eat": "putting food in your mouth",
        "drink": "swallowing liquid",
        "sleep": "resting with your eyes closed",
        "wake": "stopping sleep and opening eyes",
        "give": "letting someone have something",
        "take": "getting something for yourself",
        "come": "moving toward someone",
        "door": "what you open to enter a room",
        "window": "what you look through to see outside",
        "table": "flat surface to put things on",
        "chair": "what you sit on",
        "bed": "where you sleep at night",
        "room": "a space inside a house",
        "kitchen": "where food is cooked",
        "bathroom": "where you wash and use toilet",
        "garden": "place where plants grow",
        "park": "outdoor place to play",
        "store": "place where you buy things",
        "hospital": "place where sick people get help",
        "library": "place with many books",
        "museum": "place with interesting old things",
        "restaurant": "place where you buy food to eat",
        "bank": "place where money is kept safe",
        "post": "sending letters to people",
        "office": "place where people work",
        "factory": "place where things are made",
        "farm": "place where food is grown",
        "city": "big place where many people live",
        "country": "a large area with its own government",
        "river": "long flowing water",
        "mountain": "very high hill",
        "beach": "sandy place by the ocean",
        "forest": "place with many trees",
        "desert": "very dry place with sand",
        "island": "land surrounded by water",
        "bridge": "what helps you cross over water",
        "road": "where cars drive",
        "train": "long vehicle that runs on tracks",
        "plane": "flying vehicle in the sky",
        "boat": "vehicle that floats on water",
        "bike": "two-wheeled vehicle you pedal",
        "bus": "big vehicle that carries many people",
        "must": "have to do something",
        "advice": "helpful suggestions from others",
        "base": "the bottom part of something",
        "verb": "an action word",
        "obligation": "something you have to do",
        "recommendation": "suggesting something good"
    }

    # Return simple definition if we have one
    if word.lower() in simple_definitions:
        return simple_definitions[word.lower()]

    # For unknown words, create a very simple definition
    return f"a word that means {word}"

def split_by_sentence_punctuation(segment):
    """
    Split a segment if it contains multiple sentences (punctuation + capital letter).

    Args:
        segment: Single subtitle segment that contains multiple sentences

    Returns:
        List of split segments, each containing one sentence
    """
    text = segment['text']
    start_time = segment['start']
    duration = segment.get('duration', 0)

    # Look for sentence boundaries: punctuation (including comma) followed by space and capital letter
    sentence_breaks = list(re.finditer(r'([.!?,])\s+([A-Z])', text))

    if not sentence_breaks:
        return [segment]  # No sentence breaks found

    segments = []
    current_pos = 0

    for i, match in enumerate(sentence_breaks):
        # Extract text up to and including the punctuation
        end_pos = match.start(2)  # Position of capital letter
        sentence_text = text[current_pos:end_pos].strip()

        if sentence_text:
            # Calculate timing proportionally based on character count
            char_ratio = len(sentence_text) / len(text)
            sentence_duration = duration * char_ratio
            sentence_start = start_time + (duration * (current_pos / len(text)))

            segments.append({
                'text': sentence_text,
                'start': sentence_start,
                'duration': sentence_duration,
                'end': sentence_start + sentence_duration,
                'split_method': 'sentence_punctuation',
                'original_segments': 1
            })

        current_pos = match.start(2)  # Start of next sentence (capital letter)

    # Add remaining text as final segment
    if current_pos < len(text):
        remaining_text = text[current_pos:].strip()
        if remaining_text:
            remaining_duration = duration - sum(seg['duration'] for seg in segments)
            remaining_start = start_time + sum(seg['duration'] for seg in segments)

            segments.append({
                'text': remaining_text,
                'start': remaining_start,
                'duration': remaining_duration,
                'end': remaining_start + remaining_duration,
                'split_method': 'sentence_punctuation',
                'original_segments': 1
            })

    print(f"Split sentence: '{text[:50]}...' -> {len(segments)} sentences")
    return segments

def split_long_segment(segment, max_duration=8.0):
    """
    Split overly long segments into manageable chunks for better learning experience.

    Args:
        segment: Single subtitle segment that's too long
        max_duration: Maximum duration per chunk (default: 10 seconds)

    Returns:
        List of split segments with proper timing
    """
    text = segment['text']
    start_time = segment['start']
    total_duration = segment['duration']

    # If segment is short enough, return as-is
    if total_duration <= max_duration:
        return [segment]

    # Try splitting by natural breaks first (in order of preference)
    natural_breaks = [' - ', '. ', '! ', '? ', ', ', ' and ', ' but ', ' so ', ' because ']

    for break_char in natural_breaks:
        if break_char in text:
            parts = text.split(break_char)
            if len(parts) > 1:
                segments = []
                current_time = start_time
                words_per_second = len(text.split()) / total_duration

                for i, part in enumerate(parts):
                    if part.strip():
                        # Add back the break character (except for last part)
                        if i < len(parts) - 1:
                            part_text = part.strip() + break_char.strip()
                        else:
                            part_text = part.strip()

                        # Calculate duration based on word count
                        part_words = len(part_text.split())
                        part_duration = max(2.0, part_words / words_per_second)  # Min 2 seconds

                        # Ensure we don't exceed total duration
                        if current_time + part_duration > start_time + total_duration:
                            part_duration = start_time + total_duration - current_time

                        segments.append({
                            'text': part_text,
                            'start': current_time,
                            'duration': part_duration,
                            'end': current_time + part_duration,
                            'split_method': f'natural_break_{break_char.strip()}',
                            'original_segments': 1
                        })
                        current_time += part_duration

                        # Break if we've used up all the time
                        if current_time >= start_time + total_duration:
                            break

                # Filter out segments that are still too long and recursively split them
                final_segments = []
                for seg in segments:
                    if seg['duration'] > max_duration:
                        final_segments.extend(split_long_segment(seg, max_duration))
                    else:
                        final_segments.append(seg)

                return final_segments

    # Fallback: split by time intervals if no natural breaks work
    words = text.split()
    words_per_chunk = max(10, int(len(words) * (max_duration / total_duration)))  # Min 10 words

    segments = []
    current_time = start_time

    for i in range(0, len(words), words_per_chunk):
        chunk_words = words[i:i + words_per_chunk]
        chunk_text = ' '.join(chunk_words)

        # Calculate duration based on remaining time and word ratio
        remaining_words = len(words) - i
        time_ratio = len(chunk_words) / remaining_words if remaining_words > 0 else 1
        remaining_time = start_time + total_duration - current_time
        chunk_duration = min(max_duration, remaining_time * time_ratio)

        segments.append({
            'text': chunk_text,
            'start': current_time,
            'duration': chunk_duration,
            'end': current_time + chunk_duration,
            'split_method': 'time_interval',
            'original_segments': 1
        })

        current_time += chunk_duration

        if current_time >= start_time + total_duration:
            break

    return segments

def post_process_subtitles(raw_subtitle_segments: list, pause_gap_threshold: float = 1.0, max_segment_duration: float = 12.0) -> list:
    """
    Enhanced post-process subtitle segments with both combining and splitting logic.

    This function:
    1. First combines short fragments into complete sentences
    2. Then splits sentences at punctuation boundaries for proper learning units
    3. Finally splits any overly long segments into manageable chunks
    4. Ensures optimal segment length for language learning (2-15 seconds)

    Args:
        raw_subtitle_segments: List of subtitle entries with 'text', 'start', 'duration' fields
        pause_gap_threshold: Threshold in seconds for detecting pause gaps (default: 1.0s)
        max_segment_duration: Maximum duration before splitting (default: 15.0s)

    Returns:
        List of processed subtitle segments optimized for language learning
    """
    if not raw_subtitle_segments:
        return []

    print(f"Starting post-processing: {len(raw_subtitle_segments)} raw segments")

    # STEP 1: First combine short fragments into complete sentences
    print(f"STEP 1: Combining fragments into sentences")

    combined_segments = []
    buffer = []  # Buffer to hold segments while building a sentence

    for i, segment in enumerate(raw_subtitle_segments):
        text = segment.get('text', '').strip()
        start = float(segment.get('start', 0))
        duration = float(segment.get('duration', 0))

        # Add current segment to buffer
        buffer.append(segment)

        # Check for sentence ending punctuation (at end OR mid-text followed by capital letter)
        has_punctuation_end = bool(re.search(r'[.!?]$', text.strip()))
        has_punctuation_mid = bool(re.search(r'[.!?,]\s+[A-Z]', text.strip()))
        has_punctuation = has_punctuation_end or has_punctuation_mid

        # Check for natural sentence breaks (expanded for no-punctuation scenarios)
        natural_break_patterns = [
            r'\b(thank you|thanks|bye|goodbye|okay|alright|well|so|see you|take care|good night|good morning|good afternoon|good evening|cheers|peace|later|ciao|adios|farewell)\s*$',
            r'\b(now|then|next|first|second|third|finally|also|however|meanwhile|therefore|afterwards|before|eventually|ultimately|subsequently|additionally|furthermore|moreover|besides|incidentally|regardless)\s*$',
            r'\b(and|but|or|because|since|while|when|where|how|why|although|though|unless|until|if|as|as soon as|as long as|even though|even if|whereas|provided|supposing)\s*$',
            r'\b(let me|let\'s|I want to|we need to|you should|we can|I will|I\'d like to|I\'m going to|we\'re about to|you might want to|it\'s time to|don\'t forget to|remember to|make sure to|be sure to|try to|consider)\s*$',
            r'\b(of course|by the way|in fact|for example|such as|for instance|to illustrate|notably|especially|particularly|specifically|namely|including|among others|as a matter of fact|as an example)\s*$',
            r'\b(anyway|anyhow|regardless|nonetheless|nevertheless|still|yet|even so|in any case|in conclusion|to sum up|to summarize|in short|in brief|in summary|overall|all in all|finally|lastly|ultimately)\s*$'
        ]
        has_natural_break = any(bool(re.search(pattern, text.strip(), re.IGNORECASE)) for pattern in natural_break_patterns)

        # Check for pause gap (compare with next segment if it exists)
        has_pause_gap = False
        if i < len(raw_subtitle_segments) - 1:
            next_segment = raw_subtitle_segments[i + 1]
            next_start = float(next_segment.get('start', 0))
            current_end = start + duration
            gap = next_start - current_end
            has_pause_gap = gap > pause_gap_threshold

        # Check for buffer limits: segments, duration, and word count
        buffer_too_long_segments = len(buffer) >= 3  # Reduced from 8 to 6 for better splits

        # Calculate current buffer stats
        if buffer:
            buffer_duration = (start + duration) - float(buffer[0].get('start', 0))
            buffer_too_long_time = buffer_duration > 6.0  # Further reduced to 6s for better splits

            # Check word count - important for no-punctuation scenarios
            combined_text = " ".join([seg.get('text', '').strip() for seg in buffer]).strip()
            word_count = len(combined_text.split())
            buffer_too_long_words = word_count >= 12  # Max 12 words per segment for better learning
        else:
            buffer_too_long_time = False
            buffer_too_long_words = False

        # Decide whether to end current sentence (updated with new limits)
        should_end = (has_punctuation or has_natural_break or has_pause_gap or
                     buffer_too_long_segments or buffer_too_long_time or buffer_too_long_words or
                     i == len(raw_subtitle_segments) - 1)

        if should_end and buffer:
            # Combine all texts in buffer
            combined_text = " ".join([seg.get('text', '').strip() for seg in buffer]).strip()

            # Calculate timing: start of first segment to end of last segment
            first_segment = buffer[0]
            last_segment = buffer[-1]

            combined_start = float(first_segment.get('start', 0))
            last_start = float(last_segment.get('start', 0))
            last_duration = float(last_segment.get('duration', 0))
            combined_end = last_start + last_duration
            combined_duration = combined_end - combined_start

            # Create combined segment
            combined_segment = {
                'text': combined_text,
                'start': combined_start,
                'duration': combined_duration,
                'end': combined_end,
                'original_segments': len(buffer),
                'sentence_complete': has_punctuation or has_natural_break,
                'break_reason': ('punctuation' if has_punctuation else
                               'natural_break' if has_natural_break else
                               'pause_gap' if has_pause_gap else
                               'segment_limit' if buffer_too_long_segments else
                               'duration_limit' if buffer_too_long_time else
                               'word_limit' if buffer_too_long_words else 'end_of_transcript')
            }

            combined_segments.append(combined_segment)
            buffer = []  # Clear buffer for next sentence

    print(f"STEP 1 complete: {len(raw_subtitle_segments)} raw -> {len(combined_segments)} combined segments")

    # STEP 2: Split combined segments by sentence punctuation
    print(f"STEP 2: Splitting sentences at punctuation boundaries")
    sentence_split_segments = []
    for segment in combined_segments:
        split_parts = split_by_sentence_punctuation(segment)
        sentence_split_segments.extend(split_parts)

    print(f"STEP 2 complete: {len(combined_segments)} combined -> {len(sentence_split_segments)} sentence-split segments")

    # STEP 3: Merge single-word segments with next segment (single words lack context)
    print(f"STEP 3: Merging single-word segments for better context")
    context_merged_segments = []
    i = 0
    while i < len(sentence_split_segments):
        current_segment = sentence_split_segments[i]
        current_text = current_segment.get('text', '').strip()
        word_count = len(current_text.split())

        # If current segment has only 1 word and there's a next segment, merge them
        if word_count <= 1 and i < len(sentence_split_segments) - 1:
            next_segment = sentence_split_segments[i + 1]

            # Merge current single word with next segment
            merged_text = f"{current_text} {next_segment.get('text', '').strip()}".strip()

            # Calculate combined timing
            current_start = current_segment.get('start', 0)
            current_duration = current_segment.get('duration', 0)
            next_start = next_segment.get('start', 0)
            next_duration = next_segment.get('duration', 0)

            # Combined segment spans from start of current to end of next
            combined_end = next_start + next_duration
            combined_duration = combined_end - current_start

            merged_segment = {
                'text': merged_text,
                'start': current_start,
                'duration': combined_duration,
                'end': combined_end,
                'original_segments': current_segment.get('original_segments', 1) + next_segment.get('original_segments', 1),
                'sentence_complete': next_segment.get('sentence_complete', False),
                'break_reason': f"single_word_merged_with_{next_segment.get('break_reason', 'unknown')}",
                'merge_info': 'single_word_merged_with_next'
            }

            context_merged_segments.append(merged_segment)
            print(f"Merged single word '{current_text}' with next segment -> '{merged_text[:50]}...'")
            i += 2  # Skip both current and next segment
        else:
            # Keep segment as-is
            context_merged_segments.append(current_segment)
            i += 1

    print(f"STEP 3 complete: {len(sentence_split_segments)} segments -> {len(context_merged_segments)} context-merged segments")

    # STEP 4: Split overly long segments into manageable chunks
    print(f"STEP 4: Splitting overly long segments")
    final_segments = []
    for segment in context_merged_segments:
        duration = float(segment.get('duration', 0))
        if duration > max_segment_duration:
            print(f"🔪 Splitting long segment: {duration:.1f}s -> multiple chunks")
            split_parts = split_long_segment(segment, max_duration=7.0)
            final_segments.extend(split_parts)
        else:
            final_segments.append(segment)

    # STEP 5: Final pass - merge any single-word segments created by long segment splitting
    print(f"STEP 5: Final merge of single-word segments created during splitting")
    final_merged_segments = []
    i = 0
    while i < len(final_segments):
        current_segment = final_segments[i]
        current_text = current_segment.get('text', '').strip()
        word_count = len(current_text.split())

        # If current segment has only 1 word and there's a next segment, merge them
        if word_count <= 1 and i < len(final_segments) - 1:
            next_segment = final_segments[i + 1]

            # Merge current single word with next segment
            merged_text = f"{current_text} {next_segment.get('text', '').strip()}".strip()

            # Calculate combined timing
            current_start = current_segment.get('start', 0)
            current_duration = current_segment.get('duration', 0)
            next_start = next_segment.get('start', 0)
            next_duration = next_segment.get('duration', 0)

            # Combined segment spans from start of current to end of next
            combined_end = next_start + next_duration
            combined_duration = combined_end - current_start

            merged_segment = {
                'text': merged_text,
                'start': current_start,
                'duration': combined_duration,
                'end': combined_end,
                'original_segments': current_segment.get('original_segments', 1) + next_segment.get('original_segments', 1),
                'sentence_complete': next_segment.get('sentence_complete', False),
                'break_reason': f"single_word_merged_with_{next_segment.get('break_reason', 'unknown')}",
                'merge_info': 'single_word_merged_with_next_final_pass'
            }

            final_merged_segments.append(merged_segment)
            print(f"Final merge: '{current_text}' + next -> '{merged_text[:50]}...'")
            i += 2  # Skip both current and next segment
        else:
            # Keep segment as-is
            final_merged_segments.append(current_segment)
            i += 1

    print(f"STEP 5 complete: {len(final_segments)} segments -> {len(final_merged_segments)} final-merged segments")
    print(f"Post-processing complete: {len(raw_subtitle_segments)} raw -> {len(final_merged_segments)} final segments")
    return final_merged_segments

def save_processed_subtitles(video_id: str, processed_segments: list, raw_segments: list, vocabulary: list = None, grammar: list = None):
    """
    Save processed subtitles with ALL UI display information to _proc file.

    Args:
        video_id: YouTube video ID
        processed_segments: Post-processed subtitle segments
        raw_segments: Original raw subtitle segments
        vocabulary: Extracted vocabulary with timestamps
        grammar: Extracted grammar concepts with timestamps
    """
    try:
        script_dir = Path(__file__).parent
        cache_dir = script_dir / "cache" / "subtitles"
        cache_dir.mkdir(parents=True, exist_ok=True)

        # Create processed subtitle file with _proc suffix
        proc_file = cache_dir / f"{video_id}_proc.json"

        # Enhanced processed segments with all UI information
        ui_segments = []
        for i, segment in enumerate(processed_segments):
            ui_segment = {
                "index": i,
                "text": segment.get('text', ''),
                "start": segment.get('start', 0),
                "duration": segment.get('duration', 0),
                "end": segment.get('end', segment.get('start', 0) + segment.get('duration', 0)),
                "original_segments": segment.get('original_segments', 1),
                "sentence_complete": segment.get('sentence_complete', False),
                "break_reason": segment.get('break_reason', 'unknown'),
                "word_count": len(segment.get('text', '').split()),
                "readability_score": "A2"  # Default readability level
            }
            ui_segments.append(ui_segment)

        # Comprehensive data for UI display
        subtitle_data = {
            "video_id": video_id,
            "processing_timestamp": time.time(),
            "type": "ui_ready_processed_data",
            "source": "youtube_transcript_api_processed",

            # Statistics
            "statistics": {
                "raw_segments_count": len(raw_segments),
                "processed_segments_count": len(processed_segments),
                "compression_ratio": f"{len(raw_segments)}/{len(processed_segments)} = {len(raw_segments)/len(processed_segments):.2f}x",
                "total_duration": max([seg.get('end', 0) for seg in processed_segments], default=0),
                "average_segment_duration": sum([seg.get('duration', 0) for seg in processed_segments]) / len(processed_segments) if processed_segments else 0,
                "vocabulary_count": len(vocabulary) if vocabulary else 0,
                "grammar_count": len(grammar) if grammar else 0
            },

            # UI-ready processed segments with complete information
            "ui_segments": ui_segments,

            # Learning content
            "vocabulary": vocabulary or [],
            "grammar": grammar or [],

            # Raw segments sample for debugging (first 20 only to save space)
            "raw_segments_sample": raw_segments[:20]
        }

        # Save to JSON file
        with open(proc_file, 'w', encoding='utf-8') as f:
            json.dump(subtitle_data, f, indent=2, ensure_ascii=False)

        print(f"Saved UI-ready processed data to: {proc_file}")
        print(f"Statistics: {len(raw_segments)} raw -> {len(processed_segments)} processed segments")
        print(f"UI data: {len(vocabulary or [])} vocabulary + {len(grammar or [])} grammar concepts")

    except Exception as e:
        print(f"Failed to save processed subtitles: {e}")
        # Don't raise - this is just for debugging, shouldn't break the main flow

def save_raw_subtitles(video_id: str, raw_segments: list):
    """
    Save complete raw subtitles to a separate file (without _proc suffix) for full backup.

    Args:
        video_id: YouTube video ID
        raw_segments: Original raw subtitle segments from YouTube API
    """
    print(f"🚨 SAVE_RAW_SUBTITLES: Starting save for {video_id} with {len(raw_segments)} segments")
    try:
        script_dir = Path(__file__).parent
        cache_dir = script_dir / "cache" / "subtitles"
        cache_dir.mkdir(parents=True, exist_ok=True)

        # Create raw subtitle file without any suffix
        raw_file = cache_dir / f"{video_id}.json"

        # Prepare data for saving (compatible with get_cached_subtitles format)
        raw_data = {
            "video_id": video_id,
            "cached_at": time.time(),
            "subtitles": raw_segments,
            "source": "youtube_transcript_api_raw",
            "segments": raw_segments  # Save ALL raw segments
        }

        # Save to JSON file
        with open(raw_file, 'w', encoding='utf-8') as f:
            json.dump(raw_data, f, indent=2, ensure_ascii=False)

        print(f"Saved complete raw subtitles to: {raw_file}")
        print(f"Raw segments saved: {len(raw_segments)} segments")

    except Exception as e:
        print(f"Failed to save raw subtitles: {e}")
        # Don't raise - this is just for backup, shouldn't break the main flow

def find_sentence_boundaries_for_words(transcript: list, words: list) -> dict:
    """Find the start and end of sentences containing vocabulary words for loop playback

    Args:
        transcript: List of subtitle entries
        words: List of words to find sentence boundaries for

    Returns:
        Dictionary mapping words to their sentence timing data
    """
    word_sentence_data = {}

    # Group transcript entries into sentences
    sentences = []
    current_sentence = []
    current_start = None

    for entry in transcript:
        text = entry['text'].strip()
        if not text or text == '[Music]':
            continue

        if current_start is None:
            current_start = entry['start']

        current_sentence.append({
            'text': text,
            'start': entry['start'],
            'duration': entry.get('duration', 0)
        })

        # End sentence on punctuation or significant pause
        if (text.endswith('.') or text.endswith('!') or text.endswith('?') or
            len(current_sentence) >= 3):  # Limit sentence length for subtitle context

            # Calculate sentence end time
            last_entry = current_sentence[-1]
            sentence_end = last_entry['start'] + last_entry.get('duration', 2.0)

            sentences.append({
                'entries': current_sentence,
                'start': current_start,
                'end': sentence_end,
                'full_text': ' '.join([e['text'] for e in current_sentence])
            })
            current_sentence = []
            current_start = None

    # Handle remaining sentence
    if current_sentence and current_start is not None:
        last_entry = current_sentence[-1]
        sentence_end = last_entry['start'] + last_entry.get('duration', 2.0)

        sentences.append({
            'entries': current_sentence,
            'start': current_start,
            'end': sentence_end,
            'full_text': ' '.join([e['text'] for e in current_sentence])
        })

    # Find words in sentences and map to sentence timing data
    for sentence in sentences:
        sentence_text = sentence['full_text'].lower()

        for word in words:
            if word.lower() in sentence_text and word not in word_sentence_data:
                word_sentence_data[word] = {
                    'start': max(0, int(sentence['start'])),
                    'end': int(sentence['end']),
                    'duration': int(sentence['end'] - sentence['start']),
                    'sentence_text': sentence['full_text']
                }

    return word_sentence_data

def ends_with_sentence_boundary(text: str) -> bool:
    """Check if text ends with sentence punctuation"""
    return bool(re.search(r'[.!?]\s*$', text.strip()))

def find_chunk_with_timestamp(transcript: list, timestamp: float) -> int:
    """Find which subtitle chunk contains the target timestamp"""
    for i, chunk in enumerate(transcript):
        chunk_start = chunk['start']
        chunk_end = chunk_start + chunk.get('duration', 0)
        if chunk_start <= timestamp <= chunk_end:
            return i
    return -1

def find_sentence_start(transcript: list, target_word_timestamp: float) -> float:
    """Find the actual start of the sentence containing the target word"""
    current_chunk_index = find_chunk_with_timestamp(transcript, target_word_timestamp)

    if current_chunk_index == -1:
        return target_word_timestamp

    # Start from the chunk containing the word
    sentence_start_time = transcript[current_chunk_index]['start']

    # Look backward through overlapping chunks
    for i in range(current_chunk_index - 1, -1, -1):
        prev_chunk = transcript[i]
        current_chunk = transcript[i + 1]

        prev_end = prev_chunk['start'] + prev_chunk.get('duration', 0)
        current_start = current_chunk['start']

        # If chunks overlap, the sentence likely continues backward
        if prev_end > current_start:
            # Check if previous chunk ends with sentence boundary
            if not ends_with_sentence_boundary(prev_chunk['text']):
                sentence_start_time = prev_chunk['start']
                continue
        break

    return sentence_start_time

def find_sentence_end(transcript: list, target_word_timestamp: float) -> float:
    """Find the actual end of the sentence containing the target word"""
    current_chunk_index = find_chunk_with_timestamp(transcript, target_word_timestamp)

    if current_chunk_index == -1:
        return target_word_timestamp + 3.0  # Default 3 second fallback

    # Look forward through overlapping chunks
    sentence_end_time = transcript[current_chunk_index]['start'] + transcript[current_chunk_index].get('duration', 0)

    for i in range(current_chunk_index, len(transcript)):
        current_chunk = transcript[i]

        # If chunk ends with punctuation, this is sentence end
        if ends_with_sentence_boundary(current_chunk['text']):
            sentence_end_time = current_chunk['start'] + current_chunk.get('duration', 0)
            break

        # If next chunk doesn't overlap, assume sentence ends here
        if i + 1 < len(transcript):
            next_chunk = transcript[i + 1]
            current_end = current_chunk['start'] + current_chunk.get('duration', 0)
            next_start = next_chunk['start']

            if current_end <= next_start:
                sentence_end_time = current_end
                break
        else:
            # Last chunk, use its end time
            sentence_end_time = current_chunk['start'] + current_chunk.get('duration', 0)

    return sentence_end_time

def find_word_in_transcript(transcript: list, word: str) -> float:
    """Find the first occurrence of a word in the transcript and return its timestamp"""
    for entry in transcript:
        text = entry['text'].lower()
        if word.lower() in text:
            return entry['start']
    return None

def get_sentence_containing_word(transcript: list, word: str, timestamp: float) -> tuple:
    """Get the complete sentence containing the word by first finding where the word actually appears
    Returns: (sentence_text, start_time, end_time)"""

    # First, find the transcript chunk that actually contains the word
    word_chunk_index = None
    word_lower = word.lower()

    for i, chunk in enumerate(transcript):
        chunk_text = chunk['text'].lower()
        if word_lower in chunk_text:
            word_chunk_index = i
            break

    # If word not found in any chunk, fallback to timestamp-based approach
    if word_chunk_index is None:
        for i, chunk in enumerate(transcript):
            chunk_start = chunk['start']
            chunk_end = chunk_start + chunk.get('duration', 3.0)
            if chunk_start <= timestamp <= chunk_end:
                word_chunk_index = i
                break

    if word_chunk_index is None:
        return (f"Context sentence containing '{word}'", timestamp, timestamp + 5)

    # Start building the sentence from the word-containing chunk
    sentence_parts = []
    chunk_indices = []

    # Look backwards to find the start of the sentence
    start_index = word_chunk_index
    for i in range(word_chunk_index, -1, -1):
        chunk_text = transcript[i]['text'].strip()
        sentence_parts.insert(0, chunk_text)
        chunk_indices.insert(0, i)

        # Check if this chunk ends with sentence-ending punctuation
        if i < word_chunk_index and re.search(r'[.!?]\s*$', chunk_text):
            start_index = i + 1
            sentence_parts = sentence_parts[1:]  # Remove the chunk that ended the previous sentence
            chunk_indices = chunk_indices[1:]
            break

        # Don't go too far back (max 5 chunks)
        if word_chunk_index - i >= 5:
            start_index = i
            break

    # Look forwards to find the end of the sentence
    end_index = word_chunk_index
    for i in range(word_chunk_index + 1, len(transcript)):
        chunk_text = transcript[i]['text'].strip()
        sentence_parts.append(chunk_text)
        chunk_indices.append(i)

        # Check if this chunk ends with sentence-ending punctuation
        if re.search(r'[.!?]\s*$', chunk_text):
            end_index = i
            break

        # Don't go too far forward (max 5 chunks from target)
        if i - word_chunk_index >= 5:
            end_index = i
            break

    # Calculate sentence start and end times
    sentence_start_time = transcript[chunk_indices[0]]['start'] if chunk_indices else timestamp
    sentence_end_time = transcript[chunk_indices[-1]]['start'] + transcript[chunk_indices[-1]].get('duration', 3.0) if chunk_indices else timestamp + 5

    # Join all parts to form complete sentence
    sentence = ' '.join(sentence_parts).strip()

    # Clean up the sentence
    sentence = re.sub(r'\s+', ' ', sentence)  # Multiple spaces to single space
    sentence = sentence.replace('\n', ' ')    # Remove newlines

    # Ensure sentence ends with punctuation if it doesn't already
    if sentence and not re.search(r'[.!?]\s*$', sentence):
        sentence += '.'

    # Verify the word is actually in the sentence
    if word_lower not in sentence.lower():
        return (f"Context sentence containing '{word}' (word not found in transcript)", sentence_start_time, sentence_end_time)

    return (sentence if sentence else f"Context sentence containing '{word}'", sentence_start_time, sentence_end_time)

def find_word_timestamps_smart(transcript: list, words: list) -> dict:
    """Find word timestamps with smart position detection for better UX"""
    word_data = {}

    for word in words:
        word_lower = word.lower()

        # Find the first transcript entry containing this word
        for entry in transcript:
            text = entry['text'].lower()
            if word_lower in text:
                timing_data = get_smart_timing(text, word_lower, entry)
                word_data[word] = timing_data
                break

        # If word not found in transcript, use fallback
        if word not in word_data:
            fallback_time = random.randint(10, 200)
            word_data[word] = {
                'timestamp': fallback_time,
                'end_time': fallback_time + 5,
                'word_timestamp': fallback_time,
                'sentence_duration': 5,
                'playback_mode': 'fallback',
                'position_type': 'fallback'
            }

    return word_data

def get_smart_timing(text: str, word: str, entry: dict) -> dict:
    """Adjust timing based on word position in subtitle chunk for optimal listening experience"""
    import re

    # Clean and split text into words
    words_in_chunk = re.findall(r'\b\w+\b', text.lower())

    try:
        word_position = words_in_chunk.index(word.lower())
        total_words = len(words_in_chunk)
        position_ratio = word_position / max(1, total_words - 1) if total_words > 1 else 0.5

        start_time = entry['start']
        duration = entry.get('duration', 3)
        original_end = start_time + duration

        # Check if this is a no-punctuation scenario (no sentence endings)
        has_punctuation = bool(re.search(r'[.!?]', text))

        if not has_punctuation:
            # No-punctuation scenario: Apply 2-second slide adjustments
            if position_ratio <= 0.25:  # Word at beginning (first 25%)
                # Slide 2 seconds before the word start for better context
                buffered_start = max(0, start_time - 2.0)
                buffered_end = original_end + 0.5
                position_type = 'beginning_no_punct'

            elif position_ratio >= 0.75:  # Word at end (last 25%)
                # Slide to include 2 seconds after the word for completion
                buffered_start = max(0, start_time - 0.5)
                buffered_end = original_end + 2.0
                position_type = 'end_no_punct'

            else:  # Word in middle
                # Balanced approach for middle words in no-punctuation
                buffered_start = max(0, start_time - 1.0)
                buffered_end = original_end + 1.0
                position_type = 'middle_no_punct'
        else:
            # Original punctuation-based smart buffering
            if position_ratio <= 0.25:  # Word at beginning (first 25%)
                # Add 1.5 second buffer before for preparation
                buffered_start = max(0, start_time - 1.5)
                buffered_end = original_end + 0.5  # Small buffer after
                position_type = 'beginning'

            elif position_ratio >= 0.75:  # Word at end (last 25%)
                # Add 0.5 second buffer before, 1.5 seconds after for processing
                buffered_start = max(0, start_time - 0.5)
                buffered_end = original_end + 1.5
                position_type = 'end'

            else:  # Word in middle
                # Balanced buffering
                buffered_start = max(0, start_time - 0.5)
                buffered_end = original_end + 0.5
                position_type = 'middle'

        return {
            'timestamp': int(buffered_start),
            'end_time': int(buffered_end),
            'word_timestamp': int(start_time),  # When word actually starts
            'sentence_duration': int(buffered_end - buffered_start),
            'playback_mode': 'smart_buffered_with_punct_detection',
            'position_type': position_type,
            'position_ratio': round(position_ratio, 2),
            'has_punctuation': has_punctuation
        }

    except (ValueError, ZeroDivisionError):
        # Word not found in expected format or other error, use simple buffering
        start_time = entry['start']
        duration = entry.get('duration', 3)
        buffered_start = max(0, start_time - 0.5)
        buffered_end = start_time + duration + 0.5

        return {
            'timestamp': int(buffered_start),
            'end_time': int(buffered_end),
            'word_timestamp': int(start_time),
            'sentence_duration': int(buffered_end - buffered_start),
            'playback_mode': 'simple_buffered',
            'position_type': 'unknown'
        }

def find_word_timestamps_with_sentences(transcript: list, words: list) -> dict:
    """Enhanced version that returns sentence boundaries for each word"""
    word_data = {}

    for word in words:
        # Find where word appears in transcript
        word_timestamp = find_word_in_transcript(transcript, word)

        if word_timestamp is not None:
            sentence_start = find_sentence_start(transcript, word_timestamp)
            sentence_end = find_sentence_end(transcript, word_timestamp)

            word_data[word] = {
                'word_timestamp': int(word_timestamp),
                'sentence_start': int(sentence_start),
                'sentence_end': int(sentence_end),
                'sentence_duration': int(sentence_end - sentence_start)
            }

    return word_data

def find_word_timestamps(transcript: list, words: list, preparation_buffer: float = 2.0) -> dict:
    """Find learner-friendly timestamps for words with preparation time buffer

    Args:
        transcript: List of subtitle entries
        words: List of words to find timestamps for
        preparation_buffer: Seconds before word starts (default 2.0 for pronunciation prep)
    """
    word_timestamps = {}

    for entry in transcript:
        text = entry['text'].lower()
        actual_start_time = entry['start']  # When word actually starts

        # Calculate learner-friendly timestamp (earlier for preparation)
        learner_timestamp = max(0, actual_start_time - preparation_buffer)

        for word in words:
            if word.lower() in text and word not in word_timestamps:
                word_timestamps[word] = int(learner_timestamp)

    return word_timestamps

def adaptive_vocabulary_selection(vocabulary: list, user_level: str = "A2", max_words: int = 8) -> list:
    """Select vocabulary adaptively, prioritizing words at/below user level, with some challenging words"""

    # Define level progression for adaptive selection
    level_map = {'A1': 0, 'A2': 1, 'B1': 2, 'B2': 3, 'C1': 4, 'C2': 5}
    levels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']

    user_index = level_map.get(user_level.upper(), 1)  # Default to A2

    # Group vocabulary by level
    vocab_by_level = {}
    for item in vocabulary:
        level = item['level']
        if level not in vocab_by_level:
            vocab_by_level[level] = []
        vocab_by_level[level].append(item)

    selected = []

    # Strategy: Show words at/below user level first, then add some challenging ones
    # Priority order: user level -> one level below -> one level above -> others

    priority_levels = []

    # Add user level first
    if user_level in vocab_by_level:
        priority_levels.append(user_level)

    # Add levels below user level (easier words are still valuable for reinforcement)
    for i in range(user_index - 1, -1, -1):
        if levels[i] in vocab_by_level:
            priority_levels.append(levels[i])

    # Add levels above user level (for challenge)
    for i in range(user_index + 1, len(levels)):
        if levels[i] in vocab_by_level:
            priority_levels.append(levels[i])

    # Select words in priority order
    for level in priority_levels:
        if level in vocab_by_level:
            remaining_words = [w for w in vocab_by_level[level] if w not in selected]
            # For the first few priority levels, take more words
            slots_remaining = max_words - len(selected)
            if slots_remaining <= 0:
                break

            words_to_take = min(len(remaining_words), slots_remaining)
            selected.extend(remaining_words[:words_to_take])
    return selected[:max_words]

async def extract_vocabulary_from_transcript(transcript_text: str, transcript_data: list, user_level: str = "A2", max_words: int = 8):
    """Extract key vocabulary words from transcript text with real definitions"""
    # Extract all words and count frequency
    words = re.findall(r'\b[a-zA-Z]+\b', transcript_text.lower())

    # Enhanced common words list
    common_words = {
        'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
        'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does',
        'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this',
        'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me',
        'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their',
        'a', 'an', 'if', 'so', 'up', 'out', 'now', 'how', 'who', 'what', 'when',
        'where', 'why', 'very', 'much', 'more', 'most', 'some', 'many', 'any',
        'all', 'both', 'each', 'few', 'other', 'another', 'such', 'only', 'own',
        'same', 'so', 'than', 'too', 'well', 'can', 'just', 'dont', 'wont', 'cant',
        'im', 'youre', 'hes', 'shes', 'were', 'theyre', 'ive', 'youve', 'weve',
        'theyve', 'isnt', 'arent', 'wasnt', 'werent', 'hasnt', 'havent', 'hadnt',
        'wont', 'wouldnt', 'dont', 'doesnt', 'didnt', 'shouldnt', 'couldnt', 'mightnt'
    }

    # Count word frequency and filter interesting words
    word_counter = Counter(words)
    interesting_words = []

    for word, count in word_counter.most_common():
        if (len(word) > 3 and
            word not in common_words and
            word.isalpha() and
            count >= 2):  # Word appears at least twice
            interesting_words.append(word)

    # Take first max_words
    selected_words = interesting_words[:max_words]

    # Find word timestamps with smart position detection for optimal UX
    sentence_boundaries = find_word_timestamps_smart(transcript_data, selected_words)
    print(f"DEBUG: Found smart timestamps for {len(sentence_boundaries)} words:")
    for word, data in sentence_boundaries.items():
        print(f"  - {word}: timestamp={data['timestamp']}, position={data.get('position_type', 'unknown')}, mode={data['playback_mode']}")

    # Get simple, kid-friendly definitions
    vocabulary = []
    for word in selected_words:
        level = get_word_difficulty(word)

        # Skip proper nouns and common names/places
        if level == "SKIP":
            print(f"Skipped proper noun: {word}")
            continue

        # Get enhanced word information
        enhanced_info = get_enhanced_word_info(word, level)
        definition = enhanced_info['definition']

        # Get timestamp data from simple algorithm
        timestamp_data = sentence_boundaries.get(word)

        if timestamp_data:
            # Get Chinese translation for the word
            translation = get_chinese_translation(word)

            # Get the subtitle sentence containing this word with its timing
            sentence, sentence_start_time, sentence_end_time = get_sentence_containing_word(transcript_data, word, timestamp_data['timestamp'])

            vocab_item = {
                "word": word,
                "definition": definition,
                "level": level,
                "timestamp": timestamp_data['timestamp'],
                "end_time": timestamp_data['end_time'],
                "word_timestamp": timestamp_data['word_timestamp'],
                "sentence_duration": timestamp_data['sentence_duration'],
                "context_type": "real_transcript",
                "playback_mode": timestamp_data['playback_mode'],
                "translation": translation,
                "sentence": sentence,  # Add subtitle sentence
                "sentence_start_time": sentence_start_time,  # Sentence start timestamp
                "sentence_end_time": sentence_end_time,  # Sentence end timestamp
                # Enhanced vocabulary information
                "definition_zh": enhanced_info.get('definition_zh', ''),
                "usage": enhanced_info.get('usage', ''),
                "examples": enhanced_info.get('examples', []),
                "synonyms": enhanced_info.get('synonyms', []),
                "collocations": enhanced_info.get('collocations', []),
                "pos": enhanced_info.get('pos', [])
            }
            print(f"Added {word} with timestamp {vocab_item['timestamp']}")
            vocabulary.append(vocab_item)
        else:
            # Fallback if word not found in transcript
            fallback_start = random.randint(10, 200)
            # Get Chinese translation for the word
            translation = get_chinese_translation(word)

            vocabulary.append({
                "word": word,
                "definition": definition,
                "level": level,
                "timestamp": fallback_start,
                "end_time": fallback_start + 5,
                "word_timestamp": fallback_start,
                "sentence_duration": 5,
                "context_type": "fallback",
                "playback_mode": "fallback",
                "translation": translation
            })

    # Apply adaptive vocabulary selection based on user level
    adaptive_vocab = adaptive_vocabulary_selection(vocabulary, user_level, max_words)

    # Sort vocabulary by timestamp for chronological order
    adaptive_vocab.sort(key=lambda x: x['timestamp'])

    return adaptive_vocab

def extract_grammar_from_transcript(transcript_text: str) -> list:
    """Extract grammar concepts from transcript with pattern matching"""
    grammar_concepts = []
    text_lower = transcript_text.lower()

    # Grammar patterns and their detection logic
    grammar_patterns = [
        {
            "pattern": r"\b(is|are|was|were|am)\b",
            "concept": "Present/Past Simple (to be)",
            "explanation": "The verb 'to be' used to describe states, locations, and identities",
            "level": "A1",
            "example_words": ["is", "are", "was", "were", "am"]
        },
        {
            "pattern": r"\b(have|has|had)\s+\w+ed\b|\b(have|has|had)\s+(been|done|gone|seen)\b",
            "concept": "Present/Past Perfect",
            "explanation": "Used to talk about completed actions with relevance to the present or past",
            "level": "B1",
            "example_words": ["have been", "has done", "had gone"]
        },
        {
            "pattern": r"\b(will|shall)\s+\w+\b|\bgoing to\s+\w+\b",
            "concept": "Future Tense",
            "explanation": "Used to express future actions, plans, and predictions",
            "level": "A2",
            "example_words": ["will", "going to", "shall"]
        },
        {
            "pattern": r"\b\w+ing\b.*\b(now|currently|right now)\b|\b(am|is|are)\s+\w+ing\b",
            "concept": "Present Continuous",
            "explanation": "Used to describe actions happening now or around now",
            "level": "A1",
            "example_words": ["am doing", "is playing", "are watching"]
        },
        {
            "pattern": r"\b\w+ed\b.*\b(yesterday|ago|last)\b|\b(was|were)\s+\w+ing\b",
            "concept": "Past Tense",
            "explanation": "Used to talk about completed actions in the past",
            "level": "A1",
            "example_words": ["played", "was running", "went"]
        },
        {
            "pattern": r"\b(can|could|may|might|should|would|must|ought)\s+\w+\b",
            "concept": "Modal Verbs",
            "explanation": "Used to express ability, possibility, permission, and obligation",
            "level": "A2",
            "example_words": ["can do", "should go", "might be"]
        },
        {
            "pattern": r"\b(a|an)\s+\w+\b|\bthe\s+\w+\b",
            "concept": "Articles (a, an, the)",
            "explanation": "Words used before nouns to specify or generalize",
            "level": "A1",
            "example_words": ["a book", "an apple", "the house"]
        },
        {
            "pattern": r"\bif\s+.*,\s+.*\b|\bwhen\s+.*,\s+.*\b|\bbecause\s+.*\b",
            "concept": "Conditional Sentences",
            "explanation": "Used to express conditions, causes, and results",
            "level": "B1",
            "example_words": ["if you go", "when it rains", "because of"]
        },
        {
            "pattern": r"\b(more|most)\s+\w+\b|\b\w+er\s+(than)\b|\b\w+est\b",
            "concept": "Comparatives and Superlatives",
            "explanation": "Used to compare things and show the highest degree",
            "level": "A2",
            "example_words": ["bigger than", "most beautiful", "fastest"]
        },
        {
            "pattern": r"\b(don't|doesn't|didn't|won't|can't|isn't|aren't)\b",
            "concept": "Negative Forms",
            "explanation": "Used to make sentences negative using contractions",
            "level": "A1",
            "example_words": ["don't know", "isn't here", "can't go"]
        }
    ]

    # Check each pattern
    for pattern_info in grammar_patterns:
        import re
        matches = re.findall(pattern_info["pattern"], text_lower)
        if matches:
            # Create example from first match if possible
            example = matches[0] if isinstance(matches[0], str) else " ".join(matches[0])

            grammar_concepts.append({
                "concept": pattern_info["concept"],
                "explanation": pattern_info["explanation"],
                "level": pattern_info["level"],
                "example": example[:50] + "..." if len(example) > 50 else example,
                "timestamp": random.randint(15, 200)
            })

    # Remove duplicates and limit to 4 concepts
    seen_concepts = set()
    unique_concepts = []
    for concept in grammar_concepts:
        if concept["concept"] not in seen_concepts:
            seen_concepts.add(concept["concept"])
            unique_concepts.append(concept)

    # Sort grammar by timestamp for chronological order
    unique_concepts.sort(key=lambda x: x['timestamp'])

    return unique_concepts[:4]

@app.get("/")
async def root():
    return {"message": "Language Learning API is running"}

@app.post("/api/extract-content")
async def extract_content(video_data: dict):
    """Extract vocabulary and grammar from YouTube video using real transcript with adaptive selection"""
    try:
        video_url = video_data.get("videoUrl", "")
        user_level = video_data.get("userLevel", "A2")  # Default to A2 if not provided
        video_id = extract_video_id(video_url)

        if not video_id:
            raise HTTPException(status_code=400, detail="Invalid YouTube URL")

        # Try to get transcript using cache first, then multiple methods
        raw_segments = None
        transcript_source = ""

        # Check cache first for RAW segments
        cached_raw_segments = get_cached_subtitles(video_id)
        if cached_raw_segments:
            raw_segments = cached_raw_segments
            transcript_source = "cached_raw_subtitles"
            print(f"Using cached RAW subtitles for {video_id} ({len(raw_segments)} raw segments)")
        else:
            # Method 1: YouTube Transcript API (CORRECTED syntax for system Python3)
            try:
                print("🔍 Attempting CORRECTED YouTube Transcript API...")
                api = YouTubeTranscriptApi()
                raw_transcript = api.fetch(video_id)

                # Convert to expected format
                raw_segments = []
                for entry in raw_transcript:
                    raw_segments.append({
                        'text': entry.text,
                        'start': entry.start,
                        'duration': getattr(entry, 'duration', 0)
                    })

                transcript_source = "youtube_transcript_api_CORRECTED_RAW"
                print(f"🎉 SUCCESS: Extracted {len(raw_segments)} RAW entries using CORRECTED YouTube Transcript API")

                # Save raw subtitles immediately after successful extraction
                print(f"🚨 DEBUG: About to save raw subtitles for {video_id}, segments count: {len(raw_segments)}")
                save_raw_subtitles(video_id, raw_segments)
                print(f"🚨 DEBUG: Raw subtitles save completed for {video_id}")

            except Exception as transcript_error:
                print(f"YouTube Transcript API failed: {transcript_error}")

                # Method 2: yt-dlp fallback (if available)
                if not raw_segments and YT_DLP_AVAILABLE:
                    try:
                        print("Attempting yt-dlp subtitle extraction...")
                        raw_segments = extract_subtitles_with_ytdlp(video_url)
                        transcript_source = "yt_dlp_raw"
                        print(f"Successfully extracted {len(raw_segments)} RAW entries using yt-dlp")

                        # Save raw subtitles immediately after successful extraction
                        save_raw_subtitles(video_id, raw_segments)

                    except Exception as ytdlp_error:
                        print(f"yt-dlp subtitle extraction failed: {ytdlp_error}")
                else:
                    print("yt-dlp not available, skipping alternative extraction method")

        # Apply post-processing dynamically if we have raw segments
        transcript = None
        if raw_segments and len(raw_segments) > 0:
            # Apply post-processing to create better sentence boundaries
            transcript = post_process_subtitles(raw_segments, pause_gap_threshold=1.0)
            print(f"Applied dynamic post-processing: {len(raw_segments)} raw segments -> {len(transcript)} processed sentences")

        # Process transcript if we got one
        if transcript and len(transcript) > 0:
            transcript_text = " ".join([entry['text'] for entry in transcript])

            # Extract vocabulary and grammar from real transcript with adaptive selection
            vocabulary = await extract_vocabulary_from_transcript(transcript_text, transcript, user_level)
            grammar = extract_grammar_from_transcript(transcript_text)

            # Save processed subtitles with ALL UI information including vocabulary and grammar
            save_processed_subtitles(video_id, transcript, raw_segments, vocabulary, grammar)

            # Add first 100 subtitles for debugging as requested - now showing post-processed sentences
            subtitle_debug = []
            for i, entry in enumerate(transcript[:100]):
                subtitle_debug.append({
                    "index": i,
                    "text": entry.get('text', ''),
                    "start": entry.get('start', 0),
                    "duration": entry.get('duration', 0),
                    "end": entry.get('end', 0),
                    "original_segments": entry.get('original_segments', 1),  # How many raw segments combined
                    "sentence_complete": entry.get('sentence_complete', False)  # Ends with punctuation
                })

            return JSONResponse({
                "vocabulary": vocabulary,
                "grammar": grammar,
                "transcript_length": len(transcript_text),
                "source": f"real_transcript_{transcript_source}",
                "user_level": user_level,
                "adaptive_selection": True,
                "transcript_entries": len(transcript),
                "subtitle_debug": subtitle_debug,  # First 100 subtitles for debugging
                "success": True
            })

        else:
            print("All transcript extraction methods failed, using fallback mock data")
            # Fallback to mock data if all transcript extraction methods fail
            return JSONResponse({
                "vocabulary": [
                    {"word": "hello", "definition": "a greeting", "level": "A1", "timestamp": 15},
                    {"word": "world", "definition": "the earth", "level": "A1", "timestamp": 45},
                    {"word": "beautiful", "definition": "pleasing to the senses", "level": "A1", "timestamp": 78},
                    {"word": "language", "definition": "system of communication", "level": "A1", "timestamp": 92}
                ],
                "grammar": [
                    {"concept": "Present Simple", "explanation": "Used for facts and habits", "level": "A1", "timestamp": 30},
                    {"concept": "Articles (a, an, the)", "explanation": "Words used before nouns", "level": "A1", "timestamp": 65}
                ],
                "source": "fallback_mock",
                "error": "No subtitles available - tried both YouTube Transcript API and yt-dlp methods"
            })

    except Exception as e:
        print(f"CRITICAL ERROR in extract_content: {str(e)}")
        print("Full stack trace:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing video: {str(e)}")

# AI Teacher System
def generate_ai_teacher_response(word: str, definition: str, sentence: str, user_question: str = None) -> str:
    """Generate AI teacher response to help user learn vocabulary"""

    # Predefined AI teacher responses for common words
    ai_responses = {
        "campus": {
            "explanation": f"'{word}'是一个很实用的词！它指的是大学或学院的校园。在视频中我们听到：'{sentence[:50]}...' 这个词通常用来描述学校的整个区域。",
            "usage_tips": "记住：campus通常用作单数，复数是campuses。常见搭配有'on campus'（在校园里）、'off campus'（校园外）。",
            "memory_trick": "💡记忆小技巧：camp（营地）+ us（我们）= campus（我们学习的地方）",
            "practice": "试着造句：'I live on campus.'（我住在校园里）"
        },
        "people": {
            "explanation": f"'{word}'是一个基础但很重要的词！它表示人们、人民。在视频中：'{sentence[:50]}...' 注意people本身就是复数形式。",
            "usage_tips": "people已经是复数，不需要加s。单数用person。如：one person, two people。",
            "memory_trick": "💡记忆小技巧：people = 很多person聚在一起",
            "practice": "试着造句：'Many people like music.'（很多人喜欢音乐）"
        },
        "about": {
            "explanation": f"'{word}'是一个多功能词！它可以表示'关于'或'大约'。在视频中：'{sentence[:50]}...' 用法很灵活。",
            "usage_tips": "作介词：about something（关于某事）；作副词：about 10 minutes（大约10分钟）",
            "memory_trick": "💡记忆小技巧：a-bout = 围绕着，所以是'关于'的意思",
            "practice": "试着造句：'This book is about history.'（这本书是关于历史的）"
        },
        "from": {
            "explanation": f"'{word}'是一个基础介词！表示起点、来源。在视频中：'{sentence[:50]}...' 显示了来源关系。",
            "usage_tips": "常用搭配：come from（来自）、from...to...（从...到...）、learn from（从...学习）",
            "memory_trick": "💡记忆小技巧：想象一个箭头指向起点，这就是from的含义",
            "practice": "试着造句：'I come from China.'（我来自中国）"
        },
        "said": {
            "explanation": f"'{word}'是动词say的过去式！表示'说了'。在视频中：'{sentence[:50]}...' 描述了过去的说话动作。",
            "usage_tips": "say的过去式和过去分词都是said。常用句型：He said that...（他说...）",
            "memory_trick": "💡记忆小技巧：said的发音类似'塞得'，想象话被塞进嘴里说出来",
            "practice": "试着造句：'She said hello to me.'（她对我说你好）"
        }
    }

    # Default AI teacher response
    default_response = {
        "explanation": f"让我来帮你学习'{word}'这个词！根据定义，它的意思是：{definition}。在视频中它出现在这个句子里：'{sentence[:50]}...'",
        "usage_tips": "这个词在英语中的使用频率比较高，建议多看几个例句来理解用法。",
        "memory_trick": "💡试着在日常生活中寻找使用这个词的机会，这样能更好地记住它！",
        "practice": f"试着用'{word}'造一个你自己的句子吧！"
    }

    # Get response for the word
    response_data = ai_responses.get(word.lower(), default_response)

    # Format the AI teacher response
    ai_response = f"""🎓 AI老师来帮你学习啦！

📖 **单词解析**
{response_data['explanation']}

💭 **用法提示**
{response_data['usage_tips']}

{response_data['memory_trick']}

🎯 **练习建议**
{response_data['practice']}

❓ 还有其他问题吗？我可以帮你解释语法、造句或者记忆技巧！"""

    return ai_response

@app.post("/api/ai-teacher")
async def ai_teacher(request: dict):
    """AI Teacher endpoint to help users learn vocabulary"""
    try:
        word = request.get('word', '')
        definition = request.get('definition', '')
        sentence = request.get('sentence', '')
        user_question = request.get('question', '')

        if not word:
            raise HTTPException(status_code=400, detail="Word is required")

        ai_response = generate_ai_teacher_response(word, definition, sentence, user_question)

        return {
            "word": word,
            "ai_response": ai_response,
            "timestamp": int(time.time())
        }

    except Exception as e:
        print(f"Error in AI teacher: {e}")
        raise HTTPException(status_code=500, detail=f"AI teacher error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)