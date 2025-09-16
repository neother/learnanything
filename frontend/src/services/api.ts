const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

export interface ExtractContentRequest {
  videoUrl: string;
  userLevel: string;
}

export interface ExtractContentResponse {
  vocabulary: any[];
  grammar: any[];
  subtitleText: string;
}

export const extractContent = async (
  videoUrl: string,
  userLevel: string
): Promise<ExtractContentResponse> => {
  console.log("Requesting content extraction for:", videoUrl);

  const response = await fetch(`${API_BASE_URL}/api/extract-content`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ videoUrl, userLevel }),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return await response.json();
};

export const callAITeacher = async (
  word: string,
  definition: string,
  sentence: string
): Promise<{ response: string }> => {
  console.log("Calling AI Teacher for word:", word);

  const response = await fetch(`${API_BASE_URL}/api/ai-teacher`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      word,
      definition,
      sentence,
    }),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return await response.json();
};

export interface SessionGenerationRequest {
  vocabulary: any[];
  session_size?: number;
  user_level: string;
}

export interface SessionGenerationResponse {
  sessions: any[];
  total_sessions: number;
  total_words: number;
  user_level: string;
  session_size: number;
  generated_at: number;
}

export const generateSessions = async (
  vocabulary: any[],
  userLevel: string,
  sessionSize: number = 5
): Promise<SessionGenerationResponse> => {
  console.log("Generating learning sessions:", { vocabulary_count: vocabulary.length, userLevel, sessionSize });

  const response = await fetch(`${API_BASE_URL}/api/generate-sessions`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      vocabulary,
      user_level: userLevel,
      session_size: sessionSize,
    }),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return await response.json();
};

export interface WordReplacementRequest {
  vocabulary: any[];
  mastered_word: string;
  session_context: any[];
}

export interface WordReplacementResponse {
  replacement_found: boolean;
  replacement_word?: any;
  mastered_word: string;
  message?: string;
  replaced_at: number;
}

export const replaceWord = async (
  vocabulary: any[],
  masteredWord: string,
  sessionContext: any[],
  masteredWords: string[] = []
): Promise<WordReplacementResponse> => {
  console.log("Replacing mastered word:", masteredWord);
  console.log("Excluding mastered words:", masteredWords);

  const response = await fetch(`${API_BASE_URL}/api/replace-word`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      vocabulary,
      mastered_word: masteredWord,
      session_context: sessionContext,
      mastered_words: masteredWords,
    }),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return await response.json();
};