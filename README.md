# 🧠 NeoMind AI

> **An AI-powered study mentor designed to help students stay focused during online learning.**

NeoMind AI is a full-stack AI learning and productivity platform developed as a **CBSE Class 12 Artificial Intelligence Capstone Project** at **Delhi Public School, Kalyanpur**.

The project is designed around a simple problem: online learning provides flexibility, but maintaining concentration and tracking productive study time can be difficult.

NeoMind combines study-session tracking, productivity analytics, AI-powered mentoring, and a foundation for computer-vision-based focus monitoring into one application.

---

## 🎯 Problem Statement

Students increasingly depend on online classes and self-study platforms, but studying in front of a computer can introduce distractions and make it difficult to measure actual productivity.

NeoMind AI aims to provide a digital study companion that helps students:

- Track their study sessions
- Understand their study habits
- Monitor productivity trends
- Receive AI-powered study guidance
- Build more consistent study routines

---

# ✨ Features

## 📊 Dashboard

The dashboard provides a centralized overview of the student's study activity.

Planned metrics include:

- Total study time
- Study sessions
- Focus score
- Productivity statistics
- Recent activity

---

## ⏱️ Study Sessions

NeoMind provides infrastructure for recording study sessions.

Each session can contain information such as:

- Duration
- Distraction count
- Focus score
- Timestamp

Session data is stored in SQLite through the backend database layer.

---

## 🤖 AI Mentor

NeoMind includes a Gemini-powered AI mentor.

The mentor is designed to help students with:

- Study strategies
- Productivity advice
- Motivation
- Focus improvement
- General academic planning

The Gemini integration is handled through the FastAPI backend rather than exposing the API key directly to the frontend.

---

## 📈 Analytics

The analytics system is designed to turn study-session data into useful productivity information.

Potential metrics include:

- Daily study duration
- Weekly study duration
- Focus trends
- Distraction statistics
- Productivity trends

---

## 📄 Reports

NeoMind includes a reporting system for generating summaries of study activity.

Reports can be used to review:

- Study duration
- Focus performance
- Productivity information
- Session history

PDF generation is supported through `fpdf2`.

---

## 📹 Computer Vision Focus Monitoring

A computer-vision component is being developed separately for NeoMind.

The planned monitoring system is intended to identify focus-related signals such as:

- Face presence
- Periods when the student is away
- Potential distraction periods
- Focus-related session metrics

The project uses **OpenCV** and **PyTorch** for this component.

> ⚠️ Webcam monitoring is an active development component and should not be considered fully integrated into the current application unless the corresponding monitoring service is present and connected.

The system is intended as a **productivity aid**, not as a medical, psychological, or behavioral diagnosis.

---

# 🏗️ Technology Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Templates | Jinja2 |
| Backend | Python + FastAPI |
| Database | SQLite |
| ORM | SQLAlchemy |
| Generative AI | Google Gemini API |
| Computer Vision | OpenCV |
| Machine Learning | PyTorch |
| PDF Reports | fpdf2 |

---

# 📁 Project Structure

```text
NeoMind-An-AI-Study-Mentor/
│
├── backend/
│   └── app/
│       ├── main.py
│       ├── config.py
│       ├── database.py
│       │
│       ├── models/
│       │   ├── user.py
│       │   ├── study_session.py
│       │   └── report.py
│       │
│       ├── schemas/
│       │   ├── user.py
│       │   ├── study_session.py
│       │   └── report.py
│       │
│       ├── routes/
│       │   ├── health.py
│       │   ├── sessions.py
│       │   ├── mentor.py
│       │   ├── analytics.py
│       │   └── reports.py
│       │
│       ├── services/
│       │   ├── gemini_service.py
│       │   └── analytics_service.py
│       │
│       └── utils/
│           └── helpers.py
│
├── frontend/
│   ├── templates/
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── timer.html
│   │   ├── mentor.html
│   │   ├── analytics.html
│   │   └── reports.html
│   │
│   └── static/
│       ├── css/
│       │   └── style.css
│       ├── js/
│       │   ├── dashboard.js
│       │   ├── timer.js
│       │   ├── mentor.js
│       │   ├── analytics.js
│       │   └── reports.js
│       └── images/
│
├── neomind.db
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
 ```


## 📌 Project Status

**Status: Active Development 🚧**

NeoMind AI is currently being developed as a Class 12 Artificial Intelligence capstone project.

The core application structure and major modules are being developed incrementally. Some features are functional, while others are still under development and integration.

### Current Development Areas

- ✅ FastAPI backend architecture
- ✅ SQLite database integration
- ✅ Dashboard interface
- ✅ Study session/timer functionality
- ✅ AI Mentor interface
- ✅ Analytics module
- ✅ Report generation structure
- 🚧 User authentication
- 🚧 Webcam-based focus monitoring
- 🚧 Computer vision integration with the main application
- 🚧 Final UI/UX refinement
- 🚧 End-to-end testing

The project is intentionally being developed in stages so that each module can be tested independently before being integrated into the complete system.

---

# 🔮 Future Development

NeoMind AI is designed to be expandable beyond its current capstone implementation.

Possible future improvements include:

### 🧠 Advanced AI Personalization

- Personalized study recommendations based on previous study sessions
- Adaptive study plans based on academic goals
- AI-generated revision strategies
- Identification of frequently asked or weak topics
- More context-aware AI mentoring

### 👁️ Advanced Focus Monitoring

The current computer-vision concept can be expanded to provide more meaningful study-session insights.

Possible improvements include:

- Face presence detection
- Attention direction estimation
- Eye-closure detection
- Distraction-duration tracking
- Focus-score calculation
- Distraction frequency analysis
- Session-level attention analytics

Future versions could combine these signals to provide a more complete picture of a student's study habits.

### 📊 Advanced Analytics

Future versions could introduce:

- Weekly and monthly productivity trends
- Subject-wise study analysis
- Focus-score trends
- Study consistency tracking
- Personalized productivity insights
- Long-term progress visualization

### 💬 Improved AI Mentor

The AI Mentor could eventually support:

- Doubt solving
- Topic explanations
- Revision assistance
- Quiz generation
- Flashcard generation
- Personalized motivation
- Study-plan generation

### 📱 Cross-Platform Development

A future version could potentially be converted into:

- Progressive Web App (PWA)
- Android application
- Desktop application

This would allow students to use NeoMind across multiple devices.

### 🔐 Security & Privacy Improvements

As the project grows, additional security features could include:

- Improved authentication and authorization
- Secure password management
- Better session management
- User-specific data isolation
- Improved protection of study analytics
- Privacy-focused webcam processing

---

# 🎓 Academic Context

NeoMind AI is being developed as a **Class 12 Artificial Intelligence capstone project**.

The project focuses on applying concepts from Artificial Intelligence, Computer Vision, Natural Language Processing, data handling, and software development to solve a practical problem faced by students.

### Problem Identified

With the increasing use of online classes, video lectures, online coaching platforms, and digital study resources, students often have difficulty maintaining concentration for extended periods.

Traditional study applications generally provide timers or productivity statistics, but they may not actively respond to a student's study behavior.

### Proposed Solution

NeoMind AI aims to combine:

> **Study Management + Artificial Intelligence + Computer Vision + Analytics**

into a single learning companion.

The system is intended to help students:

- Maintain focused study sessions
- Monitor their study habits
- Understand their productivity patterns
- Receive AI-based assistance
- Review their study performance
- Build more consistent study habits

### Educational Objective

The project also serves as an opportunity to demonstrate practical implementation of concepts learned through the Artificial Intelligence curriculum, including:

- Problem identification
- Data handling
- Artificial Intelligence
- Machine Learning concepts
- Computer Vision
- Natural Language Processing
- Data analysis
- Software development
- Human-computer interaction

---
