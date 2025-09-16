import React, { useState, useEffect } from "react";
import { UserProfile, LearningProgress } from "../../types";

interface HomepageProps {
  userProfile: UserProfile;
  onVideoSelect: (videoUrl: string) => void;
  onNewVideo: () => void;
}

const Homepage: React.FC<HomepageProps> = ({ userProfile, onVideoSelect, onNewVideo }) => {
  const [continueVideos, setContinueVideos] = useState<LearningProgress[]>([]);
  const [recommendedVideos, setRecommendedVideos] = useState<any[]>([]);

  useEffect(() => {
    loadUserProgress();
    loadRecommendations();
  }, [userProfile]);

  const loadUserProgress = () => {
    // Load user's learning progress from localStorage
    // In a real app, this would come from a database
    try {
      const storedProgress = localStorage.getItem(`progress_${userProfile.id}`);
      if (storedProgress) {
        const progress = JSON.parse(storedProgress);
        setContinueVideos(Array.isArray(progress) ? progress : []);
      }
    } catch (error) {
      console.error('Error loading user progress:', error);
    }
  };

  const loadRecommendations = () => {
    // Mock recommended videos based on user level
    const recommendations = getRecommendationsForLevel(userProfile.estimatedLevel);
    setRecommendedVideos(recommendations);
  };

  const getRecommendationsForLevel = (level: string) => {
    const levelRecommendations = {
      'A1': [
        {
          title: "Basic English Conversation",
          url: "https://www.youtube.com/watch?v=RBgjzSk_38M",
          thumbnail: "🗣️",
          duration: "10 min",
          description: "Simple daily conversations for beginners"
        },
        {
          title: "Common English Words",
          url: "https://www.youtube.com/watch?v=_lLkyJJm_o4",
          thumbnail: "📝",
          duration: "8 min",
          description: "Most frequently used English words"
        }
      ],
      'A2': [
        {
          title: "English in Daily Life",
          url: "https://www.youtube.com/watch?v=RBgjzSk_38M",
          thumbnail: "🏠",
          duration: "12 min",
          description: "Practical English for everyday situations"
        },
        {
          title: "Simple Stories in English",
          url: "https://www.youtube.com/watch?v=_lLkyJJm_o4",
          thumbnail: "📚",
          duration: "15 min",
          description: "Easy-to-follow stories with basic vocabulary"
        }
      ],
      'B1': [
        {
          title: "Travel English Guide",
          url: "https://www.youtube.com/watch?v=RBgjzSk_38M",
          thumbnail: "✈️",
          duration: "18 min",
          description: "Essential English for travelers"
        },
        {
          title: "Business English Basics",
          url: "https://www.youtube.com/watch?v=_lLkyJJm_o4",
          thumbnail: "💼",
          duration: "20 min",
          description: "Professional English vocabulary and phrases"
        }
      ],
      'B2': [
        {
          title: "Advanced Conversations",
          url: "https://www.youtube.com/watch?v=RBgjzSk_38M",
          thumbnail: "💭",
          duration: "25 min",
          description: "Complex discussions on various topics"
        },
        {
          title: "Academic English",
          url: "https://www.youtube.com/watch?v=_lLkyJJm_o4",
          thumbnail: "🎓",
          duration: "30 min",
          description: "University-level English vocabulary"
        }
      ]
    };

    return levelRecommendations[level as keyof typeof levelRecommendations] || levelRecommendations['A2'];
  };

  const formatDate = (date: Date) => {
    const today = new Date();
    const diffTime = Math.abs(today.getTime() - date.getTime());
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return "Today";
    if (diffDays === 1) return "Yesterday";
    if (diffDays < 7) return `${diffDays} days ago`;
    return date.toLocaleDateString();
  };

  return (
    <div style={{
      maxWidth: "1200px",
      margin: "0 auto",
      padding: "40px 20px"
    }}>
      {/* Welcome Section */}
      <div style={{
        marginBottom: "48px",
        textAlign: "center"
      }}>
        <h1 style={{
          fontSize: "36px",
          fontWeight: "bold",
          color: "#2c3e50",
          marginBottom: "16px"
        }}>
          Welcome back, {userProfile.name}! 👋
        </h1>
        <p style={{
          fontSize: "18px",
          color: "#6c757d",
          marginBottom: "32px"
        }}>
          Ready to continue your English learning journey?
        </p>

        {/* Stats Cards */}
        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
          gap: "24px",
          marginBottom: "32px"
        }}>
          <div style={{
            padding: "24px",
            backgroundColor: "white",
            borderRadius: "12px",
            border: "1px solid #e9ecef",
            boxShadow: "0 2px 8px rgba(0,0,0,0.1)"
          }}>
            <div style={{
              fontSize: "32px",
              fontWeight: "bold",
              color: "#007bff",
              marginBottom: "8px"
            }}>
              {userProfile.estimatedLevel}
            </div>
            <div style={{
              fontSize: "14px",
              color: "#6c757d"
            }}>
              Current Level
            </div>
          </div>

          <div style={{
            padding: "24px",
            backgroundColor: "white",
            borderRadius: "12px",
            border: "1px solid #e9ecef",
            boxShadow: "0 2px 8px rgba(0,0,0,0.1)"
          }}>
            <div style={{
              fontSize: "32px",
              fontWeight: "bold",
              color: "#28a745",
              marginBottom: "8px"
            }}>
              {userProfile.wordsLearned}
            </div>
            <div style={{
              fontSize: "14px",
              color: "#6c757d"
            }}>
              Words Learned
            </div>
          </div>

          <div style={{
            padding: "24px",
            backgroundColor: "white",
            borderRadius: "12px",
            border: "1px solid #e9ecef",
            boxShadow: "0 2px 8px rgba(0,0,0,0.1)"
          }}>
            <div style={{
              fontSize: "32px",
              fontWeight: "bold",
              color: "#17a2b8",
              marginBottom: "8px"
            }}>
              {userProfile.currentStreak}
            </div>
            <div style={{
              fontSize: "14px",
              color: "#6c757d"
            }}>
              Day Streak
            </div>
          </div>

          <div style={{
            padding: "24px",
            backgroundColor: "white",
            borderRadius: "12px",
            border: "1px solid #e9ecef",
            boxShadow: "0 2px 8px rgba(0,0,0,0.1)"
          }}>
            <div style={{
              fontSize: "32px",
              fontWeight: "bold",
              color: "#fd7e14",
              marginBottom: "8px"
            }}>
              {Math.floor(userProfile.totalStudyTime / 60)}h
            </div>
            <div style={{
              fontSize: "14px",
              color: "#6c757d"
            }}>
              Total Study Time
            </div>
          </div>
        </div>

        {/* Start New Video Button */}
        <button
          onClick={onNewVideo}
          style={{
            padding: "16px 32px",
            backgroundColor: "#007bff",
            color: "white",
            border: "none",
            borderRadius: "12px",
            fontSize: "18px",
            fontWeight: "600",
            cursor: "pointer",
            boxShadow: "0 4px 12px rgba(0,123,255,0.3)",
            transition: "all 0.2s ease"
          }}
          onMouseOver={(e) => {
            e.currentTarget.style.backgroundColor = "#0056b3";
            e.currentTarget.style.transform = "translateY(-2px)";
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.backgroundColor = "#007bff";
            e.currentTarget.style.transform = "translateY(0)";
          }}
        >
          🎬 Start New Video Learning
        </button>
      </div>

      {/* Continue Learning Section */}
      {continueVideos.length > 0 && (
        <div style={{ marginBottom: "48px" }}>
          <h2 style={{
            fontSize: "24px",
            fontWeight: "600",
            color: "#2c3e50",
            marginBottom: "24px",
            display: "flex",
            alignItems: "center",
            gap: "8px"
          }}>
            📚 Continue Learning
          </h2>

          <div style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
            gap: "24px"
          }}>
            {continueVideos.slice(0, 4).map((video, index) => (
              <div
                key={index}
                onClick={() => onVideoSelect(video.videoId)}
                style={{
                  padding: "20px",
                  backgroundColor: "white",
                  borderRadius: "12px",
                  border: "1px solid #e9ecef",
                  boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
                  cursor: "pointer",
                  transition: "all 0.2s ease"
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.transform = "translateY(-4px)";
                  e.currentTarget.style.boxShadow = "0 8px 20px rgba(0,0,0,0.15)";
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.transform = "translateY(0)";
                  e.currentTarget.style.boxShadow = "0 2px 8px rgba(0,0,0,0.1)";
                }}
              >
                <div style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "flex-start",
                  marginBottom: "12px"
                }}>
                  <h3 style={{
                    fontSize: "16px",
                    fontWeight: "600",
                    color: "#2c3e50",
                    margin: "0",
                    lineHeight: "1.4"
                  }}>
                    {video.videoTitle}
                  </h3>
                  <div style={{
                    backgroundColor: "#007bff",
                    color: "white",
                    padding: "4px 8px",
                    borderRadius: "12px",
                    fontSize: "12px",
                    fontWeight: "600",
                    whiteSpace: "nowrap"
                  }}>
                    Session {video.currentSessionIndex + 1}/{video.totalSessions}
                  </div>
                </div>

                <div style={{
                  marginBottom: "12px"
                }}>
                  <div style={{
                    height: "6px",
                    backgroundColor: "#e9ecef",
                    borderRadius: "3px",
                    overflow: "hidden"
                  }}>
                    <div style={{
                      height: "100%",
                      backgroundColor: "#28a745",
                      borderRadius: "3px",
                      width: `${video.progress * 100}%`,
                      transition: "width 0.3s ease"
                    }} />
                  </div>
                  <div style={{
                    fontSize: "12px",
                    color: "#6c757d",
                    marginTop: "4px"
                  }}>
                    {Math.round(video.progress * 100)}% complete • {video.wordsLearned.length} words learned
                  </div>
                </div>

                <div style={{
                  fontSize: "12px",
                  color: "#adb5bd"
                }}>
                  Last watched: {formatDate(new Date(video.lastWatched))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommended Content */}
      <div style={{ marginBottom: "48px" }}>
        <h2 style={{
          fontSize: "24px",
          fontWeight: "600",
          color: "#2c3e50",
          marginBottom: "16px",
          display: "flex",
          alignItems: "center",
          gap: "8px"
        }}>
          ⭐ Recommended for You
        </h2>
        <p style={{
          fontSize: "16px",
          color: "#6c757d",
          marginBottom: "24px"
        }}>
          Curated content for {userProfile.estimatedLevel} level learners
        </p>

        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
          gap: "24px"
        }}>
          {recommendedVideos.map((video, index) => (
            <div
              key={index}
              onClick={() => onVideoSelect(video.url)}
              style={{
                padding: "20px",
                backgroundColor: "white",
                borderRadius: "12px",
                border: "1px solid #e9ecef",
                boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
                cursor: "pointer",
                transition: "all 0.2s ease"
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.transform = "translateY(-4px)";
                e.currentTarget.style.boxShadow = "0 8px 20px rgba(0,0,0,0.15)";
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.transform = "translateY(0)";
                e.currentTarget.style.boxShadow = "0 2px 8px rgba(0,0,0,0.1)";
              }}
            >
              <div style={{
                display: "flex",
                alignItems: "center",
                gap: "16px",
                marginBottom: "16px"
              }}>
                <div style={{
                  fontSize: "32px",
                  width: "60px",
                  height: "60px",
                  backgroundColor: "#f8f9fa",
                  borderRadius: "8px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  flexShrink: 0
                }}>
                  {video.thumbnail}
                </div>
                <div style={{ flex: 1 }}>
                  <h3 style={{
                    fontSize: "16px",
                    fontWeight: "600",
                    color: "#2c3e50",
                    margin: "0 0 4px 0",
                    lineHeight: "1.4"
                  }}>
                    {video.title}
                  </h3>
                  <div style={{
                    fontSize: "12px",
                    color: "#007bff",
                    fontWeight: "600"
                  }}>
                    {video.duration} • {userProfile.estimatedLevel} Level
                  </div>
                </div>
              </div>

              <p style={{
                fontSize: "14px",
                color: "#6c757d",
                margin: "0",
                lineHeight: "1.4"
              }}>
                {video.description}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Quick Actions */}
      <div style={{
        backgroundColor: "#f8f9fa",
        padding: "32px",
        borderRadius: "16px",
        border: "1px solid #e9ecef",
        textAlign: "center"
      }}>
        <h3 style={{
          fontSize: "20px",
          fontWeight: "600",
          color: "#2c3e50",
          marginBottom: "16px"
        }}>
          Quick Actions
        </h3>

        <div style={{
          display: "flex",
          justifyContent: "center",
          gap: "16px",
          flexWrap: "wrap"
        }}>
          <button
            onClick={onNewVideo}
            style={{
              padding: "12px 24px",
              backgroundColor: "white",
              color: "#495057",
              border: "1px solid #dee2e6",
              borderRadius: "8px",
              fontSize: "14px",
              fontWeight: "600",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "8px",
              transition: "all 0.2s ease"
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.backgroundColor = "#e9ecef";
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.backgroundColor = "white";
            }}
          >
            🔗 Paste YouTube URL
          </button>

          <button
            onClick={() => window.open('https://www.youtube.com/results?search_query=english+learning+' + userProfile.estimatedLevel, '_blank')}
            style={{
              padding: "12px 24px",
              backgroundColor: "white",
              color: "#495057",
              border: "1px solid #dee2e6",
              borderRadius: "8px",
              fontSize: "14px",
              fontWeight: "600",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "8px",
              transition: "all 0.2s ease"
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.backgroundColor = "#e9ecef";
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.backgroundColor = "white";
            }}
          >
            🔍 Find Videos on YouTube
          </button>

          <button
            onClick={() => console.log('View progress analytics')}
            style={{
              padding: "12px 24px",
              backgroundColor: "white",
              color: "#495057",
              border: "1px solid #dee2e6",
              borderRadius: "8px",
              fontSize: "14px",
              fontWeight: "600",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "8px",
              transition: "all 0.2s ease"
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.backgroundColor = "#e9ecef";
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.backgroundColor = "white";
            }}
          >
            📊 View Progress
          </button>
        </div>
      </div>
    </div>
  );
};

export default Homepage;