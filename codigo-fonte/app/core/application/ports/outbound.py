

from pathlib import Path
from typing import Protocol
from app.core.application.dto.responses import (
    InterferenceResponse,
    PolarizationResponse,
)


class ResultExporterPort(Protocol):
    

    def export_csv_interference(
        self,
        response: InterferenceResponse,
        destination_path: Path,
    ) -> None:
        
        ...

    def export_csv_polarization(
        self,
        response: PolarizationResponse,
        destination_path: Path,
    ) -> None:
        
        ...
