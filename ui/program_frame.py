# ui/program_frame.py
"""
Page Programme du jour.

Affiche le programme complet de la journée sous forme de cartes
chronologiques (TimeSlots), avec un résumé en haut (score, nombre
d'activités, humeur) et un bouton pour regénérer le programme.

Dépendances :
    - core.weather_service  : récupère la météo par créneaux horaires
    - core.day_planner      : construit le DayProgram
    - core.user_profile     : charge le profil utilisateur
    - ui.config             : couleurs, polices, load_icon partagé
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import tkinter as tk
import customtkinter as ctk
from datetime import datetime

from core.weather_service import WeatherService
from core.day_planner import DayPlanner
from core.user_profile import UserProfile
from models import DayProgram, TimeSlot
from ui.config import COLORS, get_font, load_icon, get_translation, SLOT_CATEGORIES



def get_slot_badge(activity: str) -> tuple:
    """
    Détermine le badge coloré d'un TimeSlot selon les mots clés
    présents dans la description de l'activité.

    Parcourt SLOT_CATEGORIES et retourne le premier badge dont
    le mot clé est trouvé dans l'activité (insensible à la casse).

    Parameters
    ----------
    activity : str
        Description de l'activité ex: "Visite du musée des Beaux-Arts"

    Returns
    -------
    tuple
        (label, bg_color, text_color, border_color)
        ex: ("Culture", "#0f2a1a", "#4dbb7a", "#1a8a4a")
        Retourne un badge "Activité" gris si aucun mot clé trouvé.
    """
    activity_lower = activity.lower()
    for keyword, badge in SLOT_CATEGORIES.items():
        if keyword in activity_lower:
            return badge
    return ("Activité", "#1a1a2a", "#7777aa", "#3a3a6a")


def get_closest_weather(time: str, weather_slots: dict):
    """
    Trouve la WeatherData la plus proche d'une heure donnée.

    Stratégie :
    1. Cherche l'heure exacte dans weather_slots
    2. Si absent, convertit les heures en minutes et retourne
       la WeatherData dont l'heure est la plus proche

    Parameters
    ----------
    time : str
        Heure cherchée au format "HH:MM" ex: "10:00"
    weather_slots : dict[str, WeatherData]
        Dictionnaire heure → WeatherData retourné par get_day_slots()

    Returns
    -------
    WeatherData | None
        La WeatherData la plus proche, ou None si weather_slots est vide.
    """
    if time in weather_slots:
        return weather_slots[time]

    try:
        h, m = map(int, time.split(":"))
        target_minutes = h * 60 + m
    except ValueError:
        return next(iter(weather_slots.values()), None)

    closest = None
    min_diff = float("inf")

    for slot_time, weather in weather_slots.items():
        try:
            sh, sm = map(int, slot_time.split(":"))
            diff = abs((sh * 60 + sm) - target_minutes)
            if diff < min_diff:
                min_diff = diff
                closest = weather
        except ValueError:
            continue

    return closest


class ProgramFrame(ctk.CTkFrame):
    """
    Page "Programme du jour" de l'application WeatherProgramm.

    Affiche le programme complet de la journée sous forme de cartes
    chronologiques basées sur les TimeSlots du DayProgram. Chaque carte
    montre l'heure, la météo du créneau, l'activité, le lieu optionnel
    et un badge de catégorie coloré.

    En haut de page : 3 cartes résumé (score, nb activités, humeur)
    En bas : une citation inspirante liée à la météo.

    Attributes
    ----------
    scroll : CTkScrollableFrame
        Frame scrollable contenant tout le contenu de la page.
    score_num_label : CTkLabel
        Label du score journée (chiffre bleu).
    summary_count : CTkLabel
        Label du nombre d'activités planifiées.
    summary_mood : CTkLabel
        Label de l'humeur du profil utilisateur.
    slots_count_label : CTkLabel
        Label "X créneaux planifiés".
    slots_frame : CTkFrame
        Frame contenant les cartes TimeSlot, recréées à chaque refresh.
    quote_label : CTkLabel
        Label de la citation du jour.
    """

    def __init__(self, parent, lang: str ="fr"):
        """
        Initialise la ProgramFrame.

        Parameters
        ----------
        parent : CTkFrame
            Frame parente (self.content de MainWindow).
        """
        super().__init__(parent, fg_color="transparent")
        self.T = get_translation(lang)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=COLORS["border"]
        )
        self.scroll.grid(row=0, column=0, sticky="nsew")
        self.scroll.grid_columnconfigure(0, weight=1)

        self._build_ui()
        self._load_data()

    # Construction UI 

    def _build_ui(self):
        """
        Construit la structure statique de la page.

        Crée tous les widgets avec des valeurs placeholder.
        Les vraies données sont injectées par _update_ui().
        """

        # Header
        header = ctk.CTkFrame(self.scroll, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 14))
        header.grid_columnconfigure(0, weight=1)

        date_str = datetime.now().strftime("%A %d %B")
        ctk.CTkLabel(
            header, text=date_str,
            font=get_font(13),
            text_color=COLORS["text_muted"],
            anchor="w"
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            header, text=self.T["program_title"],
            font=get_font(24, "bold"),
            text_color=COLORS["text_primary"],
            anchor="w"
        ).grid(row=1, column=0, sticky="w")

        ctk.CTkButton(
            header,
            text=self.T["regenerate"],
            font=get_font(14),
            height=38,
            corner_radius=8,
            fg_color=COLORS["accent"],
            text_color="white",
            hover_color="#2d47d4",
            command=self._load_data
        ).grid(row=1, column=1, sticky="e", padx=(12, 0))

        # 3 cartes résumé 
        stats_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        stats_frame.grid(row=1, column=0, padx=24, pady=(0, 14), sticky="ew")
        stats_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self._make_summary_card(
            stats_frame, self.T["score"], "", col=0, accent=True
        )
        self.summary_count = self._make_summary_card(
            stats_frame, self.T["activities"], "--", col=1
        )
        self.summary_mood = self._make_summary_card(
            stats_frame, self.T["mood_label"], "--", col=2
        )

        # Label nb créneaux
        self.slots_count_label = ctk.CTkLabel(
            self.scroll, text= self.T["slots_label"],
            font=get_font(13),
            text_color=COLORS["text_muted"],
            anchor="w"
        )
        self.slots_count_label.grid(
            row=2, column=0, sticky="w", padx=24, pady=(0, 8)
        )

        # Frame des slots 
        # Vide au démarrage, remplie par _update_ui()
        self.slots_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        self.slots_frame.grid(
            row=3, column=0, padx=24, pady=(0, 16), sticky="ew"
        )
        self.slots_frame.grid_columnconfigure(0, weight=1)

        # Citation 
        quote_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        quote_frame.grid(row=4, column=0, padx=24, pady=(0, 24), sticky="ew")
        quote_frame.grid_columnconfigure(1, weight=1)

        # Barre bleue verticale à gauche
        ctk.CTkFrame(
            quote_frame,
            width=4, fg_color=COLORS["accent"], corner_radius=2
        ).grid(row=0, column=0, sticky="ns", padx=(0, 12))

        self.quote_label = ctk.CTkLabel(
            quote_frame, text="...",
            font=get_font(14),
            text_color=COLORS["text_secondary"],
            wraplength=600,
            justify="left",
            anchor="w"
        )
        self.quote_label.grid(row=0, column=1, pady=8, sticky="w")

    # Méthodes helper 

    def _make_summary_card(
        self,
        parent: ctk.CTkFrame,
        title: str,
        value: str,
        col: int,
        accent: bool = False
    ) -> ctk.CTkLabel | None:
        """
        Crée une carte résumé dans la grille des stats.

        Pour la carte Score (accent=True), affiche le chiffre en bleu
        suivi de "/10" en gris sur la même ligne.
        Pour les autres cartes, affiche une valeur simple en blanc.

        Parameters
        ----------
        parent : CTkFrame
            Frame grille contenant les 3 cartes.
        title : str
            Titre de la carte ex: "Score journée"
        value : str
            Valeur initiale placeholder ex: "--"
        col : int
            Colonne dans la grille (0, 1 ou 2).
        accent : bool
            Si True → chiffre bleu + "/10" gris (carte Score).

        Returns
        -------
        CTkLabel | None
            Le label de valeur à mettre à jour dans _update_ui(),
            ou None si accent=True (score_num_label est utilisé directement).
        """
        card = ctk.CTkFrame(
            parent,
            fg_color=COLORS["bg_card"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"]
        )
        card.grid(
            row=0, column=col,
            padx=(0, 8) if col < 2 else 0,
            sticky="ew"
        )
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card, text=title,
            font=get_font(13),
            text_color=COLORS["text_muted"],
            anchor="w"
        ).grid(row=0, column=0, padx=16, pady=(16, 4), sticky="w")

        if accent:
            val_frame = ctk.CTkFrame(card, fg_color="transparent")
            val_frame.grid(row=1, column=0, padx=16, pady=(0, 16), sticky="w")

            self.score_num_label = ctk.CTkLabel(
                val_frame, text="--",
                font=get_font(24, "bold"),
                text_color=COLORS["accent"]
            )
            self.score_num_label.pack(side="left")

            ctk.CTkLabel(
                val_frame, text=" /10",
                font=get_font(14),
                text_color=COLORS["text_muted"]
            ).pack(side="left")

            return None

        value_label = ctk.CTkLabel(
            card, text=value,
            font=get_font(20, "bold"),
            text_color=COLORS["text_primary"],
            anchor="w"
        )
        value_label.grid(row=1, column=0, padx=16, pady=(0, 16), sticky="w")
        return value_label

    def _make_slot_card(
        self,
        slot: TimeSlot,
        weather_info: str,
        icon: ctk.CTkImage | None,
        row: int
    ) -> ctk.CTkFrame:
        """
        Crée une carte visuelle pour un TimeSlot.

        Structure horizontale :
        [heure + température + icône] | [séparateur] | [activité + lieu] | [badge]

        Parameters
        ----------
        slot : TimeSlot
            Créneau à afficher (time, activity, location optionnel).
        weather_info : str
            Température du créneau ex: "18°"
        icon : CTkImage | None
            Icône météo OpenWeatherMap (28x28px), ou None si indisponible.
        row : int
            Index de ligne dans slots_frame (commence à 0).

        Returns
        -------
        CTkFrame
            La carte créée.
        """
        card = ctk.CTkFrame(
            self.slots_frame,
            fg_color=COLORS["bg_card"],
            corner_radius=10,
            border_width=2,
            border_color=COLORS["border"]
        )
        card.grid(row=row, column=0, sticky="ew", pady=(0, 8))
        card.grid_columnconfigure(2, weight=1)

        # Heure + météo 
        time_frame = ctk.CTkFrame(card, fg_color="transparent")
        time_frame.grid(row=0, column=0, sticky="ns", padx=(16, 8), pady=12)

        ctk.CTkLabel(
            time_frame,
            text=slot.time,
            text_color=COLORS["accent"],
            font=get_font(14, "bold"),
            anchor="center",
            width=48
        ).grid(row=0, column=0, columnspan=2, sticky="ew")

        ctk.CTkLabel(
            time_frame,
            text=weather_info,
            text_color=COLORS["text_muted"],
            font=get_font(12),
            width=32,
            anchor="w"
        ).grid(row=1, column=0, sticky="w", pady=(2, 0))

        if icon:
            ctk.CTkLabel(
                time_frame,
                text="",
                image=icon,
            ).grid(row=1, column=1, sticky="e", pady=(2, 0))

        # Séparateur vertical 
        # Canvas 1px de hauteur fixe évite que le séparateur s'étire sur toute la hauteur de la carte
        tk.Canvas(
            card,
            width=1, height=36,
            bg=COLORS["border"],
            highlightthickness=0
        ).grid(row=0, column=1, padx=(0, 12), pady=14)

        # Activité + lieu 
        activity_frame = ctk.CTkFrame(card, fg_color="transparent")
        activity_frame.grid(row=0, column=2, sticky="ew", pady=10)
        activity_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            activity_frame,
            text=slot.activity,
            text_color=COLORS["text_primary"],
            font=get_font(14, "bold"),
            anchor="w",
            wraplength=400
        ).grid(row=0, column=0, sticky="w")

        if slot.location:
            ctk.CTkLabel(
                activity_frame,
                text=slot.location,
                text_color=COLORS["text_muted"],
                font=get_font(12),
                anchor="w"
            ).grid(row=1, column=0, sticky="w", pady=(2, 0))

        # Badge catégorie 
        badge = get_slot_badge(slot.activity)

        badge_box = ctk.CTkFrame(
            card,
            fg_color=badge[1],
            corner_radius=8,
            border_width=2,
            border_color=badge[3]
        )
        badge_box.grid(row=0, column=3, sticky="e", padx=(8, 14), pady=14)

        ctk.CTkLabel(
            badge_box,
            text=badge[0],
            text_color=badge[2],
            font=get_font(12, "bold"),
            anchor="center"
        ).grid(row=0, column=0, padx=10, pady=5)

        return card

    # Chargement des données 

    def _load_data(self, city: str = None):
        """
        Charge les données météo et construit le programme de la journée.

        Appelle WeatherService pour récupérer la météo par créneaux,
        puis DayPlanner pour construire le DayProgram selon le profil.
        Enfin appelle _update_ui() pour afficher les résultats.

        Parameters
        ----------
        city : str, optional
            Ville à utiliser. Si None, tente la géolocalisation auto
            puis utilise "Paris" comme fallback.
        """
        service = WeatherService()
        planner = DayPlanner()
        profile = UserProfile().load()

        city = city or service.get_city_auto() or "Libreville"
        weather_slots = service.get_day_slots(city)

        if not weather_slots:
            return

        program = planner.build_program(weather_slots, profile)
        dominant = planner._get_dominant_weather(weather_slots)
        quote = planner.get_quote(dominant)

        self._update_ui(program, weather_slots, quote)
        from dataclasses import asdict
        from projet import add_day_to_history

        add_day_to_history(
            program=asdict(program),
            weather=asdict(dominant)
        )

    #  Mise à jour UI 

    def _update_ui(
        self,
        program: DayProgram,
        weather_slots: dict,
        quote: str
    ):
        """
        Injecte les données du programme dans tous les widgets.

        Met à jour les cartes résumé, recrée les cartes TimeSlot
        (après avoir détruit les précédentes) et met à jour la citation.

        Parameters
        ----------
        program : DayProgram
            Programme complet de la journée.
        weather_slots : dict[str, WeatherData]
            Météo par créneau horaire, utilisé pour afficher
            la température adaptée à chaque slot.
        quote : str
            Citation du jour.
        """
        # Résumé 
        self.score_num_label.configure(text=str(program.score))
        self.summary_count.configure(text=str(len(program.slots)))

        profile = UserProfile().load()
        self.summary_mood.configure(text=profile.mood.capitalize())

        n = len(program.slots)
        self.slots_count_label.configure(
            text=f"{n} {self.T["slots_label"]} "
        )

        # Slots 
        # Détruit les cartes précédentes avant d'en créer de nouvelles
        for widget in self.slots_frame.winfo_children():
            widget.destroy()

        for i, slot in enumerate(program.slots):
            weather = get_closest_weather(slot.time, weather_slots)

            if weather:
                # load_icon importé depuis config.py — taille 28 pour les slots
                img = load_icon(weather.icon, size=28)
                weather_info = f"{int(weather.temp)}°"
            else:
                img = None
                weather_info = "--°"

            self._make_slot_card(slot, weather_info, icon=img, row=i)

        # Citation 
        self.quote_label.configure(text=f'"{quote}"')

    # Interface publique

    def refresh(self, city: str):
        """
        Rafraîchit le programme avec une nouvelle ville.

        Méthode publique appelée par MainWindow._refresh_frames()
        quand l'utilisateur change de ville via la barre de recherche.

        Parameters
        ----------
        city : str
            Nouvelle ville à utiliser.
        """
        self._load_data(city)


if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("900x700")
    root.configure(fg_color=COLORS["bg_main"])
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)
    frame = ProgramFrame(root, lang="es")
    frame.grid(row=0, column=0, sticky="nsew")
    root.mainloop()