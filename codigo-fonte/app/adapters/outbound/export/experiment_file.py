

from dataclasses import fields
from datetime import datetime, timezone
import json
import math
from pathlib import Path

from app.core.application.dto.requests import InterferenceRequest, PolarizationRequest
from app.core.application.dto.responses import InterferenceResponse, PolarizationResponse
from app.version import VERSION
from .atomic_file import atomic_output_path


def experiment_data(response: InterferenceResponse | PolarizationResponse) -> dict:
    
    if isinstance(response, InterferenceResponse):
        parameters = {field.name: getattr(response, field.name)
                      for field in fields(InterferenceRequest)
                      if field.name != "observation_angle_deg"}
        parameters["observation_angle_deg"] = response.selected_angle_deg
        module = "interference"
    else:
        parameters = {
            "polarizer_count": len(response.stages),
            "wavelength_nm": response.wavelength_nm,
            "initial_intensity": response.initial_intensity,
            "initially_polarized": response.initially_polarized,
            "initial_angle_deg": response.initial_angle_deg,
            "polarizer_angles_deg": [stage.axis_angle_deg for stage in response.stages],
        }
        module = "polarization"
    return {"format": "lumenlab.experiment", "schema_version": 1,
            "app_version": VERSION, "saved_at_utc": datetime.now(timezone.utc).isoformat(),
            "module": module, "parameters": parameters}


def save_experiment(response: InterferenceResponse | PolarizationResponse, destination: Path) -> None:
    with atomic_output_path(destination) as temporary:
        temporary.write_text(json.dumps(experiment_data(response), ensure_ascii=False,
                                        indent=2, allow_nan=False) + "\n", encoding="utf-8")


def load_experiment(source: Path) -> InterferenceRequest | PolarizationRequest:
    
    data = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("format") != "lumenlab.experiment" or type(data.get("schema_version")) is not int or data["schema_version"] != 1:
        raise ValueError("Formato ou versão de experimento não suportado.")
    module = data.get("module")
    if not isinstance(module, str):
        raise ValueError("Módulo inválido.")
    request_type = {"interference": InterferenceRequest, "polarization": PolarizationRequest}.get(module)
    parameters = data.get("parameters")
    if request_type is None or not isinstance(parameters, dict) or set(parameters) != {field.name for field in fields(request_type)}:
        raise ValueError("Módulo ou parâmetros do experimento inválidos.")
    for name, value in parameters.items():
        if name == "initially_polarized":
            valid = type(value) is bool
        elif name in ("slit_count", "polarizer_count"):
            valid = type(value) is int
        elif name == "polarizer_angles_deg":
            valid = isinstance(value, list) and all(type(v) in (int, float) and math.isfinite(v) for v in value)
        else:
            valid = (value is None and name in ("initial_angle_deg", "slit_separation_um")) or (type(value) in (int, float) and math.isfinite(value))
        if not valid:
            raise ValueError(f"Valor inválido: {name}.")
    if "polarizer_angles_deg" in parameters:
        parameters["polarizer_angles_deg"] = tuple(parameters["polarizer_angles_deg"])
    return request_type(**parameters)
