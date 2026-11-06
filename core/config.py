# core/config.py
"""
Chargement centralisé de la configuration.

En développement : cherche .env à la racine du workspace.
En mode exe      : cherche .env à côté de l'exécutable.

Ce module est importé en premier par projet.py tous les autres
modules (weather_service, ai_service, etc.) importent leurs variables
depuis os.getenv() normalement, sans appeler load_dotenv() eux-mêmes.

Gère aussi les problèmes d'encodage courants du .env :
- UTF-16 (créé via PowerShell Out-File/Set-Content ou Notepad classique)
- UTF-8 avec BOM (créé via Notepad "Enregistrer en UTF-8" sur Windows)
Ces encodages font planter python-dotenv qui attend de l'UTF-8 sans BOM.
Le fichier est automatiquement réécrit en UTF-8 propre si nécessaire.
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


def _find_user_data_dir() -> Path:
    """Return a persistent directory for user data."""
    if not getattr(sys, "frozen", False):
        return _find_data_dir()

    if sys.platform == "win32":
        app_data = os.environ.get("APPDATA")
        if not app_data:
            raise RuntimeError("APPDATA is not set; cannot locate user data directory")
        return Path(app_data) / "WeatherProgramm"

    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "WeatherProgramm"

    data_home = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return data_home / "WeatherProgramm"


def _load_env_safe(env_path: Path) -> None:
    """
    Charge le .env en gérant les problèmes d'encodage courants.

    Tente plusieurs encodages dans l'ordre : UTF-8, UTF-8 avec BOM,
    UTF-16 (LE puis BE). Si un encodage autre que UTF-8 fonctionne,
    le fichier est réécrit en UTF-8 sans BOM pour les lectures futures.

    Parameters
    ----------
    env_path : Path
        Chemin vers le fichier .env.
    """
    if not env_path.exists():
        return
    encodings_to_try = ["utf-8", "utf-8-sig", "utf-16", "utf-16-le", "utf-16-be"]

    for i, encoding in enumerate(encodings_to_try):
        try:

            with open(env_path, "r", encoding=encoding) as f:
                content = f.read()

            if i > 0:
                # Encodage non-standard détecté réécrit en UTF-8 propre
                with open(env_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f".env converti de {encoding} vers UTF-8")

            load_dotenv(env_path)
            return
        except UnicodeDecodeError:
            continue

    print(f"Impossible de lire {env_path} : encodage non reconnu")


# Chemins accessibles depuis tous les modules
ENV_PATH  = _find_env_path()
DATA_DIR  = _find_data_dir()
USER_DATA_DIR = _find_user_data_dir()
PROFILE_FILE = USER_DATA_DIR / "profile.json"


def get_user_data_path(filename: str) -> Path:
    """Return the writable path for a user-owned data file."""
    return USER_DATA_DIR / filename


def get_data_path(filename: str) -> Path:
    """Prefer a user-customized data file, falling back to bundled defaults."""
    user_path = get_user_data_path(filename)
    if user_path.exists():
        return user_path
    return DATA_DIR / filename


# Charge le .env une seule fois au démarrage
_load_env_safe(ENV_PATH)