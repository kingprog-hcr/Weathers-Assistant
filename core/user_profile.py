import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
from dataclasses import asdict
from models import ProfileData


class UserProfile:

    BASE_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    PROFILE_FILE = os.path.join(BASE_DIR, "data", "profile.json")

    def load(self) -> ProfileData:
        """Charge le profil. Crée un profil par défaut si absent."""
        try:
            with open(self.PROFILE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return ProfileData(**data)
        except FileNotFoundError:
            return ProfileData() # on retourne un profile par defaut

    def save(self, profile: ProfileData) -> None:
        """Sauvegarde le profil."""
        with open(self.PROFILE_FILE, "w", encoding="utf-8") as f:
            json.dump(asdict(profile), f, indent=2, ensure_ascii=False)