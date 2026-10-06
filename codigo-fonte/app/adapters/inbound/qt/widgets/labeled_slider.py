
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QApplication,
    QDoubleSpinBox,
    QAbstractSpinBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QSlider,
    QWidget,
)

from app.adapters.inbound.qt.styles.theme import ThemePalette, current_palette


class LabeledSlider(QWidget):
    

    valueChanged = Signal(float)

    def __init__(
        self,
        label: str,
        min_value: float,
        max_value: float,
        default_value: float,
        step: float = 1.0,
        decimals: int = 1,
        unit: str = "",
        show_color_swatch: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._min = min_value
        self._max = max_value
        self._step = step
        self._decimals = decimals
        self._multiplier = 10**decimals
        self._is_updating = False
        self._swatch_color = "transparent"

        layout = QGridLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setHorizontalSpacing(7)
        layout.setVerticalSpacing(3)

        self._label = QLabel(label)
        self._label.setProperty("class", "parameter-label")
        self._label.setMinimumWidth(92)
        layout.addWidget(self._label, 0, 0, 1, 5)

        self._slider = QSlider(Qt.Orientation.Horizontal)
        self._slider.setRange(
            int(round(min_value * self._multiplier)),
            int(round(max_value * self._multiplier)),
        )
        self._slider.setSingleStep(int(round(step * self._multiplier)))
        self._slider.setValue(int(round(default_value * self._multiplier)))
        layout.addWidget(self._slider, 1, 0, 1, 2)

        if show_color_swatch:
            self._color_swatch = QFrame()
            self._color_swatch.setFixedSize(16, 16)
            self._style_swatch(current_palette(QApplication.instance()))
            layout.addWidget(self._color_swatch, 1, 2)
        else:
            self._color_swatch = None

        self._spinbox = QDoubleSpinBox()
        self._spinbox.setRange(min_value, max_value)
        self._spinbox.setSingleStep(step)
        self._spinbox.setDecimals(decimals)
        self._spinbox.setValue(default_value)
        self._spinbox.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.PlusMinus)
        self._spinbox.setProperty("class", "numeric-input")
        self._spinbox.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._spinbox.setFixedWidth(82)
        layout.addWidget(self._spinbox, 1, 3)
        self._spinbox.setAccessibleName(label)
        self._slider.setAccessibleName(label)

        self._unit_label = None
        if unit:
            self._unit_label = QLabel(unit)
            self._unit_label.setProperty("class", "unit-label")
            self._unit_label.setFixedWidth(24)
            layout.addWidget(self._unit_label, 1, 4)

        layout.setColumnStretch(1, 1)

        self._slider.valueChanged.connect(self._on_slider_changed)
        self._spinbox.valueChanged.connect(self._on_spinbox_changed)

    def _on_slider_changed(self, int_val: int) -> None:
        if self._is_updating:
            return
        self._is_updating = True
        float_val = int_val / self._multiplier
        self._spinbox.setValue(float_val)
        self._is_updating = False
        self.valueChanged.emit(float_val)

    def _on_spinbox_changed(self, float_val: float) -> None:
        if self._is_updating:
            return
        self._is_updating = True
        self._slider.setValue(int(round(float_val * self._multiplier)))
        self._is_updating = False
        self.valueChanged.emit(float_val)

    def value(self) -> float:
        return self._spinbox.value()

    def set_value(self, val: float) -> None:
        clamped = max(self._min, min(self._max, val))
        self._is_updating = True
        self._spinbox.setValue(clamped)
        self._slider.setValue(int(round(clamped * self._multiplier)))
        self._is_updating = False
        self.valueChanged.emit(clamped)

    def set_swatch_color(self, hex_color: str) -> None:
        self._swatch_color = hex_color
        if self._color_swatch is not None:
            self._style_swatch(current_palette(QApplication.instance()))

    def apply_theme(self, palette: ThemePalette) -> None:
        self._style_swatch(palette)

    def _style_swatch(self, palette: ThemePalette) -> None:
        if self._color_swatch is not None:
            self._color_swatch.setStyleSheet(
                f"background-color: {self._swatch_color}; border-radius: 2px; border: 1px solid {palette.border_strong};"
            )
