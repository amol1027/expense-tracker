# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['expense_tracker.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['tkcalendar', 'tkcalendar.dateentry', 'tkcalendar.calendar', 'babel', 'babel.numbers', 'babel.dates'],
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
    a.datas,
    [],
    name='ExpenseTrackerApp',
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
    # version='version_info_simple.txt',
    # icon='assets/icons/icon.ico',
)
