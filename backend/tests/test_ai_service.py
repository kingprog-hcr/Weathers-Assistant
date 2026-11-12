from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app import main
from app.schemas import ActivityEnrichmentRequest, ActivityEnrichmentResponse
from app.services import ai_service
from app.services.ai_service import (
    AIConfigurationError,
    AIProviderError,
    AIRequestTimeoutError,
    AIUnavailableError,
    GroqEnrichmentService,
)


def _completion(content: str):
    return SimpleNamespace(
        choices=[
            SimpleNamespace(
                finish_reason="stop",
                message=SimpleNamespace(content=content),
            )
        ]
    )


def _install_fake_groq(monkeypatch, response):
    class FakeGroq:
        def __init__(self, *, api_key, timeout):
            assert api_key == "test-key"
            assert timeout == 20.0
            self.chat = SimpleNamespace(
                completions=SimpleNamespace(create=lambda **kwargs: response)
            )

    monkeypatch.setattr(ai_service, "Groq", FakeGroq)


def test_enrichment_parses_structured_response_and_ignores_model_coordinates(
    monkeypatch,
):
    _install_fake_groq(
        monkeypatch,
        _completion(
            '{"activities":[{"time":"10:00","location":"Musée","address":"Centre"}]}'
        ),
    )
    service = GroqEnrichmentService(api_key="test-key")
    request = ActivityEnrichmentRequest(
        city="Angers",
        activities=[{"time": "10:00", "activity": "Visite d'un musée"}],
    )

    result = service.enrich_activities(request)

    assert len(result.activities) == 1
    assert result.activities[0].time == "10:00"
    assert result.activities[0].location == "Musée"
    assert result.activities[0].address == "Centre"
    assert result.activities[0].lat is None
    assert result.activities[0].lon is None


def test_enrichment_rejects_response_with_changed_activity_times(monkeypatch):
    _install_fake_groq(
        monkeypatch,
        _completion(
            '{"activities":[{"time":"11:00","location":null,"address":null}]}'
        ),
    )
    service = GroqEnrichmentService(api_key="test-key")
    request = ActivityEnrichmentRequest(
        city="Angers",
        activities=[{"time": "10:00", "activity": "Visite d'un musée"}],
    )

    with pytest.raises(AIProviderError):
        service.enrich_activities(request)


def test_enrichment_rejects_invalid_json(monkeypatch):
    _install_fake_groq(monkeypatch, _completion("not JSON"))
    service = GroqEnrichmentService(api_key="test-key")
    request = ActivityEnrichmentRequest(
        city="Angers",
        activities=[{"time": "10:00", "activity": "Visite d'un musée"}],
    )

    with pytest.raises(AIProviderError):
        service.enrich_activities(request)


def test_enrichment_requires_api_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    with pytest.raises(AIConfigurationError):
        GroqEnrichmentService()


def test_empty_activity_list_does_not_call_groq(monkeypatch):
    def unexpected_call(**kwargs):
        raise AssertionError("Groq should not be called for empty input")

    class FakeGroq:
        def __init__(self, *, api_key, timeout):
            self.chat = SimpleNamespace(
                completions=SimpleNamespace(
                    create=unexpected_call,
                )
            )

    monkeypatch.setattr(ai_service, "Groq", FakeGroq)
    service = GroqEnrichmentService(api_key="test-key")

    result = service.enrich_activities(
        ActivityEnrichmentRequest(city="Angers", activities=[])
    )

    assert result.activities == []


@pytest.mark.parametrize(
    ("service_error", "expected_status"),
    [
        (AIConfigurationError("missing key"), 503),
        (AIUnavailableError("rate limited"), 503),
        (AIRequestTimeoutError("timeout"), 504),
        (AIProviderError("invalid output"), 502),
    ],
)
def test_activity_route_maps_ai_errors_to_http_status(
    monkeypatch,
    service_error,
    expected_status,
):
    class FakeService:
        def enrich_activities(self, request):
            raise service_error

    monkeypatch.setattr(main, "GroqEnrichmentService", FakeService)
    response = TestClient(main.app).post(
        "/v1/activities/enrich",
        json={
            "city": "Angers",
            "activities": [{"time": "10:00", "activity": "Visite d'un musée"}],
        },
    )

    assert response.status_code == expected_status


def test_activity_route_rejects_non_hhmm_time_before_calling_service(monkeypatch):
    class UnexpectedService:
        def enrich_activities(self, request):
            raise AssertionError("Invalid input must not reach the service")

    monkeypatch.setattr(main, "GroqEnrichmentService", UnexpectedService)
    response = TestClient(main.app).post(
        "/v1/activities/enrich",
        json={
            "city": "Angers",
            "activities": [{"time": "06h00", "activity": "Course à pied"}],
        },
    )

    assert response.status_code == 422


def test_activity_route_rejects_more_than_eight_activities(monkeypatch):
    class UnexpectedService:
        def enrich_activities(self, request):
            raise AssertionError("Oversized activity lists must not reach Groq")

    monkeypatch.setattr(main, "GroqEnrichmentService", UnexpectedService)
    response = TestClient(main.app).post(
        "/v1/activities/enrich",
        json={
            "city": "Angers",
            "activities": [
                {"time": f"{hour:02}:00", "activity": "Activité"}
                for hour in range(8, 17)
            ],
        },
    )

    assert response.status_code == 422


def test_activity_route_geocodes_ai_suggestions(monkeypatch):
    enrichment = ActivityEnrichmentResponse(
        activities=[
            {
                "time": "10:00",
                "location": "Musée",
                "address": "Centre-ville",
            }
        ]
    )

    class FakeAIService:
        def enrich_activities(self, request):
            assert request.city == "Angers"
            return enrichment

    class FakeGeocodingService:
        def geocode_activities(self, result, city):
            assert result is enrichment
            assert city == "Angers"
            return ActivityEnrichmentResponse(
                activities=[
                    {
                        "time": "10:00",
                        "location": "Musée",
                        "address": "Centre-ville",
                        "lat": 47.4784,
                        "lon": -0.5632,
                    }
                ]
            )

    monkeypatch.setattr(main, "GroqEnrichmentService", FakeAIService)
    monkeypatch.setattr(main, "NominatimGeocodingService", FakeGeocodingService)
    response = TestClient(main.app).post(
        "/v1/activities/enrich",
        json={
            "city": "Angers",
            "activities": [{"time": "10:00", "activity": "Visite d'un musée"}],
        },
    )

    assert response.status_code == 200
    assert response.json()["activities"][0]["lat"] == 47.4784
    assert response.json()["activities"][0]["lon"] == -0.5632


def test_activity_route_limits_requests_per_ip(monkeypatch):
    main.limiter.reset()

    class FakeService:
        def enrich_activities(self, request):
            return ActivityEnrichmentResponse(activities=[])

    monkeypatch.setattr(main, "GroqEnrichmentService", FakeService)
    client = TestClient(main.app)
    payload = {
        "city": "Angers",
        "activities": [{"time": "06:00", "activity": "Course à pied"}],
    }

    responses = [
        client.post("/v1/activities/enrich", json=payload)
        for _ in range(6)
    ]

    assert [response.status_code for response in responses] == [
        200,
        200,
        200,
        200,
        200,
        429,
    ]
    main.limiter.reset()


def test_activity_route_rejects_oversized_body_before_validation():
    response = TestClient(main.app).post(
        "/v1/activities/enrich",
        content=b"x" * (main.MAX_ENRICHMENT_BODY_BYTES + 1),
        headers={"content-type": "application/json"},
    )

    assert response.status_code == 413
