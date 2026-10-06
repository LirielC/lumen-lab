

import pytest
from PySide6.QtWidgets import QApplication
from app.bootstrap.application import create_app


@pytest.fixture(scope="session")
def app_instance():
    
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_polarization_preset_switching_and_user_scenario_defect_fix(app_instance) -> None:
    """
    Após carregar 'Luz Polarizada Inicial — φ0=30°', alterar parâmetros para:
    - 3 polarizadores
    - I0 = 6.3
    - P1 = 88°
    - P2 = 90°
    - P3 = 90°
    O seletor de preset DEVE mudar para 'Personalizado'.
    """
    _, container = create_app()
    pol_page = container.polarization_page
    pol_controller = container.polarization_controller

    
    pol_controller.apply_preset("polarized_input")
    assert pol_page.combo_presets.currentIndex() == 3
    assert "φ₀ = 30°" in pol_page.combo_presets.currentText()
    assert pol_page.count_control.selected_index() == 1  
    assert pol_page.slider_initial_angle.value() == 30.0
    assert pol_page.slider_p1.value() == 45.0
    assert pol_page.slider_p2.value() == 90.0

    
    
    pol_page.count_control.set_selected_index(2)  
    
    pol_page.slider_intensity.set_value(6.3)
    
    pol_page.slider_p1.set_value(88.0)
    pol_page.slider_p2.set_value(90.0)
    pol_page.slider_p3.set_value(90.0)

    
    pol_controller._run_simulation()

    
    assert pol_page.combo_presets.currentIndex() == 4
    assert pol_page.combo_presets.currentText() == "Personalizado"

    
    # I1 ≈ 1.76913, I2 ≈ 1.76698, I3 ≈ 1.76698, T_tot ≈ 28.05%
    resp = pol_page.last_response
    assert resp is not None
    assert len(resp.stages) == 3
    assert resp.stages[0].output_intensity == pytest.approx(1.76913, abs=1e-3)
    assert resp.stages[1].output_intensity == pytest.approx(1.76698, abs=1e-3)
    assert resp.stages[2].output_intensity == pytest.approx(1.76698, abs=1e-3)
    assert resp.final_transmission_pct == pytest.approx(28.047, abs=1e-2)

    
    pol_controller.apply_preset("polarized_input")
    assert pol_page.combo_presets.currentIndex() == 3
    assert pol_page.count_control.selected_index() == 1
    assert pol_page.slider_initial_angle.value() == 30.0


def test_crossed_polarizers_zero_field_representation(app_instance) -> None:
    """
    Na configuração de eixos cruzados, a intensidade final é zero.
    NÃO apresentar 'Direção do Campo Elétrico: 90°'.
    Apresentar: 'Sem campo transmitido (E = 0)' e 'Último eixo do polarizador: 90.0°'.
    """
    _, container = create_app()
    pol_page = container.polarization_page
    pol_controller = container.polarization_controller

    
    pol_controller.apply_preset("crossed")

    resp = pol_page.last_response
    assert resp is not None
    assert resp.final_intensity == 0.0
    assert resp.final_field_amplitude == 0.0
    assert resp.final_field_direction_deg is None

    
    val_text = pol_page.card_field._value_label.text()
    sub_text = pol_page.card_field._subtitle_label.text()

    assert val_text == "Sem campo transmitido (E = 0)"
    assert "Último eixo do polarizador: 90.0°" in sub_text

    
    p2_field_item = pol_page.table.item(2, 5)  # 2 (P2), 5 (Campo)
    assert p2_field_item is not None
    assert "Sem campo" in p2_field_item.text()


def test_all_interference_presets(app_instance) -> None:
    
    _, container = create_app()
    int_page = container.interference_page
    int_controller = container.interference_controller

    presets_to_test = [
        ("single_slit", 0, 1, 633.0),
        ("double_slit", 1, 2, 532.0),
        ("oblique", 2, 2, 550.0),
        ("blue_vs_red", 3, 2, 450.0),
    ]

    for key, expected_idx, expected_slits, expected_wl in presets_to_test:
        int_controller.apply_preset(key)
        assert int_page.combo_presets.currentIndex() == expected_idx
        assert (int_page.slit_control.selected_index() + 1) == expected_slits
        assert int_page.slider_wavelength.value() == expected_wl

        
        int_page.slider_wavelength.set_value(expected_wl + 10.0)
        assert int_page.combo_presets.currentIndex() == 4
        assert int_page.combo_presets.currentText() == "Personalizado"


def test_all_polarization_presets(app_instance) -> None:
    
    _, container = create_app()
    pol_page = container.polarization_page
    pol_controller = container.polarization_controller

    presets_to_test = [
        ("cascade_0_45_90", 0, 3, 550.0),
        ("parallel", 1, 2, 600.0),
        ("crossed", 2, 2, 520.0),
        ("polarized_input", 3, 2, 650.0),
    ]

    for key, expected_idx, expected_count, expected_wl in presets_to_test:
        pol_controller.apply_preset(key)
        assert pol_page.combo_presets.currentIndex() == expected_idx
        assert (pol_page.count_control.selected_index() + 1) == expected_count
        assert pol_page.slider_wavelength.value() == expected_wl

        
        pol_page.slider_wavelength.set_value(expected_wl + 15.0)
        assert pol_page.combo_presets.currentIndex() == 4
        assert pol_page.combo_presets.currentText() == "Personalizado"
