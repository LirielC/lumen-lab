

import math
from pathlib import Path
from typing import TYPE_CHECKING
from PySide6.QtCore import QObject, QTimer
from PySide6.QtWidgets import QFileDialog, QMessageBox

from app.core.application.dto.requests import InterferenceRequest
from app.core.application.ports.inbound import SimulateInterferencePort
from app.core.application.ports.outbound import ResultExporterPort
from app.core.domain.errors import OptiLabDomainError

if TYPE_CHECKING:
    from app.adapters.inbound.qt.views.interference_page import InterferencePage

PRESET_KEYS = ["single_slit", "double_slit", "oblique", "blue_vs_red"]

PRESET_DATA = {
    "single_slit": {
        "slit_count": 1,
        "wavelength_nm": 633.0,
        "slit_width_um": 25.0,
        "slit_separation_um": 50.0,
        "incidence_angle_deg": 0.0,
        "observation_angle_deg": 0.0,
        "initial_intensity": 1.0,
    },
    "double_slit": {
        "slit_count": 2,
        "wavelength_nm": 532.0,
        "slit_width_um": 10.0,
        "slit_separation_um": 50.0,
        "incidence_angle_deg": 0.0,
        "observation_angle_deg": 0.0,
        "initial_intensity": 1.0,
    },
    "oblique": {
        "slit_count": 2,
        "wavelength_nm": 550.0,
        "slit_width_um": 15.0,
        "slit_separation_um": 60.0,
        "incidence_angle_deg": 5.0,
        "observation_angle_deg": 5.0,
        "initial_intensity": 1.0,
    },
    "blue_vs_red": {
        "slit_count": 2,
        "wavelength_nm": 450.0,
        "slit_width_um": 12.0,
        "slit_separation_um": 45.0,
        "incidence_angle_deg": 0.0,
        "observation_angle_deg": 0.0,
        "initial_intensity": 1.0,
    },
}


class InterferenceController(QObject):
    

    def __init__(
        self,
        use_case: SimulateInterferencePort,
        exporter: ResultExporterPort,
    ) -> None:
        super().__init__()
        self._use_case = use_case
        self._exporter = exporter
        self._view: "InterferencePage | None" = None
        self._is_applying_preset = False

        
        self._debounce_timer = QTimer(self)
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.setInterval(40)  # 40ms
        self._debounce_timer.timeout.connect(self._run_simulation)

    def bind_view(self, view: "InterferencePage") -> None:
        
        self._view = view
        self._connect_signals()
        self.apply_preset("single_slit")

    def _connect_signals(self) -> None:
        assert self._view is not None
        v = self._view

        v.slit_control.selectionChanged.connect(self._on_slit_mode_changed)
        v.slider_wavelength.valueChanged.connect(self._on_parameter_edited)
        v.slider_width.valueChanged.connect(self._on_parameter_edited)
        v.slider_separation.valueChanged.connect(self._on_parameter_edited)
        v.slider_incidence.valueChanged.connect(self._on_parameter_edited)
        v.slider_observation.valueChanged.connect(self._on_parameter_edited)
        v.slider_intensity.valueChanged.connect(self._on_parameter_edited)

        v.btn_toggle_detail.toggled.connect(self._on_view_mode_changed)
        v.check_show_envelope.toggled.connect(v.plot_widget.set_envelope_visible)
        v.btn_reset.clicked.connect(self.reset_defaults)
        v.btn_export_csv.clicked.connect(self.export_csv)
        v.btn_export_plot.clicked.connect(self.export_plot)
        v.btn_reference.clicked.connect(self.freeze_reference)
        v.btn_clear_reference.clicked.connect(lambda: v.set_reference(None))
        v.combo_presets.currentIndexChanged.connect(self._on_preset_selected)

        
        v.plot_widget.angleSelected.connect(self._on_angle_selected_from_visual)
        v.screen_pattern.angleSelected.connect(self._on_angle_selected_from_visual)
        v.canvas.angleSelected.connect(self._on_angle_selected_from_visual)

    def _on_angle_selected_from_visual(self, angle_deg: float) -> None:
        if self._view is None:
            return
        self._view.slider_observation.set_value(round(angle_deg, 1))
        self._on_parameter_edited()

    def _on_slit_mode_changed(self, index: int, text: str) -> None:
        assert self._view is not None
        is_double = (index == 1)
        self._view.slider_separation.setVisible(is_double)
        self._view.check_show_envelope.setVisible(is_double)
        if not is_double:
            self._view.check_show_envelope.setChecked(False)
        self._on_parameter_edited()

    def _on_view_mode_changed(self, detailed: bool) -> None:
        assert self._view is not None
        mode = "detail" if detailed else "overview"
        self._view.btn_toggle_detail.setText("Voltar à visão completa" if detailed else "Ampliar padrão")
        self._view.plot_widget.set_view_mode(mode)
        self._view.screen_pattern.set_view_mode(mode)
        self._view.canvas.set_view_mode(mode)

    def _on_parameter_edited(self, *args) -> None:
        
        if self._is_applying_preset:
            return

        self._check_preset_match()
        assert self._view is not None
        self._view.btn_export_csv.setEnabled(False)
        self._view.btn_export_plot.setEnabled(False)
        self._schedule_update()

    def _check_preset_match(self) -> None:
        
        if self._view is None:
            return
        v = self._view

        slit_count = 1 if v.slit_control.selected_index() == 0 else 2
        wl = v.slider_wavelength.value()
        w = v.slider_width.value()
        sep = v.slider_separation.value()
        inc = v.slider_incidence.value()
        obs = v.slider_observation.value()
        i0 = v.slider_intensity.value()

        matched_index = 4  
        for idx, key in enumerate(PRESET_KEYS):
            d = PRESET_DATA[key]
            if (
                d["slit_count"] == slit_count
                and math.isclose(d["wavelength_nm"], wl, abs_tol=0.5)
                and math.isclose(d["slit_width_um"], w, abs_tol=0.1)
                and (slit_count == 1 or math.isclose(d["slit_separation_um"], sep, abs_tol=0.1))
                and math.isclose(d["incidence_angle_deg"], inc, abs_tol=0.1)
                and math.isclose(d["observation_angle_deg"], obs, abs_tol=0.1)
                and math.isclose(d["initial_intensity"], i0, abs_tol=0.05)
            ):
                matched_index = idx
                break

        v.combo_presets.blockSignals(True)
        v.combo_presets.setCurrentIndex(matched_index)
        v.combo_presets.blockSignals(False)

    def _schedule_update(self) -> None:
        
        self._debounce_timer.start()

    def _run_simulation(self) -> None:
        if self._view is None:
            return
        v = self._view

        slit_count = 1 if v.slit_control.selected_index() == 0 else 2
        wl_nm = v.slider_wavelength.value()
        w_um = v.slider_width.value()
        sep_um = v.slider_separation.value() if slit_count == 2 else None
        inc_deg = v.slider_incidence.value()
        obs_deg = v.slider_observation.value()
        i0 = v.slider_intensity.value()

        
        if slit_count == 2 and sep_um is not None and sep_um <= w_um:
            v.set_error(
                f"Separação d ({sep_um:.1f} µm) deve ser maior que a largura a ({w_um:.1f} µm)."
            )
            return

        v.clear_error()

        request = InterferenceRequest(
            slit_count=slit_count,
            wavelength_nm=wl_nm,
            slit_width_um=w_um,
            slit_separation_um=sep_um,
            incidence_angle_deg=inc_deg,
            observation_angle_deg=obs_deg,
            initial_intensity=i0,
        )

        try:
            response = self._use_case.execute(request)
            v.update_view(response)
        except OptiLabDomainError as err:
            v.set_error(err.message)

    def apply_preset(self, preset_key: str) -> None:
        
        if self._view is None:
            return
        v = self._view

        if preset_key not in PRESET_DATA:
            return

        data = PRESET_DATA[preset_key]
        self._is_applying_preset = True

        v.slit_control.blockSignals(True)
        v.slider_wavelength.blockSignals(True)
        v.slider_width.blockSignals(True)
        v.slider_separation.blockSignals(True)
        v.slider_incidence.blockSignals(True)
        v.slider_observation.blockSignals(True)
        v.slider_intensity.blockSignals(True)
        v.combo_presets.blockSignals(True)

        
        is_double = (data["slit_count"] == 2)
        v.slit_control.set_selected_index(1 if is_double else 0)
        v.slider_separation.setVisible(is_double)
        v.check_show_envelope.setVisible(is_double)
        if not is_double:
            v.check_show_envelope.setChecked(False)

        v.slider_wavelength.set_value(data["wavelength_nm"])
        v.slider_width.set_value(data["slit_width_um"])
        if is_double:
            v.slider_separation.set_value(data["slit_separation_um"])
        v.slider_incidence.set_value(data["incidence_angle_deg"])
        v.slider_observation.set_value(data["observation_angle_deg"])
        v.slider_intensity.set_value(data["initial_intensity"])

        preset_idx = PRESET_KEYS.index(preset_key)
        v.combo_presets.setCurrentIndex(preset_idx)

        v.slit_control.blockSignals(False)
        v.slider_wavelength.blockSignals(False)
        v.slider_width.blockSignals(False)
        v.slider_separation.blockSignals(False)
        v.slider_incidence.blockSignals(False)
        v.slider_observation.blockSignals(False)
        v.slider_intensity.blockSignals(False)
        v.combo_presets.blockSignals(False)

        self._is_applying_preset = False
        self._run_simulation()

    def _on_preset_selected(self, index: int) -> None:
        if 0 <= index < len(PRESET_KEYS):
            self.apply_preset(PRESET_KEYS[index])

    def reset_defaults(self) -> None:
        
        self.apply_preset("single_slit")

    def freeze_reference(self) -> None:
        self._debounce_timer.stop()
        self._run_simulation()
        if self._view is not None and self._view.last_response is not None:
            self._view.set_reference(self._view.last_response)

    def export_csv(self) -> None:
        
        self._run_simulation()
        if self._view is None or self._view.last_response is None:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self._view,
            "Exportar Dados para CSV",
            "lumenlab_fendas.csv",
            "CSV (*.csv)",
        )
        if file_path:
            try:
                self._exporter.export_csv_interference(
                    self._view.last_response,
                    Path(file_path),
                )
                QMessageBox.information(
                    self._view,
                    "Sucesso",
                    f"Arquivo salvo com sucesso em:\n{file_path}",
                )
            except Exception as e:
                QMessageBox.critical(
                    self._view,
                    "Erro ao Exportar",
                    f"Não foi possível salvar o arquivo:\n{e}",
                )

    def export_plot(self) -> None:
        
        self._run_simulation()
        if self._view is None or self._view.last_response is None:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self._view,
            "Salvar Gráfico em Imagem",
            "lumenlab_grafico_fendas.png",
            "Imagens PNG (*.png)",
        )
        if file_path:
            try:
                self._view.plot_widget.export_image(Path(file_path))
                QMessageBox.information(
                    self._view,
                    "Sucesso",
                    f"Gráfico salvo com sucesso em:\n{file_path}",
                )
            except Exception as e:
                QMessageBox.critical(
                    self._view,
                    "Erro ao Exportar",
                    f"Não foi possível salvar a imagem:\n{e}",
                )
