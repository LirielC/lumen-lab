





import math
import pytest
from app.core.domain.errors import (
    InvalidPhysicalParameterError,
    PolarizerCountError,
)
from app.core.domain.models.polarization import PolarizationParameters
from app.core.domain.physics.polarization import compute_polarization
from app.core.domain.physics.optics_color import wavelength_to_hex, wavelength_to_rgb


class TestIndependentAnalyticalPolarizerCases:
    

    def test_case_01_unpolarized_single_polarizer_0_deg(self) -> None:
        """Caso 1: Não polarizada, I0=1, P1=0° -> I1=0.5, E1/E0 ≈ 0.70710678."""
        
        I0 = 1.0
        expected_I1 = I0 / 2.0
        expected_E1_ratio = math.sqrt(expected_I1 / I0)

        params = PolarizationParameters(
            polarizer_count=1,
            wavelength_m=550e-9,
            initial_intensity=I0,
            initially_polarized=False,
            initial_angle_rad=None,
            polarizer_angles_rad=(0.0,),
        )
        res = compute_polarization(params)

        assert res.final_intensity == pytest.approx(expected_I1, rel=1e-9)
        assert res.final_field_amplitude == pytest.approx(expected_E1_ratio, rel=1e-7)
        assert res.stages[0].field_direction_rad == pytest.approx(0.0, abs=1e-9)

    def test_case_02_unpolarized_two_parallel_polarizers(self) -> None:
        """Caso 2: Não polarizada, I0=1, P1=0°, P2=0° -> I1=0.5, I2=0.5, T_etapa2=100%, T_tot=50%."""
        I0 = 1.0
        expected_I1 = I0 / 2.0
        expected_I2 = expected_I1 * (math.cos(0.0) ** 2)
        expected_T_stage2 = 1.0
        expected_T_total = expected_I2 / I0

        params = PolarizationParameters(
            polarizer_count=2,
            wavelength_m=600e-9,
            initial_intensity=I0,
            initially_polarized=False,
            initial_angle_rad=None,
            polarizer_angles_rad=(0.0, 0.0),
        )
        res = compute_polarization(params)

        assert len(res.stages) == 2
        assert res.stages[0].output_intensity == pytest.approx(expected_I1, rel=1e-9)
        assert res.stages[1].output_intensity == pytest.approx(expected_I2, rel=1e-9)
        assert res.stages[1].stage_transmission == pytest.approx(expected_T_stage2, rel=1e-9)
        assert res.stages[1].cumulative_transmission == pytest.approx(expected_T_total, rel=1e-9)

    def test_case_03_unpolarized_three_polarizers_0_45_90(self) -> None:
        """Caso 3: Não polarizada, I0=1, eixos 0°, 45° e 90° -> I1=0.5, I2=0.25, I3=0.125.
        Amplitudes: aproximadamente 0.7071, 0.5000, 0.3536.
        """
        I0 = 1.0
        p1_rad = math.radians(0.0)
        p2_rad = math.radians(45.0)
        p3_rad = math.radians(90.0)

        
        ref_I1 = I0 * 0.5
        ref_I2 = ref_I1 * (math.cos(p2_rad - p1_rad) ** 2)
        ref_I3 = ref_I2 * (math.cos(p3_rad - p2_rad) ** 2)
        ref_E1 = math.sqrt(ref_I1 / I0)
        ref_E2 = math.sqrt(ref_I2 / I0)
        ref_E3 = math.sqrt(ref_I3 / I0)

        params = PolarizationParameters(
            polarizer_count=3,
            wavelength_m=550e-9,
            initial_intensity=I0,
            initially_polarized=False,
            initial_angle_rad=None,
            polarizer_angles_rad=(p1_rad, p2_rad, p3_rad),
        )
        res = compute_polarization(params)

        assert res.stages[0].output_intensity == pytest.approx(ref_I1, rel=1e-9)
        assert res.stages[1].output_intensity == pytest.approx(ref_I2, rel=1e-9)
        assert res.stages[2].output_intensity == pytest.approx(ref_I3, rel=1e-9)

        assert res.stages[0].relative_field_amplitude == pytest.approx(ref_E1, rel=1e-4)
        assert res.stages[1].relative_field_amplitude == pytest.approx(ref_E2, rel=1e-4)
        assert res.stages[2].relative_field_amplitude == pytest.approx(ref_E3, rel=1e-4)

    def test_case_04_unpolarized_crossed_polarizers_0_and_90(self) -> None:
        """Caso 4: Não polarizada, I0=1, eixos 0° e 90° -> I1=0.5, I2=0 dentro da tolerância, amplitude final zero, direção None."""
        params = PolarizationParameters(
            polarizer_count=2,
            wavelength_m=520e-9,
            initial_intensity=1.0,
            initially_polarized=False,
            initial_angle_rad=None,
            polarizer_angles_rad=(0.0, math.radians(90.0)),
        )
        res = compute_polarization(params)

        assert res.stages[0].output_intensity == pytest.approx(0.5, rel=1e-9)
        assert res.stages[1].output_intensity == 0.0
        assert res.stages[1].relative_field_amplitude == 0.0
        assert res.final_intensity == 0.0
        assert res.final_field_amplitude == 0.0
        
        assert res.stages[1].field_direction_rad is None
        assert res.final_field_direction_rad is None

    def test_case_05_polarized_input_45_and_90(self) -> None:
        """Caso 5: Polarizada em 30°, I0=1, P1=45°, P2=90°:
        I1 ≈ 0.9330127019, I2 ≈ 0.4665063509
        Amplitudes: 0.9659258263 e 0.6830127019.
        """
        I0 = 1.0
        phi0 = math.radians(30.0)
        p1 = math.radians(45.0)
        p2 = math.radians(90.0)

        
        ref_I1 = I0 * (math.cos(p1 - phi0) ** 2)
        ref_I2 = ref_I1 * (math.cos(p2 - p1) ** 2)
        ref_E1 = math.sqrt(ref_I1 / I0)
        ref_E2 = math.sqrt(ref_I2 / I0)

        assert ref_I1 == pytest.approx(0.933012701892, rel=1e-8)
        assert ref_I2 == pytest.approx(0.466506350946, rel=1e-8)
        assert ref_E1 == pytest.approx(0.965925826289, rel=1e-8)
        assert ref_E2 == pytest.approx(0.683012701892, rel=1e-8)

        params = PolarizationParameters(
            polarizer_count=2,
            wavelength_m=650e-9,
            initial_intensity=I0,
            initially_polarized=True,
            initial_angle_rad=phi0,
            polarizer_angles_rad=(p1, p2),
        )
        res = compute_polarization(params)

        assert res.stages[0].output_intensity == pytest.approx(ref_I1, rel=1e-8)
        assert res.stages[1].output_intensity == pytest.approx(ref_I2, rel=1e-8)
        assert res.stages[0].relative_field_amplitude == pytest.approx(ref_E1, rel=1e-8)
        assert res.stages[1].relative_field_amplitude == pytest.approx(ref_E2, rel=1e-8)

    def test_case_06_exact_user_specified_cascade_88_90_90(self) -> None:
        """Caso 6: Polarizada em 30°, I0=6.3, eixos 88°, 90° e 90°:
        I1 ≈ 1.7691308876
        I2 ≈ 1.7669761307
        I3 ≈ 1.7669761307
        Transmissão final ≈ 28.04724017%
        Amplitude final relativa ≈ 0.5295964517
        """
        I0 = 6.3
        phi0 = math.radians(30.0)
        p1 = math.radians(88.0)
        p2 = math.radians(90.0)
        p3 = math.radians(90.0)

        
        ref_I1 = I0 * (math.cos(p1 - phi0) ** 2)
        ref_I2 = ref_I1 * (math.cos(p2 - p1) ** 2)
        ref_I3 = ref_I2 * (math.cos(p3 - p2) ** 2)
        ref_trans_pct = (ref_I3 / I0) * 100.0
        ref_final_amp = math.sqrt(ref_I3 / I0)

        assert ref_I1 == pytest.approx(1.7691308876, rel=1e-7)
        assert ref_I2 == pytest.approx(1.7669761307, rel=1e-7)
        assert ref_I3 == pytest.approx(1.7669761307, rel=1e-7)
        assert ref_trans_pct == pytest.approx(28.04724017, rel=1e-6)
        assert ref_final_amp == pytest.approx(0.5295964517, rel=1e-6)

        params = PolarizationParameters(
            polarizer_count=3,
            wavelength_m=650e-9,
            initial_intensity=I0,
            initially_polarized=True,
            initial_angle_rad=phi0,
            polarizer_angles_rad=(p1, p2, p3),
        )
        res = compute_polarization(params)

        assert res.stages[0].output_intensity == pytest.approx(ref_I1, rel=1e-7)
        assert res.stages[1].output_intensity == pytest.approx(ref_I2, rel=1e-7)
        assert res.stages[2].output_intensity == pytest.approx(ref_I3, rel=1e-7)
        assert (res.final_transmission * 100.0) == pytest.approx(ref_trans_pct, rel=1e-6)
        assert res.final_field_amplitude == pytest.approx(ref_final_amp, rel=1e-6)


class TestPolarizationPhysicalInvariants:
    

    @pytest.mark.parametrize("i0", [0.1, 1.0, 5.0, 10.0])
    @pytest.mark.parametrize("p1_deg", [0, 30, 45, 90, 135, 180])
    @pytest.mark.parametrize("p2_deg", [0, 45, 90, 120, 180])
    def test_invariant_intensity_monotonic_decrease_or_equality(self, i0: float, p1_deg: float, p2_deg: float) -> None:
        """Invariante: 0 <= Ik <= I(k-1) para polarizadores ideais e nenhuma intensidade pode ser negativa."""
        params = PolarizationParameters(
            polarizer_count=2,
            wavelength_m=550e-9,
            initial_intensity=i0,
            initially_polarized=False,
            initial_angle_rad=None,
            polarizer_angles_rad=(math.radians(p1_deg), math.radians(p2_deg)),
        )
        res = compute_polarization(params)

        assert res.stages[0].output_intensity >= 0.0
        assert res.stages[0].output_intensity <= i0 + 1e-12
        assert res.stages[1].output_intensity >= 0.0
        assert res.stages[1].output_intensity <= res.stages[0].output_intensity + 1e-12

    @pytest.mark.parametrize("p_deg", [0, 37, 72, 90, 143])
    def test_invariant_parallel_polarizers_cause_no_further_loss(self, p_deg: float) -> None:
        """Invariante: Eixos paralelos não causam nova perda ideal (transmissão da etapa = 100%)."""
        p_rad = math.radians(p_deg)
        params = PolarizationParameters(
            polarizer_count=3,
            wavelength_m=550e-9,
            initial_intensity=2.5,
            initially_polarized=False,
            initial_angle_rad=None,
            polarizer_angles_rad=(p_rad, p_rad, p_rad),
        )
        res = compute_polarization(params)

        assert res.stages[1].stage_transmission == pytest.approx(1.0, abs=1e-9)
        assert res.stages[2].stage_transmission == pytest.approx(1.0, abs=1e-9)
        assert res.stages[1].output_intensity == pytest.approx(res.stages[0].output_intensity, abs=1e-9)
        assert res.stages[2].output_intensity == pytest.approx(res.stages[0].output_intensity, abs=1e-9)

    @pytest.mark.parametrize("p_deg", [0, 15, 45, 90])
    def test_invariant_modulo_180_invariance(self, p_deg: float) -> None:
        """Invariante: Somar 180° a qualquer eixo não altera a intensidade."""
        p1 = math.radians(p_deg)
        p2 = math.radians(p_deg + 45.0)

        params_base = PolarizationParameters(
            polarizer_count=2,
            wavelength_m=550e-9,
            initial_intensity=1.0,
            initially_polarized=False,
            initial_angle_rad=None,
            polarizer_angles_rad=(p1, p2),
        )
        params_shifted = PolarizationParameters(
            polarizer_count=2,
            wavelength_m=550e-9,
            initial_intensity=1.0,
            initially_polarized=False,
            initial_angle_rad=None,
            polarizer_angles_rad=(p1 + math.pi, p2 + math.pi),
        )
        r_base = compute_polarization(params_base)
        r_shifted = compute_polarization(params_shifted)

        assert r_base.final_intensity == pytest.approx(r_shifted.final_intensity, abs=1e-12)

    @pytest.mark.parametrize("wavelength_nm", [400.0, 488.0, 532.0, 633.0, 700.0])
    def test_invariant_wavelength_does_not_alter_ideal_malus_law(self, wavelength_nm: float) -> None:
        """Invariante: Alterar comprimento de onda não altera a Lei de Malus ideal; altera apenas a cor visual."""
        params = PolarizationParameters(
            polarizer_count=3,
            wavelength_m=wavelength_nm * 1e-9,
            initial_intensity=2.0,
            initially_polarized=False,
            initial_angle_rad=None,
            polarizer_angles_rad=(0.0, math.radians(45.0), math.radians(90.0)),
        )
        res = compute_polarization(params)

        
        assert res.final_intensity == pytest.approx(0.25, abs=1e-12)
        
        hex_color = wavelength_to_hex(wavelength_nm)
        assert hex_color.startswith("#")
        assert len(hex_color) == 7

    def test_invariant_stage_count_matches_polarizer_count(self) -> None:
        """Invariante: Quantidade de etapas corresponde à quantidade de polarizadores."""
        for count in (1, 2, 3):
            angles = tuple(math.radians(30.0 * i) for i in range(count))
            params = PolarizationParameters(
                polarizer_count=count,
                wavelength_m=550e-9,
                initial_intensity=1.0,
                initially_polarized=False,
                initial_angle_rad=None,
                polarizer_angles_rad=angles,
            )
            res = compute_polarization(params)
            assert len(res.stages) == count

    def test_invariant_zero_initial_intensity_no_division_by_zero(self) -> None:
        """Invariante: I0=0 não causa divisão por zero e resulta em amplitude e intensidade zero."""
        params = PolarizationParameters(
            polarizer_count=3,
            wavelength_m=550e-9,
            initial_intensity=0.0,
            initially_polarized=False,
            initial_angle_rad=None,
            polarizer_angles_rad=(0.0, math.radians(45), math.radians(90)),
        )
        res = compute_polarization(params)

        assert res.final_intensity == 0.0
        assert res.final_transmission == 0.0
        assert res.final_field_amplitude == 0.0
        for stage in res.stages:
            assert stage.output_intensity == 0.0
            assert stage.relative_field_amplitude == 0.0
            assert stage.field_direction_rad is None

    def test_invariant_relative_amplitude_strictly_equals_sqrt_intensity_ratio(self) -> None:
        """Invariante: A amplitude exibida corresponde estritamente a sqrt(I/I0)."""
        I0 = 4.2
        params = PolarizationParameters(
            polarizer_count=3,
            wavelength_m=550e-9,
            initial_intensity=I0,
            initially_polarized=True,
            initial_angle_rad=math.radians(10.0),
            polarizer_angles_rad=(math.radians(25.0), math.radians(60.0), math.radians(85.0)),
        )
        res = compute_polarization(params)

        for stage in res.stages:
            expected_amp = math.sqrt(stage.output_intensity / I0)
            assert stage.relative_field_amplitude == pytest.approx(expected_amp, abs=1e-12)

    def test_invalid_parameters_rejected(self) -> None:
        """Invariante: Valores não finitos e contagens fora de [1, 3] são rejeitados."""
        with pytest.raises(PolarizerCountError):
            compute_polarization(
                PolarizationParameters(
                    polarizer_count=4,  
                    wavelength_m=550e-9,
                    initial_intensity=1.0,
                    initially_polarized=False,
                    initial_angle_rad=None,
                    polarizer_angles_rad=(0.0, 0.0, 0.0, 0.0),
                )
            )

        with pytest.raises(InvalidPhysicalParameterError):
            compute_polarization(
                PolarizationParameters(
                    polarizer_count=2,
                    wavelength_m=float("nan"),  
                    initial_intensity=1.0,
                    initially_polarized=False,
                    initial_angle_rad=None,
                    polarizer_angles_rad=(0.0, 0.0),
                )
            )
