from collections.abc import Callable
import math

from PySide6.QtCore import QPointF, QRectF, QSize, Qt, Signal
from PySide6.QtGui import QColor, QIcon, QLinearGradient, QPainter, QPen, QRadialGradient
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QScrollArea, QSizePolicy, QVBoxLayout, QWidget

from app.adapters.inbound.qt.styles.icons import scientific_icon
from app.adapters.outbound.resources.resource_resolver import get_resource_path


class ModulePreview(QWidget):

    def __init__(self, kind: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._kind = kind
        self.setFixedSize(210, 150)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#07101F"))
        if self._kind == "slits":
            self._paint_slits(painter)
        else:
            self._paint_polarizers(painter)

    def _paint_slits(self, painter: QPainter) -> None:
        center = self.width() / 2
        baseline = self.height() - 12
        for offset in range(-96, 97, 4):
            intensity = (1 / (1 + (offset / 12) ** 2)) * (0.35 + 0.65 * abs(math.cos(offset / 6)))
            height = 96 * intensity
            gradient = QLinearGradient(0, baseline, 0, baseline - height)
            gradient.setColorAt(0, QColor(18, 76, 220, 70))
            gradient.setColorAt(1, QColor(37, 112, 255, 245))
            painter.setPen(QPen(gradient, 3))
            painter.drawLine(QPointF(center + offset, baseline), QPointF(center + offset, baseline - height))

    def _paint_polarizers(self, painter: QPainter) -> None:
        beam = QLinearGradient(8, 0, self.width() - 8, 0)
        beam.setColorAt(0, QColor(255, 45, 63, 40))
        beam.setColorAt(0.5, QColor(255, 58, 75, 230))
        beam.setColorAt(1, QColor(255, 45, 63, 70))
        painter.setPen(QPen(beam, 6, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(QPointF(8, 70), QPointF(202, 70))
        for x, angle in ((62, 25), (112, -30), (164, 10)):
            painter.setBrush(QColor(130, 150, 178, 35))
            painter.setPen(QPen(QColor(174, 190, 215, 150), 3))
            painter.drawEllipse(QPointF(x, 70), 18, 45)
            painter.save()
            painter.translate(x, 70)
            painter.rotate(angle)
            painter.setPen(QPen(QColor(215, 225, 240, 175), 2))
            painter.drawLine(QPointF(0, -35), QPointF(0, 35))
            painter.restore()
        glow = QRadialGradient(QPointF(196, 70), 18)
        glow.setColorAt(0, QColor(255, 245, 245, 255))
        glow.setColorAt(1, QColor(255, 50, 65, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(glow)
        painter.drawEllipse(QPointF(196, 70), 18, 18)


class HomePage(QWidget):

    openInterferenceRequested = Signal()
    openPolarizationRequested = Signal()
    openTheoryRequested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(12, 10, 12, 12)
        root_layout.setSpacing(0)
        tab = self._label("Início", "home-page-tab")
        tab.setFixedWidth(94)
        tab.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root_layout.addWidget(tab, alignment=Qt.AlignmentFlag.AlignLeft)

        panel = QFrame()
        panel.setProperty("class", "home-page-panel")
        panel.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setWidget(panel)
        root_layout.addWidget(scroll_area)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(28, 20, 28, 20)
        layout.setSpacing(14)

        heading = QHBoxLayout()
        emblem = QLabel()
        emblem.setPixmap(QIcon(str(get_resource_path("assets/icons/lumenlab.svg"))).pixmap(64, 64))
        emblem.setFixedSize(64, 64)
        heading.addWidget(emblem)
        heading.addSpacing(8)
        heading_text = QVBoxLayout()
        heading_text.setSpacing(2)
        heading_text.addWidget(self._label("LumenLab", "home-title"))
        heading_text.addWidget(self._label("Laboratório Computacional de Óptica", "home-subtitle"))
        heading.addLayout(heading_text, 1)
        layout.addLayout(heading)

        introduction = self._label(
            "Simule e explore fenômenos de interferência, difração e polarização da luz através de modelos analíticos e visualizações interativas.",
            "home-introduction",
        )
        introduction.setWordWrap(True)
        layout.addWidget(introduction)

        modules = QHBoxLayout()
        modules.setSpacing(14)
        modules.addWidget(
            self._module_card(
                kind="slits",
                title="Interferência e Difração",
                description="Simule o padrão de difração de Fraunhofer para fendas simples e duplas, e a interferência de Young. Ajuste os parâmetros e visualize a intensidade na tela.",
                topics=("Fenda simples (Fraunhofer)", "Fenda dupla", "Interferência de Young"),
                action=self.openInterferenceRequested.emit,
            ), 1
        )
        modules.addWidget(
            self._module_card(
                kind="polarizers",
                title="Polarização",
                description="Explore a transmissão de luz não polarizada ou polarizada através de até 3 polarizadores lineares ideais. Observe a Lei de Malus em cascata e a rotação do vetor de campo elétrico.",
                topics=("Lei de Malus", "Polarizadores ideais", "Eixos cruzados", "Cascata de polarizadores"),
                action=self.openPolarizationRequested.emit,
            ), 1
        )
        layout.addLayout(modules)

        information = QHBoxLayout()
        information.setSpacing(14)
        information.addWidget(
            self._information_card(
                "Conceitos abordados",
                "•  Óptica ondulatória\n•  Interferência\n•  Difração\n•  Polarização\n•  Modelos analíticos (SI)\n•  Visualização de resultados",
                icon="math-function",
            ), 1
        )
        information.addWidget(
            self._information_card(
                "Sistema de unidades",
                "Todas as grandezas são tratadas no Sistema Internacional (SI).\n\nComprimento:   metro (m)\nÂngulo:        radiano (rad)\nIntensidade:   normalizada (I/I₀)",
                monospace=True,
                icon="ruler-measure",
            ), 1
        )
        information.addWidget(
            self._information_card(
                "Comece por aqui",
                "1   Abra um dos módulos de simulação.\n2   Ajuste os parâmetros físicos.\n3   Observe a atualização automática.\n4   Compare gráficos e valores numéricos.\n5   Consulte as equações em Referência.",
                icon="list-numbers",
            ), 1
        )
        layout.addLayout(information)
        layout.addStretch()

    @staticmethod
    def _label(text: str, style_class: str) -> QLabel:
        label = QLabel(text)
        label.setProperty("class", style_class)
        label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        return label

    def _module_card(
        self,
        *,
        kind: str,
        title: str,
        description: str,
        topics: tuple[str, ...],
        action: Callable[[], None],
    ) -> QFrame:
        card = QFrame()
        card.setProperty("class", "home-module-card")
        card.setMinimumHeight(280)
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(18)
        preview = QVBoxLayout()
        preview.addWidget(ModulePreview(kind))
        caption = self._label("DIFRAÇÃO · INTERFERÊNCIA" if kind == "slits" else "EIXOS · TRANSMISSÃO", "home-science-caption")
        caption.setWordWrap(True)
        preview.addWidget(caption)
        preview.addStretch()
        card_layout.addLayout(preview)

        content = QVBoxLayout()
        content.setSpacing(7)
        content.addLayout(self._icon_heading(title, "wave-sine" if kind == "slits" else "arrows-move", "home-module-title"))
        description_label = self._label(description, "home-module-description")
        description_label.setWordWrap(True)
        description_label.setMinimumWidth(0)
        description_label.setMinimumHeight(78)
        content.addWidget(description_label)
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setProperty("class", "home-separator")
        content.addWidget(separator)
        content.addWidget(self._label("Modelos disponíveis:" if kind == "slits" else "Tópicos disponíveis:", "home-section-label"))
        topics_label = self._label("\n".join(f"•  {topic}" for topic in topics), "home-topic-list")
        topics_label.setMinimumWidth(0)
        topics_label.setMinimumHeight(72)
        content.addWidget(topics_label)
        content.addStretch()
        button = QPushButton("Abrir")
        button.setIcon(scientific_icon("arrow-right"))
        button.setIconSize(QSize(18, 18))
        button.setAccessibleName(f"Abrir {title}")
        button.setProperty("class", "home-module-cta")
        button.setFixedHeight(32)
        button.clicked.connect(action)
        content.addWidget(button, alignment=Qt.AlignmentFlag.AlignRight)
        card_layout.addLayout(content, stretch=1)
        return card

    def _icon_heading(self, title: str, icon: str, style_class: str) -> QHBoxLayout:
        row = QHBoxLayout()
        symbol = QLabel()
        symbol.setPixmap(scientific_icon(icon).pixmap(24, 24))
        symbol.setFixedSize(24, 24)
        row.addWidget(symbol)
        label = self._label(title, style_class)
        label.setWordWrap(True)
        row.addWidget(label, 1)
        return row

    def _information_card(self, title: str, content: str, monospace: bool = False, *, icon: str) -> QFrame:
        card = QFrame()
        card.setProperty("class", "home-info-card")
        card.setMinimumHeight(165)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 13, 16, 14)
        card_layout.setSpacing(9)
        card_layout.addLayout(self._icon_heading(title, icon, "home-info-title"))
        body = self._label(content, "home-info-mono" if monospace else "home-info-body")
        body.setWordWrap(True)
        body.setMinimumWidth(0)
        card_layout.addWidget(body)
        return card
