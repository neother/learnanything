import { useState, useEffect, useCallback } from 'react';
import { UserProfile, LearningProgress } from '../types';
import { ProgressService } from '../services/progressService';

interface UseProgressTrackingProps {
  userProfile: UserProfile | null;
  currentVideoUrl: string;
  isLearningActive: boolean;
}

export const useProgressTracking = ({
  userProfile,
  currentVideoUrl,
  isLearningActive
}: UseProgressTrackingProps) => {
  const [currentProgress, setCurrentProgress] = useState<LearningProgress | null>(null);
  const [sessionStartTime, setSessionStartTime] = useState<Date | null>(null);
  const [sessionWordsLearned, setSessionWordsLearned] = useState<string[]>([]);
  const [sessionDuration, setSessionDuration] = useState(0);

  // Extract video ID from URL
  const extractVideoId = useCallback((url: string): string => {
    try {
      const urlObj = new URL(url);
      if (urlObj.hostname.includes('youtube.com') || urlObj.hostname.includes('youtu.be')) {
        const videoId = urlObj.searchParams.get('v') ||
                       urlObj.pathname.split('/')[1] ||
                       url.split('/').pop() ||
                       url;
        return videoId.replace(/[^a-zA-Z0-9_-]/g, '_');
      }
      return url.replace(/[^a-zA-Z0-9_-]/g, '_');
    } catch {
      return url.replace(/[^a-zA-Z0-9_-]/g, '_');
    }
  }, []);

  // Load progress when video changes
  useEffect(() => {
    if (userProfile && currentVideoUrl) {
      const videoId = extractVideoId(currentVideoUrl);
      const progress = ProgressService.getVideoProgress(userProfile.id, videoId);
      setCurrentProgress(progress);

      console.log('Loaded progress for video:', videoId, progress);
    }
  }, [userProfile, currentVideoUrl, extractVideoId]);

  // Start session timer when learning becomes active
  useEffect(() => {
    if (isLearningActive && !sessionStartTime && userProfile && currentVideoUrl) {
      const startTime = new Date();
      setSessionStartTime(startTime);
      setSessionWordsLearned([]);
      setSessionDuration(0);
      console.log('🕒 Session timer started for learning activity at:', startTime.toLocaleTimeString());
    }
  }, [isLearningActive, sessionStartTime, userProfile, currentVideoUrl]);

  // Update session duration every second when learning is active
  useEffect(() => {
    if (isLearningActive && sessionStartTime) {
      const interval = setInterval(() => {
        const now = new Date();
        const durationMinutes = Math.floor((now.getTime() - sessionStartTime.getTime()) / 1000 / 60);
        setSessionDuration(durationMinutes);
      }, 1000); // Update every second

      return () => clearInterval(interval);
    }
  }, [isLearningActive, sessionStartTime]);

  // Track word learning
  const trackWordLearned = useCallback((word: string) => {
    if (!sessionWordsLearned.includes(word)) {
      setSessionWordsLearned(prev => [...prev, word]);
      console.log('Tracked new word learned:', word);
    }
  }, [sessionWordsLearned]);

  // Track session completion
  const trackSessionComplete = useCallback((
    sessionNumber: number,
    totalSessions: number,
    videoTitle?: string
  ) => {
    if (!userProfile || !currentVideoUrl) return null;

    const videoId = extractVideoId(currentVideoUrl);
    const now = new Date();
    const sessionDuration = sessionStartTime
      ? Math.floor((now.getTime() - sessionStartTime.getTime()) / 1000 / 60) // minutes
      : 0;

    const progressUpdate: Partial<LearningProgress> = {
      videoTitle: videoTitle || `Video ${videoId}`,
      totalSessions,
      completedSessions: sessionNumber,
      currentSessionIndex: sessionNumber,
      wordsLearned: sessionWordsLearned,
      timeSpent: sessionDuration,
      progress: (sessionNumber / totalSessions)
    };

    const updatedProgress = ProgressService.saveLearningProgress(
      userProfile.id,
      videoId,
      progressUpdate
    );

    if (updatedProgress) {
      setCurrentProgress(updatedProgress);
    }

    // Reset session tracking
    setSessionStartTime(new Date());
    setSessionWordsLearned([]);

    console.log('Session completed:', { sessionNumber, totalSessions, wordsLearned: sessionWordsLearned.length });
    return updatedProgress;
  }, [userProfile, currentVideoUrl, sessionStartTime, sessionWordsLearned, extractVideoId]);

  // Track video completion
  const trackVideoComplete = useCallback((videoTitle?: string) => {
    if (!userProfile || !currentVideoUrl) return null;

    const videoId = extractVideoId(currentVideoUrl);
    const now = new Date();
    const sessionDuration = sessionStartTime
      ? Math.floor((now.getTime() - sessionStartTime.getTime()) / 1000 / 60)
      : 0;

    const progressUpdate: Partial<LearningProgress> = {
      videoTitle: videoTitle || `Video ${videoId}`,
      progress: 1.0,
      timeSpent: sessionDuration,
      wordsLearned: sessionWordsLearned
    };

    const updatedProgress = ProgressService.saveLearningProgress(
      userProfile.id,
      videoId,
      progressUpdate
    );

    if (updatedProgress) {
      setCurrentProgress(updatedProgress);
    }

    console.log('Video completed:', videoId);
    return updatedProgress;
  }, [userProfile, currentVideoUrl, sessionStartTime, sessionWordsLearned, extractVideoId]);

  // Get user analytics
  const getAnalytics = useCallback(() => {
    if (!userProfile) return null;
    return ProgressService.getLearningAnalytics(userProfile.id);
  }, [userProfile]);

  // Update session progress (for real-time tracking)
  const updateSessionProgress = useCallback((
    sessionNumber: number,
    totalSessions: number,
    wordsInSession: string[] = []
  ) => {
    if (!userProfile || !currentVideoUrl) return;

    const videoId = extractVideoId(currentVideoUrl);

    // Add new words to session tracking
    const newWords = wordsInSession.filter(word => !sessionWordsLearned.includes(word));
    if (newWords.length > 0) {
      setSessionWordsLearned(prev => [...prev, ...newWords]);
    }

    const currentTime = new Date();
    const sessionDuration = sessionStartTime
      ? Math.floor((currentTime.getTime() - sessionStartTime.getTime()) / 1000 / 60)
      : 0;

    // Update current progress state (don't save to storage yet)
    setCurrentProgress(prev => ({
      videoId,
      videoTitle: prev?.videoTitle || `Video ${videoId}`,
      totalSessions,
      completedSessions: sessionNumber,
      currentSessionIndex: sessionNumber,
      wordsLearned: [...(prev?.wordsLearned || []), ...sessionWordsLearned, ...newWords],
      timeSpent: (prev?.timeSpent || 0) + sessionDuration,
      lastWatched: currentTime,
      progress: sessionNumber / totalSessions
    }));
  }, [userProfile, currentVideoUrl, sessionStartTime, sessionWordsLearned, extractVideoId]);

  return {
    currentProgress,
    trackWordLearned,
    trackSessionComplete,
    trackVideoComplete,
    updateSessionProgress,
    getAnalytics,
    sessionWordsLearned,
    sessionDuration // Use the state variable that updates every second
  };
};