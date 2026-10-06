


class OptiLabDomainError(Exception):
    

    def __init__(self, message: str, parameter_name: str | None = None) -> None:
        super().__init__(message)
        self.parameter_name = parameter_name
        self.message = message


class InvalidPhysicalParameterError(OptiLabDomainError):
    """"""


class SlitSeparationGeometryError(InvalidPhysicalParameterError):
    """"""


class PolarizerCountError(InvalidPhysicalParameterError):
    """"""


class InvalidPolarizationStateError(InvalidPhysicalParameterError):
    """"""
