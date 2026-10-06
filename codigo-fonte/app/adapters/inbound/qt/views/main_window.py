from app.version import VERSION
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QAction, QIcon, QKeySequence
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.adapters.inbound.qt.styles.icons import scientific_icon
from app.adapters.outbound.resources.resource_resolver import get_resource_path
from app.adapters.inbound.qt.views.help_page import HelpPage
from app.adapters.inbound.qt.views.home_page import HomePage
from app.adapters.inbound.qt.views.interference_page import InterferencePage
from app.adapters.inbound.qt.views.polarization_page import PolarizationPage
from app.adapters.inbound.qt.views.reference_pages import create_examples_page, create_units_page
from app.adapters.inbound.qt.views.theory_page import TheoryPage


class MainWindow(QMainWindow):

    PAGE_ICONS = ("home", "wave-sine", "arrows-move", "book", "help-circle", "file-text", "ruler-measure")

    PAGE_HOME = 0
    PAGE_INTERFERENCE = 1
    PAGE_POLARIZATION = 2
    PAGE_THEORY = 3
    PAGE_HELP = 4
    PAGE_EXAMPLES = 5
    PAGE_UNITS = 6

    def __init__(
        self,
        interference_page: InterferencePage,
        polarization_page: PolarizationPage,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("LumenLab — Laboratório Computacional de Óptica")
        self.setWindowIcon(QIcon(str(get_resource_path("assets/icons/lumenlab.svg"))))
        self.resize(1366, 768)
        self.setMinimumSize(900, 480)

        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # -------------------------------------------------------------
        
        # -------------------------------------------------------------
        top_header = QFrame()
        top_header.setObjectName("topHeader")
        top_header.setFixedHeight(52)
        header_layout = QHBoxLayout(top_header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        header_layout.setSpacing(12)

        
        lbl_logo = QLabel()
        lbl_logo.setPixmap(self.windowIcon().pixmap(32, 32))
        lbl_brand = QLabel("LumenLab")
        lbl_brand.setProperty("class", "brand-title")
        header_layout.addWidget(lbl_logo)
        header_layout.addWidget(lbl_brand)
        header_layout.addSpacing(28)

        
        self._nav_buttons: list[QPushButton] = []
        self.btn_home = self._create_top_nav_button("Início", self.PAGE_HOME)
        self.btn_interference = self._create_top_nav_button("Fendas", self.PAGE_INTERFERENCE)
        self.btn_interference.setToolTip("Interferência e difração por fendas")
        self.btn_polarization = self._create_top_nav_button("Polarização", self.PAGE_POLARIZATION)
        self.btn_theory = self._create_top_nav_button("Teoria", self.PAGE_THEORY)

        header_layout.addWidget(self.btn_home)
        header_layout.addWidget(self.btn_interference)
        header_layout.addWidget(self.btn_polarization)
        header_layout.addWidget(self.btn_theory)
        header_layout.addStretch()

        self.btn_help = QPushButton()
        self.btn_help.setIcon(scientific_icon("help-circle"))
        self.btn_help.setIconSize(QSize(20, 20))
        self.btn_help.setAccessibleName("Ajuda")
        self.btn_help.setProperty("class", "top-icon-btn")
        self.btn_help.setToolTip("Ajuda")
        self.btn_help.clicked.connect(lambda: self.navigate_to(self.PAGE_HELP))
        header_layout.addWidget(self.btn_help)

        
        self.btn_examples = QPushButton("Exemplos")
        self.btn_examples.setVisible(False)
        self.btn_examples.clicked.connect(lambda: self.navigate_to(self.PAGE_EXAMPLES))
        header_layout.addWidget(self.btn_examples)

        self.btn_units = QPushButton("Unidades")
        self.btn_units.setVisible(False)
        self.btn_units.clicked.connect(lambda: self.navigate_to(self.PAGE_UNITS))
        header_layout.addWidget(self.btn_units)

        main_layout.addWidget(top_header)

        # -------------------------------------------------------------
        
        # -------------------------------------------------------------
        self.stack = QStackedWidget()
        self.home_page = HomePage()
        self.interference_page = interference_page
        self.polarization_page = polarization_page
        self.theory_page = TheoryPage()
        self.help_page = HelpPage()
        self.examples_page = create_examples_page()
        self.units_page = create_units_page()
        for page in (
            self.home_page,
            self.interference_page,
            self.polarization_page,
            self.theory_page,
            self.help_page,
            self.examples_page,
            self.units_page,
        ):
            self.stack.addWidget(page)
        
        
        self.workspace_scroll = QScrollArea()
        self.workspace_scroll.setWidgetResizable(True)
        self.workspace_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.stack.setMinimumSize(1280, 640)
        self.workspace_scroll.setWidget(self.stack)
        main_layout.addWidget(self.workspace_scroll, stretch=1)

        self.home_page.openInterferenceRequested.connect(lambda: self.navigate_to(self.PAGE_INTERFERENCE))
        self.home_page.openPolarizationRequested.connect(lambda: self.navigate_to(self.PAGE_POLARIZATION))
        self.home_page.openTheoryRequested.connect(lambda: self.navigate_to(self.PAGE_THEORY))
        self._create_actions()
        self._create_menu()
        self._create_status_bar()
        self.interference_page.statusTextChanged.connect(self._refresh_scientific_status)
        self.polarization_page.statusTextChanged.connect(self._refresh_scientific_status)
        self.navigate_to(self.PAGE_HOME)

    def _create_top_nav_button(self, label: str, target_index: int) -> QPushButton:
        button = QPushButton(label)
        button.setIcon(scientific_icon(self.PAGE_ICONS[target_index]))
        button.setIconSize(QSize(20, 20))
        button.setProperty("class", "top-nav-btn")
        button.setProperty("target_page", target_index)
        button.setCheckable(True)
        button.clicked.connect(lambda: self.navigate_to(target_index))
        self._nav_buttons.append(button)
        return button

    def _create_actions(self) -> None:
        self.action_interference = self._navigation_action("Interferência e difração", self.PAGE_INTERFERENCE, "Ctrl+1")
        self.action_polarization = self._navigation_action("Polarização", self.PAGE_POLARIZATION, "Ctrl+2")
        self.action_theory = self._navigation_action("Teoria e equações", self.PAGE_THEORY)
        self.action_examples = self._navigation_action("Exemplos", self.PAGE_EXAMPLES)
        self.action_units = self._navigation_action("Unidades e constantes", self.PAGE_UNITS)
        self.action_help = self._navigation_action("Ajuda", self.PAGE_HELP, "F1")
        self.action_save_experiment = QAction("Salvar experimento...", self)
        self.action_save_experiment.setShortcut(QKeySequence("Ctrl+S"))
        self.action_open_experiment = QAction("Abrir experimento...", self)
        self.action_open_experiment.setShortcut(QKeySequence("Ctrl+O"))
        self.action_exit = QAction("Sair", self)
        self.action_exit.triggered.connect(self.close)

    def _navigation_action(self, text: str, page: int, shortcut: str | None = None) -> QAction:
        action = QAction(scientific_icon(self.PAGE_ICONS[page]), text, self)
        if shortcut:
            action.setShortcut(QKeySequence(shortcut))
        action.triggered.connect(lambda: self.navigate_to(page))
        return action

    def _create_menu(self) -> None:
        file_menu = self.menuBar().addMenu("Arquivo")
        file_menu.addAction(self.action_open_experiment)
        file_menu.addAction(self.action_save_experiment)
        file_menu.addSeparator()
        file_menu.addAction(self.action_exit)
        simulations_menu = self.menuBar().addMenu("Simulações")
        simulations_menu.addAction(self.action_interference)
        simulations_menu.addAction(self.action_polarization)
        reference_menu = self.menuBar().addMenu("Referência")
        reference_menu.addAction(self.action_theory)
        reference_menu.addAction(self.action_examples)
        reference_menu.addAction(self.action_units)
        help_menu = self.menuBar().addMenu("Ajuda")
        help_menu.addAction(self.action_help)

    def _create_status_bar(self) -> None:
        self.scientific_status = QLabel("Pronto para simular.")
        self.scientific_status.setProperty("class", "status-readout")
        self.statusBar().addWidget(self.scientific_status, 1)
        self.statusBar().addPermanentWidget(QLabel("SI"))
        self.statusBar().addPermanentWidget(QLabel("Local"))
        self.statusBar().addPermanentWidget(QLabel(f"v{VERSION}"))

    def _refresh_scientific_status(self, *_args) -> None:
        page = self.stack.currentWidget()
        self.scientific_status.setText(getattr(page, "status_text", "LumenLab — pronto para simular. Modo local (offline)."))

    def navigate_to(self, page_index: int) -> None:
        self.stack.setCurrentIndex(page_index)
        self.action_save_experiment.setEnabled(page_index in (1, 2))
        for button in self._nav_buttons:
            button.setChecked(int(button.property("target_page")) == page_index)
        self._refresh_scientific_status()
