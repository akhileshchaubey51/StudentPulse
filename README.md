# Student Pulse 🎓
## AI-Powered Student Career Development, Skill Tracking, Placement Preparation & KIET Group of Institutions Portal

[![Live App on Render](https://img.shields.io/badge/Render-Live%20Deployment-00C0FF?style=for-the-badge&logo=render&logoColor=white)](https://student-pulse-esbc.onrender.com)
[![GitHub Repository](https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/akhileshchaubey51/StudentPulse)
[![Python Version](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.14-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)

---

### 🌐 Live Production Application

> 🚀 **Live URL:** **[https://student-pulse-esbc.onrender.com](https://student-pulse-esbc.onrender.com)**  
> Hosted on **Render** (Production WSGI with Gunicorn & automatic database synchronization).

---

### Overview

**Student Pulse** is an enterprise-grade, integrated web application connecting **Students**, **Faculty Mentors**, and **Institutional Administrators** through one centralized relational database and authentication system.

The platform answers four vital questions for student career readiness:
1. **What skills does a student currently have?** (Skill Tracker & Benchmarks)
2. **What skills do companies currently require?** (Company Requirements Analyzer & Skill Gaps)
3. **What should the student learn next?** (AI Study Planner & Custom Sprints)
4. **How consistently is the student preparing?** (GitHub/LeetCode-style Contribution Heatmap & Streak Tracker)

---

### Core Architecture & Tech Stack

- **Backend:** Python 3.10+ / Flask Application Factory Architecture
- **Database:** SQLite (`database/student_pulse.db`) via SQLAlchemy ORM
- **Authentication:** Werkzeug password hashing & Flask-Login with role-based access control
- **Frontend:** HTML5, CSS3, Bootstrap 5, Bootstrap Icons, Chart.js
- **Typography:** Times New Roman (`'Times New Roman', Times, Georgia, serif`) with enlarged readability scale
- **Supported Degree Programs:** B.Tech, BCA, MCA, B.Pharma, BBA, MBA, B.Sc
- **Campus Placement Drives:** Live recruitment announcements, package CTC, program eligibility, and 1-click student applications
- **Design System:** Light grey background (`#F1F3F4`), white rounded cards (`#FFFFFF`), green (`#2DBE65`), yellow (`#F5B91B`), red (`#E94343`)
- **Contribution Heatmap:** 52-week x 7-day contribution grid with intensity tiers (`#F1F3F4`, `#DDF5E5`, `#A8DFAF`, `#59C77C`, `#218C4A`)
- **AI Integration:** Local Ollama runtime (`qwen2.5-coder:1.5b`) with an offline, deterministic **Rule-Based Engine Fallback** so 100% of features work out-of-the-box.

---

### Three Unified Role-Based Portals

#### 1. Student Portal
- **Dashboard:** Real-time statistics, circular/horizontal proficiency indicators, upcoming deadlines, faculty feedback, and the **365-day Contribution Heatmap & Streak Tracker**.
- **Skill Tracker:** Technical (Python, Java, DSA, SQL, OOPS, Web) & Soft Skills tracking, proficiency levels, and self/verified ratings.
- **Company Requirements:** Verified placement tracks for TCS, Infosys, Wipro, Google, Microsoft, Accenture, etc.
- **AI Skill Gap Analyzer:** Side-by-side gap analysis categorizing Strong, Weak, and Missing skills, accompanied by a readiness score and preparation roadmap.
- **AI Study Planner:** Generates realistic daily and weekly tasks based on actual weekly hours and skill gaps. Completing tasks automatically logs activities and drives streaks.
- **Project Tracker:** Academic, capstone, and personal projects with milestone tracking and 1-click submission for faculty code review.
- **Coding & Aptitude:** Interactive timed assessments with instant scoring, answer explanations, and accuracy tracking.
- **Interview Preparation:** Technical & HR interview question bank with AI mock response evaluations.
- **Resume Builder:** Auto-compiles verified academic credentials, skills, and projects into a clean print/PDF view.
- **Progress Analytics:** Historical Chart.js trends, weekly study hours, and activity distribution.
- **Notifications:** In-app reminders and faculty feedback notifications.

#### 2. Faculty Portal
- **Dashboard:** Cohort overview, active vs inactive count, at-risk student warnings with explicit diagnostic reasons.
- **Assigned Student Roster:** Filter by department, semester, and batch.
- **Student Monitoring:** Inspect individual student heatmaps, streaks, study plan completion, skills, and projects.
- **Mentorship Tools:** Assign weekly learning targets with deadlines, provide feedback with at-risk flags, and review submitted projects with grades (A/B/C) and ratings (1-5).

#### 3. Administrator Console
- **User Management:** Provision students and faculty, deactivate/reactivate accounts, manage roles.
- **Academic Hierarchy:** Departments, courses, semesters, batches, sections, and faculty batch assignments.
- **Company Catalog:** Register companies, add campus job roles, and map required skills with weights.
- **Assessment Management:** Question bank for DSA, Python, Java, SQL, and Aptitude tests.
- **Institutional Analytics:** Enrolled student count, faculty mentors, active streaks across campus, and department statistics.

---

### Windows 10/11 Installation & Execution Guide

Follow these beginner-friendly steps to launch Student Pulse on any Windows 10 or 11 system:

#### Step 1: Open Terminal in Project Directory
Open **PowerShell** or **Command Prompt** and navigate to the project directory:
```powershell
cd C:\Users\hp\.gemini\antigravity\scratch\student-pulse
```

#### Step 2: Create and Activate Python Virtual Environment
```powershell
python -m venv venv
venv\Scripts\activate
```

#### Step 3: Install Required Dependencies
```powershell
pip install -r requirements.txt
```

#### Step 4: Initialize and Seed Database
Populate the database with all 14 core modules, verified companies, question banks, academic structures, and pre-configured test users:
```powershell
python seed.py
```

#### Step 5: Start the Student Pulse Web Server
```powershell
python app.py
```

#### Step 6: Open the Application in Browser
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

### Official KIET Portals & Credentials

| Role | Email | Password | Access / Capabilities |
|---|---|---|---|
| **Student** | `2628mca0206@kiet.edu` | `Student@123` | Full MCA student dashboard, 14-day streak, heatmap, study plans, capstone project, 21 interactive games, resume |
| **Faculty / Staff** | `staff@kiet.edu` | `Staff@123` *(or `Password@123`)* | Faculty dashboard, MCA 2026-2028 cohort monitoring, at-risk flags, mentorship targets & feedback |
| **Administrator** | `admin@kiet.edu` | `Admin@123` *(or `Password@123`)* | Full administrative control, user provisioning, academic hierarchy, placement drive management |

> 🔑 **Special Platforms Single Sign-On (SSO):**  
> Students can also sign in via **Google Workspace**, **KIET ERP Portal**, **Microsoft 365**, or **GitHub Student Developer** using their official `@kiet.edu` address with 2-Step OTP authentication.

---

### Running the Functional Test Suite

Execute the functional test suite covering authentication, role isolation, skill operations, heatmap calculations, and faculty mentorship:
```powershell
python -m unittest tests/test_functional.py
```

---

### Optional: Local Ollama AI Setup

Student Pulse includes an intelligent, deterministic **Rule-Based Engine** that powers all AI features when offline. To connect local Ollama AI:

1. Download Ollama from [https://ollama.ai](https://ollama.ai)
2. Pull the lightweight coding model in your terminal:
   ```powershell
   ollama run qwen2.5-coder:1.5b
   ```
3. Keep Ollama running on default port `http://localhost:11434`. Student Pulse will automatically detect Ollama and route AI study planning and interview evaluation through the local model.
