
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)


class ParameterCard(QFrame):

    def __init__(
        self,
        title: str,
        subtitle: str | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setProperty("class", "ParameterCard")
        self.setObjectName("ParameterCard")

        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(16, 14, 16, 16)
        self._main_layout.setSpacing(12)

        header_layout = QVBoxLayout()
        header_layout.setSpacing(2)

        title_label = QLabel(title)
        title_label.setProperty("class", "heading-3")
        header_layout.addWidget(title_label)

        if subtitle:
            sub_label = QLabel(subtitle)
            sub_label.setProperty("class", "text-secondary")
            sub_label.setWordWrap(True)
            header_layout.addWidget(sub_label)

        self._main_layout.addLayout(header_layout)

        self._content_layout = QVBoxLayout()
        self._content_layout.setSpacing(10)
        self._main_layout.addLayout(self._content_layout)

    @property
    def content_layout(self) -> QVBoxLayout:
        return self._content_layout

    def add_widget(self, widget: QWidget) -> None:
        self._content_layout.addWidget(widget)
