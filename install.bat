@echo off
REM DJI Tello Diagnostics - Installation Script for Windows

echo ============================================================
echo DJI TELLO DIAGNOSTICS - INSTALLATION
echo ============================================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.6 or higher from python.org
    pause
    exit /b 1
)

echo Python found!
python --version
echo.

echo Installing dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ============================================================
echo INSTALLATION COMPLETE!
echo ============================================================
echo.
echo Available tools:
echo   python tello_diagnostics.py  - Real-time diagnostic monitor
echo   python tello_logger.py       - Data logger (CSV output)
echo   python tello_manual.py       - Manual command interface
echo.
echo Next steps:
echo 1. Turn on your Tello drone
echo 2. Connect to Tello Wi-Fi (TELLO-XXXXXX)
echo 3. Run one of the tools above
echo.
pause
