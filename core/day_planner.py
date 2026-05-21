# core/day_planner.py
"""
Construit le programme complet d'une journée en fonction
de la météo et du profil utilisateur.
    1. Génère toujours le programme localement (fiable, hors-ligne)
    2. Si Groq est disponible, on tente d'enrichir les activités
       avec de vrais lieux dans la ville
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import random
from models import WeatherData, DayProgram, TimeSlot, ProfileData
from core.activity_engine import ActivityEngine
from core.ai_service import AIService
import requests
from itertools import cycle


class DayPlanner:
    """
    Construit le DayProgram complet en combinant météo, profil et IA.

    Attributes
    ----------
    engine : ActivityEngine
        Moteur local de suggestions d'activités, tenues et repas.
    ai : AIService
        Service IA Groq pour l'enrichissement optionnel des lieux.
    """

    def __init__(self):
        self.engine = ActivityEngine()
        self.ai     = AIService()

    def score_day(self, weather: WeatherData) -> int:
        """Note /10 basée sur la météo dominante."""
        score     = 0
        condition = weather.condition.lower()
        temp      = weather.temp
        wind      = weather.wind_speed

        if condition == "clear" and temp >= 23:
            score = 10
        elif condition == "clear" and 15 <= temp < 23:
            score = 8
        elif condition == "clouds":
            score = 6
        elif condition in ["drizzle", "mist", "fog"]:
            score = 5
        elif condition == "rain":
            score = 4
        elif condition == "thunderstorm":
            score = 2
        elif condition == "snow":
            score = 7
        else:
            score = 5

        if temp < 0:
            score -= 1
        if wind > 50:
            score -= 1

        return max(0, score)

    def _get_dominant_weather(
        self, weather_slots: dict[str, WeatherData]
    ) -> WeatherData:
        """Retourne la météo la plus représentative de la journée (midi)."""
        return (
            weather_slots.get("12:00")
            or weather_slots.get("11:00")
            or weather_slots.get("13:00")
            or next(iter(weather_slots.values()))
        )

    def get_quote(self, weather: WeatherData) -> str:
        """Citation inspirante — API ZenQuotes avec fallback local."""
        try:
            response = requests.get("https://zenquotes.io/api/random", timeout=3)
            response.raise_for_status()
            data = response.json()[0]
            return f"{data['q']}\n\n— {data['a']}"

        except Exception:
            QUOTES = {
                "clear":       ["Le soleil brille pour tout le monde.",
                                "Chaque matin est une nouvelle chance d'être heureux.",
                                f"Profite de cette belle journée à {weather.city} !"],
                "clouds":      ["Les nuages sont les rêves du ciel.",
                                "Même sous les nuages, le soleil existe toujours."],
                "rain":        ["Après la pluie, le beau temps.",
                                "La pluie est la chanson de la terre.",
                                "Il n'y a pas de mauvais temps, que de mauvaises tenues."],
                "drizzle":     ["La bruine est un câlin du ciel.",
                                "Les petites pluies abattent les grands vents."],
                "thunderstorm":["L'orage purifie l'air et l'âme.",
                                "Après la tempête vient le calme."],
                "snow":        ["La neige est le silence du ciel.",
                                "Sous la neige, la terre se repose et rêve."],
                "mist":        ["Le brouillard cache les détails pour révéler l'essentiel.",
                                "Dans la brume, tout devient mystère."],
                "fog":         ["Le brouillard efface les frontières du monde.",
                                "Dans le brouillard, chaque pas est une découverte."],
            }
            condition = weather.condition.lower()
            quotes    = QUOTES.get(condition, ["Chaque journée est unique."])
            return random.choice(quotes)

    def _build_local(
        self,
        weather_slots: dict[str, WeatherData],
        profile: ProfileData
    ) -> DayProgram:
        """
        Construit le programme complet avec les données locales uniquement.

        Génère 4 repas fixes + 4 activités aux heures creuses.
        Toutes les suggestions viennent des catalogues JSON locaux.

        Parameters
        ----------
        weather_slots : dict[str, WeatherData]
            Météo par créneau horaire.
        profile : ProfileData
            Profil utilisateur pour personnaliser les suggestions.
        """
        dominant = self._get_dominant_weather(weather_slots)
        score    = self.score_day(dominant)
        quote    = self.get_quote(dominant)
        outfit   = self.engine.suggest_outfit(dominant, style=profile.style)

        # Construit un pool unique de suggestions food
        food_pool = self.engine.suggest_food(dominant, cuisine=profile.cuisine)
    
    # Retire la dernière ligne "Cuisine : ..." avant de piocher
        food_items = food_pool[:-1]
    
    # Mélange le pool
        random.shuffle(food_items)

        food_cycle = cycle(food_items)
        
        slots = [
        TimeSlot(time="08:00", activity=f"Petit déjeuner : {next(food_cycle)}"),
        TimeSlot(time="12:00", activity=f"Déjeuner : {next(food_cycle)}"),
        TimeSlot(time="16:00", activity=f"Goûter : {next(food_cycle)}"),
        TimeSlot(time="19:00", activity=f"Dîner : {next(food_cycle)}"),
    ]

        # 4 créneaux d'activités aux heures creuses entre les repas
        ACTIVITY_TIMES = ["10:00", "14:00", "17:00", "21:00"]

        for time in ACTIVITY_TIMES:
            weather    = weather_slots.get(time) or dominant
            activities = self.engine.suggest_activities(
                weather=weather,
                tastes=profile.tastes,
                max_results=6  # pool plus large pour plus de variété
            )
            if activities:
                # random.choice sur le pool pour varier à chaque génération
                slots.append(TimeSlot(time=time, activity=random.choice(activities)))

        slots.sort(key=lambda s: s.time)

        return DayProgram(
            slots=slots,
            outfit=outfit,
            food=food_items,
            score=score,
            quote=quote,
        )

    def _enrich_with_ai(
        self,
        program: DayProgram,
        city: str,
        lang: str = "fr"
    ) -> DayProgram:
        """
        Enrichit optionnellement les activités avec de vrais lieux via Groq.

        Envoie les activités déjà générées à l'IA et lui demande uniquement
        d'ajouter un lieu réel s'il en connaît un sans rien inventer.
        Si Groq échoue ou retourne du JSON invalide, retourne le programme
        intact sans modification.

        Les repas sont exclus de l'enrichissement

        Parameters
        ----------
        program : DayProgram
            Programme généré localement par _build_local().
        city : str
            Ville de l'utilisateur pour guider la recherche de lieux.
        lang : str
            Langue pour les réponses de l'IA.
        """
        # Sépare les repas des activités pour n'envoyer que les activités à l'IA
        MEAL_KEYWORDS = ["petit déjeuner", "déjeuner", "goûter", "dîner"]

        activity_slots = [
            s for s in program.slots
            if not any(meal in s.activity.lower() for meal in MEAL_KEYWORDS)
        ]

        if not activity_slots:
            return program

        # Formate les activités pour l'IA
        activities_for_ai = [
            {"time": s.time, "activity": s.activity}
            for s in activity_slots
        ]

        # Appelle l'IA pour enrichir les lieux
        enrichments = self.ai.enrich_activities(activities_for_ai, city=city, lang=lang)

        if not enrichments:
            # Groq indisponible ou JSON invalide, programme local intact
            return program

        # Construit un dictionnaire {time: enrichissement} pour accès rapide
        enrich_map = {e["time"]: e for e in enrichments if isinstance(e, dict)}

        for slot in program.slots:
            if slot.time in enrich_map:
                e        = enrich_map[slot.time]
                location = e.get("location")
                address  = e.get("address")

                # N'applique l'enrichissement que si l'IA a trouvé quelque chose
                # et que ce n'est pas null — on ne force jamais un lieu fictif
                if location and location.lower() not in ("null", "none", ""):
                    slot.location = f"{location}, {address}" if address else location
                    slot.lat      = e.get("lat")
                    slot.lon      = e.get("lon")

        return program

    def build_program(
        self,
        weather_slots: dict[str, WeatherData],
        profile: ProfileData
    ) -> DayProgram:
        """
        Construit le programme complet de la journée.

        Stratégie en deux étapes :
        1. Génère toujours en local d'abord
        2. Si Groq est disponible, enrichit les activités avec de vrais lieux
           La deuxième étape est optionnelle, l'app fonctionne sans elle

        Parameters
        ----------
        weather_slots : dict[str, WeatherData]
            Météo par créneau horaire retournée par WeatherService.
        profile : ProfileData
            Profil utilisateur complet.
        """
        dominant = self._get_dominant_weather(weather_slots)

        # génération locale 
        program = self._build_local(weather_slots, profile)

        # enrichissement IA optionnel
        # Si Groq échoue, _enrich_with_ai retourne le same programme
        if self.ai.is_available():
            program = self._enrich_with_ai(
                program,
                city=dominant.city,
                lang=profile.language
            )

        return program