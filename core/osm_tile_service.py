"""Download and cache visible OpenStreetMap raster tiles."""

import sqlite3
import threading
from datetime import timedelta
from pathlib import Path

from requests_cache import CachedSession

from core.config import get_user_data_path


class OSMTileCacheError(RuntimeError):
    """The persistent tile cache could not be opened or updated."""


class OSMTileService:
    """Fetch OSM tiles directly with an identifiable client and HTTP cache."""

    TILE_URL_TEMPLATE = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
    USER_AGENT = (
        "WeatherProgramm/1.1.0 "
        "(+https://github.com/kingprog-hcr/Weathers-Assistant)"
    )
    MAX_ZOOM = 19
    CACHE_EXPIRATION = timedelta(days=7)
    REQUEST_TIMEOUT_SECONDS = 10
    MAX_CONCURRENT_REQUESTS = 3

    def __init__(self, cache_name: str | Path | None = None):
        cache_path = (
            Path(cache_name)
            if cache_name is not None
            else get_user_data_path("osm_tiles_cache")
        )
        try:
            cache_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as error:
            raise OSMTileCacheError(
                "Could not create the OpenStreetMap tile cache directory"
            ) from error

        self._cache_name = str(cache_path)
        self._sessions = threading.local()
        self._session_creation_lock = threading.Lock()
        self._request_semaphore = threading.BoundedSemaphore(
            self.MAX_CONCURRENT_REQUESTS
        )
        self._session_for_current_thread()

    def get_tile(self, zoom: int, x: int, y: int) -> bytes | None:
        """Return a tile image, or None when its coordinates are outside the map."""
        tile_url = self._tile_url(zoom, x, y)
        if tile_url is None:
            return None

        try:
            with self._request_semaphore:
                response = self._session_for_current_thread().get(
                    tile_url,
                    headers={"User-Agent": self.USER_AGENT},
                    timeout=self.REQUEST_TIMEOUT_SECONDS,
                )
            response.raise_for_status()
        except sqlite3.Error as error:
            raise OSMTileCacheError(
                "Could not read or update the OpenStreetMap tile cache"
            ) from error

        return response.content

    def _tile_url(self, zoom: int, x: int, y: int) -> str | None:
        if not 0 <= zoom <= self.MAX_ZOOM:
            return None

        tile_count = 1 << zoom
        if not 0 <= y < tile_count:
            return None

        wrapped_x = x % tile_count
        return self.TILE_URL_TEMPLATE.format(z=zoom, x=wrapped_x, y=y)

    def _session_for_current_thread(self) -> CachedSession:
        session = getattr(self._sessions, "session", None)
        if session is None:
            try:
                with self._session_creation_lock:
                    session = CachedSession(
                        cache_name=self._cache_name,
                        backend="sqlite",
                        expire_after=self.CACHE_EXPIRATION,
                        cache_control=True,
                    )
            except (OSError, sqlite3.Error) as error:
                raise OSMTileCacheError(
                    "Could not initialize the OpenStreetMap tile cache"
                ) from error
            self._sessions.session = session

        return session
