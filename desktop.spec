# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec: desktop app + Alembic + static assets."""

from pathlib import Path

from PyInstaller.building.api import EXE
from PyInstaller.building.api import PYZ
from PyInstaller.building.build_main import Analysis
from PyInstaller.utils.hooks import collect_submodules

SPECDIR = Path(SPECPATH)

datas = [
    (str(SPECDIR / 'alembic.ini'), '.'),
    (str(SPECDIR / 'alembic'), 'alembic'),
    (str(SPECDIR / 'static'), 'static'),
    (str(SPECDIR / 'templates'), 'templates'),
]

hiddenimports = (
    [
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'asyncpg',
        'greenlet',
    ]
    + collect_submodules('repository')
    + collect_submodules('handlers')
)

a = Analysis(
    [str(SPECDIR / 'src' / 'desktop.py')],
    pathex=[str(SPECDIR), str(SPECDIR / 'src')],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='obuv-demo-ex',
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(SPECDIR / 'static' / 'logo.ico'),
)
