import React, { useState } from "react";
import { UserProfile, AssessmentResult } from "../../types";

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

interface ProfileCreationProps {
  assessmentResult: AssessmentResult | null;
  onComplete: (profile: UserProfile) => void;
}

const ProfileCreation: React.FC<ProfileCreationProps> = ({ assessmentResult, onComplete }) => {
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleCreateProfile = async () => {
    if (!name.trim()) {
      setError("Please enter your name");
      return;
    }

    if (name.trim().length < 2) {
      setError("Name must be at least 2 characters long");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_BASE_URL}/api/profile/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name: name.trim(),
          estimatedLevel: assessmentResult?.estimatedLevel || 'A2',
          completedAssessment: assessmentResult !== null && assessmentResult.totalQuestions > 0
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // Convert backend timestamps to Date objects
      const profile: UserProfile = {
        ...data.profile,
        createdAt: new Date(data.profile.createdAt * 1000),
        lastActiveAt: new Date(data.profile.lastActiveAt * 1000)
      };

      // Store profile in localStorage for persistence
      localStorage.setItem('userProfile', JSON.stringify(profile));

      onComplete(profile);
    } catch (error) {
      console.error('Error creating profile:', error);

      // Create fallback profile
      const fallbackProfile: UserProfile = {
        id: `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        name: name.trim(),
        estimatedLevel: assessmentResult?.estimatedLevel || 'A2',
        completedAssessment: assessmentResult !== null,
        createdAt: new Date(),
        lastActiveAt: new Date(),
        totalStudyTime: 0,
        wordsLearned: 0,
        currentStreak: 0,
        longestStreak: 0
      };

      localStorage.setItem('userProfile', JSON.stringify(fallbackProfile));
      onComplete(fallbackProfile);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleCreateProfile();
    }
  };

  return (
    <div style={{
      maxWidth: "500px",
      margin: "0 auto",
      textAlign: "center"
    }}>
      {/* Header */}
      <div style={{
        marginBottom: "40px"
      }}>
        <div style={{
          fontSize: "64px",
          marginBottom: "24px"
        }}>
          👋
        </div>
        <h2 style={{
          fontSize: "32px",
          fontWeight: "bold",
          color: "#2c3e50",
          marginBottom: "16px"
        }}>
          Welcome to Smart Navigator!
        </h2>
        <p style={{
          fontSize: "16px",
          color: "#6c757d",
          lineHeight: "1.5"
        }}>
          Let's create your personalized learning profile
        </p>
      </div>

      {/* Assessment Summary */}
      {assessmentResult && (
        <div style={{
          backgroundColor: "#f8f9fa",
          padding: "24px",
          borderRadius: "12px",
          border: "1px solid #e9ecef",
          marginBottom: "32px",
          textAlign: "left"
        }}>
          <div style={{
            fontSize: "14px",
            color: "#6c757d",
            marginBottom: "12px",
            textTransform: "uppercase",
            letterSpacing: "0.5px",
            textAlign: "center"
          }}>
            Your Learning Profile
          </div>

          <div style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: "16px"
          }}>
            <div style={{
              padding: "16px",
              backgroundColor: "white",
              borderRadius: "8px",
              textAlign: "center"
            }}>
              <div style={{
                fontSize: "24px",
                fontWeight: "bold",
                color: "#007bff",
                marginBottom: "4px"
              }}>
                {assessmentResult.estimatedLevel}
              </div>
              <div style={{
                fontSize: "12px",
                color: "#6c757d"
              }}>
                Current Level
              </div>
            </div>

            <div style={{
              padding: "16px",
              backgroundColor: "white",
              borderRadius: "8px",
              textAlign: "center"
            }}>
              <div style={{
                fontSize: "24px",
                fontWeight: "bold",
                color: "#28a745",
                marginBottom: "4px"
              }}>
                {assessmentResult.recommendedStartLevel}
              </div>
              <div style={{
                fontSize: "12px",
                color: "#6c757d"
              }}>
                Starting Level
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Name Input */}
      <div style={{
        marginBottom: "32px",
        textAlign: "left"
      }}>
        <label style={{
          display: "block",
          fontSize: "16px",
          fontWeight: "600",
          color: "#2c3e50",
          marginBottom: "8px"
        }}>
          What should we call you?
        </label>

        <input
          type="text"
          value={name}
          onChange={(e) => {
            setName(e.target.value);
            if (error) setError("");
          }}
          onKeyPress={handleKeyPress}
          placeholder="Enter your name"
          disabled={loading}
          style={{
            width: "100%",
            padding: "16px",
            fontSize: "16px",
            border: error ? "2px solid #dc3545" : "2px solid #dee2e6",
            borderRadius: "8px",
            outline: "none",
            transition: "border-color 0.2s ease",
            backgroundColor: loading ? "#f8f9fa" : "white"
          }}
          onFocus={(e) => {
            if (!error) {
              e.target.style.borderColor = "#007bff";
            }
          }}
          onBlur={(e) => {
            if (!error) {
              e.target.style.borderColor = "#dee2e6";
            }
          }}
        />

        {error && (
          <div style={{
            color: "#dc3545",
            fontSize: "14px",
            marginTop: "8px",
            display: "flex",
            alignItems: "center",
            gap: "4px"
          }}>
            <span>⚠️</span>
            {error}
          </div>
        )}

        <div style={{
          fontSize: "14px",
          color: "#6c757d",
          marginTop: "8px"
        }}>
          This helps us personalize your learning experience
        </div>
      </div>

      {/* Features Preview */}
      <div style={{
        backgroundColor: "#f8f9fa",
        padding: "24px",
        borderRadius: "12px",
        border: "1px solid #e9ecef",
        marginBottom: "32px",
        textAlign: "left"
      }}>
        <div style={{
          fontSize: "16px",
          fontWeight: "600",
          color: "#2c3e50",
          marginBottom: "16px",
          textAlign: "center"
        }}>
          🎯 What's Next?
        </div>

        <div style={{
          display: "grid",
          gap: "12px"
        }}>
          <div style={{
            display: "flex",
            alignItems: "center",
            gap: "12px"
          }}>
            <div style={{
              width: "32px",
              height: "32px",
              backgroundColor: "#007bff",
              borderRadius: "50%",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "16px",
              color: "white",
              flexShrink: 0
            }}>
              🎬
            </div>
            <div>
              <div style={{ fontSize: "14px", fontWeight: "600", color: "#2c3e50" }}>
                Smart Video Learning
              </div>
              <div style={{ fontSize: "12px", color: "#6c757d" }}>
                Paste any YouTube URL to start learning
              </div>
            </div>
          </div>

          <div style={{
            display: "flex",
            alignItems: "center",
            gap: "12px"
          }}>
            <div style={{
              width: "32px",
              height: "32px",
              backgroundColor: "#28a745",
              borderRadius: "50%",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "16px",
              color: "white",
              flexShrink: 0
            }}>
              🎓
            </div>
            <div>
              <div style={{ fontSize: "14px", fontWeight: "600", color: "#2c3e50" }}>
                AI-Powered Tutoring
              </div>
              <div style={{ fontSize: "12px", color: "#6c757d" }}>
                Interactive conversations to deepen understanding
              </div>
            </div>
          </div>

          <div style={{
            display: "flex",
            alignItems: "center",
            gap: "12px"
          }}>
            <div style={{
              width: "32px",
              height: "32px",
              backgroundColor: "#17a2b8",
              borderRadius: "50%",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "16px",
              color: "white",
              flexShrink: 0
            }}>
              📊
            </div>
            <div>
              <div style={{ fontSize: "14px", fontWeight: "600", color: "#2c3e50" }}>
                Progress Tracking
              </div>
              <div style={{ fontSize: "12px", color: "#6c757d" }}>
                Monitor your learning journey and achievements
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Create Profile Button */}
      <button
        onClick={handleCreateProfile}
        disabled={loading || !name.trim()}
        style={{
          width: "100%",
          padding: "16px 32px",
          backgroundColor: loading || !name.trim() ? "#e9ecef" : "#007bff",
          color: loading || !name.trim() ? "#adb5bd" : "white",
          border: "none",
          borderRadius: "12px",
          fontSize: "18px",
          fontWeight: "600",
          cursor: loading || !name.trim() ? "not-allowed" : "pointer",
          transition: "all 0.2s ease",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: "8px"
        }}
        onMouseOver={(e) => {
          if (!loading && name.trim()) {
            e.currentTarget.style.backgroundColor = "#0056b3";
            e.currentTarget.style.transform = "translateY(-2px)";
          }
        }}
        onMouseOut={(e) => {
          if (!loading && name.trim()) {
            e.currentTarget.style.backgroundColor = "#007bff";
            e.currentTarget.style.transform = "translateY(0)";
          }
        }}
      >
        {loading && (
          <div style={{
            width: "20px",
            height: "20px",
            border: "2px solid transparent",
            borderTop: "2px solid currentColor",
            borderRadius: "50%",
            animation: "spin 1s linear infinite"
          }} />
        )}
        {loading ? "Creating Your Profile..." : "Start Learning Journey →"}
      </button>

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
};

export default ProfileCreation;