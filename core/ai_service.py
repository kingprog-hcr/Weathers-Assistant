# core/ai_service.py
"""
Service d'intelligence artificielle via Groq API.

Enrichit les suggestions locales avec de vraies données :
vrais lieux et adresses pour les activités déjà générées localement.
Utilise llama-3.3-70b-versatile comme modèle principal.
Fallback silencieux si Groq est indisponible , l'app fonctionne toujours.
"""

import sys
import os
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from groq import Groq
from models import WeatherData, ProfileData

load_dotenv()


class AIService:
    """
    Service IA basé sur Groq API (llama-3.3-70b-versatile).

    Rôle unique : enrichir les activités déjà générées localement avec de vrais lieux et adresses dans la ville de l'utilisateur.
    Ne génère rien de nouveau complète seulement ce qui existe.

    Attributes
    ----------
    client : Groq | None
        Client Groq initialisé, ou None si clé absente.
    MODEL : str
        Nom du modèle Groq utilisé.
    """

    MODEL = "llama-3.3-70b-versatile"

    def __init__(self):
        """
        Initialise le client Groq depuis la clé dans .env.
        Ne plante pas si la clé est absente, mode local uniquement.
        """
        load_dotenv()
        api_key = os.getenv("GROQ_API_KEY")

        if api_key:
            self.client = Groq(api_key=api_key)
        else:
            self.client = None
            print("GROQ_API_KEY absente : mode local uniquement")

    def is_available(self) -> bool:
        """
        Vérifie si le service IA est disponible.

        Returns
        -------
        bool
            True si le client Groq est initialisé avec une clé valide.
        """
        return self.client is not None

    def enrich_activities(
        self,
        activities: list[dict],
        city: str,
    ) -> list[dict] | None:
        """
        Enrichit une liste d'activités existantes avec de vrais lieux.

        Envoie à Groq la liste des activités déjà générées localement et lui demande uniquement d'ajouter un lieu réel et une adresse s'il en connaît un qui correspond. Ne crée aucune nouvelle activité.

        Parameters
        ----------
        activities : list[dict]
            Liste de dicts {"time": "10:00", "activity": "Visite d'un musée"}.
            Générés localement par DayPlanner._build_local().
        city : str
            Ville de l'utilisateur : Groq cherche des lieux dans cette ville.
        

        Returns
        -------
        list[dict] | None
            Liste enrichie avec "location", "address", "lat", "lon" ajoutés,
            ou None si Groq est indisponible ou retourne du JSON invalide.
        """
        if not self.is_available():
            return None

        # Formate les activités en texte lisible pour le prompt
        # On exclut les repas, pas besoin de localiser un petit-déjeuner
        activities_text = "\n".join([
            f"- {a['time']} : {a['activity']}"
            for a in activities
        ])

        # Prompt minimaliste
        prompt = f"""
Tu es un assistant de localisation urbaine.

Ville : {city}
Langue de réponse : Francais

Voici une liste d'activités générées pour un utilisateur à {city}.
Pour chaque activité, si tu connais avec certitude un vrai lieu existant
à {city} qui correspond naturellement à cette activité, indique-le.
Sinon, mets null, ne jamais inventer un lieu incertain.

Activités :
{activities_text}

Réponds UNIQUEMENT en JSON valide, sans markdown, sans texte avant ou après.
Format exact,  un objet par activité dans le même ordre :
[
  {{
    "time": "10:00",
    "location": "Nom exact du lieu ou null",
    "address": "Adresse approximative ou null",
    "lat": 0.0000,
    "lon": 0.0000
  }}
]
"""
        try:
            response = self.client.chat.completions.create(
                model=self.MODEL,
                messages=[{"role": "user", "content": prompt}],
                # temperature basse on veut des faits, pas de créativité
                temperature=0.2,
                max_tokens=1000,
            )

            content = response.choices[0].message.content.strip()

            # Nettoie les backticks markdown si Groq en ajoute malgré tout
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]

            return json.loads(content.strip())

        except json.JSONDecodeError:
            print("AIService: JSON invalide retourné par Groq")
            return None
        except Exception as e:
            print(f"AIService: erreur Groq :  {e}")
            return None


if __name__ == "__main__":
    # On enrichit une liste d'activités fictives pour une ville au choix
    service = AIService()

    test_activities = [
        {"time": "10:00", "activity": "Visite d'un musée"},
        {"time": "14:00", "activity": "Balade dans un parc"},
        {"time": "17:00", "activity": "Concert de jazz"},
        {"time": "21:00", "activity": "Jouer au foot"},
    ]
    ville = input("Entre une ville: ")
    result = service.enrich_activities(test_activities, city=ville)

    if result:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("Enrichissement indisponible, mode local uniquement")