# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2025-10-05

### Added
- Initial release of DJI Tello Diagnostics Tool
- Real-time diagnostic monitoring (`tello_diagnostics.py`)
  - Battery, temperature, and flight status
  - Attitude data (pitch, roll, yaw)
  - Acceleration and velocity monitoring
  - Distance sensors (TOF and barometer)
  - Formatted console display with visual indicators

- Data logger (`tello_logger.py`)
  - CSV output format
  - Configurable sample rate (default 10Hz)
  - Duration and sample count limits
  - Command-line argument support
  - Progress indicators

- Manual command interface (`tello_manual.py`)
  - Interactive command-line interface
  - Control commands (takeoff, land, movement, rotation, flips)
  - Read commands (battery, sensors, attitude, acceleration)
  - System status display
  - Built-in help system

- Documentation
  - Comprehensive README with usage examples
  - Inline code documentation
  - Safety guidelines

### Features
- Wi-Fi UDP communication (no serial port required)
- Bounded loops with explicit timeouts
- Type hints throughout codebase
- Error handling with informative messages
- Safe disconnection with auto-land feature
- Cross-platform compatibility (Windows, Linux, macOS)
