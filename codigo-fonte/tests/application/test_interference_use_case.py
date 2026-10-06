

import pytest
from app.core.application.dto.requests import InterferenceRequest
from app.core.application.use_cases.simulate_interference import (
    SimulateInterferenceUseCase,
)


def test_interference_use_case_success() -> None:
    """Verifica execução do caso de uso de fendas e conversão correta de grandezas."""
    use_case = SimulateInterferenceUseCase()
    request = InterferenceRequest(
        slit_count=2,
        wavelength_nm=650.0,
        slit_width_um=15.0,
        slit_separation_um=50.0,
        incidence_angle_deg=0.0,
        observation_angle_deg=0.0,
        initial_intensity=1.0,
    )
    response = use_case.execute(request)
    assert response.slit_count == 2
    assert response.wavelength_nm == 650.0
    assert response.beam_color_hex.startswith("#")
    assert pytest.approx(response.selected_normalized_intensity, rel=1e-5) == 1.0
    assert len(response.angles_deg) >= 2001
    assert "Interferência e Difração" in response.formula_text
