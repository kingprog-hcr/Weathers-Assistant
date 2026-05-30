# core/activity_engine.py
"""
Moteur de suggestions locales d'activités, tenues et repas.

Génère des suggestions personnalisées à partir des fichiers JSON locaux.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import random
from models import WeatherData


class ActivityEngine:
    """
    Moteur local de suggestions basé sur des catalogues JSON.

    Charge les fichiers activities.json, styles.json et food.json
    au démarrage et génère des suggestions adaptées à la météo
    et au profil utilisateur.

    Attributes
    ----------
    BASE_DIR : Path
        Racine du projet pour construire les chemins absolus.
    ACTIVITIES_FILE : Path
        Chemin vers data/activities.json.
    STYLES_FILE : Path
        Chemin vers data/styles.json.
    FOOD_FILE : Path
        Chemin vers data/food.json.
    activities : dict
        Catalogue d'activités chargé depuis activities.json.
    """

    BASE_DIR        = Path(__file__).resolve().parent.parent
    ACTIVITIES_FILE = BASE_DIR / "data" / "activities.json"
    STYLES_FILE     = BASE_DIR / "data" / "styles.json"
    FOOD_FILE       = BASE_DIR / "data" / "food.json"

    def __init__(self):
        """Initialise le moteur et charge les activités."""
        self.activities = self._load_activities()

    def _load_activities(self) -> dict:
        """Charge le fichier activities.json."""
        try:
            with open(self.ACTIVITIES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def _load_food(self) -> dict:
        """Charge le fichier food.json."""
        try:
            with open(self.FOOD_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def _load_styles(self) -> dict:
        """Charge le fichier styles.json."""
        try:
            with open(self.STYLES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def suggest_activities(
        self,
        weather: WeatherData,
        tastes: list[str] | None = None,
        max_results: int = 6
    ) -> list[str]:
        """
        Génère des suggestions d'activités en fonction de la météo et des goûts.

        Filtre les activités disponibles selon la condition météo,
        puis sélectionne aléatoirement parmi les catégories préférées
        de l'utilisateur.

        Parameters
        ----------
        weather : WeatherData
            Données météorologiques actuelles.
        tastes : list[str] | None
            Catégories préférées ex: ["culture", "sport"].
            Si None, toutes les catégories sont utilisées.
        max_results : int
            Nombre maximum d'activités retournées.

        Returns
        -------
        list[str]
            Liste d'activités mélangées aléatoirement.
        """
        condition = weather.condition.lower()

        if condition not in self.activities:
            return []

        condition_activities = self.activities[condition]

        # Si aucun goût spécifié, utilise toutes les catégories disponibles
        if not tastes:
            tastes = list(condition_activities.keys())

        suggestions = []
        for taste in tastes:
            if taste in condition_activities:
                for item in condition_activities[taste]:
                    # Gère les deux formats : string simple et dict custom
                    if isinstance(item, str):
                        suggestions.append(item)
                    elif isinstance(item, dict) and "name" in item:
                        suggestions.append(item["name"])

        if not suggestions:
            return []

        # random.sample garantit des activités différentes à chaque appel
        return random.sample(
            suggestions,
            k=min(max_results, len(suggestions))
        )

    def suggest_outfit(self, weather: WeatherData, style: str = "random") -> list[str]:
        """
        Retourne une tenue adaptée à la météo et au style vestimentaire.

        Détermine la catégorie de température, sélectionne le style
        et retourne la liste des vêtements avec accessoires météo.

        Parameters
        ----------
        weather : WeatherData
            Données météo actuelles.
        style : str
            Style vestimentaire parmi : "streetwear", "oldmoney", "casual",
            "boheme", "sportswear", "minimaliste", "preppy", "random".
        """
        temp      = weather.temp
        is_rainy  = weather.is_rainy()
        condition = weather.condition.lower()

        STYLES = self._load_styles()

        # Détermine la clé de température pour le catalogue
        if condition == "snow":
            temp_key = "neige"
        elif is_rainy:
            temp_key = "pluie"
        elif temp < 0:
            temp_key = "froid_extreme"
        elif temp < 8:
            temp_key = "froid"
        elif temp < 15:
            temp_key = "frais"
        elif temp < 23:
            temp_key = "doux"
        else:
            temp_key = "chaud"

        # Choisit un style aléatoire si "random" ou style inconnu
        if style == "random" or style not in STYLES:
            style = random.choice(list(STYLES.keys()))

        raw_outfit = list(STYLES[style][temp_key])
        outfit = []
        for item in raw_outfit:
            if isinstance(item, str):
                outfit.append(item)
            elif isinstance(item, dict) and "name" in item:
                outfit.append(item["name"])

        # random.shuffle mélange l'ordre des vêtements à chaque appel
        # pour éviter que la tenue soit toujours présentée dans le même ordre
        random.shuffle(outfit)

        # Accessoires universels selon météo extrême
        if condition == "clear" and temp > 22:
            outfit.append("lunettes de soleil")
        if temp < 5 and "bonnet" not in str(outfit):
            outfit.append("bonnet")

        # Indique le style choisi en dernière position
        outfit.append(f"Style : {style.capitalize()}")

        return outfit[:4]  # Limite à 4 éléments pour éviter surcharge d'informations

    def suggest_food(self, weather: WeatherData, cuisine: str = "random") -> list[str]:
        """
        Retourne des suggestions de plats selon la cuisine préférée.

        La météo n'influence plus le choix des plats on peut manger
        n'importe quel plat par n'importe quel temps.
        Un pool de 4 plats est retourné mélangé aléatoirement.

        Parameters
        ----------
        weather : WeatherData
            Données météo conservées en paramètre pour compatibilité
            avec les appels existants mais non utilisé dans la logique.
        cuisine : str
            Type de cuisine parmi les clés de food.json, ou "random".

        Returns
        -------
        list[str]
            Liste de suggestions mélangées + ligne "Cuisine : ..." en dernier.
        """
        CUISINES = self._load_food()

        # Choisit une cuisine aléatoire si "random" ou cuisine inconnue
        if cuisine == "random" or cuisine not in CUISINES:
            cuisine = random.choice(list(CUISINES.keys()))

        # Récupère tous les plats de cette cuisine format str ou dict custom
        raw_items = CUISINES.get(cuisine, [])
        suggestions = []
        for item in raw_items:
            if isinstance(item, str):
                suggestions.append(item)
            elif isinstance(item, dict) and "name" in item:
                suggestions.append(item["name"])

        if not suggestions:
            return [f"Cuisine : {cuisine.capitalize()}"]

        # Mélange et retourne un pool de 4 plats maximum
        random.shuffle(suggestions)
        result = suggestions[:8]   # pool plus large pour cycle() dans DayPlanner

        # Ligne de référence cuisine en dernière position
        # exclue par [:-1] dans DayPlanner avant random.choice
        result.append(f"Cuisine : {cuisine.capitalize()}")

        return result

if __name__ == "__main__":
    pass