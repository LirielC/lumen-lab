

import csv
import math
from types import SimpleNamespace
from dataclasses import replace
from pathlib import Path
from unittest.mock import Mock, patch

import numpy as np
import pytest
from PySide6.QtGui import QColor, QTextDocument
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from app.bootstrap.application import create_app
from app.core.application.dto.requests import InterferenceRequest, PolarizationRequest


@pytest.fixture
def container():
    app = QApplication.instance() or QApplication([])
    _, container = create_app()
    yield container
    container.interference_controller._debounce_timer.stop()
    container.polarization_controller._debounce_timer.stop()
    container.main_window.close()
    app.processEvents()


def test_weak_field_retains_intensity_direction_and_csv_precision(container, tmp_path: Path):
    response = container.polarization_use_case.execute(
        PolarizationRequest(3, 550, 1.0, True, 0, (89, 178, 87))
    )
    page = container.polarization_page
    page.update_view(response)
    expected = 2.82573812082077e-11
    assert float(page.card_final_intensity._value_label.text()) == pytest.approx(expected, rel=1e-4, abs=0)
    assert response.final_field_direction_deg == pytest.approx(87)
    painter = Mock()
    page.canvas._draw_field_vector(painter, 300, 100, np.radians(87), response.final_field_amplitude, QColor('white'))
    labels = [call.args[-1] for call in painter.drawText.call_args_list]
    assert any('abaixo da escala visual' in text for text in labels)
    assert not any('E = 0' in text for text in labels)
    tiny = container.polarization_use_case.execute(
        PolarizationRequest(3, 550, 1.0, True, 0, (89.999, 179.998, 89.999))
    )
    assert 0 < tiny.final_field_amplitude < 1e-12
    assert tiny.final_field_direction_deg is not None
    path = tmp_path / 'weak.csv'
    container.file_exporter.export_csv_polarization(response, path)
    row = list(csv.reader(path.open(encoding='utf-8')))[-1]
    assert float(row[3]) == response.final_intensity
    assert float(row[6]) == response.final_field_amplitude
    
    response = replace(response, stages=(replace(response.stages[0], output_intensity=1e-100),))
    container.file_exporter.export_csv_polarization(response, path)
    assert float(list(csv.reader(path.open(encoding='utf-8')))[1][3]) == 1e-100
    slits = replace(container.interference_page.last_response,
                    angles_deg=np.array([0.0]), normalized_intensity=np.array([1e-100]),
                    scaled_relative_intensity=np.array([1e-101]))
    container.file_exporter.export_csv_interference(slits, path)
    row = list(csv.reader(path.open(encoding='utf-8')))[1]
    assert float(row[1]) == 1e-100 and float(row[2]) == 1e-101


def test_invalid_geometry_blocks_both_exports_even_during_debounce(container):
    page = container.interference_page
    ctrl = container.interference_controller
    page.combo_presets.setCurrentIndex(1)
    page.slider_width._spinbox.setValue(100)
    page.slider_separation._spinbox.setValue(50)
    assert not page.btn_export_csv.isEnabled()
    assert not page.btn_export_plot.isEnabled()
    with patch('PySide6.QtWidgets.QFileDialog.getSaveFileName') as dialog:
        ctrl.export_csv()
        ctrl.export_plot()
        dialog.assert_not_called()
    assert page.last_response is None
    assert not page.lbl_error.isHidden()
    page.btn_reset.click()
    assert page.last_response is not None
    assert page.btn_export_csv.isEnabled() and page.btn_export_plot.isEnabled()


def test_status_tracks_active_module_and_keeps_absolute_intensity(container):
    window, slits, polarizers = container.main_window, container.interference_page, container.polarization_page
    window.navigate_to(window.PAGE_INTERFERENCE)
    slits.slider_intensity._spinbox.setValue(3.2)
    QTest.qWait(100)
    assert 'I = 3,2000 rel' in window.scientific_status.text()
    window.navigate_to(window.PAGE_POLARIZATION)
    assert '550 nm' in window.scientific_status.text()
    assert 'I final = 0.1250 rel' in window.scientific_status.text()
    slits.slider_wavelength._spinbox.setValue(700)
    QTest.qWait(100)
    assert '550 nm' in window.scientific_status.text()
    polarizers.slider_wavelength._spinbox.setValue(600)
    QTest.qWait(100)
    assert '600 nm' in window.scientific_status.text()
    window.navigate_to(window.PAGE_HELP)
    assert 'λ' not in window.scientific_status.text()


def test_zero_input_is_available_in_both_modules(container):
    slits, pol = container.interference_page, container.polarization_page
    for page in (slits, pol):
        page.slider_intensity._spinbox.setValue(0)
    QTest.qWait(100)
    assert slits.last_response.initial_intensity == 0
    assert slits.last_response.selected_intensity == 0
    assert not np.any(slits.screen_pattern._intensities)
    assert 'teórico' in slits.plot_widget.ax.get_ylabel()
    assert 'indefinido' in slits.formula_card._text_label.toPlainText()
    assert pol.last_response.initial_intensity == 0
    assert pol.last_response.final_intensity == 0
    assert pol.last_response.final_field_direction_deg is None
    assert pol.table.item(0, 5).text() == '0.0000 (Sem campo)'


def test_dark_plot_title_and_polarization_layout(container, tmp_path: Path):
    window, slits, pol = container.main_window, container.interference_page, container.polarization_page
    assert QColor(slits.plot_widget.ax._left_title.get_color()).lightnessF() > 0.8
    slits.plot_widget.export_image(tmp_path / 'plot.png')
    assert (tmp_path / 'plot.png').stat().st_size > 0
    window.resize(1366, 768)
    window.show()
    window.navigate_to(window.PAGE_POLARIZATION)
    QTest.qWait(100)
    assert pol.table.verticalScrollBar().maximum() == 0
    painter = Mock()
    pol.canvas._draw_field_vector(painter, 300, 100, 0, 0.5, QColor('white'))
    assert painter.drawLine.call_count == 5  
    painter.drawEllipse.assert_not_called()


@pytest.mark.parametrize("phase_cycles", [-.5, 0, .5, 1])
def test_hover_preserves_fractional_interference_phase(container, phase_cycles):
    theta = math.degrees(math.asin(phase_cycles * .01))
    response = container.interference_use_case.execute(InterferenceRequest(2, 500, 10, 50, 0, theta, 1))
    container.interference_page.update_view(response)
    plot = container.interference_page.plot_widget
    plot._on_mouse_move(SimpleNamespace(inaxes=plot.ax, xdata=theta))
    text = plot._hover_label.get_text()
    assert "ordem m" not in text
    assert float(text.split("dq/λ = ")[1]) == pytest.approx(phase_cycles, abs=1e-4)


def test_formula_card_preserves_text_and_collapsed_state(container):
    card = container.interference_page.formula_card
    source = "Condição & limite:\n  0 < I/I₀ < 1\n\nβ = 2,5 × 10⁻³"
    card.set_content(source)
    document = QTextDocument()
    document.setHtml(card._text_label.toHtml())
    assert " ".join(document.toPlainText().split()) == " ".join(source.split())
    card._toggle_expanded()
    assert card._content_widget.isHidden()
    card.set_content(source)
    assert card._content_widget.isHidden()
    card._toggle_expanded()
    assert not card._content_widget.isHidden()


def test_mathematical_sections_render_all_models_and_special_values(container):
    from PySide6.QtCore import QUrl
    from app.adapters.inbound.qt.widgets.math_document import equation_image, math_number

    requests = [InterferenceRequest(1, 633, 25, None, 0, 1.2, 2),
                InterferenceRequest(2, 500, 10, 50, 0, .3, 1),
                InterferenceRequest(1, 500, 25, None, 0, 0, 0),
                PolarizationRequest(3, 550, 1, False, None, (0, 45, 90)),
                PolarizationRequest(3, 550, 1, True, 0, (89, 178, 87)),
                PolarizationRequest(1, 550, 0, False, None, (0,))]
    for request in requests:
        use_case = container.interference_use_case if isinstance(request, InterferenceRequest) else container.polarization_use_case
        response = use_case.execute(request)
        card = container.interference_page.formula_card
        card.set_response(response)
        text = card._text_label.toPlainText()
        assert all(section in text for section in ("Teoria", "Parâmetros", "Resolução"))
        image = card._text_label.document().resource(QTextDocument.ResourceType.ImageResource, QUrl("math:equation-0"))
        assert not image.isNull()
        assert card._text_label.height() >= card._text_label.document().size().height()
        assert card._text_label.accessibleDescription() == response.formula_text
        if response.initial_intensity == 0:
            assert "indefinido" in text
    image = equation_image(r"\frac{I}{I_0}", "#EDF4FC")
    assert image.pixelColor(0, 0).alpha() == 0
    assert math_number(1e-100) == r"1{,}0000\times 10^{-100}"
