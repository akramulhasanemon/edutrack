"""Generate a comprehensive, beautifully styled PDF progress report for EduTrack."""

from __future__ import annotations

import os
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and draw total page numbers."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages: int):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#64748b"))

        # Running Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, letter[1] - 36, "EduTrack — Implementation & Progress Status Report")
            self.setStrokeColor(colors.HexColor("#e2e8f0"))
            self.setLineWidth(0.75)
            self.line(54, letter[1] - 42, letter[0] - 54, letter[1] - 42)

        # Running Footer (all pages)
        footer_text = f"Page {self._pageNumber} of {total_pages}"
        self.drawRightString(letter[0] - 54, 34, footer_text)
        self.drawString(54, 34, "Confidential — Generated for EduTrack Development Team")
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.75)
        self.line(54, 46, letter[0] - 54, 46)

        self.restoreState()


def build_pdf_report(output_path: Path):
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    primary_color = colors.HexColor("#0f172a")  # Deep slate
    accent_blue = colors.HexColor("#1d4ed8")    # Blue 700
    subtext_color = colors.HexColor("#475569")  # Slate 600

    title_style = ParagraphStyle(
        "CoverTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=28,
        textColor=primary_color,
        spaceAfter=6,
    )

    subtitle_style = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=12,
        leading=16,
        textColor=accent_blue,
        spaceAfter=15,
    )

    h1_style = ParagraphStyle(
        "SectionH1",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=primary_color,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True,
    )

    h2_style = ParagraphStyle(
        "SectionH2",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=accent_blue,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True,
    )

    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=6,
    )

    bullet_style = ParagraphStyle(
        "BulletDark",
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4,
    )

    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=11,
        textColor=colors.white,
    )

    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#1e293b"),
    )

    table_cell_bold = ParagraphStyle(
        "TableCellBold",
        parent=table_cell_style,
        fontName="Helvetica-Bold",
    )

    badge_style = ParagraphStyle(
        "BadgeText",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#047857"),
    )

    story = []

    # Title Banner
    story.append(Paragraph("EduTrack — Project Progress & Work Status Report", title_style))
    story.append(
        Paragraph(
            "Comprehensive Audit of Implemented Features, Architecture, Modules & Roadmap",
            subtitle_style,
        )
    )
    story.append(HRFlowable(width="100%", thickness=1.5, color=accent_blue, spaceBefore=0, spaceAfter=12))

    # Meta Info Table
    meta_data = [
        [
            Paragraph("<b>Target Platform:</b> Desktop (CustomTkinter)", table_cell_style),
            Paragraph("<b>Language & Runtime:</b> Python 3.12", table_cell_style),
        ],
        [
            Paragraph("<b>Database:</b> SQLite (edutrack.db)", table_cell_style),
            Paragraph("<b>Security:</b> PBKDF2-HMAC-SHA256 Auth", table_cell_style),
        ],
        [
            Paragraph("<b>AI Integration:</b> Google Gemini API + Local Fallback", table_cell_style),
            Paragraph("<b>Overall Completion:</b> ~85% (Core Features Complete)", table_cell_style),
        ],
    ]
    meta_table = Table(meta_data, colWidths=[250, 254])
    meta_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ])
    )
    story.append(meta_table)
    story.append(Spacer(1, 12))

    # 1. Executive Summary
    story.append(Paragraph("1. Executive Summary", h1_style))
    story.append(
        Paragraph(
            "EduTrack is a modern, privacy-focused desktop academic companion built for students and faculty. "
            "It bridges academic record keeping, predictive trajectory planning, BUBT-standard CGPA calculations, "
            "AI-powered mentoring, routine/attendance tracking, and formal transcript export into a cohesive desktop GUI.",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "All core data engines, database models, CRUD services, security logic, and user interface panels are "
            "fully implemented and functional. The application runs locally with zero mandatory cloud dependencies "
            "while maintaining optional Gemini AI connectivity.",
            body_style,
        )
    )

    # 2. Detailed Breakdown of Completed Features
    story.append(Paragraph("2. Detailed Breakdown of Completed Features", h1_style))

    story.append(Paragraph("A. Authentication & Multi-Role Access Control (auth_ui.py)", h2_style))
    story.append(Paragraph("• <b>Dual-Role Architecture:</b> Dedicated views and permission sets for <i>Student</i> and <i>Faculty</i>.", bullet_style))
    story.append(Paragraph("• <b>Cryptographic Security:</b> Passwords hashed using standard PBKDF2-HMAC-SHA256 with 310,000 iterations and unique per-user salts.", bullet_style))
    story.append(Paragraph("• <b>Modern CustomTkinter Sign-in GUI:</b> High-contrast responsive dark theme with instant role selection and error feedback.", bullet_style))
    story.append(Paragraph("• <b>Demo Seeding:</b> Default student (20255103311) and faculty profiles pre-populated for fast onboarding and evaluation.", bullet_style))

    story.append(Paragraph("B. Core Database Engine & Schema (database/db_config.py & schema.sql)", h2_style))
    story.append(Paragraph("• <b>Relational SQLite Architecture:</b> 8 optimized relational tables with cascading foreign keys and indexes.", bullet_style))
    story.append(Paragraph("• <b>Atomic Backup & Restore:</b> Full JSON export and import engine with conflict resolution (Merge or Replace modes).", bullet_style))
    story.append(Paragraph("• <b>Tables Implemented:</b> <code>users</code>, <code>user_settings</code>, <code>students</code>, <code>courses</code>, <code>enrollments</code>, <code>attendance</code>, <code>routines</code>, and <code>faculty_sections</code>.", bullet_style))

    story.append(Paragraph("C. Dashboard & UI Modules (main.py — 3,770+ Lines)", h2_style))
    story.append(Paragraph("• <b>Overview Dashboard:</b> Real-time metric cards showing Cumulative CGPA, Completed Credits, Target CGPA, and Academic Standing.", bullet_style))
    story.append(Paragraph("• <b>Trajectory Planner:</b> Back-calculates required GPA across remaining credit hours to hit graduation milestones; flags impossible targets (>4.00).", bullet_style))
    story.append(Paragraph("• <b>Interactive CGPA Calculator:</b> Dynamic multi-subject credit-weighted GPA calculator with real-time recalculation upon entry.", bullet_style))
    story.append(Paragraph("• <b>AI Academic Advisor:</b> Dual-tier mentoring engine. Connects to Google Gemini API for intelligent advising; falls back to an offline rule-based academic coach analyzing weak courses and low attendance (<75%).", bullet_style))
    story.append(Paragraph("• <b>Attendance & Schedule Manager:</b> Weekly timetable routine viewer with room numbers, days, and course attendance percentage trackers.", bullet_style))
    story.append(Paragraph("• <b>Performance Analytics:</b> Historical semester breakdown and grade point distribution summaries.", bullet_style))
    story.append(Paragraph("• <b>Faculty Control Portal:</b> Section assignment manager, student roster browser, and inline grade update capabilities.", bullet_style))
    story.append(Paragraph("• <b>Settings & Customization:</b> Profile details editor, theme switcher (Dark with multiple accent palettes), and API key management.", bullet_style))

    story.append(Paragraph("D. Business Logic & Helper Modules (modules/)", h2_style))
    story.append(Paragraph("• <b>Academic CRUD (crud.py — 1,130+ lines):</b> Complete transactional API for students, enrollments, attendance, and routines.", bullet_style))
    story.append(Paragraph("• <b>Grading Engine (grading.py):</b> Full BUBT official grading scale (A+, A, A-, B+, B, B-, C+, C, D, F) with precise grade points.", bullet_style))
    story.append(Paragraph("• <b>Trajectory Engine (predictor.py):</b> Math models for academic progress feasibility and GPA requirements.", bullet_style))
    story.append(Paragraph("• <b>PDF Generation (pdf_generator.py):</b> Automated ReportLab generator producing formal academic summary PDFs with student transcript data.", bullet_style))
    story.append(Paragraph("• <b>Typography & Design (typography.py):</b> Consistent font scaling, accent theme definitions, and cross-platform window maximize logic.", bullet_style))

    # Page Break for clean table layouts
    story.append(PageBreak())

    # 3. Codebase Metrics & File Inventory
    story.append(Paragraph("3. Codebase Architecture & File Metrics", h1_style))
    story.append(
        Paragraph(
            "Below is an overview of the key components developed in the codebase, their volume, and operational status:",
            body_style,
        )
    )

    code_metrics = [
        [
            Paragraph("File / Module", table_header_style),
            Paragraph("Lines", table_header_style),
            Paragraph("Primary Role / Implementation", table_header_style),
            Paragraph("Status", table_header_style),
        ],
        [
            Paragraph("<code>main.py</code>", table_cell_bold),
            Paragraph("3,772", table_cell_style),
            Paragraph("Complete CustomTkinter desktop dashboard with 8 view controllers", table_cell_style),
            Paragraph("Complete", badge_style),
        ],
        [
            Paragraph("<code>modules/crud.py</code>", table_cell_bold),
            Paragraph("1,138", table_cell_style),
            Paragraph("Comprehensive database transactions, JSON backup/restore & validation", table_cell_style),
            Paragraph("Complete", badge_style),
        ],
        [
            Paragraph("<code>auth_ui.py</code>", table_cell_bold),
            Paragraph("383", table_cell_style),
            Paragraph("Login window, role switching, authentication event loop & demo launcher", table_cell_style),
            Paragraph("Complete", badge_style),
        ],
        [
            Paragraph("<code>database/db_config.py</code>", table_cell_bold),
            Paragraph("313", table_cell_style),
            Paragraph("SQLite connection pooling, schema initialization, PBKDF2 hashing", table_cell_style),
            Paragraph("Complete", badge_style),
        ],
        [
            Paragraph("<code>modules/ai_advisor.py</code>", table_cell_bold),
            Paragraph("235", table_cell_style),
            Paragraph("Google Gemini API client with smart offline rule-based academic coach", table_cell_style),
            Paragraph("Complete", badge_style),
        ],
        [
            Paragraph("<code>modules/typography.py</code>", table_cell_bold),
            Paragraph("119", table_cell_style),
            Paragraph("Theme color palettes, font scaling, cross-platform display helpers", table_cell_style),
            Paragraph("Complete", badge_style),
        ],
        [
            Paragraph("<code>database/schema.sql</code>", table_cell_bold),
            Paragraph("86", table_cell_style),
            Paragraph("Relational database schema with 8 normalized tables and indexes", table_cell_style),
            Paragraph("Complete", badge_style),
        ],
        [
            Paragraph("<code>modules/grading.py</code>", table_cell_bold),
            Paragraph("78", table_cell_style),
            Paragraph("Official BUBT grade point matrix and credit-weighted CGPA calculator", table_cell_style),
            Paragraph("Complete", badge_style),
        ],
        [
            Paragraph("<code>modules/predictor.py</code>", table_cell_bold),
            Paragraph("52", table_cell_style),
            Paragraph("Academic trajectory and required GPA feasibility math engine", table_cell_style),
            Paragraph("Complete", badge_style),
        ],
        [
            Paragraph("<code>modules/pdf_generator.py</code>", table_cell_bold),
            Paragraph("38", table_cell_style),
            Paragraph("ReportLab transcript canvas generator producing printable summaries", table_cell_style),
            Paragraph("Complete", badge_style),
        ],
    ]

    metrics_table = Table(code_metrics, colWidths=[120, 45, 275, 64])
    metrics_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
            ("ALIGN", (1, 0), (1, -1), "CENTER"),
            ("ALIGN", (3, 0), (3, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ])
    )
    story.append(metrics_table)
    story.append(Spacer(1, 14))

    # 4. Database Schema Overview
    story.append(Paragraph("4. Database Schema Specifications", h1_style))
    db_schema_data = [
        [
            Paragraph("Table Name", table_header_style),
            Paragraph("Key Columns & Relations", table_header_style),
            Paragraph("Functionality in EduTrack", table_header_style),
        ],
        [
            Paragraph("<code>users</code>", table_cell_bold),
            Paragraph("user_id (PK), password_hash, role, display_name", table_cell_style),
            Paragraph("Stores authenticated student and faculty identities.", table_cell_style),
        ],
        [
            Paragraph("<code>user_settings</code>", table_cell_bold),
            Paragraph("user_id (PK), target_cgpa, gemini_api_key, accent_theme", table_cell_style),
            Paragraph("Saves personalized UI theme, target CGPA, and API credentials.", table_cell_style),
        ],
        [
            Paragraph("<code>students</code>", table_cell_bold),
            Paragraph("student_id (PK), name, email, intake, section, target_cgpa", table_cell_style),
            Paragraph("Core demographic and academic standing records.", table_cell_style),
        ],
        [
            Paragraph("<code>courses</code>", table_cell_bold),
            Paragraph("course_code (PK), course_title, credit_hours", table_cell_style),
            Paragraph("Course catalog containing credit weights.", table_cell_style),
        ],
        [
            Paragraph("<code>enrollments</code>", table_cell_bold),
            Paragraph("student_id (FK), course_code (FK), semester_no, grade_point", table_cell_style),
            Paragraph("Completed courses, letter grades, and earned grade points.", table_cell_style),
        ],
        [
            Paragraph("<code>attendance</code>", table_cell_bold),
            Paragraph("student_id (FK), course_code (FK), total_classes, attended_classes", table_cell_style),
            Paragraph("Tracks class presence percentages and flags low attendance.", table_cell_style),
        ],
        [
            Paragraph("<code>routines</code>", table_cell_bold),
            Paragraph("day, time, course_code (FK), room", table_cell_style),
            Paragraph("Weekly schedule timetable and classroom locations.", table_cell_style),
        ],
        [
            Paragraph("<code>faculty_sections</code>", table_cell_bold),
            Paragraph("faculty_user_id (FK), section", table_cell_style),
            Paragraph("Maps faculty members to their assigned student batches.", table_cell_style),
        ],
    ]

    db_table = Table(db_schema_data, colWidths=[110, 194, 200])
    db_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ])
    )
    story.append(db_table)

    # 5. Roadmap & Remaining Tasks
    story.append(Paragraph("5. Future Enhancements & Pending Roadmap", h1_style))
    story.append(
        Paragraph("1. <b>Visual Charts (Matplotlib integration):</b> Rendering animated semester GPA trend curves and grade distribution histograms directly inside the Analytics tab.", bullet_style)
    )
    story.append(
        Paragraph("2. <b>Class Routine Desktop Notifications:</b> Timed desktop reminders 15 minutes prior to scheduled classes.", bullet_style)
    )
    story.append(
        Paragraph("3. <b>Cloud Database Synchronization:</b> Optional sync adapter for Firebase Firestore or PostgreSQL remote storage.", bullet_style)
    )
    story.append(
        Paragraph("4. <b>Unit Testing Expansion:</b> Completing test suites in <code>tests/test_predictor.py</code> and adding automated CI workflows.", bullet_style)
    )

    # 6. Conclusion
    story.append(Spacer(1, 8))
    story.append(Paragraph("6. Project Readiness Assessment", h1_style))
    story.append(
        Paragraph(
            "<b>Status: Production-Ready Local Deployment.</b> The application is fully equipped for daily student and "
            "faculty tracking. All essential calculations, database operations, UI flows, and PDF reports operate smoothly "
            "without external server dependencies.",
            body_style,
        )
    )

    doc.build(story, canvasmaker=NumberedCanvas)
    return output_path


if __name__ == "__main__":
    report_file = Path(r"d:\EduTrack\EduTrack_Work_Progress_Report.pdf")
    build_pdf_report(report_file)
    print(f"Report generated successfully at: {report_file}")

