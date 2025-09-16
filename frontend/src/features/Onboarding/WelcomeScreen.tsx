import React from "react";

interface WelcomeScreenProps {
  onStartAssessment: () => void;
  onSkip: () => void;
}

const WelcomeScreen: React.FC<WelcomeScreenProps> = ({ onStartAssessment, onSkip }) => {
  return (
    <div style={{
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      textAlign: "center",
      maxWidth: "600px",
      margin: "0 auto",
      padding: "40px 20px"
    }}>
      {/* Hero Section */}
      <div style={{
        fontSize: "72px",
        marginBottom: "24px",
        background: "linear-gradient(135deg, #007bff, #28a745)",
        WebkitBackgroundClip: "text",
        WebkitTextFillColor: "transparent",
        backgroundClip: "text"
      }}>
        🎯
      </div>

      <h1 style={{
        fontSize: "36px",
        fontWeight: "bold",
        color: "#2c3e50",
        marginBottom: "16px",
        lineHeight: "1.2"
      }}>
        Welcome to Smart Navigator
      </h1>

      <p style={{
        fontSize: "20px",
        color: "#6c757d",
        marginBottom: "40px",
        lineHeight: "1.5"
      }}>
        Transform any YouTube video into your personal language course
      </p>

      {/* Features */}
      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
        gap: "24px",
        marginBottom: "48px",
        width: "100%"
      }}>
        <div style={{
          padding: "24px",
          backgroundColor: "#f8f9fa",
          borderRadius: "12px",
          border: "1px solid #e9ecef"
        }}>
          <div style={{ fontSize: "32px", marginBottom: "12px" }}>🎬</div>
          <h3 style={{
            fontSize: "16px",
            fontWeight: "600",
            color: "#2c3e50",
            margin: "0 0 8px 0"
          }}>
            Smart Video Learning
          </h3>
          <p style={{
            fontSize: "14px",
            color: "#6c757d",
            margin: 0,
            lineHeight: "1.4"
          }}>
            Automatic pausing at focus words with intelligent learning sessions
          </p>
        </div>

        <div style={{
          padding: "24px",
          backgroundColor: "#f8f9fa",
          borderRadius: "12px",
          border: "1px solid #e9ecef"
        }}>
          <div style={{ fontSize: "32px", marginBottom: "12px" }}>🎓</div>
          <h3 style={{
            fontSize: "16px",
            fontWeight: "600",
            color: "#2c3e50",
            margin: "0 0 8px 0"
          }}>
            AI-Powered Tutor
          </h3>
          <p style={{
            fontSize: "14px",
            color: "#6c757d",
            margin: 0,
            lineHeight: "1.4"
          }}>
            Interactive conversations to deepen your vocabulary understanding
          </p>
        </div>

        <div style={{
          padding: "24px",
          backgroundColor: "#f8f9fa",
          borderRadius: "12px",
          border: "1px solid #e9ecef"
        }}>
          <div style={{ fontSize: "32px", marginBottom: "12px" }}>📊</div>
          <h3 style={{
            fontSize: "16px",
            fontWeight: "600",
            color: "#2c3e50",
            margin: "0 0 8px 0"
          }}>
            Adaptive Learning
          </h3>
          <p style={{
            fontSize: "14px",
            color: "#6c757d",
            margin: 0,
            lineHeight: "1.4"
          }}>
            CEFR-based content that adapts to your current skill level
          </p>
        </div>
      </div>

      {/* Call to Action */}
      <div style={{
        display: "flex",
        flexDirection: "column",
        gap: "16px",
        width: "100%",
        maxWidth: "400px"
      }}>
        <button
          onClick={onStartAssessment}
          style={{
            padding: "16px 32px",
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
          Take 2-Min Assessment →
        </button>

        <div style={{
          fontSize: "14px",
          color: "#6c757d",
          lineHeight: "1.4"
        }}>
          We'll customize your learning experience based on your current vocabulary level
        </div>

        <button
          onClick={onSkip}
          style={{
            padding: "12px 24px",
            backgroundColor: "transparent",
            color: "#6c757d",
            border: "1px solid #dee2e6",
            borderRadius: "8px",
            fontSize: "14px",
            cursor: "pointer",
            transition: "all 0.2s ease"
          }}
          onMouseOver={(e) => {
            e.currentTarget.style.backgroundColor = "#f8f9fa";
            e.currentTarget.style.borderColor = "#adb5bd";
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.backgroundColor = "transparent";
            e.currentTarget.style.borderColor = "#dee2e6";
          }}
        >
          Skip assessment - Start with A2 level
        </button>
      </div>

      {/* Footer */}
      <div style={{
        marginTop: "40px",
        fontSize: "12px",
        color: "#adb5bd"
      }}>
        Join thousands of learners improving their English with Smart Navigator
      </div>
    </div>
  );
};

export default WelcomeScreen;