from datetime import datetime, time, timedelta, timezone

import httpx
import pytest
from fastapi.testclient import TestClient

from app import main
from app.schemas import CurrentWeatherResponse
from app.services.weather_service import (
    CityNotFoundError,
    OpenWeatherMapService,
    WeatherProviderError,
)


def test_get_current_weather_maps_provider_payload(monkeypatch):
    def fake_get(url, *, params, timeout):
        assert url.endswith("/weather")
        assert params["q"] == "Angers"
        assert params["appid"] == "test-key"
        assert params["units"] == "metric"
        assert timeout == OpenWeatherMapService.TIMEOUT_SECONDS
        return httpx.Response(
            200,
            json={
                "name": "Angers",
                "main": {
                    "temp": 18.5,
                    "feels_like": 18.0,
                    "humidity": 60,
                },
                "weather": [
                    {
                        "main": "Clouds",
                        "description": "partiellement nuageux",
                        "icon": "02d",
                    }
                ],
                "wind": {"speed": 3.2},
                "coord": {"lat": 47.47, "lon": -0.55},
            },
            request=httpx.Request("GET", url),
        )

    monkeypatch.setattr("app.services.weather_service.httpx.get", fake_get)
    service = OpenWeatherMapService(api_key="test-key")

    result = service.get_current_weather("Angers")

    assert result == CurrentWeatherResponse(
        city="Angers",
        temp=18.5,
        feels_like=18.0,
        condition="Clouds",
        description="partiellement nuageux",
        icon="02d",
        humidity=60,
        wind_speed=3.2,
        lat=47.47,
        lon=-0.55,
    )


def test_get_today_weather_slots_uses_city_local_date(monkeypatch):
    city_timezone = timezone(timedelta(hours=2))
    today = datetime.now(city_timezone).date()
    today_noon = datetime.combine(today, time(12), tzinfo=city_timezone)
    yesterday_noon = today_noon - timedelta(days=1)

    def forecast_entry(timestamp, temperature):
        return {
            "dt": timestamp.astimezone(timezone.utc).timestamp(),
            "main": {
                "temp": temperature,
                "feels_like": temperature,
                "humidity": 55,
            },
            "weather": [
                {
                    "main": "Clear",
                    "description": "ciel dégagé",
                    "icon": "01d",
                }
            ],
            "wind": {"speed": 2.0},
        }

    def fake_get(url, *, params, timeout):
        assert url.endswith("/forecast")
        return httpx.Response(
            200,
            json={
                "city": {"name": "Angers", "timezone": 7200},
                "list": [
                    forecast_entry(yesterday_noon, 10.0),
                    forecast_entry(today_noon, 20.0),
                ],
            },
            request=httpx.Request("GET", url),
        )

    monkeypatch.setattr("app.services.weather_service.httpx.get", fake_get)
    result = OpenWeatherMapService(api_key="test-key").get_today_weather_slots(
        "Angers"
    )

    assert result.city == "Angers"
    assert list(result.slots) == ["12:00"]
    assert result.slots["12:00"].temp == 20.0


def test_unknown_city_raises_city_not_found(monkeypatch):
    def fake_get(url, *, params, timeout):
        return httpx.Response(404, json={"message": "city not found"})

    monkeypatch.setattr("app.services.weather_service.httpx.get", fake_get)
    service = OpenWeatherMapService(api_key="test-key")

    with pytest.raises(CityNotFoundError):
        service.get_current_weather("Ville inconnue")


def test_weather_route_maps_unknown_city_to_404(monkeypatch):
    class FakeWeatherService:
        def get_current_weather(self, city):
            raise CityNotFoundError(city)

    monkeypatch.setattr(main, "OpenWeatherMapService", FakeWeatherService)
    response = TestClient(main.app).get(
        "/v1/weather/current",
        params={"city": "Ville inconnue"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Ville inconnue"


def test_provider_failure_is_reported_as_weather_provider_error(monkeypatch):
    def fake_get(url, *, params, timeout):
        raise httpx.TimeoutException("test timeout")

    monkeypatch.setattr("app.services.weather_service.httpx.get", fake_get)
    service = OpenWeatherMapService(api_key="test-key")

    with pytest.raises(WeatherProviderError):
        service.get_current_weather("Angers")
