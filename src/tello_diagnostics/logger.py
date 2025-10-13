"""
DJI Tello Data Logger

Logs comprehensive diagnostic data from Tello drone to CSV file
for analysis and research purposes.
"""

import time
import csv
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from djitellopy import Tello


class TelloDataLogger:
    """Log Tello diagnostic data to CSV file."""

    # CSV column headers
    HEADERS = [
        "timestamp",
        "elapsed_time",
        "battery",
        "temperature",
        "temp_low",
        "temp_high",
        "flight_time",
        "height",
        "barometer",
        "tof_distance",
        "pitch",
        "roll",
        "yaw",
        "speed_x",
        "speed_y",
        "speed_z",
        "accel_x",
        "accel_y",
        "accel_z",
    ]

    def __init__(
        self,
        output_file: Path,
        sample_rate: float = 0.1,
        max_samples: Optional[int] = None
    ):
        """
        Initialize data logger.

        Args:
            output_file: Path to output CSV file
            sample_rate: Time between samples in seconds (default: 0.1 = 10Hz)
            max_samples: Maximum number of samples (None for unlimited)
        """
        if not (0.05 <= sample_rate <= 10.0):
            raise ValueError("sample_rate must be between 0.05 and 10.0 seconds")

        if max_samples is not None and max_samples <= 0:
            raise ValueError("max_samples must be positive")

        self.output_file = output_file
        self.sample_rate = sample_rate
        self.max_samples = max_samples
        self.tello: Optional[Tello] = None
        self.connected = False
        self.data_buffer: List[Dict[str, Any]] = []
        self.start_time: float = 0.0

    def connect(self) -> bool:
        """
        Connect to Tello drone.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            print("Connecting to Tello...")
            self.tello = Tello()
            self.tello.connect()

            # Wait for state data
            max_wait = 5.0
            elapsed = 0.0
            wait_step = 0.1

            while elapsed < max_wait:
                if self.tello.get_current_state():
                    self.connected = True
                    battery = self.tello.get_battery()
                    sdk_version = self.tello.query_sdk_version()
                    print(f"✓ Connected! Battery: {battery}%, SDK: {sdk_version}")
                    return True
                time.sleep(wait_step)
                elapsed += wait_step

            print("✗ Failed to receive state data")
            return False

        except Exception as e:
            print(f"✗ Connection failed: {e}")
            return False

    def collect_sample(self) -> Dict[str, Any]:
        """
        Collect one sample of diagnostic data.

        Returns:
            Dict containing timestamped telemetry data
        """
        if not self.connected or self.tello is None:
            raise RuntimeError("Not connected to Tello")

        current_time = time.time()
        elapsed = current_time - self.start_time

        sample = {
            "timestamp": datetime.fromtimestamp(current_time).isoformat(),
            "elapsed_time": round(elapsed, 3),
            "battery": self.tello.get_battery(),
            "temperature": round(self.tello.get_temperature(), 2),
            "temp_low": self.tello.get_lowest_temperature(),
            "temp_high": self.tello.get_highest_temperature(),
            "flight_time": self.tello.get_flight_time(),
            "height": self.tello.get_height(),
            "barometer": self.tello.get_barometer(),
            "tof_distance": self.tello.get_distance_tof(),
            "pitch": self.tello.get_pitch(),
            "roll": self.tello.get_roll(),
            "yaw": self.tello.get_yaw(),
            "speed_x": self.tello.get_speed_x(),
            "speed_y": self.tello.get_speed_y(),
            "speed_z": self.tello.get_speed_z(),
            "accel_x": round(self.tello.get_acceleration_x(), 3),
            "accel_y": round(self.tello.get_acceleration_y(), 3),
            "accel_z": round(self.tello.get_acceleration_z(), 3),
        }

        return sample

    def write_csv_header(self) -> None:
        """Write CSV header to output file."""
        with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.HEADERS)
            writer.writeheader()

    def append_to_csv(self, sample: Dict[str, Any]) -> None:
        """
        Append sample to CSV file.

        Args:
            sample: Data sample to write
        """
        with open(self.output_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.HEADERS)
            writer.writerow(sample)

    def log_data(self, duration: Optional[float] = None) -> int:
        """
        Start logging data.

        Args:
            duration: Logging duration in seconds (None for unlimited)

        Returns:
            int: Number of samples collected
        """
        if not self.connected:
            print("Error: Not connected to Tello")
            return 0

        print(f"\nStarting data logging...")
        print(f"Output file: {self.output_file}")
        print(f"Sample rate: {self.sample_rate}s ({1/self.sample_rate:.1f} Hz)")
        if duration:
            print(f"Duration: {duration}s")
        if self.max_samples:
            print(f"Max samples: {self.max_samples}")
        print("\nPress Ctrl+C to stop logging\n")

        # Initialize CSV file
        self.write_csv_header()

        self.start_time = time.time()
        sample_count = 0
        next_sample_time = self.start_time

        try:
            while True:
                current_time = time.time()

                # Check duration limit
                if duration:
                    elapsed = current_time - self.start_time
                    if elapsed >= duration:
                        print("\nLogging duration reached.")
                        break

                # Check sample count limit
                if self.max_samples and sample_count >= self.max_samples:
                    print("\nMaximum samples reached.")
                    break

                # Time to collect next sample
                if current_time >= next_sample_time:
                    try:
                        sample = self.collect_sample()
                        self.append_to_csv(sample)
                        sample_count += 1

                        # Progress indicator
                        if sample_count % 10 == 0:
                            elapsed = sample["elapsed_time"]
                            battery = sample["battery"]
                            print(f"Samples: {sample_count:4d} | "
                                  f"Elapsed: {elapsed:6.1f}s | "
                                  f"Battery: {battery:3d}%")

                        next_sample_time += self.sample_rate

                    except Exception as e:
                        print(f"Error collecting sample: {e}")

                # Sleep briefly to avoid busy-waiting
                time.sleep(0.001)

        except KeyboardInterrupt:
            print("\n\nLogging stopped by user.")

        return sample_count

    def disconnect(self) -> None:
        """Disconnect from Tello."""
        if self.tello is not None:
            try:
                self.tello.end()
                print("Disconnected from Tello.")
            except Exception as e:
                print(f"Error during disconnect: {e}")
            finally:
                self.connected = False


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Log DJI Tello diagnostic data to CSV file"
    )

    parser.add_argument(
        "-o", "--output",
        type=str,
        default=f"tello_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        help="Output CSV file path (default: tello_log_TIMESTAMP.csv)"
    )

    parser.add_argument(
        "-d", "--duration",
        type=float,
        default=None,
        help="Logging duration in seconds (default: unlimited)"
    )

    parser.add_argument(
        "-r", "--rate",
        type=float,
        default=0.1,
        help="Sample rate in seconds (default: 0.1 = 10Hz)"
    )

    parser.add_argument(
        "-n", "--max-samples",
        type=int,
        default=None,
        help="Maximum number of samples (default: unlimited)"
    )

    return parser.parse_args()


def main() -> int:
    """Main entry point."""
    args = parse_arguments()

    print("=" * 60)
    print("DJI TELLO DATA LOGGER")
    print("=" * 60)
    print()
    print("Prerequisites:")
    print("1. Turn on your Tello drone")
    print("2. Connect your computer to Tello's Wi-Fi (TELLO-XXXXXX)")
    print()

    input("Press Enter when ready to connect...")
    print()

    # Create logger
    output_path = Path(args.output)
    logger = TelloDataLogger(
        output_file=output_path,
        sample_rate=args.rate,
        max_samples=args.max_samples
    )

    # Connect to Tello
    if not logger.connect():
        print("\nFailed to connect. Please check:")
        print("- Tello is powered on")
        print("- Computer is connected to Tello Wi-Fi")
        print("- No other applications are using the Tello")
        return 1

    # Start logging
    try:
        sample_count = logger.log_data(duration=args.duration)
        print(f"\n✓ Logged {sample_count} samples to {output_path}")
        return 0

    finally:
        logger.disconnect()


if __name__ == "__main__":
    sys.exit(main())
