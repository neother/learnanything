import React from "react";
import { Vocabulary, LearningSession, ProgressData } from "../../../types";

interface CruisingStateProps {
  previousWord?: Vocabulary;
  session?: LearningSession;
  nextWordTimestamp?: number | null;
  currentWordIndex?: number;
  progressData?: ProgressData;
}

const CruisingState: React.FC<CruisingStateProps> = ({
  previousWord,
  session,
  nextWordTimestamp,
  currentWordIndex,
  progressData
}) => {
  const formatTimestamp = (timestamp: number) => {
    const minutes = Math.floor(timestamp / 60);
    const seconds = Math.floor(timestamp % 60);
    return `${minutes}:${seconds.toString().padStart(2, "0")}`;
  };

  const getNextWord = () => {
    if (!session || !session.focusWords.length || currentWordIndex === undefined) return null;

    const sortedWords = [...session.focusWords]
      .filter(word => typeof word.timestamp === 'number')
      .sort((a, b) => (a.timestamp || 0) - (b.timestamp || 0));

    return sortedWords[currentWordIndex] || null;
  };

  const nextWord = getNextWord();

  return (
    <div className="learning-panel cruising-state" style={{
      padding: "20px",
      backgroundColor: "#f8f9fa",
      borderRadius: "12px",
      border: "2px solid #28a745",
      minHeight: "120px",
      display: "flex",
      flexDirection: "column",
      justifyContent: "center",
      alignItems: "center",
      boxShadow: "0 4px 12px rgba(40,167,69,0.15)"
    }}>
      <div style={{
        fontSize: "18px",
        fontWeight: "bold",
        color: "#28a745",
        marginBottom: "16px",
        textAlign: "center",
        display: "flex",
        alignItems: "center",
        gap: "8px"
      }}>
        🎬 Smart Watching Mode
      </div>

      {/* Progress Display */}
      {progressData && (
        <div style={{
          backgroundColor: "white",
          padding: "12px",
          borderRadius: "8px",
          border: "1px solid #dee2e6",
          width: "100%",
          marginBottom: "16px"
        }}>
          <div style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            fontSize: "12px",
            color: "#6c757d",
            marginBottom: "4px"
          }}>
            <span>Session Progress</span>
          </div>
          <div style={{
            display: "flex",
            alignItems: "center",
            gap: "8px",
            fontSize: "14px"
          }}>
            <span style={{ color: "#28a745", fontWeight: "bold" }}>
              {progressData.sessionWordsLearned.length} words learned
            </span>
            {session && (
              <span style={{ color: "#6c757d" }}>
                • Session {session.sessionNumber}/{session.totalSessions}
              </span>
            )}
          </div>
        </div>
      )}

      {nextWord ? (
        <div style={{
          textAlign: "center",
          backgroundColor: "white",
          padding: "16px",
          borderRadius: "8px",
          border: "1px solid #dee2e6",
          width: "100%"
        }}>
          <div style={{
            fontSize: "12px",
            color: "#6c757d",
            marginBottom: "8px",
            textTransform: "uppercase",
            letterSpacing: "0.5px"
          }}>
            Next Focus Word
          </div>

          <div style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "12px",
            marginBottom: "8px"
          }}>
            <div style={{
              fontSize: "22px",
              fontWeight: "bold",
              color: "#2c3e50"
            }}>
              {nextWord.word}
            </div>

            {nextWord.translation && (
              <div style={{
                fontSize: "16px",
                color: "#6c757d",
                fontStyle: "italic"
              }}>
                ({nextWord.translation})
              </div>
            )}
          </div>

          {nextWord.timestamp && (
            <div style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "8px"
            }}>
              <span style={{
                backgroundColor: "#17a2b8",
                color: "white",
                padding: "4px 8px",
                borderRadius: "12px",
                fontSize: "12px",
                fontWeight: "bold"
              }}>
                ⏰ {formatTimestamp(nextWord.timestamp)}
              </span>
              <span style={{
                backgroundColor: "#28a745",
                color: "white",
                padding: "2px 6px",
                borderRadius: "4px",
                fontSize: "10px",
                fontWeight: "bold"
              }}>
                {nextWord.level}
              </span>
            </div>
          )}
        </div>
      ) : (
        <div style={{
          fontSize: "16px",
          color: "#6c757d",
          textAlign: "center",
          fontStyle: "italic",
          backgroundColor: "white",
          padding: "16px",
          borderRadius: "8px",
          border: "1px solid #dee2e6",
          width: "100%"
        }}>
          {previousWord ? (
            <>
              <div style={{
                fontSize: "12px",
                marginBottom: "8px",
                color: "#28a745"
              }}>
                ✅ Just learned:
              </div>
              <div style={{
                fontSize: "18px",
                fontWeight: "bold",
                color: "#495057"
              }}>
                {previousWord.word}
                {previousWord.translation && (
                  <span style={{
                    fontSize: "14px",
                    color: "#6c757d",
                    marginLeft: "8px"
                  }}>
                    ({previousWord.translation})
                  </span>
                )}
              </div>
            </>
          ) : (
            "🎥 Watching video..."
          )}
        </div>
      )}
    </div>
  );
};

export default CruisingState;