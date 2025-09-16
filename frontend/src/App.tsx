import React, { useState, useEffect } from "react";
import "./App.css";
import { Vocabulary, Grammar, LearningPanelState, LearningSession, UserProfile } from "./types";
import VideoPlayer from "./features/VideoPlayer/VideoPlayer";
import LearningPanel from "./features/LearningPanel/LearningPanel";
import Onboarding from "./features/Onboarding/Onboarding";
import Homepage from "./features/Homepage/Homepage";
import AuthModal from "./features/Auth/AuthModal";
import { useVideoPlayer } from "./hooks/useVideoPlayer";
import { useSmartMicroPause } from "./hooks/useSmartMicroPause";
import { useProgressTracking } from "./hooks/useProgressTracking";
import { useAuth } from "./contexts/AuthContext";
import { extractContent, generateSessions, replaceWord } from "./services/api";

function App() {
  // State management
  const [vocabulary, setVocabulary] = useState<Vocabulary[]>([]);
  const [masteredWords, setMasteredWords] = useState<Set<string>>(new Set());
  const [grammar, setGrammar] = useState<Grammar[]>([]);
  const [videoUrl, setVideoUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [userLevel, setUserLevel] = useState("A2");
  const [subtitleText, setSubtitleText] = useState("");

  // Smart Navigator state
  const [learningPanelState, setLearningPanelState] = useState<LearningPanelState>('preview');
  const [currentSession, setCurrentSession] = useState<LearningSession | undefined>();
  const [allSessions, setAllSessions] = useState<LearningSession[]>([]);
  const [currentSessionIndex, setCurrentSessionIndex] = useState(0);
  const [currentWord, setCurrentWord] = useState<Vocabulary | undefined>();
  const [previousWord, setPreviousWord] = useState<Vocabulary | undefined>();

  // Authentication
  const { user, isLoading: authLoading, isAuthenticated } = useAuth();

  // User profile state (backwards compatibility with guest users)
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [profileLoading, setProfileLoading] = useState(true);

  // UI state
  const [currentView, setCurrentView] = useState<'homepage' | 'learning'>('homepage');

  // Smart Navigator event handlers
  const handleStateChange = (newState: LearningPanelState) => {
    console.log(`Learning panel state: ${learningPanelState} → ${newState}`);
    setLearningPanelState(newState);
  };

  // Video player hook
  const {
    player,
    isPlayerReady,
    currentPlayingWord,
    seekToTimestamp,
    handlePlayerReady,
    resetPlayer,
  } = useVideoPlayer();

  // Smart micro-pause hook
  const {
    isWatching,
    continueToNextWord,
    nextWordTimestamp,
    currentWordIndex,
    startWatching,
    stopWatching,
  } = useSmartMicroPause({
    player,
    isPlayerReady,
    currentSession,
    learningPanelState,
    onWordEncountered: (word) => {
      console.log(`🎯 Word encountered: ${word.word}`);
      setCurrentWord(word);
      // Track word learning when encountered
      if (userProfile) {
        progressTracker.trackWordLearned(word.word);
      }
    },
    onStateChange: handleStateChange,
    onPlayerCorrupted: resetPlayer,
  });

  // Progress tracking hook
  const progressTracker = useProgressTracking({
    userProfile,
    currentVideoUrl: videoUrl,
    isLearningActive: learningPanelState === 'cruising'
  });

  // Debug logging for learning activity
  useEffect(() => {
    const isActive = learningPanelState === 'cruising';
    console.log(`🔍 Learning activity: ${isActive ? 'ACTIVE' : 'INACTIVE'} (panel state: ${learningPanelState})`);
    if (isActive && userProfile && videoUrl) {
      console.log(`📊 Progress tracker should be active for user: ${userProfile.name}, video: ${videoUrl.substring(0, 50)}...`);
    }
  }, [learningPanelState, userProfile, videoUrl]);

  // Clean up player when switching views
  useEffect(() => {
    // When switching away from learning view, ensure player is cleaned
    if (currentView === 'homepage' && player) {
      console.log('View changed to homepage - ensuring player cleanup');

      // Small delay to avoid race conditions with the back button handler
      const cleanup = setTimeout(() => {
        if (resetPlayer) {
          resetPlayer();
        }
      }, 100);

      return () => clearTimeout(cleanup);
    }
  }, [currentView, player, resetPlayer]);

  // Load user profile on app start
  useEffect(() => {
    const loadUserProfile = () => {
      if (isAuthenticated && user) {
        // Use authenticated user data
        const profile: UserProfile = {
          id: user.id.toString(),
          name: user.name,
          estimatedLevel: user.estimated_level as any, // Type assertion for CEFR level
          completedAssessment: user.completed_assessment,
          createdAt: new Date(user.created_at),
          lastActiveAt: new Date(user.last_active_at),
          totalStudyTime: user.total_study_time,
          wordsLearned: user.words_learned,
          currentStreak: user.current_streak,
          longestStreak: user.longest_streak
        };
        setUserProfile(profile);
        console.log('Using authenticated user profile:', profile.name);
        setProfileLoading(false);
      } else if (!authLoading && !isAuthenticated) {
        // Try to load guest profile from localStorage
        try {
          const storedProfile = localStorage.getItem('userProfile');
          if (storedProfile) {
            const profile = JSON.parse(storedProfile);
            // Convert string dates back to Date objects
            profile.createdAt = new Date(profile.createdAt);
            profile.lastActiveAt = new Date(profile.lastActiveAt);
            setUserProfile(profile);
            console.log('Loaded guest user profile:', profile.name);
          } else {
            setShowOnboarding(true);
            console.log('No user profile found, showing onboarding');
          }
        } catch (error) {
          console.error('Error loading user profile:', error);
          setShowOnboarding(true);
        } finally {
          setProfileLoading(false);
        }
      }
    };

    if (!authLoading) {
      loadUserProfile();
    }
  }, [isAuthenticated, user, authLoading]);

  // Update user level when profile changes
  useEffect(() => {
    if (userProfile && userProfile.estimatedLevel !== userLevel) {
      setUserLevel(userProfile.estimatedLevel);
      console.log(`Updated user level to: ${userProfile.estimatedLevel}`);
    }
  }, [userProfile, userLevel]);

  // Extract content from video
  const handleExtractContent = async () => {
    setLoading(true);
    try {
      const data = await extractContent(videoUrl, userLevel);

      setVocabulary(data.vocabulary || []);
      setGrammar(data.grammar || []);
      setSubtitleText(data.subtitleText || "");

      // Reset mastered words for new video
      setMasteredWords(new Set());
      console.log("🔄 Reset mastered words for new video");

      // Generate smart learning sessions (Smart Navigator)
      if (data.vocabulary && data.vocabulary.length > 0) {
        console.log("🧠 Generating smart learning sessions...");

        try {
          const sessionData = await generateSessions(data.vocabulary, userLevel, 5);

          // Convert backend sessions to frontend format
          const frontendSessions: LearningSession[] = sessionData.sessions.map((session, index) => {
            // Sort focus words by timestamp to ensure proper order
            const sortedWords = [...session.focus_words].sort((a, b) => {
              const aTime = a.startTime ?? a.timestamp ?? 0;
              const bTime = b.startTime ?? b.timestamp ?? 0;
              return aTime - bTime;
            });

            // Calculate session start and end times
            let sessionStartTime = 0;
            let sessionEndTime = 0;

            if (index === 0) {
              // First session starts from beginning
              sessionStartTime = 0;
            } else {
              // Later sessions start from the end of previous session
              const prevSession = sessionData.sessions[index - 1];
              const prevLastWord = [...prevSession.focus_words].sort((a, b) => {
                const aTime = a.startTime ?? a.timestamp ?? 0;
                const bTime = b.startTime ?? b.timestamp ?? 0;
                return aTime - bTime;
              }).pop();
              sessionStartTime = prevLastWord ? (prevLastWord.endTime ?? prevLastWord.end_time ?? 0) : 0;
            }

            // Session ends at the last word's end time
            const lastWord = sortedWords[sortedWords.length - 1];
            sessionEndTime = lastWord ? (lastWord.endTime ?? lastWord.end_time ?? 0) : sessionStartTime;

            return {
              id: `session-${session.session_id}`,
              videoId: videoUrl,
              sessionNumber: session.session_number,
              totalSessions: session.total_sessions,
              focusWords: sortedWords, // Use sorted words
              status: 'preview' as const,
              startTime: sessionStartTime,
              endTime: sessionEndTime
            };
          });

          setAllSessions(frontendSessions);
          setCurrentSessionIndex(0);
          setCurrentSession(frontendSessions[0]);
          setLearningPanelState('preview');

          console.log(`🎯 Generated ${frontendSessions.length} smart learning sessions`);
          console.log(`📊 Session 1 words:`, frontendSessions[0]?.focusWords.map(w => w.word));

        } catch (sessionError) {
          console.error("Session generation failed, falling back to simple session:", sessionError);

          // Fallback: Create simple session if smart generation fails
          const sessionWords = data.vocabulary.slice(0, Math.min(5, data.vocabulary.length))
            .sort((a, b) => {
              const aTime = a.startTime ?? a.timestamp ?? 0;
              const bTime = b.startTime ?? b.timestamp ?? 0;
              return aTime - bTime;
            });

          const lastWord = sessionWords[sessionWords.length - 1];

          const fallbackSession: LearningSession = {
            id: `session-${Date.now()}`,
            videoId: videoUrl,
            sessionNumber: 1,
            totalSessions: Math.ceil(data.vocabulary.length / 5),
            focusWords: sessionWords,
            status: 'preview',
            startTime: 0,
            endTime: lastWord ? (lastWord.endTime ?? lastWord.end_time ?? 0) : 0
          };

          setCurrentSession(fallbackSession);
          setAllSessions([fallbackSession]);
          setLearningPanelState('preview');
        }
      }

      console.log(`✅ Extracted ${data.vocabulary?.length || 0} vocabulary items and ${data.grammar?.length || 0} grammar items`);
    } catch (error) {
      console.error("Content extraction failed:", error);
      alert(`Content extraction failed: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  const handleWordMastered = async (word: string) => {
    console.log(`Word marked as mastered: ${word}`);

    if (!currentSession || !vocabulary.length) return;

    // Add word to mastered set to prevent it from being used again
    const newMasteredWords = new Set(masteredWords);
    newMasteredWords.add(word);
    setMasteredWords(newMasteredWords);

    // Track the mastered word
    if (userProfile) {
      progressTracker.trackWordLearned(word);
      console.log(`📊 Tracked mastered word: ${word}`);
    }

    try {
      // Filter out mastered words from vocabulary pool
      const availableVocabulary = vocabulary.filter(v => !newMasteredWords.has(v.word));
      console.log(`📝 Available vocabulary pool: ${availableVocabulary.length}/${vocabulary.length} words (excluded ${newMasteredWords.size} mastered)`);

      // If available pool is too small, try with a broader pool but mark the preference
      let vocabularyForReplacement = availableVocabulary;
      let isUsingBroaderPool = false;

      if (availableVocabulary.length < 5) {
        console.log(`⚠️ Available pool too small (${availableVocabulary.length}), using broader vocabulary pool`);
        vocabularyForReplacement = vocabulary; // Use full vocabulary, backend will handle filtering
        isUsingBroaderPool = true;
      }

      // Call smart replacement API with mastered words list
      const masteredWordsArray = Array.from(newMasteredWords);
      const replacementResult = await replaceWord(vocabularyForReplacement, word, currentSession.focusWords, masteredWordsArray);

      console.log(`🔍 Replacement API response:`, {
        replacement_found: replacementResult.replacement_found,
        replacement_word: replacementResult.replacement_word?.word,
        message: replacementResult.message,
        pool_size: vocabularyForReplacement.length,
        used_broader_pool: isUsingBroaderPool
      });

      if (replacementResult.replacement_found && replacementResult.replacement_word) {
        // Replace the mastered word with the new challenge word
        const replacedWords = currentSession.focusWords.map(w =>
          w.word === word ? replacementResult.replacement_word : w
        );

        // Sort by timestamp to maintain proper order
        const sortedWords = replacedWords.sort((a, b) => {
          const aTime = a.startTime ?? a.timestamp ?? 0;
          const bTime = b.startTime ?? b.timestamp ?? 0;
          return aTime - bTime;
        });

        // Recalculate session end time
        const lastWord = sortedWords[sortedWords.length - 1];
        const newEndTime = lastWord ? (lastWord.endTime ?? lastWord.end_time ?? currentSession.endTime) : currentSession.endTime;

        setCurrentSession({
          ...currentSession,
          focusWords: sortedWords,
          endTime: newEndTime
        });

        console.log(`✅ Replaced "${word}" with "${replacementResult.replacement_word.word}" and re-sorted by timestamp`);
      } else {
        // No replacement found - just remove the word
        const filteredWords = currentSession.focusWords.filter(w => w.word !== word);

        // Recalculate session end time
        const lastWord = filteredWords[filteredWords.length - 1];
        const newEndTime = lastWord ? (lastWord.endTime ?? lastWord.end_time ?? currentSession.startTime) : currentSession.startTime;

        setCurrentSession({
          ...currentSession,
          focusWords: filteredWords,
          endTime: newEndTime
        });

        console.log(`🎉 No replacement needed for "${word}" - ${replacementResult.message || 'excellent vocabulary level!'} - recalculated session end time`);
      }

      // Update session progress after word mastery
      if (userProfile && currentSession) {
        const currentWordsInSession = progressTracker.sessionWordsLearned;
        progressTracker.updateSessionProgress(
          currentSession.sessionNumber,
          currentSession.totalSessions,
          currentWordsInSession
        );
      }

    } catch (error) {
      console.error("Smart word replacement failed:", error);

      // Fallback: just remove the word
      const updatedWords = currentSession.focusWords.filter(w => w.word !== word);
      setCurrentSession({
        ...currentSession,
        focusWords: updatedWords
      });

      console.log(`⚠️ Fallback: Removed "${word}" (replacement service unavailable)`);
    }
  };

  const handleStartWatching = () => {
    console.log(`Starting Session ${currentSession?.sessionNumber} watching experience`);
    setLearningPanelState('cruising');

    // Start the smart micro-pause experience
    if (player && isPlayerReady) {
      startWatching();
      console.log("🎬 Smart micro-pause experience started");
    } else {
      console.warn("Player not ready for start watching");
    }
  };

  const handlePracticeComplete = () => {
    console.log("Practice completed for current word");

    // Track word as learned
    if (currentWord) {
      progressTracker.trackWordLearned(currentWord.word);
      setPreviousWord(currentWord);
      setCurrentWord(undefined);
      console.log(`✅ Word "${currentWord.word}" tracked as learned`);
    }

    // Use smart micro-pause to continue to next word
    continueToNextWord();
  };

  const handleNextSession = () => {
    console.log("Moving to next session");

    if (currentSessionIndex + 1 < allSessions.length) {
      const nextIndex = currentSessionIndex + 1;
      setCurrentSessionIndex(nextIndex);
      setCurrentSession(allSessions[nextIndex]);
      setLearningPanelState('preview');

      console.log(`📚 Started Session ${nextIndex + 1}/${allSessions.length}`);
    } else {
      console.log("🎊 All sessions completed!");

      // Track video completion
      if (userProfile && videoUrl) {
        const videoProgress = progressTracker.trackVideoComplete(`Video: ${videoUrl}`);
        console.log("Video completion tracked:", videoProgress);
      }
    }
  };

  const handleSessionComplete = () => {
    console.log("Session completed!");

    // Track session completion
    if (userProfile && currentSession) {
      const sessionProgress = progressTracker.trackSessionComplete(
        currentSession.sessionNumber,
        currentSession.totalSessions,
        `Video: ${videoUrl}`
      );
      console.log("Session progress saved:", sessionProgress);
    }

    setLearningPanelState('summary');
  };

  const handleReplaySegment = (word: Vocabulary) => {
    console.log(`🎬 Replaying segment for word: ${word.word}`);
    if (word.timestamp && word.end_time && player) {
      seekToTimestamp(word);
      // The seekToTimestamp function will handle the replay automatically
    }
  };

  // Onboarding handlers
  const handleOnboardingComplete = (profile: UserProfile) => {
    setUserProfile(profile);
    setShowOnboarding(false);
    console.log('Onboarding completed for:', profile.name);
  };

  const handleOnboardingSkip = () => {
    // Create minimal profile for users who skip onboarding
    const defaultProfile: UserProfile = {
      id: `guest_${Date.now()}`,
      name: 'Guest User',
      estimatedLevel: 'A2',
      completedAssessment: false,
      createdAt: new Date(),
      lastActiveAt: new Date(),
      totalStudyTime: 0,
      wordsLearned: 0,
      currentStreak: 0,
      longestStreak: 0
    };

    localStorage.setItem('userProfile', JSON.stringify(defaultProfile));
    setUserProfile(defaultProfile);
    setShowOnboarding(false);
    console.log('Onboarding skipped, using default profile');
  };

  // Homepage handlers
  const handleVideoSelect = (videoUrl: string) => {
    setVideoUrl(videoUrl);
    setCurrentView('learning');
    console.log('Selected video from homepage:', videoUrl);
  };

  const handleNewVideo = () => {
    setCurrentView('learning');
    console.log('Starting new video learning session');
  };

  const handleBackToHomepage = () => {
    // Clean up video player state when navigating away
    if (player) {
      try {
        if (typeof player.destroy === 'function') {
          player.destroy();
        }
      } catch (error) {
        console.warn('Error destroying player during navigation:', error);
      }
    }

    // Reset player state using the resetPlayer function
    if (resetPlayer) {
      resetPlayer();
    }

    // Clear learning state
    setCurrentSession(undefined);
    setAllSessions([]);
    setLearningPanelState('preview');

    setCurrentView('homepage');
    console.log('Returning to homepage - player state cleaned');
  };

  // Legacy word click handler (will be replaced by smart micro-pause)
  const handleWordClick = (item: Vocabulary | Grammar) => {
    if (learningPanelState === 'cruising' || learningPanelState === 'preview') {
      // Set as current word and switch to focus state
      if ('word' in item) {
        setCurrentWord(item);
        setLearningPanelState('focus');
      }

      // Also seek to timestamp for immediate feedback
      seekToTimestamp(item);
    }
  };

  // Get level color for CEFR levels
  const getLevelColor = (level: string) => {
    const levelColors: { [key: string]: string } = {
      A1: "#28a745", // Green
      A2: "#17a2b8", // Cyan
      B1: "#007bff", // Blue
      B2: "#6610f2", // Purple
      C1: "#fd7e14", // Orange
      C2: "#dc3545", // Red
    };
    return levelColors[level.toUpperCase()] || "#6c757d";
  };

  // Legacy vocabulary item rendering (for fallback)
  const renderVocabularyItem = (item: Vocabulary, index: number) => {
    const wordKey = `${item.word}-${item.timestamp}`;
    const isPlaying = currentPlayingWord === wordKey;

    return (
      <div
        key={index}
        className={`content-item ${item.timestamp !== undefined ? "clickable" : ""} ${isPlaying ? "flashing" : ""}`}
        onClick={() => item.timestamp !== undefined && handleWordClick(item)}
        style={{
          cursor: item.timestamp !== undefined ? "pointer" : "default",
          padding: "12px",
          borderRadius: "8px",
          border: "1px solid #e0e0e0",
          marginBottom: "8px",
          transition: "all 0.2s ease",
        }}
      >
        <div style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          marginBottom: "4px",
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <strong style={{ fontSize: "16px", color: "#2c3e50" }}>
              {item.word}
            </strong>
            {item.translation && (
              <span style={{ color: "#6c757d", fontSize: "14px" }}>
                ({item.translation})
              </span>
            )}
          </div>
          <span
            className="level-badge"
            style={{
              backgroundColor: getLevelColor(item.level),
              color: "white",
              padding: "2px 6px",
              borderRadius: "4px",
              fontSize: "12px",
              fontWeight: "bold",
            }}
          >
            {item.level}
          </span>
        </div>

        {item.sentence && (
          <div style={{
            padding: "8px",
            backgroundColor: "#f8f9fa",
            borderRadius: "4px",
            fontSize: "13px",
            fontStyle: "italic",
            color: "#666",
            border: "1px solid #e9ecef",
          }}>
            <span
              dangerouslySetInnerHTML={{
                __html: item.sentence.replace(
                  new RegExp(`\\b${item.word}\\b`, "gi"),
                  `<mark style="background-color: #fff3cd; padding: 1px 2px; border-radius: 2px; font-weight: bold;">${item.word}</mark>`
                ),
              }}
            />
          </div>
        )}
      </div>
    );
  };

  // Show loading screen while checking authentication and profile
  if (authLoading || profileLoading) {
    return (
      <div style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        height: "100vh",
        backgroundColor: "#f8f9fa",
        textAlign: "center"
      }}>
        <div style={{
          width: "48px",
          height: "48px",
          border: "4px solid #f3f3f3",
          borderTop: "4px solid #007bff",
          borderRadius: "50%",
          animation: "spin 1s linear infinite",
          marginBottom: "24px"
        }} />
        <div style={{
          fontSize: "18px",
          color: "#6c757d",
          marginBottom: "8px"
        }}>
          Loading Smart Navigator
        </div>
        <div style={{
          fontSize: "14px",
          color: "#adb5bd"
        }}>
          Setting up your learning experience...
        </div>
        <style>
          {`
            @keyframes spin {
              0% { transform: rotate(0deg); }
              100% { transform: rotate(360deg); }
            }
          `}
        </style>
      </div>
    );
  }

  // Show onboarding for new users
  if (showOnboarding) {
    return (
      <Onboarding
        onComplete={handleOnboardingComplete}
        onSkip={handleOnboardingSkip}
      />
    );
  }

  return (
    <div className="App">
      {/* Header */}
      <header style={{
        padding: "10px 20px",
        background: "#f8f9fa",
        borderBottom: "1px solid #ddd",
      }}>
        <div style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between"
        }}>
          <div style={{
            display: "flex",
            alignItems: "center",
            gap: "16px"
          }}>
            {currentView === 'learning' && (
              <button
                onClick={handleBackToHomepage}
                style={{
                  padding: "8px 16px",
                  backgroundColor: "transparent",
                  color: "#007bff",
                  border: "1px solid #007bff",
                  borderRadius: "8px",
                  fontSize: "14px",
                  fontWeight: "600",
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",
                  transition: "all 0.2s ease"
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.backgroundColor = "#007bff";
                  e.currentTarget.style.color = "white";
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.backgroundColor = "transparent";
                  e.currentTarget.style.color = "#007bff";
                }}
              >
                ← Back to Home
              </button>
            )}
            <div>
              <h1 style={{ margin: "0", fontSize: "24px", color: "#333" }}>
                🎓 Smart Navigator - Immersive Language Learning
              </h1>
              <p style={{ margin: "5px 0 0 0", color: "#666", fontSize: "14px" }}>
                Transform any YouTube video into your personal language course
              </p>
            </div>
          </div>

          {/* User Profile Info */}
          {userProfile ? (
            <div style={{
              display: "flex",
              alignItems: "center",
              gap: "12px"
            }}>
              <div style={{
                textAlign: "right",
                fontSize: "14px"
              }}>
                <div style={{
                  color: "#2c3e50",
                  fontWeight: "600",
                  display: "flex",
                  alignItems: "center",
                  gap: "4px"
                }}>
                  Welcome, {userProfile.name}!
                  {isAuthenticated ? (
                    <span style={{
                      backgroundColor: "#28a745",
                      color: "white",
                      fontSize: "10px",
                      padding: "2px 6px",
                      borderRadius: "10px",
                      fontWeight: "bold"
                    }}>
                      SYNCED
                    </span>
                  ) : (
                    <span style={{
                      backgroundColor: "#ffc107",
                      color: "#212529",
                      fontSize: "10px",
                      padding: "2px 6px",
                      borderRadius: "10px",
                      fontWeight: "bold"
                    }}>
                      GUEST
                    </span>
                  )}
                </div>
                <div style={{
                  color: "#6c757d",
                  fontSize: "12px"
                }}>
                  Level: {userProfile.estimatedLevel} • Words: {userProfile.wordsLearned}
                </div>
              </div>
              <div style={{
                position: "relative"
              }}>
                <div style={{
                  width: "40px",
                  height: "40px",
                  borderRadius: "50%",
                  backgroundColor: "#007bff",
                  color: "white",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: "16px",
                  fontWeight: "600",
                  cursor: "pointer"
                }}
                onClick={() => setShowAuthModal(true)}
                >
                  {userProfile.name.charAt(0).toUpperCase()}
                </div>
                {!isAuthenticated && (
                  <div style={{
                    position: "absolute",
                    top: "-2px",
                    right: "-2px",
                    width: "12px",
                    height: "12px",
                    backgroundColor: "#ffc107",
                    borderRadius: "50%",
                    border: "2px solid white"
                  }}></div>
                )}
              </div>
            </div>
          ) : (
            <button
              onClick={() => setShowAuthModal(true)}
              style={{
                padding: "8px 16px",
                backgroundColor: "#007bff",
                color: "white",
                border: "none",
                borderRadius: "8px",
                fontSize: "14px",
                fontWeight: "600",
                cursor: "pointer",
                transition: "background-color 0.2s ease"
              }}
              onMouseOver={(e) => e.currentTarget.style.backgroundColor = "#0056b3"}
              onMouseOut={(e) => e.currentTarget.style.backgroundColor = "#007bff"}
            >
              Sign In
            </button>
          )}
        </div>
      </header>

      {/* Main Content */}
      {currentView === 'homepage' ? (
        <Homepage
          userProfile={userProfile!}
          onVideoSelect={handleVideoSelect}
          onNewVideo={handleNewVideo}
        />
      ) : (
        <>
          {/* Main Left-Right Layout */}
          <div className="main-layout">
            {/* Left Side - Video Section */}
            <div className="video-section">
          {/* Video Controls */}
          <div className="video-controls">
            <div className="video-controls-row">
              <input
                type="text"
                value={videoUrl}
                onChange={(e) => setVideoUrl(e.target.value)}
                placeholder="🔗 Paste YouTube URL here..."
                className="video-url-input"
              />
              <select
                value={userLevel}
                onChange={(e) => setUserLevel(e.target.value)}
                className="level-select"
              >
                <option value="A1">🌱 A1 Beginner</option>
                <option value="A2">🌿 A2 Elementary</option>
                <option value="B1">🌳 B1 Intermediate</option>
                <option value="B2">🎯 B2 Upper Intermediate</option>
                <option value="C1">🚀 C1 Advanced</option>
                <option value="C2">⭐ C2 Proficient</option>
              </select>
            </div>

            <div className="video-controls-row">
              <button
                onClick={handleExtractContent}
                disabled={loading || !videoUrl.trim()}
                className="control-button primary"
              >
                {loading ? (
                  <>⏳ Processing...</>
                ) : (
                  <>🎯 Extract Content</>
                )}
              </button>
              <button
                onClick={() => setVideoUrl("https://www.youtube.com/watch?v=_lLkyJJm_o4")}
                className="control-button test1"
              >
                📺 Test Video 1
              </button>
              <button
                onClick={() => setVideoUrl("https://www.youtube.com/watch?v=RBgjzSk_38M")}
                className="control-button test2"
              >
                🎬 Test Video 2
              </button>
            </div>
          </div>

          {/* Video Player Component */}
          <VideoPlayer
            videoUrl={videoUrl}
            player={player}
            isPlayerReady={isPlayerReady}
            onPlayerReady={handlePlayerReady}
            onSeekToTimestamp={seekToTimestamp}
            currentPlayingWord={currentPlayingWord}
          />
        </div>

        {/* Right Side - Learning Panel */}
        <div className="content-panel">
          <LearningPanel
            currentState={learningPanelState}
            session={currentSession}
            currentWord={currentWord}
            previousWord={previousWord}
            onStateChange={handleStateChange}
            onWordMastered={handleWordMastered}
            onStartWatching={handleStartWatching}
            onPracticeComplete={handlePracticeComplete}
            onNextSession={handleNextSession}
            onSessionComplete={handleSessionComplete}
            onReplaySegment={handleReplaySegment}
            nextWordTimestamp={nextWordTimestamp}
            currentWordIndex={currentWordIndex}
            progressData={{
              currentProgress: progressTracker.currentProgress,
              sessionWordsLearned: progressTracker.sessionWordsLearned,
              sessionDuration: progressTracker.sessionDuration
            }}
          />
        </div>
      </div>

      {/* Fallback Legacy Vocabulary Display (for development/debugging) */}
      {process.env.NODE_ENV === 'development' && vocabulary.length > 0 && (
        <div style={{
          padding: "20px",
          borderTop: "2px solid #dee2e6",
          backgroundColor: "#f8f9fa"
        }}>
          <h3>🐛 Debug: Legacy Vocabulary ({vocabulary.length} items)</h3>
          <div style={{ maxHeight: "200px", overflow: "auto" }}>
            {vocabulary.slice(0, 5).map(renderVocabularyItem)}
          </div>
            </div>
          )}
          </>
        )}

        {/* Authentication Modal */}
        <AuthModal
          isOpen={showAuthModal}
          onClose={() => setShowAuthModal(false)}
          onSuccess={() => {
            setShowAuthModal(false);
            // Profile will be updated automatically via useEffect
          }}
          initialData={userProfile ? {
            name: userProfile.name,
            estimatedLevel: userProfile.estimatedLevel
          } : undefined}
        />
      </div>
    );
}

export default App;