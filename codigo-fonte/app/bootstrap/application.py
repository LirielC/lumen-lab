

from app.version import VERSION
import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from app.adapters.inbound.qt.styles.theme import apply_theme
from app.bootstrap.container import ApplicationContainer


def create_app() -> tuple[QApplication, ApplicationContainer]:
    
    
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()

    app.setApplicationName("LumenLab")
    app.setApplicationVersion(VERSION)
    app.setOrganizationName("LumenLab")

    apply_theme(app)

    container = ApplicationContainer()
    return app, container
