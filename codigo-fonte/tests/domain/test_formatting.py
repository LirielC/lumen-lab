

import pytest
from app.core.utils.formatting import format_didactic_number, format_intensity, format_ratio_percent


def test_format_intensity_exact_zero() -> None:
    """Zero exato é exibido como 0.0000."""
    assert format_intensity(0.0) == "0.0000"


def test_format_intensity_standard_decimals() -> None:
    """Valores de magnitude regular usam 4 casas decimais."""
    assert format_intensity(1.0) == "1.0000"
    assert format_intensity(0.5) == "0.5000"
    assert format_intensity(0.125) == "0.1250"
    assert format_intensity(5.3) == "5.3000"


def test_format_intensity_small_scientific_notation() -> None:
    """Valores menores que 10^-3 são formatados em notação científica."""
    val = 2.2790783e-6
    formatted = format_intensity(val)
    assert "e-06" in formatted or "e-6" in formatted
    assert formatted.startswith("2.2791")

    ratio = 4.3001477e-7
    ratio_str = format_intensity(ratio)
    assert "e-07" in ratio_str or "e-7" in ratio_str
    assert ratio_str.startswith("4.3001")


def test_format_ratio_percent() -> None:
    """Formatação percentual para valores regulares e sub-centésimos."""
    assert format_ratio_percent(1.0) == "100.00%"
    assert format_ratio_percent(0.125) == "12.50%"
    assert format_ratio_percent(0.0) == "0.00%"

    small_pct = format_ratio_percent(4.3001477e-7)
    assert "e-" in small_pct


@pytest.mark.parametrize("value", [2.82573812082077e-11, 1e-20, 1e-100])
def test_positive_values_are_not_formatted_as_zero(value: float) -> None:
    assert float(format_intensity(value)) == pytest.approx(value, rel=1e-4, abs=0)
    assert "× 10" in format_didactic_number(value)
    assert float(format_ratio_percent(value).rstrip("%")) > 0
