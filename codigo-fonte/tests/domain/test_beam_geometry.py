

import math
import pytest

from app.adapters.inbound.qt.widgets.slits_canvas import incident_ray_start_y, observation_ray_endpoint


def calculate_incident_ray_slope(alpha_deg: float) -> tuple[float, float]:
    







    alpha_rad = math.radians(alpha_deg)
    
    dx = math.cos(alpha_rad)
    dy = -math.sin(alpha_rad)  
    return dx, dy


def test_incident_beam_geometry() -> None:
    """Verifica que alpha = 12.4° gera uma direção inclinada e com sinal coerente."""
    dx_0, dy_0 = calculate_incident_ray_slope(0.0)
    assert math.isclose(dx_0, 1.0)
    assert math.isclose(dy_0, 0.0)

    # alpha = 12.4°
    dx_pos, dy_pos = calculate_incident_ray_slope(12.4)
    assert dx_pos > 0.95
    
    assert dy_pos < 0.0
    angle_measured = math.degrees(math.atan2(-dy_pos, dx_pos))
    assert math.isclose(angle_measured, 12.4, abs_tol=1e-5)

    
    dx_neg, dy_neg = calculate_incident_ray_slope(-10.0)
    assert dy_neg > 0.0
    angle_neg_measured = math.degrees(math.atan2(-dy_neg, dx_neg))
    assert math.isclose(angle_neg_measured, -10.0, abs_tol=1e-5)


@pytest.mark.parametrize("alpha_deg", [-30.0, -12.4, 0.0, 12.4, 30.0])
def test_incident_ray_drawn_at_requested_angle(alpha_deg: float) -> None:
    start_x, slit_x, slit_y = 240.0, 320.0, 200.0
    start_y = incident_ray_start_y(alpha_deg, start_x, slit_x, slit_y)
    measured = math.degrees(math.atan2(start_y - slit_y, slit_x - start_x))
    assert measured == pytest.approx(alpha_deg)


def test_observation_ray_uses_tangent_geometry() -> None:
    x, y, reaches_screen = observation_ray_endpoint(25.0, 100.0, 300.0, 200.0, 0.0, 400.0)
    assert reaches_screen
    assert x == 300.0
    assert y == pytest.approx(200.0 - 200.0 * math.tan(math.radians(25.0)))
    assert math.degrees(math.atan2(200.0 - y, x - 100.0)) == pytest.approx(25.0)


def test_observation_ray_saturates_at_boundary_without_changing_direction() -> None:
    x, y, reaches_screen = observation_ray_endpoint(89.999, 100.0, 300.0, 200.0, 20.0, 380.0)
    assert not reaches_screen
    assert 100.0 <= x <= 300.0
    assert y == pytest.approx(20.0)


@pytest.mark.parametrize("theta_deg", [0, 10, 18, 25, 45, 80, 89, -10, -18, -25, -45, -80, -89])
def test_observation_ray_preserves_requested_direction(theta_deg: float) -> None:
    origin_x, center_y = 420.0, 175.0
    x, y, _ = observation_ray_endpoint(theta_deg, origin_x, 932.0, center_y, 25.0, 325.0)
    measured = math.degrees(math.atan2(center_y - y, x - origin_x))
    assert measured == pytest.approx(theta_deg, abs=1e-10)
    assert 420.0 <= x <= 932.0
    assert 25.0 <= y <= 325.0
