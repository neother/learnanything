const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

// Smart Session API functions for advanced learning features
export interface SmartSessionRequest {
  available_words: Array<{
    word: string;
    level: string;
    definition?: string;
    translation?: string;
    sentence?: string;
    timestamp?: number;
    end_time?: number;
  }>;
  target_session_size?: number;
  difficulty_preference?: 'easier' | 'harder' | null;
}

export interface AdaptiveSessionsRequest {
  available_words: Array<{
    word: string;
    level: string;
    definition?: string;
    translation?: string;
    sentence?: string;
    timestamp?: number;
    end_time?: number;
  }>;
  total_sessions?: number;
  words_per_session?: number;
}

export interface SessionOptimizationRequest {
  current_session: {
    session_id: string;
    focus_words: any[];
    session_number: number;
    total_sessions: number;
  };
  performance_data: {
    mastery_rate: number;
    average_attempts: number;
    session_duration: number;
  };
}

// Helper function to get auth headers
const getAuthHeaders = (): Record<string, string> => {
  const tokens = localStorage.getItem('auth_tokens');
  const headers: Record<string, string> = {
    'Content-Type': 'application/json'
  };

  if (tokens) {
    const { accessToken } = JSON.parse(tokens);
    headers['Authorization'] = `Bearer ${accessToken}`;
  }

  return headers;
};

// Generate a personalized learning session
export const generatePersonalizedSession = async (request: SmartSessionRequest): Promise<any> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/smart-sessions/personalized`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  } catch (error) {
    console.error('Error generating personalized session:', error);
    throw error;
  }
};

// Generate multiple adaptive sessions with progressive difficulty
export const generateAdaptiveSessions = async (request: AdaptiveSessionsRequest): Promise<any> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/smart-sessions/adaptive-series`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  } catch (error) {
    console.error('Error generating adaptive sessions:', error);
    throw error;
  }
};

// Generate spaced repetition review session
export const generateSpacedRepetitionSession = async (reviewType: 'due' | 'overdue' | 'mixed' = 'mixed'): Promise<any> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/smart-sessions/spaced-repetition?review_type=${reviewType}`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  } catch (error) {
    console.error('Error generating spaced repetition session:', error);
    throw error;
  }
};

// Optimize session difficulty based on performance
export const optimizeSessionDifficulty = async (request: SessionOptimizationRequest): Promise<any> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/smart-sessions/optimize`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  } catch (error) {
    console.error('Error optimizing session:', error);
    throw error;
  }
};

// Get personalized learning recommendations
export const getLearningRecommendations = async (): Promise<any> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/smart-sessions/recommendations`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  } catch (error) {
    console.error('Error getting recommendations:', error);
    throw error;
  }
};

// Get user learning analytics
export const getUserLearningAnalytics = async (): Promise<any> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/smart-sessions/user-analytics`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  } catch (error) {
    console.error('Error getting user analytics:', error);
    throw error;
  }
};

// Analytics API functions
export const getAnalyticsSummary = async (): Promise<any> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/analytics/summary`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  } catch (error) {
    console.error('Error getting analytics summary:', error);
    throw error;
  }
};

// Get learning insights with recommendations
export const getLearningInsights = async (days: number = 30): Promise<any> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/analytics/insights?days=${days}`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  } catch (error) {
    console.error('Error getting learning insights:', error);
    throw error;
  }
};

// Start tracking a learning session
export const startLearningSession = async (
  videoUrl: string,
  sessionNumber: number,
  totalSessions: number,
  videoTitle?: string,
  focusWords?: any[]
): Promise<any> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/analytics/sessions/start`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        video_url: videoUrl,
        session_number: sessionNumber,
        total_sessions: totalSessions,
        video_title: videoTitle,
        focus_words: focusWords,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  } catch (error) {
    console.error('Error starting learning session:', error);
    throw error;
  }
};

// Complete a learning session
export const completeLearningSession = async (
  sessionId: number,
  wordsMastered: string[] = [],
  completionPercentage: number = 1.0
): Promise<any> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/analytics/sessions/${sessionId}/complete`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        words_mastered: wordsMastered,
        completion_percentage: completionPercentage,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  } catch (error) {
    console.error('Error completing learning session:', error);
    throw error;
  }
};

// Track word progress
export const trackWordProgress = async (
  word: string,
  cefrLevel: string,
  definition?: string,
  translation?: string,
  sentence?: string,
  videoUrl?: string,
  timestamp?: number,
  sessionId?: number
): Promise<any> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/analytics/words/track`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        word,
        cefr_level: cefrLevel,
        definition,
        translation,
        sentence,
        video_url: videoUrl,
        timestamp,
        session_id: sessionId,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  } catch (error) {
    console.error('Error tracking word progress:', error);
    throw error;
  }
};

// Mark word as mastered
export const markWordMastered = async (word: string): Promise<any> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/analytics/words/${encodeURIComponent(word)}/master`, {
      method: 'PUT',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  } catch (error) {
    console.error('Error marking word as mastered:', error);
    throw error;
  }
};

// Get words for review (spaced repetition)
export const getWordsForReview = async (limit: number = 10): Promise<any> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/analytics/words/review?limit=${limit}`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  } catch (error) {
    console.error('Error getting words for review:', error);
    throw error;
  }
};

// Get comprehensive dashboard data
export const getDashboardData = async (): Promise<any> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/analytics/dashboard`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  } catch (error) {
    console.error('Error getting dashboard data:', error);
    throw error;
  }
};

// Enhanced session generation with smart algorithms
export const generateSmartSessions = async (
  vocabulary: any[],
  userLevel: string,
  maxSessions: number = 5
): Promise<any> => {
  try {
    // First try the smart adaptive sessions
    const adaptiveRequest: AdaptiveSessionsRequest = {
      available_words: vocabulary.map(word => ({
        word: word.word,
        level: word.level,
        definition: word.definition,
        translation: word.translation,
        sentence: word.sentence,
        timestamp: word.timestamp,
        end_time: word.end_time,
      })),
      total_sessions: maxSessions,
      words_per_session: 5,
    };

    const smartSessions = await generateAdaptiveSessions(adaptiveRequest);

    if (smartSessions.success) {
      console.log('🧠 Generated smart adaptive sessions with personalization');
      return smartSessions;
    }

    // Fallback to basic session generation if smart sessions fail
    throw new Error('Smart session generation failed');

  } catch (error) {
    console.warn('Smart session generation failed, falling back to basic generation:', error);

    // Fallback to existing basic session generation
    return fetch(`${API_BASE_URL}/api/generate-sessions`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        vocabulary: vocabulary,
        user_level: userLevel,
        max_sessions: maxSessions,
      }),
    }).then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    });
  }
};