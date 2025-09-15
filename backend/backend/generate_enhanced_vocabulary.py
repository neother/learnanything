#!/usr/bin/env python3
"""
Enhanced Vocabulary Generator
Converts simple word lists to detailed vocabulary data with meanings, usage, and examples.
"""

import json
import os
import time
import re
from typing import Dict, List, Any

# Enhanced vocabulary data template
def create_enhanced_word_entry(word: str, level: str) -> Dict[str, Any]:
    """Create enhanced vocabulary entry with detailed information"""

    # Predefined translations and explanations for common words
    word_data = {
        # Basic A1 words with detailed information
        "about": {
            "meaning_zh": "关于，大约",
            "meaning_en": "concerning; approximately",
            "pos": ["prep", "adv"],
            "usage": "介词：表示主题或话题（about something）；副词：表示大约的数量或时间（about 10 minutes）",
            "examples": [
                {"en": "This book is about history.", "zh": "这本书是关于历史的。", "level": "A1"},
                {"en": "He arrived at about six o'clock.", "zh": "他大约六点钟到的。", "level": "A2"}
            ],
            "synonyms": ["concerning", "regarding", "approximately"],
            "collocations": ["about time", "about to", "think about", "talk about"]
        },
        "people": {
            "meaning_zh": "人们，人民",
            "meaning_en": "persons; human beings in general",
            "pos": ["n"],
            "usage": "名词：表示一群人或人类整体，通常用复数形式",
            "examples": [
                {"en": "Many people like music.", "zh": "很多人喜欢音乐。", "level": "A1"},
                {"en": "Chinese people are very friendly.", "zh": "中国人很友好。", "level": "A2"}
            ],
            "synonyms": ["persons", "individuals", "folks"],
            "collocations": ["young people", "business people", "local people"]
        },
        "campus": {
            "meaning_zh": "校园，校区",
            "meaning_en": "the grounds and buildings of a university or college",
            "pos": ["n"],
            "usage": "名词：指大学或学院的场地和建筑群",
            "examples": [
                {"en": "The campus is very beautiful.", "zh": "校园非常美丽。", "level": "A2"},
                {"en": "Students live on campus.", "zh": "学生住在校园里。", "level": "B1"}
            ],
            "synonyms": ["university grounds", "college grounds"],
            "collocations": ["on campus", "campus life", "university campus"]
        },
        "from": {
            "meaning_zh": "从，来自",
            "meaning_en": "indicating the point in space at which a journey, motion, or action starts",
            "pos": ["prep"],
            "usage": "介词：表示起点、来源或出发地",
            "examples": [
                {"en": "I come from China.", "zh": "我来自中国。", "level": "A1"},
                {"en": "The train goes from Beijing to Shanghai.", "zh": "火车从北京开往上海。", "level": "A2"}
            ],
            "synonyms": ["out of", "starting at"],
            "collocations": ["from now on", "from time to time", "come from"]
        },
        "said": {
            "meaning_zh": "说过的，据说的",
            "meaning_en": "past tense of say; uttered",
            "pos": ["v"],
            "usage": "动词：say的过去式和过去分词，表示说话的动作已完成",
            "examples": [
                {"en": "He said hello to me.", "zh": "他对我说你好。", "level": "A1"},
                {"en": "She said she would come.", "zh": "她说她会来的。", "level": "A2"}
            ],
            "synonyms": ["told", "spoke", "mentioned"],
            "collocations": ["said that", "as said", "well said"]
        },
        "good": {
            "meaning_zh": "好的，良好的",
            "meaning_en": "having the right or desired qualities; satisfactory",
            "pos": ["adj", "n"],
            "usage": "形容词：表示质量好、令人满意的；名词：表示好处、利益",
            "examples": [
                {"en": "This is a good book.", "zh": "这是一本好书。", "level": "A1"},
                {"en": "Good morning!", "zh": "早上好！", "level": "A1"}
            ],
            "synonyms": ["excellent", "fine", "great"],
            "collocations": ["good morning", "good idea", "feel good"]
        },
        "like": {
            "meaning_zh": "喜欢，像",
            "meaning_en": "find agreeable or satisfactory; similar to",
            "pos": ["v", "prep"],
            "usage": "动词：表示喜欢、欣赏；介词：表示相似或比较",
            "examples": [
                {"en": "I like apples.", "zh": "我喜欢苹果。", "level": "A1"},
                {"en": "She looks like her mother.", "zh": "她看起来像她妈妈。", "level": "A2"}
            ],
            "synonyms": ["enjoy", "love", "similar to"],
            "collocations": ["would like", "look like", "feel like"]
        },
        "time": {
            "meaning_zh": "时间，次数",
            "meaning_en": "the indefinite continued progress of existence; an instance or occasion",
            "pos": ["n", "v"],
            "usage": "名词：表示时间概念或次数；动词：表示计时或选择合适时机",
            "examples": [
                {"en": "What time is it?", "zh": "几点了？", "level": "A1"},
                {"en": "This is the first time.", "zh": "这是第一次。", "level": "A2"}
            ],
            "synonyms": ["moment", "period", "occasion"],
            "collocations": ["on time", "all the time", "have time"]
        },
        "work": {
            "meaning_zh": "工作，起作用",
            "meaning_en": "activity involving effort; function effectively",
            "pos": ["n", "v"],
            "usage": "名词：表示工作、职业；动词：表示工作、运转或起作用",
            "examples": [
                {"en": "I go to work every day.", "zh": "我每天去上班。", "level": "A1"},
                {"en": "Does this machine work?", "zh": "这台机器能用吗？", "level": "A2"}
            ],
            "synonyms": ["job", "labor", "function"],
            "collocations": ["at work", "hard work", "work hard"]
        },
        "home": {
            "meaning_zh": "家，家庭",
            "meaning_en": "the place where one lives; family environment",
            "pos": ["n", "adv"],
            "usage": "名词：表示居住的地方或家庭；副词：表示在家或回家",
            "examples": [
                {"en": "I'm going home.", "zh": "我要回家了。", "level": "A1"},
                {"en": "Home is where the heart is.", "zh": "有爱的地方就是家。", "level": "B1"}
            ],
            "synonyms": ["house", "residence", "family"],
            "collocations": ["at home", "go home", "come home"]
        }
    }

    # Return enhanced data if available, otherwise create basic entry
    if word.lower() in word_data:
        data = word_data[word.lower()].copy()
        data["word"] = word
        data["level"] = level
        return data
    else:
        # Create basic entry for words not in predefined data
        return create_basic_entry(word, level)

def create_basic_entry(word: str, level: str) -> Dict[str, Any]:
    """Create a basic entry for words without predefined data"""
    return {
        "word": word,
        "level": level,
        "meaning_zh": f"{word}的中文意思", # Placeholder for manual translation
        "meaning_en": f"English definition of {word}",
        "pos": ["unknown"],
        "usage": "需要手动添加用法说明",
        "examples": [
            {"en": f"Example sentence with {word}.", "zh": f"包含{word}的例句。", "level": level}
        ],
        "synonyms": [],
        "collocations": []
    }

def convert_vocabulary_file(input_file: str, output_file: str):
    """Convert simple vocabulary list to enhanced format"""

    print(f"Reading vocabulary from: {input_file}")

    # Read the original vocabulary file
    with open(input_file, 'r', encoding='utf-8') as f:
        vocab_data = json.load(f)

    level = vocab_data['level']
    words = vocab_data['words']

    print(f"Processing {len(words)} words for level {level}")

    # Create enhanced vocabulary structure
    enhanced_vocab = {
        "level": level,
        "description": vocab_data.get('description', f'Enhanced vocabulary for level {level}'),
        "total_words": len(words),
        "words": {}
    }

    # Process each word
    processed_count = 0
    for word in words:
        if isinstance(word, str) and word.strip():
            enhanced_entry = create_enhanced_word_entry(word.strip(), level)
            enhanced_vocab["words"][word] = enhanced_entry
            processed_count += 1

            # Show progress
            if processed_count % 50 == 0:
                print(f"Processed {processed_count}/{len(words)} words...")

    # Save enhanced vocabulary
    print(f"Saving enhanced vocabulary to: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(enhanced_vocab, f, ensure_ascii=False, indent=2)

    print(f"✅ Successfully processed {processed_count} words!")
    return enhanced_vocab

def main():
    """Main function to process all vocabulary files"""

    # Define paths
    vocab_dir = "data/vocabulary"
    enhanced_dir = "data/vocabulary_enhanced"

    # Create enhanced directory if it doesn't exist
    os.makedirs(enhanced_dir, exist_ok=True)

    # Process A1 vocabulary first (as example)
    files_to_process = [
        ("a1_words.json", "a1_enhanced.json"),
        # Uncomment to process other levels
        # ("a2_words.json", "a2_enhanced.json"),
        # ("b1_words.json", "b1_enhanced.json"),
    ]

    for input_file, output_file in files_to_process:
        input_path = os.path.join(vocab_dir, input_file)
        output_path = os.path.join(enhanced_dir, output_file)

        if os.path.exists(input_path):
            try:
                print(f"\n{'='*60}")
                print(f"Processing: {input_file}")
                print(f"{'='*60}")

                enhanced_data = convert_vocabulary_file(input_path, output_path)

                # Show summary
                print(f"\nSummary for {input_file}:")
                print(f"- Total words: {enhanced_data['total_words']}")
                print(f"- Level: {enhanced_data['level']}")
                print(f"- Enhanced words: {len(enhanced_data['words'])}")

            except Exception as e:
                print(f"❌ Error processing {input_file}: {e}")
        else:
            print(f"⚠️  File not found: {input_path}")

    print(f"\n✅ Vocabulary enhancement complete!")
    print(f"Enhanced files saved in: {enhanced_dir}")

if __name__ == "__main__":
    main()