"""Simple test runner to execute all project tests without external test frameworks."""

import sys
import unittest
import tests.test_ai_advisor as ta
import tests.test_banglish_and_advisor as tba
import tests.test_pdf_and_retake as tpr
import tests.test_predictor as tp


def main() -> int:
    def run_banglish_tests():
        suite = unittest.TestLoader().loadTestsFromTestCase(tba.TestBanglishAndAdvisor)
        result = unittest.TextTestRunner(stream=sys.stdout, verbosity=0).run(suite)
        if not result.wasSuccessful():
            raise AssertionError(f"{len(result.failures)} tests failed, {len(result.errors)} errors")

    tests_to_run = [
        ("Predictor - Basic calculation", tp.test_trajectory_engine_basic_calculation),
        ("Predictor - Zero remaining credits", tp.test_trajectory_engine_zero_remaining_credits),
        ("Predictor - Target exceeds maximum", tp.test_trajectory_target_status_exceeds_maximum),
        ("Predictor - Already on track", tp.test_trajectory_target_status_already_on_track),
        ("Predictor - Feasible target", tp.test_trajectory_target_status_feasible),
        ("AI Advisor - Local advice fallback", ta.test_local_advice_uses_course_and_attendance_records),
        ("AI Advisor - Prompt formatting", ta.test_prompt_contains_complete_profile_and_trainer_instructions),
        ("AI Advisor - Banglish & Multilingual Intents", run_banglish_tests),
        ("Academic PDF - Standing classification", tpr.test_academic_standing_classification),
        ("Academic PDF - Transcript PDF generation", tpr.test_pdf_transcript_generation),
        ("Simulator - Retake CGPA boost formula", tpr.test_retake_cgpa_calculation_formula),
    ]

    passed = 0
    failed = 0

    print("Running EduTrack test suite...")
    print("-" * 50)
    for name, test_fn in tests_to_run:
        try:
            test_fn()
            print(f"[PASS] {name}")
            passed += 1
        except Exception as exc:
            print(f"[FAIL] {name}: {exc}")
            failed += 1

    print("-" * 50)
    print(f"Results: {passed} passed, {failed} failed.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
