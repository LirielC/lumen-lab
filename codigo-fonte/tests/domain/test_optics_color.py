

from app.core.domain.physics.optics_color import (
    wavelength_to_hex,
    wavelength_to_rgb,
)


def test_wavelength_to_rgb_ranges() -> None:
    """Verifica que as cores RGB calculadas estão no intervalo [0, 1]."""
    for wl in range(400, 701, 10):
        r, g, b = wavelength_to_rgb(float(wl))
        assert 0.0 <= r <= 1.0
        assert 0.0 <= g <= 1.0
        assert 0.0 <= b <= 1.0


def test_wavelength_prominent_hues() -> None:
    """Verifica que o azul domina em 450nm, o verde em 530nm e o vermelho em 650nm."""
    
    r_b, g_b, b_b = wavelength_to_rgb(450.0)
    assert b_b > r_b and b_b > g_b

    
    r_g, g_g, b_g = wavelength_to_rgb(530.0)
    assert g_g > r_g and g_g > b_g

    
    r_r, g_r, b_r = wavelength_to_rgb(650.0)
    assert r_r > g_r and r_r > b_r


def test_wavelength_to_hex_format() -> None:
    """Verifica formatação da string hexadecimal."""
    hex_color = wavelength_to_hex(550.0)
    assert hex_color.startswith("#")
    assert len(hex_color) == 7
    
    int(hex_color[1:], 16)
