# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path
import sys

block_cipher = None

repo_root = Path(SPECPATH).resolve().parent if "SPECPATH" in globals() else Path.cwd()

datas = [
    (str(repo_root / "assets" / "icons"), "assets/icons"),
    (str(repo_root / "app" / "adapters" / "inbound" / "qt" / "styles" / "theme.qss"), "app/adapters/inbound/qt/styles"),
]

a = Analysis(
    [str(repo_root / "main.py")],
    pathex=[str(repo_root)],
    binaries=[],
    datas=datas,
    hiddenimports=[
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
        "PySide6.QtSvg",
        "matplotlib.backends.backend_qtagg",
        "numpy",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="LumenLab",
    icon=str(repo_root / "assets" / "icons" / "lumenlab.ico"),
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
