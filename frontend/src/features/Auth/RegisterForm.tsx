import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';

interface RegisterFormProps {
  onSuccess?: () => void;
  onSwitchToLogin?: () => void;
  onClose?: () => void;
  initialData?: {
    name?: string;
    estimatedLevel?: string;
  };
}

const RegisterForm: React.FC<RegisterFormProps> = ({
  onSuccess,
  onSwitchToLogin,
  onClose,
  initialData
}) => {
  const { register } = useAuth();
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    confirmPassword: '',
    name: initialData?.name || '',
    estimatedLevel: initialData?.estimatedLevel || 'A2'
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    // Validation
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      setIsLoading(false);
      return;
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters long');
      setIsLoading(false);
      return;
    }

    try {
      await register(
        formData.email,
        formData.username,
        formData.password,
        formData.name,
        formData.estimatedLevel
      );
      onSuccess?.();
    } catch (error: any) {
      setError(error.message || 'Registration failed');
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
      maxWidth: "450px",
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
          Join Smart Navigator 🚀
        </h2>
        <p style={{
          color: "#6c757d",
          fontSize: "16px"
        }}>
          Create your account and start learning
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
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
          <div>
            <label style={{
              display: "block",
              marginBottom: "8px",
              fontSize: "14px",
              fontWeight: "600",
              color: "#495057"
            }}>
              Full Name
            </label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              required
              placeholder="John Doe"
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
              Username
            </label>
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleInputChange}
              required
              placeholder="johndoe"
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
        </div>

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
            name="email"
            value={formData.email}
            onChange={handleInputChange}
            required
            placeholder="john@example.com"
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
            Current Language Level
          </label>
          <select
            name="estimatedLevel"
            value={formData.estimatedLevel}
            onChange={handleInputChange}
            style={{
              width: "100%",
              padding: "12px",
              border: "2px solid #e9ecef",
              borderRadius: "8px",
              fontSize: "16px",
              backgroundColor: "white",
              cursor: "pointer"
            }}
          >
            <option value="A1">A1 - Beginner</option>
            <option value="A2">A2 - Elementary</option>
            <option value="B1">B1 - Intermediate</option>
            <option value="B2">B2 - Upper Intermediate</option>
            <option value="C1">C1 - Advanced</option>
            <option value="C2">C2 - Proficient</option>
          </select>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
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
              name="password"
              value={formData.password}
              onChange={handleInputChange}
              required
              placeholder="Min. 6 characters"
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
              Confirm Password
            </label>
            <input
              type="password"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleInputChange}
              required
              placeholder="Confirm password"
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
        </div>

        <button
          type="submit"
          disabled={isLoading || !formData.email.trim() || !formData.password.trim()}
          style={{
            padding: "14px",
            backgroundColor: isLoading ? "#6c757d" : "#28a745",
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
            if (!isLoading && formData.email.trim() && formData.password.trim()) {
              e.currentTarget.style.backgroundColor = "#1e7e34";
            }
          }}
          onMouseOut={(e) => {
            if (!isLoading) {
              e.currentTarget.style.backgroundColor = "#28a745";
            }
          }}
        >
          {isLoading ? "Creating Account..." : "Create Account"}
        </button>
      </form>

      <div style={{
        marginTop: "24px",
        textAlign: "center",
        fontSize: "14px",
        color: "#6c757d"
      }}>
        Already have an account?{" "}
        <button
          onClick={onSwitchToLogin}
          style={{
            background: "none",
            border: "none",
            color: "#007bff",
            fontWeight: "600",
            cursor: "pointer",
            textDecoration: "underline"
          }}
        >
          Sign in here
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

export default RegisterForm;