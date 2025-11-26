"""Tests for the TelloDiagnostics module."""

from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest

from tello_diagnostics.diagnostics import TelloDiagnostics


class TestTelloDiagnostics:
    """Test suite for TelloDiagnostics class."""

    def test_init_valid_interval(self) -> None:
        """Test initialization with valid update interval."""
        diagnostics = TelloDiagnostics(update_interval=1.0)
        assert diagnostics.update_interval == 1.0
        assert not diagnostics.connected
        assert diagnostics.tello is None

    def test_init_invalid_interval_too_low(self) -> None:
        """Test initialization with invalid interval (too low)."""
        with pytest.raises(
            ValueError,
            match="update_interval must be between 0.1 and 5.0 seconds",
        ):
            TelloDiagnostics(update_interval=0.05)

    def test_init_invalid_interval_too_high(self) -> None:
        """Test initialization with invalid interval (too high)."""
        with pytest.raises(
            ValueError,
            match="update_interval must be between 0.1 and 5.0 seconds",
        ):
            TelloDiagnostics(update_interval=10.0)

    @patch("tello_diagnostics.diagnostics.Tello")
    def test_connect_success(self, mock_tello_class: MagicMock) -> None:
        """Test successful connection to Tello."""
        mock_instance = MagicMock()
        mock_instance.get_current_state.return_value = {"bat": 85}
        mock_instance.get_battery.return_value = 85
        mock_instance.query_sdk_version.return_value = "30"
        mock_tello_class.return_value = mock_instance

        diagnostics = TelloDiagnostics()
        result = diagnostics.connect()

        assert result is True
        assert diagnostics.connected is True
        mock_instance.connect.assert_called_once()

    @patch("tello_diagnostics.diagnostics.Tello")
    def test_connect_no_state(self, mock_tello_class: MagicMock) -> None:
        """Test connection failure when no state received."""
        mock_instance = MagicMock()
        mock_instance.get_current_state.return_value = None
        mock_tello_class.return_value = mock_instance

        diagnostics = TelloDiagnostics(update_interval=0.5)
        result = diagnostics.connect()

        assert result is False
        assert not diagnostics.connected

    @patch("tello_diagnostics.diagnostics.Tello")
    def test_connect_exception(self, mock_tello_class: MagicMock) -> None:
        """Test connection failure with exception."""
        mock_tello_class.side_effect = RuntimeError("Connection failed")

        diagnostics = TelloDiagnostics()
        result = diagnostics.connect()

        assert result is False
        assert not diagnostics.connected

    def test_get_diagnostics_not_connected(self) -> None:
        """Test get_diagnostics raises error when not connected."""
        diagnostics = TelloDiagnostics()

        with pytest.raises(RuntimeError, match="Not connected to Tello"):
            diagnostics.get_diagnostics()

    def test_get_diagnostics_success(self, mock_tello: MagicMock) -> None:
        """Test successful diagnostic data retrieval."""
        diagnostics = TelloDiagnostics()
        diagnostics.tello = mock_tello
        diagnostics.connected = True

        data = diagnostics.get_diagnostics()

        assert isinstance(data, dict)
        assert "battery" in data
        assert "temperature" in data
        assert "height" in data
        assert data["battery"] == 85

    def test_get_diagnostics_exception(self, mock_tello: MagicMock) -> None:
        """Test get_diagnostics handles exceptions gracefully."""
        mock_tello.get_battery.side_effect = RuntimeError("Read error")

        diagnostics = TelloDiagnostics()
        diagnostics.tello = mock_tello
        diagnostics.connected = True

        data = diagnostics.get_diagnostics()

        assert data == {}

    def test_display_diagnostics_empty(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test display_diagnostics with empty data."""
        diagnostics = TelloDiagnostics()
        diagnostics.display_diagnostics({})

        captured = capsys.readouterr()
        assert captured.out == ""

    def test_display_diagnostics_with_data(
        self,
        capsys: pytest.CaptureFixture[str],
        sample_telemetry: Dict[str, Any],
    ) -> None:
        """Test display_diagnostics with valid data."""
        diagnostics = TelloDiagnostics()
        diagnostics.display_diagnostics(sample_telemetry)

        captured = capsys.readouterr()
        assert "TELLO DIAGNOSTICS" in captured.out
        assert "Battery:" in captured.out
        assert "85%" in captured.out

    def test_monitor_not_connected(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test monitor exits gracefully when not connected."""
        diagnostics = TelloDiagnostics()
        diagnostics.monitor()

        captured = capsys.readouterr()
        assert "Not connected" in captured.out

    def test_monitor_runs_for_duration(
        self,
        sample_telemetry: Dict[str, Any],
    ) -> None:
        """Test monitor fetches data for the specified duration."""
        diagnostics = TelloDiagnostics(update_interval=0.1)
        diagnostics.connected = True
        diagnostics.get_diagnostics = MagicMock(return_value=sample_telemetry)
        diagnostics.display_diagnostics = MagicMock()

        with patch("tello_diagnostics.diagnostics.time") as mock_time:
            mock_time.monotonic.side_effect = [0.0, 0.0, 0.2]
            mock_time.sleep.return_value = None
            diagnostics.monitor(duration=0.1)

        diagnostics.display_diagnostics.assert_called_once_with(sample_telemetry)

    def test_disconnect_when_connected(self, mock_tello: MagicMock) -> None:
        """Test disconnect when connected."""
        diagnostics = TelloDiagnostics()
        diagnostics.tello = mock_tello
        diagnostics.connected = True

        diagnostics.disconnect()

        mock_tello.end.assert_called_once()
        assert not diagnostics.connected

    def test_disconnect_when_not_connected(self) -> None:
        """Test disconnect when not connected."""
        diagnostics = TelloDiagnostics()
        diagnostics.disconnect()  # Should not raise

    def test_disconnect_with_exception(
        self,
        mock_tello: MagicMock,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Test disconnect handles exceptions."""
        mock_tello.end.side_effect = RuntimeError("Disconnect error")

        diagnostics = TelloDiagnostics()
        diagnostics.tello = mock_tello
        diagnostics.connected = True

        diagnostics.disconnect()

        assert not diagnostics.connected
        captured = capsys.readouterr()
        assert "Error during disconnect" in captured.out

