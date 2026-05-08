"""
models.py

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
    city : str
        Nom de la ville.
    temp : float
        Température actuelle en degrés Celsius.
    feels_like : float
        Température ressentie (°C).
    condition : str
        Type de météo simplifié (ex: "rain", "clear", "clouds").
    description : str
        Description textuelle lisible (ex: "ciel dégagé").
    icon : str
        Code de l'icône OpenWeatherMap (ex: "01d").
    humidity : int
        Humidité relative en pourcentage.
    wind_speed : float
        Vitesse du vent en km/h.
    """

    city: str
    temp: float
    feels_like: float
    condition: str
    description: str
    icon: str
    humidity: int
    wind_speed: float

    def __str__(self) -> str:
        """
        Retourne un résumé lisible de la météo.

        Ex:
        "Paris — ciel dégagé — 22°C (ressenti 20°C) — Humidité 45%"
        """
        return (
            f"{self.city} — {self.description} — {self.temp}°C (ressenti {self.feels_like}°C) — Humidité {self.humidity}%"
        )

    def is_rainy(self) -> bool:
        """
        Indique si les conditions météo suggèrent de la pluie.

        Returns
        bool
            True si la condition contient "rain" ou "drizzle".
        """
        return (
            "rain" in self.condition.lower()
            or "drizzle" in self.condition.lower()
        )

    def is_hot(self) -> bool:
        """
        Détermine si la température est considérée comme élevée.

        Returns
        bool
            True si la température dépasse 28°C.
        """
        return self.temp > 28


@dataclass
class TimeSlot:
    """
    Représente une activité planifiée à un moment précis de la journée.

    Attributes

    time : str
        Heure de l'activité (format "HH:MM").
    activity : str
        Description de l'activité (ex: "Visite du musée").
    location : Optional[str]
        Nom du lieu de l'activité.
    lat : Optional[float]
        Latitude du lieu (utile pour une carte).
    lon : Optional[float]
        Longitude du lieu.
    """

    time: str
    activity: str
    location: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None

    def __str__(self) -> str:
        """
        Retourne une description lisible du créneau.

        Ex: "09:00 — Visite du musée (Musée des Beaux-Arts)"
        """
        if self.location:
            return f"{self.time} — {self.activity} ({self.location})"
        return f"{self.time} — {self.activity}"


@dataclass
class DayProgram:
    """
    Représente l'organisation complète d'une journée.

    Attributes
    
    slots : list[TimeSlot]
        Liste des activités planifiées dans la journée.
    outfit : list[str]
        Suggestions de vêtements adaptées à la météo.
    food : list[str]
        Suggestions de nourriture ou boissons.
    score : int
        Note globale de la journée (sur 10).
    quote : str
        Citation liée à la météo ou à la ville.
    """

    slots: list[TimeSlot] = field(default_factory=list)
    outfit: list[str] = field(default_factory=list)
    food: list[str] = field(default_factory=list)
    score: int = 0
    quote: str = ""

    def __str__(self) -> str:
        """
        Retourne un résumé rapide du programme.

        Ex: "Programme : 4 activités — Score : 8/10"
        """
        return f"Programme : {len(self.slots)} activités — Score : {self.score}"

    def add_slot(self, slot: TimeSlot) -> None:
        """
        Ajoute un créneau d'activité au programme de la journée.

        Params
        
        slot : TimeSlot
            Créneau à ajouter.
        """
        self.slots.append(slot)

@dataclass
class ProfileData:
    """
    Représente les préférences et l'historique d'un utilisateur.

    Attributes
    ----------
    name : str
        Nom de l'utilisateur.
    description : str
        Bio courte de l'utilisateur, transmise à l'IA pour
        personnaliser les suggestions (ex: "Étudiant passionné
        de culture et de gastronomie").
    tastes : list[str]
        Centres d'intérêt parmi :
        "sport" | "culture" | "nature" | "shopping" | "repos" |
        "social" | "creatif" | "gastronomie" | "academique" |
        "religion" | "maison" | "professionnel"
    mood : str
        Type de journée souhaitée :
        "repos" | "aventure" | "random"
    style : str
        Style vestimentaire :
        "streetwear" | "oldmoney" | "casual" | "boheme" |
        "sportswear" | "minimaliste" | "preppy" | "random"
    cuisine : str
        Cuisine préférée :
        "asiatique" | "méditerranéenne" | "africaine" |
        "américaine" | "française" | "moyen-orientale" |
        "latino" | "fastfood" | "random"
    history : list[dict]
        Historique des programmes de journées précédentes.
    """

    name: str             = "Utilisateur"
    description: str      = "Anything"            
    tastes: list[str]     = field(default_factory=list)
    mood: str             = "random"
    style: str            = "random"
    cuisine: str          = "random"
    history: list[dict]   = field(default_factory=list)

    def __str__(self) -> str:
        """
        Retourne une description rapide du profil.

        Ex: "Profil : Alex — Goûts : sport, culture — Humeur : aventure
             — Style : oldmoney — Cuisine : africaine"
        """
        tastes_str = ", ".join(self.tastes) if self.tastes else "aucun"
        return (
            f"Profil : {self.name} — "
            f"Goûts : {tastes_str} — "
            f"Humeur : {self.mood} — "
            f"Style : {self.style} — "
            f"Cuisine : {self.cuisine}"
        )

    def add_to_history(self, day: dict) -> None:
        """
        Ajoute un programme de journée à l'historique.

        Parameters
        ----------
        day : dict
            Représentation d'une journée passée.
        """
        self.history.append(day)

    def to_ai_context(self) -> str:
        """
        Génère un résumé du profil formaté pour l'IA.

        Utilisé plus tard lors de l'intégration de Claude API
        pour personnaliser les suggestions.

        Returns
        -------
        str
            Contexte lisible par l'IA décrivant l'utilisateur.
        """
        tastes_str = ", ".join(self.tastes) if self.tastes else "aucun goût défini"
        desc = f" — {self.description}" if self.description else ""
        return (
            f"Utilisateur : {self.name}{desc}. "
            f"Goûts : {tastes_str}. "
            f"Humeur : {self.mood}. "
            f"Style vestimentaire : {self.style}. "
            f"Cuisine préférée : {self.cuisine}."
        )