"""Pytest configuration and shared fixtures."""

from typing import Any, Dict
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_tello() -> MagicMock:
    """
    Create a mock Tello object for testing.

    Returns:
        MagicMock: Mock Tello instance with common methods
    """
    mock = MagicMock()

    # Configure return values for common methods
    mock.get_battery.return_value = 85
    mock.get_temperature.return_value = 50.0
    mock.get_lowest_temperature.return_value = 48
    mock.get_highest_temperature.return_value = 52
    mock.get_flight_time.return_value = 0
    mock.get_height.return_value = 0
    mock.get_barometer.return_value = 100
    mock.get_distance_tof.return_value = 10
    mock.get_pitch.return_value = 0
    mock.get_roll.return_value = 0
    mock.get_yaw.return_value = 0
    mock.get_speed_x.return_value = 0
    mock.get_speed_y.return_value = 0
    mock.get_speed_z.return_value = 0
    mock.query_speed.return_value = 0
    mock.get_acceleration_x.return_value = 0.0
    mock.get_acceleration_y.return_value = 0.0
    mock.get_acceleration_z.return_value = 0.0
    mock.query_sdk_version.return_value = "30"
    mock.get_current_state.return_value = {
        "pitch": 0,
        "roll": 0,
        "yaw": 0,
        "bat": 85,
    }
    mock.is_flying = False

    return mock


@pytest.fixture
def sample_telemetry() -> Dict[str, Any]:
    """
    Provide sample telemetry data for testing.

    Returns:
        Dict[str, Any]: Sample diagnostic data
    """
    return {
        "battery": 85,
        "temperature": 50.0,
        "temp_low": 48,
        "temp_high": 52,
        "flight_time": 0,
        "height": 0,
        "barometer": 100,
        "tof_distance": 10,
        "pitch": 0,
        "roll": 0,
        "yaw": 0,
        "speed_x": 0,
        "speed_y": 0,
        "speed_z": 0,
        "accel_x": 0.0,
        "accel_y": 0.0,
        "accel_z": 0.0,
    }

