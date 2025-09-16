import React from "react";
import { LearningSession, ProgressData } from "../../../types";

interface SummaryStateProps {
  session: LearningSession;
  onNextSession?: () => void;
  onReviewSession?: () => void;
  progressData?: ProgressData;
}

const SummaryState: React.FC<SummaryStateProps> = ({
  session,
  onNextSession,
  onReviewSession,
  progressData,
}) => {
  const completedWords = session.focusWords.length;
  const isLastSession = session.sessionNumber >= session.totalSessions;

  return (
    <div className="learning-panel summary-state" style={{
      padding: "24px",
      backgroundColor: "#d4edda",
      border: "2px solid #28a745",
      borderRadius: "12px",
      textAlign: "center"
    }}>
      <div style={{
        fontSize: "48px",
        marginBottom: "16px"
      }}>
        🎉
      </div>

      <h3 style={{
        color: "#155724",
        fontSize: "24px",
        marginBottom: "12px",
        fontWeight: "bold"
      }}>
        Session {session.sessionNumber} Complete!
      </h3>

      <div style={{
        fontSize: "16px",
        color: "#155724",
        marginBottom: "20px",
        lineHeight: "1.5"
      }}>
        Great job! You've learned <strong>{completedWords} new words</strong> in this session.
        {progressData && (
          <>
            <br />
            <span style={{ fontSize: "14px", color: "#6c757d" }}>
              Session time: {progressData.sessionDuration} minutes
            </span>
          </>
        )}
        {!isLastSession && (
          <>
            <br />
            Ready for Session {session.sessionNumber + 1}?
          </>
        )}
      </div>

      {/* Progress indicator */}
      <div style={{
        marginBottom: "24px"
      }}>
        <div style={{
          fontSize: "14px",
          color: "#155724",
          marginBottom: "8px",
          fontWeight: "bold"
        }}>
          Video Progress: {session.sessionNumber}/{session.totalSessions} sessions
        </div>
        <div style={{
          width: "100%",
          height: "8px",
          backgroundColor: "#c3e6cb",
          borderRadius: "4px",
          overflow: "hidden"
        }}>
          <div style={{
            width: `${(session.sessionNumber / session.totalSessions) * 100}%`,
            height: "100%",
            backgroundColor: "#28a745",
            transition: "width 0.5s ease"
          }} />
        </div>
      </div>

      {/* Words learned */}
      <div style={{
        marginBottom: "24px",
        padding: "16px",
        backgroundColor: "white",
        borderRadius: "8px",
        border: "1px solid #c3e6cb"
      }}>
        <div style={{
          fontSize: "14px",
          color: "#155724",
          marginBottom: "12px",
          fontWeight: "bold",
          textTransform: "uppercase",
          letterSpacing: "0.5px"
        }}>
          Words you learned today
        </div>
        <div style={{
          display: "flex",
          flexWrap: "wrap",
          gap: "8px",
          justifyContent: "center"
        }}>
          {session.focusWords.map((word, index) => (
            <span
              key={index}
              style={{
                padding: "6px 12px",
                backgroundColor: "#28a745",
                color: "white",
                borderRadius: "16px",
                fontSize: "14px",
                fontWeight: "bold"
              }}
            >
              {word.word}
            </span>
          ))}
        </div>
      </div>

      {/* Action buttons */}
      <div style={{
        display: "flex",
        gap: "12px",
        justifyContent: "center",
        flexWrap: "wrap"
      }}>
        {onReviewSession && (
          <button
            onClick={onReviewSession}
            style={{
              padding: "12px 20px",
              backgroundColor: "#6c757d",
              color: "white",
              border: "none",
              borderRadius: "8px",
              fontSize: "14px",
              fontWeight: "bold",
              cursor: "pointer",
              transition: "background-color 0.2s ease"
            }}
            onMouseOver={(e) => e.currentTarget.style.backgroundColor = "#545b62"}
            onMouseOut={(e) => e.currentTarget.style.backgroundColor = "#6c757d"}
          >
            📖 Review Session
          </button>
        )}

        {!isLastSession && onNextSession ? (
          <button
            onClick={onNextSession}
            style={{
              padding: "12px 20px",
              backgroundColor: "#007bff",
              color: "white",
              border: "none",
              borderRadius: "8px",
              fontSize: "14px",
              fontWeight: "bold",
              cursor: "pointer",
              transition: "background-color 0.2s ease"
            }}
            onMouseOver={(e) => e.currentTarget.style.backgroundColor = "#0056b3"}
            onMouseOut={(e) => e.currentTarget.style.backgroundColor = "#007bff"}
          >
            ➡️ Next Session ({session.sessionNumber + 1}/{session.totalSessions})
          </button>
        ) : (
          <button
            style={{
              padding: "12px 20px",
              backgroundColor: "#28a745",
              color: "white",
              border: "none",
              borderRadius: "8px",
              fontSize: "14px",
              fontWeight: "bold",
              cursor: "pointer",
              transition: "background-color 0.2s ease"
            }}
            onMouseOver={(e) => e.currentTarget.style.backgroundColor = "#1e7e34"}
            onMouseOut={(e) => e.currentTarget.style.backgroundColor = "#28a745"}
          >
            🎊 Video Complete!
          </button>
        )}
      </div>

      {isLastSession && (
        <div style={{
          marginTop: "16px",
          fontSize: "14px",
          color: "#155724",
          fontStyle: "italic"
        }}>
          🌟 Amazing! You've completed the entire video learning journey!
        </div>
      )}
    </div>
  );
};

export default SummaryState;