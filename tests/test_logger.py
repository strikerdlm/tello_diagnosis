"""Tests for the TelloDataLogger module."""

import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from tello_diagnostics.logger import TelloDataLogger, parse_arguments, main as logger_main


class TestTelloDataLogger:
    """Test suite for TelloDataLogger class."""

    def test_init_valid_params(self, tmp_path: Path) -> None:
        """Test initialization with valid parameters."""
        output_file = tmp_path / "test.csv"
        logger = TelloDataLogger(
            output_file=output_file,
            sample_rate=0.1,
            max_samples=100,
        )

        assert logger.output_file == output_file
        assert logger.sample_rate == 0.1
        assert logger.max_samples == 100
        assert not logger.connected

    def test_init_invalid_sample_rate_too_low(self, tmp_path: Path) -> None:
        """Test initialization with invalid sample rate (too low)."""
        with pytest.raises(
            ValueError,
            match="sample_rate must be between 0.05 and 10.0 seconds",
        ):
            TelloDataLogger(
                output_file=tmp_path / "test.csv",
                sample_rate=0.01,
            )

    def test_init_invalid_sample_rate_too_high(self, tmp_path: Path) -> None:
        """Test initialization with invalid sample rate (too high)."""
        with pytest.raises(
            ValueError,
            match="sample_rate must be between 0.05 and 10.0 seconds",
        ):
            TelloDataLogger(
                output_file=tmp_path / "test.csv",
                sample_rate=20.0,
            )

    def test_init_invalid_max_samples(self, tmp_path: Path) -> None:
        """Test initialization with invalid max_samples."""
        with pytest.raises(ValueError, match="max_samples must be positive"):
            TelloDataLogger(
                output_file=tmp_path / "test.csv",
                max_samples=-1,
            )

    @patch("tello_diagnostics.logger.Tello")
    def test_connect_success(self, mock_tello_class: MagicMock, tmp_path: Path) -> None:
        """Test successful connection."""
        mock_instance = MagicMock()
        mock_instance.get_current_state.return_value = {"bat": 85}
        mock_instance.get_battery.return_value = 85
        mock_instance.query_sdk_version.return_value = "30"
        mock_tello_class.return_value = mock_instance

        logger = TelloDataLogger(output_file=tmp_path / "test.csv")
        result = logger.connect()

        assert result is True
        assert logger.connected is True

    def test_collect_sample_not_connected(self, tmp_path: Path) -> None:
        """Test collect_sample raises error when not connected."""
        logger = TelloDataLogger(output_file=tmp_path / "test.csv")

        with pytest.raises(RuntimeError, match="Not connected to Tello"):
            logger.collect_sample()

    def test_collect_sample_success(
        self,
        mock_tello: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test successful sample collection."""
        logger = TelloDataLogger(output_file=tmp_path / "test.csv")
        logger.tello = mock_tello
        logger.connected = True
        logger.start_time = 1000.0

        with patch("tello_diagnostics.logger.time.time", return_value=1001.0):
            sample = logger.collect_sample()

        assert isinstance(sample, dict)
        assert "timestamp" in sample
        assert "battery" in sample
        assert sample["battery"] == 85

    def test_write_csv_header(self, tmp_path: Path) -> None:
        """Test CSV header writing."""
        output_file = tmp_path / "test.csv"
        logger = TelloDataLogger(output_file=output_file)

        logger.write_csv_header()

        assert output_file.exists()
        content = output_file.read_text()
        assert "timestamp" in content
        assert "battery" in content

    def test_disconnect(self, mock_tello: MagicMock, tmp_path: Path) -> None:
        """Test disconnect functionality."""
        logger = TelloDataLogger(output_file=tmp_path / "test.csv")
        logger.tello = mock_tello
        logger.connected = True

        logger.disconnect()

        mock_tello.end.assert_called_once()
        assert not logger.connected

    def test_log_data_requires_connection(
        self,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """log_data should abort when not connected."""
        logger = TelloDataLogger(output_file=tmp_path / "test.csv")

        samples = logger.log_data()

        assert samples == 0
        captured = capsys.readouterr()
        assert "Error: Not connected to Tello" in captured.out

    def test_log_data_respects_max_samples(
        self,
        tmp_path: Path,
        mock_tello: MagicMock,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """log_data should stop when max_samples reached."""
        output_file = tmp_path / "log.csv"
        logger = TelloDataLogger(
            output_file=output_file,
            sample_rate=0.05,
            max_samples=2,
        )
        logger.tello = mock_tello
        logger.connected = True

        time_values = iter([0.0, 0.0, 0.01, 0.05, 0.06, 0.1, 0.11])
        with patch("tello_diagnostics.logger.time.time", side_effect=time_values):
            with patch("tello_diagnostics.logger.time.sleep", return_value=None):
                samples = logger.log_data()

        assert samples == 2
        rows = output_file.read_text().strip().splitlines()
        assert len(rows) == 3  # header + 2 samples
        captured = capsys.readouterr()
        assert "Maximum samples reached." in captured.out

    def test_log_data_respects_duration(
        self,
        tmp_path: Path,
        mock_tello: MagicMock,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """log_data should honor the provided duration limit."""
        output_file = tmp_path / "duration.csv"
        logger = TelloDataLogger(
            output_file=output_file,
            sample_rate=0.05,
        )
        logger.tello = mock_tello
        logger.connected = True

        time_values = iter([0.0, 0.0, 0.01, 0.2, 0.21])
        with patch("tello_diagnostics.logger.time.time", side_effect=time_values):
            with patch("tello_diagnostics.logger.time.sleep", return_value=None):
                samples = logger.log_data(duration=0.01)

        assert samples == 1
        rows = output_file.read_text().strip().splitlines()
        assert len(rows) == 2  # header + 1 sample
        captured = capsys.readouterr()
        assert "Logging duration reached." in captured.out

    def test_log_data_emits_progress(
        self,
        tmp_path: Path,
        mock_tello: MagicMock,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """log_data should print progress every 10 samples."""
        output_file = tmp_path / "progress.csv"
        logger = TelloDataLogger(
            output_file=output_file,
            sample_rate=0.05,
            max_samples=10,
        )
        logger.tello = mock_tello
        logger.connected = True

        time_values = iter([i * 0.05 for i in range(40)])
        with patch("tello_diagnostics.logger.time.time", side_effect=time_values):
            with patch("tello_diagnostics.logger.time.sleep", return_value=None):
                samples = logger.log_data()

        assert samples == 10
        captured = capsys.readouterr()
        assert "Samples:   10" in captured.out or "Samples:  10" in captured.out

    def test_parse_arguments_custom_values(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """parse_arguments should reflect command-line options."""
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "prog",
                "--output",
                "foo.csv",
                "--duration",
                "2",
                "--rate",
                "0.2",
                "--max-samples",
                "5",
            ],
        )

        args = parse_arguments()

        assert args.output == "foo.csv"
        assert args.duration == 2
        assert args.rate == 0.2
        assert args.max_samples == 5

    @patch("tello_diagnostics.logger.input", return_value="")
    @patch("tello_diagnostics.logger.parse_arguments")
    def test_logger_main_success(
        self,
        mock_parse: MagicMock,
        _: MagicMock,
    ) -> None:
        """Main should run logger flow when connected."""
        args = SimpleNamespace(output="main.csv", duration=1.0, rate=0.1, max_samples=2)
        mock_parse.return_value = args
        mock_logger = MagicMock()

        with patch("tello_diagnostics.logger.TelloDataLogger", return_value=mock_logger):
            mock_logger.connect.return_value = True
            mock_logger.log_data.return_value = 2
            result = logger_main()

        assert result == 0
        mock_logger.log_data.assert_called_once_with(duration=args.duration)
        mock_logger.disconnect.assert_called_once()

    @patch("tello_diagnostics.logger.input", return_value="")
    @patch("tello_diagnostics.logger.parse_arguments")
    def test_logger_main_connection_failure(
        self,
        mock_parse: MagicMock,
        _: MagicMock,
    ) -> None:
        """Main should abort when connection fails."""
        args = SimpleNamespace(output="main.csv", duration=None, rate=0.1, max_samples=None)
        mock_parse.return_value = args
        mock_logger = MagicMock()

        with patch("tello_diagnostics.logger.TelloDataLogger", return_value=mock_logger):
            mock_logger.connect.return_value = False
            result = logger_main()

        assert result == 1
        mock_logger.log_data.assert_not_called()
        mock_logger.disconnect.assert_not_called()

