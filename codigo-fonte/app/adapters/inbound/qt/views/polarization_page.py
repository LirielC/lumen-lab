
from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.adapters.inbound.qt.widgets.formula_card import FormulaCard
from app.adapters.inbound.qt.styles.icons import scientific_icon
from app.adapters.inbound.qt.widgets.labeled_slider import LabeledSlider
from app.adapters.inbound.qt.widgets.parameter_card import ParameterCard
from app.adapters.inbound.qt.widgets.polarizers_canvas import PolarizersCanvas
from app.adapters.inbound.qt.widgets.result_card import ResultCard
from app.adapters.inbound.qt.widgets.segmented_control import SegmentedControl
from app.core.application.dto.responses import PolarizationResponse
from app.core.utils.formatting import format_intensity, format_ratio_percent


class PolarizationPage(QWidget):

    statusTextChanged = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.last_response: PolarizationResponse | None = None
        self.status_text = "Polarização: aguardando simulação."

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(18, 16, 18, 12)
        main_layout.setSpacing(18)

        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setFixedWidth(380)

        controls_container = QWidget()
        controls_layout = QVBoxLayout(controls_container)
        controls_layout.setContentsMargins(0, 0, 8, 0)
        controls_layout.setSpacing(14)

        presets_card = ParameterCard("Configurações didáticas")
        self.combo_presets = QComboBox()
        self.combo_presets.addItems([
            "1. Cascata Clássica (0°, 45°, 90°)",
            "2. Eixos Paralelos (0°, 0°)",
            "3. Eixos Cruzados a 90° (Bloqueio Total)",
            "4. Luz Polarizada Inicial (φ₀ = 30°)",
            "Personalizado",
        ])
        presets_card.add_widget(self.combo_presets)
        controls_layout.addWidget(presets_card)

        params_card = ParameterCard(
            "Parâmetros físicos",
            "Configure o estado da luz incidente e os eixos dos polarizadores.",
        )

        type_label = QLabel("Estado inicial da luz incidente")
        type_label.setProperty("class", "text-secondary")
        params_card.add_widget(type_label)

        self.light_type_control = SegmentedControl(
            ["Não Polarizada", "Polarizada"],
            default_index=0,
        )
        params_card.add_widget(self.light_type_control)

        self.slider_initial_angle = LabeledSlider(
            label="Ângulo Inicial de Polarização (φ₀)",
            min_value=0.0,
            max_value=180.0,
            default_value=0.0,
            step=1.0,
            decimals=0,
            unit="°",
        )
        self.slider_initial_angle.setVisible(False)
        params_card.add_widget(self.slider_initial_angle)

        count_label = QLabel("Quantidade de polarizadores")
        count_label.setProperty("class", "text-secondary")
        params_card.add_widget(count_label)

        self.count_control = SegmentedControl(
            ["1 Polarizador", "2 Polarizadores", "3 Polarizadores"],
            default_index=2,
        )
        params_card.add_widget(self.count_control)

        self.slider_wavelength = LabeledSlider(
            label="Comprimento de Onda (λ)",
            min_value=400.0,
            max_value=700.0,
            default_value=550.0,
            step=1.0,
            decimals=0,
            unit="nm",
            show_color_swatch=True,
        )
        params_card.add_widget(self.slider_wavelength)

        self.slider_intensity = LabeledSlider(
            label="Intensidade Inicial (I₀)",
            min_value=0.0,
            max_value=10.0,
            default_value=1.0,
            step=0.1,
            decimals=1,
            unit="rel",
        )
        params_card.add_widget(self.slider_intensity)

        p_label = QLabel("Orientação dos eixos de polarização")
        p_label.setProperty("class", "text-secondary")
        params_card.add_widget(p_label)

        self.slider_p1 = LabeledSlider(
            label="Eixo do Polarizador 1 (φ₁)",
            min_value=0.0,
            max_value=180.0,
            default_value=0.0,
            step=1.0,
            decimals=0,
            unit="°",
        )
        params_card.add_widget(self.slider_p1)

        self.slider_p2 = LabeledSlider(
            label="Eixo do Polarizador 2 (φ₂)",
            min_value=0.0,
            max_value=180.0,
            default_value=45.0,
            step=1.0,
            decimals=0,
            unit="°",
        )
        params_card.add_widget(self.slider_p2)

        self.slider_p3 = LabeledSlider(
            label="Eixo do Polarizador 3 (φ₃)",
            min_value=0.0,
            max_value=180.0,
            default_value=90.0,
            step=1.0,
            decimals=0,
            unit="°",
        )
        params_card.add_widget(self.slider_p3)

        self.lbl_error = QLabel()
        self.lbl_error.setProperty("class", "error-msg")
        self.lbl_error.setWordWrap(True)
        self.lbl_error.setVisible(False)
        params_card.add_widget(self.lbl_error)

        controls_layout.addWidget(params_card)

        btn_box = QHBoxLayout()
        self.btn_reset = QPushButton("Restaurar parâmetros")
        self.btn_export_csv = QPushButton("CSV")
        self.btn_reset.setIcon(scientific_icon("restore"))
        self.btn_export_csv.setIcon(scientific_icon("file-type-csv"))
        for button in (self.btn_reset, self.btn_export_csv):
            button.setIconSize(QSize(16, 16))
            button.setProperty("class", "local-action")
            button.setFixedHeight(32)

        btn_box.addWidget(self.btn_reset)
        btn_box.addWidget(self.btn_export_csv)
        btn_box.addStretch()
        controls_layout.addLayout(btn_box)

        self.formula_card = FormulaCard(title="Lei de Malus & Equações")
        controls_layout.addWidget(self.formula_card)
        assumptions = QLabel("Modelo: polarizadores lineares ideais, sem absorção adicional, reflexão ou dispersão. λ controla a cor, não a Lei de Malus. Desenho sem escala geométrica.")
        assumptions.setWordWrap(True)
        assumptions.setProperty("class", "text-secondary")
        controls_layout.addWidget(assumptions)

        controls_layout.addStretch()
        scroll_area.setWidget(controls_container)
        main_layout.addWidget(scroll_area)

        
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(14)

        self.canvas = PolarizersCanvas()
        right_layout.addWidget(self.canvas, stretch=2)

        table_card = ParameterCard("Estágios da cascata de polarização")
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Etapa",
            "Eixo do Polarizador",
            "Intensidade de Saída",
            "Transmissão Etapa",
            "Transmissão Total",
            "Amplitude de Campo (E/E₀)",
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setMinimumHeight(172)
        self.table.verticalHeader().setDefaultSectionSize(30)
        table_card.add_widget(self.table)
        right_layout.addWidget(table_card, stretch=1)

        results_row = QHBoxLayout()
        results_row.setSpacing(12)

        self.card_final_intensity = ResultCard(
            title="Intensidade Final Transmitida",
            initial_value="0.1250",
            unit="relativa",
            subtitle="T_total = 12.5%",
        )
        results_row.addWidget(self.card_final_intensity)

        self.card_field = ResultCard(
            title="Direção do Campo Elétrico",
            initial_value="90.0°",
            subtitle="Alinhado ao último polarizador",
        )
        results_row.addWidget(self.card_field)

        self.card_wavelength = ResultCard(
            title="Comprimento de Onda",
            initial_value="550 nm",
            subtitle="Matiz do feixe",
        )
        results_row.addWidget(self.card_wavelength)

        right_layout.addLayout(results_row)
        main_layout.addWidget(right_container, stretch=1)

    def update_view(self, response: PolarizationResponse) -> None:
        self.last_response = response

        self.slider_wavelength.set_swatch_color(response.beam_color_hex)

        self.canvas.update_simulation(response)

        num_rows = len(response.stages) + 1  
        self.table.setRowCount(num_rows)

        # 0: Entrada
        item_in_name = QTableWidgetItem("Entrada (Fonte)")
        in_axis_txt = (
            f"{response.initial_angle_deg:.0f}°"
            if response.initially_polarized and response.initial_angle_deg is not None
            else "Isotrópica"
        )
        item_in_axis = QTableWidgetItem(in_axis_txt)
        item_in_intensity = QTableWidgetItem(format_intensity(response.initial_intensity))
        item_in_stage_t = QTableWidgetItem("100.0%" if response.initial_intensity > 0 else "—")
        item_in_cum_t = QTableWidgetItem("100.0%" if response.initial_intensity > 0 else "—")
        item_in_field = QTableWidgetItem("1.0000" if response.initial_intensity > 0 else "0.0000 (Sem campo)")

        for col, item in enumerate([
            item_in_name,
            item_in_axis,
            item_in_intensity,
            item_in_stage_t,
            item_in_cum_t,
            item_in_field,
        ]):
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(0, col, item)

        for r_idx, stage in enumerate(response.stages, start=1):
            name_item = QTableWidgetItem(f"Polarizador {stage.index} (P{stage.index})")
            axis_item = QTableWidgetItem(f"{stage.axis_angle_deg:.1f}°")
            out_i_item = QTableWidgetItem(format_intensity(stage.output_intensity))
            stage_t_item = QTableWidgetItem(format_ratio_percent(stage.stage_transmission_pct / 100))
            cum_t_item = QTableWidgetItem(format_ratio_percent(stage.cumulative_transmission_pct / 100))
            if stage.field_direction_deg is not None:
                field_txt = f"{format_intensity(stage.relative_field_amplitude)} ({stage.field_direction_deg:.1f}°)"
            else:
                field_txt = "0.0000 (Sem campo)"
            field_item = QTableWidgetItem(field_txt)

            for col, item in enumerate([
                name_item,
                axis_item,
                out_i_item,
                stage_t_item,
                cum_t_item,
                field_item,
            ]):
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(r_idx, col, item)

        self.card_final_intensity.set_value(
            value=format_intensity(response.final_intensity),
            subtitle=f"Transmissão = {format_ratio_percent(response.final_transmission_pct / 100)} de I₀" if response.initial_intensity > 0 else "Fonte sem luz (I₀ = 0)",
        )

        if response.final_field_direction_deg is not None:
            self.card_field.set_value(
                value=f"{response.final_field_direction_deg:.1f}°",
                subtitle="Polarização linear resultante",
            )
        else:
            last_axis = response.stages[-1].axis_angle_deg if response.stages else 0.0
            self.card_field.set_value(
                value="Sem campo transmitido (E = 0)",
                subtitle=f"Último eixo do polarizador: {last_axis:.1f}°",
            )

        self.card_wavelength.set_value(
            value=f"{response.wavelength_nm:.0f} nm",
            subtitle="Espectro visível",
        )

        self.formula_card.set_response(response)
        self.status_text = (
            f"Polarização | λ {response.wavelength_nm:.0f} nm | {len(response.stages)} polarizadores | "
            f"I final = {format_intensity(response.final_intensity)} rel | "
            + (f"T = {format_ratio_percent(response.final_transmission_pct / 100)}" if response.initial_intensity > 0 else "Fonte sem luz (I₀ = 0)")
        )
        self.statusTextChanged.emit(self.status_text)

    def set_error(self, message: str) -> None:
        
        self.lbl_error.setText(message)
        self.lbl_error.setVisible(True)

    def clear_error(self) -> None:
        
        self.lbl_error.setVisible(False)
