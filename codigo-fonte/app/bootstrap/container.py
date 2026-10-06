

from app.adapters.inbound.qt.controllers.experiment_controller import ExperimentController
from app.adapters.inbound.qt.controllers.interference_controller import (
    InterferenceController,
)
from app.adapters.inbound.qt.controllers.polarization_controller import (
    PolarizationController,
)
from app.adapters.inbound.qt.views.interference_page import InterferencePage
from app.adapters.inbound.qt.views.main_window import MainWindow
from app.adapters.inbound.qt.views.polarization_page import PolarizationPage
from app.adapters.outbound.export.file_exporter import FileResultExporter
from app.core.application.use_cases.simulate_interference import (
    SimulateInterferenceUseCase,
)
from app.core.application.use_cases.simulate_polarization import (
    SimulatePolarizationUseCase,
)


class ApplicationContainer:
    

    def __init__(self) -> None:
        
        self.interference_use_case = SimulateInterferenceUseCase()
        self.polarization_use_case = SimulatePolarizationUseCase()

        
        self.file_exporter = FileResultExporter()

        
        self.interference_controller = InterferenceController(
            use_case=self.interference_use_case,
            exporter=self.file_exporter,
        )
        self.polarization_controller = PolarizationController(
            use_case=self.polarization_use_case,
            exporter=self.file_exporter,
        )

        
        self.interference_page = InterferencePage()
        self.polarization_page = PolarizationPage()

        
        self.interference_controller.bind_view(self.interference_page)
        self.polarization_controller.bind_view(self.polarization_page)

        
        self.main_window = MainWindow(
            interference_page=self.interference_page,
            polarization_page=self.polarization_page,
        )

        self.experiment_controller = ExperimentController(
            self.main_window, self.interference_controller, self.polarization_controller,
        )
