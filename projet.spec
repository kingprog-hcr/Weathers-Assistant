# projet.spec
"""
Configuration PyInstaller pour WeatherProgramm.

Ce fichier décrit comment assembler l'application en un seul exécutable.
Il inclut :
    - Tous les fichiers Python du projet
    - Le dossier data/ avec les JSON
    - Les assets de customtkinter (thèmes, polices, icônes)
    - Les assets de tkintermapview
"""

import sys
from pathlib import Path
import customtkinter
import tkintermapview

block_cipher = None

# Racine du projet
ROOT = Path(spec_dir if 'spec_dir' in dir() else '.')

# Chemin vers les assets de customtkinter
CTK_PATH = Path(customtkinter.__file__).parent

# Chemin vers les assets de tkintermapview
MAP_PATH = Path(tkintermapview.__file__).parent

a = Analysis(
    # Point d'entrée
    ['projet.py'],

    pathex=[str(ROOT)],

    binaries=[],

    # Fichiers de données à inclure dans l'exécutable
    datas=[
        # Dossier data/ — JSON de l'app
        (str(ROOT / 'data'), 'data'),

        # Assets customtkinter — thèmes, polices, icônes
        (str(CTK_PATH / 'assets'), 'customtkinter/assets'),

        # Assets tkintermapview — tuiles offline si présentes
        (str(MAP_PATH), 'tkintermapview'),
    ],

    # Imports cachés que PyInstaller ne détecte pas automatiquement
    hiddenimports=[
        'PIL._tkinter_finder',
        'customtkinter',
        'CTkColorPicker',
        'tkintermapview',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'requests',
        'groq',
        'dotenv',
        'urllib.request',
        'io',
        'json',
        'dataclasses',
        'pathlib',
        'datetime',
        'itertools',
        'random',
        'tkinter',
        'tkinter.ttk',
        'tkinter.font',
    ],

    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclut les modules inutiles pour réduire la taille
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'notebook',
        'IPython',
        'pytest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='WeatherProgramm',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,         # compresse l'exécutable (plus petit)
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,    # pas de terminal — app graphique
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Icône selon le système
    icon=None,        # on ajoutera une icône plus tard
)