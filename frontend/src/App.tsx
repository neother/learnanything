import React, { useState } from 'react';
import './App.css';

interface Vocabulary {
  word: string;
  definition: string;
  level: string;
}

interface Grammar {
  concept: string;
  explanation: string;
  level: string;
}

function App() {
  const [vocabulary, setVocabulary] = useState<Vocabulary[]>([]);
  const [grammar, setGrammar] = useState<Grammar[]>([]);
  const [videoUrl, setVideoUrl] = useState('');

  const getYouTubeEmbedUrl = (url: string): string => {
    if (!url) return '';
    
    try {
      // Extract video ID from various YouTube URL formats
      let videoId = '';
      
      if (url.includes('youtube.com/watch?v=')) {
        videoId = url.split('watch?v=')[1].split('&')[0];
      } else if (url.includes('youtu.be/')) {
        videoId = url.split('youtu.be/')[1].split('?')[0];
      } else if (url.includes('youtube.com/embed/')) {
        return url; // Already an embed URL
      }
      
      return videoId ? `https://www.youtube.com/embed/${videoId}` : '';
    } catch (error) {
      console.error('Error parsing YouTube URL:', error);
      return '';
    }
  };

  const extractContent = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/extract-content', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ videoUrl }),
      });
      const data = await response.json();
      setVocabulary(data.vocabulary);
      setGrammar(data.grammar);
    } catch (error) {
      console.error('Error extracting content:', error);
    }
  };

  return (
    <div className="App">
      <div className="main-layout">
        <div className="video-section">
          <h2>YouTube Video</h2>
          <input
            type="text"
            placeholder="e.g. https://www.youtube.com/watch?v=dQw4w9WgXcQ or https://youtu.be/dQw4w9WgXcQ"
            value={videoUrl}
            onChange={(e) => setVideoUrl(e.target.value)}
            className="url-input"
          />
          <button onClick={extractContent} className="extract-btn">
            Extract Content
          </button>
          <div className="video-placeholder">
            {videoUrl && getYouTubeEmbedUrl(videoUrl) ? (
              <iframe
                width="100%"
                height="315"
                src={getYouTubeEmbedUrl(videoUrl)}
                title="YouTube video player"
                frameBorder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              ></iframe>
            ) : videoUrl ? (
              <div className="placeholder-text" style={{color: '#ff6b6b'}}>
                Invalid YouTube URL. Please use a valid YouTube video link.
              </div>
            ) : (
              <div className="placeholder-text">Enter a YouTube URL to display video</div>
            )}
          </div>
        </div>
        
        <div className="content-panel">
          <div className="vocabulary-section">
            <h3>Vocabulary (A1 Level)</h3>
            <div className="content-list">
              {vocabulary.map((item, index) => (
                <div key={index} className="content-item">
                  <strong>{item.word}</strong>
                  <p>{item.definition}</p>
                </div>
              ))}
            </div>
          </div>
          
          <div className="grammar-section">
            <h3>Grammar (A1 Level)</h3>
            <div className="content-list">
              {grammar.map((item, index) => (
                <div key={index} className="content-item">
                  <strong>{item.concept}</strong>
                  <p>{item.explanation}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
