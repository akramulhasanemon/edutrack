# EduTrack

![Build status](https://img.shields.io/badge/build-not%20configured-lightgrey)
![Python](https://img.shields.io/badge/python-3.12-blue)
![License](https://img.shields.io/badge/license-not%20specified-lightgrey)

**A modern desktop companion for managing student records and making academic progress easier to understand.**

---

## About the Project

EduTrack is a Python desktop application for student data management and academic tracking. Its CustomTkinter interface brings together student and course records, grade and CGPA calculations, academic trajectory tools, advising, analytics, and PDF reporting. Application data is stored locally in SQLite.

The project is designed to make academic information easier to review and act on, while keeping core records on the local machine.

## Key Features Implemented

- **Sign-in and role-aware access:** A local sign-in screen and student/faculty contexts.
- **Modern interface and accent themes:** A dark CustomTkinter interface with selectable color palettes. A light appearance mode is not currently enabled.
- **Student and academic record management:** Create, read, update, and delete student and course records, with enrollment data managed through SQLite.
- **CGPA and grading tools:** Calculate credit-weighted grades and CGPA, and explore the GPA needed to reach an academic target.
- **AI academic advisor:** Get personalized academic guidance using Google Gemini when configured, with local coaching available as a fallback.
- **Academic performance prediction:** Use academic history and trajectory inputs to estimate future performance and required GPA.
- **PDF report generation:** Export an academic trajectory summary with student, course, grade, and CGPA information.
- **Data backup and restore:** Export data to a JSON backup and restore it by merging or replacing imported records.
- **Attendance and schedule data:** Store and review attendance and routine information. Visual progress charts and reminder notifications are planned enhancements.

> [!IMPORTANT]
> The current sign-in flow includes demo access and seeded demo accounts. It is intended for development and evaluation, not as production-grade identity or access control. Change or remove demo credentials and review the authentication design before using real student data.

## Future Roadmap

- Attendance tracking with visual progress charts.
- Routine and class schedule planner with notification reminders.
- Advanced analytics and graphical grade-trend charts using Matplotlib.
- Cloud synchronization, with Firebase or PostgreSQL support.
- Role-based multi-user portals for students and instructors.

## Tech Stack & Libraries

| Technology | Purpose |
| --- | --- |
| Python 3.12 | Application language |
| CustomTkinter | Desktop GUI |
| SQLite | Local data storage |
| ReportLab | PDF report generation |
| `google-genai` | Optional Gemini-powered advising |
| OS environment variables | Pass the selected demo user context from sign-in to the dashboard |

SQLite is included with Python. PDF reports currently use ReportLab; PyPDF2 is not listed as a project dependency. AI advising can use its local fallback when a Gemini API key is not configured.

## Installation & Setup

### Prerequisites

- Python 3.x (Python 3.12 is the project target)
- Git

### 1. Clone the repository

```bash
git clone https://github.com/shaddhow/EduTrack.git
cd EduTrack
```

### 2. Create a virtual environment

**Windows PowerShell**

```powershell
py -3.12 -m venv .venv
```

**macOS / Linux**

```bash
python3.12 -m venv .venv
```

### 3. Activate `.venv`

**Windows PowerShell**

```powershell
.\.venv\Scripts\Activate.ps1
```

**Windows Command Prompt**

```bat
.venv\Scripts\activate.bat
```

**macOS / Linux**

```bash
source .venv/bin/activate
```

### 4. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configure environment variables (Optional)

```bash
cp .env.example .env
```

If you plan to use the Gemini-powered AI Advisor, add your Gemini API key to `.env`. Otherwise, EduTrack uses its local guidance engine.

### 6. Run tests

```bash
python run_tests.py
```

### 7. Run EduTrack

```bash
python main.py
```

#### Demo Development Credentials:
- **Student ID:** `20255103311`
- **Password:** `EduTrack2026!`

---

## Contributing & Team Workflow

Working on EduTrack as a team member? Please read our **[CONTRIBUTING.md](CONTRIBUTING.md)** for:
- Branching conventions (`feature/*`, `fix/*`, etc.)
- Commit message standards (Conventional Commits)
- Pull Request & code review workflow
- Security practices (avoiding committing secrets or local databases)

---

## Project Structure

```text
EduTrack/
├── assets/
├── database/
│   ├── db_config.py
│   └── schema.sql
├── modules/
│   ├── ai_advisor.py
│   ├── app_icon.py
│   ├── crud.py
│   ├── grading.py
│   ├── pdf_generator.py
│   ├── predictor.py
│   └── typography.py
├── UI/
│   ├── main_window.py
│   └── views.py
├── auth_ui.py
├── main.py
├── requirements.txt
└── tests/
```

`main.py` is the application entry point. The sign-in screen is implemented in `auth_ui.py`; database operations, grading, advising, prediction, and PDF generation are organized under `modules/`.

## License & Author

**License:** No license has been specified yet. Add a `LICENSE` file and update this section before redistributing the project.

**Author:** [Developer name]  
**Contact:** [Email address or preferred contact link]

**Credits:** Built with Python, CustomTkinter, SQLite, ReportLab, and the Google Gen AI SDK.
