#!/usr/bin/env python3
"""
Test script for subtitle processing to identify and fix issues
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.main import post_process_subtitles
import re

def test_scenario_1_short_fragments():
    """Test combining short fragments without punctuation"""
    print("\n=== TEST 1: Short fragments (should combine) ===")

    raw_segments = [
        {"text": "in this video let's talk about the", "start": 0.03, "duration": 6.059},
        {"text": "difference between should must and half", "start": 2.129, "duration": 7.321},
        {"text": "this is confusing for many students", "start": 8.5, "duration": 5.2}
    ]

    processed = post_process_subtitles(raw_segments)

    print(f"Raw segments: {len(raw_segments)}")
    print(f"Processed segments: {len(processed)}")

    for i, segment in enumerate(processed):
        print(f"  {i+1}. '{segment['text'][:60]}...' ({segment['duration']:.1f}s)")
        print(f"     Reason: {segment.get('break_reason', 'unknown')}")

    return processed

def test_scenario_2_long_segment():
    """Test handling very long segments (should split)"""
    print("\n=== TEST 2: Very long segment (should split) ===")

    raw_segments = [
        {
            "text": "in this video let's talk about the difference between should must and half - this is a lesson that's been requested by many students and I know this is a confusing topic so I'm happy to make this very clear for you of course my name is Jennifer from j4s English comm and this channel is dedicated to helping you sound like a fluent confident natural English speaker now before we go",
            "start": 0.03,
            "duration": 29.43
        }
    ]

    processed = post_process_subtitles(raw_segments)

    print(f"Raw segments: {len(raw_segments)} (duration: {raw_segments[0]['duration']}s)")
    print(f"Processed segments: {len(processed)}")

    for i, segment in enumerate(processed):
        print(f"  {i+1}. '{segment['text'][:60]}...' ({segment['duration']:.1f}s)")
        print(f"     Reason: {segment.get('break_reason', 'unknown')}")

    return processed

def test_scenario_3_mixed_lengths():
    """Test mixed segment lengths with punctuation"""
    print("\n=== TEST 3: Mixed lengths with punctuation ===")

    raw_segments = [
        {"text": "Hello everyone!", "start": 0.0, "duration": 2.0},
        {"text": "Today we're going to learn about modal verbs.", "start": 2.5, "duration": 4.0},
        {"text": "This includes should must and", "start": 7.0, "duration": 3.0},
        {"text": "have to which are very important", "start": 10.2, "duration": 4.5},
        {"text": "Let's start with should.", "start": 15.0, "duration": 2.5}
    ]

    processed = post_process_subtitles(raw_segments)

    print(f"Raw segments: {len(raw_segments)}")
    print(f"Processed segments: {len(processed)}")

    for i, segment in enumerate(processed):
        print(f"  {i+1}. '{segment['text'][:60]}...' ({segment['duration']:.1f}s)")
        print(f"     Complete: {segment.get('sentence_complete', False)}")
        print(f"     Reason: {segment.get('break_reason', 'unknown')}")

    return processed

def analyze_long_segment_splitting():
    """Analyze if we need to add long segment splitting logic"""
    print("\n=== ANALYSIS: Long Segment Splitting Need ===")

    # Your example: 29.43 second segment
    long_segment = {
        "text": "in this video let's talk about the difference between should must and half - this is a lesson that's been requested by many students and I know this is a confusing topic so I'm happy to make this very clear for you of course my name is Jennifer from j4s English comm and this channel is dedicated to helping you sound like a fluent confident natural English speaker now before we go",
        "start": 0.03,
        "duration": 29.43
    }

    text = long_segment['text']
    duration = long_segment['duration']

    # Analyze text characteristics
    words = text.split()
    sentences_by_punctuation = re.split(r'[.!?]+', text)
    sentences_by_dash = text.split(' - ')

    print(f"Original duration: {duration}s")
    print(f"Total words: {len(words)}")
    print(f"Words per second: {len(words)/duration:.2f}")
    print(f"Sentences by punctuation: {len([s for s in sentences_by_punctuation if s.strip()])}")
    print(f"Segments by dash: {len(sentences_by_dash)}")

    print(f"\nNatural break points found:")
    for i, segment in enumerate(sentences_by_dash):
        if segment.strip():
            print(f"  {i+1}. '{segment.strip()[:50]}...'")

    # Recommendation
    if duration > 15:  # Segments longer than 15s should probably be split
        print(f"\n❌ ISSUE: Segment too long ({duration}s) for effective learning")
        print("✅ SOLUTION: Split by natural breaks (dashes, commas) or time intervals")
    else:
        print(f"\n✅ OK: Segment length acceptable")

def split_long_segment_smart(segment, max_duration=10.0):
    """Smart splitting function for long segments"""
    text = segment['text']
    start_time = segment['start']
    total_duration = segment['duration']

    # Try splitting by natural breaks first
    natural_breaks = [' - ', '. ', '! ', '? ']

    for break_char in natural_breaks:
        if break_char in text:
            parts = text.split(break_char)
            if len(parts) > 1:
                segments = []
                current_time = start_time
                words_per_second = len(text.split()) / total_duration

                for i, part in enumerate(parts):
                    if part.strip():
                        part_words = len(part.split())
                        part_duration = part_words / words_per_second

                        # Add back the break character (except for last part)
                        if i < len(parts) - 1:
                            part += break_char.strip()

                        segments.append({
                            'text': part.strip(),
                            'start': current_time,
                            'duration': part_duration,
                            'end': current_time + part_duration,
                            'split_method': f'natural_break_{break_char.strip()}'
                        })
                        current_time += part_duration

                return segments

    # Fallback: split by time intervals if no natural breaks
    if total_duration > max_duration:
        words = text.split()
        words_per_chunk = int(len(words) * (max_duration / total_duration))

        segments = []
        current_time = start_time

        for i in range(0, len(words), words_per_chunk):
            chunk_words = words[i:i + words_per_chunk]
            chunk_text = ' '.join(chunk_words)
            chunk_duration = min(max_duration, total_duration - (current_time - start_time))

            segments.append({
                'text': chunk_text,
                'start': current_time,
                'duration': chunk_duration,
                'end': current_time + chunk_duration,
                'split_method': 'time_interval'
            })
            current_time += chunk_duration

            if current_time >= start_time + total_duration:
                break

        return segments

    return [segment]  # No splitting needed

def test_smart_splitting():
    """Test the smart splitting function"""
    print("\n=== TEST 4: Smart long segment splitting ===")

    long_segment = {
        "text": "in this video let's talk about the difference between should must and half - this is a lesson that's been requested by many students and I know this is a confusing topic so I'm happy to make this very clear for you of course my name is Jennifer from j4s English comm and this channel is dedicated to helping you sound like a fluent confident natural English speaker now before we go",
        "start": 0.03,
        "duration": 29.43
    }

    split_segments = split_long_segment_smart(long_segment)

    print(f"Original: 1 segment ({long_segment['duration']}s)")
    print(f"After splitting: {len(split_segments)} segments")

    for i, segment in enumerate(split_segments):
        print(f"  {i+1}. '{segment['text'][:50]}...' ({segment['duration']:.1f}s)")
        print(f"     Method: {segment.get('split_method', 'none')}")

if __name__ == "__main__":
    print("🧪 SUBTITLE PROCESSING TESTS")
    print("=" * 50)

    # Run all tests
    test_scenario_1_short_fragments()
    test_scenario_2_long_segment()
    test_scenario_3_mixed_lengths()
    analyze_long_segment_splitting()
    test_smart_splitting()

    print("\n" + "=" * 50)
    print("✅ Tests completed. Review output above for issues.")