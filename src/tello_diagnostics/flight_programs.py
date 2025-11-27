"""Pre-built, ready-to-run flight programs for DJI Tello drones."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable, Dict, Tuple, TypedDict, Literal

from djitellopy import Tello

CommandName = Literal[
    "takeoff",
    "land",
    "move_up",
    "move_down",
    "move_left",
    "move_right",
    "move_forward",
    "move_back",
    "rotate_clockwise",
    "rotate_counter_clockwise",
    "flip",
    "pause",
]


class ProgramSummary(TypedDict):
    """Lightweight metadata snapshot for listing programs."""

    identifier: str
    title: str
    objective: str
    recommended_space_m: float
    min_battery_percent: int
    estimated_duration_seconds: float


@dataclass(frozen=True, slots=True)
class FlightStep:
    """
    Represents a single drone action within a flight program.

    Attributes:
        command: Name of the Tello API command or "pause".
        args: Positional arguments for the command.
        wait_seconds: Minimum dwell time after completing the command.
        description: Human-readable explanation of the intention.
    """

    command: CommandName
    args: Tuple[int | str, ...] = ()
    wait_seconds: float = 0.0
    description: str = ""

    def __post_init__(self) -> None:
        """Validate constructor arguments."""
        if self.wait_seconds < 0:
            raise ValueError("wait_seconds must be non-negative")
        if self.command == "pause" and self.wait_seconds <= 0:
            raise ValueError("Pause steps must define wait_seconds > 0.")
        if self.command != "pause" and self.args and not all(
            isinstance(arg, (int, str)) for arg in self.args
        ):
            raise ValueError("Command arguments must be ints or strs.")


@dataclass(frozen=True, slots=True)
class FlightProgram:
    """
    Describes an entire flight choreograph that can run autonomously.

    Attributes:
        identifier: Stable slug used to fetch the program.
        title: Friendly name.
        objective: Summary of the behavior.
        steps: Ordered sequence of steps to execute.
        recommended_space_m: Minimum clear space (meters) to run safely.
        min_battery_percent: Minimum battery level before execution.
        estimated_duration_seconds: Approximate completion time.
    """

    identifier: str
    title: str
    objective: str
    steps: Tuple[FlightStep, ...]
    recommended_space_m: float
    min_battery_percent: int
    estimated_duration_seconds: float

    def __post_init__(self) -> None:
        """Basic validation for the immutable dataclass."""
        if not self.identifier:
            raise ValueError("identifier cannot be empty")
        if not self.steps:
            raise ValueError("FlightProgram must include at least one step.")
        if self.recommended_space_m <= 0:
            raise ValueError("recommended_space_m must be positive.")
        if not 0 < self.min_battery_percent <= 100:
            raise ValueError("min_battery_percent must be between 1 and 100.")
        if self.estimated_duration_seconds <= 0:
            raise ValueError("estimated_duration_seconds must be positive.")


class ProgramUploadError(RuntimeError):
    """Raised when a program cannot be validated or executed."""


class FlightProgramLibrary:
    """Immutable registry of curated flight programs."""

    def __init__(self) -> None:
        self._programs: Dict[str, FlightProgram] = self._build_catalog()

    def list_programs(self) -> Tuple[ProgramSummary, ...]:
        """
        Return lightweight metadata for every program.

        Returns:
            Tuple of metadata dictionaries safe for UI listing.
        """
        return tuple(
            ProgramSummary(
                identifier=program.identifier,
                title=program.title,
                objective=program.objective,
                recommended_space_m=program.recommended_space_m,
                min_battery_percent=program.min_battery_percent,
                estimated_duration_seconds=program.estimated_duration_seconds,
            )
            for program in self._programs.values()
        )

    def get_program(self, identifier: str) -> FlightProgram:
        """
        Fetch a specific program by slug.

        Args:
            identifier: Program slug (case-insensitive).

        Raises:
            ProgramUploadError: If the identifier is unknown.
        """
        key = identifier.lower()
        try:
            return self._programs[key]
        except KeyError as exc:
            raise ProgramUploadError(
                f"Unknown program '{identifier}'. Use 'programs list' to inspect options."
            ) from exc

    def _build_catalog(self) -> Dict[str, FlightProgram]:
        """Create the curated set of fun programs."""
        square_dance = FlightProgram(
            identifier="square-dance",
            title="Square Dance",
            objective="Trace a one-meter square with style and celebratory flips.",
            recommended_space_m=3.0,
            min_battery_percent=50,
            estimated_duration_seconds=55.0,
            steps=(
                FlightStep("takeoff", wait_seconds=2.0, description="Smooth takeoff"),
                FlightStep("move_forward", (80,), 1.0, "Forward leg"),
                FlightStep("move_right", (80,), 1.0, "Right leg"),
                FlightStep("move_back", (80,), 1.0, "Backwards leg"),
                FlightStep("move_left", (80,), 1.0, "Left leg to close square"),
                FlightStep("flip", ("l",), 1.5, "Left flip celebration"),
                FlightStep("flip", ("r",), 1.5, "Right flip celebration"),
                FlightStep("land", description="Autoland"),
            ),
        )

        spiral_climb = FlightProgram(
            identifier="spiral-climb",
            title="Spiral Climb",
            objective="Climb in a tightening spiral to showcase altitude control.",
            recommended_space_m=3.5,
            min_battery_percent=40,
            estimated_duration_seconds=60.0,
            steps=(
                FlightStep("takeoff", wait_seconds=2.0, description="Liftoff"),
                FlightStep("move_up", (40,), 0.8, "Initial climb"),
                FlightStep("rotate_clockwise", (45,), 0.6, "Start spiral"),
                FlightStep("move_forward", (60,), 0.8, "Forward move"),
                FlightStep("move_up", (30,), 0.8, "Gain altitude"),
                FlightStep("rotate_clockwise", (60,), 0.6, "Spiral turn"),
                FlightStep("move_right", (60,), 0.8, "Shift right"),
                FlightStep("move_forward", (60,), 0.8, "Forward progression"),
                FlightStep("move_up", (30,), 0.8, "Final climb"),
                FlightStep("rotate_clockwise", (90,), 1.0, "Panorama"),
                FlightStep("pause", wait_seconds=2.5, description="Hover showcase"),
                FlightStep("land", description="Descend safely"),
            ),
        )

        zigzag = FlightProgram(
            identifier="zigzag-dash",
            title="Zig-Zag Dash",
            objective="Agile lateral zig-zag with quick rotations.",
            recommended_space_m=4.0,
            min_battery_percent=35,
            estimated_duration_seconds=45.0,
            steps=(
                FlightStep("takeoff", wait_seconds=1.5, description="Takeoff"),
                FlightStep("move_forward", (70,), 0.7, "Forward sprint"),
                FlightStep("move_left", (60,), 0.6, "Left dodge"),
                FlightStep("rotate_counter_clockwise", (45,), 0.5, "Angle change"),
                FlightStep("move_forward", (70,), 0.7, "Forward sprint two"),
                FlightStep("move_right", (60,), 0.6, "Right dodge"),
                FlightStep("rotate_clockwise", (45,), 0.5, "Recenter"),
                FlightStep("move_back", (60,), 0.7, "Return to origin"),
                FlightStep("pause", wait_seconds=1.5, description="Hover reset"),
                FlightStep("land", description="Land"),
            ),
        )

        selfie_orbit = FlightProgram(
            identifier="selfie-orbit",
            title="Selfie Orbit",
            objective="Slow, camera-friendly orbit and bow for filming.",
            recommended_space_m=5.0,
            min_battery_percent=45,
            estimated_duration_seconds=75.0,
            steps=(
                FlightStep("takeoff", wait_seconds=2.0, description="Takeoff"),
                FlightStep("move_back", (80,), 0.8, "Create distance"),
                FlightStep("move_up", (40,), 0.6, "Rise to eye level"),
                FlightStep("pause", wait_seconds=2.0, description="Hold for framing"),
                FlightStep("rotate_counter_clockwise", (90,), 0.6, "Begin orbit"),
                FlightStep("move_right", (70,), 0.8, "Strafe while facing target"),
                FlightStep("rotate_counter_clockwise", (90,), 0.6, "Continue orbit"),
                FlightStep("move_right", (70,), 0.8, "Complete orbit"),
                FlightStep("move_forward", (60,), 0.7, "Approach for bow"),
                FlightStep("flip", ("f",), 1.5, "Forward flip finale"),
                FlightStep("land", description="Land gently"),
            ),
        )

        return {
            program.identifier: program
            for program in (
                square_dance,
                spiral_climb,
                zigzag,
                selfie_orbit,
            )
        }


class FlightProgramRunner:
    """Safely uploads and executes a flight program on a connected Tello."""

    def __init__(
        self,
        default_pause_seconds: float = 0.8,
        sleep_fn: Callable[[float], None] | None = None,
    ) -> None:
        if default_pause_seconds < 0:
            raise ValueError("default_pause_seconds must be non-negative.")
        self._default_pause_seconds = default_pause_seconds
        self._sleep = sleep_fn or time.sleep

    def execute(
        self,
        tello: Tello,
        program: FlightProgram,
        status_callback: Callable[[str], None] | None = None,
    ) -> None:
        """
        Run the provided program sequentially.

        Args:
            tello: Connected Tello instance.
            program: Pre-built flight program.
            status_callback: Optional callback for progress updates.

        Raises:
            ProgramUploadError: If a validation or runtime step fails.
        """
        notifier = status_callback or (lambda message: None)
        if not program.steps:
            raise ProgramUploadError("Program has no steps to execute.")

        battery_level = self._read_battery(tello)
        if battery_level < program.min_battery_percent:
            raise ProgramUploadError(
                "Battery level is too low "
                f"({battery_level}%). Required: {program.min_battery_percent}%."
            )

        notifier(
            f"Starting '{program.title}' (est. {program.estimated_duration_seconds:.0f}s)."
        )
        total_steps = len(program.steps)
        for index, step in enumerate(program.steps, start=1):
            descriptor = step.description or step.command
            notifier(f"[{index}/{total_steps}] {descriptor}")
            self._execute_step(tello, step, notifier)
        notifier(f"Completed '{program.title}'.")

    def _read_battery(self, tello: Tello) -> int:
        """Read and validate the current battery level."""
        try:
            battery = tello.get_battery()
        except Exception as exc:  # noqa: BLE001
            raise ProgramUploadError("Unable to read battery level.") from exc

        if not isinstance(battery, int):
            raise ProgramUploadError("Battery readings must be integer percentages.")
        if not 0 <= battery <= 100:
            raise ProgramUploadError(
                f"Battery reading '{battery}' is outside expected range 0-100."
            )
        return battery

    def _execute_step(
        self,
        tello: Tello,
        step: FlightStep,
        notifier: Callable[[str], None],
    ) -> None:
        """Execute an individual step and enforce a safe pause."""
        if step.command == "pause":
            self._sleep(step.wait_seconds)
            return

        try:
            command = getattr(tello, step.command)
        except AttributeError as exc:
            raise ProgramUploadError(
                f"Tello API does not implement '{step.command}'."
            ) from exc

        try:
            command(*step.args)
        except Exception as exc:  # noqa: BLE001
            raise ProgramUploadError(
                f"Command '{step.command}' with args {step.args} failed."
            ) from exc

        wait_time = max(step.wait_seconds, self._default_pause_seconds)
        if wait_time > 0:
            self._sleep(wait_time)

