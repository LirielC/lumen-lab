

import math
from app.core.application.dto.requests import PolarizationRequest
from app.core.application.dto.responses import PolarizationResponse, StageDTO
from app.core.domain.models.polarization import PolarizationParameters
from app.core.domain.physics.optics_color import (
    wavelength_to_hex,
    wavelength_to_rgb,
)
from app.core.domain.physics.polarization import compute_polarization


class SimulatePolarizationUseCase:
    

    def execute(self, request: PolarizationRequest) -> PolarizationResponse:
        
        wavelength_m = request.wavelength_nm * 1e-9
        initial_angle_rad = (
            math.radians(request.initial_angle_deg)
            if request.initially_polarized and request.initial_angle_deg is not None
            else None
        )
        polarizer_angles_rad = tuple(
            math.radians(deg) for deg in request.polarizer_angles_deg
        )

        domain_params = PolarizationParameters(
            polarizer_count=request.polarizer_count,
            wavelength_m=wavelength_m,
            initial_intensity=request.initial_intensity,
            initially_polarized=request.initially_polarized,
            initial_angle_rad=initial_angle_rad,
            polarizer_angles_rad=polarizer_angles_rad,
        )

        domain_result = compute_polarization(domain_params)

        stage_dtos: list[StageDTO] = []
        for stage in domain_result.stages:
            stage_dtos.append(
                StageDTO(
                    index=stage.index,
                    axis_angle_deg=math.degrees(stage.axis_angle_rad),
                    input_intensity=stage.input_intensity,
                    output_intensity=stage.output_intensity,
                    stage_transmission_pct=stage.stage_transmission * 100.0,
                    cumulative_transmission_pct=stage.cumulative_transmission * 100.0,
                    relative_field_amplitude=stage.relative_field_amplitude,
                    field_direction_deg=(
                        math.degrees(stage.field_direction_rad)
                        if stage.field_direction_rad is not None
                        else None
                    ),
                )
            )

        beam_color_hex = wavelength_to_hex(request.wavelength_nm)
        beam_rgb = wavelength_to_rgb(request.wavelength_nm)

        if not request.initially_polarized:
            formula_latex = (
                r"I_1 = \frac{I_0}{2}, \quad I_k = I_{k-1} \cos^2(\phi_k - \phi_{k-1})"
            )
            formula_text = (
                "Luz Inicialmente Não Polarizada:\n"
                "• P1: I₁ = I₀ / 2 (atenuação de 50%)\n"
                "• Pk (k > 1): I_k = I_{k-1} · cos²(φ_k - φ_{k-1})\n"
                "• Amplitude do campo: E_k / E₀ = √(I_k / I₀)"
            )
        else:
            formula_latex = (
                r"I_k = I_{k-1} \cos^2(\phi_k - \phi_{k-1})"
            )
            formula_text = (
                "Luz Inicialmente Polarizada (Lei de Malus em Cascata):\n"
                f"• P1: I₁ = I₀ · cos²(φ₁ - φ₀), com φ₀ = {request.initial_angle_deg:.1f}°\n"
                "• Pk (k > 1): I_k = I_{k-1} · cos²(φ_k - φ_{k-1})\n"
                "• Amplitude do campo: E_k / E₀ = √(I_k / I₀)"
            )

        final_direction_deg = (
            math.degrees(domain_result.final_field_direction_rad)
            if domain_result.final_field_direction_rad is not None
            else None
        )

        return PolarizationResponse(
            initial_intensity=request.initial_intensity,
            initially_polarized=request.initially_polarized,
            initial_angle_deg=request.initial_angle_deg,
            wavelength_nm=request.wavelength_nm,
            beam_color_hex=beam_color_hex,
            beam_rgb=beam_rgb,
            stages=tuple(stage_dtos),
            final_intensity=domain_result.final_intensity,
            final_transmission_pct=domain_result.final_transmission * 100.0,
            final_field_amplitude=domain_result.final_field_amplitude,
            final_field_direction_deg=final_direction_deg,
            formula_latex=formula_latex,
            formula_text=formula_text,
        )
