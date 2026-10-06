import math
import json
from app.adapters.outbound.export.experiment_file import experiment_data

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSplitter,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.adapters.inbound.qt.plots.intensity_plot import IntensityPlotWidget
from app.adapters.inbound.qt.styles.icons import scientific_icon
from app.adapters.inbound.qt.widgets.formula_card import FormulaCard
from app.adapters.inbound.qt.widgets.labeled_slider import LabeledSlider
from app.adapters.inbound.qt.widgets.parameter_card import ParameterCard
from app.adapters.inbound.qt.widgets.result_card import ResultCard
from app.adapters.inbound.qt.widgets.screen_pattern_widget import ScreenPatternWidget
from app.adapters.inbound.qt.widgets.segmented_control import SegmentedControl
from app.adapters.inbound.qt.widgets.slits_canvas import SlitsCanvas
from app.core.application.dto.responses import InterferenceResponse
from app.core.utils.formatting import format_didactic_number, format_ratio_percent


class InterferencePage(QWidget):

    statusTextChanged = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.last_response: InterferenceResponse | None = None
        self.status_text = "Fendas: aguardando simulação."
        self.reference_response = None

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(12, 10, 12, 8)
        root_layout.setSpacing(8)

        # -------------------------------------------------------------
        
        # -------------------------------------------------------------
        columns_layout = QHBoxLayout()
        columns_layout.setSpacing(10)

        # =============================================================
        
        # =============================================================
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setObjectName("parameterScroll")
        scroll_area.setFixedWidth(326)

        controls_container = QWidget()
        controls_layout = QVBoxLayout(controls_container)
        controls_layout.setContentsMargins(0, 0, 5, 0)
        controls_layout.setSpacing(6)

        
        lbl_params_title = QLabel("Parâmetros físicos")
        lbl_params_title.setProperty("class", "panel-title")
        controls_layout.addWidget(lbl_params_title)

        
        self.slit_control = SegmentedControl(["1 Fenda", "2 Fendas"], default_index=0)
        self.slit_control.setObjectName("slitModeControl")
        controls_layout.addWidget(self.slit_control)

        def section(title: str, *controls: QWidget) -> QGroupBox:
            panel = QGroupBox(title)
            panel.setProperty("class", "parameter-section")
            panel_layout = QVBoxLayout(panel)
            panel_layout.setContentsMargins(8, 10, 8, 7)
            panel_layout.setSpacing(2)
            for control in controls:
                panel_layout.addWidget(control)
            return panel

        self.slider_wavelength = LabeledSlider(
            label="Comprimento de onda (λ)",
            min_value=400.0,
            max_value=700.0,
            default_value=633.0,
            step=1.0,
            decimals=0,
            unit="nm",
            show_color_swatch=True,
        )

        self.slider_intensity = LabeledSlider(
            label="Intensidade inicial (I₀)",
            min_value=0.0,
            max_value=10.0,
            default_value=1.0,
            step=0.1,
            decimals=1,
            unit="rel",
        )
        controls_layout.addWidget(section("FONTE", self.slider_wavelength, self.slider_intensity))

        self.slider_width = LabeledSlider(
            label="Largura da fenda (a)",
            min_value=1.0,
            max_value=100.0,
            default_value=25.0,
            step=0.5,
            decimals=1,
            unit="µm",
        )

        self.slider_separation = LabeledSlider(
            label="Separação entre fendas (d)",
            min_value=2.0,
            max_value=300.0,
            default_value=60.0,
            step=1.0,
            decimals=1,
            unit="µm",
        )
        self.slider_separation.setVisible(False)
        controls_layout.addWidget(section("GEOMETRIA", self.slider_width, self.slider_separation))

        self.slider_incidence = LabeledSlider(
            label="Ângulo de incidência (α)",
            min_value=-30.0,
            max_value=30.0,
            default_value=0.0,
            step=0.5,
            decimals=1,
            unit="°",
        )

        self.slider_observation = LabeledSlider(
            label="Ângulo observado (θ)",
            min_value=-90.0,
            max_value=90.0,
            default_value=0.0,
            step=0.2,
            decimals=1,
            unit="°",
        )
        controls_layout.addWidget(section("OBSERVAÇÃO", self.slider_incidence, self.slider_observation))

        self.lbl_error = QLabel()
        self.lbl_error.setProperty("class", "error-msg")
        self.lbl_error.setWordWrap(True)
        self.lbl_error.setVisible(False)
        controls_layout.addWidget(self.lbl_error)

        
        btn_box = QHBoxLayout()
        btn_box.setSpacing(6)
        self.btn_reset = QPushButton("Restaurar")
        self.btn_export_csv = QPushButton("CSV")
        self.btn_export_plot = QPushButton("Imagem")
        self.btn_reset.setIcon(scientific_icon("restore"))
        self.btn_export_csv.setIcon(scientific_icon("file-type-csv"))
        self.btn_export_plot.setIcon(scientific_icon("photo"))
        for button in (self.btn_reset, self.btn_export_csv, self.btn_export_plot):
            button.setIconSize(QSize(16, 16))
            button.setProperty("class", "local-action")
            button.setFixedHeight(26)
            btn_box.addWidget(button)

        controls_layout.addLayout(btn_box)

        
        lbl_presets = QLabel("Configurações didáticas")
        lbl_presets.setProperty("class", "text-secondary")
        controls_layout.addWidget(lbl_presets)
        self.combo_presets = QComboBox()
        self.combo_presets.addItems([
            "1. Difração Padrão (1 Fenda, 633 nm)",
            "2. Interferência de Young (2 Fendas, 532 nm)",
            "3. Incidência Oblíqua (α = 5°)",
            "4. Comprimento de Onda Azul (450 nm)",
            "Personalizado",
        ])
        self.combo_presets.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.combo_presets.setMinimumContentsLength(12)
        self.combo_presets.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
        controls_layout.addWidget(self.combo_presets)

        comparison_actions = QHBoxLayout()
        self.btn_reference = QPushButton("Fixar referência")
        self.btn_clear_reference = QPushButton("Remover referência")
        self.btn_clear_reference.setEnabled(False)
        comparison_actions.addWidget(self.btn_reference)
        comparison_actions.addWidget(self.btn_clear_reference)
        controls_layout.addLayout(comparison_actions)
        self.lbl_reference = QLabel("Compare curvas normalizadas: fixe uma referência e altere os parâmetros.")
        self.lbl_reference.setWordWrap(True)
        self.lbl_reference.setProperty("class", "text-secondary")
        controls_layout.addWidget(self.lbl_reference)
        assumptions = QLabel("Modelo: Fraunhofer; luz monocromática e coerente; fendas idênticas. Desenho sem escala geométrica. Brilho visual relativo.")
        assumptions.setWordWrap(True)
        assumptions.setProperty("class", "text-secondary")
        controls_layout.addWidget(assumptions)

        self.formula_card = FormulaCard(title="Fundamentação Matemática")
        controls_layout.addWidget(self.formula_card)
        controls_layout.addStretch()

        scroll_area.setWidget(controls_container)
        columns_layout.addWidget(scroll_area)

        # =============================================================
        
        # =============================================================
        analysis_splitter = QSplitter(Qt.Orientation.Horizontal)
        analysis_splitter.setObjectName("analysisSplitter")
        analysis_splitter.setChildrenCollapsible(False)

        center_container = QWidget()
        center_layout = QVBoxLayout(center_container)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)

        self.canvas = SlitsCanvas()
        center_layout.addWidget(self.canvas, stretch=1)
        analysis_splitter.addWidget(center_container)

        # =============================================================
        
        # =============================================================
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)

        lbl_inst_title = QLabel("Instrumentação e análise")
        lbl_inst_title.setProperty("class", "panel-title")
        right_layout.addWidget(lbl_inst_title)

        
        plot_header = QHBoxLayout()
        self.btn_toggle_detail = QPushButton("Ampliar padrão")
        self.btn_toggle_detail.setCheckable(True)
        self.btn_toggle_detail.setProperty("class", "local-action")
        plot_header.addWidget(self.btn_toggle_detail)
        self.check_show_envelope = QCheckBox("Exibir envelope de difração")
        self.check_show_envelope.setVisible(False)
        plot_header.addWidget(self.check_show_envelope)
        plot_header.addStretch()
        right_layout.addLayout(plot_header)

        
        self.plot_widget = IntensityPlotWidget()
        right_layout.addWidget(self.plot_widget, stretch=3)

        
        self.screen_pattern = ScreenPatternWidget()
        right_layout.addWidget(self.screen_pattern, stretch=2)

        analysis_splitter.addWidget(right_container)
        analysis_splitter.setStretchFactor(0, 5)
        analysis_splitter.setStretchFactor(1, 4)
        analysis_splitter.setSizes([560, 440])
        columns_layout.addWidget(analysis_splitter, stretch=1)
        root_layout.addLayout(columns_layout, stretch=1)

        # =============================================================
        
        # =============================================================
        telemetry_bar = QFrame(self)
        telemetry_bar.setProperty("class", "telemetry-bar")
        telemetry_layout = QHBoxLayout(telemetry_bar)
        telemetry_layout.setContentsMargins(14, 6, 14, 6)

        
        self.lbl_telemetry = QLabel("I/I₀: 1.0000  |  I atual: 1.0000 rel  |  Ângulo θ: 0.0°  |  λ: 633 nm  |  Setup: 1 Fenda")
        self.lbl_telemetry.setProperty("class", "monospace-telemetry")
        self.lbl_telemetry.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        telemetry_layout.addWidget(self.lbl_telemetry)

        
        self.card_selected_intensity = ResultCard("Intensidade", "I = 1,0000")
        self.card_selected_intensity.setVisible(False)
        self.card_wavelength = ResultCard("Comprimento de Onda", "633 nm")
        self.card_wavelength.setVisible(False)
        self.card_config = ResultCard("Configuração", "1 Fenda")
        self.card_config.setVisible(False)
        telemetry_layout.addWidget(self.card_selected_intensity)
        telemetry_layout.addWidget(self.card_wavelength)
        telemetry_layout.addWidget(self.card_config)

        telemetry_bar.setVisible(False)

    def set_reference(self, response: InterferenceResponse | None) -> None:
        self.reference_response = response
        self.plot_widget.set_reference(response)
        self.btn_clear_reference.setEnabled(response is not None)
        if response is None:
            text = "Compare curvas normalizadas: fixe uma referência e altere os parâmetros."
        else:
            separation = f", d={response.slit_separation_um:g} µm" if response.slit_separation_um is not None else ""
            text = (f"Referência fixa: {response.slit_count} fenda(s), λ={response.wavelength_nm:g} nm, "
                    f"a={response.slit_width_um:g} µm{separation}, "
                    f"α={response.incidence_angle_deg:g}°, I₀={response.initial_intensity:g} rel. "
                    "O zoom acompanha a configuração atual. O mapa e a bancada mostram a curva atual.")
        self.lbl_reference.setText(text)
        self._update_export_metadata()

    def _update_export_metadata(self) -> None:
        if self.last_response is not None:
            data = {"current": experiment_data(self.last_response)}
            if self.reference_response is not None:
                data["reference"] = experiment_data(self.reference_response)
            self.plot_widget.experiment_metadata = json.dumps(data, ensure_ascii=False, allow_nan=False)

    def update_view(self, response: InterferenceResponse) -> None:
        self.last_response = response
        self._update_export_metadata()

        self.slider_wavelength.set_swatch_color(response.beam_color_hex)

        self.plot_widget.update_data(
            angles_deg=response.angles_deg,
            normalized_intensity=response.normalized_intensity,
            selected_angle_deg=response.selected_angle_deg,
            selected_intensity=response.selected_normalized_intensity,
            beam_color_hex=response.beam_color_hex,
            alpha_deg=response.incidence_angle_deg,
            wavelength_nm=response.wavelength_nm,
            width_um=response.slit_width_um,
            separation_um=response.slit_separation_um,
            slit_count=response.slit_count,
            initial_intensity=response.initial_intensity,
        )

        self.canvas.update_simulation(response)
        self.screen_pattern.update_simulation(response)

        abs_i_str = format_didactic_number(response.selected_intensity, precision=4)
        norm_i_str = format_didactic_number(response.selected_normalized_intensity, precision=4)
        pct_str = format_ratio_percent(response.selected_normalized_intensity, use_comma=True)

        self.card_selected_intensity.set_value(
            value=f"I = {abs_i_str}",
            subtitle=f"Intensidade normalizada:\nI/I₀ = {norm_i_str} ({pct_str})",
        )
        self.card_wavelength.set_value(
            value=f"{response.wavelength_nm:.0f} nm",
            subtitle="Espectro visível",
        )

        config_title = "1 Fenda" if response.slit_count == 1 else "2 Fendas"
        w_um = response.slit_width_um
        if response.slit_count == 1:
            config_sub = f"a = {w_um:.1f} µm"
        else:
            d_um = response.slit_separation_um or 0.0
            config_sub = f"a = {w_um:.1f} µm, d = {d_um:.1f} µm"
        self.card_config.set_value(config_title, config_sub)

        
        theta_str = f"{response.selected_angle_deg:+.1f}°" if response.selected_angle_deg != 0 else "0.0°"
        laser_label = "He-Ne" if math.isclose(response.wavelength_nm, 633.0, abs_tol=5.0) else "Laser"
        self.lbl_telemetry.setText(
            f"I/I₀: {norm_i_str}  |  I atual: {abs_i_str} rel  |  Ângulo θ: {theta_str}  |  "
            f"λ: {response.wavelength_nm:.1f} nm ({laser_label})  |  Setup: {config_title} ({config_sub})"
        )
        geometry = f"d {response.slit_separation_um:.2f} µm  |  " if response.slit_separation_um is not None else ""
        ratio_text = f"I/I₀ {norm_i_str}" if response.initial_intensity > 0 else "I₀ = 0 (fonte sem luz)"
        self.status_text = (
            f"Fendas | I = {abs_i_str} rel | {ratio_text} | λ {response.wavelength_nm:.0f} nm | "
            f"a {response.slit_width_um:.2f} µm | {geometry}"
            f"α {response.incidence_angle_deg:.2f}°  |  θ {response.selected_angle_deg:.2f}°  |  "
        )
        self.statusTextChanged.emit(self.status_text)

        self.formula_card.set_response(response)
        self.btn_export_csv.setEnabled(True)
        self.btn_export_plot.setEnabled(True)

    def set_error(self, message: str) -> None:
        
        self.lbl_error.setText(message)
        self.lbl_error.setVisible(True)
        self.last_response = None
        self.btn_export_csv.setEnabled(False)
        self.btn_export_plot.setEnabled(False)
        self.status_text = "Fendas: parâmetros inválidos. Gráfico anterior; exportação indisponível."
        self.statusTextChanged.emit(self.status_text)

    def clear_error(self) -> None:
        
        self.lbl_error.setVisible(False)
