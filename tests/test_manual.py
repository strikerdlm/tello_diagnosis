"""Tests for the TelloManualInterface module."""

from unittest.mock import MagicMock, patch

import pytest

from tello_diagnostics.manual import TelloManualInterface


class TestTelloManualInterface:
    """Test suite for TelloManualInterface class."""

    def test_init(self) -> None:
        """Test initialization."""
        interface = TelloManualInterface()

        assert interface.tello is None
        assert not interface.connected

    @patch("tello_diagnostics.manual.Tello")
    def test_connect_success(self, mock_tello_class: MagicMock) -> None:
        """Test successful connection."""
        mock_instance = MagicMock()
        mock_instance.get_current_state.return_value = {"bat": 85}
        mock_instance.get_battery.return_value = 85
        mock_instance.get_temperature.return_value = 50.0
        mock_instance.get_height.return_value = 0
        mock_instance.get_flight_time.return_value = 0
        mock_tello_class.return_value = mock_instance

        interface = TelloManualInterface()
        result = interface.connect()

        assert result is True
        assert interface.connected is True

    def test_show_status_not_connected(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Test show_status when not connected."""
        interface = TelloManualInterface()
        interface.show_status()

        captured = capsys.readouterr()
        assert "Not connected" in captured.out

    def test_show_status_connected(
        self,
        mock_tello: MagicMock,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Test show_status when connected."""
        interface = TelloManualInterface()
        interface.tello = mock_tello
        interface.connected = True

        interface.show_status()

        captured = capsys.readouterr()
        assert "TELLO STATUS" in captured.out
        assert "Battery:" in captured.out

    def test_execute_command_not_connected(self) -> None:
        """Test execute_command when not connected."""
        interface = TelloManualInterface()
        result = interface.execute_command("battery")

        assert result is True

    def test_execute_command_exit(self) -> None:
        """Test exit command."""
        interface = TelloManualInterface()
        interface.connected = True

        result = interface.execute_command("exit")

        assert result is False

    def test_execute_command_quit(self) -> None:
        """Test quit command."""
        interface = TelloManualInterface()
        interface.connected = True

        result = interface.execute_command("quit")

        assert result is False

    def test_execute_command_help(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Test help command."""
        interface = TelloManualInterface()
        interface.connected = True

        result = interface.execute_command("help")

        assert result is True
        captured = capsys.readouterr()
        assert "Available Commands" in captured.out

    def test_execute_command_battery(
        self,
        mock_tello: MagicMock,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Test battery command."""
        interface = TelloManualInterface()
        interface.tello = mock_tello
        interface.connected = True

        result = interface.execute_command("battery")

        assert result is True
        captured = capsys.readouterr()
        assert "Battery: 85%" in captured.out

    def test_execute_command_takeoff(self, mock_tello: MagicMock) -> None:
        """Test takeoff command."""
        interface = TelloManualInterface()
        interface.tello = mock_tello
        interface.connected = True

        result = interface.execute_command("takeoff")

        assert result is True
        mock_tello.takeoff.assert_called_once()

    def test_execute_command_land(self, mock_tello: MagicMock) -> None:
        """Test land command."""
        interface = TelloManualInterface()
        interface.tello = mock_tello
        interface.connected = True

        result = interface.execute_command("land")

        assert result is True
        mock_tello.land.assert_called_once()

    def test_execute_command_up_valid(self, mock_tello: MagicMock) -> None:
        """Test up command with valid distance."""
        interface = TelloManualInterface()
        interface.tello = mock_tello
        interface.connected = True

        result = interface.execute_command("up 50")

        assert result is True
        mock_tello.move_up.assert_called_once_with(50)

    def test_execute_command_up_invalid_distance(
        self,
        mock_tello: MagicMock,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Test up command with invalid distance."""
        interface = TelloManualInterface()
        interface.tello = mock_tello
        interface.connected = True

        result = interface.execute_command("up 10")

        assert result is True
        captured = capsys.readouterr()
        assert "must be between 20 and 500" in captured.out
        mock_tello.move_up.assert_not_called()

    def test_disconnect_when_flying(self, mock_tello: MagicMock) -> None:
        """Test disconnect when drone is flying."""
        mock_tello.is_flying = True

        interface = TelloManualInterface()
        interface.tello = mock_tello
        interface.connected = True

        interface.disconnect()

        mock_tello.land.assert_called_once()
        mock_tello.end.assert_called_once()
        assert not interface.connected

    def test_disconnect_when_not_flying(self, mock_tello: MagicMock) -> None:
        """Test disconnect when drone is not flying."""
        mock_tello.is_flying = False

        interface = TelloManualInterface()
        interface.tello = mock_tello
        interface.connected = True

        interface.disconnect()

        mock_tello.land.assert_not_called()
        mock_tello.end.assert_called_once()
        assert not interface.connected

