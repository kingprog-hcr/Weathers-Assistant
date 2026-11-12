from core.ai_service import AIService


class FakeResponse:
    def __init__(self, data, status_code=200):
        self._data = data
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            import requests

            raise requests.HTTPError(response=self)

    def json(self):
        return self._data


def test_enrich_activities_posts_to_backend_and_returns_list(monkeypatch):
    service = AIService()
    expected_result = [
        {
            "time": "10:00",
            "location": "Musée",
            "address": "Centre",
            "lat": 47.4784,
            "lon": -0.5632,
        }
    ]

    def fake_post(url, *, json, timeout):
        assert url.endswith("/v1/activities/enrich")
        assert json == {
            "city": "Angers",
            "activities": [
                {"time": "10:00", "activity": "Visite d'un musée"}
            ],
        }
        assert timeout == service.REQUEST_TIMEOUT
        return FakeResponse({"activities": expected_result})

    monkeypatch.setattr("core.ai_service.requests.post", fake_post)

    result = service.enrich_activities(
        [{"time": "10:00", "activity": "Visite d'un musée"}],
        city="Angers",
    )

    assert result == expected_result


def test_enrichment_returns_none_for_http_error(monkeypatch):
    service = AIService()
    monkeypatch.setattr(
        "core.ai_service.requests.post",
        lambda *args, **kwargs: FakeResponse({}, status_code=503),
    )

    result = service.enrich_activities(
        [{"time": "10:00", "activity": "Visite d'un musée"}],
        city="Angers",
    )

    assert result is None


def test_enrichment_returns_none_when_backend_changes_activity_time(monkeypatch):
    service = AIService()
    monkeypatch.setattr(
        "core.ai_service.requests.post",
        lambda *args, **kwargs: FakeResponse(
            {
                "activities": [
                    {
                        "time": "11:00",
                        "location": None,
                        "address": None,
                        "lat": None,
                        "lon": None,
                    }
                ]
            }
        ),
    )

    result = service.enrich_activities(
        [{"time": "10:00", "activity": "Visite d'un musée"}],
        city="Angers",
    )

    assert result is None


def test_empty_activity_list_skips_backend_request(monkeypatch):
    service = AIService()

    def unexpected_post(*args, **kwargs):
        raise AssertionError("Aucune activité ne doit appeler le backend")

    monkeypatch.setattr("core.ai_service.requests.post", unexpected_post)

    assert service.enrich_activities([], city="Angers") == []
