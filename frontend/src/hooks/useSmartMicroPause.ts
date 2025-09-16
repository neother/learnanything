import { useState, useEffect, useCallback, useRef } from "react";
import { Vocabulary, LearningSession, LearningPanelState } from "../types";

interface SmartMicroPauseProps {
  player: any;
  isPlayerReady: boolean;
  currentSession?: LearningSession;
  learningPanelState: LearningPanelState;
  onWordEncountered: (word: Vocabulary) => void;
  onStateChange: (newState: LearningPanelState) => void;
  onPlayerCorrupted?: () => void;
}

export const useSmartMicroPause = ({
  player,
  isPlayerReady,
  currentSession,
  learningPanelState,
  onWordEncountered,
  onStateChange,
  onPlayerCorrupted,
}: SmartMicroPauseProps) => {
  const [isWatching, setIsWatching] = useState(false);
  const [currentWordIndex, setCurrentWordIndex] = useState(0);
  const [nextWordTimestamp, setNextWordTimestamp] = useState<number | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const lastCheckedTime = useRef<number>(0);

  // Helper function to check if player is valid and ready
  const isPlayerReadyCheck = useCallback((playerObj: any): boolean => {
    if (!playerObj) return false;
    if (typeof playerObj.getCurrentTime !== "function") return false;
    if (typeof playerObj.getPlayerState !== "function") return false;
    if (typeof playerObj.pauseVideo !== "function") return false;
    if (typeof playerObj.playVideo !== "function") return false;

    // Additional comprehensive checks to ensure the player iframe is still valid
    try {
      // Test multiple player methods to ensure iframe is responsive
      const playerState = playerObj.getPlayerState();
      const currentTime = playerObj.getCurrentTime();

      // Check if we get valid responses (not undefined/null)
      if (typeof playerState !== 'number' || typeof currentTime !== 'number') {
        console.warn("Player returned invalid state or time values");
        return false;
      }

      return true;
    } catch (error) {
      console.warn("Player appears to be in invalid state:", error);
      return false;
    }
  }, []);

  // Start the smart micro-pause experience
  const startWatching = useCallback(() => {
    console.log("🎬 Starting Smart Micro-Pause experience");

    if (!currentSession || !currentSession.focusWords.length) {
      console.warn("No session or focus words available");
      return;
    }

    if (!isPlayerReadyCheck(player)) {
      console.warn("Player not ready for micro-pause experience");
      return;
    }

    // Sort focus words by timestamp (support both legacy and new property names)
    const sortedWords = [...currentSession.focusWords]
      .filter(word => {
        const startTime = word.startTime ?? word.timestamp;
        const endTime = word.endTime ?? word.end_time;
        return typeof startTime === 'number' && typeof endTime === 'number';
      })
      .sort((a, b) => {
        const aStart = a.startTime ?? a.timestamp;
        const bStart = b.startTime ?? b.timestamp;
        return (aStart || 0) - (bStart || 0);
      });

    if (sortedWords.length === 0) {
      console.warn("No words with timestamps and end_time found");
      return;
    }

    setIsWatching(true);
    setCurrentWordIndex(0);
    // Use endTime/end_time instead of startTime/timestamp to allow complete sentence playback
    const firstWordEndTime = sortedWords[0].endTime ?? sortedWords[0].end_time;
    setNextWordTimestamp(firstWordEndTime || null);
    lastCheckedTime.current = 0;

    // Use session's startTime for consistent positioning
    const startingTimestamp = Math.max(0, currentSession.startTime);

    console.log(`🎬 Session ${currentSession.sessionNumber}: Starting from ${startingTimestamp}s (session start time)`);
    console.log(`📊 Session time range: ${currentSession.startTime}s - ${currentSession.endTime}s`);

    // Seek to determined position and start playback
    try {
      player.seekTo(startingTimestamp, true);
      console.log(`🎬 Video positioned at ${startingTimestamp}s`);

      // Then start playback
      player.playVideo();
      console.log("▶️ Video playback started");
    } catch (error) {
      console.error("Error starting video playback:", error);
    }

    console.log(`🎯 Prepared ${sortedWords.length} focus words for micro-pause`);
    const firstWordStartTime = sortedWords[0].startTime ?? sortedWords[0].timestamp;
    console.log(`⏰ First word "${sortedWords[0].word}" sentence: ${firstWordStartTime}s-${firstWordEndTime}s`);
    console.log(`📊 Smart micro-pause monitoring activated (checking every 200ms)`);
  }, [player, currentSession, isPlayerReadyCheck]);

  // Stop the smart micro-pause experience
  const stopWatching = useCallback(() => {
    console.log("🛑 Stopping Smart Micro-Pause experience");

    setIsWatching(false);
    setCurrentWordIndex(0);
    setNextWordTimestamp(null);

    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  // Continue to next word after practice completion
  const continueToNextWord = useCallback(() => {
    if (!currentSession || !isWatching) return;

    const sortedWords = [...currentSession.focusWords]
      .filter(word => {
        const startTime = word.startTime ?? word.timestamp;
        const endTime = word.endTime ?? word.end_time;
        return typeof startTime === 'number' && typeof endTime === 'number';
      })
      .sort((a, b) => {
        const aStart = a.startTime ?? a.timestamp;
        const bStart = b.startTime ?? b.timestamp;
        return (aStart || 0) - (bStart || 0);
      });

    const currentWord = sortedWords[currentWordIndex];
    const currentWordEndTime = currentWord?.endTime ?? currentWord?.end_time ?? 0;

    // Find next word with adequate time gap (minimum 8 seconds)
    const MIN_GAP_SECONDS = 8.0;
    let nextIndex = currentWordIndex + 1;

    while (nextIndex < sortedWords.length) {
      const candidateWord = sortedWords[nextIndex];
      const candidateStartTime = candidateWord.startTime ?? candidateWord.timestamp ?? 0;

      // Check if there's enough time gap between current word end and next word start
      if (candidateStartTime - currentWordEndTime >= MIN_GAP_SECONDS) {
        break; // Found a good candidate with adequate gap
      } else {
        console.log(`⏭️ Skipping word "${candidateWord.word}" at ${candidateStartTime}s (too close to previous, gap: ${(candidateStartTime - currentWordEndTime).toFixed(1)}s)`);
        nextIndex++; // Skip this word, try next one
      }
    }

    if (nextIndex < sortedWords.length) {
      // Move to next word with adequate gap
      setCurrentWordIndex(nextIndex);
      // Use endTime/end_time for complete sentence playback
      const nextWordEndTime = sortedWords[nextIndex].endTime ?? sortedWords[nextIndex].end_time;
      setNextWordTimestamp(nextWordEndTime || null);
      onStateChange('cruising');

      console.log(`📚 Moving to word "${sortedWords[nextIndex].word}" at ${sortedWords[nextIndex].startTime ?? sortedWords[nextIndex].timestamp}s (gap: ${((sortedWords[nextIndex].startTime ?? sortedWords[nextIndex].timestamp ?? 0) - currentWordEndTime).toFixed(1)}s)`);

      // Resume video playback for continued watching with comprehensive error handling
      if (isPlayerReadyCheck(player)) {
        // Add a delay to let the player settle after state changes
        setTimeout(() => {
          try {
            // Additional safety check before calling playVideo
            const currentState = player.getPlayerState();
            console.log(`🔍 Player state before resume: ${currentState}`);

            // Try to play the video with a gentler approach
            player.playVideo();
            console.log(`▶️ Resuming video playback for next word`);

            // Give it a moment and verify playback started
            setTimeout(() => {
            try {
              const newState = player.getPlayerState();
              if (newState === 1) {
                console.log(`✅ Video playback resumed successfully (state: ${newState})`);
              } else {
                console.warn(`⚠️ Video may not be playing as expected (state: ${newState})`);
              }
            } catch (verifyError) {
              console.warn("Could not verify video playback state:", verifyError);
            }
          }, 500);

          } catch (error) {
            console.error("Error resuming video playback:", error);
            console.warn("🔧 Player iframe became invalid during practice session");

            // Attempt to recover the player by resetting it
            if (onPlayerCorrupted) {
            console.log("🔄 Attempting to recover YouTube player...");

              // Give it a brief moment before resetting to avoid race conditions
              setTimeout(() => {
                onPlayerCorrupted();
                console.log("🔄 Player recovery initiated - video should reappear shortly");
              }, 1000);
            } else {
              // Fallback: continue in background mode
              console.log("📝 Continuing learning session in background mode");
              console.log("💡 Video controls in the player interface can still be used manually");
              console.log("🎯 Smart micro-pause monitoring will resume if player becomes available");
            }
          }
        }, 300); // Delay before attempting playVideo

      } else {
        console.warn("❌ Player validation failed - continuing in background mode");
        console.log("🔧 Learning session continues without auto-playback");
        console.log("💡 You can manually control video playback using the player controls");
      }

      const nextWordStartTime = sortedWords[nextIndex].startTime ?? sortedWords[nextIndex].timestamp;
      console.log(`➡️ Moving to next word: "${sortedWords[nextIndex].word}" sentence: ${nextWordStartTime}s-${nextWordEndTime}s`);
    } else {
      // Session complete
      console.log("🎉 All focus words completed!");
      setIsWatching(false);
      onStateChange('summary');
    }
  }, [currentSession, isWatching, currentWordIndex, onStateChange, player, isPlayerReadyCheck]);

  // Main monitoring effect - checks video time and triggers pauses
  useEffect(() => {
    console.log(`🔍 Monitoring effect: isWatching=${isWatching}, playerReady=${isPlayerReadyCheck(player)}, nextTimestamp=${nextWordTimestamp}`);

    if (currentSession && currentSession.focusWords.length > 0) {
      console.log(`📊 Session data available: ${currentSession.focusWords.length} focus words`);
      console.log(`🎯 Focus words:`, currentSession.focusWords.map(w => {
        const startTime = w.startTime ?? w.timestamp;
        const endTime = w.endTime ?? w.end_time;
        return `"${w.word}" @ ${startTime}s-${endTime}s`;
      }));
      console.log(`📍 Current word index: ${currentWordIndex}`);
    } else {
      console.log(`❌ No session data or focus words available`);
    }

    if (!isWatching || !isPlayerReadyCheck(player) || nextWordTimestamp === null) {
      console.log(`❌ Monitoring not started - conditions not met`);
      return;
    }

    console.log(`✅ Starting video time monitoring for timestamp ${nextWordTimestamp}s`);

    const checkVideoTime = () => {
      try {
        // Re-validate player before each check in case it became invalid
        if (!isPlayerReadyCheck(player)) {
          console.warn("🔧 Player became invalid during monitoring, pausing checks");
          return;
        }

        const currentTime = player.getCurrentTime();
        const playerState = player.getPlayerState();

        // Validate the returned values
        if (typeof currentTime !== 'number' || typeof playerState !== 'number') {
          console.warn("🔧 Player returned invalid data, skipping this check");
          return;
        }

        // Debug logging (only log every 2 seconds to avoid spam)
        if (Math.floor(currentTime) % 2 === 0 && Math.abs(currentTime - lastCheckedTime.current) >= 1.9) {
          console.log(`⏱️ Video time: ${currentTime.toFixed(1)}s, next target: ${nextWordTimestamp}s, state: ${playerState}`);
        }

        // Only check if video is playing (state 1)
        if (playerState !== 1) {
          if (Math.floor(currentTime) % 3 === 0) {
            console.log(`⏸️ Video not playing (state: ${playerState}), skipping time check`);
          }
          return;
        }

        // Avoid checking too frequently (every 0.5 seconds minimum)
        if (Math.abs(currentTime - lastCheckedTime.current) < 0.5) return;

        lastCheckedTime.current = currentTime;

        // Check if we've reached or passed the target end_time (when sentence completes)
        if (currentTime >= nextWordTimestamp - 0.3) { // 0.3s buffer for accuracy
          const sortedWords = [...(currentSession?.focusWords || [])]
            .filter(word => {
              const startTime = word.startTime ?? word.timestamp;
              const endTime = word.endTime ?? word.end_time;
              return typeof startTime === 'number' && typeof endTime === 'number';
            })
            .sort((a, b) => {
              const aStart = a.startTime ?? a.timestamp;
              const bStart = b.startTime ?? b.timestamp;
              return (aStart || 0) - (bStart || 0);
            });

          const targetWord = sortedWords[currentWordIndex];

          if (targetWord) {
            console.log(`⏸️ SMART MICRO-PAUSE: Completed sentence with "${targetWord.word}" at ${currentTime.toFixed(1)}s (target end_time: ${targetWord.end_time}s)`);
            console.log(`📝 Sentence: "${targetWord.sentence || 'N/A'}"`);

            // Pause the video after sentence completion
            try {
              // Only pause if video is currently playing
              const currentPlayerState = player.getPlayerState();
              if (currentPlayerState === 1) { // Playing state
                player.pauseVideo();
                console.log(`⏸️ Video paused successfully`);
              } else {
                console.log(`🔄 Video already paused or not playing (state: ${currentPlayerState})`);
              }
            } catch (error) {
              console.error("Error pausing video in smart micro-pause:", error);
            }

            // Trigger the focus state
            onWordEncountered(targetWord);
            onStateChange('focus');

            // Clear the next word timestamp to prevent repeated triggers
            setNextWordTimestamp(null);
          }
        }

      } catch (error) {
        console.warn("Error checking video time:", error);
      }
    };

    // Set up interval to monitor video time - reduced frequency to prevent iframe corruption
    intervalRef.current = setInterval(checkVideoTime, 1000); // Check every 1000ms (less aggressive)

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };

  }, [isWatching, player, nextWordTimestamp, currentSession, currentWordIndex, onWordEncountered, onStateChange, isPlayerReadyCheck]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  // Auto-start watching when state changes to 'cruising'
  useEffect(() => {
    if (learningPanelState === 'cruising' && !isWatching && currentSession) {
      startWatching();
    } else if (learningPanelState !== 'cruising' && learningPanelState !== 'focus') {
      stopWatching();
    }
  }, [learningPanelState, isWatching, currentSession, startWatching, stopWatching]);

  return {
    isWatching,
    nextWordTimestamp,
    currentWordIndex,
    startWatching,
    stopWatching,
    continueToNextWord,
  };
};