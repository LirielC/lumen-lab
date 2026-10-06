

import math


def wavelength_to_rgb(wavelength_nm: float) -> tuple[float, float, float]:
    







    
    wl = max(400.0, min(700.0, float(wavelength_nm)))

    if 400.0 <= wl < 440.0:
        r = -(wl - 440.0) / (440.0 - 400.0)
        g = 0.0
        b = 1.0
    elif 440.0 <= wl < 490.0:
        r = 0.0
        g = (wl - 440.0) / (490.0 - 440.0)
        b = 1.0
    elif 490.0 <= wl < 510.0:
        r = 0.0
        g = 1.0
        b = -(wl - 510.0) / (510.0 - 490.0)
    elif 510.0 <= wl < 580.0:
        r = (wl - 510.0) / (580.0 - 510.0)
        g = 1.0
        b = 0.0
    elif 580.0 <= wl < 645.0:
        r = 1.0
        g = -(wl - 645.0) / (645.0 - 580.0)
        b = 0.0
    else:  # 645.0 <= wl <= 700.0
        r = 1.0
        g = 0.0
        b = 0.0

    
    if 400.0 <= wl < 420.0:
        factor = 0.3 + 0.7 * (wl - 400.0) / (420.0 - 400.0)
    elif 650.0 <= wl <= 700.0:
        factor = 0.3 + 0.7 * (700.0 - wl) / (700.0 - 650.0)
    else:
        factor = 1.0

    
    gamma = 0.8
    r_adj = (r * factor) ** gamma if r > 0 else 0.0
    g_adj = (g * factor) ** gamma if g > 0 else 0.0
    b_adj = (b * factor) ** gamma if b > 0 else 0.0

    return (
        max(0.0, min(1.0, r_adj)),
        max(0.0, min(1.0, g_adj)),
        max(0.0, min(1.0, b_adj)),
    )


def wavelength_to_hex(wavelength_nm: float) -> str:
    
    r, g, b = wavelength_to_rgb(wavelength_nm)
    ir = int(round(r * 255))
    ig = int(round(g * 255))
    ib = int(round(b * 255))
    return f"#{ir:02X}{ig:02X}{ib:02X}"
