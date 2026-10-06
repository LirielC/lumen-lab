

import math
import numpy as np
from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPen,
    QRadialGradient,
)
from PySide6.QtWidgets import QWidget
from app.core.application.dto.responses import InterferenceResponse
from app.adapters.inbound.qt.plots.angular_view import angle_to_fraction, angular_view_limits, fraction_to_angle


def observation_ray_endpoint(
    theta_deg: float,
    origin_x: float,
    screen_x: float,
    center_y: float,
    top_y: float,
    bottom_y: float,
) -> tuple[float, float, bool]:
    




    theta = math.radians(theta_deg)
    dx = max(0.0, math.cos(theta))
    dy = -math.sin(theta)
    t_screen = (screen_x - origin_x) / dx if dx > 1e-12 else math.inf
    if dy < -1e-12:
        t_boundary = (top_y - center_y) / dy
    elif dy > 1e-12:
        t_boundary = (bottom_y - center_y) / dy
    else:
        t_boundary = math.inf
    reaches_screen = t_screen <= t_boundary
    t = t_screen if reaches_screen else t_boundary
    return origin_x + t * dx, center_y + t * dy, reaches_screen


def incident_ray_start_y(alpha_deg: float, start_x: float, slit_x: float, slit_y: float) -> float:
    
    return slit_y + (slit_x - start_x) * math.tan(math.radians(alpha_deg))


class SlitsCanvas(QWidget):
    

    angleSelected = Signal(float)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMinimumHeight(380)
        self._response: InterferenceResponse | None = None
        self._view_mode = "overview"
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.setToolTip("Arraste na escala para selecionar θ.")
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

    def _display_angle(self, physical_angle: float) -> float:
        angle_min, angle_max = self._limits()
        return -90.0 + 180.0 * angle_to_fraction(physical_angle, (angle_min, angle_max))

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self._handle_canvas_click(event.position().x(), event.position().y())

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        if event.buttons() & Qt.MouseButton.LeftButton:
            self._handle_canvas_click(event.position().x(), event.position().y())

    def _handle_canvas_click(self, x: float, y: float) -> None:
        cx = self.width() * 0.48
        cy = self.height() * 0.50
        if x > cx:
            dx = x - cx
            dy = cy - y  
            display_deg = math.degrees(math.atan2(dy, dx))
            angle_min, angle_max = self._limits()
            physical_deg = fraction_to_angle((display_deg + 90.0) / 180.0, (angle_min, angle_max))
            self.angleSelected.emit(physical_deg)

    def update_simulation(self, response: InterferenceResponse) -> None:
        
        self._response = response
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()

        
        painter.fillRect(0, 0, width, height, QColor("#080D1A"))

        
        painter.setPen(QPen(QColor("#1E293B"), 1))
        painter.drawRoundedRect(0, 0, width - 1, height - 1, 6, 6)

        
        painter.setPen(QPen(QColor("#101726"), 0.8, Qt.PenStyle.DotLine))
        grid_size = 28
        for gx in range(grid_size, width, grid_size):
            painter.drawLine(gx, 0, gx, height)
        for gy in range(grid_size, height, grid_size):
            painter.drawLine(0, gy, width, gy)

        
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        painter.setPen(QColor("#E2E8F0"))
        mode = "" if self._view_mode == "overview" else " — detalhe do padrão"
        painter.drawText(QRectF(16, 12, 300, 18), Qt.AlignmentFlag.AlignLeft, f"Bancada Óptica Vetorial{mode}")

        if self._response is None:
            painter.setPen(QColor("#64748B"))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Aguardando simulação...")
            return

        resp = self._response
        base_color = QColor(resp.beam_color_hex)
        alpha_deg = resp.incidence_angle_deg
        alpha_rad = math.radians(alpha_deg)
        theta_deg = resp.selected_angle_deg

        
        slit_x = width * 0.48
        slit_y = height * 0.50

        # -------------------------------------------------------------
        
        # -------------------------------------------------------------
        laser_w = 96.0
        laser_h = 56.0
        laser_x = max(18.0, slit_x - 180.0)
        beam_start_x = laser_x + laser_w + 12.0
        laser_cy = incident_ray_start_y(alpha_deg, beam_start_x, slit_x, slit_y)
        laser_cy = max(50.0, min(height - 50.0, laser_cy))

        
        painter.setPen(QPen(QColor("#94A3B8"), 1.2))
        painter.setBrush(QBrush(QColor("#0F172A")))
        painter.drawRect(QRectF(laser_x, laser_cy - laser_h / 2, laser_w, laser_h))

        
        nozzle_w = 12.0
        nozzle_h = 24.0
        painter.drawRect(QRectF(laser_x + laser_w, laser_cy - nozzle_h / 2, nozzle_w, nozzle_h))

        
        painter.setPen(QPen(QColor("#64748B"), 1))
        stand_x = laser_x + laser_w / 2
        painter.drawLine(QPointF(stand_x, laser_cy + laser_h / 2), QPointF(stand_x, height - 25))
        painter.drawRect(QRectF(stand_x - 16, height - 25, 32, 6))

        
        beam_start_x = laser_x + laser_w + nozzle_w
        beam_start_y = laser_cy

        beam_grad = QLinearGradient(beam_start_x, beam_start_y, slit_x, slit_y)
        c_glow = QColor(base_color)
        c_glow.setAlpha(220)
        c_soft = QColor(base_color)
        c_soft.setAlpha(80)
        beam_grad.setColorAt(0.0, c_glow)
        beam_grad.setColorAt(1.0, c_soft)

        
        painter.save()
        if resp.initial_intensity == 0:
            painter.setOpacity(0.0)
        painter.setPen(QPen(c_soft, 10, Qt.PenStyle.SolidLine, Qt.PenCapStyle.FlatCap))
        painter.drawLine(QPointF(beam_start_x, beam_start_y), QPointF(slit_x, slit_y))

        
        painter.setPen(QPen(base_color, 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.FlatCap))
        painter.drawLine(QPointF(beam_start_x, beam_start_y), QPointF(slit_x, slit_y))
        painter.restore()

        # -------------------------------------------------------------
        
        # -------------------------------------------------------------
        post_w = 10.0
        post_h = 170.0
        post_top = slit_y - post_h / 2

        
        painter.setPen(QPen(QColor("#94A3B8"), 1.2))
        painter.setBrush(QBrush(QColor("#0F172A")))
        painter.drawRect(QRectF(slit_x - post_w / 2, post_top, post_w, post_h))

        
        painter.setPen(QPen(QColor("#64748B"), 1.2))
        painter.drawRect(QRectF(slit_x - 16, post_top + post_h, 32, 28))
        painter.drawRect(QRectF(slit_x - 26, post_top + post_h + 28, 52, 6))

        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor("#F8FAFC")))
        if resp.slit_count == 1:
            painter.drawRect(QRectF(slit_x - 1, slit_y - 7, 2, 14))
        else:
            painter.drawRect(QRectF(slit_x - 1, slit_y - 9, 2, 7))
            painter.drawRect(QRectF(slit_x - 1, slit_y + 2, 2, 7))

        # -------------------------------------------------------------
        
        # -------------------------------------------------------------
        arc_radius = min(width - slit_x - 45.0, (height - 60.0) * 0.5)
        arc_radius = max(110.0, arc_radius)

        
        sim_angles = resp.angles_deg
        sim_intensities = resp.normalized_intensity if resp.initial_intensity > 0 else np.zeros_like(resp.normalized_intensity)

        
        angle_min, angle_max = self._limits()
        ray_angles_deg = np.linspace(angle_min, angle_max, min(181, max(61, width // 3)))
        for ang in ray_angles_deg:
            display_rad = math.radians(self._display_angle(float(ang)))
            rx = slit_x + arc_radius * math.cos(display_rad)
            ry = slit_y - arc_radius * math.sin(display_rad)

            
            intensity = float(np.interp(ang, sim_angles, sim_intensities))
            ray_alpha = int(220 * min(1.0, max(0.0, intensity)))
            if ray_alpha < 2:
                continue

            c_ray = QColor(base_color)
            c_ray.setAlpha(ray_alpha)
            painter.setPen(QPen(c_ray, 1.0))
            painter.drawLine(QPointF(slit_x, slit_y), QPointF(rx, ry))

        
        painter.setPen(QPen(QColor("#CBD5E1"), 1.4))
        arc_rect = QRectF(slit_x - arc_radius, slit_y - arc_radius, 2 * arc_radius, 2 * arc_radius)
        painter.drawArc(arc_rect, -90 * 16, 180 * 16)

        
        painter.setFont(QFont("Segoe UI", 7.5, QFont.Weight.DemiBold))
        for index, deg in enumerate(np.linspace(angle_min, angle_max, 13)):
            deg_rad = math.radians(-90.0 + index * 15.0)
            cos_a = math.cos(deg_rad)
            sin_a = math.sin(deg_rad)

            is_major = index % 2 == 0
            tick_len = 7.0 if is_major else 4.0

            x1 = slit_x + (arc_radius - 1) * cos_a
            y1 = slit_y - (arc_radius - 1) * sin_a
            x2 = slit_x + (arc_radius + tick_len) * cos_a
            y2 = slit_y - (arc_radius + tick_len) * sin_a

            painter.setPen(QPen(QColor("#E2E8F0"), 1.2 if is_major else 0.8))
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

            if is_major:
                lx = slit_x + (arc_radius + 16) * cos_a
                ly = slit_y - (arc_radius + 16) * sin_a
                lbl = f"{deg:+.2f}°" if self._view_mode != "overview" else f"{deg:+.0f}°"
                lbl_rect = QRectF(lx - 16, ly - 7, 32, 14)
                painter.setPen(QColor("#94A3B8"))
                painter.drawText(lbl_rect, Qt.AlignmentFlag.AlignCenter, lbl)

        # -------------------------------------------------------------
        
        # -------------------------------------------------------------
        selected_fraction = angle_to_fraction(theta_deg, (angle_min, angle_max))
        if 0.0 <= selected_fraction <= 1.0:
            sel_rad = math.radians(self._display_angle(theta_deg))
            sel_rx = slit_x + arc_radius * math.cos(sel_rad)
            sel_ry = slit_y - arc_radius * math.sin(sel_rad)
            painter.setPen(QPen(QColor("#FFFFFF"), 1.6, Qt.PenStyle.DashLine))
            painter.drawLine(QPointF(slit_x, slit_y), QPointF(sel_rx, sel_ry))
            painter.setPen(QPen(QColor("#FFFFFF"), 2))
            painter.setBrush(QBrush(QColor("#EF4444")))
            painter.drawEllipse(QPointF(sel_rx, sel_ry), 4, 4)
        painter.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        suffix = " • fora do zoom" if not 0.0 <= selected_fraction <= 1.0 else ""
        painter.setPen(QColor("#FFFFFF"))
        painter.drawText(QRectF(16, 31, width - 32, 18), Qt.AlignmentFlag.AlignLeft, f"θ = {theta_deg:+.1f}°{suffix}")
