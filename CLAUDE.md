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

## Current Status: MVP

- No authentication/user system required
- Mock data for vocabulary and grammar extraction
- A1 level language support (beginner)
- YouTube video embedding with URL parsing
- Real-time content extraction simulation

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
- Mock data is used for vocabulary and grammar extraction



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

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is in development. License to be determined.

## Contact

For questions or suggestions about this language learning project, please create an issue in the repository.