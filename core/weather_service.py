# weather_service.py
"""
Module responsable de l'accès aux données météorologiques via l'API
OpenWeatherMap. Il fournit des méthodes pour :

- récupérer la météo actuelle d'une ville
- obtenir des prévisions météorologiques sur plusieurs jours
- détecter automatiquement la ville de l'utilisateur via son adresse IP
- mettre en cache les résultats afin de limiter les appels API

Le cache permet de conserver les données météorologiques pendant une
durée définie afin d'éviter des requêtes inutiles vers l'API externe.

Problème géolocalisation :
    ip-api.com peut retourner de très petites communes (ex: "Canéjean")
    qu'OpenWeatherMap ne connaît pas. get_city_auto() vérifie maintenant
    que la ville détectée existe bien dans OpenWeatherMap avant de la
    retourner. Si elle est inconnue, elle essaie la région, puis fallback
    sur None pour que main() utilise une ville par défaut.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import core.config  
import os
import requests
import json
from datetime import datetime
from models import WeatherData
from dataclasses import asdict


class WeatherService:
    """
    Service permettant d'interagir avec l'API OpenWeatherMap.

    Cette classe centralise toutes les opérations liées à la récupération
    et au traitement des données météorologiques.

    Attributes
    ----------
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

    BASE_URL       = "https://api.openweathermap.org/data/2.5"
    CACHE_FILE     =CACHE_FILE = str(core.config.DATA_DIR / "cache_meteo.json")
    CACHE_DURATION = 30  # minutes

    def __init__(self, city=None):
        """
        Initialise le service météo.

        Parameters
        ----------
        city : str | None, optional
            Ville initiale utilisée par le service (facultatif).
        """
        self.api_key   = os.getenv("API_KEY")
        self.last_city = city

    def get_current(self, city: str) -> WeatherData | None:
        """
        Récupère la météo actuelle pour une ville donnée.

        Vérifie d'abord le cache local. Si les données sont encore valides
        (moins de CACHE_DURATION minutes), les retourne directement sans
        appel réseau. Sinon effectue la requête OpenWeatherMap.

        Parameters
        ----------
        city : str
            Nom de la ville dont on souhaite obtenir la météo.

        Returns
        -------
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
            "q":     city,
            "appid": self.api_key,
            "units": "metric",
            "lang":  "fr",
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
                lat=data["coord"]["lat"],
                lon=data["coord"]["lon"],
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
        Cette méthode ne conserve que l'entrée à 12h00 pour chaque journée.

        Parameters
        ----------
        city : str
            Ville pour laquelle on souhaite obtenir les prévisions.
        days : int, optional
            Nombre de jours de prévision à récupérer (défaut : 5).

        Returns
        -------
        list[WeatherData]
            Liste contenant les données météo pour chaque jour demandé.
        """
        if not self.api_key:
            print("Erreur : API_KEY non configurée")
            return []

        params = {
            "q":     city,
            "appid": self.api_key,
            "units": "metric",
            "lang":  "fr",
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

    def get_day_slots(self, city: str) -> dict[str, WeatherData]:
        """
        Retourne la météo pour chaque créneau de la journée (toutes les 3h).

        Filtre les prévisions pour ne garder que celles d'aujourd'hui
        et les formate en dictionnaire heure → WeatherData.

        Parameters
        ----------
        city : str
            Ville pour laquelle récupérer les créneaux horaires.

        Returns
        -------
        dict[str, WeatherData]
            Dictionnaire {"08:00": WeatherData, "11:00": WeatherData, ...}
            Ne contient que les créneaux de la journée en cours.
        """
        if not self.api_key:
            return {}

        params = {
            "q":     city,
            "appid": self.api_key,
            "units": "metric",
            "lang":  "fr",
        }

        try:
            response = requests.get(f"{self.BASE_URL}/forecast", params=params)
            response.raise_for_status()
            data = response.json()

            slots = {}
            today = datetime.now().strftime("%Y-%m-%d")

            for entry in data["list"]:
                if entry["dt_txt"].startswith(today):
                    time        = entry["dt_txt"].split(" ")[1][:5]
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

    def set_city(self, city: str) -> None:
        """
        Définit la ville active du service.

        Parameters
        ----------
        city : str
            Nom de la ville.
        """
        self.last_city = city

    def get_city(self) -> str | None:
        """
        Retourne la ville actuellement définie.

        Returns
        -------
        str | None
            Nom de la ville active.
        """
        return self.last_city

    def _city_exists(self, city: str) -> bool:
        """
        Vérifie si OpenWeatherMap connaît cette ville.

        Fait une requête légère sans cache — appelée uniquement au démarrage
        par get_city_auto() pour valider la ville détectée par géolocalisation.
        Les petites communes comme "Canéjean" retournent 404 et sont rejetées.

        Parameters
        ----------
        city : str
            Nom de la ville à vérifier.

        Returns
        -------
        bool
            True si OpenWeatherMap connaît cette ville, False sinon.
        """
        if not self.api_key or not city:
            return False

        try:
            response = requests.get(
                f"{self.BASE_URL}/weather",
                params={
                    "q":     city,
                    "appid": self.api_key,
                    "units": "metric",
                },
                timeout=3
            )
            return response.status_code == 200

        except Exception:
            return False

    def get_city_auto(self) -> str | None:
        """
        Tente de détecter automatiquement la ville de l'utilisateur.

        La détection repose sur des services de géolocalisation par adresse IP.
        Problème connu : ip-api.com peut retourner de très petites communes
        (ex: "Canéjean") qu'OpenWeatherMap ne reconnaît pas et retourne 404.

        - Essaie la ville exacte détectée par IP
        - Si inconnue d'OpenWeatherMap, essaie la région (regionName)
        - Si la région est aussi inconnue, retourne None

        Returns
        -------
        str | None
            Nom de la ville validée par OpenWeatherMap, ou None si échec.
        """
        sources = [
            {"url": "http://ip-api.com/json/?lang=fr", "check_status": True},
            {"url": "https://ipinfo.io/json",           "check_status": False},
            {"url": "http://ip-api.com/json/",          "check_status": True},
        ]

        for source in sources:
            try:
                response = requests.get(source["url"], timeout=4)
                response.raise_for_status()
                data = response.json()

                city = None
                region_name = None

                if source["check_status"]:
                    if data.get("status") == "success":
                        city = data.get("city")
                        region_name = data.get("regionName")
                else:
                    city = data.get("city")
                    region_name = data.get("region")

                if not city:
                    continue

                #vérifie la ville exacte
                if self._city_exists(city):
                    self.last_city = city
                    return city

                # ville inconnue, essaie la région
                # "Canéjean" inconnue,  essaie "Gironde" ou "Nouvelle-Aquitaine"
                if region_name and self._city_exists(region_name):
                    print(f"Ville '{city}' inconnue d'OpenWeatherMap, utilisation de la région '{region_name}'")
                    self.last_city = region_name
                    return region_name

                # région aussi inconnue, on essaie la source suivante
                print(f"Ville '{city}' et région '{region_name}' inconnues d'OpenWeatherMap")

            except requests.exceptions.ConnectionError:
                continue
            except Exception:
                continue

        # Toutes les sources ont échoué donc on retourne None
        return None

    def _save_cache(self, city: str, weather: WeatherData) -> None:
        """
        Sauvegarde les données météo dans le cache JSON.

        Parameters
        ----------
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
            "data":      asdict(weather),
        }

        with open(self.CACHE_FILE, "w") as f:
            json.dump(cache, f, indent=2)

    def _load_cache(self, city: str) -> WeatherData | None:
        """
        Charge les données météo depuis le cache si elles sont encore valides.

        Le cache est valide si la dernière mise à jour date de moins de
        CACHE_DURATION minutes.

        Parameters
        ----------
        city : str
            Ville recherchée dans le cache.

        Returns
        -------
        WeatherData | None
            Données météo du cache, ou None si absent ou expiré.
        """
        try:
            with open(self.CACHE_FILE, "r") as f:
                cache = json.load(f)

            if not cache.get(city):
                return None

            timestamp = datetime.fromisoformat(cache[city]["timestamp"])
            delta     = datetime.now() - timestamp

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
                    lat=data.get("lat", 0.0),
                    lon=data.get("lon", 0.0),
                )

            return None

        except FileNotFoundError:
            return None


if __name__ == "__main__":
    s = WeatherService()
    city = s.get_city_auto()
    print(f"Ville détectée : {city}")
    if city:
        print(s.get_current(city))