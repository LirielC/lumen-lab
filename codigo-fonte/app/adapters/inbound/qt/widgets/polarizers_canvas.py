

import math
from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPen,
)
from PySide6.QtWidgets import QWidget
from app.core.application.dto.responses import PolarizationResponse
from app.core.utils.formatting import format_intensity, format_ratio_percent


class PolarizersCanvas(QWidget):
    

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMinimumHeight(240)
        self._response: PolarizationResponse | None = None

    def update_simulation(self, response: PolarizationResponse) -> None:
        
        self._response = response
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()

        
        painter.fillRect(0, 0, width, height, QColor("#131A2B"))

        
        painter.setPen(QPen(QColor("#2A3550"), 1))
        painter.drawRoundedRect(0, 0, width - 1, height - 1, 10, 10)

        if self._response is None:
            painter.setPen(QColor("#AEB8CF"))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Aguardando simulação...")
            return

        resp = self._response
        base_color = QColor(resp.beam_color_hex)
        cy = height * 0.52
        num_stages = len(resp.stages)

        
        rail_y = height - 25.0
        painter.setPen(QPen(QColor("#2A3550"), 3))
        painter.drawLine(QPointF(20, rail_y), QPointF(width - 20, rail_y))

        
        source_x = 40.0
        source_rect = QRectF(source_x - 25, cy - 35, 30, 70)
        painter.setBrush(QBrush(QColor("#1A2338")))
        painter.setPen(QPen(QColor("#3B4A70"), 2))
        painter.drawRoundedRect(source_rect, 6, 6)

        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        painter.setPen(base_color)
        painter.drawText(QRectF(10, cy - 55, 70, 20), Qt.AlignmentFlag.AlignCenter, f"{resp.wavelength_nm:.0f} nm")

        
        start_x = 180.0
        end_x = width - 170.0
        if num_stages == 1:
            polarizer_xs = [(start_x + end_x) / 2]
        else:
            spacing = (end_x - start_x) / (num_stages - 1)
            polarizer_xs = [start_x + i * spacing for i in range(num_stages)]

        disc_radius = 42.0

        
        first_p_x = polarizer_xs[0]
        self._draw_beam_segment(
            painter,
            source_x + 5,
            first_p_x - disc_radius,
            cy,
            base_color,
            intensity_ratio=1.0 if resp.initial_intensity > 0 else 0.0,
        )

        
        in_field_x = (source_x + 5 + first_p_x - disc_radius) / 2
        if resp.initial_intensity == 0:
            self._draw_field_vector(painter, in_field_x, cy, None, 0.0, base_color)
        elif not resp.initially_polarized:
            self._draw_unpolarized_vectors(painter, in_field_x, cy, base_color)
            painter.setFont(QFont("Segoe UI", 8))
            painter.setPen(QColor("#AEB8CF"))
            painter.drawText(QRectF(in_field_x - 60, cy + 42, 120, 30), Qt.AlignmentFlag.AlignCenter, "Não polarizada")
        else:
            angle_rad = math.radians(resp.initial_angle_deg or 0.0)
            self._draw_field_vector(painter, in_field_x, cy, angle_rad, 1.0, base_color)
            painter.setFont(QFont("Segoe UI", 8))
            painter.setPen(QColor("#AEB8CF"))
            painter.drawText(QRectF(in_field_x - 50, cy + 42, 100, 30), Qt.AlignmentFlag.AlignCenter, f"φ₀ = {resp.initial_angle_deg:.0f}°")

        
        for i, (p_x, stage) in enumerate(zip(polarizer_xs, resp.stages)):
            
            self._draw_polarizer_disc(painter, p_x, cy, disc_radius, stage.axis_angle_deg, stage.index)

            
            next_x = polarizer_xs[i + 1] - disc_radius if i + 1 < num_stages else width - 25.0
            beam_start_x = p_x + disc_radius

            
            int_ratio = stage.cumulative_transmission_pct / 100.0
            self._draw_beam_segment(painter, beam_start_x, next_x, cy, base_color, int_ratio)

            
            field_x = (beam_start_x + next_x) / 2
            field_rad = (
                math.radians(stage.field_direction_deg)
                if stage.field_direction_deg is not None
                else None
            )
            self._draw_field_vector(
                painter,
                field_x,
                cy,
                field_rad,
                stage.relative_field_amplitude,
                base_color,
            )

            
            painter.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
            painter.setPen(QColor("#F4F7FF"))
            trans_text = f"T = {format_ratio_percent(stage.cumulative_transmission_pct / 100)}" if resp.initial_intensity > 0 else "Fonte sem luz"
            label_x = max(8.0, min(field_x - 75, width - 158.0))
            painter.drawText(QRectF(label_x, cy + 42, 150, 20), Qt.AlignmentFlag.AlignCenter, trans_text)

    def _draw_beam_segment(
        self,
        painter: QPainter,
        x1: float,
        x2: float,
        y: float,
        color: QColor,
        intensity_ratio: float,
    ) -> None:
        
        if x2 <= x1:
            return

        beam_h = 18.0
        rect = QRectF(x1, y - beam_h / 2, x2 - x1, beam_h)

        if intensity_ratio <= 1e-4:
            
            painter.setPen(QPen(QColor("#1A2338"), 2, Qt.PenStyle.DotLine))
            painter.drawLine(QPointF(x1, y), QPointF(x2, y))
            return

        
        alpha = int(220 * (intensity_ratio ** 0.5))
        alpha = max(15, min(255, alpha))

        grad = QLinearGradient(0, y - beam_h / 2, 0, y + beam_h / 2)
        c_edge = QColor(color)
        c_edge.setAlpha(int(alpha * 0.2))
        c_center = QColor(color)
        c_center.setAlpha(alpha)

        grad.setColorAt(0.0, c_edge)
        grad.setColorAt(0.5, c_center)
        grad.setColorAt(1.0, c_edge)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad))
        painter.drawRect(rect)

        
        core_color = QColor("#FFFFFF")
        core_color.setAlpha(int(alpha * 0.7))
        painter.setPen(QPen(core_color, 1.5))
        painter.drawLine(QPointF(x1, y), QPointF(x2, y))

    def _draw_unpolarized_vectors(
        self,
        painter: QPainter,
        cx: float,
        cy: float,
        color: QColor,
    ) -> None:
        
        length = 26.0
        vec_color = QColor(color)
        vec_color.setAlpha(200)
        painter.setPen(QPen(vec_color, 1.5))

        
        for deg in (0, 45, 90, 135):
            rad = math.radians(deg)
            dx = math.cos(rad) * length
            dy = -math.sin(rad) * length
            painter.drawLine(QPointF(cx - dx, cy - dy), QPointF(cx + dx, cy + dy))
            
            painter.setBrush(QBrush(vec_color))
            painter.drawEllipse(QPointF(cx + dx, cy + dy), 2, 2)
            painter.drawEllipse(QPointF(cx - dx, cy - dy), 2, 2)

    def _draw_field_vector(
        self,
        painter: QPainter,
        cx: float,
        cy: float,
        angle_rad: float | None,
        amplitude_ratio: float,
        color: QColor,
    ) -> None:
        
        if amplitude_ratio == 0:
            painter.setFont(QFont("Segoe UI", 8))
            painter.setPen(QPen(QColor("#AEB8CF"), 1))
            painter.drawText(QRectF(cx - 35, cy - 10, 70, 20), Qt.AlignmentFlag.AlignCenter, "E = 0")
            return

        if amplitude_ratio * 34.0 < 2.0:
            painter.setFont(QFont("Segoe UI", 8))
            painter.setPen(QColor("#AEB8CF"))
            label_x = max(8.0, min(cx - 75, self.width() - 158.0))
            painter.drawText(QRectF(label_x, cy - 30, 150, 40), Qt.AlignmentFlag.AlignCenter,
                             f"E/E₀ = {format_intensity(amplitude_ratio)}\nabaixo da escala visual")
            return

        assert angle_rad is not None

        max_len = 34.0
        length = max_len * amplitude_ratio
        dx = math.cos(angle_rad) * length
        dy = -math.sin(angle_rad) * length

        vec_color = QColor("#FFFFFF")
        painter.setPen(QPen(vec_color, 2.5))
        painter.drawLine(QPointF(cx - dx, cy - dy), QPointF(cx + dx, cy + dy))

        
        head = min(6.0, length * 0.4)
        ux, uy = math.cos(angle_rad), -math.sin(angle_rad)
        for sign in (-1, 1):
            tip = QPointF(cx + sign * dx, cy + sign * dy)
            for side in (-1, 1):
                wing = QPointF(tip.x() - sign * head * ux - side * head * 0.5 * uy,
                               tip.y() - sign * head * uy + side * head * 0.5 * ux)
                painter.drawLine(tip, wing)

    def _draw_polarizer_disc(
        self,
        painter: QPainter,
        cx: float,
        cy: float,
        radius: float,
        axis_angle_deg: float,
        stage_num: int,
    ) -> None:
        
        
        post_bottom = self.height() - 25.0
        painter.setPen(QPen(QColor("#2A3550"), 4))
        painter.drawLine(QPointF(cx, cy + radius), QPointF(cx, post_bottom))

        
        painter.setPen(QPen(QColor("#7C8CFF"), 2))
        painter.setBrush(QBrush(QColor("#1A2338")))
        painter.drawEllipse(QPointF(cx, cy), radius, radius)

        
        axis_rad = math.radians(axis_angle_deg)
        dx = math.cos(axis_rad) * (radius - 4)
        dy = -math.sin(axis_rad) * (radius - 4)

        painter.setPen(QPen(QColor("#43D19E"), 2.5))
        painter.drawLine(QPointF(cx - dx, cy - dy), QPointF(cx + dx, cy + dy))

        
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        painter.setPen(QColor("#7C8CFF"))
        painter.drawText(QRectF(cx - 30, cy - radius - 24, 60, 20), Qt.AlignmentFlag.AlignCenter, f"P{stage_num}")

        
        painter.setFont(QFont("Segoe UI", 8))
        painter.setPen(QColor("#AEB8CF"))
        painter.drawText(QRectF(cx - 35, cy - radius - 10, 70, 16), Qt.AlignmentFlag.AlignCenter, f"{axis_angle_deg:.0f}°")
