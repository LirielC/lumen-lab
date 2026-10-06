

import gc
import pytest
from PySide6.QtCore import QCoreApplication, QEvent
from PySide6.QtWidgets import QApplication


@pytest.fixture(autouse=True)
def dispose_test_windows():
    yield
    if QApplication.instance() is not None:
        for window in QApplication.topLevelWidgets():
            window.close()
            window.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        gc.collect()
