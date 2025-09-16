
The new document is now a complete, developer-ready Product Requirements Document (PRD) tailored for a coding AI. It reflects the strategic pivot to an adult-focused learning workstation, details the entire user journey with UI states and interaction logic, and outlines the updated technical architecture.

Here is the fully updated file:

-----

# Immersive Language Learning Workstation (Project Navigator)

A web-based, AI-powered language learning workstation for adults and advanced students, designed to turn any YouTube video into an adaptive, context-rich lesson.

## Project Overview

**Purpose:** To help serious learners achieve language fluency by providing a powerful tool that transforms passive video consumption into an efficient, active learning process. The system acts as an intelligent **"Smart Navigator"**, guiding users through authentic content.

**Target Audience:** Adults and students preparing for exams (IELTS, TOEFL), enhancing professional skills, or pursuing advanced language mastery.

**Tech Stack:**

  - **Frontend:** React with TypeScript
  - **Backend:** FastAPI with Python
  - **AI Integration:** LLM APIs (e.g., GPT-4, Claude) for dynamic analysis, quizzes, and tutoring.
  - **Styling:** CSS3 with modern responsive design (Dark Mode first).
  - **Development:** Node.js, npm, Python virtual environment.

## Current Status: Foundational Tech Complete, Ready for "Navigator" Implementation

### ✅ **Completed Foundational Features**

#### **Backend Processing Engine:**

  - **Real YouTube subtitle extraction** via YouTube Transcript API + yt-dlp fallback.
  - **Advanced 5-step subtitle processing pipeline** for clean, coherent sentences.
  - **CEFR-based vocabulary classification** (A1→C2) with a 16,000+ word database.
  - **Intelligent proper noun filtering** to skip names, places, and brands.
  - **Chinese translation system** with local caching.
  - **Robust subtitle caching system** (7-day expiration) for high performance.

#### **Frontend User Experience:**

  - **✅ Left-Right Split Layout** - Video player on left, learning content on right.
  - **✅ Interactive word playback** - Click word → jump to video timestamp → auto-stop.
  - **✅ Visual feedback system** - Pulse animations and "🔊 Playing" indicators.
  - **✅ Clean TypeScript architecture** with no compilation errors.

-----

### 🎯 **Product Blueprint: The "Smart Navigator" Model**

This is the complete specification for the next development phase. The goal is to create a single, unified, system-led experience that is powerful, intelligent, and respects the user's focus.

#### **1.0 First-Time User Onboarding**

**Goal:** Quickly establish a baseline `User Vocabulary Profile` to enable personalization from the very first session.

  * **UI - Welcome Screen:**
    ```
    +--------------------------------------+
    |         Welcome to [Product Name]    |
    |  Turn your favorite videos into      |
    |         your personal course.        |
    |                                      |
    | [ Take a 2-min quiz to personalize ] |
    +--------------------------------------+
    ```
  * **UI - Quick Vocabulary Assessment:**
      * A 10-15 question quiz with adaptive difficulty (multiple choice).
      * Based on performance, the system assigns an initial `estimatedLevel` (e.g., "B1") to the user's profile.

#### **2.0 Homepage / Content Discovery**

**Goal:** Allow users to easily find content and resume their learning journey.

  * **UI - Homepage:**
    ```
    +------------------------------------------------------+
    | [Logo]  [ Paste YouTube URL or search... ]    [Profile]|
    +------------------------------------------------------+
    |                                                      |
    |  Continue Learning                                   |
    |  +-----------------+  +-----------------+            |
    |  | Video A         |  | Video B         |            |
    |  | [Session 2/3 ]  |  | [Completed    ] |            |
    |  +-----------------+  +-----------------+            |
    |                                                      |
    |  Recommended for You                                 |
    |  +-----------------+  +-----------------+            |
    |  | Video C         |  | Video D         |            |
    |  | [15 min] [B2]   |  | [8 min] [B1]    |            |
    |  +-----------------+  +-----------------+            |
    +------------------------------------------------------+
    ```
  * **Logic:** The "Continue Learning" section is dynamically populated with videos that have incomplete `Learning Sessions`.

#### **3.0 The Core Learning Experience**

This is the heart of the application, detailing the entire user interaction flow within the learning interface.

**3.1 Pre-Session Adjustment**

  * **Trigger:** User selects a new video. The backend generates and returns `Session 1`.
  * **UI - Learning Panel (Preview State):**
    ```
    +-------------------------------------------+
    |  Focus Words (Session 1/3)                |
    |  ---------------------------------------  |
    |  [✓] vibrant   [adj] full of energy       |
    |  [✓] culture   [n]   customs, and beliefs |
    |  [✓] economy   [n]   wealth and resources |
    |  ...                                      |
    |  ---------------------------------------  |
    |  [           ▶ Start Watching           ]  |
    +-------------------------------------------+
    ```
  * **Interaction:**
    1.  User reviews the word list and can click the **[✓]** button for any word they already know.
    2.  **System Response:** The system marks the word as "mastered" and immediately attempts to **find a replacement word** from the same video segment (**Smart Replacement**).
    3.  **Edge Case:** If all words are marked as known, the panel changes to offer the user a choice: **"Increase Challenge"** (find harder words/phrases) or **"Immerse"** (watch without learning prompts).
    4.  User clicks "Start Watching" to begin.

**3.2 The "Smart Micro-Pause" Playback Experience**

  * **UI State A - Cruising State (Between words):**
      * The Learning Panel is **minimalist**, showing only the previously learned word as a reminder. The video plays continuously.
    <!-- end list -->
    ```
    +-------------------------------------------+
    |      Previously...                        |
    |      -------------------                  |
    |      vibrant                            |
    +-------------------------------------------+
    ```
  * **UI State B - Focus & Learn State (At a word):**
      * **Trigger:** The video reaches the `startTime` of a focus word.
      * **System Action (Smart Micro-Pause):**
        1.  The video **automatically pauses**.
        2.  The Learning Panel **expands** into a full "Learning Card" with the word, sentence, AI analysis, etc.
        3.  The card bottom shows a **[ Start Practice → ]** button.
      * **User Interaction:**
        1.  User reads the card and clicks **[ Start Practice → ]**.
        2.  The card switches to the **AI Tutor** module for a conversational review.
        3.  After the review, the button becomes **[ ✓ Finish & Continue ]**.
      * **System Action (Post-Practice Replay & Resume):**
        1.  When the user clicks **[ ✓ Finish & Continue ]**, the video **automatically replays** the short clip containing the focus word.
        2.  After the clip, the video **resumes** from where it was paused.
        3.  The Learning Panel reverts to the minimalist "Cruising State".

**3.3 Session Completion & Check-in**

  * **Trigger:** The user completes the learning loop for the last focus word in the current session.
  * **System Action:** A non-intrusive notification appears: **"🎉 Daily Learning Task Complete\!"**. The user's daily streak is updated.

## Quick Start

**Windows:**

```cmd
start-dev.bat
```

**Linux/Mac:**

```bash
./start-dev.sh
```

## Technical Architecture (Updated)

### **Frontend Architecture**

The UI will be broken down into a logical, feature-based component structure to ensure maintainability and scalability.

```
src/
├── App.tsx             # Main router and layout container
├── components/         # Reusable, stateless UI elements (Button, Icon, etc.)
├── features/           # Feature-based components with state and logic
│   ├── VideoPlayer/
│   │   └── VideoPlayer.tsx
│   ├── LearningPanel/
│   │   ├── LearningPanel.tsx   # Main state manager for the panel
│   │   ├── states/             # Components for each panel state
│   │   │   ├── PreviewState.tsx
│   │   │   ├── CruisingState.tsx
│   │   │   ├── FocusState.tsx
│   │   │   └── SummaryState.tsx
│   │   └── AITutor.tsx         # The AI chat component for review
│   └── Onboarding/
│       └── VocabularyQuiz.tsx
├── hooks/              # Custom hooks (e.g., useVideoPlayer.ts)
├── services/           # API call definitions (e.g., api.ts)
└── types/              # TypeScript interfaces (e.g., Session.ts)
```

### **Backend Architecture**

```
backend/
├── main.py              # FastAPI application, routes, and API endpoints
├── processing/          # Modules for video/subtitle processing
│   └── session_generator.py
├── models/              # Pydantic models for data structures
├── services/            # Business logic (e.g., interacting with AI APIs)
└── requirements.txt     # Python dependencies
```

## Future Development Roadmap (Revised)

### **Phase 1: Smart Navigator MVP (Current Focus)**

  - [ ] Full implementation of the End-to-End User Flow described above.
  - [ ] User authentication and profiles (`User Vocabulary Profile`).
  - [ ] "Continue Learning" persistence.

### **Phase 2: Power User Features & Exploration**

  - [ ] **Global Explore Mode:** A site-wide search engine to find any word/phrase across all of YouTube (the "YouGlish" competitor).
  - [ ] **Personal Knowledge Base:** Advanced note-taking on words and sentences.
  - [ ] **Custom Decks:** Allow users to save words into personalized study decks.

### **Phase 3: Platform Expansion**

  - [ ] Multi-language support (Spanish, French, German).
  - [ ] A premium, native mobile app for on-the-go review and spaced repetition.
  - [ ] Advanced analytics and progress tracking dashboard.



以下是上面的中文翻译版本。
# 中文参考版本。

这份文档详尽、完整，可以直接作为您和AI开发人员协作的中文蓝图。

-----

# 沉浸式语言学习工作站 (项目代号：领航员)

一个为成人和高阶学生设计的、基于Web的、由AI驱动的语言学习工作站，旨在将任何YouTube视频转化为自适应的、富含语境的课程。

## 项目概览

**宗旨：** 通过提供一个强大的工具，将用户被动的视频消费转化为高效、主动的学习过程，帮助严肃学习者实现语言流利。本系统将作为一个智能的\*\*“领航员 (Smart Navigator)”\*\*，引导用户学习真实世界的内容。

**目标用户：** 备考（雅思/托福）、提升专业技能或追求高级语言能力的成人和学生。

**技术栈:**

  - **前端:** React with TypeScript
  - **后端:** FastAPI with Python
  - **AI集成:** LLM APIs (如 GPT-4, Claude) 用于动态分析、测验和辅导。
  - **样式:** CSS3 结合现代响应式设计（优先深色模式）。
  - **开发环境:** Node.js, npm, Python virtual environment。

## 当前状态: 基础技术完备，准备实施“领航员”方案

### ✅ **已完成的基础功能**

#### **后端处理引擎:**

  - 通过 YouTube Transcript API + yt-dlp 备用方案实现**真实的YouTube字幕提取**。
  - **高级的5步字幕处理流水线**，用于生成干净、连贯的句子。
  - 基于**CEFR的词汇分类**（A1→C2），拥有16,000+的词汇数据库。
  - **智能专有名词过滤**，可跳过人名、地名和品牌。
  - 带有本地缓存的**中文翻译系统**。
  - 高性能的**字幕缓存系统**（7天过期）。

#### **前端用户体验:**

  - **✅ 左右分栏布局** - 左侧视频播放器，右侧学习内容。
  - **✅ 单词交互播放** - 点击单词 → 跳转到视频时间点 → 自动停止。
  - **✅ 视觉反馈系统** - 脉冲动画和“🔊 播放中”指示器。
  - **✅ 干净的TypeScript架构**，无编译错误。

-----

### 🎯 **产品蓝图：“智能领航”模式 (Smart Navigator Model)**

这是下一开发阶段的完整规范。目标是创建一个统一的、由系统主导的体验，既强大又毫不费力。

#### **1.0 首次用户引导流程**

**目标:** 快速建立一个基准的`用户词汇画像`，以便从第一个学习会话开始就实现个性化。

  * **UI - 欢迎屏幕:**
    ```
    +--------------------------------------+
    |         欢迎来到 [产品名称]          |
    |    将您喜爱的视频变成您的专属课程      |
    |                                      |
    |      [  花2分钟，定制您的学习路径 → ]    |
    +--------------------------------------+
    ```
  * **UI - 快速词汇量评估:**
      * 一个10-15题、难度自适应的多项选择题。
      * 系统根据测试表现，为用户的个人资料分配一个初始的 `estimatedLevel` (例如 "B1")。

#### **2.0 主界面 / 内容发现**

**目标:** 让用户可以轻松找到内容并继续他们的学习之旅。

  * **UI - 主界面:**
    ```
    +------------------------------------------------------+
    | [Logo]  [  粘贴YouTube链接或搜索... ]        [头像]     |
    +------------------------------------------------------+
    |                                                      |
    |  继续学习                                            |
    |  +-----------------+  +-----------------+            |
    |  | 视频 A          |  | 视频 B          |            |
    |  | [学习会话 2/3 ]   |  | [已完成       ] |            |
    |  +-----------------+  +-----------------+            |
    |                                                      |
    |  为您推荐                                            |
    |  +-----------------+  +-----------------+            |
    |  | 视频 C          |  | 视频 D          |            |
    |  | [15分钟] [B2]   |  | [8分钟] [B1]    |            |
    |  +-----------------+  +-----------------+            |
    +------------------------------------------------------+
    ```
  * **逻辑:** “继续学习”部分动态展示包含未完成的`学习会话`的视频。

#### **3.0 核心学习体验**

这是应用的核心，详细说明了在学习界面内的完整用户交互流程。

**3.1 课前调整**

  * **触发:** 用户选择一个新视频。后端生成并返回`会话1`。
  * **UI - 学习面板 (预览状态):**
    ```
    +-------------------------------------------+
    |  本次学习焦点 (会话 1/3)                   |
    |  ---------------------------------------  |
    |  [✓] vibrant   [形容词] 充满活力的          |
    |  [✓] culture   [名词] 文化                 |
    |  ...                                      |
    |  ---------------------------------------  |
    |  [           ▶ 开始观看视频           ]  |
    +-------------------------------------------+
    ```
  * **交互:**
    1.  用户审阅单词列表，可以点击已知单词旁的 **[✓]** 按钮。
    2.  **系统响应:** 系统将该词标记为“已掌握”，并立即尝试**寻找一个替换词** (**智能替换**)。
    3.  **边缘场景:** 如果所有词都被标记为已知，面板将变化并提供选项：**“提升挑战”** (寻找更难的词汇或短语) 或 **“沉浸观看”** (无干扰观看)。
    4.  用户点击“开始观看视频”。

**3.2 “智能微暂停”播放体验**

  * **UI 状态 A - 同航状态 (单词之间):**
      * 学习面板**最小化**，只显示上一个学过的单词作为提醒。视频连续播放。
    <!-- end list -->
    ```
    +-------------------------------------------+
    |      上一个词...                          |
    |      -------------------                  |
    |      vibrant                            |
    +-------------------------------------------+
    ```
  * **UI 状态 B - 焦点学习状态 (遇到单词时):**
      * **触发:** 视频到达一个焦点词的`startTime`。
      * **系统动作 (智能微暂停):**
        1.  视频**自动暂停**。
        2.  学习面板**扩展**为完整的“学习卡片”，包含单词、原句、AI分析等。
        3.  卡片底部显示一个 **[ 开始练习 → ]** 按钮。
      * **用户交互:**
        1.  用户阅读卡片，然后点击 **[ 开始练习 → ]**。
        2.  卡片切换到**AI老师**模块，进行对话式复习。
        3.  复习后，按钮变为 **[ ✓ 完成并继续 ]**。
      * **系统动作 (学后回放与恢复):**
        1.  当用户点击 **[ ✓ 完成并继续 ]** 时，视频**自动回放**包含该焦点词的短片。
        2.  短片播完后，视频从暂停处**恢复播放**。
        3.  学习面板恢复到最小化的“同航状态”。

**3.3 会话完成与打卡**

  * **触发:** 用户完成了当前会话中最后一个焦点词的学习循环。
  * **系统动作:** 一个非打扰性的通知出现：“🎉 **今日学习任务完成！**”。用户的每日打卡记录被更新。

## 快速上手

**Windows:**

```cmd
start-dev.bat
```

**Linux/Mac:**

```bash
./start-dev.sh
```

## 技术架构 (更新后)

### **前端架构**

UI将拆分为逻辑化的、基于特性的组件结构，以确保可维护性和可扩展性。

```
src/
├── App.tsx             # 主路由和布局容器
├── components/         # 可复用的、无状态的UI元素 (Button, Icon等)
├── features/           # 基于特性的组件，包含状态和逻辑
│   ├── VideoPlayer/
│   │   └── VideoPlayer.tsx
│   ├── LearningPanel/
│   │   ├── LearningPanel.tsx   # 面板的主状态管理器
│   │   ├── states/             # 对应面板各状态的组件
│   │   │   ├── PreviewState.tsx
│   │   │   ├── CruisingState.tsx
│   │   │   ├── FocusState.tsx
│   │   │   └── SummaryState.tsx
│   │   └── AITutor.tsx         # 用于复习的AI聊天组件
│   └── Onboarding/
│       └── VocabularyQuiz.tsx
├── hooks/              # 自定义钩子 (e.g., useVideoPlayer.ts)
├── services/           # API调用定义 (e.g., api.ts)
└── types/              # TypeScript接口 (e.g., Session.ts)
```

### **后端架构**

```
backend/
├── main.py              # FastAPI应用、路由和API端点
├── processing/          # 用于视频/字幕处理的模块
│   └── session_generator.py
├── models/              # Pydantic数据模型
├── services/            # 业务逻辑 (e.g., 与AI API交互)
└── requirements.txt     # Python依赖
```

## 🚧 Development Status & Progress Tracking

**Last Updated:** 2025-01-16 04:30 UTC
**Current Session:** 🎉 **Phase 1 COMPLETE - Smart Navigator Learning System Fully Implemented!** 🎉

### Phase Progress:
- [x] **Phase 0: Foundation Complete** (100% - ✅ DONE)
  - [x] YouTube subtitle extraction with deduplication fix
  - [x] CEFR vocabulary classification system
  - [x] Left-right split layout UI
  - [x] Interactive word playback functionality
  - [x] Configurable backend API URLs
  - [x] Chinese translation system with caching
- [x] **Phase 1: Core Learning Experience** (100% - ✅ **COMPLETE**)
  - [x] **Phase 1.1: Restructure Frontend Architecture** (App.tsx → feature-based components) ✅ **COMPLETE**
  - [x] **Phase 1.2: Smart Session System** (3-5 word learning chunks + intelligent word replacement) ✅ **COMPLETE**
  - [x] **Phase 1.3: Smart Micro-Pause Video Experience** (auto-pause at focus words with enhanced UI) ✅ **COMPLETE**
  - [x] **Phase 1.4: Enhanced AI Tutor Integration** (conversational learning with interactive chat) ✅ **COMPLETE**
- [ ] **Phase 2: User Experience** (0% - ⏸️ PENDING)
  - [ ] User Onboarding & Vocabulary Assessment
  - [ ] Homepage & Content Discovery
  - [ ] Learning State Management & Progress Persistence
- [ ] **Phase 3: Data & Intelligence** (0% - ⏸️ PENDING)
  - [ ] User Authentication & Profiles
  - [ ] Learning Analytics Database
  - [ ] Smart Session Generation Algorithms

### Current Work Status:
✅ **🎊 MAJOR MILESTONE ACHIEVED:** Phase 1 - Smart Navigator Learning System COMPLETE!
🎯 **Ready for Next Phase:** Phase 2 - User Experience Implementation
⏭️ **Next Priority:** User Onboarding & Vocabulary Assessment system
🚀 **System Status:** Fully functional Smart Navigator with all core learning features

### Session History:
- **2025-01-16 Session 1**:
  - ✅ Fixed YouTube Transcript API syntax (`api.fetch()` → `YouTubeTranscriptApi.get_transcript()`)
  - ✅ Added subtitle deduplication logic to handle YouTube API overlapping segments
  - ✅ Implemented configurable backend URLs with .env file for device switching
  - ✅ Added comprehensive progress tracking system to CLAUDE.md
- **2025-01-16 Session 2** - **🎉 MAJOR MILESTONE**:
  - ✅ **Complete Frontend Architecture Restructure** - Transformed 650+ line monolithic App.tsx into feature-based components
  - ✅ **Created Feature Components**: VideoPlayer, LearningPanel (with 4 states), AITutor
  - ✅ **Built Component States**: PreviewState, CruisingState, FocusState, SummaryState
  - ✅ **Added Custom Hooks**: useVideoPlayer for video logic separation
  - ✅ **Created API Services**: Centralized API calls in services/api.ts
  - ✅ **TypeScript Integration**: Full type safety with comprehensive interfaces
  - ✅ **Build Verification**: Clean compilation with only minor ESLint warnings
  - 🎯 **Status**: Phase 1.1 Complete - Ready for Smart Session System
- **2025-01-16 Session 3** - **🚀 SMART NAVIGATOR IMPLEMENTATION COMPLETE**:
  - ✅ **Phase 1.2: Smart Session System** - Backend session generation algorithm with CEFR-based word grouping
  - ✅ **Intelligent Word Replacement API** - Dynamic word replacement when users master vocabulary
  - ✅ **Session-based Learning UI** - Preview state with focus words and mastery tracking
  - ✅ **Phase 1.3: Smart Micro-Pause Video Experience** - Automatic video pausing at focus words with timing precision
  - ✅ **Enhanced Learning States** - Cruising state with next-word preview and improved visual feedback
  - ✅ **useSmartMicroPause Hook** - Custom hook for intelligent video monitoring and state management
  - ✅ **Phase 1.4: Enhanced AI Tutor Integration** - Interactive conversational learning with contextual responses
  - ✅ **AI Teacher Pattern Recognition** - Intelligent response generation based on user question types
  - ✅ **Chat-style Learning Interface** - Real-time conversation with AI tutor including quick-action buttons
  - ✅ **Comprehensive Helper Functions** - 15+ helper functions for contextual AI responses
  - ✅ **Build Verification**: Clean TypeScript compilation with successful build
  - 🎉 **MILESTONE**: Phase 1 Smart Navigator Learning System **FULLY COMPLETE**

---

## 未来发展路线图 (修订后)

### **第一阶段: 智能领航MVP (当前焦点)**

  - [ ] 完整实现上述端到端用户流程。
  - [ ] 用户认证和个人档案 (`用户词汇画像`)。
  - [ ] "继续学习"功能的持久化。

### **第二阶段: 高级用户功能与探索**

  - [ ] **全局探索模式:** 一个网站级的搜索引擎，用于在所有YouTube视频中查找任何单词/短语。
  - [ ] **个人知识库:** 在单词和句子上进行高级笔记。
  - [ ] **自定义词库:** 允许用户将单词存入个性化学习集。

### **第三阶段: 平台扩展**

  - [ ] 多语言支持 (西班牙语, 法语, 德语)。
  - [ ] 用于移动端复习和间隔重复的高级原生App。
  - [ ] 高级数据分析和进度追踪仪表盘。

- when you think you have completed anything and want me to review or confirm, please check the log files to ensure there is no error on both front end and backend. backend.log and frontend.log.

- you will have all the acces in this project folder if you need run any command don't ask again.