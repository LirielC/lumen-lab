

from functools import lru_cache
from html import escape
from io import BytesIO

from matplotlib.font_manager import FontProperties
from matplotlib import rc_context
from matplotlib.mathtext import math_to_image
from PySide6.QtCore import QUrl
from PySide6.QtGui import QImage, QTextDocument

from app.core.application.dto.responses import InterferenceResponse, PolarizationResponse
from app.core.utils.formatting import format_didactic_number, format_intensity
from app.adapters.inbound.qt.styles.theme import ThemePalette


@lru_cache(maxsize=256)
def equation_image(expression: str, color: str) -> QImage:
    
    stream = BytesIO()
    with rc_context({"savefig.transparent": True}):
        math_to_image(f"${expression}$", stream, format="png", dpi=160, color=color,
                      prop=FontProperties(size=20, math_fontfamily="stix"))
    return QImage.fromData(stream.getvalue(), "PNG")


def math_number(value: float) -> str:
    text = format_intensity(value)
    if "e" in text:
        mantissa, exponent = text.split("e")
        return mantissa.replace(".", "{,}") + rf"\times 10^{{{int(exponent)}}}"
    return text.replace(".", "{,}")


def populate_math_document(
    document: QTextDocument,
    response: InterferenceResponse | PolarizationResponse,
    palette: ThemePalette,
    width: float,
) -> None:
    
    
    document.clear()
    parts = []
    image_index = 0

    def equation(expression: str, description: str, result: bool = False) -> None:
        nonlocal image_index
        image = equation_image(expression, palette.accent if result else palette.text_primary)
        url = QUrl(f"math:equation-{image_index}")
        image_index += 1
        document.addResource(QTextDocument.ResourceType.ImageResource, url, image)
        display_width = min(image.width() / 2, width - 12)
        display_height = display_width * image.height() / image.width()
        parts.append(f'<p style="margin:10px 0;"><img src="{url.toString()}" '
                     f'width="{round(display_width)}" height="{round(display_height)}" '
                     f'alt="{escape(description, quote=True)}"></p>')

    def section(title: str) -> None:
        if parts:
            parts.append(f'<hr color="{palette.border}">')
        parts.append(f'<p style="margin:14px 0 8px; color:{palette.accent};"><b>{title}</b></p>')

    def note(text: str) -> None:
        parts.append(f'<p style="margin:6px 0;">{escape(text)}</p>')

    def parameters(rows) -> None:
        parts.append('<table width="100%" cellspacing="0" cellpadding="3">')
        for label, value in rows:
            parts.append(f'<tr><td>{escape(label)}</td><td align="right"><b>{escape(value)}</b></td></tr>')
        parts.append('</table>')

    section("Teoria")
    if isinstance(response, InterferenceResponse):
        r = response
        expression = r"I(\theta)=I_0\left(\frac{\sin\beta}{\beta}\right)^2"
        if r.slit_count == 2:
            expression += r"\cos^2\delta"
        equation(expression, "Intensidade por difração e interferência")
        equation(r"q=\sin\theta-\sin\alpha", "Diferença dos senos dos ângulos")
        equation(r"\beta=\frac{\pi a}{\lambda}\,q", "Fase de difração")
        if r.slit_count == 2:
            equation(r"\delta=\frac{\pi d}{\lambda}\,q", "Meia diferença de fase")
            note("δ é a meia diferença de fase: Δφ = 2δ.")
        note("Para β = 0, o limite de sin β / β é 1.")
        section("Parâmetros")
        rows = [("λ · comprimento de onda", f"{r.wavelength_nm:g} nm"),
                ("a · largura", f"{r.slit_width_um:g} µm")]
        if r.slit_count == 2:
            rows.append(("d · separação", f"{r.slit_separation_um:g} µm"))
        rows += [("α · incidência", f"{r.incidence_angle_deg:g}°"),
                 ("θ · observação", f"{r.selected_angle_deg:g}°"),
                 ("I₀ · referência", f"{r.initial_intensity:g} rel")]
        parameters([(label, value.replace(".", ",")) for label, value in rows])
        note("1 nm = 10⁻⁹ m · 1 µm = 10⁻⁶ m. Cálculo interno em radianos.")
        section("Resolução")
        note("Fases calculadas")
        equation(rf"\beta\approx\mathbf{{{math_number(r.beta_rad)}}}", f"β = {r.beta_rad}", True)
        if r.delta_rad is not None:
            equation(rf"\delta\approx\mathbf{{{math_number(r.delta_rad)}}}", f"δ = {r.delta_rad}", True)
        if r.initial_intensity == 0:
            note("Fonte sem luz. I/I₀ é indefinido; o gráfico mostra o perfil teórico.")
        else:
            note("Perfil normalizado")
            equation(rf"\frac{{I}}{{I_0}}\approx\mathbf{{{math_number(r.selected_normalized_intensity)}}}",
                     f"I/I₀ = {r.selected_normalized_intensity}", True)
            note("Intensidade no ângulo selecionado")
            equation(rf"I\approx {math_number(r.initial_intensity)}\cdot {math_number(r.selected_normalized_intensity)}",
                     "Intensidade inicial vezes perfil normalizado")
        equation(rf"I\approx\mathbf{{{math_number(r.selected_intensity)}}}\;\mathrm{{rel}}",
                 f"I = {format_didactic_number(r.selected_intensity)} rel", True)
    elif isinstance(response, PolarizationResponse):
        r = response
        if not r.initially_polarized:
            equation(r"I_1=\frac{I_0}{2}", "Primeiro polarizador: metade da intensidade")
        else:
            equation(r"I_1=I_0\cos^2(\varphi_1-\varphi_0)", "Lei de Malus no primeiro polarizador")
        equation(r"I_k=I_{k-1}\cos^2(\varphi_k-\varphi_{k-1})", "Lei de Malus nas etapas seguintes")
        equation(r"\frac{E_k}{E_0}=\sqrt{\frac{I_k}{I_0}}", "Amplitude relativa do campo")
        section("Parâmetros")
        rows = [("Estado inicial", "Polarizada" if r.initially_polarized else "Não polarizada"),
                ("λ", f"{r.wavelength_nm:g} nm"), ("I₀", f"{r.initial_intensity:g} rel")]
        if r.initially_polarized:
            rows.append(("φ₀", f"{r.initial_angle_deg:g}°"))
        rows += [(f"P{s.index} · eixo", f"{s.axis_angle_deg:g}°") for s in r.stages]
        parameters([(label, value.replace(".", ",")) for label, value in rows])
        note("λ define a cor; a transmissão segue a Lei de Malus.")
        section("Resolução")
        for s in r.stages:
            note(f"Após o polarizador {s.index}")
            equation(rf"I_{s.index}\approx {math_number(s.input_intensity)}\cdot {math_number(s.stage_transmission_pct / 100)}",
                     f"Entrada vezes transmissão de P{s.index}")
            equation(rf"I_{s.index}\approx\mathbf{{{math_number(s.output_intensity)}}}\;\mathrm{{rel}}",
                     f"I{s.index} = {format_didactic_number(s.output_intensity)} rel", True)
        if r.initial_intensity == 0:
            note("Fonte sem luz. I/I₀ é indefinido; transmissões e amplitudes adotam zero por convenção.")
        else:
            note("Transmissão acumulada")
            equation(rf"T\approx\mathbf{{{math_number(r.final_transmission_pct)}}}\%", "Transmissão final", True)
    document.setDefaultStyleSheet(f'body {{color:{palette.text_secondary}; font-family:"Segoe UI"; font-size:12px;}}')
    document.setHtml('<body>' + ''.join(parts) + '</body>')
