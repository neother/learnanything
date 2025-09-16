// Global type definitions for the Smart Navigator learning system

export interface Vocabulary {
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
  // Consistent naming for focus word timing
  startTime?: number;
  endTime?: number;
  sentence_start_time?: number;
  sentence_end_time?: number;
}

export interface Grammar {
  concept: string;
  explanation: string;
  level: string;
  timestamp?: number;
  end_time?: number;
  word_timestamp?: number;
  sentence_duration?: number;
  playback_mode?: string;
  // Consistent naming for focus concept timing
  startTime?: number;
  endTime?: number;
  sentence_start_time?: number;
  sentence_end_time?: number;
}

// YouTube Player API types
declare global {
  interface Window {
    YT: any;
    onYouTubeIframeAPIReady: () => void;
  }
}

// Learning Session types (for Smart Navigator)
export interface LearningSession {
  id: string;
  videoId: string;
  sessionNumber: number;
  totalSessions: number;
  focusWords: Vocabulary[];
  status: 'preview' | 'in-progress' | 'completed';
  startTime: number; // Session start timestamp in seconds
  endTime: number;   // Session end timestamp in seconds
}

// Learning Panel State types
export type LearningPanelState = 'preview' | 'cruising' | 'focus' | 'summary';

export interface ProgressData {
  currentProgress: LearningProgress | null;
  sessionWordsLearned: string[];
  sessionDuration: number;
}

export interface LearningPanelProps {
  currentState: LearningPanelState;
  session?: LearningSession;
  currentWord?: Vocabulary;
  previousWord?: Vocabulary;
  onStateChange: (newState: LearningPanelState) => void;
  onWordMastered: (word: string) => void;
  onStartWatching: () => void;
  onPracticeComplete: () => void;
  onNextSession?: () => void;
  onSessionComplete?: () => void;
  onReplaySegment?: (word: Vocabulary) => void;
  progressData?: ProgressData;
}

// Video Player types
export interface VideoPlayerProps {
  videoUrl: string;
  player: any;
  isPlayerReady: boolean;
  onPlayerReady: (player: any) => void;
  onSeekToTimestamp: (item: Vocabulary | Grammar) => void;
  currentPlayingWord?: string | null;
}

// User Profile and Onboarding types
export interface UserProfile {
  id: string;
  name: string;
  estimatedLevel: CEFRLevel;
  completedAssessment: boolean;
  createdAt: Date;
  lastActiveAt: Date;
  totalStudyTime: number; // in minutes
  wordsLearned: number;
  currentStreak: number;
  longestStreak: number;
}

export type CEFRLevel = 'A1' | 'A2' | 'B1' | 'B2' | 'C1' | 'C2';

export interface AssessmentQuestion {
  id: number;
  word: string;
  definition: string;
  options: string[];
  correctAnswer: number;
  level: CEFRLevel;
  difficulty: number; // 1-10 scale
}

export interface AssessmentResult {
  totalQuestions: number;
  correctAnswers: number;
  estimatedLevel: CEFRLevel;
  levelConfidence: number; // 0-1 scale
  strengths: string[];
  weaknesses: string[];
  recommendedStartLevel: CEFRLevel;
}

export interface LearningProgress {
  videoId: string;
  videoTitle: string;
  totalSessions: number;
  completedSessions: number;
  currentSessionIndex: number;
  wordsLearned: string[];
  timeSpent: number; // in minutes
  lastWatched: Date;
  progress: number; // 0-1 percentage
}

export interface OnboardingProps {
  onComplete: (profile: UserProfile) => void;
  onSkip: () => void;
}