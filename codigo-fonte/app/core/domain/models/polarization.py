

from dataclasses import dataclass


@dataclass(frozen=True)
class PolarizationParameters:
    

    polarizer_count: int
    wavelength_m: float
    initial_intensity: float
    initially_polarized: bool
    initial_angle_rad: float | None
    polarizer_angles_rad: tuple[float, ...]


@dataclass(frozen=True)
class PolarizerStage:
    

    index: int
    axis_angle_rad: float
    input_intensity: float
    output_intensity: float
    stage_transmission: float
    cumulative_transmission: float
    relative_field_amplitude: float
    field_direction_rad: float | None


@dataclass(frozen=True)
class PolarizationResult:
    

    initial_intensity: float
    initially_polarized: bool
    initial_angle_rad: float | None
    stages: tuple[PolarizerStage, ...]
    final_intensity: float
    final_transmission: float
    final_field_amplitude: float
    final_field_direction_rad: float | None
