

from dataclasses import dataclass
from typing import Literal
import numpy as np
from numpy.typing import NDArray


@dataclass(frozen=True)
class InterferenceParameters:
    

    slit_count: Literal[1, 2]
    wavelength_m: float
    slit_width_m: float
    slit_separation_m: float | None
    incidence_angle_rad: float
    initial_intensity: float = 1.0  


@dataclass(frozen=True)
class InterferenceResult:
    

    observation_angles_rad: NDArray[np.float64]
    normalized_intensity: NDArray[np.float64]
    scaled_relative_intensity: NDArray[np.float64]
    selected_angle_rad: float
    selected_intensity: float
    selected_normalized_intensity: float
    selected_q: float
    selected_beta_rad: float
    selected_delta_rad: float | None
    selected_envelope: float
    selected_interference_factor: float

    @property
    def absolute_intensity(self) -> NDArray[np.float64]:
        
        return self.scaled_relative_intensity
