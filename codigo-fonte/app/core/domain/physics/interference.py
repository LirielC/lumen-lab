

import numpy as np
from numpy.typing import NDArray
from app.core.domain.errors import InvalidPhysicalParameterError
from app.core.domain.models.interference import (
    InterferenceParameters,
    InterferenceResult,
)
from app.core.domain.validation.validators import validate_interference_parameters

MIN_GRID_SAMPLES = 2001
SAMPLES_PER_SHORTEST_PERIOD = 16
MIN_OBSERVATION_ANGLE_RAD = -np.pi / 2  # -90 deg
MAX_OBSERVATION_ANGLE_RAD = np.pi / 2   # +90 deg


def generate_angular_grid(
    params: InterferenceParameters,
    min_theta_rad: float = MIN_OBSERVATION_ANGLE_RAD,
    max_theta_rad: float = MAX_OBSERVATION_ANGLE_RAD,
) -> NDArray[np.float64]:
    








    validate_interference_parameters(params)
    if not (
        np.isfinite(min_theta_rad) and np.isfinite(max_theta_rad)
        and MIN_OBSERVATION_ANGLE_RAD <= min_theta_rad < max_theta_rad <= MAX_OBSERVATION_ANGLE_RAD
    ):
        raise InvalidPhysicalParameterError(
            "Limites angulares devem ser finitos, crescentes e estar entre -90° e +90°.",
            parameter_name="observation_angles",
        )
    alpha = params.incidence_angle_rad
    q_min = float(np.sin(min_theta_rad) - np.sin(alpha))
    q_max = float(np.sin(max_theta_rad) - np.sin(alpha))
    if q_max <= q_min:
        raise InvalidPhysicalParameterError(
            "Intervalo angular pequeno demais para a precisão numérica disponível.",
            parameter_name="observation_angles",
        )
    char_length = (
        params.slit_separation_m
        if params.slit_count == 2 and params.slit_separation_m is not None
        else params.slit_width_m
    )
    max_dq = params.wavelength_m / (SAMPLES_PER_SHORTEST_PERIOD * char_length)
    max_dq = min(max_dq, (q_max - q_min) / (MIN_GRID_SAMPLES - 1))

    
    
    first_index = int(np.ceil(q_min / max_dq))
    last_index = int(np.floor(q_max / max_dq))
    q_grid = np.arange(first_index, last_index + 1, dtype=np.float64) * max_dq
    if q_grid.size == 0 or q_grid[0] > q_min:
        q_grid = np.insert(q_grid, 0, q_min)
    if q_grid[-1] < q_max:
        q_grid = np.append(q_grid, q_max)

    return np.arcsin(np.clip(q_grid + np.sin(alpha), -1.0, 1.0))


def compute_slit_point_factors(
    theta_rad: float,
    params: InterferenceParameters,
) -> tuple[float, float, float | None, float, float, float]:
    
    if not np.isfinite(theta_rad) or not MIN_OBSERVATION_ANGLE_RAD <= theta_rad <= MAX_OBSERVATION_ANGLE_RAD:
        raise InvalidPhysicalParameterError(
            "Ângulo observado deve ser finito e estar entre -90° e +90°.",
            parameter_name="selected_angle_rad",
        )

    q = float(np.sin(theta_rad) - np.sin(params.incidence_angle_rad))
    beta = float(np.pi * params.slit_width_m * q / params.wavelength_m)
    envelope = float(np.sinc(beta / np.pi) ** 2)
    delta = None
    interference = 1.0
    if params.slit_count == 2:
        assert params.slit_separation_m is not None
        delta = float(np.pi * params.slit_separation_m * q / params.wavelength_m)
        interference = float(np.cos(delta) ** 2)
    normalized = float(np.clip(envelope * interference, 0.0, 1.0))
    return q, beta, delta, envelope, interference, normalized


def compute_slit_intensity_scalar(
    theta_rad: float,
    params: InterferenceParameters,
) -> tuple[float, float]:
    











    *_, normalized_intensity = compute_slit_point_factors(theta_rad, params)
    absolute_intensity = params.initial_intensity * normalized_intensity

    return absolute_intensity, normalized_intensity


def compute_slit_interference(
    params: InterferenceParameters,
    selected_angle_rad: float = 0.0,
    observation_angles: NDArray[np.float64] | None = None,
    min_theta_rad: float = MIN_OBSERVATION_ANGLE_RAD,
    max_theta_rad: float = MAX_OBSERVATION_ANGLE_RAD,
) -> InterferenceResult:
    












    validate_interference_parameters(params)

    if observation_angles is None:
        observation_angles = generate_angular_grid(params, min_theta_rad, max_theta_rad)
    observation_angles = np.asarray(observation_angles, dtype=np.float64)
    if (
        observation_angles.ndim != 1 or observation_angles.size == 0
        or not np.all(np.isfinite(observation_angles))
        or np.any(observation_angles < MIN_OBSERVATION_ANGLE_RAD)
        or np.any(observation_angles > MAX_OBSERVATION_ANGLE_RAD)
        or np.any(np.diff(observation_angles) <= 0)
    ):
        raise InvalidPhysicalParameterError(
            "Grade angular deve ser unidimensional, não vazia, finita, estritamente crescente "
            "e estar entre -90° e +90°.",
            parameter_name="observation_angles",
        )

    q = np.sin(observation_angles) - np.sin(params.incidence_angle_rad)

    
    envelope = np.sinc((params.slit_width_m * q) / params.wavelength_m) ** 2

    if params.slit_count == 1:
        normalized = envelope
    else:
        assert params.slit_separation_m is not None
        delta = (np.pi * params.slit_separation_m * q) / params.wavelength_m
        interference = np.cos(delta) ** 2
        normalized = envelope * interference

    
    normalized = np.clip(normalized, 0.0, 1.0)

    
    zero_q_mask = np.abs(q) < 1e-15
    if np.any(zero_q_mask):
        normalized[zero_q_mask] = 1.0

    absolute = params.initial_intensity * normalized

    
    point = compute_slit_point_factors(selected_angle_rad, params)
    selected_abs = params.initial_intensity * point[-1]

    return InterferenceResult(
        observation_angles_rad=observation_angles,
        normalized_intensity=normalized,
        scaled_relative_intensity=absolute,
        selected_angle_rad=selected_angle_rad,
        selected_intensity=selected_abs,
        selected_normalized_intensity=point[-1],
        selected_q=point[0],
        selected_beta_rad=point[1],
        selected_delta_rad=point[2],
        selected_envelope=point[3],
        selected_interference_factor=point[4],
    )
