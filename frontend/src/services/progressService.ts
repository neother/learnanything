import { UserProfile, LearningProgress } from "../types";

export class ProgressService {
  private static PROGRESS_PREFIX = "progress_";
  private static PROFILE_KEY = "userProfile";

  // Save learning progress for a video
  static saveLearningProgress(userId: string, videoId: string, progress: Partial<LearningProgress>) {
    try {
      const progressKey = `${this.PROGRESS_PREFIX}${userId}`;
      const existingProgress = this.getAllUserProgress(userId);

      // Find existing progress for this video
      const videoIndex = existingProgress.findIndex(p => p.videoId === videoId);

      const updatedProgress: LearningProgress = {
        videoId,
        videoTitle: progress.videoTitle || 'Untitled Video',
        totalSessions: progress.totalSessions || 1,
        completedSessions: progress.completedSessions || 0,
        currentSessionIndex: progress.currentSessionIndex || 0,
        wordsLearned: progress.wordsLearned || [],
        timeSpent: progress.timeSpent || 0,
        lastWatched: new Date(),
        progress: progress.progress || 0
      };

      if (videoIndex >= 0) {
        // Update existing progress
        existingProgress[videoIndex] = {
          ...existingProgress[videoIndex],
          ...updatedProgress,
          wordsLearned: Array.from(new Set([...existingProgress[videoIndex].wordsLearned, ...updatedProgress.wordsLearned])),
          timeSpent: (existingProgress[videoIndex].timeSpent || 0) + (updatedProgress.timeSpent || 0)
        };
      } else {
        // Add new progress entry
        existingProgress.push(updatedProgress);
      }

      localStorage.setItem(progressKey, JSON.stringify(existingProgress));
      console.log('Progress saved for video:', videoId);

      // Update user profile stats
      this.updateUserStats(userId, updatedProgress.wordsLearned.length, updatedProgress.timeSpent || 0);

      return updatedProgress;
    } catch (error) {
      console.error('Error saving learning progress:', error);
      return null;
    }
  }

  // Get all learning progress for a user
  static getAllUserProgress(userId: string): LearningProgress[] {
    try {
      const progressKey = `${this.PROGRESS_PREFIX}${userId}`;
      const stored = localStorage.getItem(progressKey);
      if (stored) {
        const progress = JSON.parse(stored);
        // Convert date strings back to Date objects
        return progress.map((p: any) => ({
          ...p,
          lastWatched: new Date(p.lastWatched)
        }));
      }
      return [];
    } catch (error) {
      console.error('Error loading user progress:', error);
      return [];
    }
  }

  // Get progress for a specific video
  static getVideoProgress(userId: string, videoId: string): LearningProgress | null {
    const allProgress = this.getAllUserProgress(userId);
    return allProgress.find(p => p.videoId === videoId) || null;
  }

  // Update user profile statistics
  static updateUserStats(userId: string, newWordsLearned: number, additionalTime: number) {
    try {
      const storedProfile = localStorage.getItem(this.PROFILE_KEY);
      if (storedProfile) {
        const profile = JSON.parse(storedProfile);

        // Update stats
        profile.wordsLearned = Math.max(profile.wordsLearned, profile.wordsLearned + newWordsLearned);
        profile.totalStudyTime = (profile.totalStudyTime || 0) + additionalTime;
        profile.lastActiveAt = new Date();

        // Update streak logic
        const lastActive = new Date(profile.lastActiveAt);
        const today = new Date();
        const daysDiff = Math.floor((today.getTime() - lastActive.getTime()) / (1000 * 60 * 60 * 24));

        if (daysDiff === 0) {
          // Same day, maintain streak
        } else if (daysDiff === 1) {
          // Next day, increment streak
          profile.currentStreak = (profile.currentStreak || 0) + 1;
          profile.longestStreak = Math.max(profile.longestStreak || 0, profile.currentStreak);
        } else {
          // Gap in learning, reset streak
          profile.currentStreak = 1;
        }

        localStorage.setItem(this.PROFILE_KEY, JSON.stringify(profile));
        console.log('Updated user stats:', { wordsLearned: profile.wordsLearned, studyTime: profile.totalStudyTime });
      }
    } catch (error) {
      console.error('Error updating user stats:', error);
    }
  }

  // Get learning analytics
  static getLearningAnalytics(userId: string) {
    try {
      const allProgress = this.getAllUserProgress(userId);
      const profile = this.getUserProfile();

      const analytics = {
        totalVideos: allProgress.length,
        completedVideos: allProgress.filter(p => p.progress >= 1).length,
        inProgressVideos: allProgress.filter(p => p.progress > 0 && p.progress < 1).length,
        totalWordsLearned: profile?.wordsLearned || 0,
        totalStudyTime: profile?.totalStudyTime || 0,
        currentStreak: profile?.currentStreak || 0,
        longestStreak: profile?.longestStreak || 0,
        averageSessionTime: allProgress.length > 0
          ? allProgress.reduce((sum, p) => sum + (p.timeSpent || 0), 0) / allProgress.length
          : 0,
        recentActivity: allProgress
          .sort((a, b) => new Date(b.lastWatched).getTime() - new Date(a.lastWatched).getTime())
          .slice(0, 5),
        levelProgress: this.calculateLevelProgress(profile?.estimatedLevel || 'A2', profile?.wordsLearned || 0)
      };

      return analytics;
    } catch (error) {
      console.error('Error generating analytics:', error);
      return null;
    }
  }

  // Calculate progress towards next level
  private static calculateLevelProgress(currentLevel: string, wordsLearned: number) {
    const levelThresholds = {
      'A1': { min: 0, max: 500, next: 'A2' },
      'A2': { min: 500, max: 1000, next: 'B1' },
      'B1': { min: 1000, max: 2000, next: 'B2' },
      'B2': { min: 2000, max: 3500, next: 'C1' },
      'C1': { min: 3500, max: 5000, next: 'C2' },
      'C2': { min: 5000, max: 10000, next: 'Native' }
    };

    const level = levelThresholds[currentLevel as keyof typeof levelThresholds];
    if (!level) return { progress: 1, nextLevel: 'Unknown' };

    const progress = Math.min((wordsLearned - level.min) / (level.max - level.min), 1);
    return {
      progress: Math.max(0, progress),
      nextLevel: level.next,
      wordsToNext: Math.max(0, level.max - wordsLearned),
      currentLevelWords: wordsLearned - level.min
    };
  }

  // Get current user profile
  private static getUserProfile(): UserProfile | null {
    try {
      const stored = localStorage.getItem(this.PROFILE_KEY);
      if (stored) {
        return JSON.parse(stored);
      }
      return null;
    } catch (error) {
      console.error('Error loading user profile:', error);
      return null;
    }
  }

  // Export learning data (for backup/transfer)
  static exportUserData(userId: string) {
    try {
      const profile = this.getUserProfile();
      const progress = this.getAllUserProgress(userId);
      const analytics = this.getLearningAnalytics(userId);

      const exportData = {
        exportDate: new Date().toISOString(),
        version: "1.0",
        profile,
        progress,
        analytics
      };

      const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);

      const a = document.createElement('a');
      a.href = url;
      a.download = `smart-navigator-data-${userId}-${Date.now()}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      console.log('User data exported successfully');
      return true;
    } catch (error) {
      console.error('Error exporting user data:', error);
      return false;
    }
  }

  // Import learning data
  static async importUserData(file: File): Promise<boolean> {
    try {
      const text = await file.text();
      const importData = JSON.parse(text);

      if (importData.profile) {
        localStorage.setItem(this.PROFILE_KEY, JSON.stringify(importData.profile));
      }

      if (importData.progress && importData.profile) {
        const progressKey = `${this.PROGRESS_PREFIX}${importData.profile.id}`;
        localStorage.setItem(progressKey, JSON.stringify(importData.progress));
      }

      console.log('User data imported successfully');
      return true;
    } catch (error) {
      console.error('Error importing user data:', error);
      return false;
    }
  }

  // Clear all user data
  static clearUserData(userId: string) {
    try {
      const progressKey = `${this.PROGRESS_PREFIX}${userId}`;
      localStorage.removeItem(progressKey);
      localStorage.removeItem(this.PROFILE_KEY);
      console.log('User data cleared');
      return true;
    } catch (error) {
      console.error('Error clearing user data:', error);
      return false;
    }
  }
}