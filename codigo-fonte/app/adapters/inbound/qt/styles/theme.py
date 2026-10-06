from dataclasses import asdict, dataclass

from PySide6.QtWidgets import QApplication

from app.adapters.outbound.resources.resource_resolver import get_resource_path


@dataclass(frozen=True)
class ThemePalette:
    window_bg: str
    surface: str
    surface_alt: str
    sidebar_bg: str
    border: str
    border_strong: str
    text_primary: str
    text_secondary: str
    text_muted: str
    accent: str
    accent_hover: str
    selection_bg: str
    input_bg: str
    disabled_bg: str
    disabled_text: str
    success: str
    warning: str
    error: str
    plot_bg: str
    grid: str


PALETTES = {
    "dark": ThemePalette(
        "#091321", "#101D2D", "#142438", "#0C1827", "#293E57", "#3B536E",
        "#EDF4FC", "#AEC0D5", "#768BA4", "#69B7FF", "#91CBFF", "#173A60",
        "#14263A", "#0D1927", "#586C84", "#62D3A5", "#E7B35A", "#FF7C89",
        "#0C1725", "#273C53",
    ),
}


def apply_theme(app: QApplication) -> None:
    palette = PALETTES["dark"]
    stylesheet = get_resource_path("app/adapters/inbound/qt/styles/theme.qss").read_text(encoding="utf-8")
    for token, value in asdict(palette).items():
        stylesheet = stylesheet.replace(f"{{{{{token}}}}}", value)
    app.setProperty("theme", "dark")
    app.setStyleSheet(stylesheet)
    for widget in app.allWidgets():
        apply_widget_theme = getattr(widget, "apply_theme", None)
        if callable(apply_widget_theme):
            apply_widget_theme(palette)
        widget.update()


def current_theme(app: QApplication) -> str:
    return "dark"


def current_palette(app: QApplication) -> ThemePalette:
    return PALETTES[current_theme(app)]
