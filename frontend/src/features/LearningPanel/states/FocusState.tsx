import React, { useState } from "react";
import { Vocabulary } from "../../../types";
import AITutor from "../AITutor";

interface FocusStateProps {
  currentWord: Vocabulary;
  onPracticeComplete: () => void;
  onReplaySegment?: (word: Vocabulary) => void;
}

const FocusState: React.FC<FocusStateProps> = ({
  currentWord,
  onPracticeComplete,
  onReplaySegment,
}) => {
  const [showAITutor, setShowAITutor] = useState(false);
  const [practiceComplete, setPracticeComplete] = useState(false);

  const handleStartPractice = () => {
    setShowAITutor(true);
  };

  const handleAITutorComplete = () => {
    setShowAITutor(false);
    setPracticeComplete(true);
  };

  const handleFinishAndContinue = () => {
    // Continue directly without replaying segment to avoid conflicts
    // The smart micro-pause system will handle video playback flow
    console.log(`✅ Practice complete for "${currentWord.word}", continuing to next word`);
    onPracticeComplete();
    setPracticeComplete(false);
  };

  const formatTimestamp = (timestamp: number) => {
    const minutes = Math.floor(timestamp / 60);
    const seconds = Math.floor(timestamp % 60);
    return `${minutes}:${seconds.toString().padStart(2, "0")}`;
  };

  return (
    <div className="learning-panel focus-state" style={{
      border: "2px solid #007bff",
      borderRadius: "12px",
      padding: "20px",
      backgroundColor: "#f8f9fa",
      boxShadow: "0 4px 12px rgba(0,123,255,0.15)"
    }}>
      <div style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        marginBottom: "16px"
      }}>
        <h3 style={{
          margin: "0",
          color: "#007bff",
          fontSize: "20px"
        }}>
          🎯 Focus Word
        </h3>
        {currentWord.timestamp && (
          <span style={{
            backgroundColor: "#007bff",
            color: "white",
            padding: "4px 8px",
            borderRadius: "12px",
            fontSize: "12px",
            fontWeight: "bold"
          }}>
            {formatTimestamp(currentWord.timestamp)}
          </span>
        )}
      </div>

      {/* Word Header */}
      <div style={{
        display: "flex",
        alignItems: "center",
        gap: "12px",
        marginBottom: "16px",
        padding: "16px",
        backgroundColor: "white",
        borderRadius: "8px",
        border: "1px solid #dee2e6"
      }}>
        <div style={{
          fontSize: "28px",
          fontWeight: "bold",
          color: "#2c3e50"
        }}>
          {currentWord.word}
        </div>

        {currentWord.translation && (
          <div style={{
            fontSize: "16px",
            color: "#6c757d",
            fontStyle: "italic"
          }}>
            ({currentWord.translation})
          </div>
        )}

        <div style={{
          backgroundColor: "#28a745",
          color: "white",
          padding: "4px 8px",
          borderRadius: "4px",
          fontSize: "12px",
          fontWeight: "bold",
          marginLeft: "auto"
        }}>
          {currentWord.level}
        </div>
      </div>

      {/* Definition */}
      <div style={{
        marginBottom: "16px",
        padding: "12px",
        backgroundColor: "white",
        borderRadius: "8px",
        border: "1px solid #dee2e6"
      }}>
        <div style={{
          fontSize: "12px",
          color: "#6c757d",
          marginBottom: "4px",
          textTransform: "uppercase",
          letterSpacing: "0.5px"
        }}>
          Definition
        </div>
        <div style={{
          fontSize: "16px",
          color: "#495057",
          lineHeight: "1.4"
        }}>
          {currentWord.definition}
        </div>
      </div>

      {/* Context Sentence */}
      {currentWord.sentence && (
        <div style={{
          marginBottom: "20px",
          padding: "12px",
          backgroundColor: "#fff3cd",
          borderRadius: "8px",
          border: "1px solid #ffeaa7"
        }}>
          <div style={{
            fontSize: "12px",
            color: "#856404",
            marginBottom: "4px",
            textTransform: "uppercase",
            letterSpacing: "0.5px"
          }}>
            In Context
          </div>
          <div style={{
            fontSize: "15px",
            color: "#856404",
            fontStyle: "italic",
            lineHeight: "1.4"
          }}>
            <span
              dangerouslySetInnerHTML={{
                __html: currentWord.sentence.replace(
                  new RegExp(`\\b${currentWord.word}\\b`, "gi"),
                  `<mark style="background-color: #fd7e14; padding: 1px 3px; border-radius: 3px; color: white; font-weight: bold;">${currentWord.word}</mark>`
                ),
              }}
            />
          </div>
        </div>
      )}

      {/* Action Button */}
      <div style={{ textAlign: "center" }}>
        {!showAITutor && !practiceComplete && (
          <button
            onClick={handleStartPractice}
            style={{
              padding: "14px 28px",
              backgroundColor: "#28a745",
              color: "white",
              border: "none",
              borderRadius: "8px",
              fontSize: "16px",
              fontWeight: "bold",
              cursor: "pointer",
              transition: "all 0.2s ease",
              boxShadow: "0 2px 4px rgba(40,167,69,0.2)"
            }}
            onMouseOver={(e) => e.currentTarget.style.backgroundColor = "#1e7e34"}
            onMouseOut={(e) => e.currentTarget.style.backgroundColor = "#28a745"}
          >
            Start Practice →
          </button>
        )}

        {practiceComplete && (
          <button
            onClick={handleFinishAndContinue}
            style={{
              padding: "14px 28px",
              backgroundColor: "#17a2b8",
              color: "white",
              border: "none",
              borderRadius: "8px",
              fontSize: "16px",
              fontWeight: "bold",
              cursor: "pointer",
              transition: "all 0.2s ease",
              boxShadow: "0 2px 4px rgba(23,162,184,0.2)"
            }}
            onMouseOver={(e) => e.currentTarget.style.backgroundColor = "#138496"}
            onMouseOut={(e) => e.currentTarget.style.backgroundColor = "#17a2b8"}
          >
            ✓ Finish & Continue
          </button>
        )}
      </div>

      {/* AI Tutor Modal */}
      {showAITutor && (
        <AITutor
          word={currentWord}
          onComplete={handleAITutorComplete}
        />
      )}
    </div>
  );
};

export default FocusState;