

from dataclasses import dataclass


@dataclass(frozen=True)
class InterferenceRequest:
    

    slit_count: int
    wavelength_nm: float
    slit_width_um: float
    slit_separation_um: float | None
    incidence_angle_deg: float
    observation_angle_deg: float = 0.0
    initial_intensity: float = 1.0


@dataclass(frozen=True)
class PolarizationRequest:
    

    polarizer_count: int
    wavelength_nm: float
    initial_intensity: float
    initially_polarized: bool
    initial_angle_deg: float | None
    polarizer_angles_deg: tuple[float, ...]
