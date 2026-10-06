
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)


class ResultCard(QFrame):

    def __init__(
        self,
        title: str,
        initial_value: str = "—",
        unit: str = "",
        subtitle: str = "",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setProperty("class", "ResultCard")
        self.setObjectName("ResultCard")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(4)

        self._title_label = QLabel(title)
        self._title_label.setProperty("class", "text-secondary")
        layout.addWidget(self._title_label)

        val_row = QHBoxLayout()
        val_row.setSpacing(6)

        self._value_label = QLabel(initial_value)
        self._value_label.setProperty("class", "metric-value")
        val_row.addWidget(self._value_label)

        if unit:
            self._unit_label = QLabel(unit)
            self._unit_label.setProperty("class", "metric-unit")
            val_row.addWidget(self._unit_label)
        else:
            self._unit_label = None

        val_row.addStretch()
        layout.addLayout(val_row)

        self._subtitle_label = QLabel(subtitle)
        self._subtitle_label.setProperty("class", "text-muted")
        self._subtitle_label.setWordWrap(True)
        layout.addWidget(self._subtitle_label)

    def set_value(self, value: str, subtitle: str | None = None) -> None:
        self._value_label.setText(value)
        if subtitle is not None:
            self._subtitle_label.setText(subtitle)
