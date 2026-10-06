

import math
from app.core.domain.models.polarization import (
    PolarizationParameters,
    PolarizationResult,
    PolarizerStage,
)
from app.core.domain.validation.validators import validate_polarization_parameters


def normalize_angle_rad(angle_rad: float) -> float:
    
    mod = angle_rad % math.pi
    if mod < 0:
        mod += math.pi
    return mod


def malus_transmission(delta_angle_rad: float) -> float:
    
    cosine = math.cos(delta_angle_rad)
    return 0.0 if abs(cosine) < 1e-15 else cosine * cosine


def compute_polarization(params: PolarizationParameters) -> PolarizationResult:
    


















    validate_polarization_parameters(params)

    stages: list[PolarizerStage] = []
    current_intensity = params.initial_intensity
    previous_axis: float | None = (
        params.initial_angle_rad if params.initially_polarized else None
    )

    for index in range(1, params.polarizer_count + 1):
        axis_angle = params.polarizer_angles_rad[index - 1]
        input_intensity = current_intensity

        if index == 1:
            if not params.initially_polarized:
                output_intensity = input_intensity * 0.5
                stage_transmission = 0.5 if input_intensity > 0 else 0.0
            else:
                assert previous_axis is not None
                delta_angle = axis_angle - previous_axis
                cos_sq = malus_transmission(delta_angle)
                output_intensity = input_intensity * cos_sq
                stage_transmission = cos_sq if input_intensity > 0 else 0.0
        else:
            assert previous_axis is not None
            delta_angle = axis_angle - previous_axis
            cos_sq = malus_transmission(delta_angle)
            output_intensity = input_intensity * cos_sq
            stage_transmission = cos_sq if input_intensity > 0 else 0.0

        output_intensity = max(0.0, output_intensity)
        cumulative_transmission = (
            output_intensity / params.initial_intensity
            if params.initial_intensity > 0
            else 0.0
        )
        cumulative_transmission = max(0.0, min(1.0, cumulative_transmission))
        relative_field_amplitude = math.sqrt(cumulative_transmission)
        
        field_direction: float | None = (
            axis_angle if output_intensity > 0 else None
        )

        stages.append(
            PolarizerStage(
                index=index,
                axis_angle_rad=axis_angle,
                input_intensity=input_intensity,
                output_intensity=output_intensity,
                stage_transmission=stage_transmission,
                cumulative_transmission=cumulative_transmission,
                relative_field_amplitude=relative_field_amplitude,
                field_direction_rad=field_direction,
            )
        )

        current_intensity = output_intensity
        previous_axis = axis_angle

    final_stage = stages[-1]

    return PolarizationResult(
        initial_intensity=params.initial_intensity,
        initially_polarized=params.initially_polarized,
        initial_angle_rad=params.initial_angle_rad,
        stages=tuple(stages),
        final_intensity=final_stage.output_intensity,
        final_transmission=final_stage.cumulative_transmission,
        final_field_amplitude=final_stage.relative_field_amplitude,
        final_field_direction_rad=final_stage.field_direction_rad,
    )
