

import csv
from dataclasses import replace
import json
from pathlib import Path
from unittest.mock import patch
import numpy as np
import pytest
from PySide6.QtCore import QCoreApplication, QEvent
from PySide6.QtWidgets import QApplication
from PIL import Image

from app.bootstrap.application import create_app
from app.adapters.outbound.export.atomic_file import atomic_output_path
from app.adapters.outbound.export.experiment_file import load_experiment, save_experiment
from app.adapters.inbound.qt.plots.angular_view import pixel_mean_intensities
from app.core.application.dto.requests import InterferenceRequest, PolarizationRequest
from app.version import VERSION


@pytest.fixture
def lab():
    app, container = create_app()
    yield container
    for controller in (container.interference_controller, container.polarization_controller):
        controller._debounce_timer.stop()
    container.main_window.close()
    container.main_window.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)


def test_both_experiments_round_trip_and_recompute(lab, tmp_path):
    requests = [InterferenceRequest(2, 450, 12.3, 50, 5, 5.1, 2.5),
                PolarizationRequest(3, 650, 1.5, True, 30, (45, 90, 180))]
    for request, controller, page in zip(requests,
            (lab.interference_controller, lab.polarization_controller),
            (lab.interference_page, lab.polarization_page)):
        response = controller._use_case.execute(request)
        path = tmp_path / 'Experimento óptico com espaços.json'
        save_experiment(response, path)
        loaded = load_experiment(path)
        
        lab.experiment_controller.apply_request(loaded)
        assert page.slider_wavelength.value() == request.wavelength_nm
        assert page.slider_intensity.value() == request.initial_intensity
        expected = controller._use_case.execute(loaded)
        if isinstance(loaded, InterferenceRequest):
            np.testing.assert_allclose(page.last_response.scaled_relative_intensity, expected.scaled_relative_intensity)
        else:
            assert page.last_response.final_intensity == pytest.approx(expected.final_intensity)
        assert json.loads(path.read_text(encoding='utf-8'))['app_version'] == VERSION


def test_invalid_json_and_unrepresentable_values_do_not_change_controls(lab, tmp_path):
    path = tmp_path / 'invalid.json'
    save_experiment(lab.interference_page.last_response, path)
    original = json.loads(path.read_text(encoding='utf-8'))
    for bad in (True, float('nan'), '633', None):
        data = json.loads(json.dumps(original))
        data['parameters']['wavelength_nm'] = bad
        path.write_text(json.dumps(data), encoding='utf-8')
        with pytest.raises(ValueError):
            load_experiment(path)
    for wavelength in (399, 701, 550.5):
        with pytest.raises(Exception):
            lab.experiment_controller.apply_request(InterferenceRequest(1, wavelength, 25, None, 0, 0, 1))
        assert lab.interference_page.slider_wavelength.value() == 633
    with pytest.raises(Exception):
        lab.experiment_controller.apply_request(InterferenceRequest(2, 550, 50, 25, 0, 0, 1))
    assert lab.interference_page.slit_control.selected_index() == 0


def test_atomic_failure_preserves_existing_file_and_removes_temporary(tmp_path):
    path = tmp_path / 'resultado.csv'
    path.write_bytes(b'original')
    with pytest.raises(OSError):
        with atomic_output_path(path) as temporary:
            temporary.write_bytes(b'incomplete')
            raise OSError('simulated disk failure')
    assert path.read_bytes() == b'original'
    with patch('app.adapters.outbound.export.atomic_file.os.replace', side_effect=PermissionError('locked')):
        with pytest.raises(PermissionError):
            with atomic_output_path(path) as temporary:
                temporary.write_bytes(b'complete')
    assert path.read_bytes() == b'original'
    assert list(tmp_path.iterdir()) == [path]


def test_csv_contains_parameters_for_reproduction(lab, tmp_path):
    for response, export in ((lab.interference_page.last_response, lab.file_exporter.export_csv_interference),
                             (lab.polarization_page.last_response, lab.file_exporter.export_csv_polarization)):
        path = tmp_path / 'dados.csv'
        export(response, path)
        with path.open(encoding='utf-8') as stream:
            row = next(csv.DictReader(stream))
        assert row['versao_lumenlab'] == VERSION
        assert float(row['intensidade_inicial_relativa']) == response.initial_intensity
        assert float(row['comprimento_onda_nm']) == response.wavelength_nm
        assert row['exportado_em_utc'].endswith('+00:00')
        if 'fendas' in row:
            assert float(row['largura_fenda_um']) == response.slit_width_um
            assert float(row['incidencia_graus']) == response.incidence_angle_deg
        else:
            assert int(row['polarizadores']) == len(response.stages)
            assert row['inicialmente_polarizada'] == str(response.initially_polarized)


def test_comparison_is_frozen_and_png_contains_both_configurations(lab, tmp_path):
    controller, page = lab.interference_controller, lab.interference_page
    controller.freeze_reference()
    reference = page.plot_widget._reference_line.get_ydata().copy()
    page.slider_wavelength.set_value(450)
    controller._run_simulation()
    np.testing.assert_array_equal(page.plot_widget._reference_line.get_ydata(), reference)
    assert page.reference_response.wavelength_nm == 633
    assert page.last_response.wavelength_nm == 450
    for width in (350, 650):
        page.plot_widget.resize(width, 350)
        page.plot_widget.set_view_mode('detail')
        page.plot_widget.draw()
        np.testing.assert_array_equal(page.plot_widget._main_line.get_ydata(), page.last_response.normalized_intensity)
    path = tmp_path / 'comparação.png'
    page.plot_widget.export_image(path)
    with Image.open(path) as image:
        metadata = json.loads(image.info['Description'])
    assert metadata['reference']['parameters']['wavelength_nm'] == 633
    assert metadata['current']['parameters']['wavelength_nm'] == 450
    page.set_reference(None)
    assert not page.plot_widget._reference_line.get_visible()


def test_pixel_integration_preserves_narrow_fringe_energy_on_resize(lab):
    response = lab.interference_use_case.execute(InterferenceRequest(2, 400, 100, 300, 17.3, 17.3, 1))
    angles, intensities = response.angles_deg, response.normalized_intensity
    expected = np.trapezoid(intensities, angles)
    for columns in (200, 401, 800):
        pixels = pixel_mean_intensities(angles, intensities, (-90, 90), columns)
        assert pixels.sum() * 180 / columns == pytest.approx(expected, rel=1e-9)
        assert pixels.max() > 0
    
    x = np.array([-1., 0., 1.])
    np.testing.assert_allclose(pixel_mean_intensities(x, np.array([1., 0., 1.]), (-1, 1), 4), [.75, .25, .25, .75])
