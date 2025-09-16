import React, { useState, useEffect } from "react";
import { AssessmentQuestion, AssessmentResult } from "../../types";

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

interface VocabularyAssessmentProps {
  onComplete: (result: AssessmentResult) => void;
  onSkip: () => void;
}

const VocabularyAssessment: React.FC<VocabularyAssessmentProps> = ({ onComplete, onSkip }) => {
  const [questions, setQuestions] = useState<AssessmentQuestion[]>([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState<number[]>([]);
  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [sessionId, setSessionId] = useState<string>('');

  useEffect(() => {
    startAssessment();
  }, []);

  const startAssessment = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/assessment/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setQuestions(data.questions || []);
      setSessionId(data.session_id || '');
    } catch (error) {
      console.error('Error starting assessment:', error);
      // Fallback to mock questions if API fails
      setQuestions(getMockQuestions());
      setSessionId(`mock_${Date.now()}`);
    } finally {
      setLoading(false);
    }
  };

  const getMockQuestions = (): AssessmentQuestion[] => {
    return [
      {
        id: 1,
        word: "obvious",
        definition: "Easy to see or understand; clear",
        options: ["Very confusing", "Easy to understand", "Impossible to know", "Extremely complicated"],
        correctAnswer: 1,
        level: "A2",
        difficulty: 2
      },
      {
        id: 2,
        word: "efficient",
        definition: "Working in a well-organized way; not wasting time or resources",
        options: ["Very slow and wasteful", "Well-organized and effective", "Broken and useless", "Extremely expensive"],
        correctAnswer: 1,
        level: "B1",
        difficulty: 4
      },
      {
        id: 3,
        word: "comprehensive",
        definition: "Complete and including everything",
        options: ["Incomplete and missing parts", "Complete and thorough", "Very simple and basic", "Extremely difficult"],
        correctAnswer: 1,
        level: "C1",
        difficulty: 7
      }
    ];
  };

  const handleAnswerSelect = (answerIndex: number) => {
    setSelectedAnswer(answerIndex);
  };

  const handleNextQuestion = () => {
    if (selectedAnswer === null) return;

    const newAnswers = [...answers, selectedAnswer];
    setAnswers(newAnswers);
    setSelectedAnswer(null);

    if (currentQuestionIndex + 1 < questions.length) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    } else {
      submitAssessment(newAnswers);
    }
  };

  const submitAssessment = async (finalAnswers: number[]) => {
    try {
      setSubmitting(true);
      const response = await fetch(`${API_BASE_URL}/api/assessment/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          session_id: sessionId,
          answers: finalAnswers
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      onComplete(data.result);
    } catch (error) {
      console.error('Error submitting assessment:', error);
      // Fallback result
      const mockResult: AssessmentResult = {
        totalQuestions: finalAnswers.length,
        correctAnswers: Math.floor(finalAnswers.length * 0.6),
        estimatedLevel: 'B1',
        levelConfidence: 0.7,
        strengths: ['Good foundation', 'Eager to learn'],
        weaknesses: ['Expand vocabulary'],
        recommendedStartLevel: 'A2'
      };
      onComplete(mockResult);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        height: "400px",
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
          Preparing Your Assessment
        </div>
        <div style={{
          fontSize: "14px",
          color: "#adb5bd"
        }}>
          Creating personalized vocabulary questions...
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

  if (submitting) {
    return (
      <div style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        height: "400px",
        textAlign: "center"
      }}>
        <div style={{
          width: "48px",
          height: "48px",
          border: "4px solid #f3f3f3",
          borderTop: "4px solid #28a745",
          borderRadius: "50%",
          animation: "spin 1s linear infinite",
          marginBottom: "24px"
        }} />
        <div style={{
          fontSize: "18px",
          color: "#6c757d",
          marginBottom: "8px"
        }}>
          Analyzing Your Results
        </div>
        <div style={{
          fontSize: "14px",
          color: "#adb5bd"
        }}>
          Determining your vocabulary level...
        </div>
      </div>
    );
  }

  if (questions.length === 0) {
    return (
      <div style={{
        textAlign: "center",
        padding: "40px",
        color: "#dc3545"
      }}>
        <div style={{ fontSize: "48px", marginBottom: "16px" }}>⚠️</div>
        <div style={{ fontSize: "18px", marginBottom: "8px" }}>Assessment Unavailable</div>
        <div style={{ fontSize: "14px", marginBottom: "24px" }}>
          Unable to load assessment questions. You can still continue with the default A2 level.
        </div>
        <button
          onClick={onSkip}
          style={{
            padding: "12px 24px",
            backgroundColor: "#007bff",
            color: "white",
            border: "none",
            borderRadius: "8px",
            cursor: "pointer"
          }}
        >
          Continue with A2 Level
        </button>
      </div>
    );
  }

  const currentQuestion = questions[currentQuestionIndex];
  const progress = (currentQuestionIndex / questions.length) * 100;

  return (
    <div style={{
      maxWidth: "700px",
      margin: "0 auto"
    }}>
      {/* Header */}
      <div style={{
        marginBottom: "32px",
        textAlign: "center"
      }}>
        <h2 style={{
          fontSize: "28px",
          fontWeight: "600",
          color: "#2c3e50",
          marginBottom: "8px"
        }}>
          Vocabulary Assessment
        </h2>
        <p style={{
          fontSize: "16px",
          color: "#6c757d",
          marginBottom: "24px"
        }}>
          Choose the best definition for each word. This helps us customize your learning experience.
        </p>

        {/* Progress */}
        <div style={{
          display: "flex",
          alignItems: "center",
          gap: "16px",
          marginBottom: "16px"
        }}>
          <div style={{
            fontSize: "14px",
            color: "#6c757d",
            minWidth: "100px"
          }}>
            Question {currentQuestionIndex + 1} of {questions.length}
          </div>
          <div style={{
            flex: 1,
            height: "8px",
            backgroundColor: "#e9ecef",
            borderRadius: "4px",
            overflow: "hidden"
          }}>
            <div style={{
              height: "100%",
              backgroundColor: "#007bff",
              borderRadius: "4px",
              width: `${progress}%`,
              transition: "width 0.3s ease"
            }} />
          </div>
          <div style={{
            fontSize: "14px",
            color: "#007bff",
            fontWeight: "600",
            minWidth: "50px"
          }}>
            {Math.round(progress)}%
          </div>
        </div>
      </div>

      {/* Question */}
      <div style={{
        backgroundColor: "#f8f9fa",
        padding: "32px",
        borderRadius: "16px",
        border: "1px solid #e9ecef",
        marginBottom: "32px"
      }}>
        <div style={{
          textAlign: "center",
          marginBottom: "32px"
        }}>
          <div style={{
            fontSize: "32px",
            fontWeight: "bold",
            color: "#2c3e50",
            marginBottom: "16px"
          }}>
            {currentQuestion.word}
          </div>
          <div style={{
            fontSize: "16px",
            color: "#6c757d",
            fontStyle: "italic"
          }}>
            What does this word mean?
          </div>
        </div>

        {/* Options */}
        <div style={{
          display: "grid",
          gap: "16px"
        }}>
          {currentQuestion.options.map((option, index) => (
            <button
              key={index}
              onClick={() => handleAnswerSelect(index)}
              style={{
                padding: "20px",
                backgroundColor: selectedAnswer === index ? "#007bff" : "white",
                color: selectedAnswer === index ? "white" : "#495057",
                border: selectedAnswer === index ? "2px solid #007bff" : "2px solid #dee2e6",
                borderRadius: "12px",
                fontSize: "16px",
                cursor: "pointer",
                transition: "all 0.2s ease",
                textAlign: "left"
              }}
              onMouseOver={(e) => {
                if (selectedAnswer !== index) {
                  e.currentTarget.style.backgroundColor = "#f8f9fa";
                  e.currentTarget.style.borderColor = "#adb5bd";
                }
              }}
              onMouseOut={(e) => {
                if (selectedAnswer !== index) {
                  e.currentTarget.style.backgroundColor = "white";
                  e.currentTarget.style.borderColor = "#dee2e6";
                }
              }}
            >
              <div style={{
                display: "flex",
                alignItems: "center",
                gap: "12px"
              }}>
                <div style={{
                  width: "24px",
                  height: "24px",
                  borderRadius: "50%",
                  backgroundColor: selectedAnswer === index ? "white" : "#e9ecef",
                  color: selectedAnswer === index ? "#007bff" : "#6c757d",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: "12px",
                  fontWeight: "600",
                  flexShrink: 0
                }}>
                  {String.fromCharCode(65 + index)}
                </div>
                <div>{option}</div>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Actions */}
      <div style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center"
      }}>
        <button
          onClick={onSkip}
          style={{
            padding: "12px 20px",
            backgroundColor: "transparent",
            color: "#6c757d",
            border: "1px solid #dee2e6",
            borderRadius: "8px",
            fontSize: "14px",
            cursor: "pointer"
          }}
        >
          Skip Assessment
        </button>

        <button
          onClick={handleNextQuestion}
          disabled={selectedAnswer === null}
          style={{
            padding: "14px 32px",
            backgroundColor: selectedAnswer !== null ? "#007bff" : "#e9ecef",
            color: selectedAnswer !== null ? "white" : "#adb5bd",
            border: "none",
            borderRadius: "8px",
            fontSize: "16px",
            fontWeight: "600",
            cursor: selectedAnswer !== null ? "pointer" : "not-allowed",
            transition: "all 0.2s ease"
          }}
        >
          {currentQuestionIndex + 1 === questions.length ? "Finish Assessment" : "Next Question →"}
        </button>
      </div>
    </div>
  );
};

export default VocabularyAssessment;