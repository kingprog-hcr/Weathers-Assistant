# core/ai_service.py
"""
Service d'intelligence artificielle via Groq API.

Enrichit les suggestions locales avec de vraies données :
vrais lieux et adresses pour les activités déjà générées localement.
Utilise openai/gpt-oss-120b comme modèle principal.
Fallback silencieux si Groq est indisponible , l'app fonctionne toujours.
"""

import sys
import os
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from groq import Groq
import core.config 


class AIService:
    """
    Service IA basé sur Groq API (openai/gpt-oss-120b).

    Rôle unique : enrichir les activités déjà générées localement avec de vrais lieux et adresses dans la ville de l'utilisateur.
    Ne génère rien de nouveau complète seulement ce qui existe.

    Attributes
    ----------
    client : Groq | None
        Client Groq initialisé, ou None si clé absente.
    MODEL : str
        Nom du modèle Groq utilisé.
    """

    MODEL = "openai/gpt-oss-120b"

    def __init__(self):
        """
        Initialise le client Groq depuis la clé dans .env.
        Ne plante pas si la clé est absente, mode local uniquement.
        """
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

Pour chaque activité, conserve son heure et respecte l'ordre de la liste.
"""
        try:
            response = self.client.chat.completions.create(
                model=self.MODEL,
                messages=[{"role": "user", "content": prompt}],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "activity_enrichment",
                        "strict": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "activities": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "time": {"type": "string"},
                                            "location": {
                                                "type": ["string", "null"]
                                            },
                                            "address": {
                                                "type": ["string", "null"]
                                            },
                                            "lat": {
                                                "type": ["number", "null"]
                                            },
                                            "lon": {
                                                "type": ["number", "null"]
                                            },
                                        },
                                        "required": [
                                            "time",
                                            "location",
                                            "address",
                                            "lat",
                                            "lon",
                                        ],
                                        "additionalProperties": False,
                                    },
                                }
                            },
                            "required": ["activities"],
                            "additionalProperties": False,
                        },
                    },
                },
                # temperature basse on veut des faits, pas de créativité
                temperature=0.2,
                max_tokens=1000,
            )

            content = response.choices[0].message.content
            if not content:
                print("AIService: réponse vide retournée par Groq")
                return None

            result = json.loads(content)
            if not isinstance(result, dict) or not isinstance(
                result.get("activities"), list
            ):
                print("AIService: structure JSON inattendue retournée par Groq")
                return None

            return result["activities"]

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