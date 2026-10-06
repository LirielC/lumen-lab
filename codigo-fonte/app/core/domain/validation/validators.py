

import math
from app.core.domain.errors import (
    InvalidPhysicalParameterError,
    InvalidPolarizationStateError,
    PolarizerCountError,
    SlitSeparationGeometryError,
)
from app.core.domain.models.interference import InterferenceParameters
from app.core.domain.models.polarization import PolarizationParameters


MIN_WAVELENGTH_M = 400.0e-9
MAX_WAVELENGTH_M = 700.0e-9
EPSILON_WAVELENGTH = 1e-12


def validate_interference_parameters(params: InterferenceParameters) -> None:
    





    if params.slit_count not in (1, 2):
        raise InvalidPhysicalParameterError(
            f"Número de fendas deve ser 1 ou 2, recebido: {params.slit_count}",
            parameter_name="slit_count",
        )

    if not math.isfinite(params.wavelength_m):
        raise InvalidPhysicalParameterError(
            "Comprimento de onda deve ser um número finito.",
            parameter_name="wavelength_m",
        )

    if (
        params.wavelength_m < (MIN_WAVELENGTH_M - EPSILON_WAVELENGTH)
        or params.wavelength_m > (MAX_WAVELENGTH_M + EPSILON_WAVELENGTH)
    ):
        raise InvalidPhysicalParameterError(
            f"Comprimento de onda deve estar entre 400 e 700 nm, recebido: {params.wavelength_m * 1e9:.1f} nm",
            parameter_name="wavelength_m",
        )

    if not math.isfinite(params.slit_width_m) or params.slit_width_m <= 0:
        raise InvalidPhysicalParameterError(
            "Largura da fenda deve ser maior que zero.",
            parameter_name="slit_width_m",
        )

    if not math.isfinite(params.initial_intensity) or params.initial_intensity < 0:
        raise InvalidPhysicalParameterError(
            "Intensidade inicial deve ser maior ou igual a zero.",
            parameter_name="initial_intensity",
        )

    if not math.isfinite(params.incidence_angle_rad):
        raise InvalidPhysicalParameterError(
            "Ângulo de incidência deve ser um número finito.",
            parameter_name="incidence_angle_rad",
        )

    if params.slit_count == 2:
        if params.slit_separation_m is None or not math.isfinite(params.slit_separation_m):
            raise InvalidPhysicalParameterError(
                "Separação entre fendas é obrigatória para configuração de duas fendas.",
                parameter_name="slit_separation_m",
            )
        if params.slit_separation_m <= params.slit_width_m:
            raise SlitSeparationGeometryError(
                f"A separação entre os centros das fendas ({params.slit_separation_m * 1e6:.2f} µm) "
                f"deve ser maior que a largura da fenda ({params.slit_width_m * 1e6:.2f} µm).",
                parameter_name="slit_separation_m",
            )


def validate_polarization_parameters(params: PolarizationParameters) -> None:
    






    if params.polarizer_count not in (1, 2, 3):
        raise PolarizerCountError(
            f"Número de polarizadores deve ser 1, 2 ou 3, recebido: {params.polarizer_count}",
            parameter_name="polarizer_count",
        )

    if not math.isfinite(params.wavelength_m):
        raise InvalidPhysicalParameterError(
            "Comprimento de onda deve ser um número finito.",
            parameter_name="wavelength_m",
        )

    if (
        params.wavelength_m < (MIN_WAVELENGTH_M - EPSILON_WAVELENGTH)
        or params.wavelength_m > (MAX_WAVELENGTH_M + EPSILON_WAVELENGTH)
    ):
        raise InvalidPhysicalParameterError(
            f"Comprimento de onda deve estar entre 400 e 700 nm, recebido: {params.wavelength_m * 1e9:.1f} nm",
            parameter_name="wavelength_m",
        )

    if not math.isfinite(params.initial_intensity) or params.initial_intensity < 0:
        raise InvalidPhysicalParameterError(
            "Intensidade inicial deve ser maior ou igual a zero.",
            parameter_name="initial_intensity",
        )

    if params.initially_polarized:
        if params.initial_angle_rad is None or not math.isfinite(params.initial_angle_rad):
            raise InvalidPolarizationStateError(
                "Para luz inicialmente polarizada, o ângulo inicial de polarização deve ser informado.",
                parameter_name="initial_angle_rad",
            )

    if len(params.polarizer_angles_rad) != params.polarizer_count:
        raise InvalidPhysicalParameterError(
            f"Esperados {params.polarizer_count} ângulos de polarizadores, "
            f"recebidos {len(params.polarizer_angles_rad)}.",
            parameter_name="polarizer_angles_rad",
        )

    for i, angle in enumerate(params.polarizer_angles_rad, start=1):
        if not math.isfinite(angle):
            raise InvalidPhysicalParameterError(
                f"Ângulo do polarizador {i} deve ser um número finito.",
                parameter_name=f"polarizer_angle_{i}",
            )
