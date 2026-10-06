

from app.core.domain.physics.interference import (
    compute_slit_interference,
    compute_slit_intensity_scalar,
    generate_angular_grid,
)
from app.core.domain.physics.polarization import (
    compute_polarization,
    normalize_angle_rad,
)
from app.core.domain.physics.optics_color import (
    wavelength_to_rgb,
    wavelength_to_hex,
)

__all__ = [
    "compute_slit_interference",
    "compute_slit_intensity_scalar",
    "generate_angular_grid",
    "compute_polarization",
    "normalize_angle_rad",
    "wavelength_to_rgb",
    "wavelength_to_hex",
]
