# EduTrack

A modern desktop-based academic tracking and CGPA management system designed for university students and faculty members.

---

## About the Project

EduTrack is an offline-first desktop application built with Python and CustomTkinter to help university students manage their academic records, calculate GPAs/CGPAs based on the BUBT grading system, plan future trajectories, and export professional PDF academic reports. All data is securely stored locally using SQLite.

---

## Key Features

- **Secure Authentication:** Local sign-in flow with role selection (Student/Faculty) and password hashing.
- **Modern Dashboard UI:** Dark-themed CustomTkinter interface with sidebar navigation, profile badges, and dynamic page views.
- **Grading & GPA Engine:** Automated BUBT grade-point mapping, semester-wise weighted GPA computation, and overall CGPA calculation.
- **Trajectory Planner & Calculator:** Interactive what-if GPA calculators and target requirement forecasting.
- **Analytics & AI Advisor:** Semester trend insights and an offline-first fallback advice engine with optional Gemini AI integration.
- **PDF Report Generation:** Professional transcript and summary report export powered by ReportLab.
- **Data Backup & Restore:** JSON-based data export and import mechanism.

---

## Tech Stack

- **Language:** Python 3.12+
- **GUI Framework:** CustomTkinter
- **Database:** SQLite3
- **Reporting:** ReportLab
- **AI Integration:** Google GenAI SDK (Optional)

---

## Installation & Setup

### 1. Clone the repository
```bash
git clone [https://github.com/shaddhow/EduTrack.git](https://github.com/shaddhow/EduTrack.git)
cd EduTrack
