

import math
import pytest
from PySide6.QtWidgets import QApplication
from app.bootstrap.application import create_app


@pytest.fixture(scope="session")
def app_instance():
    
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_exact_prompt_scenario(app_instance) -> None:
    """Valida a configuração exata informada pelo usuário:

    λ = 652 nm, a = 32.1 µm, d = 152.0 µm, α = 12.4°, θ = 27.3°, I₀ = 5.3.
    """
    _, container = create_app()
    page = container.interference_page
    ctrl = container.interference_controller

    
    ctrl.apply_preset("double_slit")
    assert page.combo_presets.currentIndex() == 1

    
    page.slider_wavelength.set_value(652.0)
    assert page.combo_presets.currentIndex() == 4
    assert page.combo_presets.currentText() == "Personalizado"

    
    page.slider_width.set_value(32.1)
    page.slider_separation.set_value(152.0)
    page.slider_incidence.set_value(12.4)
    page.slider_observation.set_value(27.3)
    page.slider_intensity.set_value(5.3)

    
    ctrl._run_simulation()

    resp = page.last_response
    assert resp is not None

    
    alpha_rad = math.radians(12.4)
    alpha_idx = [i for i, ang in enumerate(resp.angles_deg) if math.isclose(ang, 12.4, abs_tol=1e-5)][0]
    assert pytest.approx(resp.normalized_intensity[alpha_idx], abs=1e-12) == 1.0

    
    
    assert pytest.approx(resp.selected_normalized_intensity, rel=1e-4) == 4.3001477e-7
    assert pytest.approx(resp.selected_intensity, rel=1e-4) == 2.2790783e-6

    
    card_text = page.card_selected_intensity._value_label.text()
    assert "2,2791 × 10⁻⁶" in card_text or "2.2791e-06" in card_text or "2.2791e-6" in card_text
    card_sub = page.card_selected_intensity._subtitle_label.text()
    assert "4,3001 × 10⁻⁷" in card_sub or "4.3001e-07" in card_sub or "4.3001e-7" in card_sub

    
    page.btn_toggle_detail.setChecked(True)
    xlim = page.plot_widget.ax.get_xlim()
    
    center = (xlim[0] + xlim[1]) / 2.0
    assert pytest.approx(center, abs=0.5) == 12.4

    
    assert page.canvas._response is resp
    assert page.canvas._response.incidence_angle_deg == 12.4
