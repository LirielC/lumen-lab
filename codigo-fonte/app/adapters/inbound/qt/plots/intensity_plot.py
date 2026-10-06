

from pathlib import Path
from app.version import VERSION
from app.adapters.outbound.export.atomic_file import atomic_output_path
import matplotlib
matplotlib.use("QtAgg")
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.ticker import AutoMinorLocator
import numpy as np
from numpy.typing import NDArray
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QApplication, QSizePolicy, QWidget

from app.adapters.inbound.qt.styles.theme import ThemePalette, current_palette
from app.adapters.inbound.qt.plots.angular_view import angular_view_limits
from app.core.utils.formatting import format_intensity


class IntensityPlotWidget(FigureCanvasQTAgg):
    

    angleSelected = Signal(float)

    def __init__(self, parent: QWidget | None = None) -> None:
        self.figure = Figure(figsize=(4.4, 3.2), dpi=100, layout="constrained")
        super().__init__(self.figure)
        self.setParent(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.updateGeometry()

        self.mpl_connect("button_press_event", self._on_canvas_click)
        self.mpl_connect("motion_notify_event", self._on_mouse_move)

        self.ax = self.figure.add_subplot(111)
        palette = current_palette(QApplication.instance())
        self._setup_axes(palette)

        
        (self._main_line,) = self.ax.plot(
            [],
            [],
            color=palette.accent,
            linewidth=1.8,
            label="Perfil I(θ)/I₀",
        )
        (self._envelope_line,) = self.ax.plot(
            [], [], color=palette.text_secondary, linewidth=1.0,
            linestyle="--", alpha=0.85, label="Envelope de difração",
        )
        self._envelope_line.set_visible(False)
        (self._reference_line,) = self.ax.plot(
            [], [], color=palette.text_primary, linewidth=1.3, linestyle="--",
            label="Referência",
        )
        self._reference_line.set_visible(False)
        self.experiment_metadata = ""
        self._marker_v_line = self.ax.axvline(
            0.0,
            color=palette.text_primary,
            linestyle="--",
            linewidth=1.2,
            alpha=0.8,
            label="Ângulo observado",
        )
        (self._marker_point,) = self.ax.plot(
            [0.0],
            [1.0],
            marker="o",
            markersize=6,
            color=palette.error,
            linestyle="None",
        )
        self._marker_label = self.ax.annotate(
            "θ = 0,0°", (0.0, 1.0), xytext=(8, -18), textcoords="offset points",
            color=palette.text_primary, fontsize=8,
        )

        self._view_mode: str = "overview"  
        self._current_alpha_deg: float = 0.0
        self._current_wavelength_nm: float = 550.0
        self._current_width_um: float = 20.0
        self._selected_angle_deg: float = 0.0
        self._angles = np.array([], dtype=np.float64)
        self._intensities = np.array([], dtype=np.float64)
        self._separation_um: float | None = None
        self._slit_count = 1
        self._show_envelope = False
        self._hover_label = self.ax.annotate(
            "", xy=(0, 0), xytext=(10, 12), textcoords="offset points",
            color=palette.text_primary, fontsize=8,
            bbox={"boxstyle": "square,pad=0.35", "fc": palette.surface_alt, "ec": palette.border_strong},
        )
        self._hover_label.set_visible(False)

    def _on_canvas_click(self, event) -> None:
        
        if event.inaxes == self.ax and event.xdata is not None:
            clamped_angle = float(max(-90.0, min(90.0, event.xdata)))
            self.angleSelected.emit(clamped_angle)

    def _on_mouse_move(self, event) -> None:
        if event.inaxes != self.ax or event.xdata is None or self._angles.size == 0:
            self._hover_label.set_visible(False)
            self.draw_idle()
            return
        index = int(np.abs(self._angles - event.xdata).argmin())
        theta = float(self._angles[index])
        intensity = float(self._intensities[index])
        order = "—"
        if self._slit_count == 2 and self._separation_um is not None:
            q = np.sin(np.radians(theta)) - np.sin(np.radians(self._current_alpha_deg))
            order = f"{self._separation_um * 1000.0 * q / self._current_wavelength_nm:.4f}"
        self._hover_label.xy = (theta, intensity)
        self._hover_label.set_text(f"θ = {theta:.2f}°\nPerfil normalizado = {format_intensity(intensity)}\ndq/λ = {order}")
        self._hover_label.set_visible(True)
        self.draw_idle()

    def _setup_axes(self, palette: ThemePalette) -> None:
        self.figure.patch.set_facecolor(palette.surface)
        self.ax.set_facecolor(palette.plot_bg)
        self.ax.tick_params(colors=palette.text_secondary, labelsize=9)
        for spine in self.ax.spines.values():
            spine.set_color(palette.border_strong)

        self.ax.xaxis.label.set_color(palette.text_secondary)
        self.ax.yaxis.label.set_color(palette.text_secondary)
        self.ax.title.set_color(palette.text_primary)

        self.ax.set_xlabel("θ (°)", fontsize=9)
        self.ax.set_ylabel("I(θ)/I₀", fontsize=9)
        self.ax.set_title("Distribuição angular de intensidade", fontsize=10, fontweight="semibold", loc="left", pad=15, color=palette.text_primary)

        self.ax.set_xlim(-90, 90)
        self.ax.set_ylim(-0.02, 1.05)
        self.ax.xaxis.set_minor_locator(AutoMinorLocator(3))
        self.ax.yaxis.set_minor_locator(AutoMinorLocator(2))
        self.ax.tick_params(which="minor", length=2, colors=palette.text_muted)
        self.ax.grid(True, which="major", linestyle="-", linewidth=0.45, color=palette.grid, alpha=0.7)

    def apply_theme(self, palette: ThemePalette) -> None:
        self._setup_axes(palette)
        self._marker_v_line.set_color(palette.text_primary)
        self._marker_point.set_color(palette.error)
        self._marker_label.set_color(palette.text_primary)
        self._envelope_line.set_color(palette.text_secondary)
        self.draw_idle()

    def set_view_mode(self, mode: str) -> None:
        
        self._view_mode = mode
        self._apply_axis_limits()
        self._update_marker_visibility()
        self.draw_idle()

    def _apply_axis_limits(self) -> None:
        
        self.ax.set_xlim(*angular_view_limits(
            mode=self._view_mode,
            alpha_deg=self._current_alpha_deg,
            wavelength_nm=self._current_wavelength_nm,
            slit_width_um=self._current_width_um,
        ))
        self.ax.set_ylim(-0.02, 1.05)

    def update_data(
        self,
        angles_deg: NDArray[np.float64],
        normalized_intensity: NDArray[np.float64],
        selected_angle_deg: float,
        selected_intensity: float,
        beam_color_hex: str,
        alpha_deg: float = 0.0,
        wavelength_nm: float = 550.0,
        width_um: float = 20.0,
        separation_um: float | None = None,
        slit_count: int = 1,
        initial_intensity: float = 1.0,
    ) -> None:
        
        self._current_alpha_deg = alpha_deg
        self._current_wavelength_nm = wavelength_nm
        self._current_width_um = width_um
        self._selected_angle_deg = selected_angle_deg
        self._angles = angles_deg
        self._intensities = normalized_intensity
        self._separation_um = separation_um
        self._slit_count = slit_count

        
        self._main_line.set_data(angles_deg, normalized_intensity)
        self._main_line.get_path().should_simplify = False
        self._main_line.set_color(beam_color_hex)
        self._main_line.set_label(f"Atual: {slit_count}F · λ={wavelength_nm:g} nm · a={width_um:g} µm")
        q = np.sin(np.radians(angles_deg)) - np.sin(np.radians(alpha_deg))
        envelope = np.sinc(width_um * 1000.0 * q / wavelength_nm) ** 2
        self._envelope_line.set_data(angles_deg, envelope)
        self._envelope_line.set_visible(self._show_envelope and slit_count == 2)
        separation = f" | d = {separation_um:.2f} µm" if separation_um is not None else ""
        profile_label = "Distribuição angular de intensidade" if initial_intensity > 0 else "I₀ = 0 · perfil normalizado teórico"
        self.ax.set_ylabel("I(θ)/I₀" if initial_intensity > 0 else "Perfil normalizado (teórico)")
        self.ax.set_title(
            f"{profile_label}\n"
            f"λ = {wavelength_nm:.0f} nm | a = {width_um:.2f} µm{separation}",
            fontsize=9, fontweight="normal", loc="left", pad=8,
            color=current_palette(QApplication.instance()).text_primary,
        )

        
        self._marker_v_line.set_xdata([selected_angle_deg, selected_angle_deg])
        self._marker_point.set_data([selected_angle_deg], [selected_intensity])
        self._marker_label.xy = (selected_angle_deg, selected_intensity)
        self._marker_label.set_text(f"θ = {selected_angle_deg:+.1f}°")
        self._marker_label.set_position((8, 12) if selected_intensity < 0.15 else (8, -18))

        
        self._apply_axis_limits()
        self._update_marker_visibility()
        self._update_legend()

        self.draw_idle()

    def set_reference(self, response) -> None:
        
        if response is None:
            self._reference_line.set_visible(False)
            self._reference_line.set_data([], [])
        else:
            self._reference_line.set_data(response.angles_deg.copy(), response.normalized_intensity.copy())
            self._reference_line.get_path().should_simplify = False
            self._reference_line.set_label(
                f"Referência: {response.slit_count}F · λ={response.wavelength_nm:g} nm · a={response.slit_width_um:g} µm")
            self._reference_line.set_visible(True)
        self._update_legend()
        self.draw_idle()

    def _update_legend(self) -> None:
        if self._reference_line.get_visible():
            palette = current_palette(QApplication.instance())
            self.ax.legend(handles=[self._main_line, self._reference_line], loc="lower center",
                           fontsize=7, facecolor=palette.surface, edgecolor=palette.border_strong,
                           labelcolor=palette.text_primary)
        elif self.ax.get_legend() is not None:
            self.ax.get_legend().remove()

    def set_envelope_visible(self, visible: bool) -> None:
        self._show_envelope = visible
        self._envelope_line.set_visible(visible and self._slit_count == 2)
        self.draw_idle()

    def _update_marker_visibility(self) -> None:
        lower, upper = self.ax.get_xlim()
        visible = lower <= self._selected_angle_deg <= upper
        for artist in (self._marker_v_line, self._marker_point, self._marker_label):
            artist.set_visible(visible)

    def export_image(self, destination: Path) -> None:
        
        with atomic_output_path(destination) as temporary:
            self.figure.savefig(
                temporary,
                format="png",
                metadata={"Software": f"LumenLab {VERSION}", "Description": self.experiment_metadata},
                dpi=200,
                facecolor=self.figure.get_facecolor(),
                edgecolor="none",
                bbox_inches="tight",
            )
