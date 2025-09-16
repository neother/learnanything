import React, { useRef, useEffect } from "react";
import { VideoPlayerProps } from "../../types";

const VideoPlayer: React.FC<VideoPlayerProps> = ({
  videoUrl,
  player,
  isPlayerReady,
  onPlayerReady,
  onSeekToTimestamp,
  currentPlayingWord,
}) => {
  const playerRef = useRef<HTMLDivElement>(null);

  // Extract YouTube video ID
  const getYouTubeVideoId = (url: string): string => {
    if (!url) return "";

    const patterns = [
      /(?:https?:\/\/)?(?:www\.)?(?:youtube\.com|youtu\.be)\/(?:watch\?v=|embed\/|v\/)?([a-zA-Z0-9_-]{11})/,
      /(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})/,
      /(?:https?:\/\/)?youtu\.be\/([a-zA-Z0-9_-]{11})/,
    ];

    for (const pattern of patterns) {
      const match = url.match(pattern);
      if (match) return match[1];
    }

    return "";
  };

  // Load YouTube API script
  useEffect(() => {
    if (!window.YT) {
      const tag = document.createElement("script");
      tag.src = "https://www.youtube.com/iframe_api";
      const firstScriptTag = document.getElementsByTagName("script")[0];
      firstScriptTag.parentNode?.insertBefore(tag, firstScriptTag);

      window.onYouTubeIframeAPIReady = () => {
        console.log("YouTube API ready");
        // Player creation will be handled in the next useEffect
      };
    }
  }, []);

  // Create YouTube player when API is ready
  useEffect(() => {
    const videoId = getYouTubeVideoId(videoUrl);
    if (window.YT && window.YT.Player && videoId && playerRef.current && !player) {
      console.log("Creating YouTube player for:", videoId);

      // Ensure DOM element is properly attached and ready
      const container = playerRef.current;
      if (!container || !container.isConnected) {
        console.warn("Player container not properly attached to DOM, retrying...");
        return;
      }

      // Clear the container and ensure it has proper structure
      container.innerHTML = '';
      container.style.width = '100%';
      container.style.height = '100%';

      // Add a small delay to ensure DOM is fully ready
      const createPlayer = () => {
        try {
          console.log("Initializing YouTube player instance...");
          const newPlayer = new window.YT.Player(container, {
            height: "100%",
            width: "100%",
            videoId: videoId,
            playerVars: {
              autoplay: 0,
              controls: 1,
              disablekb: 0,
              enablejsapi: 1,
              fs: 1,
              rel: 0,
            },
            events: {
              onReady: (event: any) => {
                console.log("✅ YouTube player is ready and attached to DOM");
                onPlayerReady(event.target);
              },
              onError: (event: any) => {
                console.error("YouTube player error:", event.data);
              },
              onStateChange: (event: any) => {
                console.log("Player state changed:", event.data);
              },
            },
          });
        } catch (error) {
          console.error("Error creating YouTube player:", error);
        }
      };

      // Use setTimeout to ensure DOM is fully ready
      setTimeout(createPlayer, 100);
    }
  }, [videoUrl, player, onPlayerReady]);

  // Load new video when URL changes
  useEffect(() => {
    const videoId = getYouTubeVideoId(videoUrl);
    if (player && videoId && player.cueVideoById) {
      console.log("Cueing new video (without autoplay):", videoId);

      // Add a small delay to ensure player is fully attached
      setTimeout(() => {
        try {
          // Verify player is still valid before cueing
          if (player && typeof player.cueVideoById === 'function') {
            player.cueVideoById(videoId);
            console.log("✅ Video cued successfully");
          }
        } catch (error) {
          console.error("Error cueing video:", error);
        }
      }, 200);
    }
  }, [player, videoUrl]);

  return (
    <div className="video-section">
      <h2>📺 Video Player</h2>

      <div className="video-placeholder">
        {videoUrl && getYouTubeVideoId(videoUrl) ? (
          <div
            ref={playerRef}
            style={{ width: "100%", height: "100%" }}
          ></div>
        ) : (
          <div className="placeholder-text">
            Enter a YouTube URL above to load the video
          </div>
        )}
        {!player && isPlayerReady && (
          <div
            style={{
              position: "absolute",
              top: "10px",
              right: "10px",
              background: "rgba(0,0,0,0.7)",
              color: "white",
              padding: "5px 10px",
              borderRadius: "5px",
              fontSize: "12px",
            }}
          >
            YouTube API Ready
          </div>
        )}
        {currentPlayingWord && (
          <div
            style={{
              position: "absolute",
              bottom: "10px",
              left: "10px",
              background: "rgba(40, 167, 69, 0.9)",
              color: "white",
              padding: "5px 10px",
              borderRadius: "5px",
              fontSize: "12px",
              fontWeight: "bold",
            }}
          >
            🔊 Playing: {currentPlayingWord}
          </div>
        )}
      </div>
    </div>
  );
};

export default VideoPlayer;