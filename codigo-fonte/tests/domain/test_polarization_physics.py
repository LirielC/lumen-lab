

import math
import pytest
from app.core.domain.errors import (
    InvalidPolarizationStateError,
    PolarizerCountError,
)
from app.core.domain.models.polarization import PolarizationParameters
from app.core.domain.physics.polarization import compute_polarization


class TestPolarizationPhysics:
    

    def test_vp01_unpolarized_light_through_first_polarizer(self) -> None:
        """VP-01: Luz não polarizada + primeiro polarizador => I1 = I0 / 2."""
        i0 = 1.0
        params = PolarizationParameters(
            polarizer_count=1,
            wavelength_m=550e-9,
            initial_intensity=i0,
            initially_polarized=False,
            initial_angle_rad=None,
            polarizer_angles_rad=(math.radians(30.0),),
        )
        result = compute_polarization(params)
        assert len(result.stages) == 1
        assert pytest.approx(result.stages[0].output_intensity, rel=1e-6) == 0.5 * i0
        assert pytest.approx(result.final_intensity, rel=1e-6) == 0.5 * i0
        assert pytest.approx(result.final_transmission, rel=1e-6) == 0.5
        assert pytest.approx(result.final_field_amplitude, rel=1e-6) == math.sqrt(0.5)

    def test_vp02_polarized_light_aligned(self) -> None:
        """VP-02: Luz polarizada e alinhada ao primeiro polarizador => I1 = I0."""
        i0 = 2.0
        angle = math.radians(45.0)
        params = PolarizationParameters(
            polarizer_count=1,
            wavelength_m=500e-9,
            initial_intensity=i0,
            initially_polarized=True,
            initial_angle_rad=angle,
            polarizer_angles_rad=(angle,),
        )
        result = compute_polarization(params)
        assert pytest.approx(result.final_intensity, rel=1e-6) == i0
        assert pytest.approx(result.final_transmission, rel=1e-6) == 1.0
        assert pytest.approx(result.final_field_amplitude, rel=1e-6) == 1.0

    def test_vp03_polarized_light_perpendicular(self) -> None:
        """VP-03: Luz polarizada e perpendicular ao primeiro polarizador => I1 = 0."""
        i0 = 1.5
        params = PolarizationParameters(
            polarizer_count=1,
            wavelength_m=650e-9,
            initial_intensity=i0,
            initially_polarized=True,
            initial_angle_rad=0.0,
            polarizer_angles_rad=(math.radians(90.0),),
        )
        result = compute_polarization(params)
        assert pytest.approx(result.final_intensity, abs=1e-7) == 0.0
        assert pytest.approx(result.final_transmission, abs=1e-7) == 0.0
        assert pytest.approx(result.final_field_amplitude, abs=1e-7) == 0.0

    def test_vp04_two_parallel_polarizers(self) -> None:
        """VP-04: Dois polarizadores paralelos => segunda etapa não reduz a intensidade."""
        params = PolarizationParameters(
            polarizer_count=2,
            wavelength_m=550e-9,
            initial_intensity=1.0,
            initially_polarized=False,
            initial_angle_rad=None,
            polarizer_angles_rad=(math.radians(30.0), math.radians(30.0)),
        )
        result = compute_polarization(params)
        assert len(result.stages) == 2
        assert pytest.approx(result.stages[0].output_intensity, rel=1e-6) == 0.5
        assert pytest.approx(result.stages[1].output_intensity, rel=1e-6) == 0.5
        assert pytest.approx(result.stages[1].stage_transmission, rel=1e-6) == 1.0

    def test_vp05_two_crossed_polarizers(self) -> None:
        """VP-05: Dois polarizadores cruzados => intensidade final zero."""
        params = PolarizationParameters(
            polarizer_count=2,
            wavelength_m=550e-9,
            initial_intensity=1.0,
            initially_polarized=False,
            initial_angle_rad=None,
            polarizer_angles_rad=(0.0, math.radians(90.0)),
        )
        result = compute_polarization(params)
        assert pytest.approx(result.final_intensity, abs=1e-7) == 0.0
        assert pytest.approx(result.final_transmission, abs=1e-7) == 0.0

    def test_vp06_three_polarizers_cascade_0_45_90(self) -> None:
        """VP-06: Três polarizadores em 0°, 45° e 90° com luz não polarizada => I3 = I0 / 8."""
        i0 = 1.0
        params = PolarizationParameters(
            polarizer_count=3,
            wavelength_m=550e-9,
            initial_intensity=i0,
            initially_polarized=False,
            initial_angle_rad=None,
            polarizer_angles_rad=(0.0, math.radians(45.0), math.radians(90.0)),
        )
        result = compute_polarization(params)
        assert len(result.stages) == 3
        # I1 = I0 / 2 = 0.5
        assert pytest.approx(result.stages[0].output_intensity, rel=1e-6) == 0.5 * i0
        # I2 = I1 * cos^2(45°) = 0.5 * 0.5 = 0.25
        assert pytest.approx(result.stages[1].output_intensity, rel=1e-6) == 0.25 * i0
        # I3 = I2 * cos^2(45°) = 0.25 * 0.5 = 0.125
        assert pytest.approx(result.stages[2].output_intensity, rel=1e-6) == 0.125 * i0
        assert pytest.approx(result.final_intensity, rel=1e-6) == 0.125 * i0
        assert pytest.approx(result.final_transmission, rel=1e-6) == 0.125
        assert pytest.approx(result.final_field_amplitude, rel=1e-6) == math.sqrt(0.125)

    def test_vp07_zero_initial_intensity(self) -> None:
        """VP-07: I0 = 0 => todas as intensidades e amplitudes iguais a zero."""
        params = PolarizationParameters(
            polarizer_count=3,
            wavelength_m=500e-9,
            initial_intensity=0.0,
            initially_polarized=False,
            initial_angle_rad=None,
            polarizer_angles_rad=(0.0, math.radians(45.0), math.radians(90.0)),
        )
        result = compute_polarization(params)
        for stage in result.stages:
            assert stage.output_intensity == 0.0
            assert stage.cumulative_transmission == 0.0
            assert stage.relative_field_amplitude == 0.0
        assert result.final_intensity == 0.0

    def test_modulo_180_invariance(self) -> None:
        """Polarizadores com ângulos diferindo de 180° produzem a mesma transmissão."""
        params1 = PolarizationParameters(
            polarizer_count=1,
            wavelength_m=500e-9,
            initial_intensity=1.0,
            initially_polarized=True,
            initial_angle_rad=0.0,
            polarizer_angles_rad=(math.radians(30.0),),
        )
        params2 = PolarizationParameters(
            polarizer_count=1,
            wavelength_m=500e-9,
            initial_intensity=1.0,
            initially_polarized=True,
            initial_angle_rad=0.0,
            polarizer_angles_rad=(math.radians(210.0),),  # 30 + 180
        )
        r1 = compute_polarization(params1)
        r2 = compute_polarization(params2)
        assert pytest.approx(r1.final_intensity, rel=1e-6) == r2.final_intensity

    def test_tiny_aligned_intensity_is_preserved(self) -> None:
        params = PolarizationParameters(1, 550e-9, 1e-16, True, 0.0, (0.0,))
        result = compute_polarization(params)
        assert result.final_intensity == pytest.approx(1e-16, rel=1e-15)
        assert result.final_transmission == 1.0

    def test_validation_errors(self) -> None:
        """Validação rejeita número de polarizadores fora de 1..3 e falta de ângulo inicial."""
        with pytest.raises(PolarizerCountError):
            compute_polarization(
                PolarizationParameters(0, 500e-9, 1.0, False, None, ())
            )
        with pytest.raises(PolarizerCountError):
            compute_polarization(
                PolarizationParameters(4, 500e-9, 1.0, False, None, (0.0, 0.0, 0.0, 0.0))
            )
        with pytest.raises(InvalidPolarizationStateError):
            compute_polarization(
                PolarizationParameters(1, 500e-9, 1.0, True, None, (0.0,))
            )
