# ui/weather_frame.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import tkinter as tk
import tkinter.font as tkfont
import customtkinter as ctk
from datetime import datetime

from core.activity_engine import ActivityEngine
from core.weather_service import WeatherService
from core.day_planner import DayPlanner
from core.user_profile import UserProfile
from ui.config import COLORS, get_font, load_icon


class WeatherFrame(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Frame scrollable contient tout le contenu
        self.scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=COLORS["border"],
        )
        self.scroll.grid(row=0, column=0, sticky="nsew")
        self.scroll.grid_columnconfigure(0, weight=1)
        self._build_ui()
        self._load_data()

    # Construction de l'UI 

    def _build_ui(self):

        # Header : date + titre 
        header = ctk.CTkFrame(self.scroll, fg_color="transparent")
        header.grid(row=0, column=0, padx=24, pady=(20, 12), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        date_str = datetime.now().strftime("%A %d %B")
        ctk.CTkLabel(
            header, text=date_str,
            font=get_font(14),
            text_color=COLORS["text_muted"],
            anchor="w"
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            header, text="Météo du jour",
            font=get_font(24, "bold"),
            text_color=COLORS["text_primary"],
            anchor="w"
        ).grid(row=1, column=0, sticky="w")

        # Carte météo principale 
        main_card = ctk.CTkFrame(
            self.scroll,
            fg_color=COLORS["bg_card"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"]
        )
        main_card.grid(row=1, column=0, padx=24, pady=(0, 14), sticky="ew")
        main_card.grid_columnconfigure(0, weight=1)
        main_card.grid_columnconfigure(1, weight=0)  # colonne icône de taille fixe

        # Ville
        self.city_label = ctk.CTkLabel(
            main_card, text="Ville",
            font=get_font(14),
            text_color=COLORS["text_muted"],
            anchor="w"
        )
        self.city_label.grid(row=0, column=0, padx=20, pady=(20, 6), sticky="w")

        # Température
        self.temp_label = ctk.CTkLabel(
            main_card, text="--°",
            font=get_font(56, "bold"),
            text_color=COLORS["text_primary"],
            anchor="w"
        )
        self.temp_label.grid(row=1, column=0, padx=20, pady=(0, 4), sticky="w")

        # Ressenti + condition
        self.desc_label = ctk.CTkLabel(
            main_card, text="Ressenti --° — --",
            font=get_font(16),
            text_color=COLORS["text_secondary"],
            anchor="w"
        )
        self.desc_label.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="w")

        # Icône météo, colonne droite, occupe les 3 lignes
        self.icon_label = ctk.CTkLabel(main_card, text="")
        self.icon_label.grid(
            row=0, column=1, rowspan=3,
            padx=20, pady=20, sticky="e"
        )

        # 3 cartes stats 
        stats_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        stats_frame.grid(row=2, column=0, padx=24, pady=(0, 14), sticky="ew")
        stats_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.wind_label = self._make_stat_card(
            stats_frame, "Vent", "-- km/h", col=0
        )
        # Score : accent=True → chiffre bleu + /10 gris
        self._make_stat_card(
            stats_frame, "Score journée", "", col=1, accent=True
        )
        self.hum_label = self._make_stat_card(
            stats_frame, "Humidité", "--%", col=2
        )

        # Tenue suggérée 
        outfit_card = ctk.CTkFrame(
            self.scroll,
            fg_color=COLORS["bg_card"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"]
        )
        outfit_card.grid(row=3, column=0, padx=24, pady=(0, 12), sticky="ew")
        outfit_card.grid_columnconfigure(0, weight=1)

        self.outfit_title_label = ctk.CTkLabel(
            outfit_card, text="Tenue suggérée",
            font=get_font(14),
            text_color=COLORS["text_muted"],
            anchor="w"
        )
        self.outfit_title_label.grid(
            row=0, column=0, padx=16, pady=(14, 8), sticky="w"
        )

        # Frame badges — remplie dynamiquement dans _update_ui
        self.outfit_badges_frame = ctk.CTkFrame(
            outfit_card, fg_color="transparent"
        )
        self.outfit_badges_frame.grid(
            row=1, column=0, padx=12, pady=(0, 14), sticky="w"
        )

        # Citation
        quote_frame = ctk.CTkFrame(
            self.scroll, fg_color="transparent"
        )
        quote_frame.grid(row=4, column=0, padx=24, pady=(0, 12), sticky="ew")
        quote_frame.grid_columnconfigure(1, weight=1)

        # Barre bleue verticale à gauche
        ctk.CTkFrame(
            quote_frame,
            width=4,
            fg_color=COLORS["accent"],
            corner_radius=2
        ).grid(row=0, column=0, sticky="ns", padx=(0, 12))

        self.quote_label = ctk.CTkLabel(
            quote_frame, text="...",
            font=get_font(16),
            text_color=COLORS["text_secondary"],
            wraplength=500,
            justify="left",
            anchor="w"
        )
        self.quote_label.grid(row=0, column=1, pady=8, sticky="w")

        # Suggestions repas
        food_card = ctk.CTkFrame(
            self.scroll,
            fg_color=COLORS["bg_card"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"]
        )
        food_card.grid(row=5, column=0, padx=24, pady=(0, 24), sticky="ew")
        food_card.grid_columnconfigure(1, weight=1)

        self.food_title_label = ctk.CTkLabel(
            food_card, text="Suggestions repas",
            font=get_font(14),
            text_color=COLORS["text_muted"],
            anchor="w"
        )
        self.food_title_label.grid(
            row=0, column=0, columnspan=2,
            padx=16, pady=(12, 8), sticky="w"
        )

        # Frame repas remplie dynamiquement dans _update_ui
        self.food_frame = ctk.CTkFrame(food_card, fg_color="transparent")
        self.food_frame.grid(
            row=1, column=0, columnspan=2,
            padx=16, pady=(0, 16), sticky="ew"
        )
        self.food_frame.grid_columnconfigure(1, weight=1)

    # Méthode helper : carte stat 

    def _make_stat_card(
        self,
        parent,
        title: str,
        value: str,
        col: int,
        accent: bool = False
    ) -> ctk.CTkLabel | None:
        """
        Crée une carte statistique (Vent, Score, Humidité).

        Parameters
        accent : bool
            Si True chiffre en bleu accent + "/10" en gris.
            Utilisé pour le score journée.

        Returns
        CTkLabel | None
            Le label de valeur à mettre à jour, ou None si accent=True
            (dans ce cas self.score_num_label est utilisé directement).
        """
        card = ctk.CTkFrame(
            parent,
            fg_color=COLORS["bg_card"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"]
        )
        # padx=(0,8) sur col 0 et 1 pour espacer les cartes entre elles
        card.grid(
            row=0, column=col,
            padx=(0, 8) if col < 2 else 0,
            sticky="ew"
        )
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card, text=title,
            font=get_font(14),
            text_color=COLORS["text_muted"],
            anchor="w"
        ).grid(row=0, column=0, padx=16, pady=(18, 6), sticky="w")

        if accent:
            # Chiffre bleu + "/10" gris sur la même ligne
            val_frame = ctk.CTkFrame(card, fg_color="transparent")
            val_frame.grid(row=1, column=0, padx=16, pady=(0, 18), sticky="w")

            self.score_num_label = ctk.CTkLabel(
                val_frame, text="--",
                font=get_font(26, "bold"),
                text_color=COLORS["accent"]
            )
            self.score_num_label.pack(side="left")

            ctk.CTkLabel(
                val_frame, text=" /10",
                font=get_font(16),
                text_color=COLORS["text_muted"]
            ).pack(side="left")

            return None  # pas de label unique à retourner

        else:
            value_label = ctk.CTkLabel(
                card, text=value,
                font=get_font(22, "bold"),
                text_color=COLORS["text_primary"],
                anchor="w"
            )
            value_label.grid(row=1, column=0, padx=16, pady=(0, 18), sticky="w")
            return value_label

    # Chargement des données

    def _load_data(self, city = None):
        """
        Récupère la météo, le profil utilisateur et génère
        les suggestions. Met à jour l'UI avec les vraies données.
        """
        service = WeatherService()
        engine  = ActivityEngine()
        planner = DayPlanner()
        profile = UserProfile().load()

        city = city or service.get_city_auto() or "Libreville"
        weather = service.get_current(city)

        if not weather:
            return

        outfit = engine.suggest_outfit(weather, style=profile.style)
        food   = engine.suggest_food(weather, cuisine=profile.cuisine)
        quote  = planner.get_quote(weather)
        score  = planner.score_day(weather)

        self._update_ui(
            weather=weather,
            outfit=outfit,
            food=food,
            quote=quote,
            score=score,
            cuisine=profile.cuisine
        )

    # Mise à jour de l'UI

    def _update_ui(
        self,
        weather,
        outfit,
        food,
        quote,
        score,
        cuisine: str = "random"
    ):
        """Injecte toutes les données dans les widgets existants."""

        # Carte principale 
        self.city_label.configure(text=weather.city)
        self.temp_label.configure(text=f"{int(weather.temp)}°")
        self.desc_label.configure(
            text=f"Ressenti {int(weather.feels_like)}° — {weather.description}"
        )

        # Icône météo OpenWeatherMap
        icon = load_icon(weather.icon, size=110)
        if icon:
            self.icon_label.configure(image=icon, text="")
            self.icon_label.image = icon  # référence pour éviter garbage collection

        # Stats 
        self.wind_label.configure(text=f"{weather.wind_speed} km/h")
        self.hum_label.configure(text=f"{weather.humidity}%")
        self.score_num_label.configure(text=str(score))

        #  Citation 
        self.quote_label.configure(text=f'{quote}')

        # Tenue  titre avec style
        # Récupère le style depuis le dernier élément des suggestions
        style_line = outfit[-1] if "Style" in outfit[-1] else ""
        style_name = style_line.strip() if style_line else ""
        self.outfit_title_label.configure(
            text=f"Tenue suggérée{f' — {style_name}' if style_name else ''}"
        )

        # Badges tenue — filtre la ligne " Style : ..."
        for widget in self.outfit_badges_frame.winfo_children():
            widget.destroy()  # nettoie les anciens badges

        for item in outfit:
            if "Style" in item:
                continue  # ignore la ligne de style
            badge = ctk.CTkLabel(
                self.outfit_badges_frame,
                text=item,
                font=get_font(14),
                fg_color=COLORS["bg_main"],
                text_color=COLORS["accent"],
                corner_radius=6,
                padx=10, pady=4
            )
            badge.pack(side="left", padx=(0, 6), pady=6)

        #Repas titre avec cuisine 
        cuisine_name = cuisine.capitalize() if cuisine != "random" else ""
        self.food_title_label.configure(
            text=f"Suggestions repas{f' — Cuisine {cuisine_name}' if cuisine_name else ''}"
        )

        # Lignes repas : nettoie d'abord
        for widget in self.food_frame.winfo_children():
            widget.destroy()

        MEAL_TIMES = ["08:00", "12:00", "16:00", "19:00"]

        # Filtre la ligne " Cuisine : ..." et prend 3 suggestions
        clean_food = [f for f in food if "Cuisine" not in f][:4]

        for i, (time, plat) in enumerate(zip(MEAL_TIMES, clean_food)):
            # Heure
            ctk.CTkLabel(
                self.food_frame, text=time,
                font=get_font(14),
                text_color=COLORS["text_muted"],
                anchor="w",
                width=50
            ).grid(row=i * 2, column=0, pady=(6, 0), sticky="w")

            # Plat
            ctk.CTkLabel(
                self.food_frame, text=plat,
                font=get_font(16),
                text_color=COLORS["text_primary"],
                anchor="w"
            ).grid(row=i * 2, column=1, padx=(16, 0), pady=(6, 0), sticky="w")

            # Séparateur sauf après le dernier repas
            if i < len(clean_food) - 1:
                tk.Canvas(
                    self.food_frame,
                    height=1,
                    bg=COLORS["border"],
                    highlightthickness=0
                ).grid(row=i * 2 + 1, column=0, columnspan=2, sticky="ew", pady=4)

    
    def refresh(self, city: str):
        """
        Rafraîchit le programme avec une nouvelle ville.
        Appelée par MainWindow quand l'utilisateur change de ville.
        """
        self._load_data(city)


if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("800x650")
    root.configure(fg_color=COLORS["bg_main"])
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)
    frame = WeatherFrame(root)
    frame.grid(row=0, column=0, sticky="nsew")
    root.mainloop()