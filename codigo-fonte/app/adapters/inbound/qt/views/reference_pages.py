from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from app.adapters.inbound.qt.widgets.parameter_card import ParameterCard


class ReferencePage(QWidget):

    def __init__(self, title: str, introduction: str, sections: tuple[tuple[str, str], ...]) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(12)
        heading = QLabel(title)
        heading.setProperty("class", "heading-1")
        layout.addWidget(heading)
        summary = QLabel(introduction)
        summary.setProperty("class", "text-secondary")
        summary.setWordWrap(True)
        layout.addWidget(summary)
        for section_title, text in sections:
            card = ParameterCard(section_title)
            body = QLabel(text)
            body.setProperty("class", "text-secondary")
            body.setTextFormat(Qt.TextFormat.RichText)
            body.setWordWrap(True)
            card.add_widget(body)
            layout.addWidget(card)
        layout.addStretch()


def create_examples_page() -> ReferencePage:
    return ReferencePage(
        "Exemplos",
        "Configurações didáticas disponíveis nos seletores de preset de cada simulação.",
        (
            ("Interferência e difração", "<b>Uma fenda:</b> envelope de Fraunhofer.<br><b>Duas fendas:</b> franjas sob o envelope.<br><b>Incidência oblíqua:</b> deslocamento angular do máximo."),
            ("Polarização", "<b>0°–45°–90°:</b> transmissão em três etapas.<br><b>Eixos paralelos:</b> sem perda adicional ideal.<br><b>Eixos cruzados:</b> transmissão final nula."),
        ),
    )


def create_units_page() -> ReferencePage:
    return ReferencePage(
        "Unidades e constantes",
        "A interface converte as entradas para o Sistema Internacional antes dos cálculos.",
        (
            ("Unidades", "Comprimento de onda: nanômetro (nm), convertido para metro (m).<br>Largura e separação: micrômetro (µm), convertido para metro (m).<br>Ângulos: grau (°), convertido para radiano (rad).<br>Intensidade: unidade relativa."),
            ("Faixas e referência", "Comprimento de onda permitido: 400 a 700 nm.<br>Comprimento de onda padrão: 633 nm.<br>π = 3,141592653589793."),
        ),
    )
