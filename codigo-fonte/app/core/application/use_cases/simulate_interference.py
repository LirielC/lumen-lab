

import math
from typing import Literal
import numpy as np
from app.core.application.dto.requests import InterferenceRequest
from app.core.application.dto.responses import InterferenceResponse
from app.core.domain.models.interference import InterferenceParameters
from app.core.domain.physics.interference import (
    compute_slit_interference,
    generate_angular_grid,
)
from app.core.domain.physics.optics_color import (
    wavelength_to_hex,
    wavelength_to_rgb,
)


class SimulateInterferenceUseCase:
    

    def execute(self, request: InterferenceRequest) -> InterferenceResponse:
        
        
        wavelength_m = request.wavelength_nm * 1e-9
        slit_width_m = request.slit_width_um * 1e-6
        slit_separation_m = (
            request.slit_separation_um * 1e-6
            if request.slit_separation_um is not None and request.slit_count == 2
            else None
        )
        incidence_angle_rad = math.radians(request.incidence_angle_deg)
        observation_angle_rad = math.radians(request.observation_angle_deg)

        assert request.slit_count in (1, 2)
        slit_count_lit: Literal[1, 2] = 1 if request.slit_count == 1 else 2

        domain_params = InterferenceParameters(
            slit_count=slit_count_lit,
            wavelength_m=wavelength_m,
            slit_width_m=slit_width_m,
            slit_separation_m=slit_separation_m,
            incidence_angle_rad=incidence_angle_rad,
            initial_intensity=request.initial_intensity,
        )

        domain_result = compute_slit_interference(
            params=domain_params,
            selected_angle_rad=observation_angle_rad,
        )

        
        angles_deg = np.degrees(domain_result.observation_angles_rad)
        beam_color_hex = wavelength_to_hex(request.wavelength_nm)
        beam_rgb = wavelength_to_rgb(request.wavelength_nm)

        
        q_val = domain_result.selected_q
        beta_val = domain_result.selected_beta_rad
        delta_val = domain_result.selected_delta_rad

        from app.core.utils.formatting import format_didactic_number, format_ratio_percent

        a_sci = (
            f"{request.slit_width_um:.0f} × 10⁻⁶"
            if math.isclose(request.slit_width_um, round(request.slit_width_um))
            else f"{request.slit_width_um:.2f} × 10⁻⁶".replace(".", ",")
        )
        wl_sci = (
            f"{request.wavelength_nm:.0f} × 10⁻⁹"
            if math.isclose(request.wavelength_nm, round(request.wavelength_nm))
            else f"{request.wavelength_nm:.1f} × 10⁻⁹".replace(".", ",")
        )
        sin_theta_str = f"{math.sin(observation_angle_rad):+.4f}".replace(".", ",")
        sin_alpha_str = f"{math.sin(incidence_angle_rad):+.4f}".replace(".", ",")
        q_str = f"{q_val:+.4f}".replace(".", ",")
        factor_beta = (math.pi * slit_width_m) / wavelength_m
        factor_beta_str = f"{factor_beta:.3f}".replace(".", ",")
        beta_str = format_didactic_number(beta_val, precision=3)
        norm_i_str = format_didactic_number(domain_result.selected_normalized_intensity, precision=4)
        abs_i_str = format_didactic_number(domain_result.selected_intensity, precision=4)
        i0_str = f"{request.initial_intensity:.4f}".rstrip("0").rstrip(".").replace(".", ",")
        if not i0_str or i0_str == "0":
            i0_str = "0,0"
        pct_str = format_ratio_percent(domain_result.selected_normalized_intensity, use_comma=True)

        if request.slit_count == 1:
            formula_latex = (
                r"I(\theta) = I_0 \left[ \frac{\sin\beta}{\beta} \right]^2, \quad "
                r"\beta = \frac{\pi a}{\lambda}(\sin\theta - \sin\alpha)"
            )

            if abs(beta_val) < 1e-10:
                step_by_step = (
                    "Substituição Didática dos Valores:\n"
                    f"  β = [π · ({a_sci}) / ({wl_sci})] · [sin({request.observation_angle_deg:+.1f}°) − sin({request.incidence_angle_deg:+.1f}°)]\n"
                    f"  β = [{factor_beta_str}] · [{sin_theta_str} − ({sin_alpha_str})]\n"
                    f"  β = [{factor_beta_str}] · [0,0000]\n"
                    "  β = 0,000  (Máximo Principal: θ = α)\n\n"
                    "Depois (Limite Fundamental quando β → 0):\n"
                    "  Como β → 0, utiliza-se analiticamente o limite:\n"
                    "    lim_{β → 0} [sin(β) / β]² = 1\n"
                    f"  I / I₀ = 1,0000 ({pct_str})\n\n"
                    f"  I = {i0_str} · 1,0000\n"
                    f"  I = {abs_i_str}"
                )
            else:
                sin_beta_val = math.sin(beta_val)
                sin_beta_str = f"{sin_beta_val:+.4f}".replace(".", ",")
                step_by_step = (
                    "Substituição Didática dos Valores:\n"
                    f"  β = [π · ({a_sci}) / ({wl_sci})] · [sin({request.observation_angle_deg:+.1f}°) − sin({request.incidence_angle_deg:+.1f}°)]\n"
                    f"  β = [{factor_beta_str}] · [{sin_theta_str} − ({sin_alpha_str})]\n"
                    f"  β = [{factor_beta_str}] · [{q_str}]\n"
                    f"  β ≈ {beta_str}\n\n"
                    "Depois:\n"
                    f"  I / I₀ = [sin({beta_str}) / {beta_str}]²\n"
                    f"  I / I₀ ≈ {norm_i_str} ({pct_str})\n\n"
                    f"  I = {i0_str} · {norm_i_str}\n"
                    f"  I ≈ {abs_i_str}"
                )

            formula_text = (
                "Equação Física da Difração por Uma Fenda:\n\n"
                "  I(θ) = I₀ · [sin(β) / β]²\n\n"
                "  β = (πa / λ) · (sin θ − sin α)\n\n"
                "Para os parâmetros atuais:\n\n"
                f"  β = {beta_str}\n"
                f"  I / I₀ = {norm_i_str}\n"
                f"  I = {abs_i_str}\n\n"
                "Parâmetros de Entrada:\n"
                f"  • a (largura da fenda) = {request.slit_width_um:.2f} µm ({a_sci} m)\n"
                f"  • λ (comprimento de onda) = {request.wavelength_nm:.1f} nm ({wl_sci} m)\n"
                f"  • α (ângulo de incidência) = {request.incidence_angle_deg:+.1f}° ({incidence_angle_rad:+.4f} rad)\n"
                f"  • θ (ângulo observado) = {request.observation_angle_deg:+.1f}° ({observation_angle_rad:+.4f} rad)\n"
                f"  • I₀ (intensidade de referência do pico central) = {i0_str}\n\n"
                f"{step_by_step}\n\n"
                "Nota Didática:\n"
                "Internamente, os cálculos trigonométricos são realizados em radianos, "
                "mantendo apresentação ao usuário em graus."
            )
        else:
            assert request.slit_separation_um is not None
            assert delta_val is not None
            d_sci = (
                f"{request.slit_separation_um:.0f} × 10⁻⁶"
                if math.isclose(request.slit_separation_um, round(request.slit_separation_um))
                else f"{request.slit_separation_um:.2f} × 10⁻⁶".replace(".", ",")
            )
            factor_delta = (math.pi * slit_separation_m) / wavelength_m
            factor_delta_str = f"{factor_delta:.3f}".replace(".", ",")
            delta_str = format_didactic_number(delta_val, precision=3)

            formula_latex = (
                r"I(\theta) = I_0 \left[ \frac{\sin\beta}{\beta} \right]^2 \cos^2\delta, \quad "
                r"\beta = \frac{\pi a}{\lambda}(\sin\theta - \sin\alpha), \quad "
                r"\delta = \frac{\pi d}{\lambda}(\sin\theta - \sin\alpha)"
            )

            envelope_norm = domain_result.selected_envelope
            interference_term = domain_result.selected_interference_factor
            env_str = format_didactic_number(envelope_norm, precision=4)
            interf_str = format_didactic_number(interference_term, precision=4)

            formula_text = (
                "Equação Física de Interferência e Difração (Duas Fendas):\n"
                "  I(θ) = I₀ · [sin(β) / β]² · cos²(δ)\n"
                "  β = (π · a / λ) · (sin θ − sin α)   (envelope de difração)\n"
                "  δ = (π · d / λ) · (sin θ − sin α)   (interferência de Young)\n\n"
                "Parâmetros e Valores Atuais:\n"
                f"  • a (largura das fendas): {request.slit_width_um:.2f} µm ({a_sci} m)\n"
                f"  • d (distância entre fendas): {request.slit_separation_um:.2f} µm ({d_sci} m)\n"
                f"  • λ (comprimento de onda): {request.wavelength_nm:.1f} nm ({wl_sci} m)\n"
                f"  • α (incidência): {request.incidence_angle_deg:+.1f}°  |  θ (observado): {request.observation_angle_deg:+.1f}°\n"
                f"  • I₀ (intensidade de referência do pico central): {i0_str}\n\n"
                "Cálculo das Variáveis de Fase:\n"
                f"  • β = [{factor_beta_str}] · [{q_str}] ≈ {beta_str}\n"
                f"  • δ = [{factor_delta_str}] · [{q_str}] ≈ {delta_str}\n\n"
                "Composição dos Termos Ópticos:\n"
                f"  • Envelope difrativo [sin(β) / β]² ≈ {env_str}\n"
                f"  • Fator interferencial cos²(δ) ≈ {interf_str}\n"
                f"  • I / I₀ = {env_str} · {interf_str} ≈ {norm_i_str} ({pct_str})\n\n"
                "Cálculo da Intensidade Observada (I):\n"
                f"  I = I₀ · (I / I₀) = {i0_str} · {norm_i_str}\n"
                f"  I ≈ {abs_i_str}"
            )

        if request.initial_intensity == 0:
            formula_text = (
                "Fonte sem luz: I₀ = 0 e I = 0 em todas as direções.\n"
                "I/I₀ é indefinido. O gráfico conserva apenas o perfil teórico normalizado.\n\n"
                + formula_text.replace("I / I₀", "Perfil normalizado")
            )

        return InterferenceResponse(
            angles_deg=angles_deg,
            normalized_intensity=domain_result.normalized_intensity,
            scaled_relative_intensity=domain_result.scaled_relative_intensity,
            selected_angle_deg=request.observation_angle_deg,
            selected_intensity=domain_result.selected_intensity,
            selected_normalized_intensity=domain_result.selected_normalized_intensity,
            wavelength_nm=request.wavelength_nm,
            beam_color_hex=beam_color_hex,
            beam_rgb=beam_rgb,
            slit_count=request.slit_count,
            slit_width_um=request.slit_width_um,
            slit_separation_um=request.slit_separation_um,
            incidence_angle_deg=request.incidence_angle_deg,
            initial_intensity=request.initial_intensity,
            formula_latex=formula_latex,
            formula_text=formula_text,
            beta_rad=beta_val,
            delta_rad=delta_val,
        )
