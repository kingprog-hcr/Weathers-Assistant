import httpx
import pytest

from app.schemas import ActivityEnrichmentResponse, EnrichedActivityResponse
from app.services import geocoding_service
from app.services.geocoding_service import NominatimGeocodingService


def _nominatim_result(city="Angers", latitude="47.4784", longitude="-0.5632"):
    return {
        "lat": latitude,
        "lon": longitude,
        "address": {"city": city},
    }


def _http_response(results):
    return httpx.Response(
        200,
        json=results,
        request=httpx.Request(
            "GET",
            "https://nominatim.openstreetmap.org/search",
        ),
    )


def _enrichment():
    return ActivityEnrichmentResponse(
        activities=[
            {
                "time": "10:00",
                "location": "Musée",
                "address": "Centre-ville",
            },
            {
                "time": "12:00",
                "location": None,
                "address": None,
            },
        ]
    )


def test_geocodes_only_results_in_requested_city_and_persists_cache(
    monkeypatch,
    tmp_path,
):
    calls = []

    def fake_get(url, *, params, headers, timeout):
        calls.append((url, params, headers, timeout))
        return _http_response([_nominatim_result()])

    monkeypatch.setattr(geocoding_service.httpx, "get", fake_get)
    cache_path = tmp_path / "nominatim.sqlite3"
    service = NominatimGeocodingService(cache_path=cache_path)

    result = service.geocode_activities(_enrichment(), city="Angers")
    repeated_result = NominatimGeocodingService(
        cache_path=cache_path
    ).geocode_activities(_enrichment(), city="Angers")

    assert result.activities[0].lat == 47.4784
    assert result.activities[0].lon == -0.5632
    assert result.activities[1].lat is None
    assert repeated_result.activities[0].lat == 47.4784
    assert len(calls) == 1
    assert calls[0][0] == "https://nominatim.openstreetmap.org/search"
    assert calls[0][1]["limit"] == 5
    assert calls[0][1]["q"] == "Musée, Angers"
    assert "WeatherProgramm" in calls[0][2]["User-Agent"]


def test_geocoder_uses_address_when_place_name_has_no_match(
    monkeypatch,
    tmp_path,
):
    queries = []

    def fake_get(url, *, params, headers, timeout):
        queries.append(params["q"])
        results = [] if "Musée" in params["q"] else [_nominatim_result()]
        return _http_response(results)

    monkeypatch.setattr(geocoding_service.httpx, "get", fake_get)

    result = NominatimGeocodingService(
        cache_path=tmp_path / "nominatim.sqlite3"
    ).geocode_activities(_enrichment(), city="Angers")

    assert queries == ["Musée, Angers", "Centre-ville, Angers"]
    assert result.activities[0].lat == 47.4784


def test_geocoder_rejects_results_outside_the_requested_city(
    monkeypatch,
    tmp_path,
):
    monkeypatch.setattr(
        geocoding_service.httpx,
        "get",
        lambda *args, **kwargs: _http_response(
            [_nominatim_result(city="Paris")]
        ),
    )

    result = NominatimGeocodingService(
        cache_path=tmp_path / "nominatim.sqlite3"
    ).geocode_activities(_enrichment(), city="Angers")

    assert result.activities[0].lat is None
    assert result.activities[0].lon is None


def test_geocoder_enforces_one_second_between_uncached_requests(
    monkeypatch,
    tmp_path,
):
    sleeps = []
    monkeypatch.setattr(geocoding_service.time, "time", lambda: 100.0)
    monkeypatch.setattr(geocoding_service.time, "sleep", sleeps.append)
    monkeypatch.setattr(
        geocoding_service.httpx,
        "get",
        lambda *args, **kwargs: _http_response([_nominatim_result()]),
    )
    enrichment = ActivityEnrichmentResponse(
        activities=[
            {
                "time": "10:00",
                "location": "Musée",
                "address": "Centre-ville",
            },
            {
                "time": "11:00",
                "location": "Parc",
                "address": "Centre-ville",
            },
        ]
    )

    NominatimGeocodingService(
        cache_path=tmp_path / "nominatim.sqlite3"
    ).geocode_activities(enrichment, city="Angers")

    assert sleeps == [pytest.approx(1.0)]


def test_geocoding_failure_keeps_enrichment_without_coordinates(
    monkeypatch,
    tmp_path,
):
    def fail_request(*args, **kwargs):
        raise httpx.ConnectError("offline")

    monkeypatch.setattr(geocoding_service.httpx, "get", fail_request)

    result = NominatimGeocodingService(
        cache_path=tmp_path / "nominatim.sqlite3"
    ).geocode_activities(_enrichment(), city="Angers")

    assert result.activities[0].location == "Musée"
    assert result.activities[0].lat is None
    assert result.activities[0].lon is None


def test_activity_coordinates_must_be_a_valid_pair():
    with pytest.raises(ValueError):
        EnrichedActivityResponse(
            time="10:00",
            location="Musée",
            lat=47.4784,
            lon=None,
        )

    with pytest.raises(ValueError):
        EnrichedActivityResponse(
            time="10:00",
            location="Musée",
            lat=91,
            lon=0,
        )
