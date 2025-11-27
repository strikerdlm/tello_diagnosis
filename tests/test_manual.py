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

    @patch("tello_diagnostics.manual.Tello")
    def test_connect_failure_no_state(self, mock_tello_class: MagicMock) -> None:
        """Test connection failure when no telemetry available."""
        mock_instance = MagicMock()
        mock_instance.get_current_state.return_value = None
        mock_tello_class.return_value = mock_instance

        interface = TelloManualInterface()
        result = interface.connect()

        assert result is False
        assert not interface.connected

    @patch("tello_diagnostics.manual.Tello")
    def test_connect_exception(self, mock_tello_class: MagicMock) -> None:
        """Test exception during connection."""
        mock_tello_class.side_effect = RuntimeError("boom")

        interface = TelloManualInterface()
        result = interface.connect()

        assert result is False
        assert not interface.connected

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

    def test_execute_command_emergency(self, mock_tello: MagicMock) -> None:
        """Test emergency command."""
        interface = TelloManualInterface()
        interface.tello = mock_tello
        interface.connected = True

        result = interface.execute_command("emergency")

        assert result is True
        mock_tello.emergency.assert_called_once()

    def test_execute_command_status_calls_show_status(
        self,
        mock_tello: MagicMock,
    ) -> None:
        """Test status command delegates to show_status."""
        interface = TelloManualInterface()
        interface.tello = mock_tello
        interface.connected = True
        interface.show_status = MagicMock()

        interface.execute_command("status")

        interface.show_status.assert_called_once()

    def test_execute_command_rotate_cw(self, mock_tello: MagicMock) -> None:
        """Test cw rotation."""
        interface = TelloManualInterface()
        interface.tello = mock_tello
        interface.connected = True

        result = interface.execute_command("cw 90")

        assert result is True
        mock_tello.rotate_clockwise.assert_called_once_with(90)

    def test_execute_command_rotate_invalid_degrees(
        self,
        mock_tello: MagicMock,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Test cw rotation with invalid degrees."""
        interface = TelloManualInterface()
        interface.tello = mock_tello
        interface.connected = True

        result = interface.execute_command("cw 0")

        assert result is True
        captured = capsys.readouterr()
        assert "Degrees must be between 1 and 360" in captured.out
        mock_tello.rotate_clockwise.assert_not_called()

    def test_execute_command_flip_valid(self, mock_tello: MagicMock) -> None:
        """Test flip command."""
        interface = TelloManualInterface()
        interface.tello = mock_tello
        interface.connected = True

        result = interface.execute_command("flip l")

        assert result is True
        mock_tello.flip.assert_called_once_with("l")

    def test_execute_command_flip_invalid_direction(
        self,
        mock_tello: MagicMock,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Test flip command with invalid direction."""
        interface = TelloManualInterface()
        interface.tello = mock_tello
        interface.connected = True

        result = interface.execute_command("flip x")

        assert result is True
        captured = capsys.readouterr()
        assert "Direction must be" in captured.out
        mock_tello.flip.assert_not_called()

    @pytest.mark.parametrize(
        ("command", "expected"),
        [
            ("battery", "Battery: 85%"),
            ("speed", "Speed: 0 cm/s"),
            ("time", "Flight time: 0s"),
            ("height", "Height: 0 cm"),
            ("tof", "TOF Distance: 10 cm"),
            ("baro", "Barometer: 100 cm"),
        ],
    )
    def test_execute_command_readouts(
        self,
        command: str,
        expected: str,
        mock_tello: MagicMock,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Test multiple read commands."""
        interface = TelloManualInterface()
        interface.tello = mock_tello
        interface.connected = True

        result = interface.execute_command(command)

        assert result is True
        captured = capsys.readouterr()
        assert expected in captured.out

    def test_execute_command_temperature(
        self,
        mock_tello: MagicMock,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Test temperature command."""
        interface = TelloManualInterface()
        interface.tello = mock_tello
        interface.connected = True

        result = interface.execute_command("temp")

        assert result is True
        captured = capsys.readouterr()
        assert "Temperature" in captured.out

    def test_execute_command_attitude(
        self,
        mock_tello: MagicMock,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Test attitude command."""
        interface = TelloManualInterface()
        interface.tello = mock_tello
        interface.connected = True

        result = interface.execute_command("attitude")

        assert result is True
        captured = capsys.readouterr()
        assert "Attitude - Pitch" in captured.out

    def test_execute_command_acceleration(
        self,
        mock_tello: MagicMock,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Test acceleration command."""
        interface = TelloManualInterface()
        interface.tello = mock_tello
        interface.connected = True

        result = interface.execute_command("acceleration")

        assert result is True
        captured = capsys.readouterr()
        assert "Acceleration - X" in captured.out

    def test_execute_command_state(
        self,
        mock_tello: MagicMock,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Test state command."""
        interface = TelloManualInterface()
        interface.tello = mock_tello
        interface.connected = True

        result = interface.execute_command("state")

        assert result is True
        captured = capsys.readouterr()
        assert "pitch" in captured.out.lower()

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

    def test_programs_command_list(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Ensure the catalog is printed."""
        interface = TelloManualInterface()

        result = interface.execute_command("programs")

        assert result is True
        output = capsys.readouterr().out
        assert "Available Flight Programs" in output

    def test_programs_command_info(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Ensure detailed info renders without connection."""
        interface = TelloManualInterface()

        result = interface.execute_command("programs info square-dance")

        assert result is True
        output = capsys.readouterr().out
        assert "Square Dance" in output

    def test_programs_command_run(
        self,
        mock_tello: MagicMock,
    ) -> None:
        """Ensure `programs run` delegates to the runner."""
        interface = TelloManualInterface()
        interface.tello = mock_tello
        interface.connected = True

        mock_runner = MagicMock()
        interface.program_runner = mock_runner

        result = interface.execute_command("programs run square-dance")

        assert result is True
        mock_runner.execute.assert_called_once()

    def test_programs_run_requires_connection(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """programs run should prompt to connect first."""
        interface = TelloManualInterface()

        result = interface.execute_command("programs run square-dance")

        assert result is True
        output = capsys.readouterr().out
        assert "Connect to the Tello" in output

    @patch("builtins.input", side_effect=["help", "exit"])
    def test_run_processes_commands(
        self,
        mock_input: MagicMock,
        mock_tello: MagicMock,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Run loop should continue until exit command."""
        interface = TelloManualInterface()
        interface.tello = mock_tello
        interface.connected = True

        interface.run()

        captured = capsys.readouterr()
        assert "Tello Manual Command Interface" in captured.out
        assert mock_input.call_count == 2

