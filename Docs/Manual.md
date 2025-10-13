# Tello Diagnostics - Complete Manual

This manual provides comprehensive documentation for all features and usage patterns of the Tello Diagnostics toolkit.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Diagnostic Monitor](#diagnostic-monitor)
3. [Data Logger](#data-logger)
4. [Manual Command Interface](#manual-command-interface)
5. [Python API](#python-api)
6. [Docker Deployment](#docker-deployment)
7. [Troubleshooting](#troubleshooting)
8. [Advanced Usage](#advanced-usage)

---

## Getting Started

### Prerequisites

- DJI Tello or Tello EDU drone
- Computer with Wi-Fi capability
- Python 3.8+ or Docker

### Connection Process

1. **Power on the Tello** - Press the power button and wait for the LED to blink yellow
2. **Connect to Tello Wi-Fi** - Look for network "TELLO-XXXXXX" and connect
3. **Verify connection** - The LED should turn green when connected
4. **Run diagnostic tool** - Choose one of the three available tools

### Communication Protocol

The Tello uses UDP protocol on three ports:

- **8889**: Command channel (bidirectional)
- **8890**: State broadcast (receive only, 10-20Hz)
- **11111**: Video stream (not used by this toolkit)

---

## Diagnostic Monitor

### Overview

The diagnostic monitor provides real-time visualization of all Tello sensors and status information.

### Usage

```bash
# Using installed package
tello-diagnostics

# Using Python module
python -m tello_diagnostics.diagnostics

# With custom update interval
tello-diagnostics --interval 1.0
```

### Display Layout

The monitor shows:

```
┌─ POWER & STATUS ────────────────────────────────
│ Battery:       85% [█████████████████░░░]
│ Temperature:   50.0°C  (Range: 48°C - 52°C)
│ Flight Time:   0s

┌─ POSITION & ALTITUDE ───────────────────────────
│ Height:        0 cm
│ Barometer:     100 cm
│ TOF Distance:  10 cm

┌─ ATTITUDE (IMU) ────────────────────────────────
│ Pitch:         +0°
│ Roll:          +0°
│ Yaw:           +0°

┌─ VELOCITY ──────────────────────────────────────
│ X-axis:        +0 dm/s
│ Y-axis:        +0 dm/s
│ Z-axis:        +0 dm/s

┌─ ACCELERATION ──────────────────────────────────
│ X-axis:        +0.00 cm/s²
│ Y-axis:        +0.00 cm/s²
│ Z-axis:        +0.00 cm/s²
```

### Controls

- **Ctrl+C** - Exit the monitor

### Options

- `--interval` - Update interval in seconds (0.1 - 5.0, default: 0.5)
- `--duration` - Run for specific duration in seconds

---

## Data Logger

### Overview

The data logger records telemetry data to CSV files for offline analysis.

### Usage

```bash
# Basic usage
tello-logger --output flight_data.csv

# With duration limit
tello-logger --duration 60 --output flight_data.csv

# With custom sample rate (5Hz)
tello-logger --rate 0.2 --output flight_data.csv

# With sample count limit
tello-logger --max-samples 1000 --output flight_data.csv
```

### Arguments

| Argument | Short | Type | Default | Description |
|----------|-------|------|---------|-------------|
| `--output` | `-o` | string | timestamped | Output CSV file path |
| `--duration` | `-d` | float | unlimited | Logging duration (seconds) |
| `--rate` | `-r` | float | 0.1 | Sample rate (seconds) |
| `--max-samples` | `-n` | int | unlimited | Maximum samples to collect |

### CSV Format

The output CSV includes the following columns:

| Column | Unit | Description |
|--------|------|-------------|
| `timestamp` | ISO 8601 | Wall clock time |
| `elapsed_time` | seconds | Time since logging started |
| `battery` | % | Battery percentage (0-100) |
| `temperature` | °C | Average temperature |
| `temp_low` | °C | Lowest temperature |
| `temp_high` | °C | Highest temperature |
| `flight_time` | seconds | Total flight time |
| `height` | cm | Height above takeoff point |
| `barometer` | cm | Barometric altitude |
| `tof_distance` | cm | Time-of-flight sensor distance |
| `pitch` | degrees | Pitch angle |
| `roll` | degrees | Roll angle |
| `yaw` | degrees | Yaw angle |
| `speed_x` | dm/s | Velocity on X axis |
| `speed_y` | dm/s | Velocity on Y axis |
| `speed_z` | dm/s | Velocity on Z axis |
| `accel_x` | cm/s² | Acceleration on X axis |
| `accel_y` | cm/s² | Acceleration on Y axis |
| `accel_z` | cm/s² | Acceleration on Z axis |

### Example Analysis

```python
import pandas as pd
import matplotlib.pyplot as plt

# Load data
df = pd.read_csv('flight_data.csv')

# Plot battery over time
plt.figure(figsize=(10, 6))
plt.plot(df['elapsed_time'], df['battery'])
plt.xlabel('Time (s)')
plt.ylabel('Battery (%)')
plt.title('Battery Discharge During Flight')
plt.grid(True)
plt.show()
```

---

## Manual Command Interface

### Overview

Interactive command-line interface for manual drone control and testing.

### Usage

```bash
# Start interface
tello-manual

# After connecting, you'll see:
tello>
```

### Control Commands

| Command | Arguments | Range | Description |
|---------|-----------|-------|-------------|
| `takeoff` | - | - | Auto takeoff |
| `land` | - | - | Auto landing |
| `up` | distance | 20-500 cm | Move upward |
| `down` | distance | 20-500 cm | Move downward |
| `left` | distance | 20-500 cm | Move left |
| `right` | distance | 20-500 cm | Move right |
| `forward` | distance | 20-500 cm | Move forward |
| `back` | distance | 20-500 cm | Move backward |
| `cw` | degrees | 1-360° | Rotate clockwise |
| `ccw` | degrees | 1-360° | Rotate counter-clockwise |
| `flip` | direction | l/r/f/b | Flip (left/right/forward/back) |
| `emergency` | - | - | Emergency stop (motors off) |

### Read Commands

| Command | Description | Output |
|---------|-------------|--------|
| `battery` | Battery percentage | `Battery: 85%` |
| `speed` | Current speed | `Speed: 10 cm/s` |
| `time` | Flight time | `Flight time: 45s` |
| `temp` | Temperature | `Temperature: 50.0°C (Range: 48-52°C)` |
| `height` | Current height | `Height: 100 cm` |
| `tof` | TOF distance | `TOF Distance: 10 cm` |
| `baro` | Barometer | `Barometer: 105 cm` |
| `attitude` | Pitch/roll/yaw | `Attitude - Pitch: 0°, Roll: 0°, Yaw: 0°` |
| `acceleration` | X/Y/Z accel | `Acceleration - X: 0.00, Y: 0.00, Z: 0.00 cm/s²` |
| `state` | All state data | Full state dictionary |

### System Commands

| Command | Description |
|---------|-------------|
| `help` | Show help text |
| `status` | Show current status |
| `exit` | Exit program (auto-lands if flying) |
| `quit` | Same as exit |

### Example Session

```
tello> takeoff
Taking off...
✓ Takeoff complete

tello> battery
Battery: 85%

tello> up 50
Moving up 50 cm...
✓ Move complete

tello> attitude
Attitude - Pitch: 0°, Roll: 0°, Yaw: 0°

tello> land
Landing...
✓ Landed

tello> exit
Landing before disconnect...
Disconnected from Tello.
```

---

## Python API

### Using as a Library

You can import and use the toolkit in your own Python scripts.

#### Diagnostic Monitor

```python
from tello_diagnostics import TelloDiagnostics

# Create diagnostics instance
diag = TelloDiagnostics(update_interval=0.5)

# Connect to Tello
if diag.connect():
    # Get diagnostic data
    data = diag.get_diagnostics()
    print(f"Battery: {data['battery']}%")
    print(f"Height: {data['height']} cm")

    # Start monitoring (runs until Ctrl+C)
    diag.monitor(duration=30)  # Monitor for 30 seconds

    # Disconnect
    diag.disconnect()
```

#### Data Logger

```python
from pathlib import Path
from tello_diagnostics import TelloDataLogger

# Create logger
logger = TelloDataLogger(
    output_file=Path("my_flight.csv"),
    sample_rate=0.1,  # 10Hz
    max_samples=1000
)

# Connect and log
if logger.connect():
    sample_count = logger.log_data(duration=60)
    print(f"Logged {sample_count} samples")
    logger.disconnect()
```

#### Manual Interface

```python
from tello_diagnostics import TelloManualInterface

# Create interface
interface = TelloManualInterface()

# Connect
if interface.connect():
    # Execute commands
    interface.execute_command("takeoff")
    interface.execute_command("up 50")
    interface.execute_command("battery")
    interface.execute_command("land")

    # Disconnect
    interface.disconnect()
```

---

## Docker Deployment

### Building the Image

```bash
# Build with Docker Compose
docker-compose build

# Build manually
docker build -t tello-diagnostics:latest .
```

### Running Containers

```bash
# Diagnostic monitor
docker-compose up tello-diagnostics

# Data logger (saves to ./data directory)
docker-compose up tello-logger

# Manual interface (interactive)
docker-compose up tello-manual
```

### Custom Commands

Edit `docker-compose.yml`:

```yaml
services:
  custom-logger:
    image: tello-diagnostics:latest
    network_mode: host
    volumes:
      - ./data:/app/data:rw
    command: python -m tello_diagnostics.logger --output /app/data/custom.csv --duration 300 --rate 0.05
```

---

## Troubleshooting

### Connection Issues

**Problem:** Cannot connect to Tello

**Solutions:**
1. Verify Tello is powered on (LED blinking or solid)
2. Ensure computer is connected to Tello Wi-Fi network
3. Check no other application is using the Tello
4. Try power cycling the drone
5. Move closer to the drone (< 5 meters)

### Timeout Errors

**Problem:** Connection times out

**Solutions:**
1. Increase connection timeout in code
2. Check firewall settings (allow UDP ports 8889, 8890)
3. Disable VPN or proxy
4. Try different Wi-Fi adapter

### Missing Data

**Problem:** Some telemetry values are zero or missing

**Solutions:**
1. Wait 2-3 seconds after connection
2. Send `command` first to initialize SDK
3. Check drone firmware is up to date

### High CPU Usage

**Problem:** Diagnostic monitor uses high CPU

**Solutions:**
1. Increase update interval (`--interval 1.0`)
2. Reduce sample rate for logger
3. Close other applications

---

## Advanced Usage

### Custom Update Rates

```python
# Very fast monitoring (5Hz display)
diag = TelloDiagnostics(update_interval=0.2)

# Slow monitoring (0.5Hz display)
diag = TelloDiagnostics(update_interval=2.0)
```

### Filtering Logged Data

```python
# Only log when flying
if logger.tello.get_height() > 10:
    sample = logger.collect_sample()
    logger.append_to_csv(sample)
```

### Batch Commands

```python
interface = TelloManualInterface()
if interface.connect():
    commands = ["takeoff", "up 50", "cw 90", "forward 100", "land"]
    for cmd in commands:
        interface.execute_command(cmd)
    interface.disconnect()
```

### Real-time Plotting

```python
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

fig, ax = plt.subplots()
x_data, y_data = [], []

def update(frame):
    data = diag.get_diagnostics()
    x_data.append(frame)
    y_data.append(data['battery'])
    ax.clear()
    ax.plot(x_data, y_data)

ani = FuncAnimation(fig, update, interval=500)
plt.show()
```

---

## Research Applications

### Flight Performance Analysis

Log full flight data and analyze:
- Battery discharge curves
- Temperature vs flight time
- Acceleration during maneuvers
- Altitude control accuracy

### Sensor Calibration

Compare Tello sensors with ground truth:
- Barometer vs actual height
- TOF sensor accuracy
- IMU drift over time

### Educational Projects

- Learn UDP networking
- Understand PID control
- Analyze sensor fusion
- Study drone physics

---

## Safety Guidelines

⚠️ **Always follow these safety guidelines:**

1. Fly in open areas away from people
2. Monitor battery levels (land at 20%)
3. Keep visual line of sight
4. Obey local drone regulations
5. Do not fly in adverse weather
6. Have emergency stop ready
7. Test in safe environment first

---

## Support

- **Issues:** https://github.com/strikerdlm/tello-diagnostics/issues
- **Email:** dlmalpica@me.com
- **Documentation:** See [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

---

**Last Updated:** October 2025

