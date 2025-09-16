const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

// User Profile and Assessment API functions
export const startAssessment = async (): Promise<any> => {
  const response = await fetch(`${API_BASE_URL}/api/assessment/start`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
};

export const submitAssessment = async (sessionId: string, answers: number[]): Promise<any> => {
  const response = await fetch(`${API_BASE_URL}/api/assessment/submit`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      session_id: sessionId,
      answers: answers
    }),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
};

export const createUserProfile = async (name: string, estimatedLevel: string, completedAssessment: boolean): Promise<any> => {
  const response = await fetch(`${API_BASE_URL}/api/profile/create`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      name: name,
      estimatedLevel: estimatedLevel,
      completedAssessment: completedAssessment
    }),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
};

export const getUserProfile = async (userId: string): Promise<any> => {
  const response = await fetch(`${API_BASE_URL}/api/profile/${userId}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
};

export const updateUserProfile = async (userId: string, updates: any): Promise<any> => {
  const response = await fetch(`${API_BASE_URL}/api/profile/update`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      userId: userId,
      updates: updates
    }),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
};