#!/usr/bin/env python3
"""
Temporary script to create missing _lLkyJJm_o4.json raw file
"""

import json
import time
import subprocess
import sys
from pathlib import Path

def extract_with_ytdlp(video_url):
    """Extract subtitles using yt-dlp"""
    try:
        # Run yt-dlp to extract subtitle data
        result = subprocess.run([
            'yt-dlp',
            '--write-auto-sub',
            '--skip-download',
            '--sub-format', 'json3',
            '--output', 'temp_subtitle',
            video_url
        ], capture_output=True, text=True, check=False)

        if result.returncode == 0:
            print("yt-dlp extraction successful")
            # Look for subtitle file
            subtitle_files = list(Path('.').glob('temp_subtitle*.json3'))
            if subtitle_files:
                with open(subtitle_files[0], 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Convert to our format
                raw_segments = []
                if 'events' in data:
                    for event in data['events']:
                        if 'segs' in event and 'tStartMs' in event:
                            start_time = event['tStartMs'] / 1000.0
                            text = ''.join([seg.get('utf8', '') for seg in event['segs']])
                            if text.strip():
                                raw_segments.append({
                                    'text': text.strip(),
                                    'start': start_time
                                })

                # Clean up temp files
                for f in subtitle_files:
                    f.unlink()

                return raw_segments
        else:
            print(f"yt-dlp failed: {result.stderr}")
    except Exception as e:
        print(f"yt-dlp extraction error: {e}")

    return []

def create_raw_file():
    """Create the missing raw subtitle file"""
    video_id = "_lLkyJJm_o4"
    video_url = f"https://www.youtube.com/watch?v={video_id}"

    print(f"Extracting subtitles for {video_id}...")

    # Extract raw subtitles
    raw_segments = extract_with_ytdlp(video_url)

    if not raw_segments:
        print("Failed to extract subtitles")
        return False

    print(f"Extracted {len(raw_segments)} raw segments")

    # Create the raw data in correct format
    raw_data = {
        "video_id": video_id,
        "cached_at": time.time(),
        "subtitles": raw_segments,
        "source": "yt_dlp_manual_extraction",
        "segments_count": len(raw_segments)
    }

    # Save to cache directory
    cache_dir = Path("backend/backend/cache/subtitles")
    cache_dir.mkdir(parents=True, exist_ok=True)

    raw_file = cache_dir / f"{video_id}.json"

    with open(raw_file, 'w', encoding='utf-8') as f:
        json.dump(raw_data, f, ensure_ascii=False, indent=2)

    print(f"✅ Created raw file: {raw_file}")
    print(f"File contains {len(raw_segments)} subtitle segments")
    return True

if __name__ == "__main__":
    success = create_raw_file()
    if success:
        print("✅ Raw file creation successful!")
    else:
        print("❌ Raw file creation failed!")
        sys.exit(1)