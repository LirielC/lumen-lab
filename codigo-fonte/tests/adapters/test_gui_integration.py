

import pytest
from PySide6.QtWidgets import QApplication, QAbstractSpinBox, QLabel, QPushButton, QToolBar
from app.bootstrap.application import create_app


@pytest.fixture(scope="session")
def app_instance():
    
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_main_window_and_controllers_instantiation(app_instance) -> None:
    """Verifica se a janela principal e os controladores inicializam com sucesso."""
    _, container = create_app()
    window = container.main_window

    assert window is not None
    assert window.stack.count() == 7
    assert window.findChildren(QToolBar) == []
    assert [action.text() for action in window.menuBar().actions()] == [
        "Arquivo", "Simulações", "Referência", "Ajuda"
    ]

    
    int_page = container.interference_page
    assert int_page.last_response is not None
    assert int_page.last_response.slit_count == 1
    assert int_page.last_response.wavelength_nm == 633.0
    assert int_page.card_selected_intensity._value_label.text() == "I = 1,0000"
    assert int_page.card_wavelength._value_label.text() == "633 nm"
    assert int_page.card_config._value_label.text() == "1 Fenda"
    assert "633.0 nm" in int_page.lbl_telemetry.text()

    
    pol_page = container.polarization_page
    assert pol_page.last_response is not None
    assert len(pol_page.last_response.stages) == 3
    assert pytest.approx(pol_page.last_response.final_intensity, rel=1e-5) == 0.125


def test_home_ctas_open_each_destination(app_instance) -> None:
    _, container = create_app()
    home = container.main_window.home_page
    destinations = []
    home.openInterferenceRequested.connect(lambda: destinations.append("fendas"))
    home.openPolarizationRequested.connect(lambda: destinations.append("polarizadores"))

    module_buttons = [button for button in home.findChildren(QPushButton) if button.text() == "Abrir"]
    module_buttons[0].click()
    module_buttons[1].click()

    assert destinations == ["fendas", "polarizadores"]
    assert all(button.height() == 32 for button in module_buttons)


def test_application_uses_dark_theme_only(app_instance) -> None:
    app, container = create_app()
    assert app.applicationName() == "LumenLab"
    assert container.main_window.windowTitle() == "LumenLab — Laboratório Computacional de Óptica"
    assert not container.main_window.windowIcon().isNull()
    assert any(label.text() == "LumenLab" for label in container.main_window.home_page.findChildren(QLabel))
    for button in container.main_window._nav_buttons:
        assert not button.icon().isNull()
        assert not button.icon().pixmap(24, 24).isNull()
    assert app.property("theme") == "dark"
    assert not hasattr(container.main_window, "appearance_actions")
    assert not hasattr(container.main_window, "btn_theme_toggle")


def test_numeric_controls_use_working_plus_minus_buttons(app_instance) -> None:
    _, container = create_app()
    control = container.interference_page.slider_wavelength
    spinbox = control._spinbox
    assert spinbox.buttonSymbols() == QAbstractSpinBox.ButtonSymbols.PlusMinus
    initial = spinbox.value()
    spinbox.stepUp()
    assert spinbox.value() == initial + spinbox.singleStep()
    spinbox.stepDown()
    assert spinbox.value() == initial


def test_reference_navigation_has_real_destinations(app_instance) -> None:
    _, container = create_app()
    window = container.main_window

    window.btn_examples.click()
    assert window.stack.currentWidget() is window.examples_page
    window.btn_units.click()
    assert window.stack.currentWidget() is window.units_page


def test_preset_switching_and_custom_transition(app_instance) -> None:
    """10. Carregar preset carrega todos os valores. 11. Alterar manualmente muda para Personalizado."""
    _, container = create_app()
    int_page = container.interference_page
    int_controller = container.interference_controller

    
    int_controller.apply_preset("double_slit")
    assert int_page.combo_presets.currentIndex() == 1  # 2. Interferência de Young
    assert int_page.slider_wavelength.value() == 532.0
    assert int_page.slider_width.value() == 10.0
    assert int_page.slider_separation.value() == 50.0

    
    int_page.slider_wavelength.set_value(652.0)
    
    assert int_page.combo_presets.currentIndex() == 4  # "Personalizado"
    assert int_page.combo_presets.currentText() == "Personalizado"

    
    int_page.slider_wavelength.set_value(532.0)
    assert int_page.combo_presets.currentIndex() == 1  


def test_canvas_and_plot_receive_same_scientific_result(app_instance) -> None:
    """13. O canvas recebe o mesmo resultado científico usado pelo gráfico."""
    _, container = create_app()
    int_page = container.interference_page

    assert int_page.canvas._response is not None
    assert int_page.canvas._response is int_page.last_response

    
    int_page.slider_wavelength.set_value(652.0)
    int_page.slider_width.set_value(32.1)
    int_page.slider_separation.set_value(152.0)
    int_page.slider_incidence.set_value(12.4)
    int_page.slider_observation.set_value(27.3)
    int_page.slider_intensity.set_value(5.3)

    
    container.interference_controller._run_simulation()

    resp = int_page.last_response
    assert resp is not None
    assert int_page.canvas._response is resp
    assert resp.incidence_angle_deg == 12.4
    assert resp.selected_angle_deg == 27.3
    
    val_text = int_page.card_selected_intensity._value_label.text()
    assert "× 10⁻" in val_text or "e-" in val_text


def test_invalid_input_does_not_crash_app(app_instance) -> None:
    """14. Entradas inválidas continuam não encerrando a aplicação."""
    _, container = create_app()
    int_page = container.interference_page
    int_controller = container.interference_controller

    
    int_controller.apply_preset("double_slit")
    
    int_page.slider_width.set_value(50.0)
    int_page.slider_separation.set_value(30.0)

    int_controller._run_simulation()

    
    assert not int_page.lbl_error.isHidden()
    assert "deve ser maior que a largura" in int_page.lbl_error.text()


def test_zoom_mode_toggling(app_instance) -> None:
    """4. Alternância entre Visão Geral e Zoom no Padrão."""
    _, container = create_app()
    int_page = container.interference_page

    
    int_page.btn_toggle_detail.setChecked(False)
    assert int_page.plot_widget._view_mode == "overview"
    assert int_page.plot_widget.ax.get_xlim() == (-90.0, 90.0)

    
    int_page.btn_toggle_detail.setChecked(True)
    assert int_page.btn_toggle_detail.text() == "Voltar à visão completa"
    assert int_page.plot_widget._view_mode == "detail"
    assert int_page.screen_pattern._view_mode == "detail"
    assert int_page.canvas._view_mode == "detail"
    xlim = int_page.plot_widget.ax.get_xlim()
    assert xlim[0] > -90.0 or xlim[1] < 90.0

def test_marker_outside_detail_is_hidden(app_instance) -> None:
    _, container = create_app()
    page = container.interference_page
    page.slider_observation.set_value(24.6)
    container.interference_controller._run_simulation()
    page.btn_toggle_detail.setChecked(True)

    assert not page.plot_widget._marker_point.get_visible()
    assert not page.plot_widget._marker_v_line.get_visible()
    assert not page.plot_widget._marker_label.get_visible()
