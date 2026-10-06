import pytest

from app.adapters.inbound.qt.plots.angular_view import angle_to_fraction, angular_view_limits, fraction_to_angle


def test_zoom_uses_first_single_slit_minima() -> None:
    limits = angular_view_limits(
        mode="detail", alpha_deg=0.0, wavelength_nm=500.0,
        slit_width_um=25.0,
    )
    assert limits == pytest.approx((-1.14599, 1.14599), abs=1e-5)


def test_detail_uses_envelope_zeros_for_double_slit() -> None:
    limits = angular_view_limits(
        mode="detail", alpha_deg=0.0, wavelength_nm=500.0,
        slit_width_um=10.0,
    )
    assert limits == pytest.approx((-2.86598, 2.86598), abs=1e-5)


@pytest.mark.parametrize(
    ("angle", "fraction"),
    [(3.0, -0.5), (4.0, 0.0), (5.0, 0.5), (6.0, 1.0), (7.0, 1.5), (24.6, 10.3)],
)
def test_physical_angle_to_screen_fraction_is_never_clamped(angle: float, fraction: float) -> None:
    limits = (4.0, 6.0)
    assert angle_to_fraction(angle, limits) == pytest.approx(fraction)
    assert fraction_to_angle(fraction, limits) == pytest.approx(angle)
