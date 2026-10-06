

import math
import numpy as np


def pixel_mean_intensities(angles, intensities, limits, columns: int):
    




    edges = np.linspace(*limits, columns + 1)
    widths = np.diff(angles)
    slopes = np.diff(intensities) / widths
    integral = np.concatenate(([0.0], np.cumsum(widths * (intensities[:-1] + intensities[1:]) / 2)))
    indices = np.clip(np.searchsorted(angles, edges, side="right") - 1, 0, len(angles) - 2)
    offsets = edges - angles[indices]
    at_edges = integral[indices] + intensities[indices] * offsets + slopes[indices] * offsets**2 / 2
    return np.clip(np.diff(at_edges) / np.diff(edges), 0.0, 1.0)


def angular_view_limits(
    *,
    mode: str,
    alpha_deg: float,
    wavelength_nm: float,
    slit_width_um: float,
) -> tuple[float, float]:
    
    if mode == "overview":
        return -90.0, 90.0
    scale_um = slit_width_um
    q_minimum = wavelength_nm * 1e-3 / scale_um
    center = math.sin(math.radians(alpha_deg))
    return tuple(
        math.degrees(math.asin(max(-1.0, min(1.0, center + sign * q_minimum))))
        for sign in (-1.0, 1.0)
    )


def angle_to_fraction(angle_deg: float, limits: tuple[float, float]) -> float:
    
    return (angle_deg - limits[0]) / (limits[1] - limits[0])


def fraction_to_angle(fraction: float, limits: tuple[float, float]) -> float:
    
    return limits[0] + fraction * (limits[1] - limits[0])
