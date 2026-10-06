

import math
import numpy as np
import pytest
from app.core.domain.errors import (
    InvalidPhysicalParameterError,
    SlitSeparationGeometryError,
)
from app.core.domain.models.interference import InterferenceParameters
from app.core.domain.physics.interference import (
    compute_slit_interference,
    compute_slit_intensity_scalar,
    generate_angular_grid,
)


@pytest.mark.parametrize("grid", [[], [0, np.nan], [0, np.inf], [0, np.pi],
                                     [-np.pi, 0], [0, 0], [.1, 0], [[0, .1]], 0])
def test_invalid_custom_grid_is_rejected(grid):
    params = InterferenceParameters(1, 500e-9, 25e-6, None, 0)
    with pytest.raises(InvalidPhysicalParameterError, match="Grade angular"):
        compute_slit_interference(params, observation_angles=np.asarray(grid))


@pytest.mark.parametrize("bounds", [(0, 0), (1, -1), (-np.pi, np.pi),
                                       (np.nan, 1), (0, np.inf),
                                       (np.nextafter(np.pi / 2, 0), np.pi / 2)])
def test_invalid_generated_grid_is_rejected(bounds):
    params = InterferenceParameters(1, 500e-9, 25e-6, None, 0)
    for calculate in (generate_angular_grid,
                      lambda p, lo, hi: compute_slit_interference(p, min_theta_rad=lo, max_theta_rad=hi)):
        with pytest.raises(InvalidPhysicalParameterError):
            calculate(params, *bounds)


def test_custom_grid_endpoints_and_single_point_are_supported():
    params = InterferenceParameters(1, 500e-9, 25e-6, None, 0)
    for grid in ([0.0], [-np.pi / 2, 0, np.pi / 2]):
        result = compute_slit_interference(params, observation_angles=np.array(grid))
        assert np.all(np.isfinite(result.normalized_intensity))
        assert result.normalized_intensity[grid.index(0)] == pytest.approx(1)


class TestInterferencePhysics:
    

    def test_criterion_01_and_02_theta_equals_alpha_is_one_and_in_grid(self) -> None:
        """1. θ = α produz I/I₀ = 1. 2. A grade angular inclui exatamente α."""
        alpha = math.radians(12.4)
        params = InterferenceParameters(
            slit_count=2,
            wavelength_m=652e-9,
            slit_width_m=32.1e-6,
            slit_separation_m=152.0e-6,
            incidence_angle_rad=alpha,
            initial_intensity=5.3,
        )

        grid = generate_angular_grid(params)
        
        assert np.any(np.isclose(grid, alpha, atol=1e-14))

        result = compute_slit_interference(params, selected_angle_rad=alpha)
        
        assert pytest.approx(result.selected_normalized_intensity, abs=1e-12) == 1.0
        assert pytest.approx(result.selected_intensity, abs=1e-12) == 5.3

        
        alpha_idx = np.where(np.isclose(result.observation_angles_rad, alpha, atol=1e-14))[0][0]
        assert pytest.approx(result.normalized_intensity[alpha_idx], abs=1e-12) == 1.0

    def test_criterion_03_normal_incidence_symmetry(self) -> None:
        """3. Incidência normal produz perfil simétrico."""
        params = InterferenceParameters(
            slit_count=1,
            wavelength_m=600e-9,
            slit_width_m=20e-6,
            slit_separation_m=None,
            incidence_angle_rad=0.0,
            initial_intensity=1.0,
        )
        theta_pos = math.radians(1.5)
        theta_neg = -theta_pos
        _, i_pos = compute_slit_intensity_scalar(theta_pos, params)
        _, i_neg = compute_slit_intensity_scalar(theta_neg, params)
        assert pytest.approx(i_pos, rel=1e-6) == i_neg

    def test_criterion_04_oblique_incidence_shifts_peak(self) -> None:
        """4. Incidência oblíqua desloca o máximo para θ = α."""
        alpha = math.radians(7.5)
        params = InterferenceParameters(
            slit_count=1,
            wavelength_m=500e-9,
            slit_width_m=20e-6,
            slit_separation_m=None,
            incidence_angle_rad=alpha,
            initial_intensity=1.0,
        )
        result = compute_slit_interference(params, selected_angle_rad=alpha)
        
        max_idx = np.argmax(result.normalized_intensity)
        theta_peak = result.observation_angles_rad[max_idx]
        assert pytest.approx(theta_peak, abs=1e-4) == alpha
        assert pytest.approx(result.normalized_intensity[max_idx], abs=1e-10) == 1.0

    def test_criterion_05_two_slits_fringes_inside_envelope(self) -> None:
        """5. Duas fendas apresentam franjas de interferência sob envelope de difração."""
        params_2slits = InterferenceParameters(
            slit_count=2,
            wavelength_m=550e-9,
            slit_width_m=10e-6,
            slit_separation_m=50e-6,
            incidence_angle_rad=0.0,
            initial_intensity=1.0,
        )
        params_1slit = InterferenceParameters(
            slit_count=1,
            wavelength_m=550e-9,
            slit_width_m=10e-6,
            slit_separation_m=None,
            incidence_angle_rad=0.0,
            initial_intensity=1.0,
        )

        r2 = compute_slit_interference(params_2slits)
        r1 = compute_slit_interference(params_1slit, observation_angles=r2.observation_angles_rad)

        
        assert np.all(r2.normalized_intensity <= r1.normalized_intensity + 1e-9)

    def test_criterion_06_resolution_resolves_0252_deg_fringes(self) -> None:
        """6. A resolução escolhida representa adequadamente uma separação de aproximadamente 0,252°."""
        params = InterferenceParameters(
            slit_count=2,
            wavelength_m=652e-9,
            slit_width_m=32.1e-6,
            slit_separation_m=152.0e-6,
            incidence_angle_rad=math.radians(12.4),
            initial_intensity=5.3,
        )
        grid = generate_angular_grid(params)
        q = np.sin(grid) - math.sin(params.incidence_angle_rad)
        center = int(np.argmin(np.abs(q)))
        samples_per_period = (652e-9 / 152e-6) / (q[center + 1] - q[center])
        
        assert samples_per_period >= 12.0

    def test_criterion_07_and_08_screen_case_numerical_precision(self) -> None:
        """7 e 8. O caso da tela produz I/I₀ ≈ 4,3001477 × 10⁻⁷ e I ≈ 2,2790783 × 10⁻⁶ para I₀ = 5,3."""
        alpha = math.radians(12.4)
        theta = math.radians(27.3)
        i0 = 5.3
        params = InterferenceParameters(
            slit_count=2,
            wavelength_m=652e-9,
            slit_width_m=32.1e-6,
            slit_separation_m=152.0e-6,
            incidence_angle_rad=alpha,
            initial_intensity=i0,
        )

        abs_i, norm_i = compute_slit_intensity_scalar(theta, params)

        expected_norm = 4.3001477e-7
        expected_abs = 2.2790783e-6

        
        assert pytest.approx(norm_i, rel=1e-4) == expected_norm
        assert pytest.approx(abs_i, rel=1e-4) == expected_abs

    def test_criterion_12_single_slit_does_not_use_separation(self) -> None:
        """12. O modo de uma fenda não utiliza d."""
        p_no_d = InterferenceParameters(1, 500e-9, 15e-6, None, 0.0, 1.0)
        p_with_d = InterferenceParameters(1, 500e-9, 15e-6, 100e-6, 0.0, 1.0)

        r1 = compute_slit_interference(p_no_d)
        r2 = compute_slit_interference(p_with_d, observation_angles=r1.observation_angles_rad)

        assert np.allclose(r1.normalized_intensity, r2.normalized_intensity)

    def test_criterion_14_invalid_inputs_rejected_cleanly(self) -> None:
        """14. Entradas inválidas continuam não encerrando a aplicação."""
        with pytest.raises(InvalidPhysicalParameterError):
            compute_slit_interference(
                InterferenceParameters(1, 350e-9, 10e-6, None, 0.0)
            )

        with pytest.raises(SlitSeparationGeometryError):
            compute_slit_interference(
                InterferenceParameters(2, 500e-9, 20e-6, 15e-6, 0.0)
            )

    def test_extreme_valid_separation_resolves_interference_orders(self) -> None:
        
        wavelength = 400e-9
        separation = 300e-6
        params = InterferenceParameters(2, wavelength, 1e-6, separation, 0.0)
        result = compute_slit_interference(params)
        q = np.sin(result.observation_angles_rad)
        center = int(np.argmin(np.abs(q)))
        dq = q[center + 1] - q[center]

        assert wavelength / separation / dq >= 16.0 - 1e-10
        assert np.isfinite(result.normalized_intensity).all()

        
        
        for order in range(1, 201):
            theta_max = math.asin(order * wavelength / separation)
            theta_min = math.asin((order + 0.5) * wavelength / separation)
            max_index = int(np.argmin(np.abs(result.observation_angles_rad - theta_max)))
            min_index = int(np.argmin(np.abs(result.observation_angles_rad - theta_min)))
            assert abs(result.observation_angles_rad[max_index] - theta_max) < 1e-12
            assert result.normalized_intensity[min_index] < 1e-24

    def test_nonfinite_selected_angle_is_rejected(self) -> None:
        params = InterferenceParameters(1, 500e-9, 10e-6, None, 0.0)
        with pytest.raises(InvalidPhysicalParameterError, match="Ângulo observado"):
            compute_slit_interference(params, selected_angle_rad=math.nan)
