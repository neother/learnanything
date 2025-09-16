import React from "react";
import { LearningPanelProps } from "../../types";
import PreviewState from "./states/PreviewState";
import CruisingState from "./states/CruisingState";
import FocusState from "./states/FocusState";
import SummaryState from "./states/SummaryState";

interface ExtendedLearningPanelProps extends LearningPanelProps {
  nextWordTimestamp?: number | null;
  currentWordIndex?: number;
}

const LearningPanel: React.FC<ExtendedLearningPanelProps> = ({
  currentState,
  session,
  currentWord,
  previousWord,
  onStateChange,
  onWordMastered,
  onStartWatching,
  onPracticeComplete,
  onNextSession,
  onSessionComplete,
  onReplaySegment,
  nextWordTimestamp,
  currentWordIndex,
  progressData,
}) => {

  const handleNextSession = () => {
    if (onNextSession) {
      onNextSession();
    } else {
      // Fallback: reset to preview state
      onStateChange('preview');
    }
  };

  const handleReviewSession = () => {
    // This would show a review of the current session
    // For now, we'll just go back to preview
    onStateChange('preview');
  };

  const renderCurrentState = () => {
    switch (currentState) {
      case 'preview':
        if (!session) {
          return (
            <div style={{
              padding: "20px",
              textAlign: "center",
              color: "#6c757d",
              fontSize: "16px"
            }}>
              🎥 Enter a YouTube URL and click "Extract Content" to start learning!
            </div>
          );
        }
        return (
          <PreviewState
            session={session}
            onWordMastered={onWordMastered}
            onStartWatching={onStartWatching}
          />
        );

      case 'cruising':
        return (
          <CruisingState
            previousWord={previousWord}
            session={session}
            nextWordTimestamp={nextWordTimestamp}
            currentWordIndex={currentWordIndex}
            progressData={progressData}
          />
        );

      case 'focus':
        if (!currentWord) {
          return (
            <div style={{
              padding: "20px",
              textAlign: "center",
              color: "#dc3545",
              fontSize: "16px"
            }}>
              ⚠️ No focus word available
            </div>
          );
        }
        return (
          <FocusState
            currentWord={currentWord}
            onPracticeComplete={onPracticeComplete}
            onReplaySegment={onReplaySegment}
          />
        );

      case 'summary':
        if (!session) {
          return (
            <div style={{
              padding: "20px",
              textAlign: "center",
              color: "#dc3545",
              fontSize: "16px"
            }}>
              ⚠️ No session data available
            </div>
          );
        }
        return (
          <SummaryState
            session={session}
            onNextSession={handleNextSession}
            onReviewSession={handleReviewSession}
            progressData={progressData}
          />
        );

      default:
        return (
          <div style={{
            padding: "20px",
            textAlign: "center",
            color: "#dc3545",
            fontSize: "16px"
          }}>
            ⚠️ Unknown learning panel state: {currentState}
          </div>
        );
    }
  };

  return (
    <div className="content-panel" style={{
      padding: "20px",
      minHeight: "400px"
    }}>
      <div className="learning-panel-container">
        {renderCurrentState()}
      </div>
    </div>
  );
};

export default LearningPanel;