"""
weather_service.py

Module responsable de l'accès aux données météorologiques via l'API
OpenWeatherMap. Il fournit des méthodes pour :

- récupérer la météo actuelle d'une ville
- obtenir des prévisions météorologiques sur plusieurs jours
- détecter automatiquement la ville de l'utilisateur via son adresse IP
- mettre en cache les résultats afin de limiter les appels API

Le cache permet de conserver les données météorologiques pendant une
durée définie afin d'éviter des requêtes inutiles vers l'API externe.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv
from models import WeatherData
from dataclasses import asdict


class WeatherService:
    """
    Service permettant d'interagir avec l'API OpenWeatherMap.

    Cette classe centralise toutes les opérations liées à la récupération
    et au traitement des données météorologiques.

    Attributes
   
    BASE_URL : str
        URL de base de l'API OpenWeatherMap.
    CACHE_FILE : str
        Chemin vers le fichier JSON contenant les données mises en cache.
    CACHE_DURATION : int
        Durée de validité du cache en minutes.
    api_key : str | None
        Clé API utilisée pour authentifier les requêtes vers l'API météo.
    last_city : str | None
        Dernière ville consultée par l'utilisateur.
    """

    BASE_URL = "https://api.openweathermap.org/data/2.5"
    CACHE_FILE = "data/cache_meteo.json"
    CACHE_DURATION = 30  # minutes

    def __init__(self, city=None):
        """
        Initialise le service météo.

        Parameters
        
        city : str | None, optional
            Ville initiale utilisée par le service (facultatif).
        """
        load_dotenv()
        self.api_key = os.getenv("API_KEY")
        self.last_city = city

    def get_current(self, city: str) -> WeatherData | None:
        """
        Récupère la météo actuelle pour une ville donnée.

        Cette méthode vérifie d'abord si des données valides sont présentes
        dans le cache. Si c'est le cas, elles sont retournées directement
        sans effectuer d'appel à l'API.

        Parameters
        
        city : str
            Nom de la ville dont on souhaite obtenir la météo.

        Returns

        WeatherData | None
            Objet contenant les données météorologiques si la requête
            réussit, sinon None.
        """

        cached = self._load_cache(city)
        if cached:
            return cached

        if not self.api_key:
            print("Erreur : API_KEY non configurée")
            return None

        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric",
            "lang": "fr",
        }

        try:
            response = requests.get(f"{self.BASE_URL}/weather", params=params)
            response.raise_for_status()
            data = response.json()

            weather = WeatherData(
                city=data["name"],
                temp=data["main"]["temp"],
                feels_like=data["main"]["feels_like"],
                condition=data["weather"][0]["main"],
                description=data["weather"][0]["description"],
                icon=data["weather"][0]["icon"],
                humidity=data["main"]["humidity"],
                wind_speed=data["wind"]["speed"],
            )

            self._save_cache(city, weather)
            self.last_city = city

            return weather

        except requests.exceptions.HTTPError as e:
            print(f"Erreur HTTP : {e}")
        except requests.exceptions.ConnectionError:
            print("Pas de connexion internet")

        return None

    def get_forecast(self, city: str, days: int = 5) -> list[WeatherData]:
        """
        Récupère les prévisions météorologiques pour plusieurs jours.

        L'API OpenWeatherMap renvoie des prévisions toutes les 3 heures.
        Afin de simplifier l'affichage, cette méthode ne conserve que
        l'entrée correspondant à 12h00 pour chaque journée.

        Parameters
    
        city : str
            Ville pour laquelle on souhaite obtenir les prévisions.
        days : int, optional
            Nombre de jours de prévision à récupérer (par défaut : 5).

        Returns

        list[WeatherData]
            Liste contenant les données météo pour chaque jour demandé.
        """

        if not self.api_key:
            print("Erreur : API_KEY non configurée")
            return []

        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric",
            "lang": "fr",
        }

        try:
            response = requests.get(f"{self.BASE_URL}/forecast", params=params)
            response.raise_for_status()
            data = response.json()

            forecasts = []

            for entry in data["list"]:
                if "12:00:00" in entry["dt_txt"]:
                    weather = WeatherData(
                        city=city,
                        temp=entry["main"]["temp"],
                        feels_like=entry["main"]["feels_like"],
                        condition=entry["weather"][0]["main"],
                        description=entry["weather"][0]["description"],
                        icon=entry["weather"][0]["icon"],
                        humidity=entry["main"]["humidity"],
                        wind_speed=entry["wind"]["speed"],
                    )

                    forecasts.append(weather)

                    if len(forecasts) == days:
                        break

            return forecasts

        except requests.exceptions.HTTPError as e:
            print(f"Erreur HTTP : {e}")
        except requests.exceptions.ConnectionError:
            print("Pas de connexion internet")

        return []

    def set_city(self, city):
        """
        Définit la ville active du service.

        Parameters
        
        city : str
            Nom de la ville.
        """
        self.last_city = city

    def get_city(self):
        """
        Retourne la ville actuellement définie.

        Returns

        str
            Nom de la ville active.
        """
        return self.last_city

    def get_city_auto(self) -> str | None:
        """
        Tente de détecter automatiquement la ville de l'utilisateur.

        La détection repose sur des services de géolocalisation par adresse IP.
        Plusieurs sources sont testées afin d'augmenter la robustesse du
        système en cas d'indisponibilité d'un service.

        Returns
        
        str | None
            Nom de la ville détectée ou None si la détection échoue.
        """

        sources = [
            {"url": "http://ip-api.com/json/?lang=fr", "check_status": True},
            {"url": "https://ipinfo.io/json", "check_status": False},
            {"url": "http://ip-api.com/json/", "check_status": True},
        ]

        for source in sources:
            try:
                response = requests.get(source["url"])
                response.raise_for_status()
                data = response.json()

                if source["check_status"]:
                    if data.get("status") == "success" and data.get("city"):
                        self.last_city = data["city"]
                        return data["city"]
                else:
                    if data.get("city"):
                        self.last_city = data["city"]
                        return data["city"]

            except requests.exceptions.ConnectionError:
                pass

        return None
    
    def get_day_slots(self, city: str) -> dict[str, WeatherData]:
        """
        Retourne la météo pour chaque créneau de la journée (données toutes les 3h).
        Retourne un dict { "08:00": WeatherData, "11:00": WeatherData, ... }
        """
        if not self.api_key:
            return {}

        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric",
            "lang": "fr",
        }

        try:
            response = requests.get(f"{self.BASE_URL}/forecast", params=params)
            response.raise_for_status()
            data = response.json()

            slots = {}
            today = datetime.now().strftime("%Y-%m-%d")

            for entry in data["list"]:
                # garder uniquement les créneaux d'aujourd'hui
                if entry["dt_txt"].startswith(today):
                    time = entry["dt_txt"].split(" ")[1][:5]  # "08:00"
                    slots[time] = WeatherData(
                        city=city,
                        temp=entry["main"]["temp"],
                        feels_like=entry["main"]["feels_like"],
                        condition=entry["weather"][0]["main"],
                        description=entry["weather"][0]["description"],
                        icon=entry["weather"][0]["icon"],
                        humidity=entry["main"]["humidity"],
                        wind_speed=entry["wind"]["speed"],
                    )

            return slots

        except requests.exceptions.HTTPError as e:
            print(f"Erreur HTTP : {e}")
        except requests.exceptions.ConnectionError:
            print("Pas de connexion internet")
        return {}

    # Méthodes privées (cache)

    def _save_cache(self, city: str, weather: WeatherData) -> None:
        """
        Sauvegarde les données météo dans le cache JSON.

        Parameters
    
        city : str
            Ville associée aux données météo.
        weather : WeatherData
            Données météorologiques à sauvegarder.
        """

        try:
            with open(self.CACHE_FILE, "r") as f:
                cache = json.load(f)
        except FileNotFoundError:
            cache = {}

        cache[city] = {
            "timestamp": datetime.now().isoformat(),
            "data": asdict(weather),
        }

        with open(self.CACHE_FILE, "w") as f:
            json.dump(cache, f, indent=2)

    def _load_cache(self, city: str) -> WeatherData | None:
        """
        Charge les données météo depuis le cache si elles sont encore valides.

        Le cache est considéré valide uniquement si la dernière mise à jour
        est inférieure à CACHE_DURATION en minutes.

        Parameters

        city : str
            Ville recherchée.

        Returns
    
        WeatherData | None
            Données météo provenant du cache ou None si le cache est absent
            ou expiré.
        """

        try:
            with open(self.CACHE_FILE, "r") as f:
                cache = json.load(f)

            if not cache.get(city):
                return None

            timestamp = datetime.fromisoformat(cache[city]["timestamp"])
            delta = datetime.now() - timestamp

            if delta.total_seconds() / 60 <= self.CACHE_DURATION:
                data = cache[city]["data"]

                return WeatherData(
                    city=data["city"],
                    temp=data["temp"],
                    feels_like=data["feels_like"],
                    condition=data["condition"],
                    description=data["description"],
                    icon=data["icon"],
                    humidity=data["humidity"],
                    wind_speed=data["wind_speed"],
                )

            return None

        except FileNotFoundError:
            return None


if __name__ == "__main__":
    pass