# DJI Tello Diagnostics Tool

[![CI](https://github.com/strikerdlm/tello-diagnostics/workflows/CI/badge.svg)](https://github.com/strikerdlm/tello-diagnostics/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Type Checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](http://mypy-lang.org/)
[![Security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)

A comprehensive, production-ready toolkit for connecting to DJI Tello drones and retrieving diagnostic data via Wi-Fi UDP protocol. Built with strict type safety, comprehensive testing, and Docker support.

## ✨ Features

- **Real-time Telemetry Monitoring** - Live display of all drone sensors and status
- **Data Logging** - CSV export for analysis and research
- **Interactive Command Interface** - Manual control and testing
- **Type-Safe** - Full type hints with strict mypy checking
- **Well-Tested** - Comprehensive test suite with pytest
- **Docker Support** - Fully containerized for easy deployment
- **Cross-Platform** - Works on Windows, Linux, and macOS
- **Zero-Warning Code** - Passes Ruff, MyPy, Black, isort, and Bandit with strict settings

## 📋 Requirements

- Python 3.8 or higher
- DJI Tello or Tello EDU drone
- Computer with Wi-Fi capability
- (Optional) Docker for containerized deployment

## 🚀 Quick Start

### Installation

#### Using pip (recommended)

```bash
pip install tello-diagnostics
```

#### From source

```bash
git clone https://github.com/strikerdlm/tello-diagnostics.git
cd tello-diagnostics
pip install -e ".[dev]"
```

#### Using Docker

```bash
docker-compose up tello-diagnostics
```

### Basic Usage

1. **Turn on your Tello drone**
2. **Connect your computer to the Tello's Wi-Fi** (SSID: TELLO-XXXXXX)
3. **Run one of the tools:**

#### Real-time Diagnostic Monitor

```bash
tello-diagnostics
```

or

```bash
python -m tello_diagnostics.diagnostics
```

#### Data Logger

```bash
tello-logger --duration 60 --output flight_data.csv
```

or

```bash
python -m tello_diagnostics.logger --duration 60 --rate 0.1 --output flight_data.csv
```

**Arguments:**
- `-o, --output`: Output CSV file (default: timestamped)
- `-d, --duration`: Logging duration in seconds
- `-r, --rate`: Sample rate in seconds (default: 0.1 = 10Hz)
- `-n, --max-samples`: Maximum number of samples

#### Manual Command Interface

```bash
tello-manual
```

or

```bash
python -m tello_diagnostics.manual
```

**Available Commands:**
- **Control:** `takeoff`, `land`, `up`, `down`, `left`, `right`, `forward`, `back`, `cw`, `ccw`, `flip`, `emergency`
- **Read:** `battery`, `speed`, `time`, `temp`, `height`, `tof`, `baro`, `attitude`, `acceleration`, `state`
- **System:** `help`, `status`, `exit`

## 📊 Available Telemetry Data

### Power & Status
- Battery percentage (0-100%)
- Temperature (min/max/average in °C)
- Flight time (seconds)

### Position & Altitude
- Height above takeoff (cm)
- Barometer pressure (cm)
- Time-of-Flight distance sensor (cm)

### Attitude (IMU)
- Pitch (degrees)
- Roll (degrees)
- Yaw (degrees)

### Motion
- Velocity (x, y, z axes in dm/s)
- Acceleration (x, y, z axes in cm/s²)

### Additional
- Wi-Fi signal strength
- SDK version
- Serial number

## 🏗️ Architecture

The Tello communicates via Wi-Fi UDP on three ports:

- **Port 8889**: Command/response channel
- **Port 8890**: State/telemetry broadcast (10-20Hz)
- **Port 11111**: Video stream (optional, not implemented)

The drone creates its own Wi-Fi access point that your computer connects to. **No physical serial port is required or available.**

## 🐳 Docker Usage

### Build and Run

```bash
# Build the image
docker-compose build

# Run diagnostic monitor
docker-compose up tello-diagnostics

# Run data logger
docker-compose up tello-logger

# Run manual interface
docker-compose up tello-manual
```

### Custom Configuration

Edit `docker-compose.yml` to customize command arguments:

```yaml
command: python -m tello_diagnostics.logger --output /app/data/my_log.csv --duration 120
```

Logs are saved to the `./data` directory on your host machine.

## 🧪 Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/strikerdlm/tello-diagnostics.git
cd tello-diagnostics

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install with development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov

# Run specific test file
pytest tests/test_diagnostics.py

# Run with verbose output
pytest -v
```

### Code Quality Checks

```bash
# Run all checks
ruff check src/ tests/
black --check src/ tests/
isort --check-only src/ tests/
mypy src/
bandit -r src/ -c pyproject.toml

# Auto-fix formatting
black src/ tests/
isort src/ tests/
ruff check --fix src/ tests/
```

### Pre-commit Hooks

Pre-commit hooks run automatically before each commit:

```bash
# Run manually
pre-commit run --all-files
```

## 📚 Documentation

- [Project Summary](Docs/PROJECT_SUMMARY.md) - Detailed project overview
- [Manual](Docs/Manual.md) - Complete feature documentation
- [Changelog](CHANGELOG.md) - Version history
- [Contributing](CONTRIBUTING.md) - Contribution guidelines

## 🔒 Security

This project follows strict security practices:

- ✅ No `eval()` or `exec()`
- ✅ No untrusted pickle/marshal
- ✅ Input validation on all user inputs
- ✅ Bounded loops and timeouts
- ✅ No recursion or dynamic code execution
- ✅ Bandit security scanning in CI/CD
- ✅ Dependency vulnerability scanning

Report security issues to: dlmalpica@me.com

## ⚠️ Safety Notes

- Always fly in a safe, open area
- Monitor battery levels
- The drone will auto-land if no commands received for 15 seconds
- Keep firmware updated via official Tello app
- Follow local drone regulations

## 🔗 References

- [Tello SDK 1.3 Documentation](https://dl-cdn.ryzerobotics.com/downloads/tello/20180910/Tello%20SDK%20Documentation%20EN_1.3.pdf)
- [Tello SDK 2.0 User Guide](https://dl-cdn.ryzerobotics.com/downloads/Tello/Tello%20SDK%202.0%20User%20Guide.pdf)
- [DJITelloPy Library](https://djitellopy.readthedocs.io/)

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting pull requests.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and quality checks
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Daniel L. Malpica** ([@strikerdlm](https://github.com/strikerdlm))

- Email: dlmalpica@me.com
- GitHub: [@strikerdlm](https://github.com/strikerdlm)

## ⭐ Support

If you find this project helpful, please consider giving it a star on GitHub!

## 🙏 Acknowledgments

- DJI for the Tello SDK
- [djitellopy](https://github.com/damiafuentes/DJITelloPy) library maintainers
- The Python community for excellent tooling

---

**Note:** This toolkit is for diagnostic and educational purposes. Always follow local regulations when operating drones.
