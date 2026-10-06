

from datetime import datetime, timezone
import json
import math
from pathlib import Path
import sys
import traceback
from PySide6.QtCore import QTimer
from app.adapters.outbound.export.experiment_file import save_experiment, load_experiment
from app.core.application.dto.requests import InterferenceRequest, PolarizationRequest
from app.version import VERSION


def run_installation_check(app, container, output: Path) -> int:
    output.mkdir(parents=True, exist_ok=True)
    window = container.main_window
    window.show()

    def check() -> None:
        report = {"version": VERSION, "frozen": bool(getattr(sys, "frozen", False)),
                  "executable": sys.executable, "date_utc": datetime.now(timezone.utc).isoformat(),
                  "checks": [], "passed": False}
        try:
            cases = [(InterferenceRequest(1, 500, 25, None, 0, 1.1, 2), .003476912635531636),
                     (InterferenceRequest(2, 500, 10, 50, 0, .6, 1), .844935718993447),
                     (PolarizationRequest(3, 550, 1, False, None, (0, 45, 90)), .125),
                     (PolarizationRequest(2, 650, 1, True, 30, (45, 90)), .4665063509461097)]
            for index, (request, expected) in enumerate(cases):
                container.experiment_controller.apply_request(request)
                app.processEvents()
                page = window.stack.currentWidget()
                response = page.last_response
                actual = response.selected_intensity if isinstance(request, InterferenceRequest) else response.final_intensity
                assert math.isclose(actual, expected, rel_tol=1e-10)
                path = output / f"experimento-{index}.json"
                save_experiment(response, path)
                container.experiment_controller.apply_request(load_experiment(path))
                export = container.file_exporter.export_csv_interference if index < 2 else container.file_exporter.export_csv_polarization
                export(response, output / f"experimento-{index}.csv")
                assert window.grab().save(str(output / f"tela-{index}.png"))
                report["checks"].append(f"experiment-{index}: physics, JSON round trip, CSV, Qt render")
            window.navigate_to(1)
            container.interference_controller.freeze_reference()
            container.interference_page.slider_wavelength.set_value(450)
            container.interference_controller._run_simulation()
            container.interference_page.plot_widget.export_image(output / "comparacao.png")
            assert container.interference_page.reference_response.wavelength_nm == 500
            report["checks"].append("comparison and PNG export")
            container.experiment_controller.apply_request(PolarizationRequest(1, 550, 0, False, None, (0,)))
            assert container.polarization_page.last_response.final_intensity == 0
            container.experiment_controller.apply_request(InterferenceRequest(1, 500, 25, None, 0, 0, 0))
            assert container.interference_page.last_response.selected_intensity == 0
            report["checks"].append("zero-intensity source in both modules")
            page = container.interference_page
            page.slit_control.set_selected_index(1)
            page.slider_width.set_value(100)
            page.slider_separation.set_value(50)
            container.interference_controller._run_simulation()
            assert page.last_response is None and not page.btn_export_csv.isEnabled() and not page.btn_export_plot.isEnabled()
            report["checks"].append("invalid geometry blocks CSV and PNG")
            report["passed"] = True
        except Exception:
            report["error"] = traceback.format_exc()
        finally:
            (output / "verification.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
            window.close()
            app.exit(0 if report["passed"] else 1)

    QTimer.singleShot(300, check)
    return app.exec()
