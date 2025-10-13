"""
DJI Tello Diagnostics Tool

Real-time monitoring of Tello drone diagnostic data including battery,
temperature, attitude, acceleration, and sensor readings.
"""

import time
import sys
from typing import Dict, Any, Optional
from djitellopy import Tello


class TelloDiagnostics:
    """Monitor and display Tello diagnostic data in real-time."""

    def __init__(self, update_interval: float = 0.5):
        """
        Initialize Tello diagnostics monitor.

        Args:
            update_interval: Time between display updates in seconds (default: 0.5)
        """
        if not (0.1 <= update_interval <= 5.0):
            raise ValueError("update_interval must be between 0.1 and 5.0 seconds")

        self.tello: Optional[Tello] = None
        self.update_interval = update_interval
        self.connected = False

    def connect(self) -> bool:
        """
        Connect to the Tello drone.

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            print("Initializing connection to Tello...")
            self.tello = Tello()
            self.tello.connect()

            # Wait for first state packet
            max_wait = 5.0
            elapsed = 0.0
            wait_step = 0.1

            while elapsed < max_wait:
                state = self.tello.get_current_state()
                if state:
                    self.connected = True
                    print(f"✓ Connected successfully!")
                    print(f"✓ Battery: {self.tello.get_battery()}%")
                    print(f"✓ SDK Version: {self.tello.query_sdk_version()}")
                    return True
                time.sleep(wait_step)
                elapsed += wait_step

            print("✗ Failed to receive state data from Tello")
            return False

        except Exception as e:
            print(f"✗ Connection failed: {e}")
            return False

    def get_diagnostics(self) -> Dict[str, Any]:
        """
        Retrieve all diagnostic data from Tello.

        Returns:
            Dict containing all telemetry data
        """
        if not self.connected or self.tello is None:
            raise RuntimeError("Not connected to Tello")

        try:
            diagnostics = {
                # Power and status
                "battery": self.tello.get_battery(),
                "temperature": self.tello.get_temperature(),
                "temp_low": self.tello.get_lowest_temperature(),
                "temp_high": self.tello.get_highest_temperature(),
                "flight_time": self.tello.get_flight_time(),

                # Position and altitude
                "height": self.tello.get_height(),
                "barometer": self.tello.get_barometer(),
                "tof_distance": self.tello.get_distance_tof(),

                # Attitude
                "pitch": self.tello.get_pitch(),
                "roll": self.tello.get_roll(),
                "yaw": self.tello.get_yaw(),

                # Velocity
                "speed_x": self.tello.get_speed_x(),
                "speed_y": self.tello.get_speed_y(),
                "speed_z": self.tello.get_speed_z(),

                # Acceleration
                "accel_x": self.tello.get_acceleration_x(),
                "accel_y": self.tello.get_acceleration_y(),
                "accel_z": self.tello.get_acceleration_z(),
            }

            return diagnostics

        except Exception as e:
            print(f"Error reading diagnostics: {e}")
            return {}

    def display_diagnostics(self, data: Dict[str, Any]) -> None:
        """
        Display diagnostic data in formatted output.

        Args:
            data: Dictionary containing diagnostic data
        """
        if not data:
            return

        # Clear screen (Windows compatible)
        print("\033[2J\033[H", end="")

        print("=" * 60)
        print("DJI TELLO DIAGNOSTICS - REAL-TIME MONITOR")
        print("=" * 60)
        print()

        # Power Status
        print("┌─ POWER & STATUS " + "─" * 41)
        battery = data.get("battery", 0)
        bat_indicator = "█" * (battery // 5) + "░" * (20 - battery // 5)
        print(f"│ Battery:       {battery:3d}% [{bat_indicator}]")
        print(f"│ Temperature:   {data.get('temperature', 0):5.1f}°C  "
              f"(Range: {data.get('temp_low', 0)}°C - {data.get('temp_high', 0)}°C)")
        print(f"│ Flight Time:   {data.get('flight_time', 0):3d}s")
        print()

        # Position & Altitude
        print("┌─ POSITION & ALTITUDE " + "─" * 36)
        print(f"│ Height:        {data.get('height', 0):5d} cm")
        print(f"│ Barometer:     {data.get('barometer', 0):5d} cm")
        print(f"│ TOF Distance:  {data.get('tof_distance', 0):5d} cm")
        print()

        # Attitude
        print("┌─ ATTITUDE (IMU) " + "─" * 41)
        print(f"│ Pitch:         {data.get('pitch', 0):+4d}°")
        print(f"│ Roll:          {data.get('roll', 0):+4d}°")
        print(f"│ Yaw:           {data.get('yaw', 0):+4d}°")
        print()

        # Velocity
        print("┌─ VELOCITY " + "─" * 47)
        print(f"│ X-axis:        {data.get('speed_x', 0):+4d} dm/s")
        print(f"│ Y-axis:        {data.get('speed_y', 0):+4d} dm/s")
        print(f"│ Z-axis:        {data.get('speed_z', 0):+4d} dm/s")
        print()

        # Acceleration
        print("┌─ ACCELERATION " + "─" * 43)
        print(f"│ X-axis:        {data.get('accel_x', 0):+7.2f} cm/s²")
        print(f"│ Y-axis:        {data.get('accel_y', 0):+7.2f} cm/s²")
        print(f"│ Z-axis:        {data.get('accel_z', 0):+7.2f} cm/s²")
        print()

        print("=" * 60)
        print("Press Ctrl+C to exit")
        print()

    def monitor(self, duration: Optional[float] = None) -> None:
        """
        Start continuous monitoring of diagnostics.

        Args:
            duration: Monitoring duration in seconds (None for infinite)
        """
        if not self.connected:
            print("Error: Not connected to Tello")
            return

        print("Starting diagnostic monitoring...")
        print(f"Update interval: {self.update_interval}s")
        if duration:
            print(f"Duration: {duration}s")
        print()

        start_time = time.monotonic()

        try:
            while True:
                # Check duration limit
                if duration:
                    elapsed = time.monotonic() - start_time
                    if elapsed >= duration:
                        print("\nMonitoring duration reached.")
                        break

                # Get and display diagnostics
                data = self.get_diagnostics()
                if data:
                    self.display_diagnostics(data)

                time.sleep(self.update_interval)

        except KeyboardInterrupt:
            print("\n\nMonitoring stopped by user.")

    def disconnect(self) -> None:
        """Safely disconnect from Tello."""
        if self.tello is not None:
            try:
                self.tello.end()
                print("Disconnected from Tello.")
            except Exception as e:
                print(f"Error during disconnect: {e}")
            finally:
                self.connected = False


def main() -> int:
    """Main entry point for the diagnostic tool."""
    print("=" * 60)
    print("DJI TELLO DIAGNOSTICS TOOL")
    print("=" * 60)
    print()
    print("Prerequisites:")
    print("1. Turn on your Tello drone")
    print("2. Connect your computer to Tello's Wi-Fi (TELLO-XXXXXX)")
    print()

    input("Press Enter when ready to connect...")
    print()

    diagnostics = TelloDiagnostics(update_interval=0.5)

    # Connect to Tello
    if not diagnostics.connect():
        print("\nFailed to connect. Please check:")
        print("- Tello is powered on")
        print("- Computer is connected to Tello Wi-Fi")
        print("- No other applications are using the Tello")
        return 1

    print()
    time.sleep(1)

    # Start monitoring
    try:
        diagnostics.monitor()
    finally:
        diagnostics.disconnect()

    return 0


if __name__ == "__main__":
    sys.exit(main())
