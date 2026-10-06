

import math
import numpy as np
import pytest

from app.core.application.dto.requests import InterferenceRequest
from app.core.application.use_cases.simulate_interference import SimulateInterferenceUseCase
from app.core.domain.models.interference import InterferenceParameters
from app.core.domain.physics.interference import (
    compute_slit_interference,
    compute_slit_intensity_scalar,
)
from app.core.utils.formatting import format_didactic_number, format_ratio_percent


def test_format_didactic_number_cases():
    
    assert format_didactic_number(104.8734, precision=3) == "104,873"
    assert format_didactic_number(7.9022e-5, precision=4) == "7,9022 × 10⁻⁵"
    assert format_didactic_number(2.5287e-4, precision=4) == "2,5287 × 10⁻⁴"
    assert format_didactic_number(0.0, precision=4) == "0,0000"
    assert format_didactic_number(1.0, precision=4) == "1,0000"
    assert format_didactic_number(3.2, precision=4) == "3,2000"


def test_case_a_didactic_values():
    """CASO A:

    λ = 633 nm
    a = 25 µm
    α = -25°
    θ = +25°
    I₀ = 3,2

    
    β ≈ 104,873
    I / I₀ ≈ 7,9022 × 10⁻⁵
    I ≈ 2,5287 × 10⁻⁴
    """
    use_case = SimulateInterferenceUseCase()
    req = InterferenceRequest(
        slit_count=1,
        slit_width_um=25.0,
        slit_separation_um=None,
        wavelength_nm=633.0,
        incidence_angle_deg=-25.0,
        observation_angle_deg=25.0,
        initial_intensity=3.2,
    )
    res = use_case.execute(req)

    
    expected_beta = (math.pi * 25e-6 / 633e-9) * (
        math.sin(math.radians(25.0)) - math.sin(math.radians(-25.0))
    )
    assert math.isclose(res.beta_rad, expected_beta, rel_tol=1e-4)
    assert math.isclose(res.beta_rad, 104.873, abs_tol=0.01)

    
    expected_norm_i = (math.sin(expected_beta) / expected_beta) ** 2
    assert math.isclose(res.selected_normalized_intensity, expected_norm_i, rel_tol=1e-4)
    assert math.isclose(res.selected_normalized_intensity, 7.9022e-5, rel_tol=1e-3)

    
    expected_abs_i = 3.2 * expected_norm_i
    assert math.isclose(res.selected_intensity, expected_abs_i, rel_tol=1e-4)
    assert math.isclose(res.selected_intensity, 2.5287e-4, rel_tol=1e-3)

    
    assert "β = 104,873" in res.formula_text
    assert "7,9022 × 10⁻⁵" in res.formula_text
    assert "2,5287 × 10⁻⁴" in res.formula_text
    assert "Equação Física da Difração por Uma Fenda:" in res.formula_text
    assert "Substituição Didática dos Valores:" in res.formula_text


def test_case_b_normal_incidence_center():
    """CASO B:

    α = 0°
    θ = 0°

    
    β = 0
    I / I₀ = 1
    I = I₀
    """
    use_case = SimulateInterferenceUseCase()
    req = InterferenceRequest(
        slit_count=1,
        slit_width_um=20.0,
        slit_separation_um=None,
        wavelength_nm=550.0,
        incidence_angle_deg=0.0,
        observation_angle_deg=0.0,
        initial_intensity=2.5,
    )
    res = use_case.execute(req)

    assert math.isclose(res.beta_rad, 0.0, abs_tol=1e-9)
    assert math.isclose(res.selected_normalized_intensity, 1.0, abs_tol=1e-9)
    assert math.isclose(res.selected_intensity, 2.5, abs_tol=1e-9)
    assert "lim_{β → 0} [sin(β) / β]² = 1" in res.formula_text
    assert "1,0000" in res.formula_text


def test_case_c_oblique_incidence_peak():
    """CASO C:

    α = -25°
    θ = -25°

    
    β ≈ 0
    I / I₀ ≈ 1
    I ≈ I₀
    
    """
    use_case = SimulateInterferenceUseCase()
    req = InterferenceRequest(
        slit_count=1,
        slit_width_um=25.0,
        slit_separation_um=None,
        wavelength_nm=633.0,
        incidence_angle_deg=-25.0,
        observation_angle_deg=-25.0,
        initial_intensity=4.0,
    )
    res = use_case.execute(req)

    assert math.isclose(res.beta_rad, 0.0, abs_tol=1e-9)
    assert math.isclose(res.selected_normalized_intensity, 1.0, abs_tol=1e-9)
    assert math.isclose(res.selected_intensity, 4.0, abs_tol=1e-9)

    
    max_idx = np.argmax(res.normalized_intensity)
    peak_angle = res.angles_deg[max_idx]
    assert math.isclose(peak_angle, -25.0, abs_tol=0.2)


def test_case_d_intensity_scaling():
    """CASO D:

    
    
    
    """
    use_case = SimulateInterferenceUseCase()
    req1 = InterferenceRequest(
        slit_count=1,
        slit_width_um=30.0,
        slit_separation_um=None,
        wavelength_nm=500.0,
        incidence_angle_deg=10.0,
        observation_angle_deg=15.0,
        initial_intensity=1.0,
    )
    req2 = InterferenceRequest(
        slit_count=1,
        slit_width_um=30.0,
        slit_separation_um=None,
        wavelength_nm=500.0,
        incidence_angle_deg=10.0,
        observation_angle_deg=15.0,
        initial_intensity=5.0,
    )

    res1 = use_case.execute(req1)
    res2 = use_case.execute(req2)

    
    np.testing.assert_allclose(res1.normalized_intensity, res2.normalized_intensity, rtol=1e-12)
    assert math.isclose(res1.selected_normalized_intensity, res2.selected_normalized_intensity, rel_tol=1e-12)

    
    assert math.isclose(res2.selected_intensity, 5.0 * res1.selected_intensity, rel_tol=1e-9)


def test_special_numerical_cases_no_nan_or_zero_division():
    
    params = InterferenceParameters(
        slit_count=1,
        slit_width_m=1e-6,
        slit_separation_m=None,
        wavelength_m=700e-9,
        incidence_angle_rad=0.0,
        initial_intensity=1.0,
    )
    res = compute_slit_interference(params, selected_angle_rad=0.0)

    assert not np.any(np.isnan(res.normalized_intensity))
    assert not np.any(np.isinf(res.normalized_intensity))
    assert np.all(res.normalized_intensity >= 0.0)
    assert np.all(res.normalized_intensity <= 1.0 + 1e-9)
