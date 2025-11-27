"""
DJI Tello Diagnostics Tool

A comprehensive toolkit for monitoring and logging diagnostic data from DJI Tello drones.
"""

__version__ = "1.0.0"
__author__ = "Diego L. Malpica"
__email__ = "dlmalpica@me.com"
__license__ = "MIT"

from .diagnostics import TelloDiagnostics
from .flight_programs import (
    FlightProgram,
    FlightProgramLibrary,
    FlightProgramRunner,
    FlightStep,
    ProgramSummary,
    ProgramUploadError,
)
from .logger import TelloDataLogger
from .manual import TelloManualInterface

__all__ = [
    "TelloDiagnostics",
    "TelloDataLogger",
    "TelloManualInterface",
    "FlightStep",
    "FlightProgram",
    "FlightProgramLibrary",
    "FlightProgramRunner",
    "ProgramSummary",
    "ProgramUploadError",
]

