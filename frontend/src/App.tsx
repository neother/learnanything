import React, { useState, useRef, useEffect } from "react";
import "./App.css";

// Declare YouTube Player API types
declare global {
  interface Window {
    YT: any;
    onYouTubeIframeAPIReady: () => void;
  }
}

interface Vocabulary {
  word: string;
  definition: string;
  level: string;
  translation?: string;
  sentence?: string;
  timestamp?: number;
  end_time?: number;
  word_timestamp?: number;
  sentence_duration?: number;
  playback_mode?: string;
}

interface Grammar {
  concept: string;
  explanation: string;
  level: string;
  timestamp?: number;
  end_time?: number;
  word_timestamp?: number;
  sentence_duration?: number;
  playback_mode?: string;
}

function App() {
  const [vocabulary, setVocabulary] = useState<Vocabulary[]>([]);
  const [grammar, setGrammar] = useState<Grammar[]>([]);
  const [videoUrl, setVideoUrl] = useState("");
  const [player, setPlayer] = useState<any>(null);
  const [isPlayerReady, setIsPlayerReady] = useState(false);
  const [loading, setLoading] = useState(false);
  const [userLevel, setUserLevel] = useState("A2");
  const [subtitleText, setSubtitleText] = useState("");
  const [currentPlayingWord, setCurrentPlayingWord] = useState<string | null>(null);
  const [playbackTimer, setPlaybackTimer] = useState<NodeJS.Timeout | null>(null);
  const [aiTeacherResponse, setAiTeacherResponse] = useState<string>('');
  const [showAiTeacher, setShowAiTeacher] = useState<boolean>(false);
  const [selectedWord, setSelectedWord] = useState<string>('');
  const playerRef = useRef<HTMLDivElement>(null);

  const getYouTubeVideoId = (url: string): string => {
    if (!url) return "";

    const patterns = [
      /(?:https?:\/\/)?(?:www\.)?(?:youtube\.com|youtu\.be)\/(?:watch\?v=|embed\/|v\/)?([a-zA-Z0-9_-]{11})/,
      /(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})/,
      /(?:https?:\/\/)?youtu\.be\/([a-zA-Z0-9_-]{11})/
    ];

    for (const pattern of patterns) {
      const match = url.match(pattern);
      if (match) return match[1];
    }

    return "";
  };

  // Load YouTube API
  useEffect(() => {
    if (!window.YT) {
      const script = document.createElement("script");
      script.src = "https://www.youtube.com/iframe_api";
      script.async = true;
      document.body.appendChild(script);

      window.onYouTubeIframeAPIReady = () => {
        console.log("YouTube API ready");
        setIsPlayerReady(true);
      };
    } else {
      setIsPlayerReady(true);
    }
  }, []);

  // Create YouTube player when API is ready
  useEffect(() => {
    const videoId = getYouTubeVideoId(videoUrl);
    if (isPlayerReady && videoId && playerRef.current) {
      console.log("Creating YouTube player for:", videoId);

      try {
        const newPlayer = new window.YT.Player(playerRef.current, {
          height: "100%",
          width: "100%",
          videoId: videoId,
          playerVars: {
            autoplay: 0,
            controls: 1,
            disablekb: 0,
            fs: 1,
            iv_load_policy: 3,
            modestbranding: 1,
            rel: 0,
            showinfo: 0,
          },
          events: {
            onReady: (event: any) => {
              console.log("Player is ready");
              setPlayer(event.target);
            },
            onError: (event: any) => {
              console.error("YouTube player error:", event.data);
            },
            onStateChange: (event: any) => {
              console.log("Player state changed:", event.data);
            }
          }
        });
      } catch (error) {
        console.error("Error creating YouTube player:", error);
      }
    }
  }, [isPlayerReady, videoUrl]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (player && typeof player.destroy === 'function') {
        try {
          player.destroy();
        } catch (error) {
          console.warn("Error destroying YouTube player:", error);
        }
      }
    };
  }, [player]);

  // Helper function to check if player is valid and ready
  const isPlayerReadyCheck = (playerObj: any): boolean => {
    if (!playerObj) return false;
    if (typeof playerObj.seekTo !== 'function') return false;
    if (typeof playerObj.getPlayerState !== 'function') return false;
    return true;
  };

  const seekToTimestamp = (item: Vocabulary | Grammar) => {
    if (!isPlayerReadyCheck(player)) {
      console.warn("YouTube player is not ready or has been destroyed");
      return;
    }

    if (typeof item.timestamp !== 'number') {
      console.warn("Invalid timestamp for item:", item);
      return;
    }

    // Stop any current playback
    stopCurrentPlayback();

    const wordKey = 'word' in item ? `${item.word}-${item.timestamp}` : `${item.concept}-${item.timestamp}`;
    setCurrentPlayingWord(wordKey);

    try {
      player.seekTo(item.timestamp, true);
      player.playVideo();

      // If we have end time, auto-stop at the end
      if (typeof item.end_time === 'number') {
        const startTime = item.timestamp;
        const endTime = item.end_time;
        const duration = (endTime - startTime) * 1000;
        const timer = setTimeout(() => {
          if (isPlayerReadyCheck(player)) {
            try {
              player.pauseVideo();
            } catch (error) {
              console.warn("Error pausing YouTube player:", error);
            }
          }
          setCurrentPlayingWord(null);
          setPlaybackTimer(null);
        }, duration);
        setPlaybackTimer(timer);
      }
    } catch (error) {
      console.error("Error seeking to timestamp:", error);
      setCurrentPlayingWord(null);
    }
  };

  const stopCurrentPlayback = () => {
    if (playbackTimer) {
      clearTimeout(playbackTimer);
      setPlaybackTimer(null);
    }

    if (isPlayerReadyCheck(player)) {
      try {
        player.pauseVideo();
      } catch (error) {
        console.warn("Error pausing YouTube player:", error);
      }
    }

    setCurrentPlayingWord(null);
  };

  const callAiTeacher = async (word: string, definition: string, sentence: string) => {
    try {
      console.log("Calling AI Teacher for word:", word);

      const response = await fetch("http://192.168.0.170:8000/api/ai-teacher", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          word,
          definition,
          sentence
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log("AI Teacher response:", data);

      setSelectedWord(word);
      setAiTeacherResponse(data.ai_response);
      setShowAiTeacher(true);
    } catch (error) {
      console.error("Error calling AI Teacher:", error);
      alert("AI老师暂时不可用，请稍后再试！");
    }
  };

  const filteredVocabulary = vocabulary;
  const filteredGrammar = grammar;

  const extractContent = async () => {
    setLoading(true);
    try {
      console.log("Requesting content extraction for:", videoUrl);
      const response = await fetch(
        "http://192.168.0.170:8000/api/extract-content",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ videoUrl, userLevel }),
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log("Received data:", data);

      if (data.vocabulary) {
        console.log("Setting vocabulary:", data.vocabulary);
        setVocabulary(data.vocabulary);
      }

      if (data.grammar) {
        console.log("Setting grammar:", data.grammar);
        setGrammar(data.grammar);
      }

      // Extract first 200 words from subtitle data for testing
      if (data.subtitles && Array.isArray(data.subtitles)) {
        const subtitleWords = data.subtitles
          .map((sub: any) => sub.text)
          .join(" ")
          .split(" ")
          .slice(0, 200)
          .join(" ");
        setSubtitleText(subtitleWords);
      }
    } catch (error) {
      console.error("Error extracting content:", error);
      alert("Failed to extract content. Check console for details.");
    } finally {
      setLoading(false);
    }
  };

  // Get level color for CEFR levels
  const getLevelColor = (level: string) => {
    const levelColors: { [key: string]: string } = {
      'A1': '#28a745', // Green
      'A2': '#17a2b8', // Cyan
      'B1': '#007bff', // Blue
      'B2': '#6610f2', // Purple
      'C1': '#fd7e14', // Orange
      'C2': '#dc3545'  // Red
    };
    return levelColors[level.toUpperCase()] || '#6c757d';
  };

  // Render vocabulary item with timestamp, translation on same row, and subtitle below
  const renderVocabularyItem = (item: Vocabulary, index: number) => {
    const wordKey = `${item.word}-${item.timestamp}`;
    const isPlaying = currentPlayingWord === wordKey;

    return (
      <div
        key={index}
        className={`content-item ${item.timestamp !== undefined ? "clickable" : ""} ${isPlaying ? "flashing" : ""}`}
        onClick={() => item.timestamp !== undefined && seekToTimestamp(item)}
        style={{
          cursor: item.timestamp !== undefined ? "pointer" : "default",
          padding: "12px",
          borderRadius: "8px",
          border: "1px solid #e0e0e0",
          marginBottom: "8px",
          transition: "all 0.2s ease"
        }}
      >
        {/* First row: Word + Translation + Timestamp + Level */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "4px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <strong style={{ fontSize: "16px", color: "#2c3e50" }}>{item.word}</strong>
            {item.translation && (
              <span style={{ color: "#6c757d", fontSize: "14px" }}>
                ({item.translation})
              </span>
            )}
            {item.timestamp !== undefined && (
              <span style={{
                backgroundColor: "#e74c3c",
                color: "white",
                padding: "2px 6px",
                borderRadius: "4px",
                fontSize: "11px",
                fontWeight: "bold",
                marginLeft: "4px"
              }}>
                {Math.floor(item.timestamp / 60)}:{(item.timestamp % 60).toString().padStart(2, '0')}
              </span>
            )}
            {/* AI Teacher Button */}
            <button
              onClick={(e) => {
                e.stopPropagation();
                callAiTeacher(item.word, item.definition, item.sentence || '');
              }}
              style={{
                backgroundColor: "#28a745",
                color: "white",
                border: "none",
                padding: "2px 6px",
                borderRadius: "4px",
                fontSize: "11px",
                cursor: "pointer",
                marginLeft: "4px"
              }}
              title="AI老师帮助"
            >
              🎓 AI
            </button>
          </div>
          <span className="level-badge" style={{
            backgroundColor: getLevelColor(item.level),
            color: "white",
            padding: "2px 6px",
            borderRadius: "4px",
            fontSize: "12px",
            fontWeight: "bold"
          }}>{item.level}</span>
        </div>

        {/* Second row: Definition */}
        {/* <div className="definition" style={{ color: "#555", fontSize: "14px", marginBottom: "6px" }}>
          {item.definition}
        </div> */}

        {/* Third row: Subtitle sentence with highlighted word */}
        {item.sentence && (
          <div style={{
            padding: "8px",
            backgroundColor: "#f8f9fa",
            borderRadius: "4px",
            fontSize: "13px",
            fontStyle: "italic",
            color: "#666",
            border: "1px solid #e9ecef"
          }}>
            <span dangerouslySetInnerHTML={{
              __html: item.sentence.replace(
                new RegExp(`\\b${item.word}\\b`, 'gi'),
                `<mark style="background-color: #fff3cd; padding: 1px 2px; border-radius: 2px; font-weight: bold;">${item.word}</mark>`
              )
            }} />
          </div>
        )}
      </div>
    );
  };

  // Render grammar item
  const renderGrammarItem = (item: Grammar, index: number) => {
    const grammarKey = `${item.concept}-${item.timestamp}`;
    const isPlaying = currentPlayingWord === grammarKey;

    return (
      <div
        key={index}
        className={`content-item ${item.timestamp !== undefined ? "clickable" : ""}`}
        onClick={() => item.timestamp !== undefined && seekToTimestamp(item)}
        style={{
          cursor: item.timestamp !== undefined ? "pointer" : "default",
          backgroundColor: isPlaying ? "#e8f5e8" : "transparent",
          animation: isPlaying ? "pulse 2s infinite" : "none",
          padding: "12px",
          borderRadius: "8px",
          border: "1px solid #e0e0e0",
          marginBottom: "8px"
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <strong>{item.concept}</strong>
          <span className="level-badge">{item.level}</span>
          {isPlaying && (
            <span style={{
              color: "#28a745",
              fontSize: "12px",
              fontWeight: "bold"
            }}>
              🔊 Playing
            </span>
          )}
        </div>
        <div className="explanation" style={{ marginTop: "4px" }}>
          {item.explanation}
        </div>
      </div>
    );
  };

  return (
    <div className="App">
      {/* Header */}
      <header style={{ padding: "10px 20px", background: "#f8f9fa", borderBottom: "1px solid #ddd" }}>
        <h1 style={{ margin: "0", fontSize: "24px", color: "#333" }}>🎓 Immersive Language Learning</h1>
        <p style={{ margin: "5px 0 0 0", color: "#666", fontSize: "14px" }}>
          Learn languages through YouTube videos with vocabulary and grammar extraction!
        </p>
      </header>

      {/* Main Left-Right Layout */}
      <div className="main-layout">
        {/* Left Side - Video Section */}
        <div className="video-section">
          <h2>📺 Video Player</h2>

          {/* Video Controls */}
          <input
            type="text"
            placeholder="Enter YouTube URL (e.g., https://www.youtube.com/watch?v=VIDEO_ID)"
            value={videoUrl}
            onChange={(e) => setVideoUrl(e.target.value)}
            className="url-input"
          />

          <div style={{ display: "flex", gap: "10px", marginBottom: "15px" }}>
            <button
              onClick={extractContent}
              disabled={loading || !videoUrl.trim()}
              className="extract-btn"
            >
              {loading ? "Processing..." : "Extract Content"}
            </button>
            <button
              onClick={() => setVideoUrl("https://www.youtube.com/watch?v=_lLkyJJm_o4")}
              className="extract-btn"
              style={{ backgroundColor: "#007bff" }}
            >
              Test Video
            </button>
          </div>

          {/* Video Player */}
          <div className="video-placeholder">
            {videoUrl && getYouTubeVideoId(videoUrl) ? (
              <div ref={playerRef} style={{ width: "100%", height: "100%" }}></div>
            ) : (
              <div className="placeholder-text">
                Enter a YouTube URL above to load the video
              </div>
            )}
            {!player && isPlayerReady && (
              <div style={{
                position: "absolute",
                top: "10px",
                right: "10px",
                background: "rgba(0,0,0,0.7)",
                color: "white",
                padding: "5px 10px",
                borderRadius: "5px",
                fontSize: "12px"
              }}>
                YouTube API Ready
              </div>
            )}
          </div>
        </div>

        {/* Right Side - Learning Content Panel */}
        <div className="content-panel">
          {/* Vocabulary Section */}
          <div className="vocabulary-section">
            <h3>📚 Vocabulary ({filteredVocabulary.length})</h3>
            <div className="content-list">
              {filteredVocabulary.length === 0 ? (
                <div style={{ color: "#888", textAlign: "center", padding: "20px" }}>
                  No vocabulary extracted yet. Click "Extract Content" to analyze a video!
                </div>
              ) : (
                filteredVocabulary.map(renderVocabularyItem)
              )}
            </div>
          </div>

          {/* Grammar Section */}
          <div className="grammar-section">
            <h3>📝 Grammar ({filteredGrammar.length})</h3>
            <div className="content-list">
              {filteredGrammar.length === 0 ? (
                <div style={{ color: "#888", textAlign: "center", padding: "20px" }}>
                  No grammar concepts extracted yet. Click "Extract Content" to analyze a video!
                </div>
              ) : (
                filteredGrammar.map(renderGrammarItem)
              )}
            </div>
          </div>
        </div>
      </div>

      {/* AI Teacher Modal */}
      {showAiTeacher && (
        <div style={{
          position: "fixed",
          top: "0",
          left: "0",
          right: "0",
          bottom: "0",
          backgroundColor: "rgba(0,0,0,0.5)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          zIndex: 1000
        }}>
          <div style={{
            backgroundColor: "white",
            padding: "20px",
            borderRadius: "12px",
            maxWidth: "600px",
            maxHeight: "80vh",
            overflow: "auto",
            margin: "20px",
            boxShadow: "0 4px 20px rgba(0,0,0,0.15)"
          }}>
            <div style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: "15px",
              borderBottom: "2px solid #f0f0f0",
              paddingBottom: "10px"
            }}>
              <h3 style={{ margin: "0", color: "#2c3e50" }}>
                🎓 AI老师：{selectedWord}
              </h3>
              <button
                onClick={() => setShowAiTeacher(false)}
                style={{
                  backgroundColor: "#dc3545",
                  color: "white",
                  border: "none",
                  padding: "8px 12px",
                  borderRadius: "6px",
                  cursor: "pointer",
                  fontSize: "14px"
                }}
              >
                关闭
              </button>
            </div>
            <div style={{
              whiteSpace: "pre-line",
              lineHeight: "1.6",
              color: "#333",
              fontSize: "14px"
            }}>
              {aiTeacherResponse}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;