# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[('assets/*.png', 'assets')],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=['cv2'],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz, a.scripts, [],
    exclude_binaries=True,
    name='Pomodoro Pet',
    debug=False,
    console=False,
)

coll = COLLECT(
    exe, a.binaries, a.datas,
    name='Pomodoro Pet',
)

app = BUNDLE(
    coll,
    name='Pomodoro Pet.app',
    bundle_identifier='com.pomodoro-pet.app',
    info_plist={
        'NSHighResolutionCapable': True,
        'LSUIElement': True,
        'CFBundleShortVersionString': '1.0.0',
    },
)
