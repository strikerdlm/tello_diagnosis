# DJI Tello Diagnostics Project Summary

## Overview

This project provides a complete toolkit for connecting to DJI Tello drones via Wi-Fi UDP protocol and retrieving comprehensive diagnostic data. **Important: The Tello does NOT have a physical serial port** - all communication happens wirelessly over Wi-Fi UDP.

## Key Findings

### Communication Architecture

The DJI Tello uses **Wi-Fi UDP protocol** for all communication:

- **Port 8889**: Command/response channel
- **Port 8890**: Real-time state/telemetry broadcast (10-20Hz)
- **Port 11111**: Video stream (optional)

The drone creates its own Wi-Fi access point (SSID: TELLO-XXXXXX) that your computer connects to.

### No Physical Serial Port

Unlike some drones, the Tello does **not** expose a physical serial port for diagnostic access. The Tello Talent/RMTT expansion board has GPIO pins with UART capability, but these are for external modules, not for diagnostic data retrieval.

### Available Diagnostic Data

The Tello broadcasts extensive telemetry data at 10-20Hz including:

**Power & Status:**
- Battery percentage (0-100%)
- Temperature (min/max/average in °C)
- Flight time (seconds)

**Position & Altitude:**
- Height above takeoff (cm)
- Barometer pressure (cm)
- Time-of-Flight distance sensor (cm)

**Attitude (IMU):**
- Pitch (degrees)
- Roll (degrees)
- Yaw (degrees)

**Motion:**
- Velocity (x, y, z axes in dm/s)
- Acceleration (x, y, z axes in cm/s²)

**Additional:**
- Wi-Fi signal strength
- SDK version
- Serial number

## Project Structure

```
tello_diagnostics/
├── README.md                  # User documentation
├── CHANGELOG.md              # Version history
├── PROJECT_SUMMARY.md        # This file
├── requirements.txt          # Python dependencies
├── install.bat              # Windows installation script
├── tello_diagnostics.py     # Real-time monitor
├── tello_logger.py          # Data logger (CSV)
└── tello_manual.py          # Interactive CLI
```

## Tools Provided

### 1. Real-Time Diagnostic Monitor (`tello_diagnostics.py`)

Displays live telemetry data with formatted output:
- Visual battery indicator
- Real-time attitude data
- Sensor readings
- Update rate: 2Hz (configurable)

**Usage:**
```bash
python tello_diagnostics.py
```

### 2. Data Logger (`tello_logger.py`)

Logs diagnostic data to CSV for analysis:
- Configurable sample rate (default 10Hz)
- Duration or sample count limits
- Timestamped data
- Progress indicators

**Usage:**
```bash
python tello_logger.py --duration 60 --rate 0.1 --output flight_data.csv
```

**Arguments:**
- `-o, --output`: Output CSV file (default: timestamped)
- `-d, --duration`: Logging duration in seconds
- `-r, --rate`: Sample rate in seconds (default: 0.1 = 10Hz)
- `-n, --max-samples`: Maximum number of samples

### 3. Manual Command Interface (`tello_manual.py`)

Interactive command-line interface for:
- Sending control commands
- Reading sensor data
- Testing SDK functionality
- Learning the API

**Usage:**
```bash
python tello_manual.py
```

**Available Commands:**
- Control: `takeoff`, `land`, `up`, `down`, `left`, `right`, `forward`, `back`, `cw`, `ccw`, `flip`
- Read: `battery`, `speed`, `time`, `temp`, `height`, `tof`, `baro`, `attitude`, `acceleration`, `state`
- System: `help`, `status`, `exit`

## Technical Details

### Dependencies

- **djitellopy** (>=2.4.0): High-level Python interface to Tello SDK
  - Handles UDP communication
  - Parses state packets
  - Provides convenient API methods

### Connection Process

1. Turn on Tello drone
2. Connect computer to Tello Wi-Fi (SSID: TELLO-XXXXXX)
3. Application sends "command" to UDP port 8889
4. Wait for state packet on UDP port 8890
5. Connection established - telemetry flows continuously

### State Packet Format

State data arrives as semicolon-separated key:value pairs:

```
pitch:0;roll:0;yaw:0;vgx:0;vgy:0;vgz:0;templ:50;temph:52;tof:10;h:0;bat:100;baro:100.00;time:0;agx:0.00;agy:0.00;agz:0.00;
```

The library automatically parses this into a dictionary with typed values.

### Safety Features

All tools include:
- Explicit input validation with bounded ranges
- Finite timeouts on all operations
- Safe disconnection with auto-land
- Error handling with informative messages
- No unbounded loops or recursion

### Code Quality

The project follows strict Python development guidelines:
- Type hints throughout
- Explicit error handling
- No eval/exec or dynamic code execution
- Bounded loops with explicit termination
- Comprehensive docstrings
- Memory-safe operations

## Research Applications

This toolkit is suitable for:

- **Flight Performance Analysis**: Log and analyze flight characteristics
- **Sensor Calibration**: Verify IMU and sensor accuracy
- **Thermal Studies**: Monitor temperature under various flight conditions
- **Battery Discharge Profiles**: Track battery performance
- **Altitude Control Research**: Study barometer and TOF sensor behavior
- **Flight Dynamics**: Analyze acceleration and velocity data
- **Educational Purposes**: Learn drone communication protocols

## Limitations

1. **No Physical Serial Port**: Cannot access hardware-level diagnostics
2. **Wi-Fi Range**: Limited by drone's Wi-Fi range (~100m)
3. **Update Rate**: State data limited to 10-20Hz
4. **Battery Dependent**: All operations require drone power
5. **Single Connection**: Only one device can control drone at a time

## Future Enhancements

Possible additions:
- Video stream capture and analysis
- Multi-drone swarm support
- Real-time plotting of telemetry
- Mission pad (April Tag) detection
- Automated test sequences
- Data analysis utilities

## References

- [Tello SDK 1.3 Documentation](https://dl-cdn.ryzerobotics.com/downloads/tello/20180910/Tello%20SDK%20Documentation%20EN_1.3.pdf)
- [Tello SDK 2.0 User Guide](https://dl-cdn.ryzerobotics.com/downloads/Tello/Tello%20SDK%202.0%20User%20Guide.pdf)
- [DJITelloPy Library](https://djitellopy.readthedocs.io/)
- [GitHub: dji-sdk/Tello-Python](https://github.com/dji-sdk/Tello-Python)

## License

MIT License - See README.md for details

## Support

For issues or questions:
- Check the README.md for usage instructions
- Review SDK documentation for protocol details
- Ensure Tello firmware is up to date via official app
