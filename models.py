# models.py
"""
Contient les structures de données principales utilisées dans l'application.
Chaque classe représente une entité du programme (météo, activité, programme
de la journée, profil utilisateur).
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class WeatherData:
    """
    Représente les informations météorologiques pour une ville donnée.

    Attributes
    ----------
    city : str
        Nom de la ville.
    temp : float
        Température actuelle en degrés Celsius.
    feels_like : float
        Température ressentie en degrés Celsius.
    condition : str
        Type de météo simplifié ex: "rain", "clear", "clouds".
    description : str
        Description textuelle lisible ex: "ciel dégagé".
    icon : str
        Code de l'icône OpenWeatherMap ex: "01d".
    humidity : int
        Humidité relative en pourcentage.
    wind_speed : float
        Vitesse du vent en km/h.
    lat : float
        Latitude de la ville utilisée pour centrer la carte.
    lon : float
        Longitude de la ville utilisée pour centrer la carte.
    """

    city:        str
    temp:        float
    feels_like:  float
    condition:   str
    description: str
    icon:        str
    humidity:    int
    wind_speed:  float
    lat:         float = 0.0
    lon:         float = 0.0

    def __str__(self) -> str:
        """
        Retourne un résumé lisible de la météo.

        Ex: "Paris, ciel dégagé, 22°C (ressenti 20°C). Humidité 45%"
        """
        return (
            f"{self.city}, {self.description}, "
            f"{self.temp}°C (ressenti {self.feels_like}°C). "
            f"Humidité {self.humidity}%"
        )

    def is_rainy(self) -> bool:
        """
        Indique si les conditions météo suggèrent de la pluie.

        Returns
        -------
        bool
            True si la condition contient "rain" ou "drizzle".
        """
        return (
            "rain"    in self.condition.lower()
            or "drizzle" in self.condition.lower()
        )


@dataclass
class TimeSlot:
    """
    Représente une activité planifiée à un moment précis de la journée.

    Attributes
    ----------
    time : str
        Heure de l'activité au format "HH:MM".
    activity : str
        Description de l'activité ex: "Visite du musée".
    location : Optional[str]
        Nom du lieu  rempli par l'enrichissement IA si disponible.
    lat : Optional[float]
        Latitude du lieu utilisée pour placer un marqueur sur la carte.
    lon : Optional[float]
        Longitude du lieu utilisée pour placer un marqueur sur la carte.
    """

    time:     str
    activity: str
    location: Optional[str]   = None
    lat:      Optional[float] = None
    lon:      Optional[float] = None


@dataclass
class DayProgram:
    """
    Représente l'organisation complète d'une journée.

    Attributes
    ----------
    slots : list[TimeSlot]
        Liste des activités et repas planifiés dans la journée.
    outfit : list[str]
        Suggestions de vêtements adaptées à la météo et au style.
    food : list[str]
        Suggestions de plats selon la cuisine préférée.
    score : int
        Note globale de la journée sur 10 calculée depuis la météo.
    quote : str
        Citation inspirante liée à la météo ou à la ville.
    """

    slots:  list[TimeSlot] = field(default_factory=list)
    outfit: list[str]      = field(default_factory=list)
    food:   list[str]      = field(default_factory=list)
    score:  int            = 0
    quote:  str            = ""


@dataclass
class ProfileData:
    """
    Représente les préférences et l'historique d'un utilisateur.

    Attributes
    ----------
    name : str
        Nom de l'utilisateur.
    description : str
        Bio courte transmise à l'IA pour personnaliser les suggestions.
    tastes : list[str]
        Centres d'intérêt clés de categories.json.
    mood : str
        Type de journée souhaitée : "repos" | "aventure" | "random".
    style : str
        Style vestimentaire : "streetwear" | "oldmoney" | "casual" |
        "boheme" | "sportswear" | "minimaliste" | "preppy" | "random".
    cuisine : str
        Cuisine préférée : "asiatique" | "méditerranéenne" | "gabonaise" |
        "américaine" | "française" | "moyen-orientale" | "latino" |
        "fastfood" | "random" | etc.
    history : list[dict]
        Historique des programmes de journées précédentes.
    """

    name:        str        = "Utilisateur"
    description: str        = ""
    tastes:      list[str]  = field(default_factory=list)
    mood:        str        = "random"
    style:       str        = "random"
    cuisine:     str        = "random"
    history:     list[dict] = field(default_factory=list)

    def to_ai_context(self) -> str:
        """
        Génère un résumé du profil formaté pour l'IA Groq.

        Utilisé dans AIService.enrich_activities() pour personnaliser
        les suggestions de lieux selon le profil utilisateur.

        Returns
        -------
        str
            Contexte lisible par l'IA décrivant l'utilisateur.
        """
        tastes_str = ", ".join(self.tastes) if self.tastes else "aucun goût défini"
        desc       = f" {self.description}" if self.description else ""
        return (
            f"Utilisateur : {self.name}{desc}. "
            f"Goûts : {tastes_str}. "
            f"Humeur : {self.mood}. "
            f"Style vestimentaire : {self.style}. "
            f"Cuisine préférée : {self.cuisine}."
        )