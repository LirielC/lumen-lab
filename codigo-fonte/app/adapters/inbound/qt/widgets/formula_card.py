
from html import escape

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLayout,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
    QApplication,
    QTextBrowser,
)
from app.adapters.inbound.qt.styles.theme import current_palette
from app.adapters.inbound.qt.widgets.math_document import populate_math_document
from app.core.application.dto.responses import InterferenceResponse, PolarizationResponse


class FormulaCard(QFrame):

    def __init__(
        self,
        title: str = "Fundamentação & Equação Ativa",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._response = None
        self._document_width = 0
        self.setObjectName("scientificModelPanel")
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)

        layout = QVBoxLayout(self)
        layout.setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        header_row = QHBoxLayout()

        self._title_label = QLabel(title)
        self._title_label.setWordWrap(True)
        self._title_label.setProperty("class", "formula-title")
        header_row.addWidget(self._title_label)

        header_row.addStretch()

        self._toggle_btn = QPushButton("▾")
        self._toggle_btn.setObjectName("formulaToggle")
        self._toggle_btn.setToolTip("Recolher modelo matemático")
        self._toggle_btn.setAccessibleName("Recolher modelo matemático")
        self._toggle_btn.setFixedSize(24, 22)
        self._toggle_btn.clicked.connect(self._toggle_expanded)
        header_row.addWidget(self._toggle_btn)

        layout.addLayout(header_row)

        self._content_widget = QWidget()
        content_layout = QVBoxLayout(self._content_widget)
        content_layout.setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)
        content_layout.setContentsMargins(0, 4, 0, 0)
        content_layout.setSpacing(6)

        self._text_label = QTextBrowser()
        self._text_label.setFrameShape(QFrame.Shape.NoFrame)
        self._text_label.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._text_label.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._text_label.document().setDocumentMargin(0)
        self._text_label.document().documentLayout().documentSizeChanged.connect(self._fit_document)
        self._text_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self._text_label.setProperty("class", "formula-body")
        self._text_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        content_layout.addWidget(self._text_label)

        layout.addWidget(self._content_widget)

    def _fit_document(self, size) -> None:
        self._text_label.setFixedHeight(int(size.height()) + 8)
        self._text_label.verticalScrollBar().setValue(0)

    def set_response(self, response: InterferenceResponse | PolarizationResponse) -> None:
        
        self._response = response
        self._text_label.setAccessibleDescription(response.formula_text)
        self._render_response()

    def _render_response(self) -> None:
        width = max(180, self._text_label.viewport().width())
        self._document_width = width
        document = self._text_label.document()
        populate_math_document(document, self._response, current_palette(QApplication.instance()), width)
        document.setTextWidth(width)
        self._fit_document(document.size())
        self._text_label.verticalScrollBar().setValue(0)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if self._response is not None and self._text_label.viewport().width() != self._document_width:
            self._render_response()

    def set_content(self, text: str) -> None:
        
        self._response = None
        palette = current_palette(QApplication.instance())
        paragraphs = []
        for block in text.split("\n\n"):
            lines = []
            for line in block.splitlines():
                content = escape(line.strip())
                if line.strip().endswith(":"):
                    content = f'<b style="color:{palette.accent}">{content}</b>'
                elif line.startswith("  ") and not line.strip().startswith("•"):
                    content = f'<span style="font-family:Cambria; font-size:14px; color:{palette.text_primary}">{content}</span>'
                lines.append(content)
            paragraphs.append('<p style="margin-top:0; margin-bottom:14px;">' + '<br>'.join(lines) + '</p>')
        self._text_label.setHtml("".join(paragraphs))
        self._text_label.document().setTextWidth(max(180, self._text_label.viewport().width()))
        self._fit_document(self._text_label.document().size())

    def _toggle_expanded(self) -> None:
        is_visible = not self._content_widget.isHidden()
        self._content_widget.setVisible(not is_visible)
        self._toggle_btn.setText("▸" if is_visible else "▾")
        self._toggle_btn.setToolTip("Expandir modelo matemático" if is_visible else "Recolher modelo matemático")
        self._toggle_btn.setAccessibleName(self._toggle_btn.toolTip())
