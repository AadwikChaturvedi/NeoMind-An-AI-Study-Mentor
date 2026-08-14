# NeoMind AI

> **Your Intelligent Study Companion for Focused Online Learning**

NeoMind AI is an AI-powered learning and productivity platform designed to help students stay focused during online learning. It combines study-session tracking, productivity analytics, webcam-based focus monitoring, and an AI mentor into a single application.

## 🎯 Problem Statement

Online learning gives students flexibility, but it also creates an environment where distractions can easily reduce concentration and productivity.

NeoMind AI aims to address this problem by monitoring study sessions, analyzing focus-related activity, and providing personalized guidance to help students build better study habits.

## ✨ Planned Features

### 📊 Dashboard

A centralized overview of the student's productivity, including:

* Total study time
* Focus score
* Number of study sessions
* Productivity statistics
* Recent activity

### ⏱️ Study Timer

Track focused study sessions with:

* Start / pause / resume / stop controls
* Session duration tracking
* Persistent study-session records
* Study history

### 🤖 AI Mentor

An AI-powered study companion using the Gemini API to:

* Motivate students
* Suggest study strategies
* Help students improve focus
* Provide personalized productivity advice

### 📹 Webcam Focus Monitoring

NeoMind uses computer vision to monitor study-session activity.

The planned monitoring system can track indicators such as:

* Whether a face is present
* Periods when the student is away
* Potential distraction periods
* Focus-related session statistics

The system is intended as a productivity aid rather than a medical or psychological assessment.

### 📈 Analytics

Visualize productivity trends through:

* Daily and weekly study hours
* Focus trends
* Distraction statistics
* Productivity scores

### 📄 Reports

Generate summaries of study performance, including:

* Total study time
* Average focus score
* Distraction statistics
* Productivity insights

## 🏗️ Technology Stack

| Component       | Technology                                  |
| --------------- | ------------------------------------------- |
| Frontend        | HTML, Tailwind CSS, JavaScript              |
| Backend         | Python, FastAPI                             |
| Database        | SQLite                                      |
| AI              | Gemini API                                  |
| Computer Vision | OpenCV                                      |
| ML Model        | PyTorch                                     |
| Charts          | Chart.js / equivalent visualization library |

## 📁 Project Architecture

```text
NeoMind/
│
├── frontend/
│   ├── pages/
│   ├── assets/
│   ├── css/
│   └── js/
│
├── backend/
│   ├── main.py
│   ├── routes/
│   ├── models/
│   ├── services/
│   └── database/
│
├── ai/
│   ├── mentor/
│   └── monitoring/
│
├── database/
│   └── neomind.db
│
├── .env.example
├── requirements.txt
└── README.md
```

## 🔐 Authentication

NeoMind is designed to support user accounts so that each student can maintain their own:

* Profile
* Study sessions
* Analytics
* Reports
* AI mentor interactions

Passwords should never be stored directly; authentication should use secure password hashing and token-based authorization.

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone <repository-url>
cd neomind
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file:

```env
GEMINI_API_KEY=your_gemini_api_key
JWT_SECRET_KEY=your_secret_key
```

### 5. Start the FastAPI backend

```bash
uvicorn backend.main:app --reload
```

### 6. Open the frontend

Serve the frontend using the project's configured frontend server or development setup.

## 🔒 Privacy

Webcam monitoring should be designed with privacy in mind. Camera processing should be limited to what is necessary for the focus-monitoring feature, and sensitive webcam data should not be unnecessarily stored.

## 🧪 Project Status

**Current status:** MVP in development.

The project is being developed incrementally, with the major components being integrated and tested individually before final deployment.

## 🎓 Academic Purpose

NeoMind AI is being developed as a **CBSE Class 12 Artificial Intelligence Capstone Project**. The project demonstrates the application of:

* Artificial Intelligence
* Machine Learning
* Computer Vision
* Generative AI
* Web Development
* Database Management

## 👥 Team

**Project:** NeoMind AI
**Type:** CBSE AI Capstone Project
**Institution:** Delhi Public School, Kalyanpur

---

### Future Improvements

Potential future enhancements include:

* Advanced attention estimation
* Personalized study recommendations
* More detailed productivity analytics
* Teacher/parent dashboards
* Improved AI-powered study planning
* Cross-device synchronization

---

**NeoMind AI — Study smarter. Stay focused. Learn better.**
