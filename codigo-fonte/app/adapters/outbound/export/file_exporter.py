

import csv
from datetime import datetime, timezone
from app.version import VERSION
from .atomic_file import atomic_output_path
from pathlib import Path
from app.core.application.dto.responses import (
    InterferenceResponse,
    PolarizationResponse,
)
from app.core.application.ports.outbound import ResultExporterPort


class FileResultExporter(ResultExporterPort):
    

    def export_csv_interference(
        self,
        response: InterferenceResponse,
        destination_path: Path,
    ) -> None:
        
        exported_at = datetime.now(timezone.utc).isoformat()
        with atomic_output_path(destination_path) as temporary, open(temporary, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "angulo_graus",
                "intensidade_normalizada",
                "intensidade_relativa_escalada",
                "comprimento_onda_nm",
                "fendas",
                "largura_fenda_um", "separacao_centros_um", "incidencia_graus",
                "intensidade_inicial_relativa", "angulo_selecionado_graus",
                "versao_lumenlab", "exportado_em_utc",
            ])
            for angle, norm_i, abs_i in zip(
                response.angles_deg,
                response.normalized_intensity,
                response.scaled_relative_intensity,
            ):
                writer.writerow([
                    angle,
                    norm_i,
                    abs_i,
                    f"{response.wavelength_nm:.1f}",
                    response.slit_count,
                    response.slit_width_um, response.slit_separation_um,
                    response.incidence_angle_deg, response.initial_intensity,
                    response.selected_angle_deg, VERSION, exported_at,
                ])

    def export_csv_polarization(
        self,
        response: PolarizationResponse,
        destination_path: Path,
    ) -> None:
        
        exported_at = datetime.now(timezone.utc).isoformat()
        with atomic_output_path(destination_path) as temporary, open(temporary, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
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
            ])
            for stage in response.stages:
                field_dir_str = (
                    f"{stage.field_direction_deg:.2f}"
                    if stage.field_direction_deg is not None
                    else "N/A (E=0)"
                )
                writer.writerow([
                    f"P{stage.index}",
                    f"{stage.axis_angle_deg:.2f}",
                    stage.input_intensity,
                    stage.output_intensity,
                    stage.stage_transmission_pct,
                    stage.cumulative_transmission_pct,
                    stage.relative_field_amplitude,
                    field_dir_str,
                    response.wavelength_nm, response.initial_intensity,
                    response.initially_polarized, response.initial_angle_deg,
                    len(response.stages), VERSION, exported_at,
                ])
