

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)
from app.adapters.inbound.qt.widgets.parameter_card import ParameterCard


class TheoryPage(QWidget):
    

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(16, 16, 16, 16)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 10, 24, 20)
        layout.setSpacing(16)

        
        title = QLabel("Fundamentação Teórica e Modelagem Física")
        title.setProperty("class", "heading-1")
        layout.addWidget(title)

        subtitle = QLabel(
            "Consulte os modelos analíticos, convenções de coordenadas e equações utilizadas pelo LumenLab."
        )
        subtitle.setProperty("class", "text-secondary")
        layout.addWidget(subtitle)

        # 1: Uma Fenda
        card_1 = ParameterCard("1. Difração de Fraunhofer por Uma Fenda")
        text_1 = QLabel(
            "Para uma fenda retangular delgada de largura <i>a</i> iluminada por radiação monocromática "
            "coerente de comprimento de onda <i>λ</i> com ângulo de incidência <i>α</i>, a intensidade observada "
            "em um ângulo <i>θ</i> no regime de campo distante (Fraunhofer) é dada por:<br><br>"
            "&nbsp;&nbsp;&nbsp;&nbsp;<b>I(θ) = I₀ · [ sin(β) / β ]² = I₀ · [ sinc(β/π) ]²</b><br><br>"
            "onde a variável de fase difrativa é:<br>"
            "&nbsp;&nbsp;&nbsp;&nbsp;<b>β = (π · a / λ) · (sin θ - sin α)</b><br><br>"
            "• <b>Máximo Central:</b> Ocorre quando sin θ = sin α (para incidência normal α = 0, no centro θ = 0). "
            "No limite β → 0, temos sin(β)/β → 1, logo I = I₀.<br>"
            "• <b>Mínimos de Difração:</b> Ocorrem onde a · (sin θ - sin α) = m · λ (com m = ±1, ±2, ...). "
            "Nesses ângulos, a intensidade se anula completamente.<br>"
            "• <b>Efeito da Largura (a):</b> Aumentar a largura estreita o lóbulo central de difração."
        )
        text_1.setTextFormat(Qt.TextFormat.RichText)
        text_1.setWordWrap(True)
        text_1.setProperty("class", "text-secondary")
        card_1.add_widget(text_1)
        layout.addWidget(card_1)

        # 2: Duas Fendas
        card_2 = ParameterCard("2. Interferência e Modulação Difrativa por Duas Fendas")
        text_2 = QLabel(
            "Para duas fendas idênticas de largura <i>a</i> com distância entre centros <i>d</i> (onde d > a):<br><br>"
            "&nbsp;&nbsp;&nbsp;&nbsp;<b>I(θ) = I₀ · [ sinc(β/π) ]² · cos²(δ)</b><br><br>"
            "onde δ é a meia diferença de fase entre as ondas provenientes das duas fendas:<br>"
            "&nbsp;&nbsp;&nbsp;&nbsp;<b>δ = (π · d / λ) · (sin θ - sin α)</b><br><br>"
            "A diferença de fase completa é <b>Δφ = 2δ</b>; portanto o fator de intensidade é cos²(Δφ/2).<br><br>"
            "• <b>Envelope de Difração:</b> O termo [sinc(β/π)]² modula a amplitude máxima das franjas.<br>"
            "• <b>Franjas de Interferência:</b> O termo cos²(δ) introduz oscilações rápidas no perfil angular.<br>"
            "• <b>Máximos do Fator de Interferência:</b> d · (sin θ - sin α) = m · λ (m inteiro). "
            "O envelope pode deslocar os máximos da intensidade total. O hover mostra dq/λ, sem arredondar para uma ordem inteira.<br>"
            "• <b>Mínimos de Interferência:</b> d · (sin θ - sin α) = (m + 1/2) · λ.<br>"
            "• <b>Ordens Ausentes:</b> Se um máximo de interferência coincidir com um mínimo do envelope difrativo, "
            "a franja correspondente desaparece."
        )
        text_2.setTextFormat(Qt.TextFormat.RichText)
        text_2.setWordWrap(True)
        text_2.setProperty("class", "text-secondary")
        card_2.add_widget(text_2)
        layout.addWidget(card_2)

        # 3: Polarização e Lei de Malus
        card_3 = ParameterCard("3. Polarização Linear e Lei de Malus em Cascata")
        text_3 = QLabel(
            "O LumenLab modela polarizadores lineares ideais:<br><br>"
            "• <b>Luz Inicialmente Não Polarizada:</b> Como o feixe incidente é uma superposição isotrópica "
            "de todas as orientações transversais com média temporal uniforme, o primeiro polarizador ideal "
            "transmite exatamente metade da intensidade média incidente:<br>"
            "&nbsp;&nbsp;&nbsp;&nbsp;<b>I₁ = I₀ / 2</b><br>"
            "Após P₁, a radiação emerge linearmente polarizada paralelamente ao eixo de transmissão φ₁.<br><br>"
            "• <b>Luz Inicialmente Polarizada:</b> Se o feixe incidente já possui polarização linear orientada em φ₀:<br>"
            "&nbsp;&nbsp;&nbsp;&nbsp;<b>I₁ = I₀ · cos²(φ₁ - φ₀)</b><br><br>"
            "• <b>Estágios Subsequentes (k > 1):</b> A intensidade transmitida por cada polarizador seguinte obedece à "
            "Lei de Malus em relação ao estágio imediatamente anterior:<br>"
            "&nbsp;&nbsp;&nbsp;&nbsp;<b>I_k = I_{k-1} · cos²(φ_k - φ_{k-1})</b><br><br>"
            "• <b>Amplitude do Campo Elétrico:</b> Sendo a intensidade proporcional ao quadrado da amplitude do campo (I ∝ E²), "
            "a amplitude relativa transmitida é dada por:<br>"
            "&nbsp;&nbsp;&nbsp;&nbsp;<b>E_k / E₀ = √(I_k / I₀)</b>"
        )
        text_3.setTextFormat(Qt.TextFormat.RichText)
        text_3.setWordWrap(True)
        text_3.setProperty("class", "text-secondary")
        card_3.add_widget(text_3)
        layout.addWidget(card_3)

        # 4: Hipóteses
        card_4 = ParameterCard("4. Hipóteses Físicas e Limites de Validade")
        text_4 = QLabel(
            "• <b>Regime Escalar de Fraunhofer:</b> A simulação assume anteparo no campo distante em relação à abertura "
            "(condição suficiente conservadora: D >> L²/λ, com L = a para uma fenda e L = d + a para duas, "
            "na direção transversal modelada). A extensão total da abertura importa, inclusive a separação das fendas. "
            "O programa assume esse regime; não recebe D nem verifica uma distância experimental. "
            "Efeitos de campo próximo (Fresnel) não são modelados.<br>"
            "• <b>Monocromaticidade e Coerência:</b> A fonte é tratada como estritamente monocromática e espacialmente coerente.<br>"
            "• <b>Polarizadores Ideais:</b> Desconsideram-se reflexões de Fresnel nas interfaces, absorção parasita em materiais e "
            "dispersão cromática nos cristais/polímeros.<br>"
            "• <b>Colorimetria:</b> O comprimento de onda (400 a 700 nm) é mapeado em RGB aproximado para visualização didática em monitores padrão sRGB."
        )
        text_4.setTextFormat(Qt.TextFormat.RichText)
        text_4.setWordWrap(True)
        text_4.setProperty("class", "text-secondary")
        card_4.add_widget(text_4)
        layout.addWidget(card_4)

        scroll.setWidget(container)
        outer_layout.addWidget(scroll)
