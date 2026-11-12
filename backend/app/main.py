from fastapi import FastAPI, HTTPException, Query, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.schemas import (
    ActivityEnrichmentRequest,
    ActivityEnrichmentResponse,
    CurrentWeatherResponse,
    DaySlotsResponse,
)
from app.middleware import EnrichmentBodySizeLimitMiddleware
from app.services.weather_service import (
    CityNotFoundError,
    OpenWeatherMapService,
    WeatherConfigurationError,
    WeatherProviderError,
    WeatherServiceError,
)
from app.services.ai_service import(
    AIConfigurationError,
    AIProviderError,
    AIRequestTimeoutError,
    AIServiceError,
    AIUnavailableError,
    GroqEnrichmentService
)
from app.services.geocoding_service import NominatimGeocodingService

limiter = Limiter(key_func=get_remote_address)
MAX_ENRICHMENT_BODY_BYTES = 4096

app = FastAPI(
    title="WeatherProgramm API",
    version="1.0.1",
    description="API de programme météo",
)
app.add_middleware(
    EnrichmentBodySizeLimitMiddleware,
    max_body_bytes=MAX_ENRICHMENT_BODY_BYTES,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


def _weather_error_response(error: WeatherServiceError) -> HTTPException:
    """Convertit les erreurs du fournisseur en statuts HTTP sans details internes."""
    if isinstance(error, CityNotFoundError):
        return HTTPException(status_code=404, detail="Ville inconnue")
    if isinstance(error, WeatherConfigurationError):
        return HTTPException(
            status_code=503,
            detail="Le service météo n'est pas configuré",
        )
    if isinstance(error, WeatherProviderError):
        return HTTPException(
            status_code=502,
            detail="Le fournisseur météo est temporairement indisponible",
        )
    return HTTPException(status_code=502, detail="Erreur du service météo")

def _ai_error_response(error : AIServiceError) -> HTTPException:
    """Convertit les erreurs Groq en reponses HTTP sans details internes."""
    if isinstance(error, AIConfigurationError):
        return HTTPException(
            status_code=503,
            detail="Le service d'enrichissement n'est pas configure",
        )
    if isinstance(error, AIRequestTimeoutError):
        return HTTPException(
            status_code=504,
            detail="Le service d'enrichissement met trop de temps a repondre",
        )
    if isinstance(error, AIUnavailableError):
        return HTTPException(
            status_code=503,
            detail="Le service d'enrichissement est temporairement indisponible",
        )
    if isinstance(error, AIProviderError):
        return HTTPException(
            status_code=502,
            detail="Le fournisseur d'IA a retourne une reponse invalide",
        )
    return HTTPException(
        status_code=502,
        detail="Erreur du service d'enrichissement",
    )


@app.get("/")
def health_check():
    return {"status": "ok", "message": "Serveur opérationnel"}


@app.get(
    "/v1/weather/current",
    response_model=CurrentWeatherResponse,
    tags=["weather"],
)
@limiter.limit("30/minute")
def get_current_weather(
    request: Request,
    city: str = Query(min_length=1, max_length=100),
):
    try:
        return OpenWeatherMapService().get_current_weather(city)
    except WeatherServiceError as error:
        raise _weather_error_response(error) from error


@app.get(
    "/v1/weather/forecast/today",
    response_model=DaySlotsResponse,
    tags=["weather"],
)
@limiter.limit("30/minute")
def get_today_weather_slots(
    request: Request,
    city: str = Query(min_length=1, max_length=100),
):
    try:
        return OpenWeatherMapService().get_today_weather_slots(city)
    except WeatherServiceError as error:
        raise _weather_error_response(error) from error


@app.post(
    "/v1/activities/enrich",
    response_model=ActivityEnrichmentResponse,
    tags=["activities"],
)
@limiter.limit("5/minute")
def enrich_activities(
    request: Request,
    enrichment_request: ActivityEnrichmentRequest,
):
    try:
        enrichment = GroqEnrichmentService().enrich_activities(enrichment_request)
        return NominatimGeocodingService().geocode_activities(
            enrichment,
            city=enrichment_request.city,
        )
    except AIServiceError as error:
        raise _ai_error_response(error) from error