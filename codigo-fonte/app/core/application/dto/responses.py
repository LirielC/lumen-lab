

from dataclasses import dataclass
import numpy as np
from numpy.typing import NDArray


@dataclass(frozen=True)
class InterferenceResponse:
    

    angles_deg: NDArray[np.float64]
    normalized_intensity: NDArray[np.float64]
    scaled_relative_intensity: NDArray[np.float64]
    selected_angle_deg: float
    selected_intensity: float
    selected_normalized_intensity: float
    wavelength_nm: float
    beam_color_hex: str
    beam_rgb: tuple[float, float, float]
    slit_count: int
    slit_width_um: float
    slit_separation_um: float | None
    incidence_angle_deg: float
    initial_intensity: float
    formula_latex: str
    formula_text: str
    beta_rad: float = 0.0
    delta_rad: float | None = None

    @property
    def absolute_intensity(self) -> NDArray[np.float64]:
        
        return self.scaled_relative_intensity


@dataclass(frozen=True)
class StageDTO:
    

    index: int
    axis_angle_deg: float
    input_intensity: float
    output_intensity: float
    stage_transmission_pct: float
    cumulative_transmission_pct: float
    relative_field_amplitude: float
    field_direction_deg: float | None


@dataclass(frozen=True)
class PolarizationResponse:
    

    initial_intensity: float
    initially_polarized: bool
    initial_angle_deg: float | None
    wavelength_nm: float
    beam_color_hex: str
    beam_rgb: tuple[float, float, float]
    stages: tuple[StageDTO, ...]
    final_intensity: float
    final_transmission_pct: float
    final_field_amplitude: float
    final_field_direction_deg: float | None
    formula_latex: str
    formula_text: str
