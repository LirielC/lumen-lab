# LumenLab

### A computational laboratory for physical optics

LumenLab is an educational desktop application that helps students explore wave-optics phenomena through interactive simulations. Users can adjust physical parameters, observe the resulting visual patterns, review the underlying equations, and export experiment data for further analysis.

The project was developed collaboratively by [Liriel C.](https://github.com/LirielC) and [Melyssa Souza](https://github.com/Melyssa-Souza) for the **Physics III** course at the [State University of Rio de Janeiro (UERJ)](https://www.uerj.br/).

## Overview

LumenLab brings two core optics experiments into one focused interface:

- **Interference and diffraction:** explore Fraunhofer diffraction through a single slit and the interference pattern produced by a double slit.
- **Polarization:** investigate the transmission of light through up to three ideal polarizers using Malus's law.

The application combines visual intuition with quantitative results, making it possible to connect parameter changes to the equations and physical behavior behind each experiment.

## Experiments

### Interference and diffraction

The experiment models the angular intensity distribution of light after one or two slits. It supports:

- Single-slit Fraunhofer diffraction.
- Double-slit interference with a diffraction envelope.
- Wavelength selection from 400 to 700 nm, with an approximate color representation.
- Adjustable slit width, slit separation, incidence angle, and reference intensity.
- Interactive observation-angle selection.
- Incident-beam geometry with vectors, normal reference, and incidence-angle visualization.
- Overview and pattern-zoom views.
- Adaptive sampling for narrow fringes and supersampled screen rendering.
- CSV data export and high-resolution PNG export.

For a single slit, the normalized intensity is modeled as:

$$
\frac{I(\theta)}{I_0} = \mathrm{sinc}^2\left(\frac{a q}{\lambda}\right),
\qquad q = \sin\theta - \sin\alpha
$$

For two slits, the diffraction envelope is combined with the interference term:

$$
\frac{I(\theta)}{I_0} =
\mathrm{sinc}^2\left(\frac{a q}{\lambda}\right)
\cos^2\left(\frac{\pi d q}{\lambda}\right)
$$

### Polarization

The polarization experiment simulates the transmission of polarized and unpolarized light through a cascade of ideal polarizers. It supports:

- One, two, or three polarizers.
- Independent transmission-axis angles from 0° to 180°.
- Polarized or unpolarized incident light.
- An initial polarization angle for polarized light.
- Visual representations of the beam, polarization axes, electric-field vector, and brightness reduction.
- Per-stage and cumulative transmission results.
- CSV export of the experiment data.

The simulation applies Malus's law at each stage:

$$
I_k = I_{k-1}\cos^2(\phi_k - \phi_{k-1})
$$

For unpolarized light, the first ideal polarizer transmits half of the incident intensity:

$$
I_1 = \frac{I_0}{2}
$$

## Technical design

The source code follows a **hexagonal architecture**, also known as Ports and Adapters. The physics domain and application use cases remain independent from the graphical interface and file-export mechanisms. This separation keeps the scientific logic testable and makes the UI easier to evolve.

```text
codigo-fonte/
├── app/
│   ├── core/
│   │   ├── domain/         # Models, validation, and pure physics calculations
│   │   └── application/    # DTOs, ports, and experiment use cases
│   ├── adapters/
│   │   ├── inbound/qt/     # PySide6 views, controllers, widgets, and plots
│   │   └── outbound/       # Resource resolution and CSV export
│   └── bootstrap/          # Application startup and dependency wiring
├── tests/                  # Domain, application, adapter, and UI tests
├── assets/                 # Icons and bundled visual resources
└── main.py                 # Application entry point
```

## Technology stack

- Python 3.11+
- PySide6 for the desktop interface
- NumPy for numerical calculations
- Matplotlib for intensity plots
- Pytest and Coverage for automated verification
- PyInstaller for Windows packaging
- Tabler Icons for locally bundled interface icons

## Running from source

From the `codigo-fonte` directory:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

## Testing

Run the full test suite with:

```powershell
python -m pytest -v tests/
```

To generate a coverage report:

```powershell
python -m coverage run -m pytest -q
python -m coverage report
python -m coverage html
```

## Windows distribution

The repository includes a packaged Windows release. Users can launch `LumenLab.exe` without installing Python or the project dependencies. Before running it, extract the complete distribution package to a local folder.

- [Windows user manual](documentacao/Manual_do_Usuario_LumenLab.pdf)
- [Source code and development files](codigo-fonte/)
- [Verification evidence](evidencias/)
- [SHA-256 checksums](SHA256SUMS.txt)

## References

- [OpenStax University Physics, Volume 3](https://openstax.org/details/books/university-physics-volume-3), used as the theoretical foundation for diffraction, interference, and polarization.
- [Qt for Python documentation](https://doc.qt.io/qtforpython-6/)
- [NumPy documentation](https://numpy.org/doc/)
- [Matplotlib documentation](https://matplotlib.org/stable/)
- [PyInstaller documentation](https://pyinstaller.org/en/stable/)
- [Tabler Icons](https://tabler.io/icons), distributed with the project under the MIT License.

## Academic context

LumenLab was created as a group project for Physics III at UERJ. Its purpose is to support the study of physical optics by connecting theoretical models, numerical computation, and interactive visualization in a single educational tool.

## Authors

- [Liriel C.](https://github.com/LirielC)
- [Melyssa Souza](https://github.com/Melyssa-Souza)

