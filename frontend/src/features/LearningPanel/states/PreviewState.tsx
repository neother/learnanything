import React from "react";
import { Vocabulary, LearningSession } from "../../../types";

interface PreviewStateProps {
  session: LearningSession;
  onWordMastered: (word: string) => void;
  onStartWatching: () => void;
}

const PreviewState: React.FC<PreviewStateProps> = ({
  session,
  onWordMastered,
  onStartWatching,
}) => {
  return (
    <div className="learning-panel preview-state">
      <div className="learning-panel-header">
        <h3 className="learning-panel-title">
          🎯 Smart Watching Mode
        </h3>
        <span className="learning-state-badge preview">
          Session {session.sessionNumber}/{session.totalSessions}
        </span>
      </div>

      <div style={{ marginBottom: "20px" }}>
        {session.focusWords.map((word, index) => (
          <div key={index} className="focus-word-card">
            <div className="focus-word-header">
              <div className="focus-word-main">
                <div>
                  <span className="focus-word-text">{word.word}</span>
                  <span className="focus-word-level" style={{
                    backgroundColor: word.level === 'A1' || word.level === 'A2' ? '#28a745' :
                                   word.level === 'B1' || word.level === 'B2' ? '#007bff' : '#dc3545',
                    color: 'white'
                  }}>
                    {word.level}
                  </span>
                  {word.timestamp && (
                    <span style={{
                      marginLeft: "8px",
                      fontSize: "12px",
                      color: "#007bff",
                      backgroundColor: "#f8f9fa",
                      padding: "2px 6px",
                      borderRadius: "12px",
                      fontFamily: "monospace",
                      fontWeight: "600"
                    }}>
                      ⏱️ {Math.floor(word.timestamp / 60)}:{(word.timestamp % 60).toFixed(0).padStart(2, '0')}
                    </span>
                  )}
                </div>
              </div>

              <button
                onClick={() => onWordMastered(word.word)}
                className="mastery-button"
                title="Mark as already known"
              >
                ✓ Know it
              </button>
            </div>


            <div style={{
              fontSize: "14px",
              color: "#666",
              marginTop: "8px",
              lineHeight: "1.4"
            }}>
              💡 {word.definition}
            </div>

            {word.sentence && (
              <div style={{
                fontSize: "13px",
                color: "#6c757d",
                fontStyle: "italic",
                marginTop: "8px",
                padding: "8px",
                backgroundColor: "#f8f9fa",
                borderRadius: "6px",
                borderLeft: "3px solid #007bff"
              }}>
                📝 {word.sentence}
              </div>
            )}
          </div>
        ))}
      </div>

      <button
        onClick={onStartWatching}
        className="primary-action-button"
      >
        🎬 Start Smart Watching
      </button>

      <div style={{
        marginTop: "16px",
        fontSize: "13px",
        color: "#6c757d",
        textAlign: "center",
        padding: "12px",
        backgroundColor: "#f8f9fa",
        borderRadius: "8px",
        border: "1px solid #e9ecef"
      }}>
        💡 <strong>Tip:</strong> Click "✓ Know it" on words you already know to get more challenging vocabulary!
      </div>
    </div>
  );
};

export default PreviewState;