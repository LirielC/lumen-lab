

import math
from pathlib import Path
from typing import TYPE_CHECKING
from PySide6.QtCore import QObject, QTimer
from PySide6.QtWidgets import QFileDialog, QMessageBox

from app.core.application.dto.requests import PolarizationRequest
from app.core.application.ports.inbound import SimulatePolarizationPort
from app.core.application.ports.outbound import ResultExporterPort
from app.core.domain.errors import OptiLabDomainError

if TYPE_CHECKING:
    from app.adapters.inbound.qt.views.polarization_page import PolarizationPage

PRESET_KEYS = ["cascade_0_45_90", "parallel", "crossed", "polarized_input"]

PRESET_DATA = {
    "cascade_0_45_90": {
        "light_type": 0,  
        "polarizer_count": 3,
        "wavelength": 550.0,
        "intensity": 1.0,
        "p1": 0.0,
        "p2": 45.0,
        "p3": 90.0,
        "initial_angle": 0.0,
    },
    "parallel": {
        "light_type": 0,  
        "polarizer_count": 2,
        "wavelength": 600.0,
        "intensity": 1.0,
        "p1": 0.0,
        "p2": 0.0,
        "p3": 0.0,
        "initial_angle": 0.0,
    },
    "crossed": {
        "light_type": 0,  
        "polarizer_count": 2,
        "wavelength": 520.0,
        "intensity": 1.0,
        "p1": 0.0,
        "p2": 90.0,
        "p3": 0.0,
        "initial_angle": 0.0,
    },
    "polarized_input": {
        "light_type": 1,  
        "initial_angle": 30.0,
        "polarizer_count": 2,
        "wavelength": 650.0,
        "intensity": 1.0,
        "p1": 45.0,
        "p2": 90.0,
        "p3": 0.0,
    },
}


class PolarizationController(QObject):
    

    def __init__(
        self,
        use_case: SimulatePolarizationPort,
        exporter: ResultExporterPort,
    ) -> None:
        super().__init__()
        self._use_case = use_case
        self._exporter = exporter
        self._view: "PolarizationPage | None" = None
        self._is_applying_preset = False

        self._debounce_timer = QTimer(self)
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.setInterval(40)
        self._debounce_timer.timeout.connect(self._run_simulation)

    def bind_view(self, view: "PolarizationPage") -> None:
        
        self._view = view
        self._connect_signals()
        self.apply_preset("cascade_0_45_90")

    def _connect_signals(self) -> None:
        assert self._view is not None
        v = self._view

        v.light_type_control.selectionChanged.connect(self._on_light_type_changed)
        v.count_control.selectionChanged.connect(self._on_count_changed)

        v.slider_wavelength.valueChanged.connect(self._on_parameter_edited)
        v.slider_intensity.valueChanged.connect(self._on_parameter_edited)
        v.slider_initial_angle.valueChanged.connect(self._on_parameter_edited)

        v.slider_p1.valueChanged.connect(self._on_parameter_edited)
        v.slider_p2.valueChanged.connect(self._on_parameter_edited)
        v.slider_p3.valueChanged.connect(self._on_parameter_edited)

        v.btn_reset.clicked.connect(self.reset_defaults)
        v.btn_export_csv.clicked.connect(self.export_csv)
        v.combo_presets.currentIndexChanged.connect(self._on_preset_selected)

    def _on_light_type_changed(self, index: int, text: str) -> None:
        assert self._view is not None
        is_polarized = (index == 1)
        self._view.slider_initial_angle.setVisible(is_polarized)
        self._on_parameter_edited()

    def _on_count_changed(self, index: int, text: str) -> None:
        assert self._view is not None
        count = index + 1
        self._view.slider_p2.setVisible(count >= 2)
        self._view.slider_p3.setVisible(count >= 3)
        self._on_parameter_edited()

    def _on_parameter_edited(self, *args) -> None:
        
        if self._is_applying_preset:
            return

        self._check_preset_match()
        self._schedule_update()

    def _check_preset_match(self) -> None:
        
        if self._view is None:
            return
        v = self._view

        light_type = v.light_type_control.selected_index()
        polarizer_count = v.count_control.selected_index() + 1
        wl = v.slider_wavelength.value()
        i0 = v.slider_intensity.value()
        phi0 = v.slider_initial_angle.value()
        p1 = v.slider_p1.value()
        p2 = v.slider_p2.value()
        p3 = v.slider_p3.value()

        matched_index = 4  
        for idx, key in enumerate(PRESET_KEYS):
            d = PRESET_DATA[key]
            if (
                d["light_type"] == light_type
                and d["polarizer_count"] == polarizer_count
                and math.isclose(d["wavelength"], wl, abs_tol=1e-3)
                and math.isclose(d["intensity"], i0, abs_tol=1e-3)
                and math.isclose(d["p1"], p1, abs_tol=1e-3)
            ):
                if polarizer_count >= 2 and not math.isclose(d["p2"], p2, abs_tol=1e-3):
                    continue
                if polarizer_count >= 3 and not math.isclose(d["p3"], p3, abs_tol=1e-3):
                    continue
                if light_type == 1 and not math.isclose(d["initial_angle"], phi0, abs_tol=1e-3):
                    continue
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

        initially_polarized = (v.light_type_control.selected_index() == 1)
        polarizer_count = v.count_control.selected_index() + 1
        wl_nm = v.slider_wavelength.value()
        i0 = v.slider_intensity.value()
        phi0_deg = v.slider_initial_angle.value() if initially_polarized else None

        angles = [v.slider_p1.value()]
        if polarizer_count >= 2:
            angles.append(v.slider_p2.value())
        if polarizer_count >= 3:
            angles.append(v.slider_p3.value())

        request = PolarizationRequest(
            polarizer_count=polarizer_count,
            wavelength_nm=wl_nm,
            initial_intensity=i0,
            initially_polarized=initially_polarized,
            initial_angle_deg=phi0_deg,
            polarizer_angles_deg=tuple(angles),
        )

        try:
            response = self._use_case.execute(request)
            v.update_view(response)
            v.clear_error()
        except OptiLabDomainError as err:
            v.set_error(err.message)

    def apply_preset(self, preset_key: str) -> None:
        
        if self._view is None or preset_key not in PRESET_DATA:
            return
        v = self._view

        self._is_applying_preset = True
        preset_idx = PRESET_KEYS.index(preset_key)

        v.combo_presets.blockSignals(True)
        v.combo_presets.setCurrentIndex(preset_idx)
        v.combo_presets.blockSignals(False)

        d = PRESET_DATA[preset_key]

        v.light_type_control.blockSignals(True)
        v.light_type_control.set_selected_index(d["light_type"])
        v.light_type_control.blockSignals(False)

        is_polarized = (d["light_type"] == 1)
        v.slider_initial_angle.setVisible(is_polarized)
        if is_polarized:
            v.slider_initial_angle.set_value(d["initial_angle"])

        count = d["polarizer_count"]
        v.count_control.blockSignals(True)
        v.count_control.set_selected_index(count - 1)
        v.count_control.blockSignals(False)

        v.slider_p2.setVisible(count >= 2)
        v.slider_p3.setVisible(count >= 3)

        v.slider_wavelength.set_value(d["wavelength"])
        v.slider_intensity.set_value(d["intensity"])
        v.slider_p1.set_value(d["p1"])
        v.slider_p2.set_value(d["p2"])
        v.slider_p3.set_value(d["p3"])

        self._is_applying_preset = False
        self._run_simulation()

    def _on_preset_selected(self, index: int) -> None:
        if self._is_applying_preset:
            return
        if 0 <= index < len(PRESET_KEYS):
            self.apply_preset(PRESET_KEYS[index])

    def reset_defaults(self) -> None:
        
        assert self._view is not None
        self.apply_preset("cascade_0_45_90")

    def export_csv(self) -> None:
        
        self._run_simulation()
        if self._view is None or self._view.last_response is None:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self._view,
            "Exportar Dados para CSV",
            "lumenlab_polarizadores.csv",
            "CSV (*.csv)",
        )
        if file_path:
            try:
                self._exporter.export_csv_polarization(
                    self._view.last_response,
                    Path(file_path),
                )
                QMessageBox.information(
                    self._view,
                    "Sucesso",
                    f"Tabela salva com sucesso em:\n{file_path}",
                )
            except Exception as e:
                QMessageBox.critical(
                    self._view,
                    "Erro ao Exportar",
                    f"Não foi possível salvar o arquivo:\n{e}",
                )
