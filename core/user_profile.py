import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
from dataclasses import asdict
from models import ProfileData
from core.config import DATA_DIR

class UserProfile:

    PROFILE_FILE = DATA_DIR / "profile.json"

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