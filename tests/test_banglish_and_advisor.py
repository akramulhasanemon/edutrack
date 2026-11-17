import unittest
from modules.ai_advisor import AIAdvisorEngine

class TestBanglishAndAdvisor(unittest.TestCase):
    def setUp(self):
        self.engine = AIAdvisorEngine(api_key="")
        self.student_profile = {
            "student_name": "Mahabub Shaddhow",
            "target_cgpa": 3.85,
            "program_credits": 142.0,
            "current_cgpa": 3.22,
            "completed_credits": 24.0,
            "courses": [
                {"course_code": "CSE101", "course_title": "Structured Programming", "grade_point": 3.50, "credits": 3.0},
                {"course_code": "MAT101", "course_title": "Differential Calculus", "grade_point": 2.25, "credits": 3.0},
            ],
            "weak_courses": [
                {"course_code": "MAT101", "course_title": "Differential Calculus", "grade_point": 2.25, "credits": 3.0}
            ],
            "attendance": [
                {"course_code": "MAT101", "attendance_percentage": 70.0},
                {"course_code": "CSE101", "attendance_percentage": 90.0}
            ],
            "routines": []
        }

    def test_greetings_banglish(self):
        queries = ["kemon aso", "ki obostha", "ki khobor", "valo aso", "kemon acho"]
        for q in queries:
            resp = self.engine._local_advice(self.student_profile, q)
            self.assertIn("Hello Mahabub Shaddhow", resp)
            self.assertIn("EduTrack AI", resp)

    def test_identity_banglish(self):
        queries = ["tumi ke", "ki korte paro", "who are you", "tumar kaj ki"]
        for q in queries:
            resp = self.engine._local_advice(self.student_profile, q)
            self.assertIn("EduTrack AI", resp)

    def test_routine_banglish(self):
        queries = ["porar routine dao", "kivabe porbo", "study schedule", "timetable", "shomoy paina"]
        for q in queries:
            resp = self.engine._local_advice(self.student_profile, q)
            self.assertIn("TIMETABLE", resp)

    def test_retake_banglish(self):
        queries = ["retake kivabe korbo", "retake dibo", "which course repeat", "grade replacement"]
        for q in queries:
            resp = self.engine._local_advice(self.student_profile, q)
            self.assertIn("RETAKE", resp)

    def test_motivation_banglish(self):
        queries = ["porar mon boshe na", "onek stress lagtese", "fail korbo mone hoy", "tensed"]
        for q in queries:
            resp = self.engine._local_advice(self.student_profile, q)
            self.assertIn("MOTIVATION", resp)

    def test_attendance_banglish(self):
        queries = ["attendance kom", "hazira kom", "75% er niche attendance", "class routine"]
        for q in queries:
            resp = self.engine._local_advice(self.student_profile, q)
            self.assertIn("ATTENDANCE", resp)

    def test_any_unseen_query_fallback(self):
        resp = self.engine._local_advice(self.student_profile, "amar kichu bhalo lagche na ki korbo bolen toh")
        self.assertIn("EDUTRACK AI", resp)
        self.assertTrue(len(resp) > 50)

if __name__ == "__main__":
    unittest.main()
