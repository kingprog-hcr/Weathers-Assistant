from core.weather_service import WeatherService
from models import WeatherData


class FakeResponse:
    def __init__(self, data, status_code=200):
        self._data = data
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            import requests

            error = requests.HTTPError(response=self)
            raise error

    def json(self):
        return self._data


def test_get_current_requests_backend_and_maps_response(monkeypatch):
    service = WeatherService()
    monkeypatch.setattr(service, "_load_cache", lambda city: None)
    saved = []
    monkeypatch.setattr(
        service,
        "_save_cache",
        lambda city, weather: saved.append((city, weather)),
    )

    def fake_get(url, *, params, timeout):
        assert url.endswith("/v1/weather/current")
        assert params == {"city": "Angers"}
        assert timeout == service.REQUEST_TIMEOUT
        return FakeResponse(
            {
                "city": "Angers",
                "temp": 18.5,
                "feels_like": 18.0,
                "condition": "Clouds",
                "description": "partiellement nuageux",
                "icon": "02d",
                "humidity": 60,
                "wind_speed": 3.2,
                "lat": 47.47,
                "lon": -0.55,
            }
        )

    monkeypatch.setattr("core.weather_service.requests.get", fake_get)

    result = service.get_current("Angers")

    assert result == WeatherData(
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
    assert saved == [("Angers", result)]
    assert service.get_city() == "Angers"


def test_get_day_slots_adds_city_from_response_envelope(monkeypatch):
    service = WeatherService()

    def fake_get(url, *, params, timeout):
        assert url.endswith("/v1/weather/forecast/today")
        assert params == {"city": "Angers"}
        return FakeResponse(
            {
                "city": "Angers",
                "slots": {
                    "12:00": {
                        "temp": 20.0,
                        "feels_like": 19.0,
                        "condition": "Clear",
                        "description": "ciel dégagé",
                        "icon": "01d",
                        "humidity": 50,
                        "wind_speed": 2.0,
                    }
                },
            }
        )

    monkeypatch.setattr("core.weather_service.requests.get", fake_get)

    slots = service.get_day_slots("Angers")

    assert slots["12:00"] == WeatherData(
        city="Angers",
        temp=20.0,
        feels_like=19.0,
        condition="Clear",
        description="ciel dégagé",
        icon="01d",
        humidity=50,
        wind_speed=2.0,
    )


def test_get_city_auto_uses_https_geolocation_without_weather_validation(
    monkeypatch,
):
    service = WeatherService()

    def fake_get(url, *, timeout):
        assert url == service.GEOLOCATION_URL
        assert url.startswith("https://")
        return FakeResponse({"city": "Angers"})

    monkeypatch.setattr("core.weather_service.requests.get", fake_get)

    assert service.get_city_auto() == "Angers"
    assert service.get_city() == "Angers"
