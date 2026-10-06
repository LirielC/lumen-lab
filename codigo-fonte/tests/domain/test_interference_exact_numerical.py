









import math
import numpy as np
import pytest

from app.core.domain.models.interference import InterferenceParameters
from app.core.domain.physics.interference import (
    compute_slit_interference,
    compute_slit_intensity_scalar,
    compute_slit_point_factors,
    generate_angular_grid,
)


class TestExactNumericalPhysics:
    

    def test_reported_single_slit_case_is_preserved(self) -> None:
        params = InterferenceParameters(
            slit_count=1,
            wavelength_m=629e-9,
            slit_width_m=25e-6,
            slit_separation_m=None,
            incidence_angle_rad=math.radians(4.5),
            initial_intensity=1.0,
        )
        result = compute_slit_interference(params, selected_angle_rad=math.radians(4.9))
        assert result.selected_normalized_intensity == pytest.approx(0.7724035, abs=5e-7)

    def test_single_slit_analytical_profile(self) -> None:
        
        wavelength = 632.8e-9  
        a = 25.0e-6           
        i0 = 2.5

        params = InterferenceParameters(
            slit_count=1,
            wavelength_m=wavelength,
            slit_width_m=a,
            slit_separation_m=None,
            incidence_angle_rad=0.0,
            initial_intensity=i0,
        )

        
        res_center = compute_slit_interference(params, selected_angle_rad=0.0)
        assert pytest.approx(res_center.selected_normalized_intensity, abs=1e-12) == 1.0
        assert pytest.approx(res_center.selected_intensity, abs=1e-12) == i0

        
        sin_theta_min1 = wavelength / a
        theta_min1 = math.asin(sin_theta_min1)
        res_min1 = compute_slit_interference(params, selected_angle_rad=theta_min1)
        assert pytest.approx(res_min1.selected_normalized_intensity, abs=1e-10) == 0.0
        assert pytest.approx(res_min1.selected_intensity, abs=1e-10) == 0.0

        
        sin_theta_half = (wavelength / a) * 0.5
        theta_half = math.asin(sin_theta_half)
        res_half = compute_slit_interference(params, selected_angle_rad=theta_half)
        expected_norm = (2.0 / math.pi) ** 2
        assert pytest.approx(res_half.selected_normalized_intensity, rel=1e-5) == expected_norm
        assert pytest.approx(res_half.selected_intensity, rel=1e-5) == i0 * expected_norm

    def test_double_slit_analytical_profile(self) -> None:
        
        wavelength = 532.0e-9  
        a = 10.0e-6           # 10 µm
        d = 50.0e-6           # 50 µm
        i0 = 3.0

        params = InterferenceParameters(
            slit_count=2,
            wavelength_m=wavelength,
            slit_width_m=a,
            slit_separation_m=d,
            incidence_angle_rad=0.0,
            initial_intensity=i0,
        )

        
        res_center = compute_slit_interference(params, selected_angle_rad=0.0)
        assert pytest.approx(res_center.selected_normalized_intensity, abs=1e-12) == 1.0
        assert pytest.approx(res_center.selected_intensity, abs=1e-12) == i0

        
        sin_theta_int_min1 = (wavelength / (2.0 * d))
        theta_int_min1 = math.asin(sin_theta_int_min1)
        res_int_min1 = compute_slit_interference(params, selected_angle_rad=theta_int_min1)
        assert pytest.approx(res_int_min1.selected_normalized_intensity, abs=1e-10) == 0.0

        
        sin_theta_int_max1 = wavelength / d
        theta_int_max1 = math.asin(sin_theta_int_max1)
        res_int_max1 = compute_slit_interference(params, selected_angle_rad=theta_int_max1)
        
        expected_envelope = float(np.sinc((a / d)) ** 2)
        assert pytest.approx(res_int_max1.selected_envelope, rel=1e-5) == expected_envelope
        assert pytest.approx(res_int_max1.selected_interference_factor, abs=1e-10) == 1.0
        assert pytest.approx(res_int_max1.selected_normalized_intensity, rel=1e-5) == expected_envelope

    def test_missing_order_criterion(self) -> None:
        

        wavelength = 500e-9
        a = 15.0e-6
        d = 30.0e-6  # d = 2 * a

        params = InterferenceParameters(
            slit_count=2,
            wavelength_m=wavelength,
            slit_width_m=a,
            slit_separation_m=d,
            incidence_angle_rad=0.0,
            initial_intensity=1.0,
        )

        sin_theta_missing = 2.0 * wavelength / d  # = wavelength / a
        theta_missing = math.asin(sin_theta_missing)

        res = compute_slit_interference(params, selected_angle_rad=theta_missing)
        assert pytest.approx(res.selected_interference_factor, abs=1e-10) == 1.0  # cos^2(2*pi) = 1
        assert pytest.approx(res.selected_envelope, abs=1e-10) == 0.0             # sinc(1)^2 = 0
        assert pytest.approx(res.selected_normalized_intensity, abs=1e-10) == 0.0

    def test_oblique_incidence_shift(self) -> None:
        
        alpha = math.radians(8.5)
        wavelength = 600e-9
        a = 20.0e-6
        d = 80.0e-6

        params_single = InterferenceParameters(
            slit_count=1,
            wavelength_m=wavelength,
            slit_width_m=a,
            slit_separation_m=None,
            incidence_angle_rad=alpha,
            initial_intensity=4.0,
        )
        res_single = compute_slit_interference(params_single, selected_angle_rad=alpha)
        assert pytest.approx(res_single.selected_normalized_intensity, abs=1e-12) == 1.0
        assert pytest.approx(res_single.selected_intensity, abs=1e-12) == 4.0

        params_double = InterferenceParameters(
            slit_count=2,
            wavelength_m=wavelength,
            slit_width_m=a,
            slit_separation_m=d,
            incidence_angle_rad=alpha,
            initial_intensity=4.0,
        )
        res_double = compute_slit_interference(params_double, selected_angle_rad=alpha)
        assert pytest.approx(res_double.selected_normalized_intensity, abs=1e-12) == 1.0
        assert pytest.approx(res_double.selected_intensity, abs=1e-12) == 4.0
