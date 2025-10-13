"""
DJI Tello Manual Command Interface

Interactive command-line interface for sending commands to Tello
and reading diagnostic responses.
"""

import sys
from typing import Optional
from djitellopy import Tello


class TelloManualInterface:
    """Interactive command interface for Tello drone."""

    HELP_TEXT = """
Available Commands:
==================

CONTROL COMMANDS:
  takeoff          - Auto takeoff
  land             - Auto landing
  up <x>           - Move up x cm (20-500)
  down <x>         - Move down x cm (20-500)
  left <x>         - Move left x cm (20-500)
  right <x>        - Move right x cm (20-500)
  forward <x>      - Move forward x cm (20-500)
  back <x>         - Move back x cm (20-500)
  cw <x>           - Rotate clockwise x degrees (1-360)
  ccw <x>          - Rotate counter-clockwise x degrees (1-360)
  flip <d>         - Flip in direction (l/r/f/b)
  emergency        - Emergency stop (motors off)

READ COMMANDS:
  battery          - Get battery percentage
  speed            - Get current speed
  time             - Get flight time
  temp             - Get temperature
  height           - Get current height
  tof              - Get TOF distance
  baro             - Get barometer reading
  attitude         - Get pitch, roll, yaw
  acceleration     - Get acceleration x, y, z
  state            - Get all state data

SYSTEM COMMANDS:
  help             - Show this help
  status           - Show current status
  exit/quit        - Exit program

Examples:
  > up 50
  > battery
  > cw 90
"""

    def __init__(self):
        """Initialize manual interface."""
        self.tello: Optional[Tello] = None
        self.connected = False

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

            # Wait for state
            import time
            max_wait = 5.0
            elapsed = 0.0
            wait_step = 0.1

            while elapsed < max_wait:
                if self.tello.get_current_state():
                    self.connected = True
                    print(f"✓ Connected!")
                    self.show_status()
                    return True
                time.sleep(wait_step)
                elapsed += wait_step

            print("✗ Failed to receive state data")
            return False

        except Exception as e:
            print(f"✗ Connection failed: {e}")
            return False

    def show_status(self) -> None:
        """Display current Tello status."""
        if not self.connected or self.tello is None:
            print("Not connected")
            return

        try:
            battery = self.tello.get_battery()
            temp = self.tello.get_temperature()
            height = self.tello.get_height()
            flight_time = self.tello.get_flight_time()

            print("\n" + "=" * 50)
            print("TELLO STATUS")
            print("=" * 50)
            print(f"Battery:     {battery}%")
            print(f"Temperature: {temp:.1f}°C")
            print(f"Height:      {height} cm")
            print(f"Flight Time: {flight_time}s")
            print("=" * 50 + "\n")

        except Exception as e:
            print(f"Error reading status: {e}")

    def execute_command(self, cmd: str) -> bool:
        """
        Execute a command.

        Args:
            cmd: Command string

        Returns:
            bool: False if should exit, True otherwise
        """
        if not self.connected or self.tello is None:
            print("Not connected to Tello")
            return True

        cmd = cmd.strip().lower()
        if not cmd:
            return True

        parts = cmd.split()
        action = parts[0]

        try:
            # System commands
            if action in ['exit', 'quit']:
                return False

            elif action == 'help':
                print(self.HELP_TEXT)

            elif action == 'status':
                self.show_status()

            # Control commands
            elif action == 'takeoff':
                print("Taking off...")
                self.tello.takeoff()
                print("✓ Takeoff complete")

            elif action == 'land':
                print("Landing...")
                self.tello.land()
                print("✓ Landed")

            elif action == 'emergency':
                print("EMERGENCY STOP!")
                self.tello.emergency()

            elif action in ['up', 'down', 'left', 'right', 'forward', 'back']:
                if len(parts) < 2:
                    print(f"Usage: {action} <distance>")
                    return True
                distance = int(parts[1])
                if not (20 <= distance <= 500):
                    print("Distance must be between 20 and 500 cm")
                    return True

                print(f"Moving {action} {distance} cm...")
                getattr(self.tello, f"move_{action}")(distance)
                print("✓ Move complete")

            elif action in ['cw', 'ccw']:
                if len(parts) < 2:
                    print(f"Usage: {action} <degrees>")
                    return True
                degrees = int(parts[1])
                if not (1 <= degrees <= 360):
                    print("Degrees must be between 1 and 360")
                    return True

                print(f"Rotating {action} {degrees}°...")
                if action == 'cw':
                    self.tello.rotate_clockwise(degrees)
                else:
                    self.tello.rotate_counter_clockwise(degrees)
                print("✓ Rotation complete")

            elif action == 'flip':
                if len(parts) < 2:
                    print("Usage: flip <direction>  (l/r/f/b)")
                    return True
                direction = parts[1].lower()
                if direction not in ['l', 'r', 'f', 'b']:
                    print("Direction must be l (left), r (right), f (forward), or b (back)")
                    return True

                print(f"Flipping {direction}...")
                self.tello.flip(direction)
                print("✓ Flip complete")

            # Read commands
            elif action == 'battery':
                battery = self.tello.get_battery()
                print(f"Battery: {battery}%")

            elif action == 'speed':
                speed = self.tello.query_speed()
                print(f"Speed: {speed} cm/s")

            elif action == 'time':
                flight_time = self.tello.get_flight_time()
                print(f"Flight time: {flight_time}s")

            elif action == 'temp':
                temp = self.tello.get_temperature()
                temp_low = self.tello.get_lowest_temperature()
                temp_high = self.tello.get_highest_temperature()
                print(f"Temperature: {temp:.1f}°C (Range: {temp_low}-{temp_high}°C)")

            elif action == 'height':
                height = self.tello.get_height()
                print(f"Height: {height} cm")

            elif action == 'tof':
                tof = self.tello.get_distance_tof()
                print(f"TOF Distance: {tof} cm")

            elif action == 'baro':
                baro = self.tello.get_barometer()
                print(f"Barometer: {baro} cm")

            elif action == 'attitude':
                pitch = self.tello.get_pitch()
                roll = self.tello.get_roll()
                yaw = self.tello.get_yaw()
                print(f"Attitude - Pitch: {pitch}°, Roll: {roll}°, Yaw: {yaw}°")

            elif action == 'acceleration':
                accel_x = self.tello.get_acceleration_x()
                accel_y = self.tello.get_acceleration_y()
                accel_z = self.tello.get_acceleration_z()
                print(f"Acceleration - X: {accel_x:.2f}, Y: {accel_y:.2f}, Z: {accel_z:.2f} cm/s²")

            elif action == 'state':
                state = self.tello.get_current_state()
                print("\nAll State Data:")
                for key, value in sorted(state.items()):
                    print(f"  {key:15s}: {value}")
                print()

            else:
                print(f"Unknown command: {action}")
                print("Type 'help' for available commands")

        except ValueError as e:
            print(f"Invalid value: {e}")
        except Exception as e:
            print(f"Error executing command: {e}")

        return True

    def run(self) -> None:
        """Run the interactive interface."""
        print("\nTello Manual Command Interface")
        print("Type 'help' for available commands\n")

        while True:
            try:
                cmd = input("tello> ")
                if not self.execute_command(cmd):
                    break
            except KeyboardInterrupt:
                print("\n")
                break
            except EOFError:
                break

    def disconnect(self) -> None:
        """Disconnect from Tello."""
        if self.tello is not None:
            try:
                # Land if flying
                if self.tello.is_flying:
                    print("\nLanding before disconnect...")
                    self.tello.land()

                self.tello.end()
                print("Disconnected from Tello.")
            except Exception as e:
                print(f"Error during disconnect: {e}")
            finally:
                self.connected = False


def main() -> int:
    """Main entry point."""
    print("=" * 60)
    print("DJI TELLO MANUAL COMMAND INTERFACE")
    print("=" * 60)
    print()
    print("Prerequisites:")
    print("1. Turn on your Tello drone")
    print("2. Connect your computer to Tello's Wi-Fi (TELLO-XXXXXX)")
    print()

    input("Press Enter when ready to connect...")
    print()

    interface = TelloManualInterface()

    # Connect
    if not interface.connect():
        print("\nFailed to connect. Please check:")
        print("- Tello is powered on")
        print("- Computer is connected to Tello Wi-Fi")
        print("- No other applications are using the Tello")
        return 1

    # Run interface
    try:
        interface.run()
    finally:
        interface.disconnect()

    return 0


if __name__ == "__main__":
    sys.exit(main())
