import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv

from app.schemas import (
    CurrentWeatherResponse,
    DaySlotsResponse,
    WeatherSlotResponse,
)


# En local, charge le .env du backend. L'hebergeur fournit cette variable
# directement dans sa configuration de secrets.
BACKEND_ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(BACKEND_ENV_PATH)


class WeatherServiceError(Exception):
    """Erreur meteo que les routes peuvent convertir en reponse HTTP."""


class WeatherConfigurationError(WeatherServiceError):
    """La cle OpenWeatherMap est absente."""


class CityNotFoundError(WeatherServiceError):
    """OpenWeatherMap ne connait pas la ville demandee."""


class WeatherProviderError(WeatherServiceError):
    """Le fournisseur est indisponible ou a renvoye des donnees invalides."""


class OpenWeatherMapService:
    """Recupere et transforme les donnees meteorologiques pour le backend."""

    BASE_URL = "https://api.openweathermap.org/data/2.5"
    TIMEOUT_SECONDS = 10.0

    def __init__(self, api_key: str | None = None):
        configured_api_key = api_key or os.getenv("OPENWEATHER_API_KEY")
        if not configured_api_key:
            raise WeatherConfigurationError(
                "The OPENWEATHER_API_KEY setting is missing"
            )
        self._api_key: str = configured_api_key

    def get_current_weather(self, city: str) -> CurrentWeatherResponse:
        """Retourne la meteo actuelle d'une ville."""
        data = self._get_city_data("/weather", city)

        try:
            weather = data["weather"][0]
            return CurrentWeatherResponse(
                city=data["name"],
                temp=data["main"]["temp"],
                feels_like=data["main"]["feels_like"],
                condition=weather["main"],
                description=weather["description"],
                icon=weather["icon"],
                humidity=data["main"]["humidity"],
                wind_speed=data["wind"]["speed"],
                lat=data["coord"]["lat"],
                lon=data["coord"]["lon"],
            )
        except (IndexError, KeyError, TypeError, ValueError) as error:
            raise WeatherProviderError(
                "OpenWeatherMap returned an invalid current-weather payload"
            ) from error

    def get_today_weather_slots(self, city: str) -> DaySlotsResponse:
        """Retourne les previsions par creneau dans l'heure locale de la ville."""
        data = self._get_city_data("/forecast", city)

        try:
            city_data = data["city"]
            city_timezone = timezone(timedelta(seconds=city_data["timezone"]))
            today = datetime.now(city_timezone).date()
            slots: dict[str, WeatherSlotResponse] = {}

            for entry in data["list"]:
                # Les dates OpenWeatherMap sont en UTC. On les convertit dans
                # le fuseau de la ville, pas celui du serveur.
                local_time = datetime.fromtimestamp(
                    entry["dt"], tz=timezone.utc
                ).astimezone(city_timezone)
                if local_time.date() != today:
                    continue

                weather = entry["weather"][0]
                slots[local_time.strftime("%H:%M")] = WeatherSlotResponse(
                    temp=entry["main"]["temp"],
                    feels_like=entry["main"]["feels_like"],
                    condition=weather["main"],
                    description=weather["description"],
                    icon=weather["icon"],
                    humidity=entry["main"]["humidity"],
                    wind_speed=entry["wind"]["speed"],
                )

            return DaySlotsResponse(city=city_data["name"], slots=slots)
        except (
            IndexError,
            KeyError,
            OverflowError,
            TypeError,
            ValueError,
        ) as error:
            raise WeatherProviderError(
                "OpenWeatherMap returned an invalid forecast payload"
            ) from error

    def _get_city_data(self, endpoint: str, city: str) -> dict[str, Any]:
        """Appelle un endpoint OpenWeatherMap et valide sa reponse JSON."""
        try:
            response = httpx.get(
                f"{self.BASE_URL}{endpoint}",
                params={
                    "q": city,
                    "appid": self._api_key,
                    "units": "metric",
                    "lang": "fr",
                },
                timeout=self.TIMEOUT_SECONDS,
            )

            if response.status_code == 404:
                raise CityNotFoundError(f"City not found: {city}")

            response.raise_for_status()
            data = response.json()
        except CityNotFoundError:
            raise
        except httpx.TimeoutException as error:
            raise WeatherProviderError(
                "OpenWeatherMap request timed out"
            ) from error
        except httpx.HTTPStatusError as error:
            raise WeatherProviderError(
                f"OpenWeatherMap returned HTTP {error.response.status_code}"
            ) from error
        except httpx.RequestError as error:
            raise WeatherProviderError(
                "Could not connect to OpenWeatherMap"
            ) from error
        except ValueError as error:
            raise WeatherProviderError(
                "OpenWeatherMap returned invalid JSON"
            ) from error

        if not isinstance(data, dict):
            raise WeatherProviderError(
                "OpenWeatherMap returned an invalid response"
            )
        return data
