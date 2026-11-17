# EduTrack - Contribution & Team Guidelines

Welcome to the **EduTrack** development team! This document outlines our branch strategy, code standards, pull request workflow, and local development setup to ensure smooth and conflict-free collaboration.

---

## 1. Team Roles & Ownership

- **Project Owner:** Manages repositories, reviews Pull Requests, and authorizes merges into the protected `main` branch.
- **Team Members / Collaborators:** Develop assigned features on dedicated feature/bugfix branches and submit Pull Requests.

---

## 2. Branching Strategy

To protect the integrity of the project, **direct pushes to the `main` branch are strictly prohibited**.

### Branch Naming Conventions:
- **Features:** `feature/<feature-name>` (e.g., `feature/attendance-charts`, `feature/student-analytics`)
- **Bug Fixes:** `fix/<bug-description>` (e.g., `fix/login-crash`, `fix/gpa-precision`)
- **Documentation:** `docs/<topic>` (e.g., `docs/api-guide`)
- **Chores / Refactoring:** `chore/<task>` (e.g., `chore/cleanup-assets`)

### Workflow:
1. Ensure your local `main` or `dev` branch is up to date:
   ```bash
   git checkout main
   git pull origin main
   ```
2. Create and switch to a new branch for your task:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make atomic, well-tested changes on your branch.

---

## 3. Commit Message Guidelines

We follow the **Conventional Commits** standard:
- `feat: ...` for a new feature (e.g., `feat: add semester-wise course filter`)
- `fix: ...` for bug fixes (e.g., `fix: correct CGPA calculation rounding`)
- `docs: ...` for documentation changes (e.g., `docs: update setup guide`)
- `refactor: ...` for code changes that neither fix a bug nor add a feature
- `test: ...` for adding or improving tests
- `chore: ...` for build, dependency, or configuration updates

Keep commit messages concise, in imperative mood, and descriptive.

---

## 4. Local Development & Testing

### Environment Setup:
1. Clone the repository and navigate into it:
   ```bash
   git clone https://github.com/shaddhow/EduTrack.git
   cd EduTrack
   ```
2. Create and activate a virtual environment:
   ```bash
   # Windows PowerShell
   py -3.12 -m venv .venv
   .\.venv\Scripts\Activate.ps1

   # Linux / macOS
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy the environment template:
   ```bash
   cp .env.example .env
   ```
   *(Add your `GEMINI_API_KEY` in `.env` if testing the Gemini AI advisor).*

### Running Tests:
Before submitting code, always ensure the test suite passes:
```bash
python run_tests.py
```

### Running the App:
```bash
python main.py
```

### Default Development Login Credentials:
- **Student ID:** `20255103311`
- **Password:** `EduTrack2026!`

---

## 5. Pull Request (PR) Checklist

When your work is ready:
1. Push your branch to GitHub:
   ```bash
   git push -u origin feature/your-feature-name
   ```
2. Open a **Pull Request** against `dev` or `main`.
3. Fill out the PR template completely:
   - What does this PR do?
   - How was it tested?
   - Any screenshots or recordings (for UI changes).
4. Request review from the Project Owner.
5. Address any requested changes promptly.

---

## 6. Code Style & Secrets Protection

- **Never commit secrets:** Never commit API keys, personal credentials, or production databases. Always check `.gitignore`.
- **Modular Design:** Keep UI separate from database logic (`modules/` vs `UI/` / `main.py`).
- **Database Migrations:** If modifying SQLite schemas, update `database/schema.sql` and document the changes in your PR.
