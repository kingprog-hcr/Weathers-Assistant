from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

from core.osm_tile_service import OSMTileService


@contextmanager
def local_tile_server(cache_control):
    requests_seen = []

    class TileHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            requests_seen.append(
                {
                    "path": self.path,
                    "user_agent": self.headers.get("User-Agent"),
                    "if_none_match": self.headers.get("If-None-Match"),
                }
            )

            if self.headers.get("If-None-Match") == '"tile-v1"':
                self.send_response(304)
                self.send_header("Cache-Control", "max-age=60")
                self.send_header("ETag", '"tile-v1"')
                self.end_headers()
                return

            body = b"tile image bytes"
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", cache_control)
            self.send_header("ETag", '"tile-v1"')
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, _format, *_args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), TileHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        yield f"http://127.0.0.1:{server.server_port}", requests_seen
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


def test_tile_requests_identify_app_and_reuse_fresh_cached_response(
    monkeypatch, tmp_path
):
    with local_tile_server("max-age=3600") as (server_url, requests_seen):
        monkeypatch.setattr(
            OSMTileService,
            "TILE_URL_TEMPLATE",
            f"{server_url}/{{z}}/{{x}}/{{y}}.png",
        )
        service = OSMTileService(cache_name=tmp_path / "tiles")

        first_tile = service.get_tile(2, 5, 2)
        restarted_service = OSMTileService(cache_name=tmp_path / "tiles")
        second_tile = restarted_service.get_tile(2, 5, 2)

    assert first_tile == second_tile == b"tile image bytes"
    assert len(requests_seen) == 1
    assert requests_seen[0]["path"] == "/2/1/2.png"
    assert requests_seen[0]["user_agent"] == OSMTileService.USER_AGENT


def test_expired_tile_is_revalidated_with_etag(monkeypatch, tmp_path):
    with local_tile_server("max-age=0") as (server_url, requests_seen):
        monkeypatch.setattr(
            OSMTileService,
            "TILE_URL_TEMPLATE",
            f"{server_url}/{{z}}/{{x}}/{{y}}.png",
        )
        service = OSMTileService(cache_name=tmp_path / "tiles")

        first_tile = service.get_tile(3, 1, 4)
        restarted_service = OSMTileService(cache_name=tmp_path / "tiles")
        second_tile = restarted_service.get_tile(3, 1, 4)

    assert first_tile == second_tile == b"tile image bytes"
    assert len(requests_seen) == 2
    assert requests_seen[1]["if_none_match"] == '"tile-v1"'


def test_out_of_bounds_tiles_are_not_requested(monkeypatch, tmp_path):
    with local_tile_server("max-age=3600") as (server_url, requests_seen):
        monkeypatch.setattr(
            OSMTileService,
            "TILE_URL_TEMPLATE",
            f"{server_url}/{{z}}/{{x}}/{{y}}.png",
        )
        service = OSMTileService(cache_name=tmp_path / "tiles")

        result = service.get_tile(2, 0, 4)

    assert result is None
    assert requests_seen == []


def test_concurrent_tile_requests_share_the_persistent_cache_safely(
    monkeypatch, tmp_path
):
    with local_tile_server("max-age=3600") as (server_url, requests_seen):
        monkeypatch.setattr(
            OSMTileService,
            "TILE_URL_TEMPLATE",
            f"{server_url}/{{z}}/{{x}}/{{y}}.png",
        )
        service = OSMTileService(cache_name=tmp_path / "tiles")

        with ThreadPoolExecutor(max_workers=6) as executor:
            tiles = list(
                executor.map(
                    lambda x: service.get_tile(3, x, 2),
                    range(6),
                )
            )

    assert tiles == [b"tile image bytes"] * 6
    assert len(requests_seen) == 6
