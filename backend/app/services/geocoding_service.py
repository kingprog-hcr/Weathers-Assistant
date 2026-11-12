"""Geocode activity venues with a cached, rate-limited Nominatim client."""

import hashlib
import logging
import os
import re
import sqlite3
import time
import unicodedata
from pathlib import Path
from typing import TypeAlias

import httpx
from dotenv import load_dotenv

from app.schemas import ActivityEnrichmentResponse


BACKEND_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_DIR / ".env")

logger = logging.getLogger(__name__)

Coordinates: TypeAlias = tuple[float, float] | None


class NominatimGeocodingService:
    """Adds verified venue coordinates to Groq's textual place suggestions."""

    DEFAULT_BASE_URL = "https://nominatim.openstreetmap.org"
    DEFAULT_USER_AGENT = (
        "WeatherProgramm/1.0.1 "
        "(https://github.com/kingprog-hcr/Weathers-Assistant)"
    )
    DEFAULT_CACHE_PATH = BACKEND_DIR / ".cache" / "nominatim.sqlite3"
    REQUEST_TIMEOUT_SECONDS = 5.0
    MIN_REQUEST_INTERVAL_SECONDS = 1.0
    POSITIVE_CACHE_TTL_SECONDS = 30 * 24 * 60 * 60
    NEGATIVE_CACHE_TTL_SECONDS = 24 * 60 * 60
    CITY_ADDRESS_FIELDS = (
        "city",
        "town",
        "village",
        "municipality",
        "hamlet",
    )

    def __init__(
        self,
        cache_path: str | Path | None = None,
        base_url: str | None = None,
        user_agent: str | None = None,
    ):
        self.cache_path = Path(
            cache_path
            or os.getenv("NOMINATIM_CACHE_PATH")
            or self.DEFAULT_CACHE_PATH
        )
        self.base_url = (
            base_url or os.getenv("NOMINATIM_BASE_URL") or self.DEFAULT_BASE_URL
        ).rstrip("/")
        self.user_agent = (
            user_agent
            or os.getenv("NOMINATIM_USER_AGENT")
            or self.DEFAULT_USER_AGENT
        )

    def geocode_activities(
        self,
        enrichment: ActivityEnrichmentResponse,
        city: str,
    ) -> ActivityEnrichmentResponse:
        """Return the enrichment with coordinates for places found in ``city``."""
        activities = []
        for activity in enrichment.activities:
            if not activity.location or not activity.location.strip():
                activities.append(activity)
                continue

            place_queries = [activity.location.strip()]
            if (
                activity.address
                and activity.address.strip()
                and self._normalize(activity.address)
                != self._normalize(activity.location)
            ):
                place_queries.append(activity.address.strip())

            coordinates = None
            for place_query in place_queries:
                query = self._with_city(place_query, city)
                coordinates = self._geocode(query, city)
                if coordinates is not None:
                    break

            if coordinates is None:
                activities.append(
                    activity.model_copy(update={"lat": None, "lon": None})
                )
                continue

            latitude, longitude = coordinates
            activities.append(
                activity.model_copy(
                    update={"lat": latitude, "lon": longitude}
                )
            )

        return enrichment.model_copy(update={"activities": activities})

    def _geocode(self, query: str, city: str) -> Coordinates:
        cache_input = f"{query}\n{city}"
        cache_key = hashlib.sha256(
            self._normalize(cache_input).encode("utf-8")
        ).hexdigest()

        try:
            return self._geocode_with_cache(cache_key, query, city)
        except (OSError, sqlite3.Error) as error:
            logger.warning("Nominatim cache is unavailable: %s", error)
            return None

    def _geocode_with_cache(
        self,
        cache_key: str,
        query: str,
        city: str,
    ) -> Coordinates:
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.cache_path, timeout=30)
        connection.execute("PRAGMA busy_timeout = 30000")
        try:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS geocode_cache (
                    cache_key TEXT PRIMARY KEY,
                    latitude REAL,
                    longitude REAL,
                    expires_at REAL NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS geocoder_state (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    last_request_at REAL NOT NULL
                )
                """
            )
            connection.execute("BEGIN IMMEDIATE")

            now = time.time()
            cached = connection.execute(
                """
                SELECT latitude, longitude, expires_at
                FROM geocode_cache
                WHERE cache_key = ?
                """,
                (cache_key,),
            ).fetchone()
            if cached is not None and cached[2] > now:
                connection.commit()
                if cached[0] is None or cached[1] is None:
                    return None
                return float(cached[0]), float(cached[1])
            if cached is not None:
                connection.execute(
                    "DELETE FROM geocode_cache WHERE cache_key = ?",
                    (cache_key,),
                )

            previous = connection.execute(
                "SELECT last_request_at FROM geocoder_state WHERE id = 1"
            ).fetchone()
            if previous is not None:
                wait_seconds = (
                    previous[0] + self.MIN_REQUEST_INTERVAL_SECONDS - time.time()
                )
                if wait_seconds > 0:
                    time.sleep(wait_seconds)

            coordinates, cacheable = self._request_coordinates(query, city)
            connection.execute(
                """
                INSERT OR REPLACE INTO geocoder_state (id, last_request_at)
                VALUES (1, ?)
                """,
                (time.time(),),
            )

            if cacheable:
                ttl = (
                    self.POSITIVE_CACHE_TTL_SECONDS
                    if coordinates is not None
                    else self.NEGATIVE_CACHE_TTL_SECONDS
                )
                connection.execute(
                    """
                    INSERT OR REPLACE INTO geocode_cache
                        (cache_key, latitude, longitude, expires_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        cache_key,
                        coordinates[0] if coordinates else None,
                        coordinates[1] if coordinates else None,
                        time.time() + ttl,
                    ),
                )
            connection.commit()
            return coordinates
        except sqlite3.Error:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _request_coordinates(
        self,
        query: str,
        city: str,
    ) -> tuple[Coordinates, bool]:
        try:
            response = httpx.get(
                f"{self.base_url}/search",
                params={
                    "q": query,
                    "format": "jsonv2",
                    "addressdetails": 1,
                    "limit": 5,
                    "accept-language": "fr",
                },
                headers={"User-Agent": self.user_agent},
                timeout=self.REQUEST_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            results = response.json()
        except (httpx.RequestError, httpx.HTTPStatusError, ValueError) as error:
            logger.warning("Nominatim lookup failed: %s", error)
            return None, False

        if not isinstance(results, list):
            logger.warning("Nominatim returned an invalid search response")
            return None, False

        for result in results:
            coordinates = self._coordinates_for_city(result, city)
            if coordinates is not None:
                return coordinates, True
        return None, True

    @classmethod
    def _coordinates_for_city(cls, result: object, city: str) -> Coordinates:
        if not isinstance(result, dict):
            return None

        address = result.get("address")
        if not isinstance(address, dict) or not cls._matches_city(address, city):
            return None

        try:
            latitude = float(result["lat"])
            longitude = float(result["lon"])
        except (KeyError, TypeError, ValueError):
            return None

        if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
            return None
        return latitude, longitude

    @classmethod
    def _matches_city(cls, address: dict, city: str) -> bool:
        requested_city = city.split(",", maxsplit=1)[0]
        normalized_city = cls._normalize(requested_city)
        return any(
            isinstance(address.get(field), str)
            and cls._normalize(address[field]) == normalized_city
            for field in cls.CITY_ADDRESS_FIELDS
        )

    @classmethod
    def _with_city(cls, place: str, city: str) -> str:
        normalized_place = cls._normalize(place)
        normalized_city = cls._normalize(city.split(",", maxsplit=1)[0])
        if f" {normalized_city} " in f" {normalized_place} ":
            return place
        return f"{place}, {city}"

    @staticmethod
    def _normalize(value: str) -> str:
        without_accents = unicodedata.normalize("NFKD", value)
        ascii_text = without_accents.encode("ascii", "ignore").decode("ascii")
        return re.sub(r"\s+", " ", ascii_text.casefold()).strip()
