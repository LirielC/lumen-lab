

import json
import math
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.core.application.dto.requests import InterferenceRequest, PolarizationRequest
from app.core.application.use_cases.simulate_interference import SimulateInterferenceUseCase
from app.core.application.use_cases.simulate_polarization import SimulatePolarizationUseCase
from app.core.domain.models.interference import InterferenceParameters
from app.core.domain.errors import InvalidPhysicalParameterError
from app.core.domain.physics.interference import compute_slit_interference, generate_angular_grid


def main() -> None:
    rng = np.random.default_rng(20260911)
    slits = SimulateInterferenceUseCase()
    polarizers = SimulatePolarizationUseCase()
    errors = {"slit_scalar_absolute": 0.0, "slit_array_normalized": 0.0,
              "aperture_quadrature": 0.0, "polarization_coherency": 0.0}
    nodes, weights = np.polynomial.legendre.leggauss(128)
    for index in range(1000):
        count = 1 + index % 2
        wavelength = float(rng.uniform(400, 700))
        width = float(rng.uniform(1, 100))
        separation = float(rng.uniform(max(2, width + .1), 300)) if count == 2 else None
        alpha = float(rng.uniform(-30, 30))
        theta = float(rng.uniform(-90, 90))
        intensity = float(rng.uniform(.1, 10))
        response = slits.execute(InterferenceRequest(count, wavelength, width, separation, alpha, theta, intensity))

        def reference(angle: float) -> float:
            q = math.sin(math.radians(angle)) - math.sin(math.radians(alpha))
            beta = math.pi * width * 1000 / wavelength * q
            envelope = (math.sin(beta) / beta) ** 2 if beta else 1.0
            return envelope * (math.cos(math.pi * separation * 1000 / wavelength * q) ** 2 if separation else 1)

        errors["slit_scalar_absolute"] = max(errors["slit_scalar_absolute"], abs(response.selected_intensity - intensity * reference(theta)))
        indices = np.linspace(0, len(response.angles_deg) - 1, 41, dtype=int)
        for i in indices:
            errors["slit_array_normalized"] = max(errors["slit_array_normalized"], abs(response.normalized_intensity[i] - reference(float(response.angles_deg[i]))))
        assert np.all(np.isfinite(response.normalized_intensity))
        assert np.all(np.diff(response.angles_deg) > 0)
        assert np.all((response.normalized_intensity >= 0) & (response.normalized_intensity <= 1))

        
        q = float(rng.uniform(-.9, .9)) * wavelength / (1000 * width)
        sine = math.sin(math.radians(alpha)) + q
        if abs(sine) <= 1:
            near_theta = math.degrees(math.asin(sine))
            centers = (0,) if count == 1 else (-separation / 2, separation / 2)
            field = sum(np.dot(weights, np.exp(2j * math.pi * (center + nodes * width / 2) * 1000 * q / wavelength)) / 2 for center in centers) / count
            errors["aperture_quadrature"] = max(errors["aperture_quadrature"], abs(abs(field) ** 2 - reference(near_theta)))

        
        number = 1 + index % 3
        polarized = bool(index % 2)
        angle0 = float(rng.uniform(0, 180))
        angles = tuple(float(v) for v in rng.uniform(0, 180, number))
        response = polarizers.execute(PolarizationRequest(number, wavelength, intensity, polarized, angle0 if polarized else None, angles))
        direction = np.array([math.cos(math.radians(angle0)), math.sin(math.radians(angle0))])
        coherency = intensity * (np.outer(direction, direction) if polarized else np.eye(2) / 2)
        for angle, stage in zip(angles, response.stages):
            axis = np.array([math.cos(math.radians(angle)), math.sin(math.radians(angle))])
            projection = np.outer(axis, axis)
            coherency = projection @ coherency @ projection
            expected = float(np.trace(coherency))
            errors["polarization_coherency"] = max(errors["polarization_coherency"], abs(expected - stage.output_intensity))
            assert math.isclose(stage.relative_field_amplitude ** 2, stage.output_intensity / intensity, abs_tol=1e-14)
        other_color = polarizers.execute(PolarizationRequest(number, 400, intensity, polarized, angle0 if polarized else None, angles))
        assert other_color.final_intensity == response.final_intensity

    assert max(errors.values()) < 1e-10, errors
    params = InterferenceParameters(2, 400e-9, 100e-6, 300e-6, 0, 1)
    observations = {}
    for name, calculate in (
        ("custom_nan_grid_rejected", lambda: compute_slit_interference(params, observation_angles=np.array([0., np.nan]))),
        ("equal_grid_bounds_rejected", lambda: generate_angular_grid(params, 0, 0)),
    ):
        try:
            calculate()
        except InvalidPhysicalParameterError:
            observations[name] = True
        else:
            raise AssertionError(f"Invalid angular grid accepted: {name}")
    result = {"seed": 20260911, "slit_configurations": 1000, "polarization_configurations": 1000,
              "maximum_absolute_errors": errors, "observations": observations}
    destination = ROOT / "build" / "physics-audit-20260911"
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "results.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
