

import pytest
from PySide6.QtWidgets import QApplication
from app.bootstrap.application import create_app


@pytest.fixture(scope="session")
def app_instance():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_interference_three_column_layout_and_components(app_instance) -> None:
    """Verifica se a tela de interferência possui as 4 saídas simultâneas e componentes requeridos."""
    _, container = create_app()
    int_page = container.interference_page
    controller = container.interference_controller

    # 1. Quatro saídas presentes e inicializadas
    assert int_page.canvas is not None
    assert int_page.screen_pattern is not None
    assert int_page.plot_widget is not None
    assert int_page.card_selected_intensity is not None

    # 2. Todas as saídas utilizam a mesma resposta científica do domínio
    resp = int_page.last_response
    assert resp is not None
    assert int_page.canvas._response is resp
    assert int_page.screen_pattern._response is resp

    # 3. Botões padronizados
    assert int_page.btn_reset.text() == "Restaurar"
    assert int_page.btn_export_csv.text() == "CSV"
    assert int_page.btn_export_plot.text() == "Imagem"

    # 4. Alternância 1 fenda vs 2 fendas e visibilidade de d
    assert int_page.slit_control.selected_index() == 0  # 1 fenda inicial
    assert int_page.slider_separation.isHidden()

    int_page.slit_control.set_selected_index(1)  # 2 fendas
    controller._on_slit_mode_changed(1, "2 Fendas")
    assert not int_page.slider_separation.isHidden()

    int_page.slit_control.set_selected_index(0)  # volta para 1 fenda
    controller._on_slit_mode_changed(0, "1 Fenda")
    assert int_page.slider_separation.isHidden()

    # 5. Seleção interativa de ângulo via gráfico e padrão
    int_page.plot_widget.angleSelected.emit(15.4)
    controller._run_simulation()
    assert pytest.approx(int_page.slider_observation.value(), abs=0.1) == 15.4
    assert pytest.approx(int_page.last_response.selected_angle_deg, abs=0.1) == 15.4

    int_page.screen_pattern.angleSelected.emit(-22.6)
    controller._run_simulation()
    assert pytest.approx(int_page.slider_observation.value(), abs=0.1) == -22.6
    assert pytest.approx(int_page.last_response.selected_angle_deg, abs=0.1) == -22.6
