import React, { useState } from "react";
import { Vocabulary } from "../../types";

interface AITutorProps {
  word: Vocabulary;
  onComplete: () => void;
}

// API base URL (should match App.tsx configuration)
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

interface ConversationMessage {
  type: 'user' | 'ai';
  content: string;
  timestamp: Date;
}

const AITutor: React.FC<AITutorProps> = ({ word, onComplete }) => {
  const [aiResponse, setAiResponse] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [hasStarted, setHasStarted] = useState(false);
  const [conversation, setConversation] = useState<ConversationMessage[]>([]);
  const [userInput, setUserInput] = useState<string>("");
  const [currentPhase, setCurrentPhase] = useState<'initial' | 'interactive' | 'completed'>('initial');

  const callAITeacher = async (question: string = "") => {
    setLoading(true);
    if (!hasStarted) setHasStarted(true);

    try {
      console.log("Calling AI Teacher for word:", word.word, "Question:", question);

      const response = await fetch(`${API_BASE_URL}/api/ai-teacher`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          word: word.word,
          definition: word.definition,
          sentence: word.sentence || "",
          question: question,
          conversation_history: conversation
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      const aiResponseText = data.ai_response || "AI teacher response not available";

      setAiResponse(aiResponseText);

      // Add to conversation history
      const newMessages: ConversationMessage[] = [];
      if (question) {
        newMessages.push({
          type: 'user',
          content: question,
          timestamp: new Date()
        });
      }
      newMessages.push({
        type: 'ai',
        content: aiResponseText,
        timestamp: new Date()
      });

      setConversation(prev => [...prev, ...newMessages]);
      setCurrentPhase(question ? 'interactive' : 'initial');

    } catch (error) {
      console.error("AI Teacher error:", error);
      const errorMessage = "Sorry, I'm having trouble connecting to the AI teacher right now. Please try again later.";
      setAiResponse(errorMessage);

      setConversation(prev => [...prev, {
        type: 'ai',
        content: errorMessage,
        timestamp: new Date()
      }]);
    } finally {
      setLoading(false);
    }
  };

  const sendUserMessage = async () => {
    if (!userInput.trim() || loading) return;

    const question = userInput.trim();
    setUserInput("");
    await callAITeacher(question);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendUserMessage();
    }
  };

  const handleComplete = () => {
    setAiResponse("");
    setHasStarted(false);
    setConversation([]);
    setUserInput("");
    setCurrentPhase('initial');
    onComplete();
  };

  return (
    <div style={{
      position: "fixed",
      top: "0",
      left: "0",
      right: "0",
      bottom: "0",
      backgroundColor: "rgba(0,0,0,0.7)",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      zIndex: 1000,
      animation: "fadeIn 0.2s ease-in"
    }}>
      <div style={{
        backgroundColor: "white",
        borderRadius: "16px",
        width: "90%",
        maxWidth: "600px",
        maxHeight: "80vh",
        overflow: "hidden",
        boxShadow: "0 8px 32px rgba(0,0,0,0.3)",
        display: "flex",
        flexDirection: "column"
      }}>
        {/* Header */}
        <div style={{
          padding: "20px",
          backgroundColor: "#28a745",
          color: "white",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center"
        }}>
          <h3 style={{
            margin: "0",
            fontSize: "20px",
            fontWeight: "bold"
          }}>
            🎓 AI Teacher: {word.word}
          </h3>
          <button
            onClick={handleComplete}
            style={{
              backgroundColor: "rgba(255,255,255,0.2)",
              color: "white",
              border: "none",
              borderRadius: "8px",
              padding: "8px 12px",
              cursor: "pointer",
              fontSize: "14px",
              fontWeight: "bold",
              transition: "background-color 0.2s ease"
            }}
            onMouseOver={(e) => e.currentTarget.style.backgroundColor = "rgba(255,255,255,0.3)"}
            onMouseOut={(e) => e.currentTarget.style.backgroundColor = "rgba(255,255,255,0.2)"}
          >
            Close
          </button>
        </div>

        {/* Content */}
        <div style={{
          padding: "20px",
          flex: "1",
          overflow: "auto",
          display: "flex",
          flexDirection: "column",
          gap: "16px"
        }}>
          {!hasStarted ? (
            <div style={{ textAlign: "center" }}>
              <div style={{
                fontSize: "16px",
                color: "#495057",
                marginBottom: "20px",
                lineHeight: "1.5"
              }}>
                Ready to practice <strong>"{word.word}"</strong> with your AI teacher?
                <br />
                I'll help you understand and remember this word better.
              </div>

              <button
                onClick={() => callAITeacher()}
                disabled={loading}
                style={{
                  padding: "14px 28px",
                  backgroundColor: "#007bff",
                  color: "white",
                  border: "none",
                  borderRadius: "8px",
                  fontSize: "16px",
                  fontWeight: "bold",
                  cursor: loading ? "not-allowed" : "pointer",
                  opacity: loading ? 0.7 : 1,
                  transition: "all 0.2s ease"
                }}
              >
                {loading ? "Connecting..." : "Start Learning Session"}
              </button>
            </div>
          ) : (
            <>
              {/* Conversation Display */}
              <div style={{
                flex: "1",
                maxHeight: "400px",
                overflow: "auto",
                backgroundColor: "#f8f9fa",
                borderRadius: "12px",
                border: "1px solid #e9ecef",
                padding: "16px",
                marginBottom: "16px"
              }}>
                {conversation.length === 0 && !loading ? (
                  <div style={{
                    textAlign: "center",
                    color: "#6c757d",
                    fontStyle: "italic",
                    padding: "20px"
                  }}>
                    Start your conversation with the AI teacher!
                  </div>
                ) : (
                  <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                    {conversation.map((message, index) => (
                      <div
                        key={index}
                        style={{
                          display: "flex",
                          flexDirection: message.type === 'user' ? 'row-reverse' : 'row',
                          alignItems: "flex-start",
                          gap: "8px"
                        }}
                      >
                        <div style={{
                          backgroundColor: message.type === 'user' ? '#007bff' : '#28a745',
                          color: "white",
                          borderRadius: "50%",
                          width: "32px",
                          height: "32px",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          fontSize: "16px",
                          flexShrink: 0
                        }}>
                          {message.type === 'user' ? '👤' : '🎓'}
                        </div>
                        <div style={{
                          backgroundColor: message.type === 'user' ? '#007bff' : 'white',
                          color: message.type === 'user' ? 'white' : '#495057',
                          padding: "12px 16px",
                          borderRadius: "18px",
                          maxWidth: "80%",
                          border: message.type === 'ai' ? '1px solid #dee2e6' : 'none',
                          lineHeight: "1.4",
                          fontSize: "14px",
                          whiteSpace: "pre-line"
                        }}>
                          {message.content}
                        </div>
                      </div>
                    ))}

                    {loading && (
                      <div style={{
                        display: "flex",
                        alignItems: "flex-start",
                        gap: "8px"
                      }}>
                        <div style={{
                          backgroundColor: '#28a745',
                          color: "white",
                          borderRadius: "50%",
                          width: "32px",
                          height: "32px",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          fontSize: "16px"
                        }}>
                          🎓
                        </div>
                        <div style={{
                          backgroundColor: "white",
                          padding: "12px 16px",
                          borderRadius: "18px",
                          border: '1px solid #dee2e6',
                          display: "flex",
                          alignItems: "center",
                          gap: "8px"
                        }}>
                          <div style={{
                            width: "16px",
                            height: "16px",
                            border: "2px solid #f3f3f3",
                            borderTop: "2px solid #28a745",
                            borderRadius: "50%",
                            animation: "spin 1s linear infinite"
                          }} />
                          <span style={{
                            fontSize: "14px",
                            color: "#6c757d"
                          }}>
                            AI Teacher is thinking...
                          </span>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Input Area */}
              {hasStarted && (
                <div style={{
                  display: "flex",
                  gap: "8px",
                  alignItems: "flex-end",
                  marginBottom: "16px"
                }}>
                  <textarea
                    value={userInput}
                    onChange={(e) => setUserInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Ask a question about this word..."
                    disabled={loading}
                    style={{
                      flex: "1",
                      padding: "12px",
                      borderRadius: "12px",
                      border: "1px solid #dee2e6",
                      resize: "none",
                      minHeight: "44px",
                      maxHeight: "100px",
                      fontFamily: "inherit",
                      fontSize: "14px",
                      outline: "none"
                    }}
                    rows={1}
                  />
                  <button
                    onClick={sendUserMessage}
                    disabled={loading || !userInput.trim()}
                    style={{
                      padding: "12px 16px",
                      backgroundColor: "#007bff",
                      color: "white",
                      border: "none",
                      borderRadius: "12px",
                      cursor: loading || !userInput.trim() ? "not-allowed" : "pointer",
                      opacity: loading || !userInput.trim() ? 0.5 : 1,
                      fontSize: "14px",
                      fontWeight: "bold",
                      minWidth: "60px"
                    }}
                  >
                    {loading ? "..." : "Send"}
                  </button>
                </div>
              )}

              {/* Action Buttons */}
              <div style={{
                display: "flex",
                justifyContent: "center",
                gap: "12px",
                flexWrap: "wrap"
              }}>
                {conversation.length > 0 && (
                  <button
                    onClick={handleComplete}
                    style={{
                      padding: "12px 24px",
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
                    ✓ Got it! Continue Learning
                  </button>
                )}

                {conversation.length === 0 && !loading && (
                  <div style={{
                    display: "flex",
                    gap: "8px",
                    flexWrap: "wrap",
                    justifyContent: "center"
                  }}>
                    <button
                      onClick={() => callAITeacher("How do I use this word in a sentence?")}
                      style={{
                        padding: "8px 16px",
                        backgroundColor: "#17a2b8",
                        color: "white",
                        border: "none",
                        borderRadius: "6px",
                        fontSize: "12px",
                        cursor: "pointer"
                      }}
                    >
                      How to use?
                    </button>
                    <button
                      onClick={() => callAITeacher("What are similar words?")}
                      style={{
                        padding: "8px 16px",
                        backgroundColor: "#6610f2",
                        color: "white",
                        border: "none",
                        borderRadius: "6px",
                        fontSize: "12px",
                        cursor: "pointer"
                      }}
                    >
                      Similar words?
                    </button>
                    <button
                      onClick={() => callAITeacher("Can you give me more examples?")}
                      style={{
                        padding: "8px 16px",
                        backgroundColor: "#fd7e14",
                        color: "white",
                        border: "none",
                        borderRadius: "6px",
                        fontSize: "12px",
                        cursor: "pointer"
                      }}
                    >
                      More examples?
                    </button>
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </div>

      <style>
        {`
          @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
          }

          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}
      </style>
    </div>
  );
};

export default AITutor;