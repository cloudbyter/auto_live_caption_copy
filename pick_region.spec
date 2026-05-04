# PyInstaller spec for region picker (used by main app when frozen).
# Run: pyinstaller pick_region.spec
# Output: dist/pick_region/pick_region.exe — copy into dist/LiveCaptionCopy/ after main build.

# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['pick_region.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['config'],
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
    a.datas,
    [],
    name='pick_region',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
