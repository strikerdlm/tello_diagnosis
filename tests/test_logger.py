"""Tests for the TelloDataLogger module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from tello_diagnostics.logger import TelloDataLogger


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

