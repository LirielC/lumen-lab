

import math

SUPERSCRIPT_MAP = {
    "-": "⁻",
    "+": "⁺",
    "0": "⁰",
    "1": "¹",
    "2": "²",
    "3": "³",
    "4": "⁴",
    "5": "⁵",
    "6": "⁶",
    "7": "⁷",
    "8": "⁸",
    "9": "⁹",
}


def to_superscript(exp: int) -> str:
    
    return "".join(SUPERSCRIPT_MAP.get(c, c) for c in str(exp))


def format_didactic_number(
    value: float,
    precision: int = 4,
    sci_threshold: float = 1e-3,
) -> str:
    







    if not math.isfinite(value):
        return "—"

    abs_val = abs(value)
    if value == 0.0:
        return "0," + ("0" * precision)

    if sci_threshold <= abs_val <= 9999.0:
        return f"{value:.{precision}f}".replace(".", ",")

    
    s_raw = f"{value:.{precision}e}"
    mantissa, exp_part = s_raw.split("e")
    exp_int = int(exp_part)
    mantissa_formatted = mantissa.replace(".", ",")
    return f"{mantissa_formatted} × 10{to_superscript(exp_int)}"


def format_intensity(value: float, precision: int = 4, sci_threshold: float = 1e-3) -> str:
    





    if not math.isfinite(value):
        return "—"

    abs_val = abs(value)
    if value == 0.0:
        return f"{0.0:.{precision}f}"

    if sci_threshold <= abs_val <= 9999.0:
        return f"{value:.{precision}f}"

    
    return f"{value:.{precision}e}"


def format_ratio_percent(ratio: float, use_comma: bool = False) -> str:
    





    if not math.isfinite(ratio):
        return "—%"

    pct = ratio * 100.0
    abs_pct = abs(pct)

    if ratio == 0.0:
        return "0,00%" if use_comma else "0.00%"

    if abs_pct >= 0.01:
        res = f"{pct:.2f}%"
        return res.replace(".", ",") if use_comma else res

    res = f"{pct:.2e}%"
    if use_comma:
        mantissa, exp_part = res[:-1].split("e")
        exp_int = int(exp_part)
        return f"{mantissa.replace('.', ',')} × 10{to_superscript(exp_int)}%"
    return res
