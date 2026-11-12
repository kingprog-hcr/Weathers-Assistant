import json
import os
from pathlib import Path

from dotenv import load_dotenv
from groq import (
    APIConnectionError,
    APIError,
    APIStatusError,
    APITimeoutError,
    Groq,
    RateLimitError,
)
from pydantic import ValidationError

from app.schemas import ActivityEnrichmentRequest, ActivityEnrichmentResponse


# En local, charge le .env du backend. L'hebergeur fournit la meme variable
# directement dans sa configuration de secrets.
BACKEND_ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(BACKEND_ENV_PATH)


class AIServiceError(Exception):
    """Erreur IA que la route peut convertir en reponse HTTP."""


class AIConfigurationError(AIServiceError):
    """La cle Groq est absente ou rejetee."""


class AIUnavailableError(AIServiceError):
    """Groq est temporairement inaccessible ou limite les requetes."""


class AIRequestTimeoutError(AIServiceError):
    """La requete Groq a depasse le delai d'attente."""


class AIProviderError(AIServiceError):
    """Groq a renvoye une reponse invalide ou une erreur inattendue."""


class GroqEnrichmentService:
    """Enrichit les activites locales avec des suggestions de lieux Groq."""

    MODEL = "openai/gpt-oss-120b"

    def __init__(self, api_key: str | None = None):
        configured_api_key = api_key or os.getenv("GROQ_API_KEY")
        if not configured_api_key:
            raise AIConfigurationError("La variable GROQ_API_KEY est absente")

        self.client = Groq(api_key=configured_api_key, timeout=20.0)

    def enrich_activities(
        self,
        request: ActivityEnrichmentRequest,
    ) -> ActivityEnrichmentResponse:
        """Demande des lieux, puis valide la reponse avant de la retourner."""
        if not request.activities:
            return ActivityEnrichmentResponse(activities=[])

        activities_text = "\n".join(
            f"- {activity.time} : {activity.activity}"
            for activity in request.activities
        )
        prompt = f"""Tu aides a trouver des lieux correspondant a des activites.

Ville : {request.city}
Langue : francais

Pour chaque activite, suggere uniquement un lieu reel dont tu es raisonnablement
certain et qui se trouve dans cette ville. Si tu ne peux pas en proposer un
avec confiance, retourne null pour location et address.
Ne cree, ne supprime et ne reordonne aucune activite. Recopie exactement chaque
heure. Ne retourne pas de coordonnees : elles seront obtenues par geocodage.

Activites :
{activities_text}
"""

        try:
            response = self.client.chat.completions.create(
                model=self.MODEL,
                messages=[{"role": "user", "content": prompt}],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "activity_enrichment",
                        "strict": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "activities": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "time": {"type": "string"},
                                            "location": {
                                                "type": ["string", "null"]
                                            },
                                            "address": {
                                                "type": ["string", "null"]
                                            },
                                        },
                                        "required": [
                                            "time",
                                            "location",
                                            "address",
                                        ],
                                        "additionalProperties": False,
                                    },
                                }
                            },
                            "required": ["activities"],
                            "additionalProperties": False,
                        },
                    },
                },
                temperature=0.2,
                max_tokens=1000,
            )
        except APITimeoutError as error:
            raise AIRequestTimeoutError("La requete Groq a expire") from error
        except (APIConnectionError, RateLimitError) as error:
            raise AIUnavailableError("Groq est temporairement indisponible") from error
        except APIStatusError as error:
            if error.status_code in (401, 403):
                raise AIConfigurationError(
                    "Groq a refuse la cle API configuree"
                ) from error
            raise AIProviderError(
                f"Groq a retourne le statut HTTP {error.status_code}"
            ) from error
        except APIError as error:
            raise AIProviderError("La requete Groq a echoue") from error

        if not response.choices:
            raise AIProviderError("Groq n'a retourne aucun choix")

        choice = response.choices[0]
        if choice.finish_reason == "length":
            raise AIProviderError("La reponse Groq a ete tronquee")

        content = choice.message.content
        if not content:
            raise AIProviderError("Groq a retourne une reponse vide")

        try:
            result = json.loads(content)
        except json.JSONDecodeError as error:
            raise AIProviderError("Groq a retourne un JSON invalide") from error

        try:
            enrichment = ActivityEnrichmentResponse.model_validate(result)
        except ValidationError as error:
            raise AIProviderError(
                "La reponse Groq ne respecte pas le schema attendu"
            ) from error

        expected_times = [activity.time for activity in request.activities]
        returned_times = [activity.time for activity in enrichment.activities]
        if returned_times != expected_times:
            raise AIProviderError(
                "La reponse Groq ne correspond pas aux activites demandees"
            )

        # Groq n'est pas une source fiable de coordonnees. Elles restent nulles
        # jusqu'a ce qu'un service de geocodage independant les confirme.
        return enrichment