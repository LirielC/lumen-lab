

from pathlib import Path
import math
from PySide6.QtCore import QObject, QSignalBlocker
from PySide6.QtWidgets import QFileDialog, QMessageBox
from app.adapters.outbound.export.experiment_file import load_experiment, save_experiment
from app.core.application.dto.requests import InterferenceRequest, PolarizationRequest
from app.core.domain.errors import OptiLabDomainError


class ExperimentController(QObject):
    def __init__(self, window, interference_controller, polarization_controller) -> None:
        super().__init__(window)
        self.window = window
        self.controllers = {1: interference_controller, 2: polarization_controller}
        window.action_save_experiment.triggered.connect(self.save)
        window.action_open_experiment.triggered.connect(self.open)

    def save(self) -> None:
        controller = self.controllers.get(self.window.stack.currentIndex())
        if controller is None:
            return
        controller._debounce_timer.stop()
        controller._run_simulation()
        response = controller._view.last_response
        if response is None:
            return
        name, _ = QFileDialog.getSaveFileName(self.window, "Salvar experimento", "lumenlab_experimento.json", "Experimento JSON (*.json)")
        if name:
            try:
                save_experiment(response, Path(name))
                self.window.statusBar().showMessage("Experimento salvo.", 5000)
            except (OSError, ValueError) as error:
                QMessageBox.critical(self.window, "Não foi possível salvar", str(error))

    def open(self) -> None:
        name, _ = QFileDialog.getOpenFileName(self.window, "Abrir experimento", "", "Experimento JSON (*.json)")
        if name:
            try:
                self.apply_request(load_experiment(Path(name)))
            except (OSError, ValueError, TypeError, OptiLabDomainError) as error:
                QMessageBox.warning(self.window, "Experimento inválido", str(error))

    def apply_request(self, request: InterferenceRequest | PolarizationRequest) -> None:
        
        index = 1 if isinstance(request, InterferenceRequest) else 2
        controller = self.controllers[index]
        view = controller._view
        values = [(view.slider_wavelength, request.wavelength_nm),
                  (view.slider_intensity, request.initial_intensity)]
        if index == 1:
            values += [(view.slider_width, request.slit_width_um),
                       (view.slider_incidence, request.incidence_angle_deg),
                       (view.slider_observation, request.observation_angle_deg)]
            if request.slit_count == 2:
                values.append((view.slider_separation, request.slit_separation_um))
            choices = [(view.slit_control, request.slit_count - 1)]
        else:
            values += list(zip((view.slider_p1, view.slider_p2, view.slider_p3), request.polarizer_angles_deg))
            if request.initially_polarized:
                values.append((view.slider_initial_angle, request.initial_angle_deg))
            choices = [(view.count_control, request.polarizer_count - 1),
                       (view.light_type_control, int(request.initially_polarized))]
        for control, value in values:
            if value is None or not control._min <= value <= control._max or not math.isclose(round(value, control._decimals), value, rel_tol=0, abs_tol=1e-10):
                raise ValueError(f"{control._label.text()}: valor fora dos limites ou da precisão dos controles.")
        response = controller._use_case.execute(request)
        controller._debounce_timer.stop()
        blockers = [QSignalBlocker(control) for control, _ in values + choices]
        for control, value in values:
            control.set_value(value)
        for control, value in choices:
            control.set_selected_index(value)
        del blockers
        if index == 1:
            view.slider_separation.setVisible(request.slit_count == 2)
            view.check_show_envelope.setVisible(request.slit_count == 2)
            if request.slit_count == 1:
                view.check_show_envelope.setChecked(False)
        else:
            view.slider_initial_angle.setVisible(request.initially_polarized)
            view.slider_p2.setVisible(request.polarizer_count >= 2)
            view.slider_p3.setVisible(request.polarizer_count >= 3)
        view.clear_error()
        view.update_view(response)
        controller._check_preset_match()
        self.window.navigate_to(index)
