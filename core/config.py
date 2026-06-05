# core/config.py
"""
Chargement centralisé de la configuration.

En développement : cherche .env à la racine du workspace.
En mode exe      : cherche .env à côté de l'exécutable.

Ce module est importé en premier par projet.py tous les autres
modules (weather_service, ai_service, etc.) importent leurs variables
depuis os.getenv() normalement, sans appeler load_dotenv() eux-mêmes.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv


def _find_env_path() -> Path:
    """
    Détermine où chercher le fichier .env selon le mode d'exécution.

    En mode exécutable PyInstaller (frozen=True) :
        L'exe est dans un dossier quelconque sur le PC de l'utilisateur.
        Le .env doit être dans CE même dossier, à côté de l'exe.
        sys.executable = chemin complet vers l'exe
        Path(sys.executable).parent = dossier qui contient l'exe

    En mode développement (frozen=False) :
        On cherche .env à la racine du projet (comportement normal).
    """
    if getattr(sys, 'frozen', False):
        # Mode exe  cherche .env à côté de l'exécutable
        return Path(sys.executable).parent / ".env"
    else:
        # Mode développement cherche .env à la racine du workspace
        return Path(__file__).parent.parent / ".env"


def _find_data_dir() -> Path:
    """
    Détermine où se trouve le dossier data/ selon le mode d'exécution.

    En mode exe : data/ est extrait dans sys._MEIPASS (dossier temporaire).
    En développement : data/ est à la racine du workspace.
    """
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS) / "data"
    else:
        return Path(__file__).parent.parent / "data"


# Chemins accessibles depuis tous les modules
ENV_PATH  = _find_env_path()
DATA_DIR  = _find_data_dir()

# Charge le .env une seule fois au démarrage
load_dotenv(ENV_PATH)