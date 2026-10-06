

import pytest
from PySide6.QtGui import QImage, QPainter
from PySide6.QtCore import QSize

from app.adapters.inbound.qt.widgets.slits_canvas import SlitsCanvas
from app.core.application.dto.requests import InterferenceRequest
from app.core.application.use_cases.simulate_interference import SimulateInterferenceUseCase


from PySide6.QtWidgets import QApplication

@pytest.fixture(scope="session")
def app_instance():
    
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def use_case():
    return SimulateInterferenceUseCase()


def render_canvas_to_image(canvas: SlitsCanvas, size: QSize = QSize(800, 300)) -> QImage:
    
    canvas.resize(size)
    image = QImage(size, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(0)
    canvas.render(image)
    return image


def test_visual_case_1_oblique_incidence_positive_observation(app_instance, use_case):
    """CASO 1: α = -25°, θ = +25°."""
    req = InterferenceRequest(
        slit_count=1,
        slit_width_um=25.0,
        slit_separation_um=None,
        wavelength_nm=633.0,
        incidence_angle_deg=-25.0,
        observation_angle_deg=25.0,
        initial_intensity=3.2,
    )
    resp = use_case.execute(req)
    canvas = SlitsCanvas()
    canvas.update_simulation(resp)

    img = render_canvas_to_image(canvas, QSize(800, 300))
    assert not img.isNull()
    assert canvas.toolTip() != ""


def test_visual_case_2_peak_alignment(app_instance, use_case):
    """CASO 2: α = -25°, θ = -25° (alinhamento no pico máximo)."""
    req = InterferenceRequest(
        slit_count=1,
        slit_width_um=25.0,
        slit_separation_um=None,
        wavelength_nm=633.0,
        incidence_angle_deg=-25.0,
        observation_angle_deg=-25.0,
        initial_intensity=3.2,
    )
    resp = use_case.execute(req)
    canvas = SlitsCanvas()
    canvas.update_simulation(resp)

    img = render_canvas_to_image(canvas, QSize(800, 300))
    assert not img.isNull()


def test_visual_case_3_mirrored_angles(app_instance, use_case):
    """CASO 3: α = +25°, θ = +25° (espelhado)."""
    req = InterferenceRequest(
        slit_count=1,
        slit_width_um=25.0,
        slit_separation_um=None,
        wavelength_nm=633.0,
        incidence_angle_deg=25.0,
        observation_angle_deg=25.0,
        initial_intensity=3.2,
    )
    resp = use_case.execute(req)
    canvas = SlitsCanvas()
    canvas.update_simulation(resp)

    img = render_canvas_to_image(canvas, QSize(800, 300))
    assert not img.isNull()


def test_visual_case_4_normal_incidence_center(app_instance, use_case):
    """CASO 4: α = 0°, θ = 0° (feixe alinhado à normal)."""
    req = InterferenceRequest(
        slit_count=1,
        slit_width_um=20.0,
        slit_separation_um=None,
        wavelength_nm=550.0,
        incidence_angle_deg=0.0,
        observation_angle_deg=0.0,
        initial_intensity=1.0,
    )
    resp = use_case.execute(req)
    canvas = SlitsCanvas()
    canvas.update_simulation(resp)

    img = render_canvas_to_image(canvas, QSize(800, 300))
    assert not img.isNull()


def test_visual_case_5_extreme_angles(app_instance, use_case):
    """CASO 5: α = +30° (max interface), θ = -60°."""
    req = InterferenceRequest(
        slit_count=1,
        slit_width_um=20.0,
        slit_separation_um=None,
        wavelength_nm=550.0,
        incidence_angle_deg=30.0,
        observation_angle_deg=-60.0,
        initial_intensity=1.0,
    )
    resp = use_case.execute(req)
    canvas = SlitsCanvas()
    canvas.update_simulation(resp)

    
    img_small = render_canvas_to_image(canvas, QSize(500, 240))
    assert not img_small.isNull()

    img_large = render_canvas_to_image(canvas, QSize(1600, 500))
    assert not img_large.isNull()
