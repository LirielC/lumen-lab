

from typing import Protocol
from app.core.application.dto.requests import (
    InterferenceRequest,
    PolarizationRequest,
)
from app.core.application.dto.responses import (
    InterferenceResponse,
    PolarizationResponse,
)


class SimulateInterferencePort(Protocol):
    

    def execute(self, request: InterferenceRequest) -> InterferenceResponse:
        
        ...


class SimulatePolarizationPort(Protocol):
    

    def execute(self, request: PolarizationRequest) -> PolarizationResponse:
        
        ...
