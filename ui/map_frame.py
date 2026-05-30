# ui/map_frame.py
"""
Page Carte interactive de l'application WeatherProgramm.

Affiche une carte centrée sur la ville avec des marqueurs pour chaque
activité du programme du jour qui dispose de coordonnées GPS.
Utilise le même programme que ProgramFrame via un callback get_program.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import customtkinter as ctk
import tkintermapview as tkmap

from core.weather_service import WeatherService
from ui.config import COLORS, get_font


class MapFrame(ctk.CTkFrame):
    """
    Page carte interactive du programme du jour.

    Affiche la carte avec les marqueurs correspondent
    exactement aux activités affichées dans le programme, sans régénérer
    un nouveau programme.

    Attributes
    ----------
    _current_city : str | None
        Ville actuellement affichée.
    _get_program : callable | None
        Callback vers MainWindow pour récupérer le DayProgram actuel
        de ProgramFrame sans le régénérer.
    mapp : TkinterMapView
        Widget carte interactif OpenStreetMap.
    info_label : CTkLabel
        Label affichant le nombre de lieux géolocalisés.
    """

    def __init__(self, parent, get_program=None):
        """
        Initialise la MapFrame.

        Parameters
        ----------
        parent : CTkFrame
            Frame parente.
        lang : str
            Langue de l'interface.
        get_program : callable | None
            Fonction sans argument qui retourne le DayProgram actuel
            de ProgramFrame. Passé par MainWindow.
        """
        super().__init__(parent, fg_color="transparent")
        self._current_city = None
        self._get_program  = get_program

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_ui()
        self._load_data()

    def _build_ui(self):
        """
        Construit l'interface : header compact + carte pleine hauteur.
        """

        # Header : titre + info 
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=24, pady=(16, 8), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="Carte du jour",
            font=get_font(22, "bold"),
            text_color=COLORS["text_primary"],
            anchor="w"
        ).grid(row=0, column=0, sticky="w")

        self.info_label = ctk.CTkLabel(
            header,
            text="Chargement...",
            font=get_font(15),
            text_color=COLORS["text_muted"],
            anchor="w"
        )
        self.info_label.grid(row=0, column=1, sticky="e")

        # Conteneur carte prend tout l'espace restant
        map_container = ctk.CTkFrame(
            self,
            fg_color=COLORS["bg_card"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"]
        )
        map_container.grid(
            row=1, column=0,
            padx=24, pady=(0, 20),
            sticky="nsew"   # s'étire dans toutes les directions
        )
        map_container.grid_columnconfigure(0, weight=1)
        map_container.grid_rowconfigure(0, weight=1)

        # Carte OpenStreetMap
        self.mapp = tkmap.TkinterMapView(
            map_container,
            corner_radius=10
        )
        self.mapp.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        self.mapp.set_zoom(13)

    def _load_data(self, city: str = None):
        """
        Charge la carte avec la ville et les marqueurs du programme actuel.

        Récupère le programme depuis ProgramFrame via _get_program()
        pour afficher exactement les mêmes activités.
        Si _get_program est None ou que le programme est vide,
        affiche juste la carte centrée sur la ville.

        Parameters
        ----------
        city : str, optional
            Ville à centrer. Si None, utilise la ville mémorisée
            ou la géolocalisation automatique.
        """
        service = WeatherService()

        city = city or self._current_city or service.get_city_auto() or "Libreville"
        self._current_city = city
        weather = service.get_current(city)

        # Récupère le programme de ProgramFrame via le callback
        # Si aucun programme n'est disponible encore, slots sera vide
        slots = []
        if self._get_program:
            program = self._get_program()
            if program is None:
                # ProgramFrame n'a pas encore fini de charge donc on Réessaie dans 2 secondes
                self.after(2000, lambda: self._load_data(city))
                return
            slots = program.slots

        self._update_ui(weather, slots)

    def _update_ui(self, weather, slots: list):
        """
        Centre la carte et place les marqueurs des activités géolocalisées.

        Parameters
        ----------
        city : str
            Ville à centrer sur la carte.
        slots : list[TimeSlot]
            Créneaux du programme seuls ceux avec lat/lon ont un marqueur.
        """
        # set_position avec coordonnées réelles
        if weather and weather.lat and weather.lon:
            self.mapp.after(100, lambda: self.mapp.set_position(weather.lat, weather.lon))
        else:
            self.mapp.after(100, lambda: self.mapp.set_address(self._current_city))

        # Supprime les anciens marqueurs
        self.mapp.delete_all_marker()

        # Filtre uniquement les slots avec coordonnées GPS valides
        slots_with_coords = [
            s for s in slots
            if s.lat is not None and s.lon is not None
        ]

        for slot in slots_with_coords:
            # Texte du marqueur : heure + activité + lieu si disponible
            text = f"{slot.time} : {slot.activity}"
            if slot.location:
                text += f"\n {slot.location}"

            self.mapp.set_marker(slot.lat, slot.lon, text=text)

        # Met à jour le label d'info
        n = len(slots_with_coords)
        if n == 0:
            self.info_label.configure(
                text="Aucun lieu géolocalisé, donc utilise ton imagination pour savoir où aller."
            )
        else:
            self.info_label.configure(
                text=f"{n} lieu{'x' if n > 1 else ''} affiché{'s' if n > 1 else ''} sur la carte"
            )

    def refresh(self, city: str):
        """
        Rafraîchit la carte avec une nouvelle ville.

        Appelée par MainWindow._refresh_frames() lors d'un changement de ville.
        """
        self._load_data(city)


if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("1200x800")
    root.configure(fg_color=COLORS["bg_main"])
    root.title("WeatherProgramm : Carte")
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)

    frame = MapFrame(root)
    frame.grid(row=0, column=0, sticky="nsew")
    root.mainloop()