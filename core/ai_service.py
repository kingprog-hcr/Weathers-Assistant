"""Client desktop pour le service d'enrichissement du backend."""

import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent.parent))

import core.config


class AIService:
    """Envoie les activités au backend et préserve le repli local de l'application."""

    ENDPOINT = "/v1/activities/enrich"
    REQUEST_TIMEOUT = 30

    def __init__(self):
        """Initialise le client sans charger de clé Groq sur le desktop."""
        self.api_base_url = core.config.WEATHER_API_BASE_URL

    def is_available(self) -> bool:
        """Indique si une URL de backend est configurée, sans tester le réseau."""
        return bool(self.api_base_url)

    def enrich_activities(
        self,
        activities: list[dict],
        city: str,
    ) -> list[dict] | None:
        """Demande au backend d'enrichir les activités existantes.

        Retourne la liste enrichie attendue par ``DayPlanner``. En cas d'erreur
        réseau, HTTP ou de réponse invalide, retourne ``None`` pour que le
        programme local reste utilisable.
        """
        if not activities:
            return []

        payload = {
            "city": city,
            "activities": activities,
        }

        try:
            response = requests.post(
                f"{self.api_base_url}{self.ENDPOINT}",
                json=payload,
                timeout=self.REQUEST_TIMEOUT,
            )
        except requests.exceptions.Timeout:
            print("Le service d'enrichissement a dépassé le délai d'attente")
            return None
        except requests.exceptions.RequestException as error:
            print(f"Impossible de contacter le service d'enrichissement : {error}")
            return None

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as error:
            status_code = error.response.status_code if error.response else None
            print(f"Erreur HTTP du service d'enrichissement : {status_code}")
            return None

        try:
            result = response.json()
        except ValueError as error:
            print(f"Réponse JSON invalide du service d'enrichissement : {error}")
            return None

        if not isinstance(result, dict):
            print("Réponse invalide du service d'enrichissement")
            return None

        enriched_activities = result.get("activities")
        if not isinstance(enriched_activities, list):
            print("La réponse du backend ne contient pas une liste d'activités")
            return None

        expected_times = [activity.get("time") for activity in activities]
        returned_times = [
            activity.get("time") if isinstance(activity, dict) else None
            for activity in enriched_activities
        ]
        if returned_times != expected_times:
            print("La réponse du backend ne correspond pas aux activités envoyées")
            return None

        for activity in enriched_activities:
            if not isinstance(activity, dict):
                print("Le backend a renvoyé une activité invalide")
                return None
            if activity.get("location") is not None and not isinstance(
                activity["location"], str
            ):
                print("Le backend a renvoyé un lieu invalide")
                return None
            if activity.get("address") is not None and not isinstance(
                activity["address"], str
            ):
                print("Le backend a renvoyé une adresse invalide")
                return None

        return enriched_activities


if __name__ == "__main__":
    service = AIService()
    test_activities = [
        {"time": "10:00", "activity": "Visite d'un musée"},
        {"time": "14:00", "activity": "Balade dans un parc"},
    ]
    city = input("Entre une ville : ")
    result = service.enrich_activities(test_activities, city=city)
    if result is None:
        print("Enrichissement indisponible, le programme local reste utilisable")
    else:
        print(result)
