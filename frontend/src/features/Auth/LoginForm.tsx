import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';

interface LoginFormProps {
  onSuccess?: () => void;
  onSwitchToRegister?: () => void;
  onClose?: () => void;
}

const LoginForm: React.FC<LoginFormProps> = ({
  onSuccess,
  onSwitchToRegister,
  onClose
}) => {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      await login(email, password);
      onSuccess?.();
    } catch (error: any) {
      setError(error.message || 'Login failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{
      padding: "32px",
      backgroundColor: "white",
      borderRadius: "12px",
      boxShadow: "0 8px 32px rgba(0,0,0,0.12)",
      width: "100%",
      maxWidth: "400px",
      margin: "0 auto"
    }}>
      <div style={{
        textAlign: "center",
        marginBottom: "24px"
      }}>
        <h2 style={{
          fontSize: "28px",
          fontWeight: "bold",
          color: "#2c3e50",
          marginBottom: "8px"
        }}>
          Welcome Back! 👋
        </h2>
        <p style={{
          color: "#6c757d",
          fontSize: "16px"
        }}>
          Sign in to continue your learning journey
        </p>
      </div>

      {error && (
        <div style={{
          backgroundColor: "#fee",
          border: "1px solid #fcc",
          color: "#c33",
          padding: "12px",
          borderRadius: "8px",
          marginBottom: "20px",
          fontSize: "14px",
          textAlign: "center"
        }}>
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
        <div>
          <label style={{
            display: "block",
            marginBottom: "8px",
            fontSize: "14px",
            fontWeight: "600",
            color: "#495057"
          }}>
            Email Address
          </label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            placeholder="Enter your email"
            style={{
              width: "100%",
              padding: "12px",
              border: "2px solid #e9ecef",
              borderRadius: "8px",
              fontSize: "16px",
              transition: "border-color 0.2s ease",
              outline: "none"
            }}
            onFocus={(e) => e.target.style.borderColor = "#007bff"}
            onBlur={(e) => e.target.style.borderColor = "#e9ecef"}
          />
        </div>

        <div>
          <label style={{
            display: "block",
            marginBottom: "8px",
            fontSize: "14px",
            fontWeight: "600",
            color: "#495057"
          }}>
            Password
          </label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            placeholder="Enter your password"
            style={{
              width: "100%",
              padding: "12px",
              border: "2px solid #e9ecef",
              borderRadius: "8px",
              fontSize: "16px",
              transition: "border-color 0.2s ease",
              outline: "none"
            }}
            onFocus={(e) => e.target.style.borderColor = "#007bff"}
            onBlur={(e) => e.target.style.borderColor = "#e9ecef"}
          />
        </div>

        <button
          type="submit"
          disabled={isLoading || !email.trim() || !password.trim()}
          style={{
            padding: "14px",
            backgroundColor: isLoading ? "#6c757d" : "#007bff",
            color: "white",
            border: "none",
            borderRadius: "8px",
            fontSize: "16px",
            fontWeight: "600",
            cursor: isLoading ? "not-allowed" : "pointer",
            transition: "background-color 0.2s ease",
            marginTop: "8px"
          }}
          onMouseOver={(e) => {
            if (!isLoading && email.trim() && password.trim()) {
              e.currentTarget.style.backgroundColor = "#0056b3";
            }
          }}
          onMouseOut={(e) => {
            if (!isLoading) {
              e.currentTarget.style.backgroundColor = "#007bff";
            }
          }}
        >
          {isLoading ? "Signing In..." : "Sign In"}
        </button>
      </form>

      <div style={{
        marginTop: "24px",
        textAlign: "center",
        fontSize: "14px",
        color: "#6c757d"
      }}>
        Don't have an account?{" "}
        <button
          onClick={onSwitchToRegister}
          style={{
            background: "none",
            border: "none",
            color: "#007bff",
            fontWeight: "600",
            cursor: "pointer",
            textDecoration: "underline"
          }}
        >
          Sign up here
        </button>
      </div>

      {onClose && (
        <div style={{
          marginTop: "16px",
          textAlign: "center"
        }}>
          <button
            onClick={onClose}
            style={{
              background: "none",
              border: "1px solid #dee2e6",
              color: "#6c757d",
              padding: "8px 16px",
              borderRadius: "6px",
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
            Continue as Guest
          </button>
        </div>
      )}
    </div>
  );
};

export default LoginForm;