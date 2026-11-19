"""Generate a comprehensive, professional academic Project Progress Report in PDF for EduTrack.

Targeted for university project evaluation, faculty progress presentation, and portfolio documentation.
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
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


class ProgressReportNumberedCanvas(canvas.Canvas):
    """Two-pass canvas for professional university project progress reports."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._saved_page_states: list[dict[str, Any]] = []

    def showPage(self) -> None:
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self) -> None:
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages: int) -> None:
        self.saveState()
        self.setFont("Helvetica", 8.5)
        self.setFillColor(colors.HexColor("#64748b"))

        page_w, page_h = letter

        # Running header on pages > 1
        if self._pageNumber > 1:
            self.drawString(50, page_h - 32, "EduTrack — Academic Intelligence & Trajectory Planner")
            self.drawRightString(page_w - 50, page_h - 32, "Technical Progress Report")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.75)
            self.line(50, page_h - 38, page_w - 50, page_h - 38)

        # Running footer on every page
        footer_text = f"Page {self._pageNumber} of {total_pages}"
        self.drawRightString(page_w - 50, 30, footer_text)
        self.drawString(
            50,
            30,
            "BUBT Department of CSE • Project Progress Evaluation Milestone • Confidential"
        )
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.75)
        self.line(50, 42, page_w - 50, 42)

        self.restoreState()


def build_progress_report(output_path: str = "EduTrack_Progress_Report.pdf") -> str:
    """Build the multi-page academic project progress report."""
    target_file = Path(output_path).resolve()
    target_file.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(target_file),
        pagesize=letter,
        leftMargin=50,
        rightMargin=50,
        topMargin=50,
        bottomMargin=54,
    )

    printable_w = letter[0] - 100  # 512 points

    base_styles = getSampleStyleSheet()

    # Custom typography styles
    c_primary = colors.HexColor("#0f172a")    # Deep slate
    c_navy = colors.HexColor("#1e293b")       # Dark blue slate
    c_accent = colors.HexColor("#0284c7")     # Sky cyan/blue
    c_muted = colors.HexColor("#475569")      # Muted body text
    c_light = colors.HexColor("#f8fafc")      # Soft background

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=base_styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=19,
        leading=23,
        textColor=colors.HexColor("#0f172a"),
        alignment=0,
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=base_styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=c_accent,
    )
    meta_style = ParagraphStyle(
        "ReportMeta",
        parent=base_styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=c_muted,
    )
    h2_style = ParagraphStyle(
        "ReportH2",
        parent=base_styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12.5,
        leading=16,
        textColor=c_navy,
        spaceBefore=14,
        spaceAfter=6,
    )
    h3_style = ParagraphStyle(
        "ReportH3",
        parent=base_styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#0369a1"),
        spaceBefore=8,
        spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "ReportBody",
        parent=base_styles["BodyText"],
        fontName="Helvetica",
        fontSize=8.8,
        leading=13.2,
        textColor=c_muted,
    )
    bold_body_style = ParagraphStyle(
        "ReportBoldBody",
        parent=body_style,
        fontName="Helvetica-Bold",
        textColor=c_navy,
    )
    card_title_style = ParagraphStyle(
        "CardTitle",
        parent=base_styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#64748b"),
        alignment=1,
    )
    card_val_style = ParagraphStyle(
        "CardVal",
        parent=base_styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=c_navy,
        alignment=1,
    )
    table_hdr_style = ParagraphStyle(
        "TableHdr",
        parent=base_styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
    )
    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=base_styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=c_navy,
    )
    badge_done_style = ParagraphStyle(
        "BadgeDone",
        parent=base_styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=9,
        textColor=colors.HexColor("#065f46"),
        alignment=1,
    )

    story: list[Any] = []

    # =========================================================================
    # HEADER BANNER & PROJECT METADATA
    # =========================================================================
    header_table_data = [
        [
            Paragraph("<b>BANGLADESH UNIVERSITY OF BUSINESS AND TECHNOLOGY (BUBT)</b><br/>Department of Computer Science and Engineering (CSE)", subtitle_style),
            Paragraph(f"<b>Date:</b> {datetime.now().strftime('%B %d, %Y')}<br/><b>Milestone:</b> Sprint 1–3 Complete", meta_style),
        ]
    ]
    t_hdr = Table(header_table_data, colWidths=[printable_w * 0.68, printable_w * 0.32])
    t_hdr.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(t_hdr)
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_accent, spaceBefore=2, spaceAfter=10))

    story.append(Paragraph("EduTrack: Academic Intelligence & Trajectory Planner", title_style))
    story.append(Spacer(1, 3))
    story.append(Paragraph(
        "<b>Comprehensive Project Milestone & Technical Progress Report</b> • Desktop Decision Support System",
        subtitle_style
    ))
    story.append(Spacer(1, 10))

    # Project metadata grid
    meta_box_data = [
        [
            Paragraph("<b>Candidate:</b> Mahabub Shaddhow (ID: 20255103311)", body_style),
            Paragraph("<b>Degree:</b> B.Sc. in Computer Science & Engineering", body_style),
        ],
        [
            Paragraph("<b>Project Scope:</b> Intelligent Academic Desktop Architecture", body_style),
            Paragraph("<b>Current Status:</b> Production-Ready Local Milestone & Standalone .EXE", body_style),
        ]
    ]
    t_meta = Table(meta_box_data, colWidths=[printable_w * 0.52, printable_w * 0.48])
    t_meta.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
        ("PADDING", (0, 0), (-1, -1), 7),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 12))

    # =========================================================================
    # EXECUTIVE KPI / METRIC CARDS
    # =========================================================================
    card_data = [
        [
            Paragraph("CORE SPRINT", card_title_style),
            Paragraph("AUTOMATED TESTS", card_title_style),
            Paragraph("OFFLINE CAPABILITY", card_title_style),
            Paragraph("EXE PACKAGING", card_title_style),
        ],
        [
            Paragraph("100% Verified", card_val_style),
            Paragraph("11 / 11 Passed", card_val_style),
            Paragraph("Full Offline", card_val_style),
            Paragraph("37.5 MB Ready", card_val_style),
        ],
        [
            Paragraph("Sprint 1–3 Complete", card_title_style),
            Paragraph("Zero Regression", card_title_style),
            Paragraph("Local SQLite & AI", card_title_style),
            Paragraph("One-Click Launch", card_title_style),
        ]
    ]
    t_cards = Table(card_data, colWidths=[printable_w / 4] * 4)
    t_cards.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("BOX", (0, 0), (0, -1), 1, colors.HexColor("#cbd5e1")),
        ("BOX", (1, 0), (1, -1), 1, colors.HexColor("#cbd5e1")),
        ("BOX", (2, 0), (2, -1), 1, colors.HexColor("#cbd5e1")),
        ("BOX", (3, 0), (3, -1), 1, colors.HexColor("#cbd5e1")),
        ("TOPPADDING", (0, 0), (-1, 0), 6),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(t_cards)
    story.append(Spacer(1, 14))

    # =========================================================================
    # SECTION 1: EXECUTIVE SUMMARY
    # =========================================================================
    story.append(Paragraph("1. Executive Summary & Problem Formulation", h2_style))
    story.append(Paragraph(
        "Undergraduate university students in Computer Science & Engineering face severe informational asymmetry "
        "regarding degree trajectory management. Traditional university web portals function merely as static record repositories, "
        "offering zero predictive analytics, no course retake impact simulations, and no proactive scheduling or automated academic advising. "
        "Consequently, students frequently realize credit shortfalls or GPA bottlenecks too late in their degree progression.",
        body_style
    ))
    story.append(Spacer(1, 5))
    story.append(Paragraph(
        "<b>EduTrack</b> was engineered as an offline-first, cosmic glassmorphic academic intelligence system designed specifically to bridge this gap. "
        "It integrates real-time trajectory mathematical modeling, automated degree progress tracking, a dynamic course retake boost simulator, "
        "official PDF transcript generation compliant with university standards, and <b>EduTrack AI</b> — a multilingual intelligent advisory assistant "
        "proficient in English, Banglish, and Bengali.",
        body_style
    ))
    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 2: SYSTEM ARCHITECTURE & TECHNOLOGY STACK
    # =========================================================================
    story.append(Paragraph("2. Technical Architecture & Technology Stack", h2_style))
    story.append(Paragraph(
        "EduTrack utilizes a decoupled, high-performance desktop architecture engineered in Python 3.12, prioritizing zero external database latency, "
        "cryptographic security, and full offline resilience:",
        body_style
    ))
    story.append(Spacer(1, 6))

    tech_table_data = [
        [
            Paragraph("<b>Layer / Subsystem</b>", table_hdr_style),
            Paragraph("<b>Core Technology</b>", table_hdr_style),
            Paragraph("<b>Architecture & Implementation Details</b>", table_hdr_style),
        ],
        [
            Paragraph("<b>Presentation & UI</b>", table_cell_style),
            Paragraph("CustomTkinter & PIL", table_cell_style),
            Paragraph("Cosmic dark glassmorphism theme (#050A13, #070E1B, #0C1729, #38BDF8), smooth scroll canvas, responsive dual-workspace shell.", table_cell_style),
        ],
        [
            Paragraph("<b>Authentication & RBAC</b>", table_cell_style),
            Paragraph("PBKDF2-HMAC-SHA256", table_cell_style),
            Paragraph("310,000 salt iterations, constant-time compare, strict Student vs Faculty workspace role-based authorization.", table_cell_style),
        ],
        [
            Paragraph("<b>Database & Storage</b>", table_cell_style),
            Paragraph("SQLite 3 & Atomic Engine", table_cell_style),
            Paragraph("ACID compliance, auto-provisioning schema, atomic temporary file replacement for zero-corruption backups.", table_cell_style),
        ],
        [
            Paragraph("<b>Trajectory & Simulator</b>", table_cell_style),
            Paragraph("Deterministic Math Engine", table_cell_style),
            Paragraph("Exact algebraic remaining GPA calculations, C/D replacement delta formulas, degree completion pacing algorithms.", table_cell_style),
        ],
        [
            Paragraph("<b>Document Generation</b>", table_cell_style),
            Paragraph("ReportLab Platypus 5.0", table_cell_style),
            Paragraph("Two-pass NumberedCanvas, official BUBT layout, dynamic academic badges, course transcript tables.", table_cell_style),
        ],
        [
            Paragraph("<b>EduTrack AI Assistant</b>", table_cell_style),
            Paragraph("Hybrid Multilingual Engine", table_cell_style),
            Paragraph("Rule-based inference for full offline resilience, native Banglish/Bengali NLP classifier, optional Gemini/Ollama LLM hook.", table_cell_style),
        ],
        [
            Paragraph("<b>Packaging & Release</b>", table_cell_style),
            Paragraph("PyInstaller 6.x", table_cell_style),
            Paragraph("Single-binary standalone executable (.exe) with embedded DLLs, schemas, icon assets, and auto-detecting working directory.", table_cell_style),
        ],
    ]
    t_tech = Table(tech_table_data, colWidths=[printable_w * 0.23, printable_w * 0.22, printable_w * 0.55])
    t_tech.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), c_navy),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t_tech)
    story.append(Spacer(1, 14))

    # =========================================================================
    # SECTION 3: KEY DELIVERED CAPABILITIES
    # =========================================================================
    story.append(Paragraph("3. Detailed Module Implementations & Delivered Features", h2_style))

    story.append(Paragraph("3.1 Interactive Student Dashboard & Academic Profile", h3_style))
    story.append(Paragraph(
        "• <b>Avatar Initials Badge & Dynamic Standing:</b> Dynamically renders student initial badges and computes formal academic standing "
        "(Dean's Honor Roll for CGPA ≥ 3.75, High Distinction for ≥ 3.50, Good Standing for ≥ 3.00).<br/>"
        "• <b>Degree Credit Progress Bar:</b> Visual progression metric tracking completed credits against total 142.0 degree requirements.<br/>"
        "• <b>Live Class Schedule Hub:</b> Automatically queries and organizes daily academic routine records into a time-sorted schedule card.",
        body_style
    ))
    story.append(Spacer(1, 4))

    story.append(Paragraph("3.2 Trajectory Planner & Course Retake Simulator", h3_style))
    story.append(Paragraph(
        "• <b>Forward-Looking Mathematical Predictor:</b> Evaluates the exact average GPA required across remaining credits: "
        "<i>Req_GPA = [(Target × Total_Credits) - (Current_CGPA × Graded_Credits)] / Remaining_Credits</i>.<br/>"
        "• <b>Course Retake & Grade Improvement Simulator:</b> Allows students to select previously completed courses with lower grade bands (C/D) "
        "and simulate replacing them with target grades (A/A+). Unlike naive calculators, EduTrack models true grade replacement without penalizing "
        "the student with redundant credit hours.",
        body_style
    ))
    story.append(Spacer(1, 4))

    story.append(Paragraph("3.3 EduTrack AI — Multilingual & Offline Academic Intelligence", h3_style))
    story.append(Paragraph(
        "• <b>Floating Capsule & Pop-up Drawer:</b> An always-accessible interactive floating action button (FAB) with a 385×510px glassmorphic drawer, "
        "featuring page-aware contextual monitoring (tracking active screen and goal) and one-touch Quick Prompt chips.<br/>"
        "• <b>Multilingual & Banglish NLP Classifier:</b> Fully trained to understand natural student language in English, phonetic Banglish "
        "(e.g., <i>'kemon acho'</i>, <i>'porar routine dao'</i>, <i>'cgpa barabo kivabe'</i>, <i>'retake strategy ki'</i>, <i>'fail korbo mone hoy'</i>), "
        "and Bengali script.<br/>"
        "• <b>Instant Enter-to-Send Workflow:</b> Optimized messaging pipeline where pressing <b>Enter</b> immediately transmits questions, with "
        "<b>Shift+Enter</b> reserved for newlines.",
        body_style
    ))
    story.append(Spacer(1, 4))

    story.append(Paragraph("3.4 ReportLab Official PDF Transcript Generator", h3_style))
    story.append(Paragraph(
        "• <b>Platypus-Powered Multi-Page Engine:</b> Generates certified academic transcripts matching official university layouts, including "
        "numbered canvas headers, verification serials, signature execution blocks, and academic standing classification.<br/>"
        "• <b>Direct 1-Click Export:</b> Integrated directly into the Student Dashboard for rapid document production.",
        body_style
    ))
    story.append(Spacer(1, 4))

    story.append(Paragraph("3.5 Distribution & Standalone Executable Packaging", h3_style))
    story.append(Paragraph(
        "• <b>Zero-Dependency Deployment:</b> Bundled via PyInstaller into a standalone <b>EduTrack.exe</b> (~37.5 MB), containing all GUI themes, "
        "ReportLab typography fonts, database schemas, and application icon assets.<br/>"
        "• <b>Automated One-Click Build Script:</b> Includes <b>build_exe.bat</b> in the project root for instantaneous rebuilds across any workstation.",
        body_style
    ))
    story.append(Spacer(1, 14))

    # =========================================================================
    # SECTION 4: SPRINT DELIVERABLES & MILESTONE MATRIX
    # =========================================================================
    story.append(KeepTogether([
        Paragraph("4. Milestone Deliverables & Implementation Status Matrix", h2_style),
        Paragraph(
            "Summary of planned project objectives vs verified implementation status for the current milestone:",
            body_style
        ),
        Spacer(1, 6),
    ]))

    matrix_data = [
        [
            Paragraph("<b>Deliverable / Feature</b>", table_hdr_style),
            Paragraph("<b>Target Module</b>", table_hdr_style),
            Paragraph("<b>Implementation Status</b>", table_hdr_style),
            Paragraph("<b>Engineering Impact</b>", table_hdr_style),
        ],
        [
            Paragraph("Dark Cosmic Glass UI", table_cell_style),
            Paragraph("main.py, auth_ui.py", table_cell_style),
            Paragraph("<b>COMPLETED</b>", badge_done_style),
            Paragraph("Unified modern aesthetic matching university design standards.", table_cell_style),
        ],
        [
            Paragraph("Course Retake Simulator", table_cell_style),
            Paragraph("main.py, grading.py", table_cell_style),
            Paragraph("<b>COMPLETED</b>", badge_done_style),
            Paragraph("Instant calculation of CGPA boost via grade replacement.", table_cell_style),
        ],
        [
            Paragraph("Official PDF Transcript", table_cell_style),
            Paragraph("modules/pdf_generator.py", table_cell_style),
            Paragraph("<b>COMPLETED</b>", badge_done_style),
            Paragraph("Vector-grade printable academic records with Dean's badges.", table_cell_style),
        ],
        [
            Paragraph("Dynamic Floating AI Capsule", table_cell_style),
            Paragraph("main.py (FAB + Drawer)", table_cell_style),
            Paragraph("<b>COMPLETED</b>", badge_done_style),
            Paragraph("Cross-page contextual guidance available from any screen.", table_cell_style),
        ],
        [
            Paragraph("Multilingual & Banglish AI", table_cell_style),
            Paragraph("modules/ai_advisor.py", table_cell_style),
            Paragraph("<b>COMPLETED</b>", badge_done_style),
            Paragraph("100% offline advisory supporting English, Banglish, and Bangla.", table_cell_style),
        ],
        [
            Paragraph("Enter-to-Send Messaging", table_cell_style),
            Paragraph("main.py (Chat Bindings)", table_cell_style),
            Paragraph("<b>COMPLETED</b>", badge_done_style),
            Paragraph("Frictionless conversational interaction across all chat views.", table_cell_style),
        ],
        [
            Paragraph("Daily Routine Schedule Hub", table_cell_style),
            Paragraph("main.py, crud.py", table_cell_style),
            Paragraph("<b>COMPLETED</b>", badge_done_style),
            Paragraph("Automated routine parsing and real-time class schedule cards.", table_cell_style),
        ],
        [
            Paragraph("Standalone Win64 Executable", table_cell_style),
            Paragraph("EduTrack.exe, build_exe.bat", table_cell_style),
            Paragraph("<b>COMPLETED</b>", badge_done_style),
            Paragraph("Portable distribution without requiring Python environment.", table_cell_style),
        ],
    ]
    t_matrix = Table(matrix_data, colWidths=[printable_w * 0.28, printable_w * 0.22, printable_w * 0.18, printable_w * 0.32])
    t_matrix.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), c_navy),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("PADDING", (0, 0), (-1, -1), 4.5),
        ("ALIGN", (2, 1), (2, -1), "CENTER"),
    ]))
    story.append(t_matrix)
    story.append(Spacer(1, 14))

    # =========================================================================
    # SECTION 5: QUALITY ASSURANCE & TEST VERIFICATION
    # =========================================================================
    story.append(KeepTogether([
        Paragraph("5. Quality Assurance & Automated Test Results", h2_style),
        Paragraph(
            "EduTrack maintains a zero-dependency automated test harness (<b>run_tests.py</b>) executed continuously to prevent regression. "
            "All 11 automated test suites passed successfully with zero failures:",
            body_style
        ),
        Spacer(1, 6),
    ]))

    test_data = [
        [
            Paragraph("<b>Test Case Name</b>", table_hdr_style),
            Paragraph("<b>Target Functional Unit</b>", table_hdr_style),
            Paragraph("<b>Status</b>", table_hdr_style),
            Paragraph("<b>Validation Criteria</b>", table_hdr_style),
        ],
        [
            Paragraph("Predictor - Basic calculation", table_cell_style),
            Paragraph("Trajectory Engine", table_cell_style),
            Paragraph("<b>PASSED</b>", badge_done_style),
            Paragraph("Validates required GPA formula across active course records.", table_cell_style),
        ],
        [
            Paragraph("Predictor - Zero remaining credits", table_cell_style),
            Paragraph("Trajectory Engine", table_cell_style),
            Paragraph("<b>PASSED</b>", badge_done_style),
            Paragraph("Handles degree completion boundary without division by zero.", table_cell_style),
        ],
        [
            Paragraph("Predictor - Target exceeds max", table_cell_style),
            Paragraph("Trajectory Engine", table_cell_style),
            Paragraph("<b>PASSED</b>", badge_done_style),
            Paragraph("Flags impossible targets exceeding mathematical 4.00 ceiling.", table_cell_style),
        ],
        [
            Paragraph("Predictor - Already on track", table_cell_style),
            Paragraph("Trajectory Engine", table_cell_style),
            Paragraph("<b>PASSED</b>", badge_done_style),
            Paragraph("Verifies status when current CGPA already satisfies target.", table_cell_style),
        ],
        [
            Paragraph("Predictor - Feasible target", table_cell_style),
            Paragraph("Trajectory Engine", table_cell_style),
            Paragraph("<b>PASSED</b>", badge_done_style),
            Paragraph("Validates achievable GPA targets under normal pacing.", table_cell_style),
        ],
        [
            Paragraph("AI Advisor - Local advice fallback", table_cell_style),
            Paragraph("Offline Inference Engine", table_cell_style),
            Paragraph("<b>PASSED</b>", badge_done_style),
            Paragraph("Ensures full offline operation using local course & attendance.", table_cell_style),
        ],
        [
            Paragraph("AI Advisor - Prompt formatting", table_cell_style),
            Paragraph("Prompt Builder", table_cell_style),
            Paragraph("<b>PASSED</b>", badge_done_style),
            Paragraph("Verifies schema for external LLM API fallback providers.", table_cell_style),
        ],
        [
            Paragraph("AI Advisor - Banglish & Multilingual", table_cell_style),
            Paragraph("Intent Classifier", table_cell_style),
            Paragraph("<b>PASSED</b>", badge_done_style),
            Paragraph("Validates Banglish greetings, retake, routine, and motivation prompts.", table_cell_style),
        ],
        [
            Paragraph("Academic PDF - Standing classification", table_cell_style),
            Paragraph("ReportLab Generator", table_cell_style),
            Paragraph("<b>PASSED</b>", badge_done_style),
            Paragraph("Tests Dean's Honor Roll, Distinction, and Satisfactory thresholds.", table_cell_style),
        ],
        [
            Paragraph("Academic PDF - Transcript generation", table_cell_style),
            Paragraph("ReportLab Generator", table_cell_style),
            Paragraph("<b>PASSED</b>", badge_done_style),
            Paragraph("Verifies valid multi-page binary PDF stream output.", table_cell_style),
        ],
        [
            Paragraph("Simulator - Retake boost formula", table_cell_style),
            Paragraph("Simulation Engine", table_cell_style),
            Paragraph("<b>PASSED</b>", badge_done_style),
            Paragraph("Validates exact delta calculations during grade point replacement.", table_cell_style),
        ],
    ]
    t_test = Table(test_data, colWidths=[printable_w * 0.32, printable_w * 0.22, printable_w * 0.16, printable_w * 0.30])
    t_test.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), c_navy),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("PADDING", (0, 0), (-1, -1), 4),
        ("ALIGN", (2, 1), (2, -1), "CENTER"),
    ]))
    story.append(t_test)
    story.append(Spacer(1, 14))

    # =========================================================================
    # SECTION 6: ROADMAP & FUTURE WORK
    # =========================================================================
    story.append(KeepTogether([
        Paragraph("6. Project Roadmap & Upcoming Phase 2 Objectives", h2_style),
        Paragraph(
            "Building upon the completed and verified Sprint 1–3 foundation, the following phase will introduce:",
            body_style
        ),
        Spacer(1, 4),
        Paragraph(
            "• <b>Faculty Portal Expansion:</b> Direct bulk routine CSV/Excel import tools and student risk-flagging dashboards.<br/>"
            "• <b>Encrypted Cloud Synchronization:</b> Optional end-to-end encrypted backup sync across multiple student devices.<br/>"
            "• <b>Curriculum Prerequisite Graph Visualization:</b> Interactive tree mapping course prerequisites and elective dependencies.<br/>"
            "• <b>Push Notification Alarms:</b> System-tray notifications alerting students 30 minutes prior to scheduled lecture sessions.",
            body_style
        ),
        Spacer(1, 16),
    ]))

    # =========================================================================
    # SECTION 7: FORMAL ACADEMIC SIGN-OFF
    # =========================================================================
    sign_box_data = [
        [
            Paragraph("<b>Report Prepared By:</b><br/><br/><br/>___________________________________<br/><b>Mahabub Shaddhow</b><br/>Candidate (ID: 20255103311)<br/>Department of CSE, BUBT", body_style),
            Paragraph("<b>Supervised & Reviewed By:</b><br/><br/><br/>___________________________________<br/><b>Faculty Project Supervisor</b><br/>Department of CSE<br/>BUBT", body_style),
            Paragraph("<b>Departmental Approval:</b><br/><br/><br/>___________________________________<br/><b>Head of Department / Coordinator</b><br/>Department of CSE<br/>BUBT", body_style),
        ]
    ]
    t_sign = Table(sign_box_data, colWidths=[printable_w / 3] * 3)
    t_sign.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
    ]))

    story.append(KeepTogether([
        Paragraph("7. Academic Milestone Evaluation & Formal Sign-Off", h2_style),
        Spacer(1, 6),
        t_sign,
    ]))

    # Build the document
    doc.build(story, canvasmaker=ProgressReportNumberedCanvas)
    return str(target_file)


if __name__ == "__main__":
    out = build_progress_report("EduTrack_Progress_Report.pdf")
    print(f"Generated Progress Report PDF: {out}")
