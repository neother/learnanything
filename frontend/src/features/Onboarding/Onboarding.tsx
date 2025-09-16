import React, { useState } from "react";
import { OnboardingProps, UserProfile, AssessmentResult } from "../../types";
import WelcomeScreen from "./WelcomeScreen";
import VocabularyAssessment from "./VocabularyAssessment";
import AssessmentResults from "./AssessmentResults";
import ProfileCreation from "./ProfileCreation";

type OnboardingStep = 'welcome' | 'assessment' | 'results' | 'profile';

const Onboarding: React.FC<OnboardingProps> = ({ onComplete, onSkip }) => {
  const [currentStep, setCurrentStep] = useState<OnboardingStep>('welcome');
  const [assessmentResult, setAssessmentResult] = useState<AssessmentResult | null>(null);
  const [userProfile, setUserProfile] = useState<Partial<UserProfile>>({});

  const handleWelcomeComplete = () => {
    setCurrentStep('assessment');
  };

  const handleAssessmentComplete = (result: AssessmentResult) => {
    setAssessmentResult(result);
    setCurrentStep('results');
  };

  const handleResultsViewed = () => {
    setCurrentStep('profile');
  };

  const handleProfileCreated = (profile: UserProfile) => {
    setUserProfile(profile);
    onComplete(profile);
  };

  const handleSkipAssessment = () => {
    // Create default result for users who skip assessment
    const defaultResult: AssessmentResult = {
      totalQuestions: 0,
      correctAnswers: 0,
      estimatedLevel: 'A2',
      levelConfidence: 0.5,
      strengths: ['Ready to learn'],
      weaknesses: ['Assessment skipped'],
      recommendedStartLevel: 'A2'
    };
    setAssessmentResult(defaultResult);
    setCurrentStep('profile');
  };

  const renderCurrentStep = () => {
    switch (currentStep) {
      case 'welcome':
        return (
          <WelcomeScreen
            onStartAssessment={handleWelcomeComplete}
            onSkip={onSkip}
          />
        );

      case 'assessment':
        return (
          <VocabularyAssessment
            onComplete={handleAssessmentComplete}
            onSkip={handleSkipAssessment}
          />
        );

      case 'results':
        return (
          <AssessmentResults
            result={assessmentResult!}
            onContinue={handleResultsViewed}
          />
        );

      case 'profile':
        return (
          <ProfileCreation
            assessmentResult={assessmentResult}
            onComplete={handleProfileCreated}
          />
        );

      default:
        return (
          <WelcomeScreen
            onStartAssessment={handleWelcomeComplete}
            onSkip={onSkip}
          />
        );
    }
  };

  return (
    <div style={{
      position: "fixed",
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: "#f8f9fa",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      zIndex: 2000,
      fontFamily: "system-ui, -apple-system, sans-serif"
    }}>
      <div style={{
        width: "100%",
        maxWidth: "900px",
        height: "100%",
        maxHeight: "700px",
        backgroundColor: "white",
        borderRadius: "16px",
        boxShadow: "0 8px 32px rgba(0,0,0,0.1)",
        overflow: "hidden",
        display: "flex",
        flexDirection: "column"
      }}>
        {/* Progress indicator */}
        <div style={{
          padding: "16px 32px",
          borderBottom: "1px solid #e9ecef",
          backgroundColor: "#f8f9fa"
        }}>
          <div style={{
            display: "flex",
            alignItems: "center",
            gap: "16px"
          }}>
            <div style={{
              fontSize: "18px",
              fontWeight: "bold",
              color: "#2c3e50"
            }}>
              🎓 Welcome to Smart Navigator
            </div>
            <div style={{
              flex: 1,
              height: "4px",
              backgroundColor: "#e9ecef",
              borderRadius: "2px",
              overflow: "hidden"
            }}>
              <div style={{
                height: "100%",
                backgroundColor: "#007bff",
                borderRadius: "2px",
                width: currentStep === 'welcome' ? "25%" :
                       currentStep === 'assessment' ? "50%" :
                       currentStep === 'results' ? "75%" : "100%",
                transition: "width 0.3s ease"
              }} />
            </div>
            <div style={{
              fontSize: "14px",
              color: "#6c757d",
              minWidth: "80px"
            }}>
              {currentStep === 'welcome' ? "Step 1/4" :
               currentStep === 'assessment' ? "Step 2/4" :
               currentStep === 'results' ? "Step 3/4" : "Step 4/4"}
            </div>
          </div>
        </div>

        {/* Content area */}
        <div style={{
          flex: 1,
          overflow: "auto",
          padding: "32px"
        }}>
          {renderCurrentStep()}
        </div>
      </div>
    </div>
  );
};

export default Onboarding;