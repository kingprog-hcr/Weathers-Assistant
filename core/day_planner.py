"""
Construit le programme complet d'une journée en fonction
de la météo et du profil utilisateur.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import random
from models import WeatherData, DayProgram, TimeSlot, ProfileData
from core.activity_engine import ActivityEngine
import requests



class DayPlanner:

    def __init__(self):
        self.engine = ActivityEngine()

    def score_day(self, weather: WeatherData) -> int:
        """Note /10 basée sur la météo dominante."""
        score = 0
        condition = weather.condition.lower()
        temp = weather.temp
        wind = weather.wind_speed
        
        # Score principal selon météo

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
            score = 5  # valeur par défaut

        # Ajustements

        if temp < 0:
            score -= 1

        if wind > 50:
            score -= 1

        return score
    

    def _get_dominant_weather(
        self, weather_slots: dict[str, WeatherData]
    ) -> WeatherData:
        """Retourne la météo la plus représentative de la journée."""
        return (
            weather_slots.get("12:00")
            or weather_slots.get("11:00")
            or weather_slots.get("13:00")
            or next(iter(weather_slots.values()))
        )

    

    def get_quote(self, weather: WeatherData) -> str:
        """Citation inspirante — API externe avec fallback local."""
        try:
            response = requests.get("https://zenquotes.io/api/random", timeout=3)
            response.raise_for_status()
            data = response.json()[0]
            return f"{data['q']}\n— {data['a']}"

        except Exception:
            QUOTES = {
                "clear": [
                    "Le soleil brille pour tout le monde.",
                    "Chaque matin est une nouvelle chance d'être heureux.",
                    f"Profite de cette belle journée à {weather.city} !",
                ],
                "clouds": [
                    "Les nuages sont les rêves du ciel.",
                    "Même sous les nuages, le soleil existe toujours.",
                ],
                "rain": [
                    "Après la pluie, le beau temps.",
                    "La pluie est la chanson de la terre.",
                    "Il n'y a pas de mauvais temps, que de mauvaises tenues.",
                ],
                "drizzle": [
                    "La bruine est un câlin du ciel.",
                    "Les petites pluies abattent les grands vents.",
                ],
                "thunderstorm": [
                    "L'orage purifie l'air et l'âme.",
                    "Après la tempête vient le calme.",
                ],
                "snow": [
                    "La neige est le silence du ciel.",
                    "Sous la neige, la terre se repose et rêve.",
                ],
                "mist": [
                    "Le brouillard cache les détails pour révéler l'essentiel.",
                    "Dans la brume, tout devient mystère.",
                ],
                "fog": [
                    "Le brouillard efface les frontières du monde.",
                    "Dans le brouillard, chaque pas est une découverte.",
                ],
            }
            condition = weather.condition.lower()
            quotes = QUOTES.get(condition, ["Chaque journée est unique."])
            return random.choice(quotes)


    def build_program(
        self,
        weather_slots: dict[str, WeatherData],
        profile: ProfileData
    ) -> DayProgram:
        """Construit le programme en adaptant chaque créneau à sa météo."""

        dominant = self._get_dominant_weather(weather_slots)
        score  = self.score_day(dominant)
        quote  = self.get_quote(dominant) 
        outfit = self.engine.suggest_outfit(dominant, style=profile.style)

        weather_matin = weather_slots.get("08:00") or weather_slots.get("09:00") or dominant
        weather_midi  = weather_slots.get("12:00") or weather_slots.get("11:00") or dominant
        weather_soir  = weather_slots.get("19:00") or weather_slots.get("20:00") or dominant

        food_matin = self.engine.suggest_food(weather_matin, cuisine=profile.cuisine)
        food_midi  = self.engine.suggest_food(weather_midi,  cuisine=profile.cuisine)
        food_soir  = self.engine.suggest_food(weather_soir,  cuisine=profile.cuisine)

        slots = [
            TimeSlot(time="08:00", activity=f"Petit déjeuner — {food_matin[0]}"),
            TimeSlot(time="12:00", activity=f"Déjeuner — {food_midi[0]}"),
            TimeSlot(time="19:00", activity=f"Dîner — {food_soir[0]}"),
        ]

        # 4 créneaux d'activités — rythme naturel 
        ACTIVITY_TIMES = ["10:00", "14:00", "17:00", "21:00"]

        for time in ACTIVITY_TIMES:
            weather = weather_slots.get(time) or dominant
            activities = self.engine.suggest_activities(
                weather=weather,
                tastes=profile.tastes,
                max_results=3
            )
            if activities:
                slots.append(TimeSlot(time=time, activity=random.choice(activities)))

        slots.sort(key=lambda s: s.time)

        return DayProgram(
            slots=slots,
            outfit=outfit,
            food=food_matin + food_midi + food_soir,
            score=score,
            quote=quote,
        )
        
