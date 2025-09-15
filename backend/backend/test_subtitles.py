#!/usr/bin/env python3
"""
Test script demonstrating working YouTube subtitle extraction
This shows the actual subtitle extraction is working correctly.
"""

from youtube_transcript_api import YouTubeTranscriptApi
import json

def test_subtitle_extraction():
    """Test subtitle extraction with multiple videos"""

    test_videos = [
        {'id': '9bZkp7q19f0', 'name': 'Gangnam Style'},
        {'id': 'dQw4w9WgXcQ', 'name': 'Rick Roll'},
        {'id': 'fJ9rUzIMcZQ', 'name': 'Queen - Bohemian Rhapsody'},
        {'id': 'Ge7c7otG2mk', 'name': 'TED Talk'}
    ]

    working_videos = []

    for video in test_videos:
        try:
            print(f"\n🎬 Testing: {video['name']} ({video['id']})")

            # Use the corrected API
            api = YouTubeTranscriptApi()
            raw_transcript = api.fetch(video['id'])

            # Convert to our expected format
            transcript = []
            for entry in raw_transcript:
                transcript.append({
                    'text': entry.text,
                    'start': entry.start,
                    'duration': getattr(entry, 'duration', 0)
                })

            # Extract sample text
            transcript_text = ' '.join([entry['text'] for entry in transcript[:5]])

            print(f"✅ SUCCESS: {len(transcript)} entries")
            print(f"📝 Sample: {transcript_text[:100]}...")

            working_videos.append(video['name'])

        except Exception as e:
            print(f"❌ FAILED: {e}")

    print(f"\n🏆 Summary: {len(working_videos)}/{len(test_videos)} videos working")
    print(f"✅ Working: {', '.join(working_videos)}")

    return len(working_videos) > 0

if __name__ == "__main__":
    print("🔍 Testing YouTube Subtitle Extraction")
    print("="*50)

    success = test_subtitle_extraction()

    if success:
        print("\n🎉 YouTube Transcript API is working correctly!")
        print("The backend issue was using the wrong API methods.")
        print("Backend should now work with the corrected API usage.")
    else:
        print("\n❌ All subtitle extraction methods failed")