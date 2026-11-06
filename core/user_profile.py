import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
from dataclasses import asdict
from models import ProfileData
from core.config import PROFILE_FILE as USER_PROFILE_FILE

class UserProfile:

    PROFILE_FILE = USER_PROFILE_FILE

    @staticmethod
    def _decode_profile(raw: bytes) -> tuple[str, bool]:
        text = raw.decode("utf-8", errors="surrogateescape")
        if not any(0xDC80 <= ord(character) <= 0xDCFF for character in text):
            return text, False

        decoded = []
        for character in text:
            codepoint = ord(character)
            if 0xDC80 <= codepoint <= 0xDCFF:
                decoded.append(bytes([codepoint - 0xDC00]).decode("cp1252"))
            else:
                decoded.append(character)
        return "".join(decoded), True

    def load(self) -> ProfileData:
        """Charge le profil. Crée un profil par défaut si absent."""
        try:
            raw = self.PROFILE_FILE.read_bytes()
        except FileNotFoundError:
            return ProfileData() # on retourne un profile par defaut

        text, migrated = self._decode_profile(raw)
        profile = ProfileData(**json.loads(text))
        if migrated:
            self.save(profile)
            print("Ancien encodage du profil détecté et converti en UTF-8.")
        return profile

    def save(self, profile: ProfileData) -> None:
        """Sauvegarde le profil."""
        self.PROFILE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(self.PROFILE_FILE, "w", encoding="utf-8") as f:
            json.dump(asdict(profile), f, indent=2, ensure_ascii=False)