import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
from dataclasses import asdict
from models import ProfileData
from core.config import PROFILE_FILE as USER_PROFILE_FILE

class UserProfile:

    PROFILE_FILE = USER_PROFILE_FILE

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
        self.PROFILE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(self.PROFILE_FILE, "w", encoding="utf-8") as f:
            json.dump(asdict(profile), f, indent=2, ensure_ascii=False)