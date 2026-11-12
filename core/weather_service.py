"""Client météo de l'application desktop.

Les données OpenWeatherMap sont maintenant récupérées par le backend FastAPI.
Ce module conserve l'interface utilisée par l'application, adapte les réponses
JSON aux dataclasses du desktop et garde le cache météo local.
"""

import json
import sys
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

sys.path.insert(0, str(Path(__file__).parent.parent))

import core.config
from models import WeatherData


class WeatherService:
    """Fournit à l'application desktop les données météo du backend."""

    API_BASE_URL = core.config.WEATHER_API_BASE_URL
    CACHE_FILE = str(core.config.USER_DATA_DIR / "cache_meteo.json")
    CACHE_DURATION = 30
    REQUEST_TIMEOUT = 10
    GEOLOCATION_URL = "https://ipinfo.io/json"

    def __init__(self, city: str | None = None):
        """Initialise le service et mémorise éventuellement la ville active."""
        self.last_city = city

    def get_current(self, city: str) -> WeatherData | None:
        """Retourne la météo actuelle d'une ville.

        Les données du cache local sont utilisées si elles ont moins de
        ``CACHE_DURATION`` minutes. Sinon, le service appelle le backend.
        Une erreur réseau, une ville inconnue ou une réponse invalide donne
        ``None`` afin que l'interface puisse afficher son état d'erreur.
        """
        cached_weather = self._load_cache(city)
        if cached_weather is not None:
            return cached_weather

        weather_data = self._get_api_json(
            "/v1/weather/current",
            city,
        )
        if weather_data is None:
            return None

        try:
            weather = WeatherData(**weather_data)
        except (TypeError, ValueError) as error:
            print(f"Réponse météo invalide du backend : {error}")
            return None

        self._save_cache(city, weather)
        self.last_city = city
        return weather

    def get_day_slots(self, city: str) -> dict[str, WeatherData]:
        """Retourne les prévisions météo par créneau pour la journée.

        Le backend renvoie un objet contenant le nom de la ville et un
        dictionnaire ``slots``. Cette méthode ajoute le nom de la ville à
        chaque créneau pour construire les ``WeatherData`` attendus par l'UI.
        """
        forecast = self._get_api_json(
            "/v1/weather/forecast/today",
            city,
        )
        if forecast is None:
            return {}

        city_name = forecast.get("city")
        forecast_slots = forecast.get("slots")
        if not isinstance(city_name, str) or not isinstance(forecast_slots, dict):
            print("Réponse de prévisions invalide du backend")
            return {}

        slots: dict[str, WeatherData] = {}
        try:
            for slot_time, slot_data in forecast_slots.items():
                if not isinstance(slot_data, dict):
                    raise TypeError("Un créneau météo n'est pas un objet JSON")
                slots[str(slot_time)] = WeatherData(
                    city=city_name,
                    **slot_data,
                )
        except (TypeError, ValueError) as error:
            print(f"Créneaux météo invalides du backend : {error}")
            return {}

        self.last_city = city_name
        return slots

    def set_city(self, city: str) -> None:
        """Définit la ville active du service."""
        self.last_city = city

    def get_city(self) -> str | None:
        """Retourne la ville actuellement mémorisée, ou ``None``."""
        return self.last_city

    def get_city_auto(self) -> str | None:
        """Tente d'obtenir la ville approximative depuis l'adresse IP publique.

        La requête de géolocalisation est envoyée à ipinfo.io en HTTPS. Cette
        ville n'est pas vérifiée auprès d'OpenWeatherMap ici : le backend
        retournera une erreur si le fournisseur météo ne la reconnaît pas.
        Le service tiers de géolocalisation reçoit l'adresse IP du client.
        """
        try:
            response = requests.get(
                self.GEOLOCATION_URL,
                timeout=4,
            )
            response.raise_for_status()
            location_data = response.json()
        except requests.exceptions.Timeout:
            print("La géolocalisation a dépassé le délai d'attente")
            return None
        except ValueError as error:
            print(f"Réponse de géolocalisation invalide : {error}")
            return None
        except requests.exceptions.RequestException as error:
            print(f"Erreur de géolocalisation : {error}")
            return None

        if not isinstance(location_data, dict):
            print("Réponse de géolocalisation invalide")
            return None

        city = location_data.get("city")
        if not isinstance(city, str) or not city.strip():
            return None

        self.last_city = city.strip()
        return self.last_city

    def _get_api_json(self, endpoint: str, city: str) -> dict[str, Any] | None:
        """Appelle une route météo du backend et retourne son objet JSON.

        ``endpoint`` est le chemin de la route backend, par exemple
        ``/v1/weather/current``. La ville est transmise comme paramètre de
        requête, et non concaténée manuellement à l'URL.
        """
        try:
            response = requests.get(
                f"{self.API_BASE_URL}{endpoint}",
                params={"city": city},
                timeout=self.REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.Timeout:
            print("La requête météo a dépassé le délai d'attente")
            return None
        except requests.exceptions.HTTPError as error:
            status_code = error.response.status_code if error.response else None
            if status_code == 404:
                print(f"Ville inconnue du service météo : {city}")
            else:
                print(f"Erreur HTTP du service météo : {status_code}")
            return None
        except ValueError as error:
            print(f"Le backend météo a renvoyé un JSON invalide : {error}")
            return None
        except requests.exceptions.RequestException as error:
            print(f"Impossible de contacter le backend météo : {error}")
            return None

        if not isinstance(data, dict):
            print("Le backend météo n'a pas renvoyé un objet JSON")
            return None
        return data

    def _save_cache(self, city: str, weather: WeatherData) -> None:
        """Enregistre la météo actuelle dans le cache JSON local."""
        cache_path = Path(self.CACHE_FILE)
        try:
            with cache_path.open("r", encoding="utf-8") as cache_file:
                cache = json.load(cache_file)
        except FileNotFoundError:
            cache = {}
        except json.JSONDecodeError as error:
            print(f"Cache météo illisible, il sera recréé : {error}")
            cache = {}

        if not isinstance(cache, dict):
            print("Cache météo invalide, il sera recréé")
            cache = {}

        cache[city] = {
            "timestamp": datetime.now().isoformat(),
            "data": asdict(weather),
        }

        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with cache_path.open("w", encoding="utf-8") as cache_file:
            json.dump(cache, cache_file, indent=2, ensure_ascii=False)

    def _load_cache(self, city: str) -> WeatherData | None:
        """Retourne les données météo du cache si elles sont encore valides."""
        cache_path = Path(self.CACHE_FILE)
        try:
            with cache_path.open("r", encoding="utf-8") as cache_file:
                cache = json.load(cache_file)

            if not isinstance(cache, dict):
                raise ValueError("Le contenu du cache n'est pas un objet JSON")

            cache_entry = cache.get(city)
            if not isinstance(cache_entry, dict):
                return None

            timestamp = datetime.fromisoformat(cache_entry["timestamp"])
            age_minutes = (datetime.now() - timestamp).total_seconds() / 60
            if not 0 <= age_minutes <= self.CACHE_DURATION:
                return None

            weather_data = cache_entry["data"]
            if not isinstance(weather_data, dict):
                raise ValueError("Les données météo en cache sont invalides")
            return WeatherData(**weather_data)
        except FileNotFoundError:
            return None
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
            print(f"Entrée de cache météo invalide pour {city} : {error}")
            return None


if __name__ == "__main__":
    service = WeatherService()
    city = service.get_city_auto() or "Libreville"
    print(f"Ville utilisée : {city}")
    print(service.get_current(city))
