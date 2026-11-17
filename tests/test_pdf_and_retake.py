"""Unit tests for AcademicPDFReport and Course Retake simulation calculations."""

import math
import os
import tempfile
from pathlib import Path

from modules.pdf_generator import AcademicPDFReport


def test_academic_standing_classification() -> None:
    standing, _ = AcademicPDFReport.get_academic_standing(3.85)
    assert standing == "Dean's Honor Roll"

    standing, _ = AcademicPDFReport.get_academic_standing(3.60)
    assert standing == "High Distinction"

    standing, _ = AcademicPDFReport.get_academic_standing(3.20)
    assert standing == "Good Standing"

    standing, _ = AcademicPDFReport.get_academic_standing(2.70)
    assert standing == "Satisfactory Pace"

    standing, _ = AcademicPDFReport.get_academic_standing(2.20)
    assert standing == "Academic Monitoring"

    standing, _ = AcademicPDFReport.get_academic_standing(None)
    assert "No Graded Records" in standing


def test_pdf_transcript_generation() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        pdf_path = Path(tmp_dir) / "test_report.pdf"
        student_info = {
            "name": "Shahadat Hossain",
            "student_id": "20255103311",
            "semester": "Fall 2026",
            "role": "Student",
        }
        enrollments = [
            {
                "course_code": "CSE101",
                "course_title": "Structured Programming",
                "credit_hours": 3.0,
                "semester_no": "1",
                "letter_grade": "A+",
                "grade_point": 4.0,
            },
            {
                "course_code": "MAT101",
                "course_title": "Calculus",
                "credit_hours": 3.0,
                "semester_no": "1",
                "letter_grade": "A-",
                "grade_point": 3.5,
            },
        ]
        out_file = AcademicPDFReport.generate_transcript_pdf(
            filename=pdf_path,
            student_info=student_info,
            enrollments=enrollments,
            current_cgpa=3.75,
            completed_credits=6.0,
            program_credits=142.0,
        )
        assert Path(out_file).exists()
        assert Path(out_file).stat().st_size > 1000  # valid PDF generated


def test_retake_cgpa_calculation_formula() -> None:
    # Student has 60 total credits and 3.00 CGPA (180 total grade points).
    # Retakes a 3-credit course that previously had a C (2.25) = 6.75 points.
    # Replaces with an A (3.75) = 11.25 points.
    # New total points = 180 - 6.75 + 11.25 = 184.5
    # New CGPA = 184.5 / 60 = 3.075 -> 3.08
    # Boost = +0.075 -> +0.08
    total_credits = 60.0
    current_cgpa = 3.00
    course_credits = 3.0
    old_gp = 2.25
    target_gp = 3.75

    current_points = current_cgpa * total_credits
    new_points = current_points - (course_credits * old_gp) + (course_credits * target_gp)
    new_cgpa = new_points / total_credits
    boost = new_cgpa - current_cgpa

    assert math.isclose(new_cgpa, 3.075, rel_tol=1e-5)
    assert math.isclose(boost, 0.075, rel_tol=1e-5)
