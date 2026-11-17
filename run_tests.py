"""Simple test runner to execute all project tests without external test frameworks."""

import sys
import tests.test_ai_advisor as ta
import tests.test_predictor as tp


def main() -> int:
    tests_to_run = [
        ("Predictor - Basic calculation", tp.test_trajectory_engine_basic_calculation),
        ("Predictor - Zero remaining credits", tp.test_trajectory_engine_zero_remaining_credits),
        ("Predictor - Target exceeds maximum", tp.test_trajectory_target_status_exceeds_maximum),
        ("Predictor - Already on track", tp.test_trajectory_target_status_already_on_track),
        ("Predictor - Feasible target", tp.test_trajectory_target_status_feasible),
        ("AI Advisor - Local advice fallback", ta.test_local_advice_uses_course_and_attendance_records),
        ("AI Advisor - Prompt formatting", ta.test_prompt_contains_complete_profile_and_trainer_instructions),
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
