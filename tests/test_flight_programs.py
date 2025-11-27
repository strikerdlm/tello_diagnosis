"""Unit tests for pre-built flight program helpers."""

from typing import List
from unittest.mock import MagicMock

import pytest

from tello_diagnostics.flight_programs import (
    FlightProgram,
    FlightProgramLibrary,
    FlightProgramRunner,
    FlightStep,
    ProgramUploadError,
)


def _sleep_stub(_: float) -> None:
    """No-op sleep helper for deterministic tests."""


def test_library_lists_expected_programs() -> None:
    """Library should expose all curated programs."""
    library = FlightProgramLibrary()

    catalog = library.list_programs()
    slugs = {entry["identifier"] for entry in catalog}

    assert len(catalog) >= 4
    assert "square-dance" in slugs
    assert "spiral-climb" in slugs


def test_library_invalid_slug() -> None:
    """Unknown slugs raise an explicit error."""
    library = FlightProgramLibrary()

    with pytest.raises(ProgramUploadError):
        library.get_program("unknown")


def test_runner_executes_steps(mock_tello: MagicMock) -> None:
    """Runner should call the right Tello APIs."""
    mock_tello.get_battery.return_value = 80
    program = FlightProgram(
        identifier="unit-test",
        title="Unit Test",
        objective="Smoke test routine",
        steps=(
            FlightStep("takeoff", wait_seconds=0.0, description="Lift"),
            FlightStep("pause", wait_seconds=0.1, description="Hover"),
            FlightStep("land", wait_seconds=0.0, description="Land"),
        ),
        recommended_space_m=2.0,
        min_battery_percent=20,
        estimated_duration_seconds=5.0,
    )

    runner = FlightProgramRunner(default_pause_seconds=0.0, sleep_fn=_sleep_stub)
    messages: List[str] = []

    runner.execute(mock_tello, program, messages.append)

    assert mock_tello.takeoff.called
    assert mock_tello.land.called
    assert messages[0].startswith("Starting 'Unit Test'")
    assert messages[-1].startswith("Completed")


def test_runner_rejects_low_battery(mock_tello: MagicMock) -> None:
    """Battery guard should abort risky uploads."""
    mock_tello.get_battery.return_value = 10
    program = FlightProgram(
        identifier="requires-charge",
        title="Needs Juice",
        objective="",
        steps=(FlightStep("takeoff", wait_seconds=0.0, description=""),),
        recommended_space_m=2.0,
        min_battery_percent=50,
        estimated_duration_seconds=5.0,
    )

    runner = FlightProgramRunner(default_pause_seconds=0.0, sleep_fn=_sleep_stub)

    with pytest.raises(ProgramUploadError):
        runner.execute(mock_tello, program)
