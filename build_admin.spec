# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# inclusions
a = Analysis(
    ['desktop_admin/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('desktop_admin/theme', 'desktop_admin/theme'),
        ('desktop_admin/windows', 'desktop_admin/windows'),
        ('AGENTS.md', '.'),
    ],
    hiddenimports=[
        'customtkinter',
        'darkdetect',
        'matplotlib',
        'PIL',
        'PIL._tkinter_finder',
        'matplotlib.backends.backend_tkagg',
        'numpy',
        'scipy',
        'pandas',
        'reportlab',
        'fpdf',
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
    name='MobiTranzAdmin',
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
    icon='desktop_admin/assets/icon.ico' if __import__('os').path.exists('desktop_admin/assets/icon.ico') else None,
    version='version.txt' if __import__('os').path.exists('version.txt') else None,
)