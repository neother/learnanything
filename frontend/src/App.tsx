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
  const playerRef = useRef<HTMLDivElement>(null);

  const getYouTubeVideoId = (url: string): string => {
    if (!url) return "";

    try {
      let videoId = "";

      if (url.includes("youtube.com/watch?v=")) {
        videoId = url.split("watch?v=")[1].split("&")[0];
      } else if (url.includes("youtu.be/")) {
        videoId = url.split("youtu.be/")[1].split("?")[0];
      } else if (url.includes("youtube.com/embed/")) {
        videoId = url.split("embed/")[1].split("?")[0];
      }

      return videoId;
    } catch (error) {
      console.error("Error parsing YouTube URL:", error);
      return "";
    }
  };

  // Load YouTube Player API
  useEffect(() => {
    if (!window.YT) {
      const script = document.createElement("script");
      script.src = "https://www.youtube.com/iframe_api";
      document.body.appendChild(script);

      window.onYouTubeIframeAPIReady = () => {
        setIsPlayerReady(true);
      };
    } else {
      setIsPlayerReady(true);
    }
  }, []);

  // Initialize YouTube Player when API is ready
  useEffect(() => {
    if (isPlayerReady && videoUrl && playerRef.current) {
      const videoId = getYouTubeVideoId(videoUrl);
      if (videoId) {
        console.log("Creating YouTube Player for video:", videoId);

        if (player && player.destroy) {
          player.destroy();
        }

        playerRef.current.innerHTML = "";

        new window.YT.Player(playerRef.current, {
          height: "315",
          width: "100%",
          videoId: videoId,
          playerVars: {
            playsinline: 1,
            rel: 0,
            cc_load_policy: 1,
            modestbranding: 1,
            fs: 1,
            iv_load_policy: 3,
          },
          events: {
            onReady: (event: any) => {
              console.log("YouTube Player Ready for interactive control");
              setPlayer(event.target);
            },
            onStateChange: (event: any) => {
              // Handle player state changes if needed
            },
          },
        });
      }
    }
  }, [isPlayerReady, videoUrl, player]);

  // Cleanup timer on component unmount
  useEffect(() => {
    return () => {
      if (playbackTimer) {
        clearTimeout(playbackTimer);
      }
    };
  }, [playbackTimer]);

  const seekToTimestamp = (item: Vocabulary | Grammar) => {
    if (player && player.seekTo) {
      const wordKey = `${'word' in item ? item.word : item.concept}-${item.timestamp}`;

      // If this word is already playing, stop it
      if (currentPlayingWord === wordKey) {
        stopCurrentPlayback();
        return;
      }

      // Stop any currently playing word
      stopCurrentPlayback();

      const startTime = item.timestamp || 0;
      const endTime = item.end_time;

      // Start playing the new word
      player.seekTo(startTime, true);
      player.playVideo();

      // Set the current playing word
      setCurrentPlayingWord(wordKey);

      // Set up auto-stop timer if we have end time
      if (endTime && endTime > startTime) {
        const duration = (endTime - startTime) * 1000;
        const timer = setTimeout(() => {
          if (player && player.pauseVideo) {
            player.pauseVideo();
          }
          setCurrentPlayingWord(null);
          setPlaybackTimer(null);
        }, duration);

        setPlaybackTimer(timer);
      }
    }
  };

  const stopCurrentPlayback = () => {
    if (playbackTimer) {
      clearTimeout(playbackTimer);
      setPlaybackTimer(null);
    }

    if (player && player.pauseVideo) {
      player.pauseVideo();
    }

    setCurrentPlayingWord(null);
  };

  const filteredVocabulary = vocabulary;
  const filteredGrammar = grammar;

  const extractContent = async () => {
    setLoading(true);
    try {
      console.log("Requesting content extraction for:", videoUrl);
      const response = await fetch(
        "http://192.168.0.66:8000/api/extract-content",
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
      if (data.subtitle_debug) {
        const subtitleWords = data.subtitle_debug
          .map((entry: any) => entry.text)
          .join(" ")
          .replace(/\[Music\]/g, "")
          .split(" ")
          .filter((word: string) => word.length > 0)
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

  const renderVocabularyItem = (item: Vocabulary, index: number) => {
    const wordKey = `${item.word}-${item.timestamp}`;
    const isPlaying = currentPlayingWord === wordKey;

    return (
      <div
        key={index}
        className={`content-item ${item.timestamp !== undefined ? "clickable" : ""}`}
        onClick={() => item.timestamp !== undefined && seekToTimestamp(item)}
        style={{
          cursor: item.timestamp !== undefined ? "pointer" : "default",
          backgroundColor: isPlaying ? "#e8f5e8" : "transparent",
          border: isPlaying ? "2px solid #28a745" : "1px solid #e9ecef",
          transition: "all 0.3s ease",
          transform: isPlaying ? "scale(1.02)" : "scale(1)",
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <strong>{item.word}</strong>
            {isPlaying && (
              <span
                style={{
                  fontSize: "12px",
                  color: "#28a745",
                  fontWeight: "bold",
                  animation: "pulse 1.5s infinite",
                }}
              >
                🔊 Playing
              </span>
            )}
          </div>
          <span
            className={`level-badge level-${item.level.toLowerCase()}`}
            style={{
              fontSize: "12px",
              fontWeight: "bold",
              padding: "2px 6px",
              borderRadius: "10px",
              backgroundColor:
                item.level === "A1"
                  ? "#2ecc71"
                  : item.level === "A2"
                  ? "#3498db"
                  : item.level === "B1"
                  ? "#f39c12"
                  : "#e74c3c",
              color: "white",
            }}
          >
            {item.level}
          </span>
        </div>
        <p>{item.definition}</p>
        {item.timestamp !== undefined && (
          <div>
            <span className="timestamp-indicator">
              🎯 {Math.floor(item.timestamp / 60)}:
              {(item.timestamp % 60).toFixed(0).padStart(2, "0")}
              {item.end_time &&
                ` - ${Math.floor(item.end_time / 60)}:${(
                  item.end_time % 60
                )
                  .toFixed(0)
                  .padStart(2, "0")}`}
              {((item.sentence_duration && item.sentence_duration > 0) ||
                (item.end_time &&
                  item.timestamp &&
                  item.end_time > item.timestamp)) &&
                ` (${Math.round(
                  item.sentence_duration ||
                    (item.end_time && item.timestamp
                      ? item.end_time - item.timestamp
                      : 0) ||
                    0
                )}s)`}
            </span>
            {(item.playback_mode === "sentence_loop" ||
              item.playback_mode === "loop") && (
              <span
                style={{
                  fontSize: "12px",
                  color: "#28a745",
                  fontWeight: "bold",
                  marginLeft: "8px",
                }}
              >
                🔄 Complete Sentence
              </span>
            )}
          </div>
        )}
      </div>
    );
  };

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
          border: isPlaying ? "2px solid #28a745" : "1px solid #e9ecef",
          transition: "all 0.3s ease",
          transform: isPlaying ? "scale(1.02)" : "scale(1)",
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <strong>{item.concept}</strong>
            {isPlaying && (
              <span
                style={{
                  fontSize: "12px",
                  color: "#28a745",
                  fontWeight: "bold",
                  animation: "pulse 1.5s infinite",
                }}
              >
                🔊 Playing
              </span>
            )}
          </div>
          <span
            className={`level-badge level-${item.level.toLowerCase()}`}
            style={{
              fontSize: "12px",
              fontWeight: "bold",
              padding: "2px 6px",
              borderRadius: "10px",
              backgroundColor:
                item.level === "A1"
                  ? "#2ecc71"
                  : item.level === "A2"
                  ? "#3498db"
                  : item.level === "B1"
                  ? "#f39c12"
                  : "#e74c3c",
              color: "white",
            }}
          >
            {item.level}
          </span>
        </div>
        <p>{item.explanation}</p>
        {item.timestamp !== undefined && (
          <div>
            <span className="timestamp-indicator">
              🎯 {Math.floor(item.timestamp / 60)}:
              {(item.timestamp % 60).toFixed(0).padStart(2, "0")}
              {item.end_time &&
                ` - ${Math.floor(item.end_time / 60)}:${(
                  item.end_time % 60
                )
                  .toFixed(0)
                  .padStart(2, "0")}`}
              {((item.sentence_duration && item.sentence_duration > 0) ||
                (item.end_time &&
                  item.timestamp &&
                  item.end_time > item.timestamp)) &&
                ` (${Math.round(
                  item.sentence_duration ||
                    (item.end_time && item.timestamp
                      ? item.end_time - item.timestamp
                      : 0) ||
                    0
                )}s)`}
            </span>
            {(item.playback_mode === "sentence_loop" ||
              item.playback_mode === "loop") && (
              <span
                style={{
                  fontSize: "12px",
                  color: "#28a745",
                  fontWeight: "bold",
                  marginLeft: "8px",
                }}
              >
                🔄 Complete Sentence
              </span>
            )}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="App">
      <div className="main-layout">
        <div className="video-section">
          <input
            type="text"
            placeholder="https://www.youtube.com/watch?v=_lLkyJJm_o4"
            value={videoUrl}
            onChange={(e) => setVideoUrl(e.target.value)}
            className="url-input"
          />
          <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
            <button
              onClick={extractContent}
              className="extract-btn"
              disabled={loading}
              style={{ flex: 1 }}
            >
              {loading ? "Loading..." : "Extract Content"}
            </button>
            <button
              onClick={() => setVideoUrl("https://www.youtube.com/watch?v=_lLkyJJm_o4")}
              className="extract-btn"
              style={{
                backgroundColor: "#2196F3",
                fontSize: "14px",
                padding: "12px 16px",
                whiteSpace: "nowrap"
              }}
            >
              Test Video
            </button>
          </div>

          <div
            className="adaptive-indicator"
            style={{
              marginTop: "15px",
              padding: "10px",
              backgroundColor: "#f8f9fa",
              borderRadius: "5px",
              border: "1px solid #e9ecef",
            }}
          >
            <span
              style={{ fontSize: "14px", fontWeight: "bold", color: "#495057" }}
            >
              🧠 Adaptive Learning: Content optimized for {userLevel} level
            </span>
          </div>
          <div className="video-placeholder">
            {videoUrl && getYouTubeVideoId(videoUrl) ? (
              <div>
                <div ref={playerRef} id="youtube-player"></div>
                {!player && isPlayerReady && (
                  <div className="placeholder-text">
                    Loading interactive video player...
                  </div>
                )}
                <p
                  style={{
                    fontSize: "12px",
                    color: "#2ecc71",
                    marginTop: "10px",
                    fontWeight: "bold",
                  }}
                >
                  🎮 Smart Sentence Mode: Click vocabulary words to hear
                  complete sentences for better context
                </p>
              </div>
            ) : videoUrl ? (
              <div className="placeholder-text" style={{ color: "#ff6b6b" }}>
                Invalid YouTube URL. Please use a valid YouTube video link.
              </div>
            ) : (
              <div className="placeholder-text">
                Enter a YouTube URL to display video
              </div>
            )}
          </div>
        </div>

        <div className="content-panel">
          <div className="vocabulary-section">
            <h3>
              Vocabulary - {filteredVocabulary.length} words
              <span
                style={{
                  fontSize: "14px",
                  color: "#28a745",
                  fontWeight: "normal",
                  marginLeft: "10px",
                }}
              >
                ✨ Adaptively Selected
              </span>
            </h3>
            <div className="content-list">
              {filteredVocabulary.length === 0 ? (
                vocabulary.length === 0 ? (
                  <div className="placeholder-text">
                    Click "Extract Content" to load vocabulary
                  </div>
                ) : (
                  <div className="placeholder-text">
                    No vocabulary found in content
                  </div>
                )
              ) : (
                filteredVocabulary.map((item, index) => renderVocabularyItem(item, index))
              )}
            </div>
          </div>

          <div className="grammar-section">
            <h3>
              Grammar - {filteredGrammar.length} concepts
              <span
                style={{
                  fontSize: "14px",
                  color: "#28a745",
                  fontWeight: "normal",
                  marginLeft: "10px",
                }}
              >
                📝 Context-Aware
              </span>
            </h3>
            <div className="content-list">
              {filteredGrammar.length === 0 ? (
                grammar.length === 0 ? (
                  <div className="placeholder-text">
                    Grammar concepts will appear here
                  </div>
                ) : (
                  <div className="placeholder-text">
                    No grammar patterns found in content
                  </div>
                )
              ) : (
                filteredGrammar.map((item, index) => renderGrammarItem(item, index))
              )}
            </div>
          </div>

          {/* Subtitle Testing Section */}
          {subtitleText && (
            <div
              className="subtitle-section"
              style={{
                marginTop: "20px",
                padding: "15px",
                backgroundColor: "#f8f9fa",
                borderRadius: "8px",
                border: "1px solid #dee2e6",
              }}
            >
              <h3
                style={{
                  fontSize: "16px",
                  marginBottom: "10px",
                  color: "#495057",
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",
                }}
              >
                <span>📝</span>
                First 200 Subtitle Words
                <span
                  style={{
                    fontSize: "12px",
                    backgroundColor: "#28a745",
                    color: "white",
                    padding: "2px 6px",
                    borderRadius: "10px",
                    fontWeight: "normal",
                  }}
                >
                  TESTING
                </span>
              </h3>
              <div
                style={{
                  fontSize: "14px",
                  lineHeight: "1.5",
                  color: "#6c757d",
                  maxHeight: "150px",
                  overflowY: "auto",
                  padding: "10px",
                  backgroundColor: "white",
                  borderRadius: "4px",
                  border: "1px solid #e9ecef",
                }}
              >
                {subtitleText}
              </div>
              <div
                style={{
                  fontSize: "12px",
                  color: "#6c757d",
                  marginTop: "8px",
                  textAlign: "center",
                }}
              >
                Extracted from real YouTube subtitles • Total words:{" "}
                {subtitleText.split(" ").length}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;