<div align="center">

<img src="./assets/banner.svg" width="100%" alt="EduTrack Banner" />

<br/>

**Next-Generation Desktop Platform for Academic Trajectory Forecasting, CGPA Simulation & Student-Faculty Workspaces**

[![Python Version](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![GUI Framework](https://img.shields.io/badge/GUI-PyWebView%20%7C%20WebView2-0078D4?style=for-the-badge&logo=microsoft-edge&logoColor=white)](https://pywebview.flowrl.com/)
[![Database](https://img.shields.io/badge/Storage-Local%20SQLite3-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org/)
[![Machine Learning](https://img.shields.io/badge/ML-Scikit--Learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-4B5563?style=for-the-badge)](#)

<br/>

[Key Highlights](#-key-features) • [Installation](#-quick-start) • [Architecture](#-architecture) • [Demo Access](#-default-credentials) • [Author](#-author)

</div>

---

## 🌟 Overview

**EduTrack** is an offline-first academic management and trajectory forecasting platform tailored for university students and faculty (optimized according to BUBT CSE grading and credit standards). 

Built on a modern bioluminescent glassmorphic UI via Microsoft Edge WebView2 and PyWebView, EduTrack unifies academic record keeping, dynamic Catmull-Rom trajectory curves, target CGPA forecasting, automated transcript PDF exports, and an offline machine learning advisor into a single responsive desktop client.

---

## ⚡ Key Features

- **💎 Bioluminescent Glassmorphism Interface**
  - Fluid glass cards, subtle neon aura gradients, and full high-DPI scaling (100%–200%).
  - Multi-theme switching with responsive layout adaptation across all monitor resolutions.

- **📈 Academic Trajectory & S-Curve Forecasting**
  - Antialiased velocity modeling curves that map credit completions against semester GPA goals.
  - Interactive target calculator estimating required semester GPAs to graduate with desired honors.

- **🤖 Local AI Academic Advisor & ML Predictor**
  - Built-in machine learning models trained on academic performance indicators.
  - Natural multilingual support (English and Banglish) providing actionable study advice without relying on cloud servers.

- **👨‍🏫 Dual Role Architecture (Student & Faculty)**
  - **Student View:** Real-time course grade audit, attendance tracking, syllabus milestone viewer.
  - **Faculty View:** Interactive section grading roster, distribution analytics, and instant roster search.

- **📄 Official Academic Transcript Generation**
  - Generates verifiable PDF performance summaries and transcripts with clean tabular formatting using ReportLab.

- **🔒 Local Data Sovereignty**
  - Zero required telemetry; all records, student metrics, and course rosters reside in your local encrypted SQLite instance.

---

## 🛠️ Architecture & Tech Stack

| Domain | Technology / Module | Purpose |
| :--- | :--- | :--- |
| **Runtime** | Python 3.12 | Core execution environment & API layer |
| **Desktop Shell** | PyWebView & WebView2 | Native hardware-accelerated presentation shell |
| **Frontend UI** | HTML5 / CSS3 / Vanilla JS / Chart.js | Dynamic trajectory charts & glass UI components |
| **Intelligence** | Scikit-Learn & NumPy | Offline academic outcome prediction & analysis |
| **Storage** | SQLite3 | Relational academic records, schemas & migrations |
| **Reporting** | ReportLab | Automated academic transcript & statement generation |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+ (Python 3.12 recommended)
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/akramulhasanemon/edutrack.git
cd edutrack
```

### 2. Set Up Virtual Environment
```bash
# Windows
python -m venv .venv
.\.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Launch EduTrack
```bash
# Direct run via Python
python main.py

# Alternatively on Windows, double-click:
run_edutrack.bat
```

---

## 🧪 Verification & Tests

To execute the test suite validating GPA algorithms, transcript generation, and ML modules:

```bash
python run_tests.py
```

---

## 🔐 Default Credentials

For local development and testing, pre-configured role presets are available:

| Role | User ID | Password | Access Scope |
| :--- | :--- | :--- | :--- |
| **Student** | `20255103311` | `EduTrack2026!` | Course tracking, CGPA planner, AI advisor |
| **Faculty** | `FAC-2026-CSE` | `EduTrack2026!` | Grade assignment, student section roster |

---

## 📂 Project Organization

```text
edutrack/
├── assets/                  # Icons and visual branding assets
├── data/                    # Academic knowledge base & curriculum reference
├── database/                # SQLite schemas and ML models
├── modules/                 # Academic calculation, AI advisor & PDF engine
├── web_ui/                  # Glassmorphism HTML/CSS/JS interface
├── tests/                   # Automated unit and integration tests
├── desktop_app.py           # Native window manager and IPC bridge
├── main.py                  # Main bootstrap launcher
├── requirements.txt         # Package dependencies
└── run_edutrack.bat         # Windows one-click start script
```

---

## 👤 Author

**Akramul Hasan**
- GitHub: [@akramulhasanemon](https://github.com/akramulhasanemon)
- Repository: [akramulhasanemon/edutrack](https://github.com/akramulhasanemon/edutrack)

---

<div align="center">
Developed with modern Python desktop engineering principles.
</div>
