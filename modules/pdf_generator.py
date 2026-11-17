"""Official academic transcript and trajectory report PDF generator for EduTrack.

Built with ReportLab Platypus for pixel-perfect, multi-page university transcripts.
"""

from __future__ import annotations

import math
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
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to compute and render total page count and page decorations."""

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
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#64748b"))

        # Running header for pages > 1
        if self._pageNumber > 1:
            self.drawString(54, letter[1] - 36, "EduTrack — Official Academic Transcript")
            self.setStrokeColor(colors.HexColor("#e2e8f0"))
            self.setLineWidth(0.75)
            self.line(54, letter[1] - 42, letter[0] - 54, letter[1] - 42)

        # Running footer on every page
        footer_text = f"Page {self._pageNumber} of {total_pages}"
        self.drawRightString(letter[0] - 54, 34, footer_text)
        self.drawString(54, 34, "EduTrack Academic Intelligence — Certified Academic Record")
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.75)
        self.line(54, 46, letter[0] - 54, 46)

        self.restoreState()


class AcademicPDFReport:
    """Generate high-quality, professional university academic transcripts."""

    @staticmethod
    def get_academic_standing(cgpa: float | None) -> tuple[str, str]:
        """Return academic standing label and accent hex color."""
        if cgpa is None:
            return "New Intake / No Graded Records", "#64748b"
        if cgpa >= 3.75:
            return "Dean's Honor Roll", "#059669"
        if cgpa >= 3.50:
            return "High Distinction", "#2563eb"
        if cgpa >= 3.00:
            return "Good Standing", "#0284c7"
        if cgpa >= 2.50:
            return "Satisfactory Pace", "#d97706"
        return "Academic Monitoring", "#dc2626"

    @classmethod
    def generate_transcript_pdf(
        cls,
        filename: str | Path,
        student_info: dict[str, Any],
        enrollments: list[dict[str, Any]],
        current_cgpa: float | None = None,
        completed_credits: float | None = None,
        program_credits: float = 142.0,
    ) -> str:
        """Create a polished multi-page PDF transcript report."""
        output_path = Path(filename).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)

        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            leftMargin=54,
            rightMargin=54,
            topMargin=54,
            bottomMargin=54,
        )

        styles = getSampleStyleSheet()

        # Custom Palette
        c_primary = colors.HexColor("#0f172a")     # Deep Slate
        c_secondary = colors.HexColor("#1e3a8a")   # Academic Navy
        c_accent = colors.HexColor("#2563eb")      # Blue Accent
        c_muted = colors.HexColor("#64748b")       # Muted Slate
        c_border = colors.HexColor("#cbd5e1")      # Slate 300
        c_table_hdr = colors.HexColor("#1e293b")   # Slate 800

        # Styles
        style_title = ParagraphStyle(
            "DocTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=20,
            textColor=c_secondary,
            alignment=1,  # Center
            spaceAfter=3,
        )
        style_dept = ParagraphStyle(
            "DeptTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=c_primary,
            alignment=1,
            spaceAfter=2,
        )
        style_subtitle = ParagraphStyle(
            "DocSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=c_muted,
            alignment=1,
            spaceAfter=14,
        )
        style_meta_label = ParagraphStyle(
            "MetaLabel",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=12,
            textColor=c_muted,
        )
        style_meta_val = ParagraphStyle(
            "MetaVal",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=13,
            textColor=c_primary,
        )
        style_table_hdr = ParagraphStyle(
            "TblHeader",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=11,
            textColor=colors.white,
            alignment=0,
        )
        style_table_cell = ParagraphStyle(
            "TblCell",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=11,
            textColor=c_primary,
        )
        style_table_cell_center = ParagraphStyle(
            "TblCellCenter",
            parent=style_table_cell,
            alignment=1,
        )
        style_table_cell_bold = ParagraphStyle(
            "TblCellBold",
            parent=style_table_cell,
            fontName="Helvetica-Bold",
            alignment=1,
        )

        elements: list[Any] = []

        # --- UNIVERSITY HEADER ---
        elements.append(Paragraph("BANGLADESH UNIVERSITY OF BUSINESS AND TECHNOLOGY (BUBT)", style_title))
        elements.append(Paragraph("Department of Computer Science & Engineering", style_dept))
        elements.append(Paragraph("EduTrack Smart Academic Trajectory & Official Performance Record", style_subtitle))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=c_accent, spaceBefore=0, spaceAfter=14))

        # --- STUDENT METADATA & ACADEMIC STANDING CARDS ---
        sid = str(student_info.get("student_id") or "N/A")
        sname = str(student_info.get("name") or "CSE Student")
        sem = str(student_info.get("semester") or student_info.get("current_semester") or "Current Term")
        standing_label, standing_color = cls.get_academic_standing(current_cgpa)

        # Calculate totals if not passed
        total_credits = 0.0
        total_gp = 0.0
        for r in enrollments:
            try:
                cr = float(r.get("credit_hours", 0))
                gp = r.get("grade_point")
                if cr > 0 and gp is not None and math.isfinite(float(gp)):
                    total_credits += cr
                    total_gp += cr * float(gp)
            except (ValueError, TypeError):
                continue

        actual_cgpa = (total_gp / total_credits) if total_credits > 0 else current_cgpa
        comp_credits = completed_credits if completed_credits is not None else total_credits
        cgpa_str = f"{actual_cgpa:.2f}" if actual_cgpa is not None else "N/A"
        date_str = datetime.now().strftime("%d %B, %Y")

        meta_data = [
            [
                Paragraph("STUDENT ID", style_meta_label),
                Paragraph(sid, style_meta_val),
                Paragraph("CUMULATIVE GPA", style_meta_label),
                Paragraph(f"<b>{cgpa_str}</b> / 4.00", style_meta_val),
            ],
            [
                Paragraph("STUDENT NAME", style_meta_label),
                Paragraph(sname, style_meta_val),
                Paragraph("COMPLETED CREDITS", style_meta_label),
                Paragraph(f"{comp_credits:g} of {program_credits:g} Cr.", style_meta_val),
            ],
            [
                Paragraph("SEMESTER / SESSION", style_meta_label),
                Paragraph(sem, style_meta_val),
                Paragraph("ACADEMIC STANDING", style_meta_label),
                Paragraph(f"<b>{standing_label}</b>", ParagraphStyle("Standing", parent=style_meta_val, textColor=colors.HexColor(standing_color))),
            ],
            [
                Paragraph("DATE GENERATED", style_meta_label),
                Paragraph(date_str, style_meta_val),
                Paragraph("DEGREE PROGRAM", style_meta_label),
                Paragraph("B.Sc. in CSE (142 Credits)", style_meta_val),
            ],
        ]

        meta_table = Table(meta_data, colWidths=[110, 160, 115, 119])
        meta_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                ("BOX", (0, 0), (-1, -1), 1, c_border),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ])
        )
        elements.append(meta_table)
        elements.append(Spacer(1, 16))

        # --- COURSE ENROLLMENT TABLE ---
        table_rows = [
            [
                Paragraph("Sem", style_table_hdr),
                Paragraph("Course Code", style_table_hdr),
                Paragraph("Course Title", style_table_hdr),
                Paragraph("Credits", ParagraphStyle("HdrC", parent=style_table_hdr, alignment=1)),
                Paragraph("Grade", ParagraphStyle("HdrC", parent=style_table_hdr, alignment=1)),
                Paragraph("Grade Point", ParagraphStyle("HdrC", parent=style_table_hdr, alignment=1)),
            ]
        ]

        # Sort enrollments by semester then course code
        def sort_key(row: dict[str, Any]) -> tuple[int, str, str]:
            sno = str(row.get("semester_no", "0")).strip()
            try:
                sem_int = int(sno)
            except ValueError:
                sem_int = 999
            return (sem_int, sno, str(row.get("course_code", "")))

        sorted_enrollments = sorted(enrollments, key=sort_key)

        for i, row in enumerate(sorted_enrollments):
            c_code = str(row.get("course_code", "-"))
            c_title = str(row.get("course_title", "-"))
            c_cred = f"{float(row.get('credit_hours', 0)):g}" if row.get("credit_hours") else "-"
            c_sem = str(row.get("semester_no", "-"))
            c_grade = str(row.get("letter_grade", "-")).strip() or "-"
            c_gp = f"{float(row['grade_point']):.2f}" if row.get("grade_point") is not None else "-"

            table_rows.append([
                Paragraph(c_sem, style_table_cell_center),
                Paragraph(c_code, style_table_cell_bold),
                Paragraph(c_title, style_table_cell),
                Paragraph(c_cred, style_table_cell_center),
                Paragraph(c_grade, style_table_cell_bold),
                Paragraph(c_gp, style_table_cell_center),
            ])

        if not sorted_enrollments:
            table_rows.append([
                Paragraph("-", style_table_cell_center),
                Paragraph("No records", style_table_cell),
                Paragraph("No courses currently enrolled or graded.", style_table_cell),
                Paragraph("-", style_table_cell_center),
                Paragraph("-", style_table_cell_center),
                Paragraph("-", style_table_cell_center),
            ])

        col_widths = [38, 76, 230, 48, 52, 60]
        course_table = Table(table_rows, colWidths=col_widths, repeatRows=1)
        
        t_style = [
            ("BACKGROUND", (0, 0), (-1, 0), c_table_hdr),
            ("BOX", (0, 0), (-1, -1), 1, c_border),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]

        # Alternating row colors
        for row_idx in range(1, len(table_rows)):
            bg = colors.HexColor("#f8fafc") if row_idx % 2 == 1 else colors.white
            t_style.append(("BACKGROUND", (0, row_idx), (-1, row_idx), bg))

        course_table.setStyle(TableStyle(t_style))
        elements.append(course_table)
        elements.append(Spacer(1, 20))

        # --- SIGNATURE & VERIFICATION SECTION (KeepTogether so it never breaks alone) ---
        sig_data = [
            [
                Paragraph("<b>System Authentication Note:</b><br/>This document is an electronically generated academic trajectory & transcript summary verified by EduTrack Core Engine.", ParagraphStyle("Note", parent=styles["Normal"], fontSize=8, leading=11, textColor=c_muted)),
                Paragraph("<br/><br/>___________________________________<br/><b>Academic Advisor / Dept. Controller</b><br/>Department of CSE, BUBT", ParagraphStyle("Sig", parent=styles["Normal"], fontSize=8.5, leading=12, alignment=2, textColor=c_primary)),
            ]
        ]
        sig_table = Table(sig_data, colWidths=[310, 194])
        sig_table.setStyle(
            TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ])
        )
        elements.append(KeepTogether([sig_table]))

        # Build document
        doc.build(elements, canvasmaker=NumberedCanvas)
        return str(output_path)
