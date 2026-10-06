

import pytest
from app.core.application.dto.requests import PolarizationRequest
from app.core.application.use_cases.simulate_polarization import (
    SimulatePolarizationUseCase,
)


def test_polarization_use_case_success() -> None:
    """Verifica execução do caso de uso de polarização com cascata de 3 polarizadores."""
    use_case = SimulatePolarizationUseCase()
    request = PolarizationRequest(
        polarizer_count=3,
        wavelength_nm=532.0,
        initial_intensity=1.0,
        initially_polarized=False,
        initial_angle_deg=None,
        polarizer_angles_deg=(0.0, 45.0, 90.0),
    )
    response = use_case.execute(request)
    assert len(response.stages) == 3
    assert pytest.approx(response.stages[0].output_intensity, rel=1e-5) == 0.5
    assert pytest.approx(response.stages[1].output_intensity, rel=1e-5) == 0.25
    assert pytest.approx(response.stages[2].output_intensity, rel=1e-5) == 0.125
    assert pytest.approx(response.final_intensity, rel=1e-5) == 0.125
    assert pytest.approx(response.final_transmission_pct, rel=1e-5) == 12.5
    assert response.beam_color_hex.startswith("#")
