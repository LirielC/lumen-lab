

import csv
import tempfile
from pathlib import Path
import pytest
from app.adapters.outbound.export.file_exporter import FileResultExporter
from app.core.application.dto.requests import InterferenceRequest, PolarizationRequest
from app.core.application.use_cases.simulate_interference import SimulateInterferenceUseCase
from app.core.application.use_cases.simulate_polarization import SimulatePolarizationUseCase


def test_export_csv_interference_complete(tmp_path: Path) -> None:
    
    use_case = SimulateInterferenceUseCase()
    exporter = FileResultExporter()

    req = InterferenceRequest(
        slit_count=2,
        wavelength_nm=652.0,
        slit_width_um=32.1,
        slit_separation_um=152.0,
        incidence_angle_deg=12.4,
        observation_angle_deg=27.3,
        initial_intensity=5.3,
    )
    resp = use_case.execute(req)

    out_file = tmp_path / "interference_audit.csv"
    exporter.export_csv_interference(resp, out_file)

    assert out_file.exists()
    assert out_file.stat().st_size > 0

    
    with open(out_file, mode="r", encoding="utf-8") as f:
        reader = list(csv.reader(f))

    headers = reader[0]
    expected_headers = [
        "angulo_graus",
        "intensidade_normalizada",
        "intensidade_relativa_escalada",
        "comprimento_onda_nm",
        "fendas",
        "largura_fenda_um", "separacao_centros_um", "incidencia_graus",
        "intensidade_inicial_relativa", "angulo_selecionado_graus",
        "versao_lumenlab", "exportado_em_utc",
    ]
    assert headers == expected_headers

    
    data_rows = reader[1:]
    assert len(data_rows) == len(resp.angles_deg)

    
    first_angle = float(data_rows[0][0])
    assert first_angle == pytest.approx(resp.angles_deg[0], abs=1e-3)
    assert int(data_rows[0][4]) == 2


def test_export_csv_polarization_with_zero_field_handling(tmp_path: Path) -> None:
    



    use_case = SimulatePolarizationUseCase()
    exporter = FileResultExporter()

    
    req = PolarizationRequest(
        polarizer_count=2,
        wavelength_nm=550.0,
        initial_intensity=1.0,
        initially_polarized=False,
        initial_angle_deg=None,
        polarizer_angles_deg=(0.0, 90.0),
    )
    resp = use_case.execute(req)

    out_file = tmp_path / "polarization_crossed_audit.csv"
    exporter.export_csv_polarization(resp, out_file)

    assert out_file.exists()
    with open(out_file, mode="r", encoding="utf-8") as f:
        reader = list(csv.reader(f))

    headers = reader[0]
    expected_headers = [
        "etapa",
        "eixo_graus",
        "intensidade_entrada",
        "intensidade_saida",
        "transmissao_etapa_pct",
        "transmissao_acumulada_pct",
        "amplitude_campo_relativa",
        "direcao_campo_graus",
        "comprimento_onda_nm", "intensidade_inicial_relativa",
        "inicialmente_polarizada", "angulo_inicial_graus", "polarizadores",
        "versao_lumenlab", "exportado_em_utc",
    ]
    assert headers == expected_headers

    stages = reader[1:]
    assert len(stages) == 2

    
    assert stages[0][0] == "P1"
    assert stages[0][7] == "0.00"

    
    assert stages[1][0] == "P2"
    assert stages[1][1] == "90.00"  
    assert float(stages[1][3]) == 0.0  
    assert float(stages[1][6]) == 0.0  
    assert stages[1][7] == "N/A (E=0)"  


def test_export_file_overwrite_safely(tmp_path: Path) -> None:
    
    use_case = SimulatePolarizationUseCase()
    exporter = FileResultExporter()

    req = PolarizationRequest(
        polarizer_count=1,
        wavelength_nm=550.0,
        initial_intensity=1.0,
        initially_polarized=False,
        initial_angle_deg=None,
        polarizer_angles_deg=(0.0,),
    )
    resp = use_case.execute(req)

    out_file = tmp_path / "overwrite_test.csv"
    
    exporter.export_csv_polarization(resp, out_file)
    size1 = out_file.stat().st_size

    
    exporter.export_csv_polarization(resp, out_file)
    size2 = out_file.stat().st_size
    assert size1 == size2
