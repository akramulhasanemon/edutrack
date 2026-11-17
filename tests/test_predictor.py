"""Unit tests for the TrajectoryEngine and CGPA prediction logic."""

from modules.predictor import TrajectoryEngine


def test_trajectory_engine_basic_calculation() -> None:
    # Student has 3.00 CGPA with 60 credits completed, targets 3.50 with 60 remaining credits.
    # Total credits = 120, total required points = 120 * 3.5 = 420
    # Current points = 60 * 3.0 = 180
    # Remaining points needed = 240 / 60 = 4.00
    engine = TrajectoryEngine(
        current_cgpa=3.00,
        completed_credits=60.0,
        target_cgpa=3.50,
        remaining_credits=60.0,
    )
    assert engine.calculate_required_gpa() == 4.00


def test_trajectory_engine_zero_remaining_credits() -> None:
    engine = TrajectoryEngine(
        current_cgpa=3.80,
        completed_credits=120.0,
        target_cgpa=3.80,
        remaining_credits=0.0,
    )
    assert engine.calculate_required_gpa() == 0.0


def test_trajectory_target_status_exceeds_maximum() -> None:
    # Requires higher than 4.00
    req_gpa, status = TrajectoryEngine.calculate_target_required_gpa(
        current_cgpa=2.50,
        completed_credits=100.0,
        target_cgpa=3.90,
        remaining_credits=20.0,
    )
    assert req_gpa > 4.0
    assert "Target exceeds the maximum GPA" in status


def test_trajectory_target_status_already_on_track() -> None:
    # Target is already met / negative required GPA
    req_gpa, status = TrajectoryEngine.calculate_target_required_gpa(
        current_cgpa=3.95,
        completed_credits=100.0,
        target_cgpa=3.00,
        remaining_credits=20.0,
    )
    assert req_gpa <= 0
    assert "already on track" in status


def test_trajectory_target_status_feasible() -> None:
    req_gpa, status = TrajectoryEngine.calculate_target_required_gpa(
        current_cgpa=3.20,
        completed_credits=60.0,
        target_cgpa=3.50,
        remaining_credits=60.0,
    )
    assert 0 < req_gpa <= 4.0
    assert "Target is achievable" in status
