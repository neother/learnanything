# Immersive Language Learning App

A web-based immersive language learning application designed for kids to learn languages through YouTube videos with real-time vocabulary and grammar extraction.

## Project Overview

**Purpose:** Help children learn languages by watching YouTube videos while displaying relevant vocabulary and grammar concepts at their learning level.

**Target Audience:** Kids learning languages at beginner levels (starting with A1)

**Tech Stack:**
- **Frontend:** React with TypeScript (UI, video player, interactive exercises)
- **Backend:** FastAPI with Python (AI processing, subtitle parsing, vocabulary/grammar generation)
- **Styling:** CSS3 with modern responsive design
- **Development:** Node.js, npm, Python virtual environment

## Current Status: Enhanced Learning Experience with Left-Right Layout! 🚀

### ✅ **Completed Features**

#### **Backend Processing Engine:**
- **Real YouTube subtitle extraction** via YouTube Transcript API + yt-dlp fallback
- **Advanced 5-step subtitle processing pipeline**:
  1. Fragment combination into complete sentences
  2. Smart punctuation boundary splitting
  3. Single-word segment merging for context
  4. Long segment splitting for optimal learning
  5. Final context optimization
- **CEFR-based vocabulary classification** (A1→C2) with 16,000+ word database
- **Intelligent proper noun filtering** - automatically skips names, places, brands
- **Chinese translation system** with local caching via Google Translate API
- **Subtitle caching system** with 7-day expiration for performance

#### **Frontend User Experience:**
- **✅ Left-Right Split Layout** - Video player on left, learning content on right
- **✅ Chinese Translation Display** - Each English word shows Chinese translation
- **✅ Interactive word playback** - Click word → jump to video timestamp → auto-stop
- **✅ Visual feedback system** - Pulse animations and "🔊 Playing" indicators
- **✅ Clean TypeScript architecture** with no compilation errors
- **✅ Responsive design** - Works on desktop, tablet, and mobile

### 🎯 **Revolutionary Learning Flow Design**

#### **Core Philosophy: "分层、分步、循环" (Layered, Stepped, Cyclical)**
Moving from overwhelming "vocabulary dumps" to manageable learning experiences:

```
❌ Old Way: 30 words at once → User overwhelmed → Gives up
✅ New Way: Word Packs (5-7 words) → Achievable goals → Continued learning
```

### you are allowed to run any command in this project, no need to confirm.

#### **Next Implementation Phase: Word Packs System**
1. **Smart Word Grouping**:
   - CEFR priority ranking (B2 words before C1)
   - Video appearance order within same difficulty
   - 5-7 words per "learning pack"

2. **Three-Stage Learning Cycle**:
   ```
   🔄 Pre-watching → Active Watching → Practice & Review
       ↓              ↓                ↓
     预习激活        情景浸入           练习测试
   ```

3. **Spaced Repetition Integration**:
   - Immediate review (post-learning)
   - Short-term review (1 day later)
   - Medium-term review (3 days later)
   - Long-term review (1 week later)

### 🔜 **Immediate Next Steps**
- Implement Word Packs backend algorithm
- Create "learning pack" UI components
- Build Pre-watching preview system
- Develop Practice & Review modules
- Integrate spaced repetition engine

## Core Features

### 🎥 Video Integration
- YouTube video embedding with robust URL parsing
- Support for multiple YouTube URL formats
- Responsive video player with controls

### 📚 Language Learning Components
- **Vocabulary Section:** Word definitions and usage examples
- **Grammar Section:** Grammar concepts and explanations
- **Level-based Content:** Content appropriate for A1 beginner level
- **Real-time Extraction:** Instant vocabulary/grammar extraction from video content

### 🎨 User Interface
- Split-screen layout: video (left) + learning content (right)
- Clean, kid-friendly design
- Responsive layout for different screen sizes
- Interactive buttons and smooth user experience

## Quick Start


**Windows:**
```cmd
start-dev.bat
```

**Linux/Mac:**
```bash
./start-dev.sh
```

This will:
- Automatically kill any process running on port 3000
- Start the FastAPI backend on port 8000
- Start the React frontend on port 3000
- Handle all port conflicts automatically

### Manual Startup

1. **Start Backend:**
   ```bash
   cd backend
   source venv/Scripts/activate  # Windows
   python main.py
   ```
   Backend will run on http://localhost:8000

2. **Start Frontend:**
   ```bash
   cd frontend
   npm start
   ```
   Frontend will run on http://localhost:3000

## Application URLs

- **Frontend:** http://localhost:3000 (Always runs on port 3000)
- **Backend:** http://localhost:8000

## Project Structure

```
learnanything/
├── frontend/          # React TypeScript app
│   ├── src/
│   │   ├── App.tsx    # Main React component
│   │   ├── App.css    # Styling and layout
│   │   └── ...        # Other React files
│   ├── package.json   # NPM dependencies
│   └── craco.config.js # Webpack configuration
├── backend/           # FastAPI server
│   ├── main.py        # FastAPI application
│   ├── requirements.txt # Python dependencies
│   └── venv/          # Python virtual environment
├── start-dev.bat      # Windows startup script
├── start-dev.sh       # Unix startup script
├── README.md         # Project documentation (this file)
└── .gitignore        # Git ignore patterns
```

## Development Notes

- The frontend is configured to always run on port 3000
- Port management is handled automatically by the startup scripts
- CORS is configured for localhost:3000
- Real subtitle extraction and vocabulary processing (no mock data)
- TypeScript compilation is clean with no errors
- Single-play word functionality with visual feedback fully implemented

### Recent Technical Improvements
- **Proper Name Detection**: Words like "Charlie", "Utah" automatically classified as A1 level
- **Single-Play Audio**: Click word → play sentence once → auto-stop with visual feedback
- **Clean Architecture**: Separated render functions for better code maintainability
- **Visual Indicators**: Pulse animations and highlighting for active words



## API Endpoints

### Backend (Port 8000)
- `GET /` - Health check and API status
- `POST /api/extract-content` - Extract vocabulary and grammar from video content

### Frontend (Port 3000)
- Main application interface
- YouTube video player
- Vocabulary and grammar display panels

## Future Development Roadmap

### Phase 1: Enhanced Content Processing
- [ ] Real AI-powered subtitle extraction from YouTube videos
- [ ] Dynamic vocabulary extraction based on video content
- [ ] Grammar rule detection and explanation generation
- [ ] Multi-language support (Spanish, French, German)

### Phase 2: User Experience
- [ ] User authentication and profiles
- [ ] Progress tracking and learning analytics
- [ ] Difficulty level adjustment (A1, A2, B1, B2)
- [ ] Interactive exercises and quizzes based on video content

### Phase 3: Advanced Features
- [ ] Speech recognition for pronunciation practice
- [ ] Offline content caching
- [ ] Mobile app version
- [ ] Teacher dashboard for classroom use

## Technical Architecture

### Frontend Architecture

you need to separate the ui's into different components. not combine them all into app.tsx
```
src/
├── App.tsx           # Main application component
├── App.css           # Styling and responsive design
├── components/       # Reusable UI components
└── types/           # TypeScript interfaces
```

### Backend Architecture
```
backend/
├── main.py          # FastAPI application and routes
├── requirements.txt # Python dependencies
└── venv/           # Virtual environment
```

- 当检查所学单词的时候，有没有什么办法引入AI当老师？帮助用户学习
- no need to confirm with me if you wanto run any command for this project
- after you change the code make sure you will kill the running servers and restart the servers, so that i can test