import React from "react";
import { AssessmentResult, CEFRLevel } from "../../types";

interface AssessmentResultsProps {
  result: AssessmentResult;
  onContinue: () => void;
}

const AssessmentResults: React.FC<AssessmentResultsProps> = ({ result, onContinue }) => {
  const getLevelColor = (level: CEFRLevel): string => {
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

  const getLevelDescription = (level: CEFRLevel): string => {
    const descriptions: { [key: string]: string } = {
      A1: "Beginner - Can understand and use familiar everyday expressions",
      A2: "Elementary - Can understand sentences and frequently used expressions",
      B1: "Intermediate - Can understand clear standard speech on familiar matters",
      B2: "Upper Intermediate - Can understand complex texts on abstract topics",
      C1: "Advanced - Can understand demanding longer texts and implicit meaning",
      C2: "Proficient - Can understand virtually everything heard or read"
    };
    return descriptions[level.toUpperCase()] || "Developing vocabulary skills";
  };

  const getScoreEmoji = (accuracy: number): string => {
    if (accuracy >= 0.9) return "🌟";
    if (accuracy >= 0.8) return "🎯";
    if (accuracy >= 0.7) return "💪";
    if (accuracy >= 0.6) return "👍";
    if (accuracy >= 0.5) return "📈";
    return "🌱";
  };

  const accuracy = result.totalQuestions > 0 ? result.correctAnswers / result.totalQuestions : 0;

  return (
    <div style={{
      maxWidth: "600px",
      margin: "0 auto",
      textAlign: "center"
    }}>
      {/* Header */}
      <div style={{
        marginBottom: "40px"
      }}>
        <div style={{
          fontSize: "64px",
          marginBottom: "16px"
        }}>
          {getScoreEmoji(accuracy)}
        </div>
        <h2 style={{
          fontSize: "32px",
          fontWeight: "bold",
          color: "#2c3e50",
          marginBottom: "8px"
        }}>
          Assessment Complete!
        </h2>
        <p style={{
          fontSize: "16px",
          color: "#6c757d"
        }}>
          Here's your personalized learning profile
        </p>
      </div>

      {/* Results Summary */}
      <div style={{
        backgroundColor: "#f8f9fa",
        padding: "32px",
        borderRadius: "16px",
        border: "1px solid #e9ecef",
        marginBottom: "32px"
      }}>
        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))",
          gap: "24px",
          marginBottom: "32px"
        }}>
          <div style={{
            padding: "20px",
            backgroundColor: "white",
            borderRadius: "12px",
            border: "1px solid #dee2e6"
          }}>
            <div style={{
              fontSize: "32px",
              fontWeight: "bold",
              color: "#007bff",
              marginBottom: "8px"
            }}>
              {result.correctAnswers}/{result.totalQuestions}
            </div>
            <div style={{
              fontSize: "14px",
              color: "#6c757d"
            }}>
              Correct Answers
            </div>
          </div>

          <div style={{
            padding: "20px",
            backgroundColor: "white",
            borderRadius: "12px",
            border: "1px solid #dee2e6"
          }}>
            <div style={{
              fontSize: "32px",
              fontWeight: "bold",
              color: getLevelColor(result.estimatedLevel),
              marginBottom: "8px"
            }}>
              {result.estimatedLevel}
            </div>
            <div style={{
              fontSize: "14px",
              color: "#6c757d"
            }}>
              Your Level
            </div>
          </div>

          <div style={{
            padding: "20px",
            backgroundColor: "white",
            borderRadius: "12px",
            border: "1px solid #dee2e6"
          }}>
            <div style={{
              fontSize: "32px",
              fontWeight: "bold",
              color: "#28a745",
              marginBottom: "8px"
            }}>
              {Math.round(result.levelConfidence * 100)}%
            </div>
            <div style={{
              fontSize: "14px",
              color: "#6c757d"
            }}>
              Confidence
            </div>
          </div>
        </div>

        {/* Level Description */}
        <div style={{
          padding: "24px",
          backgroundColor: getLevelColor(result.estimatedLevel),
          color: "white",
          borderRadius: "12px",
          marginBottom: "24px"
        }}>
          <div style={{
            fontSize: "20px",
            fontWeight: "600",
            marginBottom: "8px"
          }}>
            {result.estimatedLevel} Level - {result.estimatedLevel === "A1" ? "Beginner" :
             result.estimatedLevel === "A2" ? "Elementary" :
             result.estimatedLevel === "B1" ? "Intermediate" :
             result.estimatedLevel === "B2" ? "Upper Intermediate" :
             result.estimatedLevel === "C1" ? "Advanced" : "Proficient"}
          </div>
          <div style={{
            fontSize: "14px",
            opacity: 0.9,
            lineHeight: "1.4"
          }}>
            {getLevelDescription(result.estimatedLevel)}
          </div>
        </div>

        {/* Strengths and Weaknesses */}
        <div style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "24px",
          textAlign: "left"
        }}>
          {/* Strengths */}
          <div style={{
            padding: "20px",
            backgroundColor: "white",
            borderRadius: "12px",
            border: "1px solid #dee2e6"
          }}>
            <div style={{
              display: "flex",
              alignItems: "center",
              gap: "8px",
              marginBottom: "16px"
            }}>
              <div style={{ fontSize: "20px" }}>💪</div>
              <div style={{
                fontSize: "16px",
                fontWeight: "600",
                color: "#28a745"
              }}>
                Strengths
              </div>
            </div>
            <ul style={{
              margin: 0,
              padding: "0 0 0 20px",
              listStyle: "none"
            }}>
              {result.strengths.map((strength, index) => (
                <li key={index} style={{
                  fontSize: "14px",
                  color: "#495057",
                  marginBottom: "8px",
                  position: "relative",
                  paddingLeft: "16px"
                }}>
                  <span style={{
                    position: "absolute",
                    left: 0,
                    color: "#28a745"
                  }}>✓</span>
                  {strength}
                </li>
              ))}
            </ul>
          </div>

          {/* Areas for Growth */}
          <div style={{
            padding: "20px",
            backgroundColor: "white",
            borderRadius: "12px",
            border: "1px solid #dee2e6"
          }}>
            <div style={{
              display: "flex",
              alignItems: "center",
              gap: "8px",
              marginBottom: "16px"
            }}>
              <div style={{ fontSize: "20px" }}>🎯</div>
              <div style={{
                fontSize: "16px",
                fontWeight: "600",
                color: "#007bff"
              }}>
                Growth Areas
              </div>
            </div>
            <ul style={{
              margin: 0,
              padding: "0 0 0 20px",
              listStyle: "none"
            }}>
              {result.weaknesses.map((weakness, index) => (
                <li key={index} style={{
                  fontSize: "14px",
                  color: "#495057",
                  marginBottom: "8px",
                  position: "relative",
                  paddingLeft: "16px"
                }}>
                  <span style={{
                    position: "absolute",
                    left: 0,
                    color: "#007bff"
                  }}>→</span>
                  {weakness}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* Recommendation */}
      <div style={{
        backgroundColor: "#e7f3ff",
        padding: "24px",
        borderRadius: "12px",
        border: "1px solid #bee5eb",
        marginBottom: "32px"
      }}>
        <div style={{
          fontSize: "16px",
          fontWeight: "600",
          color: "#0c5460",
          marginBottom: "8px"
        }}>
          📚 Recommended Starting Level: {result.recommendedStartLevel}
        </div>
        <div style={{
          fontSize: "14px",
          color: "#0c5460",
          lineHeight: "1.5"
        }}>
          We'll start your learning journey at the {result.recommendedStartLevel} level to build a strong foundation,
          then gradually introduce {result.estimatedLevel} level vocabulary as you progress.
        </div>
      </div>

      {/* Continue Button */}
      <button
        onClick={onContinue}
        style={{
          padding: "16px 48px",
          backgroundColor: "#007bff",
          color: "white",
          border: "none",
          borderRadius: "12px",
          fontSize: "18px",
          fontWeight: "600",
          cursor: "pointer",
          transition: "all 0.2s ease",
          boxShadow: "0 4px 12px rgba(0,123,255,0.3)"
        }}
        onMouseOver={(e) => {
          e.currentTarget.style.backgroundColor = "#0056b3";
          e.currentTarget.style.transform = "translateY(-2px)";
          e.currentTarget.style.boxShadow = "0 6px 16px rgba(0,123,255,0.4)";
        }}
        onMouseOut={(e) => {
          e.currentTarget.style.backgroundColor = "#007bff";
          e.currentTarget.style.transform = "translateY(0)";
          e.currentTarget.style.boxShadow = "0 4px 12px rgba(0,123,255,0.3)";
        }}
      >
        Continue to Profile Setup →
      </button>
    </div>
  );
};

export default AssessmentResults;