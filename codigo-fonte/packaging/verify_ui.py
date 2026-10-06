

import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from PySide6.QtCore import QTimer
from app.bootstrap.application import create_app


def main() -> None:
    scale = float(os.environ.get("QT_SCALE_FACTOR", "1"))
    output = ROOT / "build" / "release-verification" / f"dpi-{scale:g}"
    output.mkdir(parents=True, exist_ok=True)
    app, lab = create_app()
    window = lab.main_window
    window.resize(round(1366 / scale), round(768 / scale))
    window.show()
    evidence = []

    def capture() -> None:
        for index, name in ((0, "inicio"), (1, "fendas"), (2, "polarizacao")):
            window.navigate_to(index)
            app.processEvents()
            window.grab().save(str(output / f"{name}.png"))
            assert window.width() <= round(1366 / scale)
            assert window.height() <= round(768 / scale)
            assert window.btn_help.geometry().right() <= window.width()
            evidence.append({"page": name, "logical_size": window.size().toTuple(),
                             "device_pixel_ratio": window.devicePixelRatioF(),
                             "horizontal_scroll": window.workspace_scroll.horizontalScrollBar().maximum(),
                             "vertical_scroll": window.workspace_scroll.verticalScrollBar().maximum()})
        window.navigate_to(1)
        lab.interference_controller.freeze_reference()
        lab.interference_page.slider_wavelength.set_value(450)
        lab.interference_controller._run_simulation()
        lab.interference_page.btn_toggle_detail.setChecked(True)
        app.processEvents()
        window.grab().save(str(output / "comparacao.png"))
        lab.interference_page.plot_widget.export_image(output / "comparacao-grafico.png")
        (output / "checks.json").write_text(json.dumps(evidence, indent=2), encoding="utf-8")
        window.close()
        app.quit()

    QTimer.singleShot(300, capture)
    app.exec()


if __name__ == "__main__":
    main()
