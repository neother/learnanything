from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from youtube_transcript_api import YouTubeTranscriptApi
try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    pass  # Will be logged after logger initialization
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
import logging
import sys
try:
    from googletrans import Translator
    translator = Translator()
    TRANSLATION_ENABLED = True
except ImportError:
    pass  # Will be logged after logger initialization
    translator = None
    TRANSLATION_ENABLED = False

# Configure logging to output to both console and file
def setup_logging():
    """Setup logging configuration for both console and file output."""
    # Create logs directory if it doesn't exist
    log_dir = Path(__file__).parent.parent.parent  # Go up to project root
    log_file = log_dir / "backend.log"

    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Clear any existing handlers
    logger.handlers.clear()

    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S'
    )

    # File handler with UTF-8 encoding
    file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(file_formatter)

    # Console handler with UTF-8 encoding
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Configure uvicorn logger
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.handlers = []
    uvicorn_logger.addHandler(file_handler)
    uvicorn_logger.addHandler(console_handler)

    # Configure uvicorn.access logger
    access_logger = logging.getLogger("uvicorn.access")
    access_logger.handlers = []
    access_logger.addHandler(file_handler)
    access_logger.addHandler(console_handler)

    logging.info("Logging system initialized - outputs to both console and backend.log")
    return logger

# Initialize logging
logger = setup_logging()

# Log initial import warnings
if not YT_DLP_AVAILABLE:
    logger.warning("yt-dlp not available, will use YouTube Transcript API only")
if not TRANSLATION_ENABLED:
    logger.warning("Google Translate not available, translation disabled")

app = FastAPI(title="Language Learning API", version="1.0.0")

# Initialize database on startup
from database import init_db
from routes.auth import router as auth_router
from routes.analytics import router as analytics_router
from routes.smart_sessions import router as smart_sessions_router

@app.on_event("startup")
async def startup_event():
    init_db()
    logging.info("Language Learning API started successfully")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=True,  # Enable credentials for JWT tokens
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(analytics_router)
app.include_router(smart_sessions_router)

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
            logger.error(f"Error loading translation cache: {e}")
            return {}
    return {}

# Save translation cache
def save_translation_cache(cache):
    """Save translations to cache file"""
    try:
        with open(TRANSLATION_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error saving translation cache: {e}")

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
            logger.debug(f"Using hardcoded translation '{word}' -> '{translation}'")
        except UnicodeEncodeError:
            logger.debug(f"Using hardcoded translation '{word}' -> [Chinese characters]")
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

        logger.debug(f"Translated '{word}' to '{translation}'")
        return translation

    except Exception as e:
        logger.error(f"Translation error for '{word}': {e}")
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

            logger.info(f"Using cached subtitles for {video_id} (cached {hours_since_cache:.1f}h ago)")
            return cached_data.get('subtitles', [])

        except Exception as e:
            logger.error(f"Error reading cache for {video_id}: {e}")
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

        logger.info(f"Cached PURE RAW subtitles for {video_id} ({len(raw_subtitles)} original segments)")

    except Exception as e:
        logger.error(f"Error caching subtitles for {video_id}: {e}")

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

            logger.debug(f"Available manual subtitles: {list(subtitles_data.keys())}")
            logger.debug(f"Available auto subtitles: {list(auto_subtitles_data.keys())}")

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

            logger.info(f"Using subtitle format: {best_subtitle.get('ext')}")

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

            logger.info(f"Parsed {len(transcript_entries)} subtitle entries")
            return transcript_entries

    except Exception as e:
        logger.error(f"yt-dlp subtitle extraction failed: {e}")
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
        logger.error(f"Error parsing srv3: {e}")

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
        logger.error(f"Error parsing TTML: {e}")

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
                    logger.info(f"Loaded {len(data['words'])} {level.upper()} words")
            else:
                logger.warning(f"Warning: {vocab_file} not found")
                CEFR_WORDS[level] = set()
        except Exception as e:
            logger.error(f"Error loading {vocab_file}: {e}")
            CEFR_WORDS[level] = set()

    logger.info(f"Total vocabulary loaded: {sum(len(words) for words in CEFR_WORDS.values())} words")

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
        logger.warning(f"Enhanced vocabulary file not found for level {level}")
        return {}
    except Exception as e:
        logger.error(f"Error loading enhanced vocabulary for {level}: {e}")
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

    # Look for sentence boundaries: punctuation (including comma) followed by space and letter
    sentence_breaks = list(re.finditer(r'([.!?,])\s+([A-Za-z])', text))

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

    logger.debug(f"Split sentence: '{text[:50]}...' -> {len(segments)} sentences")
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

def deduplicate_overlapping_texts(segments: list) -> list:
    """
    Remove overlapping/duplicate content from subtitle segments.
    YouTube API sometimes provides overlapping segments where later segments
    repeat parts of earlier segments.

    Args:
        segments: List of segments with 'text' field

    Returns:
        List of segments with deduplicated text
    """
    if not segments or len(segments) <= 1:
        return segments

    deduplicated = []

    for i, segment in enumerate(segments):
        current_text = segment.get('text', '').strip()

        if not current_text:
            continue

        # Check if this text is already contained in previous segments
        is_duplicate = False

        # Look at previous segments to see if current text is a subset/duplicate
        for prev_segment in deduplicated:
            prev_text = prev_segment.get('text', '').strip()

            # Skip if current text is completely contained in previous text
            if current_text in prev_text:
                is_duplicate = True
                break

            # Check if current text starts with end of previous text (overlap)
            words_current = current_text.split()
            words_prev = prev_text.split()

            if len(words_current) >= 3 and len(words_prev) >= 3:
                # Check for overlap: if first 3+ words of current match last 3+ words of previous
                for overlap_len in range(min(len(words_current), len(words_prev)), 2, -1):
                    if (words_current[:overlap_len] == words_prev[-overlap_len:]):
                        # Remove the overlapping part from current text
                        remaining_words = words_current[overlap_len:]
                        if remaining_words:  # Only keep if there's non-overlapping content
                            segment = segment.copy()
                            segment['text'] = ' '.join(remaining_words)
                            current_text = segment['text']
                        else:
                            is_duplicate = True
                        break

        if not is_duplicate and current_text.strip():
            deduplicated.append(segment)

    return deduplicated

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

    logger.info(f"Starting post-processing: {len(raw_subtitle_segments)} raw segments")

    # STEP 1: First combine short fragments into complete sentences
    logger.debug(f"STEP 1: Combining fragments into sentences")

    combined_segments = []
    buffer = []  # Buffer to hold segments while building a sentence

    # STEP 0: Remove overlapping/duplicate content first
    logger.debug(f"STEP 0: Deduplicating overlapping content")
    raw_subtitle_segments = deduplicate_overlapping_texts(raw_subtitle_segments)
    logger.debug(f"After deduplication: {len(raw_subtitle_segments)} segments")

    for i, segment in enumerate(raw_subtitle_segments):
        text = segment.get('text', '').strip()
        start = float(segment.get('start', 0))
        duration = float(segment.get('duration', 0))

        # Add current segment to buffer
        buffer.append(segment)

        # Check for sentence ending punctuation (at end OR mid-text followed by capital letter)
        has_punctuation_end = bool(re.search(r'[.!?,]$', text.strip()))
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
            buffer_too_long_time = buffer_duration > 8.0  # Further reduced to 8s for better splits

            # Check word count - important for no-punctuation scenarios
            combined_text = " ".join([seg.get('text', '').strip() for seg in buffer]).strip()
            word_count = len(combined_text.split())
            buffer_too_long_words = word_count >= 15  # Max 15 words per segment - optimal for kids learning
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
            # CRITICAL: Preserve original YouTube timing boundaries for video accuracy
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

    logger.debug(f"STEP 1 complete: {len(raw_subtitle_segments)} raw -> {len(combined_segments)} combined segments")

    # STEP 2: Split combined segments by sentence punctuation
    logger.debug(f"STEP 2: Splitting sentences at punctuation boundaries")
    sentence_split_segments = []
    for segment in combined_segments:
        split_parts = split_by_sentence_punctuation(segment)
        sentence_split_segments.extend(split_parts)

    logger.debug(f"STEP 2 complete: {len(combined_segments)} combined -> {len(sentence_split_segments)} sentence-split segments")

    # STEP 3: Recursively merge incomplete segments until complete sentences are formed
    logger.debug(f"STEP 3: Recursively merging incomplete segments for complete sentences")
    context_merged_segments = []
    i = 0
    while i < len(sentence_split_segments):
        current_segment = sentence_split_segments[i]
        current_text = current_segment.get('text', '').strip()
        word_count = len(current_text.split())

        # Check if segment is incomplete (no sentence-ending punctuation including comma)
        is_incomplete = not bool(re.search(r'[.!?,]\s*$', current_text))

        # If current segment is incomplete, keep merging with next segments until complete
        if (word_count <= 1 or is_incomplete) and i < len(sentence_split_segments) - 1:
            # Start building complete sentence
            merged_segments = [current_segment]
            merged_text = current_text
            j = i + 1

            # Keep adding segments until we find a complete sentence or run out
            while j < len(sentence_split_segments):
                next_segment = sentence_split_segments[j]
                next_text = next_segment.get('text', '').strip()
                merged_text = f"{merged_text} {next_text}".strip()
                merged_segments.append(next_segment)

                # Check if we now have a complete sentence (including comma)
                has_complete_punctuation = bool(re.search(r'[.!?,]\s*$', merged_text))
                if has_complete_punctuation:
                    break
                j += 1

            # Create merged segment from all collected segments
            # CRITICAL FIX: Preserve original timing boundaries to maintain video accuracy
            first_segment = merged_segments[0]
            last_segment = merged_segments[-1]

            # Use the actual start time from the original segments, not calculated times
            combined_start = float(first_segment.get('start', 0))
            last_start = float(last_segment.get('start', 0))
            last_duration = float(last_segment.get('duration', 0))
            combined_end = last_start + last_duration
            combined_duration = combined_end - combined_start

            # Create the final merged segment with original segment mapping for word timing
            merged_segment = {
                'text': merged_text,
                'start': combined_start,
                'duration': combined_duration,
                'end': combined_end,
                'original_segments': sum(seg.get('original_segments', 1) for seg in merged_segments),
                'sentence_complete': bool(re.search(r'[.!?,]\s*$', merged_text)),
                'break_reason': f"recursive_merge_{len(merged_segments)}_segments",
                'merge_info': f'incomplete_merged_with_{len(merged_segments)}_segments',
                # CRITICAL: Store original segment mappings for accurate word timing
                'original_segment_mapping': [
                    {
                        'text': seg.get('text', ''),
                        'start': seg.get('start', 0),
                        'end': seg.get('end', seg.get('start', 0) + seg.get('duration', 0)),
                        'duration': seg.get('duration', 0)
                    } for seg in merged_segments
                ]
            }

            context_merged_segments.append(merged_segment)
            logger.debug(f"Recursively merged {len(merged_segments)} incomplete segments -> '{merged_text[:50]}...'")
            i = j + 1  # Skip all merged segments
        else:
            # Keep segment as-is
            context_merged_segments.append(current_segment)
            i += 1

    logger.debug(f"STEP 3 complete: {len(sentence_split_segments)} segments -> {len(context_merged_segments)} context-merged segments")

    # STEP 4: Split overly long segments into manageable chunks
    logger.debug(f"STEP 4: Splitting overly long segments")
    final_segments = []
    for segment in context_merged_segments:
        duration = float(segment.get('duration', 0))
        if duration > max_segment_duration:
            logging.info(f"Splitting long segment: {duration:.1f}s -> multiple chunks")
            split_parts = split_long_segment(segment, max_duration=7.0)
            final_segments.extend(split_parts)
        else:
            final_segments.append(segment)

    # STEP 5: Final pass - merge any single-word segments created by long segment splitting
    logger.debug(f"STEP 5: Final merge of single-word segments created during splitting")
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

            # Calculate combined timing - preserve original boundaries
            current_start = float(current_segment.get('start', 0))
            current_duration = float(current_segment.get('duration', 0))
            next_start = float(next_segment.get('start', 0))
            next_duration = float(next_segment.get('duration', 0))

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
            logger.debug(f"Final merge: '{current_text}' + next -> '{merged_text[:50]}...'")
            i += 2  # Skip both current and next segment
        else:
            # Keep segment as-is
            final_merged_segments.append(current_segment)
            i += 1

    logger.debug(f"STEP 5 complete: {len(final_segments)} segments -> {len(final_merged_segments)} final-merged segments")
    logger.info(f"Post-processing complete: {len(raw_subtitle_segments)} raw -> {len(final_merged_segments)} final segments")
    return final_merged_segments

def save_learning_content(video_id: str, vocabulary: list = None, grammar: list = None):
    """
    Save vocabulary and grammar learning content to separate _learn.json file.

    Args:
        video_id: YouTube video ID
        vocabulary: Extracted vocabulary with timestamps
        grammar: Extracted grammar concepts with timestamps
    """
    try:
        script_dir = Path(__file__).parent
        cache_dir = script_dir / "cache" / "subtitles"
        cache_dir.mkdir(parents=True, exist_ok=True)

        # Create learning content file with _learn suffix
        learn_file = cache_dir / f"{video_id}_learn.json"

        learning_data = {
            "video_id": video_id,
            "learning_timestamp": time.time(),
            "type": "learning_content",
            "source": "ai_extracted_content",

            # Learning statistics
            "statistics": {
                "vocabulary_count": len(vocabulary) if vocabulary else 0,
                "grammar_count": len(grammar) if grammar else 0,
                "total_learning_items": (len(vocabulary) if vocabulary else 0) + (len(grammar) if grammar else 0)
            },

            # Learning content - separate from subtitle processing
            "vocabulary": vocabulary or [],
            "grammar": grammar or []
        }

        # Save to JSON file
        with open(learn_file, 'w', encoding='utf-8') as f:
            json.dump(learning_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved learning content to: {learn_file}")
        logger.info(f"Learning content: {len(vocabulary or [])} vocabulary + {len(grammar or [])} grammar concepts")

    except Exception as e:
        logger.error(f"Failed to save learning content: {e}")

def save_processed_subtitles(video_id: str, processed_segments: list, raw_segments: list):
    """
    Save processed subtitles with UI display information to _proc file (WITHOUT learning content).

    Args:
        video_id: YouTube video ID
        processed_segments: Post-processed subtitle segments
        raw_segments: Original raw subtitle segments
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

        # Comprehensive data for UI display (subtitle processing only)
        subtitle_data = {
            "video_id": video_id,
            "processing_timestamp": time.time(),
            "type": "ui_ready_processed_data",
            "source": "youtube_transcript_api_processed",

            # Statistics (subtitle processing only)
            "statistics": {
                "raw_segments_count": len(raw_segments),
                "processed_segments_count": len(processed_segments),
                "compression_ratio": f"{len(raw_segments)}/{len(processed_segments)} = {len(raw_segments)/len(processed_segments):.2f}x",
                "total_duration": max([seg.get('end', 0) for seg in processed_segments], default=0),
                "average_segment_duration": sum([seg.get('duration', 0) for seg in processed_segments]) / len(processed_segments) if processed_segments else 0
            },

            # UI-ready processed segments with complete information
            "ui_segments": ui_segments

            # Learning content moved to separate _learn.json file
        }

        # Save to JSON file
        with open(proc_file, 'w', encoding='utf-8') as f:
            json.dump(subtitle_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved UI-ready processed data to: {proc_file}")
        logger.info(f"Statistics: {len(raw_segments)} raw -> {len(processed_segments)} processed segments")

    except Exception as e:
        logger.error(f"Failed to save processed subtitles: {e}")
        # Don't raise - this is just for debugging, shouldn't break the main flow

def save_raw_subtitles(video_id: str, raw_segments: list):
    """
    Save complete raw subtitles to a separate file (without _proc suffix) for full backup.

    Args:
        video_id: YouTube video ID
        raw_segments: Original raw subtitle segments from YouTube API
    """
    logger.debug(f"🚨 SAVE_RAW_SUBTITLES: Starting save for {video_id} with {len(raw_segments)} segments")
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

        logger.info(f"Saved complete raw subtitles to: {raw_file}")
        logger.info(f"Raw segments saved: {len(raw_segments)} segments")

    except Exception as e:
        logger.error(f"Failed to save raw subtitles: {e}")
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
    """Get the sentence containing the word from processed segments
    Returns: (sentence_text, start_time, end_time)"""

    word_lower = word.lower()

    # Find the processed segment that contains this word
    for segment in transcript:
        segment_text = segment.get('text', '').lower()
        if word_lower in segment_text:
            # Use the processed segment directly - it's already a complete learning unit
            sentence = segment.get('text', '').strip()
            start_time = segment.get('start', timestamp)
            end_time = segment.get('end', start_time + segment.get('duration', 3.0))

            return (sentence, start_time, end_time)

    # Fallback: if word not found, find segment by timestamp
    for segment in transcript:
        segment_start = segment.get('start', 0)
        segment_end = segment.get('end', segment_start + segment.get('duration', 3.0))

        if segment_start <= timestamp <= segment_end:
            sentence = segment.get('text', '').strip()
            return (sentence, segment_start, segment_end)

    # Final fallback
    return (f"Context sentence containing '{word}'", timestamp, timestamp + 5)

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

        # CRITICAL FIX: Check for original segment mapping to get accurate word timing
        start_time = entry['start']
        duration = entry.get('duration', 3)

        # If this is a merged segment, find the original segment containing the word
        if 'original_segment_mapping' in entry:
            for orig_segment in entry['original_segment_mapping']:
                orig_text = orig_segment['text'].lower()
                if word.lower() in orig_text:
                    # Use the original segment's timing instead of merged timing
                    start_time = orig_segment['start']
                    duration = orig_segment['duration']
                    logger.debug(f"Found word '{word}' in original segment at {start_time}s (was {entry['start']}s in merged)")
                    break
        else:
            duration = entry.get('duration', 3)
        original_end = start_time + duration

        # Check if this is a no-punctuation scenario (no sentence endings)
        has_punctuation = bool(re.search(r'[.!?,]', text))

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

async def extract_vocabulary_from_transcript(transcript_text: str, transcript_data: list, user_level: str = "A2", max_words: int = 8, raw_segments: list = None):
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
    # Use raw segments for accurate timing, fallback to processed data
    timing_data_source = raw_segments if raw_segments else transcript_data
    sentence_boundaries = find_word_timestamps_smart(timing_data_source, selected_words)
    logger.debug(f"DEBUG: Using {'raw' if raw_segments else 'processed'} segments for word timing")
    logger.debug(f"DEBUG: Found smart timestamps for {len(sentence_boundaries)} words:")
    for word, data in sentence_boundaries.items():
        logger.debug(f"  - {word}: timestamp={data['timestamp']}, position={data.get('position_type', 'unknown')}, mode={data['playback_mode']}")

    # Get simple, kid-friendly definitions
    vocabulary = []
    for word in selected_words:
        level = get_word_difficulty(word)

        # Skip proper nouns and common names/places
        if level == "SKIP":
            logger.debug(f"Skipped proper noun: {word}")
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
                # Consistent naming for frontend
                "startTime": timestamp_data['timestamp'],
                "endTime": timestamp_data['end_time'],
                # Enhanced vocabulary information
                "definition_zh": enhanced_info.get('definition_zh', ''),
                "usage": enhanced_info.get('usage', ''),
                "examples": enhanced_info.get('examples', []),
                "synonyms": enhanced_info.get('synonyms', []),
                "collocations": enhanced_info.get('collocations', []),
                "pos": enhanced_info.get('pos', [])
            }
            logger.debug(f"Added {word} with timestamp {vocab_item['timestamp']}")
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
                "translation": translation,
                # Consistent naming for frontend
                "startTime": fallback_start,
                "endTime": fallback_start + 5,
                "sentence_start_time": fallback_start,
                "sentence_end_time": fallback_start + 5
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

            timestamp_start = random.randint(15, 200)
            grammar_concepts.append({
                "concept": pattern_info["concept"],
                "explanation": pattern_info["explanation"],
                "level": pattern_info["level"],
                "example": example[:50] + "..." if len(example) > 50 else example,
                "timestamp": timestamp_start,
                # Consistent naming for frontend
                "startTime": timestamp_start,
                "endTime": timestamp_start + 10,
                "sentence_start_time": timestamp_start,
                "sentence_end_time": timestamp_start + 10
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
            logger.info(f"Using cached RAW subtitles for {video_id} ({len(raw_segments)} raw segments)")
        else:
            # Method 1: YouTube Transcript API (CORRECTED syntax for system Python3)
            try:
                logger.info("🔍 Attempting CORRECTED YouTube Transcript API...")
                raw_transcript = YouTubeTranscriptApi.get_transcript(video_id)

                # Convert to expected format
                raw_segments = []
                for entry in raw_transcript:
                    raw_segments.append({
                        'text': entry.text,
                        'start': entry.start,
                        'duration': getattr(entry, 'duration', 0)
                    })

                transcript_source = "youtube_transcript_api_CORRECTED_RAW"
                logger.info(f"🎉 SUCCESS: Extracted {len(raw_segments)} RAW entries using CORRECTED YouTube Transcript API")

                # Save raw subtitles immediately after successful extraction
                logger.debug(f"🚨 DEBUG: About to save raw subtitles for {video_id}, segments count: {len(raw_segments)}")
                save_raw_subtitles(video_id, raw_segments)
                logger.debug(f"🚨 DEBUG: Raw subtitles save completed for {video_id}")

            except Exception as transcript_error:
                logger.error(f"YouTube Transcript API failed: {transcript_error}")

                # Method 2: yt-dlp fallback (if available)
                if not raw_segments and YT_DLP_AVAILABLE:
                    try:
                        logger.info("Attempting yt-dlp subtitle extraction...")
                        raw_segments = extract_subtitles_with_ytdlp(video_url)
                        transcript_source = "yt_dlp_raw"
                        logger.info(f"Successfully extracted {len(raw_segments)} RAW entries using yt-dlp")

                        # Save raw subtitles immediately after successful extraction
                        save_raw_subtitles(video_id, raw_segments)

                    except Exception as ytdlp_error:
                        logger.error(f"yt-dlp subtitle extraction failed: {ytdlp_error}")
                else:
                    logger.warning("yt-dlp not available, skipping alternative extraction method")

        # Apply post-processing dynamically if we have raw segments
        transcript = None
        if raw_segments and len(raw_segments) > 0:
            # Apply post-processing to create better sentence boundaries
            transcript = post_process_subtitles(raw_segments, pause_gap_threshold=1.0)
            logger.info(f"Applied dynamic post-processing: {len(raw_segments)} raw segments -> {len(transcript)} processed sentences")

        # Process transcript if we got one
        if transcript and len(transcript) > 0:
            transcript_text = " ".join([entry['text'] for entry in transcript])

            # Extract vocabulary and grammar from real transcript with adaptive selection
            # Pass both processed and raw data for accurate timing
            vocabulary = await extract_vocabulary_from_transcript(transcript_text, transcript, user_level, 8, raw_segments)
            grammar = extract_grammar_from_transcript(transcript_text)

            # Save processed subtitles (subtitle processing only)
            save_processed_subtitles(video_id, transcript, raw_segments)

            # Save learning content separately (vocabulary and grammar)
            save_learning_content(video_id, vocabulary, grammar)

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
            logger.warning("All transcript extraction methods failed, using fallback mock data")
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
        logger.error(f"CRITICAL ERROR in extract_content: {str(e)}")
        logger.error("Full stack trace:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing video: {str(e)}")

# AI Teacher System
def generate_contextual_response(word: str, definition: str, sentence: str, question: str) -> str:
    """Generate contextual AI teacher responses based on user questions"""

    question_lower = question.lower()

    # Question pattern matching for intelligent responses
    if any(phrase in question_lower for phrase in ["how to use", "how do i use", "usage", "use this"]):
        return f"""Great question! Here are several ways to use '{word}':

**Definition**: {definition}

**In the video context**: "{sentence}"

**More examples:**
• "I learned about {word} in my English class."
• "The {word} helps us understand the topic better."
• "Can you explain {word} in simpler terms?"

**Grammar tip**: '{word}' is typically used as a {get_word_type(word)}. Remember to match it with appropriate articles (a, an, the) when needed.

Try creating your own sentence with '{word}' - what situation would you use it in? 🤔"""

    elif any(phrase in question_lower for phrase in ["similar", "synonym", "like", "related"]):
        return f"""Excellent question! Here are words similar to '{word}':

**Main word**: {word} - {definition}

**Similar words**:
{generate_similar_words(word, definition)}

**Context differences**:
Each similar word has slightly different usage contexts. For example:
- In formal writing: Use more sophisticated synonyms
- In casual conversation: Simpler words work better
- In academic contexts: Precise terminology is important

**Practice**: Try replacing '{word}' in this sentence with one of the similar words: "{sentence}"

Does that help clarify the differences? Feel free to ask about any specific word! 📚"""

    elif any(phrase in question_lower for phrase in ["example", "more examples", "sentences"]):
        return f"""Perfect! Let me give you more examples with '{word}':

**Original context**: "{sentence}"

**Additional examples**:
{generate_example_sentences(word, definition)}

**Different contexts**:
• **Formal**: In academic discussions about {word}...
• **Casual**: You know, {word} is really interesting because...
• **Question form**: What do you think about {word}?
• **Negative form**: I don't fully understand {word} yet.

**Your turn**: Can you create a sentence using '{word}' in a different context? I'd love to hear your attempt! ✨"""

    elif any(phrase in question_lower for phrase in ["remember", "memorize", "memory", "forget"]):
        return f"""Great question about memory techniques! Here are proven methods to remember '{word}':

**Memory Techniques**:
{generate_memory_tricks(word, definition)}

**Spaced Repetition**:
• Review '{word}' tomorrow
• Review again in 3 days
• Review again in 1 week
• Review again in 1 month

**Active Usage**:
Try using '{word}' in conversations this week. The more you use it, the better you'll remember it!

**Context Connection**:
Remember this video context: "{sentence[:50]}..."
This real situation will help trigger your memory of '{word}'.

What memory technique works best for you usually? 🧠"""

    elif any(phrase in question_lower for phrase in ["difficult", "hard", "confusing", "don't understand"]):
        return f"""I understand! '{word}' can be tricky. Let me break it down simply:

**Simple explanation**: {get_simple_explanation(word, definition)}

**Why it might be confusing**:
{analyze_difficulty(word, definition)}

**Step-by-step understanding**:
1. First, think of {word} as: {get_simple_analogy(word)}
2. In the video: "{sentence}"
3. The key idea is: {extract_key_concept(definition)}
4. Practice: Use it in a simple sentence about your daily life

**Don't worry!** Even native speakers sometimes find certain words challenging. The fact that you're asking shows you're learning actively!

What specific part about '{word}' confuses you most? Let's tackle it together! 💪"""

    elif any(phrase in question_lower for phrase in ["grammar", "grammatical", "part of speech"]):
        return f"""Excellent grammar question! Let me explain '{word}' grammatically:

**Part of Speech**: {get_word_type(word)}
**Grammar Pattern**: {analyze_grammar_pattern(word, sentence)}

**In your sentence**: "{sentence}"
Here, '{word}' functions as {explain_grammatical_function(word, sentence)}

**Grammar Rules**:
{generate_grammar_rules(word)}

**Common Mistakes to Avoid**:
{generate_common_mistakes(word)}

**Practice Patterns**:
• Try: [Subject] + [Verb] + {word}
• Try: {word} + [Verb] + [Object]

Grammar can be complex, but don't worry! Focus on understanding the pattern first, then practice it. 📝"""

    else:
        # Generic helpful response for other questions
        return f"""That's a thoughtful question about '{word}'! Let me help:

**About '{word}'**: {definition}

**In context**: "{sentence}"

**Key points**:
• **Meaning**: {extract_key_concept(definition)}
• **Usage**: Most commonly used in {get_usage_context(word)}
• **Level**: This is a {get_difficulty_level(word)}-level word
• **Frequency**: {get_word_frequency(word)} in everyday English

**Interactive Learning**:
- Try using '{word}' in your next English conversation
- Look for '{word}' in other videos, articles, or books
- Practice explaining '{word}' to someone else

**Follow-up questions you might ask**:
• "How do I use {word} in a sentence?"
• "What are words similar to {word}?"
• "Can you give me more examples?"

Feel free to ask me anything else about '{word}' or English learning! I'm here to help! 🎯"""

# Helper functions for AI teacher responses
def get_word_type(word: str) -> str:
    """Determine the likely part of speech for a word"""
    # Simple heuristics - could be enhanced with NLP libraries
    if word.endswith(('ing', 'ed', 'ize', 'ise')):
        return "verb"
    elif word.endswith(('tion', 'sion', 'ness', 'ity', 'ment')):
        return "noun"
    elif word.endswith(('ly')):
        return "adverb"
    elif word.endswith(('ful', 'less', 'ous', 'ive', 'able')):
        return "adjective"
    else:
        return "noun/verb"  # Most common types

def generate_similar_words(word: str, definition: str) -> str:
    """Generate contextually similar words"""
    # Simple synonym mapping - could be enhanced with actual thesaurus API
    common_synonyms = {
        'people': '• folks, individuals, persons, humans\n• community, society, population',
        'about': '• concerning, regarding, related to\n• approximately, roughly, around',
        'campus': '• grounds, premises, facility\n• university, college, school',
        'from': '• out of, away from, starting at\n• originating in, coming from',
        'said': '• stated, mentioned, declared\n• expressed, articulated, voiced'
    }

    return common_synonyms.get(word.lower(), f"• related words to '{word}'\n• similar terms in context\n• contextual alternatives")

def generate_example_sentences(word: str, definition: str) -> str:
    """Generate example sentences for the word"""
    examples = {
        'people': '• "Many people enjoy learning languages."\n• "The people in this video are very friendly."\n• "Young people often use social media."',
        'about': '• "This book is about language learning."\n• "I know about that topic."\n• "It takes about 30 minutes to get there."',
        'campus': '• "I live on campus during the semester."\n• "The campus library is very modern."\n• "Students walk around campus every day."',
        'from': '• "I come from China."\n• "This letter is from my teacher."\n• "The store is open from 9 to 5."',
        'said': '• "She said hello to everyone."\n• "He said it was important."\n• "They said goodbye before leaving."'
    }

    return examples.get(word.lower(), f'• "The {word} is important in this context."\n• "I learned about {word} today."\n• "Using {word} correctly takes practice."')

def generate_memory_tricks(word: str, definition: str) -> str:
    """Generate memory techniques for the word"""
    tricks = {
        'people': '• Visual: Picture a group of **people** (PEE-ple)\n• Connection: "people" = many persons\n• Rhyme: "People like to be equal"',
        'about': '• Think: "a-BOUT" = around/concerning something\n• Memory: "about" = "a" + "bout" (fight about something)\n• Visual: Draw a circle **about** the word',
        'campus': '• Memory: "camp" + "us" = where we camp to study\n• Visual: Picture a school **campus** with buildings\n• Sound: "CAM-pus" sounds like "camp us"',
        'from': '• Direction: Always shows movement away **from** somewhere\n• Visual: Draw an arrow pointing **from** one place\n• Opposite: Remember "from" vs "to" (from → to)',
        'said': '• Past tense: "say" becomes "said" (irregular verb)\n• Pronunciation: "said" sounds like "sed"\n• Pattern: I say → I said → I have said'
    }

    return tricks.get(word.lower(), f'• Break down "{word}" into smaller parts\n• Connect "{word}" to something you know\n• Use "{word}" in a personal sentence')

def get_simple_explanation(word: str, definition: str) -> str:
    """Provide a simple explanation of the word"""
    return f"Think of '{word}' as: {definition[:50]}..." if len(definition) > 50 else definition

def analyze_difficulty(word: str, definition: str) -> str:
    """Analyze why a word might be difficult"""
    return f"'{word}' can be confusing because it has multiple meanings and is used in different contexts. Don't worry - with practice, it becomes natural!"

def get_simple_analogy(word: str) -> str:
    """Provide a simple analogy for the word"""
    analogies = {
        'people': 'humans like you and me',
        'about': 'the topic of something',
        'campus': 'a school\'s outdoor area',
        'from': 'the starting point',
        'said': 'spoke in the past'
    }
    return analogies.get(word.lower(), f'the main idea of {word}')

def extract_key_concept(definition: str) -> str:
    """Extract the key concept from definition"""
    # Take first part of definition before comma or period
    key_part = definition.split(',')[0].split('.')[0]
    return key_part if len(key_part) < 100 else definition[:50] + "..."

def analyze_grammar_pattern(word: str, sentence: str) -> str:
    """Analyze the grammar pattern of the word in sentence"""
    return f"In this sentence, '{word}' follows standard English grammar patterns"

def explain_grammatical_function(word: str, sentence: str) -> str:
    """Explain the grammatical function of word in sentence"""
    return f"a key element that helps convey the main message"

def generate_grammar_rules(word: str) -> str:
    """Generate grammar rules for the word"""
    return f"• Use '{word}' in subject-verb-object patterns\n• Remember proper article usage (a/an/the)\n• Pay attention to singular/plural forms"

def generate_common_mistakes(word: str) -> str:
    """Generate common mistakes to avoid"""
    return f"• Don't confuse '{word}' with similar-sounding words\n• Remember the correct spelling\n• Use in appropriate contexts"

def get_usage_context(word: str) -> str:
    """Get the usage context for the word"""
    contexts = {
        'people': 'social situations, describing groups',
        'about': 'explanations, topics, estimates',
        'campus': 'educational settings, school discussions',
        'from': 'origins, directions, sources',
        'said': 'reporting speech, past conversations'
    }
    return contexts.get(word.lower(), 'general conversation and writing')

def get_difficulty_level(word: str) -> str:
    """Get the difficulty level of the word"""
    return "beginner"  # Default for now

def get_word_frequency(word: str) -> str:
    """Get word frequency information"""
    frequent_words = ['people', 'about', 'from', 'said']
    if word.lower() in frequent_words:
        return "Very common"
    else:
        return "Moderately common"

# Assessment System Functions
def generate_assessment_questions() -> list:
    """Generate adaptive vocabulary assessment questions"""
    questions = [
        {
            "id": 1,
            "word": "ambitious",
            "definition": "Having a strong desire for success or achievement",
            "options": ["Lazy and unmotivated", "Having strong desire for success", "Feeling sad or depressed", "Being very quiet"],
            "correctAnswer": 1,
            "level": "B2",
            "difficulty": 6
        },
        {
            "id": 2,
            "word": "fundamental",
            "definition": "Basic and essential; of central importance",
            "options": ["Optional and unnecessary", "Basic and essential", "Complex and confusing", "Temporary and changeable"],
            "correctAnswer": 1,
            "level": "B2",
            "difficulty": 5
        },
        {
            "id": 3,
            "word": "significant",
            "definition": "Important; having meaning or consequence",
            "options": ["Unimportant", "Important and meaningful", "Very small", "Completely useless"],
            "correctAnswer": 1,
            "level": "B1",
            "difficulty": 4
        },
        {
            "id": 4,
            "word": "evaluate",
            "definition": "To judge or determine the worth of something",
            "options": ["To ignore completely", "To judge or assess", "To buy something expensive", "To throw away"],
            "correctAnswer": 1,
            "level": "B2",
            "difficulty": 6
        },
        {
            "id": 5,
            "word": "efficient",
            "definition": "Working in a well-organized way; not wasting time or resources",
            "options": ["Very slow and wasteful", "Well-organized and effective", "Broken and useless", "Extremely expensive"],
            "correctAnswer": 1,
            "level": "B1",
            "difficulty": 4
        },
        {
            "id": 6,
            "word": "comprehensive",
            "definition": "Complete and including everything",
            "options": ["Incomplete and missing parts", "Complete and thorough", "Very simple and basic", "Extremely difficult"],
            "correctAnswer": 1,
            "level": "C1",
            "difficulty": 7
        },
        {
            "id": 7,
            "word": "demonstrate",
            "definition": "To show clearly by giving proof or evidence",
            "options": ["To hide something", "To show or prove", "To break something", "To forget completely"],
            "correctAnswer": 1,
            "level": "B1",
            "difficulty": 4
        },
        {
            "id": 8,
            "word": "alternative",
            "definition": "One of two or more available possibilities",
            "options": ["The only option", "One of several choices", "Something impossible", "A broken item"],
            "correctAnswer": 1,
            "level": "B2",
            "difficulty": 5
        },
        {
            "id": 9,
            "word": "inevitable",
            "definition": "Certain to happen; unavoidable",
            "options": ["Certain to happen", "Never going to happen", "Maybe happening", "Already finished"],
            "correctAnswer": 0,
            "level": "C1",
            "difficulty": 8
        },
        {
            "id": 10,
            "word": "contemporary",
            "definition": "Belonging to the present time; modern",
            "options": ["Very old and ancient", "Modern and current", "Future and unknown", "Broken and useless"],
            "correctAnswer": 1,
            "level": "C1",
            "difficulty": 7
        },
        {
            "id": 11,
            "word": "obvious",
            "definition": "Easy to see or understand; clear",
            "options": ["Very confusing", "Easy to understand", "Impossible to know", "Extremely complicated"],
            "correctAnswer": 1,
            "level": "A2",
            "difficulty": 2
        },
        {
            "id": 12,
            "word": "successful",
            "definition": "Achieving what you wanted to achieve",
            "options": ["Failing completely", "Achieving your goals", "Starting something new", "Being very tired"],
            "correctAnswer": 1,
            "level": "A2",
            "difficulty": 3
        }
    ]

    return questions

def evaluate_assessment(answers: list) -> dict:
    """Evaluate assessment answers and determine user level"""
    if not answers:
        return get_default_assessment_result()

    questions = generate_assessment_questions()
    correct_answers = 0
    level_scores = {"A1": 0, "A2": 0, "B1": 0, "B2": 0, "C1": 0, "C2": 0}

    for i, answer in enumerate(answers):
        if i < len(questions):
            question = questions[i]
            if answer == question["correctAnswer"]:
                correct_answers += 1
                level_scores[question["level"]] += 1

    total_questions = len(answers)
    accuracy = correct_answers / total_questions if total_questions > 0 else 0

    # Determine estimated level based on performance
    estimated_level = determine_level_from_scores(level_scores, accuracy)
    confidence = calculate_confidence(level_scores, accuracy)

    return {
        "totalQuestions": total_questions,
        "correctAnswers": correct_answers,
        "estimatedLevel": estimated_level,
        "levelConfidence": confidence,
        "strengths": get_strengths(level_scores),
        "weaknesses": get_weaknesses(level_scores),
        "recommendedStartLevel": get_recommended_start_level(estimated_level)
    }

def get_default_assessment_result() -> dict:
    """Return default assessment result for new users"""
    return {
        "totalQuestions": 0,
        "correctAnswers": 0,
        "estimatedLevel": "A2",
        "levelConfidence": 0.5,
        "strengths": ["Eager to learn"],
        "weaknesses": ["Assessment not completed"],
        "recommendedStartLevel": "A2"
    }

def determine_level_from_scores(level_scores: dict, accuracy: float) -> str:
    """Determine CEFR level based on question performance"""
    if accuracy < 0.3:
        return "A1"
    elif accuracy < 0.5:
        return "A2"
    elif accuracy < 0.7:
        return "B1"
    elif accuracy < 0.85:
        return "B2"
    elif accuracy < 0.95:
        return "C1"
    else:
        return "C2"

def calculate_confidence(level_scores: dict, accuracy: float) -> float:
    """Calculate confidence level for the assessment result"""
    # Higher accuracy and consistent performance across levels = higher confidence
    max_score = max(level_scores.values()) if level_scores.values() else 0
    consistency = 1.0 - (max_score / sum(level_scores.values()) if sum(level_scores.values()) > 0 else 0)
    return min(0.9, accuracy * 0.7 + consistency * 0.3)

def get_strengths(level_scores: dict) -> list:
    """Identify user strengths based on performance"""
    strengths = []
    max_score = max(level_scores.values()) if level_scores.values() else 0

    if max_score > 2:
        best_level = max(level_scores.items(), key=lambda x: x[1])[0]
        strengths.append(f"Strong {best_level} level vocabulary")

    if level_scores.get("A2", 0) > 1:
        strengths.append("Good foundation in basic vocabulary")

    if level_scores.get("B1", 0) > 1:
        strengths.append("Solid intermediate vocabulary")

    if level_scores.get("C1", 0) > 0:
        strengths.append("Advanced vocabulary knowledge")

    return strengths if strengths else ["Motivation to learn"]

def get_weaknesses(level_scores: dict) -> list:
    """Identify areas for improvement"""
    weaknesses = []

    if level_scores.get("A2", 0) == 0:
        weaknesses.append("Basic vocabulary needs work")

    if level_scores.get("B1", 0) == 0:
        weaknesses.append("Intermediate vocabulary development needed")

    if level_scores.get("B2", 0) == 0:
        weaknesses.append("Upper-intermediate vocabulary expansion")

    return weaknesses if weaknesses else ["Continue building vocabulary"]

def get_recommended_start_level(estimated_level: str) -> str:
    """Get recommended starting level for learning"""
    level_progression = {"A1": "A1", "A2": "A1", "B1": "A2", "B2": "B1", "C1": "B2", "C2": "C1"}
    return level_progression.get(estimated_level, "A2")

def generate_ai_teacher_response(word: str, definition: str, sentence: str, user_question: str = None) -> str:
    """Generate AI teacher response to help user learn vocabulary"""

    # If user asked a specific question, provide contextual response
    if user_question:
        return generate_contextual_response(word, definition, sentence, user_question)

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

# User Profile and Assessment System
@app.post("/api/assessment/start")
async def start_assessment():
    """Start vocabulary assessment and return initial questions"""
    try:
        questions = generate_assessment_questions()
        return {
            "questions": questions,
            "total_questions": len(questions),
            "session_id": f"assessment_{int(time.time())}",
            "timestamp": int(time.time())
        }
    except Exception as e:
        logger.error(f"Error starting assessment: {e}")
        raise HTTPException(status_code=500, detail=f"Assessment error: {str(e)}")

@app.post("/api/assessment/submit")
async def submit_assessment(request: dict):
    """Submit assessment answers and get user level recommendation"""
    try:
        answers = request.get('answers', [])
        session_id = request.get('session_id', '')

        if not answers:
            raise HTTPException(status_code=400, detail="Answers are required")

        result = evaluate_assessment(answers)

        return {
            "session_id": session_id,
            "result": result,
            "timestamp": int(time.time())
        }
    except Exception as e:
        logger.error(f"Error submitting assessment: {e}")
        raise HTTPException(status_code=500, detail=f"Assessment submission error: {str(e)}")

@app.post("/api/profile/create")
async def create_user_profile(request: dict):
    """Create new user profile"""
    try:
        name = request.get('name', 'Anonymous User')
        estimated_level = request.get('estimatedLevel', 'A2')
        completed_assessment = request.get('completedAssessment', False)

        profile = {
            "id": f"user_{int(time.time())}_{hash(name) % 10000}",
            "name": name,
            "estimatedLevel": estimated_level,
            "completedAssessment": completed_assessment,
            "createdAt": int(time.time()),
            "lastActiveAt": int(time.time()),
            "totalStudyTime": 0,
            "wordsLearned": 0,
            "currentStreak": 0,
            "longestStreak": 0
        }

        # In a real app, save to database
        # For now, return the profile for frontend storage

        return {
            "profile": profile,
            "message": "Profile created successfully",
            "timestamp": int(time.time())
        }
    except Exception as e:
        logger.error(f"Error creating profile: {e}")
        raise HTTPException(status_code=500, detail=f"Profile creation error: {str(e)}")

@app.get("/api/profile/{user_id}")
async def get_user_profile(user_id: str):
    """Get user profile by ID"""
    try:
        # In a real app, fetch from database
        # For now, return a mock profile
        profile = {
            "id": user_id,
            "name": "Language Learner",
            "estimatedLevel": "A2",
            "completedAssessment": True,
            "createdAt": int(time.time()) - 86400,  # 1 day ago
            "lastActiveAt": int(time.time()),
            "totalStudyTime": 120,  # 2 hours
            "wordsLearned": 45,
            "currentStreak": 3,
            "longestStreak": 7
        }

        return {
            "profile": profile,
            "timestamp": int(time.time())
        }
    except Exception as e:
        logger.error(f"Error fetching profile: {e}")
        raise HTTPException(status_code=500, detail=f"Profile fetch error: {str(e)}")

@app.post("/api/profile/update")
async def update_user_profile(request: dict):
    """Update user profile"""
    try:
        user_id = request.get('userId', '')
        updates = request.get('updates', {})

        if not user_id:
            raise HTTPException(status_code=400, detail="User ID is required")

        # In a real app, update database
        # For now, return success response

        return {
            "userId": user_id,
            "updates": updates,
            "message": "Profile updated successfully",
            "timestamp": int(time.time())
        }
    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        raise HTTPException(status_code=500, detail=f"Profile update error: {str(e)}")

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
        logger.error(f"Error in AI teacher: {e}")
        raise HTTPException(status_code=500, detail=f"AI teacher error: {str(e)}")

def generate_learning_sessions(vocabulary_list: list, session_size: int = 5, user_level: str = "A2") -> list:
    """
    Generate smart learning sessions from vocabulary list.

    Smart Navigator Algorithm:
    1. Group words by difficulty (CEFR level)
    2. Prioritize user level and one level above
    3. Distribute words with minimum time gaps to avoid clustering
    4. Create balanced sessions of 3-7 words each
    """
    if not vocabulary_list:
        return []

    # CEFR level priority mapping (lower number = higher priority)
    level_priority = {"A1": 1, "A2": 2, "B1": 3, "B2": 4, "C1": 5, "C2": 6}

    # Determine priority levels based on user level
    user_priority = level_priority.get(user_level.upper(), 2)
    target_levels = []

    # Include user level and next level up for optimal challenge
    for level, priority in level_priority.items():
        if priority == user_priority:
            target_levels.append(level)
        elif priority == user_priority + 1:  # One level up for challenge
            target_levels.append(level)

    # Sort vocabulary by priority, then by timestamp
    def word_priority(word):
        word_level = word.get('level', 'A2').upper()
        level_score = level_priority.get(word_level, 3)

        # Boost priority for target levels
        if word_level in target_levels:
            level_score -= 0.5

        # Use timestamp for chronological ordering within same priority
        timestamp = word.get('timestamp', 0)

        return (level_score, timestamp)

    sorted_vocabulary = sorted(vocabulary_list, key=word_priority)

    # Apply smart time-based distribution to avoid clustering
    def select_distributed_words(words, max_per_session, min_time_gap=15.0):
        """
        Select words ensuring minimum time gap between consecutive words
        to prevent clustering and rapid consecutive pauses
        """
        if not words:
            return []

        selected = []
        last_timestamp = -min_time_gap  # Start with negative to allow first word

        for word in words:
            current_timestamp = word.get('timestamp', 0)

            # Check if enough time has passed since last selected word
            if current_timestamp - last_timestamp >= min_time_gap:
                selected.append(word)
                last_timestamp = current_timestamp

                # Stop if we have enough words for this session
                if len(selected) >= max_per_session:
                    break

        return selected

    # Generate sessions with distributed word selection
    sessions = []
    session_id = 1
    remaining_words = sorted_vocabulary[:]

    while remaining_words:
        # Select distributed words for this session
        session_words = select_distributed_words(remaining_words, session_size)

        if not session_words:
            # If no words meet the time gap requirement, take the first available
            session_words = remaining_words[:min(session_size, len(remaining_words))]

        # Remove selected words from remaining pool
        selected_word_texts = {word.get('word', '').lower() for word in session_words}
        remaining_words = [w for w in remaining_words if w.get('word', '').lower() not in selected_word_texts]

        # Sort session words by timestamp for proper playback order
        session_words_sorted = sorted(session_words, key=lambda x: x.get('timestamp', 0))

        # Calculate session difficulty (average of word levels)
        levels = [word.get('level', 'A2') for word in session_words_sorted]
        level_scores = [level_priority.get(level.upper(), 3) for level in levels]
        avg_difficulty = sum(level_scores) / len(level_scores) if level_scores else 2

        # Determine session level based on average difficulty
        session_level = "A2"  # Default
        for level, score in level_priority.items():
            if abs(score - avg_difficulty) < 0.6:
                session_level = level
                break

        # Calculate session timing
        if session_words_sorted:
            start_time = session_words_sorted[0].get('timestamp', 0)
            end_time = session_words_sorted[-1].get('end_time', session_words_sorted[-1].get('timestamp', 0) + 3)
        else:
            start_time = end_time = 0

        session = {
            "session_id": session_id,
            "session_number": session_id,
            "total_sessions": 0,  # Will be updated after all sessions are created
            "focus_words": session_words_sorted,
            "session_level": session_level,
            "estimated_duration": len(session_words_sorted) * 2,  # ~2 minutes per word
            "difficulty_distribution": {
                level: levels.count(level) for level in set(levels)
            },
            "startTime": start_time,
            "endTime": end_time,
            "status": "ready"
        }

        sessions.append(session)
        session_id += 1

        # Log session info for debugging
        if session_words_sorted:
            timestamps = [f"{w.get('word')}@{w.get('timestamp', 0):.1f}s" for w in session_words_sorted]
            logger.info(f"📚 Session {session_id-1}: {', '.join(timestamps)}")

    # Update total session count for all sessions
    total_sessions = len(sessions)
    for session in sessions:
        session["total_sessions"] = total_sessions

    logger.info(f"✅ Generated {total_sessions} learning sessions with improved word distribution")
    return sessions

def find_replacement_word(vocabulary_list: list, mastered_word: str, session_context: list, mastered_words: list = None) -> dict:
    """
    Find a replacement word when user marks a word as already known.

    Smart Replacement Logic:
    1. Find words of same or higher difficulty
    2. Prefer words from same video segment (similar timestamp)
    3. Avoid words already in the session
    4. Prioritize words that appear in context
    """
    if not vocabulary_list:
        return None

    # Get the mastered word info
    mastered_word_info = None
    for word in vocabulary_list:
        if word.get('word', '').lower() == mastered_word.lower():
            mastered_word_info = word
            break

    if not mastered_word_info:
        return None

    # Get context info
    mastered_timestamp = mastered_word_info.get('timestamp', 0)
    mastered_level = mastered_word_info.get('level', 'A2')

    # Get words already in session
    session_words = {word.get('word', '').lower() for word in session_context}
    session_words.add(mastered_word.lower())

    # Add previously mastered words to exclusion list
    if mastered_words:
        session_words.update(word.lower() for word in mastered_words)
        logger.info(f"🚫 Excluding {len(session_words)} total words from replacement pool (session + mastered)")

    # Find candidate replacements
    level_priority = {"A1": 1, "A2": 2, "B1": 3, "B2": 4, "C1": 5, "C2": 6}
    mastered_priority = level_priority.get(mastered_level.upper(), 2)

    candidates = []
    for word in vocabulary_list:
        word_text = word.get('word', '').lower()
        word_level = word.get('level', 'A2')
        word_priority = level_priority.get(word_level.upper(), 2)
        word_timestamp = word.get('timestamp', 0)

        # Skip if already in session or same as mastered word
        if word_text in session_words:
            continue

        # Only consider same level or harder
        if word_priority < mastered_priority:
            continue

        # Calculate proximity score (closer timestamp = better)
        time_distance = abs(word_timestamp - mastered_timestamp)
        proximity_score = 1.0 / (1.0 + time_distance / 30.0)  # 30 second window

        # Calculate difficulty match score
        level_match_score = 1.0 if word_priority == mastered_priority else 0.7

        # Overall score
        total_score = proximity_score * 0.6 + level_match_score * 0.4

        candidates.append({
            'word_info': word,
            'score': total_score,
            'proximity_score': proximity_score,
            'level_match_score': level_match_score
        })

    # Sort by score and return best candidate
    if candidates:
        logger.info(f"🎯 Found {len(candidates)} replacement candidates")
        best_candidate = sorted(candidates, key=lambda x: x['score'], reverse=True)[0]
        logger.info(f"✅ Selected replacement: '{best_candidate['word_info']['word']}' (score: {best_candidate['score']:.3f})")
        return best_candidate['word_info']

    logger.warning(f"❌ No replacement candidates found for '{mastered_word}' - pool may be exhausted")
    return None

@app.post("/api/generate-sessions")
async def generate_sessions_endpoint(request: dict):
    """Generate smart learning sessions from vocabulary list"""
    try:
        vocabulary_list = request.get('vocabulary', [])
        session_size = request.get('session_size', 5)
        user_level = request.get('user_level', 'A2')

        if not vocabulary_list:
            raise HTTPException(status_code=400, detail="Vocabulary list is required")

        sessions = generate_learning_sessions(vocabulary_list, session_size, user_level)

        return {
            "sessions": sessions,
            "total_sessions": len(sessions),
            "total_words": len(vocabulary_list),
            "user_level": user_level,
            "session_size": session_size,
            "generated_at": int(time.time())
        }

    except Exception as e:
        logger.error(f"Error generating sessions: {e}")
        raise HTTPException(status_code=500, detail=f"Session generation error: {str(e)}")

@app.post("/api/replace-word")
async def replace_word_endpoint(request: dict):
    """Replace a mastered word with a new challenge word"""
    try:
        vocabulary_list = request.get('vocabulary', [])
        mastered_word = request.get('mastered_word', '')
        session_context = request.get('session_context', [])
        mastered_words = request.get('mastered_words', [])  # List of all previously mastered words

        if not vocabulary_list or not mastered_word:
            raise HTTPException(status_code=400, detail="Vocabulary list and mastered word are required")

        replacement_word = find_replacement_word(vocabulary_list, mastered_word, session_context, mastered_words)

        if replacement_word:
            return {
                "replacement_found": True,
                "replacement_word": replacement_word,
                "mastered_word": mastered_word,
                "replaced_at": int(time.time())
            }
        else:
            return {
                "replacement_found": False,
                "mastered_word": mastered_word,
                "message": "No suitable replacement found - excellent vocabulary level!",
                "replaced_at": int(time.time())
            }

    except Exception as e:
        logger.error(f"Error replacing word: {e}")
        raise HTTPException(status_code=500, detail=f"Word replacement error: {str(e)}")

if __name__ == "__main__":
    import uvicorn

    # Configure uvicorn logging
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["default"]["fmt"] = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    log_config["formatters"]["access"]["fmt"] = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_config=log_config,
        access_log=True
    )