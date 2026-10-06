
from typing import Sequence
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QHBoxLayout,
    QPushButton,
    QWidget,
)


class SegmentedControl(QWidget):

    selectionChanged = Signal(int, str)

    def __init__(
        self,
        options: Sequence[str],
        default_index: int = 0,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._buttons: list[QPushButton] = []
        self._group = QButtonGroup(self)
        self._group.setExclusive(True)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        for index, text in enumerate(options):
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setProperty("class", "segmented-btn")
            if index == default_index:
                btn.setChecked(True)
            self._group.addButton(btn, index)
            layout.addWidget(btn)
            self._buttons.append(btn)

        self._group.idClicked.connect(self._on_button_clicked)

    def _on_button_clicked(self, btn_id: int) -> None:
        if 0 <= btn_id < len(self._buttons):
            text = self._buttons[btn_id].text()
            self.selectionChanged.emit(btn_id, text)

    def selected_index(self) -> int:
        return self._group.checkedId()

    def set_selected_index(self, index: int) -> None:
        if 0 <= index < len(self._buttons):
            self._buttons[index].setChecked(True)
            self.selectionChanged.emit(index, self._buttons[index].text())
