import { useState, useEffect, useCallback } from "react";
import { Vocabulary, Grammar } from "../types";

export const useVideoPlayer = () => {
  const [player, setPlayer] = useState<any>(null);
  const [isPlayerReady, setIsPlayerReady] = useState(false);
  const [currentPlayingWord, setCurrentPlayingWord] = useState<string | null>(null);
  const [playbackTimer, setPlaybackTimer] = useState<NodeJS.Timeout | null>(null);

  // Helper function to check if player is valid and ready
  const isPlayerReadyCheck = (playerObj: any): boolean => {
    if (!playerObj) return false;
    if (typeof playerObj.seekTo !== "function") return false;
    if (typeof playerObj.getPlayerState !== "function") return false;
    if (typeof playerObj.pauseVideo !== "function") return false;
    if (typeof playerObj.playVideo !== "function") return false;

    // Additional check to ensure the player iframe is still valid
    try {
      playerObj.getPlayerState();
      return true;
    } catch (error) {
      console.warn("Player appears to be in invalid state in useVideoPlayer:", error);
      return false;
    }
  };

  // Stop current playback
  const stopCurrentPlayback = useCallback(() => {
    if (playbackTimer) {
      clearTimeout(playbackTimer);
      setPlaybackTimer(null);
    }

    if (isPlayerReadyCheck(player)) {
      try {
        // Check if player is in a valid state before pausing
        const currentState = player.getPlayerState();
        if (currentState === 1) { // Only pause if currently playing
          player.pauseVideo();
        }
      } catch (error) {
        console.warn("Error pausing YouTube player:", error);
      }
    }

    setCurrentPlayingWord(null);
  }, [player, playbackTimer]);

  // Seek to timestamp and play
  const seekToTimestamp = useCallback((item: Vocabulary | Grammar) => {
    if (!isPlayerReadyCheck(player)) {
      console.warn("YouTube player is not ready or has been destroyed");
      return;
    }

    // Support both legacy timestamp and new startTime properties
    const startTime = item.startTime ?? item.timestamp;
    const endTime = item.endTime ?? item.end_time;

    if (typeof startTime !== "number") {
      console.warn("Invalid timestamp for item:", item);
      return;
    }

    // Stop any current playback
    stopCurrentPlayback();

    const wordKey =
      "word" in item
        ? `${item.word}-${startTime}`
        : `${item.concept}-${startTime}`;
    setCurrentPlayingWord(wordKey);

    try {
      player.seekTo(startTime, true);
      player.playVideo();

      // If we have end time, auto-stop at the end
      if (typeof endTime === "number") {
        const duration = (endTime - startTime) * 1000;
        const timer = setTimeout(() => {
          if (isPlayerReadyCheck(player)) {
            try {
              // Check if player is in a valid state before pausing
              const currentState = player.getPlayerState();
              if (currentState === 1) { // Only pause if currently playing
                player.pauseVideo();
              }
            } catch (error) {
              console.warn("Error pausing YouTube player:", error);
            }
          }
          setCurrentPlayingWord(null);
        }, Math.max(duration, 1000));
        setPlaybackTimer(timer);
      }
    } catch (error) {
      console.error("Error seeking to timestamp:", error);
      setCurrentPlayingWord(null);
    }
  }, [player, stopCurrentPlayback]);

  // Handle player ready
  const handlePlayerReady = useCallback((newPlayer: any) => {
    console.log("Video player ready");
    setPlayer(newPlayer);
    setIsPlayerReady(true);
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (playbackTimer) {
        clearTimeout(playbackTimer);
      }
      if (player && typeof player.destroy === "function") {
        try {
          player.destroy();
        } catch (error) {
          console.warn("Error destroying YouTube player:", error);
        }
      }
    };
  }, [player, playbackTimer]);

  // Function to reset player when it becomes invalid
  const resetPlayer = useCallback(() => {
    console.log("🔄 Resetting YouTube player due to corruption");

    // Clear current player
    if (player) {
      try {
        if (typeof player.destroy === "function") {
          player.destroy();
        }
      } catch (error) {
        console.warn("Error destroying corrupted player:", error);
      }
    }

    // Clear playback timer
    if (playbackTimer) {
      clearTimeout(playbackTimer);
      setPlaybackTimer(null);
    }

    // Reset player state
    setPlayer(null);
    setIsPlayerReady(false);
    setCurrentPlayingWord(null);

    console.log("🔄 Player reset complete - VideoPlayer component should reinitialize");
  }, [player, playbackTimer]);

  return {
    player,
    isPlayerReady,
    currentPlayingWord,
    seekToTimestamp,
    stopCurrentPlayback,
    handlePlayerReady,
    setIsPlayerReady,
    resetPlayer,
  };
};