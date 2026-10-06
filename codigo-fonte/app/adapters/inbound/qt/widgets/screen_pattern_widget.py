

import math
import numpy as np
from numpy.typing import NDArray
from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import (
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPen,
)
from PySide6.QtWidgets import QWidget
from app.core.application.dto.responses import InterferenceResponse
from app.adapters.inbound.qt.plots.angular_view import angle_to_fraction, angular_view_limits, fraction_to_angle, pixel_mean_intensities


class ScreenPatternWidget(QWidget):
    






    angleSelected = Signal(float)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMinimumHeight(110)
        self.setMaximumHeight(160)
        self._response: InterferenceResponse | None = None
        self._angles: NDArray[np.float64] | None = None
        self._intensities: NDArray[np.float64] | None = None
        self._selected_angle_deg: float = 0.0
        self._beam_color = QColor("#FF3344")
        self._view_mode = "overview"
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.setToolTip("Arraste para selecionar θ.")
        self.setToolTipDuration(1500)

    def set_view_mode(self, mode: str) -> None:
        self._view_mode = mode
        self.update()

    def _limits(self) -> tuple[float, float]:
        if self._response is None:
            return -90.0, 90.0
        r = self._response
        return angular_view_limits(
            mode=self._view_mode, alpha_deg=r.incidence_angle_deg,
            wavelength_nm=r.wavelength_nm, slit_width_um=r.slit_width_um,
        )

    def update_simulation(self, response: InterferenceResponse) -> None:
        
        self._response = response
        self._angles = response.angles_deg
        self._intensities = response.normalized_intensity if response.initial_intensity > 0 else np.zeros_like(response.normalized_intensity)
        self._selected_angle_deg = response.selected_angle_deg
        self._beam_color = QColor(response.beam_color_hex)
        self.update()

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self._handle_mouse(event.position().x())

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        if event.buttons() & Qt.MouseButton.LeftButton:
            self._handle_mouse(event.position().x())

    def _handle_mouse(self, mouse_x: float) -> None:
        screen_left = 12.0
        screen_right = self.width() - 12.0
        screen_w = max(1.0, screen_right - screen_left)
        fraction = max(0.0, min(1.0, (mouse_x - screen_left) / screen_w))
        angle_min, angle_max = self._limits()
        clicked_angle = fraction_to_angle(fraction, (angle_min, angle_max))
        self.angleSelected.emit(clicked_angle)

    def paintEvent(self, event) -> None:  # noqa: N802
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()

        
        painter.fillRect(0, 0, width, height, QColor("#080D1A"))

        
        painter.setPen(QPen(QColor("#1E293B"), 1))
        painter.drawRoundedRect(0, 0, width - 1, height - 1, 6, 6)

        header_rect = QRectF(12, 6, width - 24, 16)
        painter.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))
        painter.setPen(QColor("#94A3B8"))
        mode = "visão completa" if self._view_mode == "overview" else "detalhe do padrão"
        painter.drawText(header_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, f"Mapa Angular de Intensidade — {mode}")

        if self._response is None or self._angles is None or self._intensities is None:
            painter.setPen(QColor("#64748B"))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Aguardando simulação...")
            return

        screen_left = 12.0
        screen_right = width - 12.0
        screen_top = 26.0
        screen_bottom = height - 22.0
        screen_w = screen_right - screen_left
        screen_h = screen_bottom - screen_top

        
        screen_rect = QRectF(screen_left, screen_top, screen_w, screen_h)
        painter.setPen(QPen(QColor("#334155"), 1))
        painter.setBrush(QColor("#030712"))
        painter.drawRoundedRect(screen_rect, 4, 4)

        
        cols = int(screen_w)
        if cols > 1 and len(self._angles) > 1:
            angle_min, angle_max = self._limits()
            col_intensities = pixel_mean_intensities(self._angles, self._intensities, (angle_min, angle_max), cols)

            
            cy = screen_top + screen_h / 2.0
            beam_half_h = screen_h * 0.45

            for c in range(cols):
                intensity = float(col_intensities[c])
                if intensity < 1e-4:
                    continue

                x_pos = screen_left + c
                
                perceptual_i = intensity ** 0.6
                alpha = int(255 * min(1.0, perceptual_i))

                col_color = QColor(self._beam_color)
                col_color.setAlpha(alpha)

                grad = QLinearGradient(x_pos, cy - beam_half_h, x_pos, cy + beam_half_h)
                c_edge = QColor(self._beam_color)
                c_edge.setAlpha(0)
                grad.setColorAt(0.0, c_edge)
                grad.setColorAt(0.2, col_color)
                grad.setColorAt(0.5, col_color)
                grad.setColorAt(0.8, col_color)
                grad.setColorAt(1.0, c_edge)

                painter.setPen(QPen(grad, 1.2))
                painter.drawLine(QPointF(x_pos, screen_top + 1), QPointF(x_pos, screen_bottom - 1))

        
        painter.setFont(QFont("Segoe UI", 7))
        angle_min, angle_max = self._limits()
        for deg in np.linspace(angle_min, angle_max, 7):
            frac = (deg - angle_min) / (angle_max - angle_min)
            tx = screen_left + frac * screen_w
            painter.setPen(QPen(QColor("#475569"), 1))
            painter.drawLine(QPointF(tx, screen_bottom), QPointF(tx, screen_bottom + 4))

            painter.setPen(QColor("#94A3B8"))
            lbl = f"{deg:+.2f}°" if self._view_mode != "overview" else f"{deg:+.0f}°"
            painter.drawText(QRectF(tx - 18, screen_bottom + 4, 36, 14), Qt.AlignmentFlag.AlignCenter, lbl)

        
        sel_deg = self._selected_angle_deg
        sel_frac = angle_to_fraction(sel_deg, (angle_min, angle_max))
        sel_x = screen_left + sel_frac * screen_w
        if 0.0 <= sel_frac <= 1.0:
            painter.setPen(QPen(QColor("#FFFFFF"), 1.2, Qt.PenStyle.DashLine))
            painter.drawLine(QPointF(sel_x, screen_top + 2), QPointF(sel_x, screen_bottom - 2))
            painter.setBrush(QColor("#EF4444"))
            painter.drawPolygon([
                QPointF(sel_x, screen_top + 7),
                QPointF(sel_x - 4, screen_top + 1),
                QPointF(sel_x + 4, screen_top + 1),
            ])
        painter.setPen(QColor("#FFFFFF"))
        suffix = " • fora do zoom" if not 0.0 <= sel_frac <= 1.0 else ""
        painter.drawText(QRectF(width - 190, 6, 178, 16), Qt.AlignmentFlag.AlignRight, f"θ = {sel_deg:+.1f}°{suffix}")
